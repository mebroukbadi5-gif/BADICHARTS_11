#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تشخيص مسار رفع علامة التجمد في fill_gap_once (نفس إعداد Test 2)"""
import os, sys, time, types, asyncio, importlib

SERVER = "/home/z/my-project/download/qx_server_v14.py"
sys.path.insert(0, os.path.dirname(SERVER))
mod = importlib.import_module("qx_server_v14")

PERIOD = mod.PERIOD_SECONDS
NOW = int(time.time()) // 60 * 60

def make_raw(end_time, n, period=60):
    out = []
    t0 = end_time - n * period + period
    for i in range(n):
        t = t0 + i * period
        o = 1.0 + (i % 10) / 100.0
        out.append({"time": t, "open": o, "close": o + 0.005,
                    "high": o + 0.01, "low": o - 0.01, "volume": 100})
    return out

class FakeAPI:
    def __init__(self):
        self.state = types.SimpleNamespace(check_accepted_connection=True)

class FakeClient:
    def __init__(self):
        self.api = FakeAPI()
    async def get_candles(self, asset, end_from_time, offset, period, **kw):
        n = min(199, int(offset) // int(period))
        return make_raw(int(end_from_time), n)

async def main():
    mod.ASYNC_LOOP = asyncio.get_running_loop()
    mod.CLIENT = FakeClient()
    mod.CONNECTION_ALIVE = True

    seed = mod._format_raw_candles(make_raw(NOW, 300))
    mod._ASSETS = {}
    asset = mod._get_or_create_asset("BRLUSD_otc")
    mod._apply_candles_to_asset(asset, seed)

    line = [dict(c) for c in asset.candles]
    mid = len(line) // 2
    hole_ts = [line[i]["time"] for i in range(mid, mid + 5)]
    with_holes = [c for c in line if c["time"] not in hole_ts]
    asset.candles = with_holes
    mod.MT4_WRITER.sync_state["BRLUSD_otc"] = {
        "period": mod.PERIOD, "candles": list(with_holes),
        "last_write": 0, "last_price": float(with_holes[-1]["close"]),
    }
    mod.MT4_WRITER._gap_filled["BRLUSD_otc"] = True
    # محاكاة واقعية: آخر سد ناجح كان قبل 301 ثانية (خارج فترة التحديث 300s)
    mod.MT4_WRITER._gap_filled_at["BRLUSD_otc"] = time.time() - 301
    mod.MT4_WRITER.candle_store.set_gap_filled("BRLUSD_otc", True, time.time())

    # === فحص كل شرط بفرع علامة التجمد ===
    is_filled, last_at = mod.MT4_WRITER.candle_store.is_gap_filled("BRLUSD_otc")
    print(f"is_gap_filled -> {is_filled}, last_at={last_at}")
    holes_found = mod.MT4_WRITER._scan_line_holes(list(with_holes), mod.PERIOD_SECONDS)
    print(f"_scan_line_holes(with_holes) -> {holes_found}")
    holes_seed = mod.MT4_WRITER._scan_line_holes(list(asset.candles), mod.PERIOD_SECONDS)
    print(f"_scan_line_holes(asset.candles) -> {holes_seed}")

    class FA:
        symbol = "BRLUSD_otc"
        api_symbol = "BRLUSD_otc"
        candles = with_holes
        price = 1.0
        def write(self, force=False): pass

    await mod.MT4_WRITER.fill_gap_once(FakeClient(), FA(), mod.PERIOD)
    after = mod.MT4_WRITER.sync_state["BRLUSD_otc"]["candles"]
    times = {c["time"] for c in after}
    filled = [t for t in hole_ts if t in times]
    print(f"after: n={len(after)} filled {len(filled)}/5")
    print(f"gap_filled flag now: {mod.MT4_WRITER._gap_filled.get('BRLUSD_otc')}")
    print(f"db flag now: {mod.MT4_WRITER.candle_store.is_gap_filled('BRLUSD_otc')[0]}")

asyncio.run(main())
