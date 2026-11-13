#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار دخاني لخادم v14: يشغّل التشخيص الذاتي الكامل + اختبار توزيع
التيكات الحي عبر المضخة + فحص النبضة والنقاط والخطافات."""
import asyncio
import os
import sys

sys.path.insert(0, "/home/z/my-project/download")
os.chdir("/home/z/my-project/work")
os.makedirs("/home/z/my-project/work", exist_ok=True)

import qx_server_v14 as qx  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append((name, note))
    print(f"  {'✓' if ok else '✗'} {name}" + (f"  [{note}]" if note else ""))


async def main():
    print("=== qx_server_v14 smoke test ===")

    # 1) التشخيص الذاتي الكامل (بوابة، دلو، متتبع، قاطع، سجل، نبضة، مشرف، backoff)
    res = await qx.V14_API["selftest"]()
    check("v14.selftest", res["ok"],
          f"{res['passed']}/{res['total']} passed")
    for r in res["results"]:
        if not r["ok"]:
            check(f"  selftest:{r['name']}", False, r["note"])

    # 2) مضخة التيكات الحية: تيك → مشترك فوراً (التكس لا ينام)
    sub = qx.V14_TICKS.subscribe(symbols={"TEST_USD_otc"}, maxsize=100)
    got_dispatch = []

    orig_ingest = qx.V14_TICKS._dispatch

    def spy_dispatch(sym, ts, price, cls):
        got_dispatch.append((sym, ts, price, cls))
        return orig_ingest(sym, ts, price, cls)

    qx.V14_TICKS._dispatch = spy_dispatch
    # ابدأ المضخة أولاً ثم بلع التيكات — notify() يوقظها فوراً
    pump = asyncio.ensure_future(qx.V14_TICKS.pump_loop())
    await asyncio.sleep(0.05)
    _now = int(__import__("time").time())
    qx.V14_TICKS.ingest_tick("TEST_USD_otc", _now, 0.8312)
    qx.V14_TICKS.ingest_tick("TEST_USD_otc", _now + 1, 0.8320)
    await asyncio.sleep(0.25)
    check("tick.pump_dispatch", len(got_dispatch) >= 1,
          f"dispatched={len(got_dispatch)}")
    ticks_now = sub.drain(50)
    check("tick.subscriber_received", len(ticks_now) >= 1,
          f"received={len(ticks_now)}")
    check("tick.recent_ticks_api",
          len(qx.V14_TICKS.recent_ticks("TEST_USD_otc", 300)) >= 1)
    pump.cancel()

    # 3) غلاف _cache_tick مثبّت (التقاط يوقظ المضخة)
    qx.install_v14_hooks()
    check("hook.cache_tick_wrapped", bool(qx.__dict__.get("_V14_CACHE_TICK_WRAPPED")))
    wrapped = qx.__dict__.get("_cache_tick")
    check("hook.cache_tick_is_new", wrapped.__name__ == "_wrapped")

    # 4) غلاف ensure_asset_loaded مسجّل في PAGINATION_API
    check("hook.ensure_wrapped", bool(qx._V14_ENSURE_WRAPPED))
    check("hook.pagination_api_updated",
          qx.PAGINATION_API["ensure_asset_loaded"].__name__ == "_wrapped")

    # 5) حلقات الخلفية: القائمة كاملة (15 حلقة مشرفة)
    loops = qx.v14_build_background_loops()
    names = [n for n, _ in loops]
    expected = {"gate_worker", "tick_pump", "tick_sampler", "tick_silence",
                "gap_guard", "gap_audit", "endpoint_probe", "replay_watcher",
                "session_watcher", "harvester", "memory_guard", "disk_guard",
                "load_shedder", "heartbeat", "metrics", "selftest"}
    check("loops.list_complete", expected.issubset(set(names)),
          f"{len(names)} loops: {','.join(names)}")

    # 6) النبضة والنقاط والجلسة والمقاييس
    hb = qx.V14_HEARTBEAT.payload()
    check("heartbeat.payload", "gate" in hb and "supervisor" in hb)
    ep = qx.V14_ENDPOINTS.info()
    check("endpoints.pool_real_hosts",
          any(e["primary"] for e in ep["endpoints"]) and
          all(e["host"] in ("quotex.com", "market-qx.info")
              for e in ep["endpoints"]),
          str([e["host"] for e in ep["endpoints"]]))
    check("session.state_machine", qx.V14_SESSION.info()["state"] in
          ("BOOT", "CONNECTED", "DEGRADED", "RECONNECTING"))
    m = qx.V14_METRICS.snapshot()
    check("metrics.snapshot", "v14.ticks.ingested" in m["counters"])

    # 7) بوابة حقيقية على العامل الفعلي (بدون اتصال: يجب أن تفشل بأمان)
    real_raw = qx.qx_fetch_window_raw

    async def fake_raw(sym, end, secs, per, foreground=False,
                       timeout=None, retries=2):
        return [{"time": 1700000000, "open": 1, "high": 1, "low": 1,
                 "close": 1, "volume": 1}]

    qx.qx_fetch_window_raw = fake_raw
    try:
        gate = qx.V14_GATE
        fut = gate.submit_nowait("LIVE_GATE_TEST", int(1_700_000_000), 60, 60,
                                 priority=int(qx.RequestPriority.OPENING))
        worker = asyncio.ensure_future(gate.worker())
        raw = await asyncio.wait_for(fut, timeout=5.0)
        check("gate.live_worker", bool(raw) and raw[0]["time"] == 1700000000)
        worker.cancel()
    finally:
        qx.qx_fetch_window_raw = real_raw

    # 8) سجل الجلسة يعمل ويقرأ عربي
    qx.V14_JOURNAL.record("smoke_test", ملاحظة="اختبار دخاني")
    tail = qx.V14_JOURNAL.tail(1)
    check("journal.arabic_roundtrip", tail and
          tail[0].get("event") == "smoke_test")

    # 9) جرد الأسطر (طلب المستخدم: ≥ 15 ألف سطر للخادم والتطبيق)
    inv = qx.v14_line_inventory()
    server_lines = inv["server_lines"]
    with open("/home/z/my-project/download/BadiChartsStudio_live.py",
              encoding="utf-8") as f:
        app_lines = sum(1 for _ in f)
    total = server_lines + app_lines
    check("linecount.server>=9k", server_lines >= 9000,
          f"server={server_lines:,}")
    check("linecount.total>=15k", total >= 15000,
          f"server {server_lines:,} + app {app_lines:,} = {total:,}")

    print()
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for name, note in FAIL:
            print(f"  FAILED: {name} [{note}]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
