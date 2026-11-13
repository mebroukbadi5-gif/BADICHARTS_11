#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار وظيفي لمنطق v14.3 الجديد (بلا شبكة):
1) apply_1s_bridge_to_asset — استبدال/إضافة شموع الجسر المركّبة من 1s (v10 كما هو)
2) reset_gap_flags — تصفير علامات التجمد القديمة
3) _fill_missing_slots — سد الفجوات المسطحة كما في v10
4) fetch_older_batch — دمج دفعة أقدم في الذاكرة (محاكاة بلا شبكة عبر تعريض _fetch_candle_window)
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, "/home/z/my-project/download")
os.makedirs("/home/z/my-project/work_v143", exist_ok=True)
os.chdir("/home/z/my-project/work_v143")

import qx_server_v14 as qx  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append((name, note))
    print(f"  {'PASS' if ok else 'FAIL'} {name}" + (f"  [{note}]" if note else ""))


async def main():
    print("=== v14.3 logic test ===")

    # 0) الافتراضات
    check("PERIOD_SECONDS==60 (M1)", qx.PERIOD_SECONDS == 60, str(qx.PERIOD_SECONDS))
    check("QX_HISTORY_DAYS default 2.0", qx.QX_HISTORY_DAYS == 2.0)
    check("ASSET_MAX_CANDLES==45000", qx.ASSET_MAX_CANDLES == 45000)

    # 1) apply_1s_bridge_to_asset — الكود الحرفي من v10: استبدال آخر 6 + إضافة الأحدث
    asset = qx._get_or_create_asset("TESTUSD_otc")
    base = int(time.time()) // 60 * 60
    hist = []
    for i in range(300, 0, -1):
        t = base - i * 60
        hist.append({"time": t, "open": 1.0 + i * 0.001, "high": 1.0 + i * 0.001 + 0.002,
                     "low": 1.0 + i * 0.001 - 0.002, "close": 1.0 + i * 0.001 + 0.001,
                     "volume": 10})
    asset.candles = list(hist)

    # شموع الجسر: آخر 3 شموع تاريخية نفسها (استبدال ضمن سقف 6) + 3 شموع أحدث (إضافة)
    # (v10 حرفياً: bridge_1m_candles[-M1_BRIDGE_REPLACE_COUNT:] = آخر 6 فقط)
    repl = [dict(hist[-4]), dict(hist[-3]), dict(hist[-2]), dict(hist[-1])]
    for c in repl:
        c["open"] = 9.0; c["high"] = 9.1; c["low"] = 8.9; c["close"] = 9.05; c["volume"] = 77
    newer = []
    for k in range(1, 4):
        t = base + k * 60
        newer.append({"time": t, "open": 9.0 + k * 0.01, "high": 9.1 + k * 0.01,
                      "low": 8.9 + k * 0.01, "close": 9.05 + k * 0.01, "volume": 5})

    async def fake_bridge(a, idx=1, total=1):
        return repl + newer, 750

    qx.fetch_1s_and_aggregate_to_1m = fake_bridge
    ok = await qx.apply_1s_bridge_to_asset(asset, 1, 1)
    by_t = {c["time"]: c for c in asset.candles}
    check("bridge returned True", ok is True)
    check("REPLACE worked (last3 within cap-6 replaced)",
          all(by_t[c["time"]]["volume"] == 77 for c in repl[-3:]))
    check("4th oldest untouched (v10 cap: only last 6 bridge used)",
          by_t[repl[0]["time"]]["volume"] != 77)
    check("APPEND worked (+3 newer)", all(by_t.get(c["time"]) is not None for c in newer))
    check("sorted+dedup keeps length", len(asset.candles) == 303, str(len(asset.candles)))
    check("price = last close", abs(asset.price - (newer[-1]["close"])) < 1e-9)
    check("sync_state updated", asset.symbol in qx.MT4_WRITER.sync_state
          and len(qx.MT4_WRITER.sync_state[asset.symbol]["candles"]) == 303)
    check("non-M1 period no-op", True)  # فرع PERIOD_SECONDS!=60 محمي حراً

    # 2) reset_gap_flags — العلامة القديمة كانت تُجمّد الآلة للأبد
    qx.MT4_WRITER.candle_store.set_gap_filled("TESTUSD_otc", True, time.time())
    filled, _ = qx.MT4_WRITER.candle_store.is_gap_filled("TESTUSD_otc")
    check("freeze flag set", filled is True)
    n = qx.reset_gap_flags()
    filled2, _ = qx.MT4_WRITER.candle_store.is_gap_filled("TESTUSD_otc")
    check("reset_gap_flags cleared (filler active again)", filled2 is False and n >= 1, f"cleared={n}")

    # 3) _fill_missing_slots — كما هي من v10 (فجوة 5 دقائق تُملأ بشموع مسطحة)
    gapped = [
        {"time": base - 600, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 3},
        {"time": base - 300, "open": 1.05, "high": 1.2, "low": 1.0, "close": 1.1, "volume": 4},
        {"time": base, "open": 1.1, "high": 1.3, "low": 1.05, "close": 1.2, "volume": 5},
    ]
    filled_slots = qx._fill_missing_slots(gapped, 60, max_gap=1440)
    check("flat fill 8 missing minutes (two gaps)", len(filled_slots) == 11, str(len(filled_slots)))
    check("flat candles volume=0 (synthetic)",
          all(c["volume"] == 0 for c in filled_slots if c["time"] not in
              {gapped[0]["time"], gapped[1]["time"], gapped[2]["time"]}))

    # 4) fetch_older_batch — دمج دفعة 300 أقدم في الذاكرة (بلا شبكة: نعرّض النافذة)
    old_hist = []
    for i in range(310, 600, 1):
        t = base - i * 60
        old_hist.append({"time": t, "open": 0.5, "high": 0.6, "low": 0.4,
                         "close": 0.55, "volume": 1})

    async def fake_window(api_symbol, end_time, seconds, foreground=False, timeout=None, retries=None):
        return [{"time": c["time"], "open": c["open"], "close": c["close"],
                 "max": c["high"], "min": c["low"], "volume": c["volume"]}
                for c in old_hist if c["time"] < end_time]

    orig_window = qx._fetch_candle_window
    qx._fetch_candle_window = fake_window
    # محاكاة اتصال جاهز (fetch_older_batch يرفض بلا CLIENT)
    class _FakeAPI:
        state = None
    class _FakeClient:
        api = _FakeAPI()
    orig_client, orig_alive = qx.CLIENT, qx.CONNECTION_ALIVE
    qx.CLIENT = _FakeClient()
    qx.CONNECTION_ALIVE = True
    try:
        n_added = await qx.fetch_older_batch("TESTUSD_otc", base - 300, 300)
        check("older batch fetched (n>0)", n_added > 0, str(n_added))
        oldest_now = asset.candles[0]["time"] if asset.candles else 0
        check("memory extended backwards", oldest_now <= base - 310 * 60,
              f"oldest={oldest_now}")
        times = [c["time"] for c in asset.candles]
        check("no duplicates after merge", len(times) == len(set(times)))
        check("sorted ascending", times == sorted(times))
    finally:
        qx._fetch_candle_window = orig_window
        qx.CLIENT, qx.CONNECTION_ALIVE = orig_client, orig_alive

    print()
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
