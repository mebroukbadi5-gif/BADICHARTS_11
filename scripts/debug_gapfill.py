#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تشخيص fill_gap_once خطوة بخطوة"""
import os, sys, time, types, asyncio, importlib

SERVER = "/home/z/my-project/download/qx_server_v14.py"
sys.path.insert(0, os.path.dirname(SERVER))
mod = importlib.import_module("qx_server_v14")

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

    # خط بفجوة واضحة: شمعتان ثم فراغ 5 ثم شمعة
    a = {"time": NOW - 700, "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.0, "volume": 10}
    b = {"time": NOW - 640, "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.05, "volume": 10}
    c = {"time": NOW - 300, "open": 1.05, "high": 1.06, "low": 1.04, "close": 1.05, "volume": 10}
    line = [a, b, c]
    print("holes before:", mod._fill_missing_slots(list(line), 60, max_gap=1440))

    mod.MT4_WRITER.sync_state["X"] = {"period": 1, "candles": list(line),
                                      "last_write": 0, "last_price": 1.05}
    # تعطيل الفحص المرتبط بقاعدة البيانات لتطبيق سد الثغرات نفسه فقط
    mod.MT4_WRITER._gap_filled["X"] = False
    mod.MT4_WRITER._gap_filled_at["X"] = 0.0

    class FA:
        symbol = "X"
        api_symbol = "X"
        candles = list(line)
        price = 1.05
        def write(self, force=False): pass

    # مراقبة write_to_file
    orig_wtf = mod.MT4_WRITER.write_to_file
    def wtf_probe(symbol, period, candles):
        print(f"write_to_file called: {symbol} p{period} n={len(candles)}")
        return orig_wtf(symbol, period, candles)
    mod.MT4_WRITER.write_to_file = wtf_probe

    orig_save = mod.MT4_WRITER.save_snapshot
    def save_probe(symbol, candles):
        print(f"save_snapshot called: {symbol} n={len(candles)}")
        return orig_save(symbol, candles)
    mod.MT4_WRITER.save_snapshot = save_probe

    await mod.MT4_WRITER.fill_gap_once(mod.CLIENT, FA(), 1)
    st = mod.MT4_WRITER.sync_state["X"]["candles"]
    print("after fill_gap_once: n =", len(st))
    times = [c["time"] for c in st]
    print("times:", times[:8])
    holes = [t for t in range(NOW - 660, NOW - 300, 60) if t in times]
    print("gap slots present:", holes)

asyncio.run(main())
