#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات v14.2 — الجذر الحقيقي الذي قتل التمرير للخلف وسد الثغرات:

1) قفل البوابة المرتب بحلقة ميتة: بعد إعادة إنشاء حلقة asyncio (gen 2)
   كان كل جلب عبر البوابة يرفع RuntimeError — الآن يتبع الحلقة الجارية.
2) بوابة v14 (Event/Locks): تُربط من جديد عند تغيّر الحلقة دون إلغاء
   طلبات سُلّمت قبل بدء العامل على نفس الحلقة.
3) fill_gap_once: النداء الأصلي client.get_candles حرفياً (بلا بوابة).
4) ترحيل بدء التشغيل: علامات التجمد القديمة تُصفَّر حتى تعمل الطريقة
   الأصلية فوراً وتسدّ الفجوات الموجودة.
5) إعادة الجدولة: حلقات v14 + mt4_gap_filer تُعاد جدولتها عند gen>1.
"""
import asyncio
import os
import sys
import tempfile
import time

sys.path.insert(0, "/home/z/my-project/download")
os.chdir("/home/z/my-project/work")

import qx_server_v14 as qx  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append((name, note))
    print(f"  {'✓' if ok else '✗'} {name}" + (f"  [{note}]" if note else ""))


def test_gate_lock_follows_loop():
    print("1) قفل البوابة يتبع الحلقة الجارية")
    async def get_lock():
        return qx._fetch_gate_lock()
    # كل asyncio.run ينشئ حلقة حقيقية جديدة — مثل gen-1 ثم gen-2
    lock_a = asyncio.run(get_lock())
    lock_b = asyncio.run(get_lock())
    check("lock.recreated_per_loop", lock_a is not lock_b,
          "same-object means stale gen-1 lock (BUG)")
    async def use_now():
        async with qx._fetch_gate_lock():
            return True
    check("lock.usable_now", asyncio.run(use_now()))


def test_v14_gate_ensure_loop():
    print("2) بوابة v14 — إعادة الربط عند تغيّر الحلقة فقط")
    gate = qx.V14RequestGate()

    async def first_bind():
        gate.submit_nowait("A", 0, 60, 60, label="t")
        gate._ensure_loop()
        return gate._bound_loop, len(gate._pending)

    async def same_loop():
        gate._ensure_loop()
        return len(gate._pending)

    # أول ربط + ثبات على نفس الحلقة داخل asyncio.run واحدة (حلقة gen-1 واحدة)
    async def gen1():
        gate.submit_nowait("A", 0, 60, 60, label="t")
        gate._ensure_loop()
        b1 = gate._bound_loop
        n1 = len(gate._pending)
        gate._ensure_loop()   # نفس الحلقة — لا تغيير
        return b1, n1, len(gate._pending)

    b1, n1, n2 = asyncio.run(gen1())
    check("ensure.first_bind_ok", b1 is not None,
          "first bind must succeed")
    check("ensure.first_keeps_pending", n1 == 1, f"pending={n1}")
    check("ensure.same_loop_noop", n2 == 1, f"pending after noop={n2}")
    # حلقة جديدة (gen-2 بعد إعادة الاتصال) → الطلبات القديمة تُلغى
    async def new_loop():
        gate._ensure_loop()
        return len(gate._pending), gate._bound_loop
    pending2, bound2 = asyncio.run(new_loop())
    check("ensure.loop_change_resets",
          pending2 == 0 and bound2 is not None and bound2 is not b1)


def test_fill_gap_once_verbatim():
    print("3) fill_gap_once — النداء الأصلي client.get_candles")
    src = open("/home/z/my-project/download/qx_server_v14.py",
               encoding="utf-8").read()
    m = src.find("async def fill_gap_once")
    body = src[m:m + 6000]
    check("gap.original_call",
          "candles = await client.get_candles(api_symbol, time.time(), "
          "int(small_days * 86400), PERIOD_SECONDS)" in body,
          "must call client.get_candles exactly as the reference code")
    check("gap.no_gate_in_gapfill", "qx_fetch_window_raw" not in body,
          "gap-fill must not route through the fetch gate")
    check("gap.original_freeze",
          body.count("if is_filled:") == 1 and
          "return    # frozen - keep candles exactly as they were" in body,
          "original freeze branch verbatim")
    check("gap.no_hole_scan_in_freeze",
          "_scan_line_holes" not in body,
          "v14.1 freeze-lift extension removed (user demand: original verbatim)")


def test_startup_migration():
    print("4) ترحيل بدء التشغيل — علامات التجمد تُصفَّر")
    db = os.path.join(tempfile.mkdtemp(prefix="migr_test_"), "candles.db")
    store = qx.CandleStore(db)
    store.set_gap_filled("TESTUSD_otc", True, time.time())
    filled, _ = store.is_gap_filled("TESTUSD_otc")
    check("migr.set_works", filled is True,
          "flag writable+readable on a healthy db")
    # متجر جديد على نفس الملف → الترحيل يصفّر العلامات
    store2 = qx.CandleStore(db)
    filled2, _ = store2.is_gap_filled("TESTUSD_otc")
    check("migr.reset_on_init", filled2 is False,
          "startup migration clears stale frozen flags so the original "
          "method can fill existing holes")


def test_engine_reschedule():
    print("5) إعادة الجدولة عند gen>1")
    src = open("/home/z/my-project/download/qx_server_v14.py",
               encoding="utf-8").read()
    m = src.find("def start_async_engine")
    body = src[m:m + 4000]
    check("engine.reschedules_gap_filler",
          "mt4_gap_filler()" in body,
          "mt4_gap_filler survives loop regeneration")
    check("engine.reschedules_v14_loops",
          "v14_build_background_loops" in body,
          "v14 strengthening loops survive loop regeneration")


def main():
    print("=== qx_server v14.2 tests ===")
    test_gate_lock_follows_loop()
    test_v14_gate_ensure_loop()
    test_fill_gap_once_verbatim()
    test_startup_migration()
    test_engine_reschedule()
    print()
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for name, note in FAIL:
            print(f"  FAILED: {name} [{note}]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
