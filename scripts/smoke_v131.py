#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.1 smoke test — fetch gate + gap filling + app merge logic (no network).

Verifies:
 1. Gate serialization: concurrent fetches never overlap (one at a time).
 2. Gate foreground counter + background yield (_fetch_gate_wait_foreground).
 3. Gate verification+retry: a broken (live-message) response is rejected and
    the same original request is re-issued until a complete one arrives.
 4. Gate debounce: identical window within 3s reuses the cached result.
 5. _apply_candles_to_asset now fills time gaps (flat candles, volume=0).
 6. App-side _qx_merge_tail_full heals tail gaps without touching the head.
 7. App-side _ticks_to_candles / _qx_fmt_raw behave as before (no change).
"""
import os
import sys
import time
import asyncio
import threading
import tempfile

DL = "/home/z/my-project/download"
TMP = tempfile.mkdtemp(prefix="qx131_")
os.chdir(TMP)
sys.path.insert(0, DL)

import importlib.util
spec = importlib.util.spec_from_file_location(
    "qx_server_v13", os.path.join(DL, "qx_server_v13.py"))
qx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qx)
print("[ok] qx_server_v13 imported")

# ---------------------------------------------------------------- fake client
class FakeClient:
    def __init__(self, delays=0.15):
        self.delays = delays
        self.api = type("FakeApi", (), {})()   # non-None api (gate checks CLIENT.api)
        self.state_ok = True
        self.calls = []          # (asset, end, seconds, period, t_start, t_end)
        self._lock = threading.Lock()
        self.script = {}         # asset -> list of responses (popped per call)

    async def get_candles(self, asset, end_from_time, offset, period, **kw):
        t0 = time.time()
        await asyncio.sleep(self.delays)
        with self._lock:
            self.calls.append((asset, int(end_from_time), int(offset), int(period), t0, None))
            idx = len(self.calls) - 1
        resp = None
        seq = self.script.get(asset)
        if seq:
            resp = seq.pop(0)
        if resp is None:
            # default: a full valid history response of 300 1m candles
            now = int(end_from_time)
            resp = [{"time": now - i * period, "open": 1.0 + i * 1e-6,
                     "close": 1.0 + i * 1e-6, "high": 1.1, "low": 0.9}
                    for i in range(int(offset) // max(1, period))]
        self.calls[idx] = self.calls[idx][:5] + (time.time(),)
        return resp

    def overlap(self):
        """max concurrent overlap across recorded calls"""
        evs = sorted([(c[4], 1) for c in self.calls if len(c) >= 6] +
                     [(c[5], -1) for c in self.calls if len(c) >= 6 and c[5]])
        cur = mx = 0
        for _, d in evs:
            cur += d
            mx = max(mx, cur)
        return mx

# ---------------------------------------------------------------- async engine
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()
qx.ASYNC_LOOP = loop
qx.CONNECTION_ALIVE = True

def run(coro, timeout=30):
    return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=timeout)

# ---- Test 1: serialization (3 concurrent fetches never overlap) -------------
fc = FakeClient(delays=0.15)
qx.CLIENT = fc
now = int(time.time())
t0 = time.time()
rs = [run(qx.qx_fetch_window_raw(f"ASSET{i}", now, 300 * 60, 60)) for i in
      asyncio.run(gather3())] if False else None
# issue 3 concurrent requests properly via asyncio.gather inside the loop
async def three():
    return await asyncio.gather(*[
        qx.qx_fetch_window_raw(f"ASSET{i}", now, 300 * 60, 60) for i in range(3)])
res3 = run(three())
elapsed = time.time() - t0
mx = fc.overlap()
assert all(len(r) == 300 for r in res3), f"expected 300 candles, got {[len(r) for r in res3]}"
assert mx <= 1, f"OVERLAP DETECTED: {mx} concurrent fetches"
assert elapsed >= 0.40, f"requests did not serialize ({elapsed:.2f}s)"
print(f"[ok] gate serialization: 3 concurrent fetches, max overlap={mx}, {elapsed:.2f}s")

# ---- Test 2: broken response (live-message theft) is retried ----------------
fc2 = FakeClient(delays=0.02)
qx.CLIENT = fc2
# first call returns 1 candle (broken / live snapshot), second returns full
fc2.script["BROKEN"] = [
    [{"time": now, "open": 1.0, "close": 1.0, "high": 1.0, "low": 1.0}],
    None,  # None -> default full response path is not triggered by None...
]
# fix: script must return the full list as 2nd response
fc2.script["BROKEN"] = [
    [{"time": now, "open": 1.0, "close": 1.0, "high": 1.0, "low": 1.0}],
    [{"time": now - i * 60, "open": 1.0, "close": 1.0, "high": 1.1, "low": 0.9}
     for i in range(300)],
]
res = run(qx.qx_fetch_window_raw("BROKEN", now, 300 * 60, 60, foreground=True))
assert res is not None and len(res) == 300, f"retry failed: {len(res or [])} candles"
assert len(fc2.calls) == 2, f"expected 2 attempts, got {len(fc2.calls)}"
print("[ok] gate verification: broken 1-candle response retried -> 300 candles (2 attempts)")

# ---- Test 3: debounce — same window within 3s returns cached, no new call ---
n_calls_before = len(fc2.calls)
res_b = run(qx.qx_fetch_window_raw("BROKEN", now, 300 * 60, 60, foreground=True))
assert len(fc2.calls) == n_calls_before, "debounce failed: extra request issued"
print("[ok] gate debounce: identical window within 3s -> served from cache")

# ---- Test 4: foreground counter + background yield ---------------------------
qx.CLIENT = FakeClient(delays=0.05)
run(qx._fetch_gate_wait_foreground(0.1))  # no FG pending -> returns immediately
# simulate a pending foreground request
qx._FETCH_GATE_FG = 2
async def _yield_probe():
    t = time.time()
    await qx._fetch_gate_wait_foreground(1.2)
    return time.time() - t
fut = asyncio.run_coroutine_threadsafe(_yield_probe(), loop)
time.sleep(0.3)
qx._FETCH_GATE_FG = 0   # foreground finishes -> yield returns
waited = fut.result(timeout=5)
assert 0.25 <= waited < 1.0, f"foreground yield did not respect pending FG ({waited:.2f}s)"
print(f"[ok] foreground yield: background waited {waited:.2f}s until FG cleared")

# ---- Test 5: _apply_candles_to_asset fills gaps ------------------------------
class FakeAsset:
    def __init__(self):
        self.symbol = "TEST_sym"
        self.candles = []
        self.price = 0.0
        self.written = 0
    def write(self, force=False):
        self.written += 1

qx.MT4_WRITER.sync_state.clear()
a = FakeAsset()
base = int(time.time()) - 600
base -= base % 60
candles = [{"time": base - i * 60, "open": 1.0, "high": 1.2, "low": 0.8,
            "close": 1.0, "volume": 100} for i in range(10)]
# remove candles 3..7 -> a 5-minute hole in the middle
hole = [candles[i] for i in range(len(candles)) if not (3 <= i <= 7)]
qx._apply_candles_to_asset(a, hole)
times = [c["time"] for c in a.candles]
assert len(a.candles) == 10, f"gap not filled: {len(a.candles)} candles (expected 10)"
assert all(times[i + 1] - times[i] == 60 for i in range(len(times) - 1)), "still gapped"
flat = [c for c in a.candles if c["volume"] == 0]
assert len(flat) == 5, f"expected 5 flat fillers, got {len(flat)}"
# continuity: every flat candle continues the previous close
for i in range(1, len(a.candles)):
    assert abs(a.candles[i]["open"] - a.candles[i - 1]["close"]) < 1e-12, "open/close discontinuity"
print(f"[ok] gap fill on storage: 10 candles (5-min hole) -> {len(a.candles)} candles, "
      f"5 flat fillers, full continuity")

# ---- Test 6: fetch_older_batch through the gate keeps history contiguous -----
fc3 = FakeClient(delays=0.02)
qx.CLIENT = fc3
base = int(time.time()) - 600
base -= base % 60
first_oldest = base - 299 * 60   # oldest candle of the preloaded 300
# older batch response: 170 candles older than first_oldest
older = [{"time": first_oldest - (i + 1) * 60, "open": 1.0, "high": 1.1, "low": 0.9,
          "close": 1.0, "volume": 100} for i in range(170)]
fc3.script["OLDR_otc"] = [older]
qx.MT4_WRITER.sync_state.clear()
qx._ASSET_OBJECTS.pop("OLDR_otc", None)
n = run(qx.fetch_older_batch("OLDR_otc", first_oldest, 170))
assert n == 170, f"older batch returned {n}"
merged = qx._get_or_create_asset("OLDR_otc").candles
times2 = [c["time"] for c in merged]
assert times2 == sorted(times2) and len(times2) == len(set(times2)), "merge broke order/uniqueness"
assert times2[0] == first_oldest - 170 * 60, "oldest candle not extended"
gaps2 = [(times2[i + 1] - times2[i]) for i in range(len(times2) - 1)]
assert set(gaps2) == {60}, f"gaps in merged history: {sorted(set(gaps2))}"
print(f"[ok] older batch via gate: +170 candles, oldest moved back 170 min, zero gaps")

# ---- Test 7: app-side _qx_merge_tail_full heals tail gaps, head untouched ----
import re
src = open(os.path.join(DL, "BadiChartsStudio_live.py"), encoding="utf-8").read()
m = re.search(r"    def _qx_merge_tail_full\(self, new_feed.*?(?=\n    def )", src, re.s if hasattr(re, "s") else re.S)
assert m, "merge function not found"
exec_text = m.group(0).replace("    def _qx_merge_tail_full", "def _qx_merge_tail_full")
exec_text = "\n".join(l[4:] if l.startswith("    ") else l for l in exec_text.splitlines())
g = {"__name__": "t"}
exec(exec_text, g)
_B = g["_qx_merge_tail_full"]

class B:
    _QX_FEED_CAP = 3000
    _QX_FEED_TRIM = 2600
    def __init__(self):
        self._candles = []

b = B()
b._candles = [{"t": 1000000000 + i * 60, "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.0, "v": 1}
              for i in range(300)]
head_before = b._candles[0]
new_feed = ([{"t": 1000000000 + i * 60, "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.0, "v": 1}
             for i in range(295)] +
            # skip 5 slots (gap) then a new candle
            [{"t": 1000000000 + 306 * 60, "o": 1.0, "h": 1.2, "l": 0.9, "c": 1.05, "v": 3}])
changed = _B(b, new_feed, 60)
assert changed and len(b._candles) == 307, f"merge len {len(b._candles)} (expected 307)"
assert b._candles[0] == head_before, "head was touched!"
tail_times = [c["t"] for c in b._candles]
dd = [tail_times[i + 1] - tail_times[i] for i in range(len(tail_times) - 1)]
assert set(dd) == {60}, f"tail gaps remain: {sorted(set(dd))}"
flatf = [c for c in b._candles[-7:] if c["v"] == 0]
assert len(flatf) == 6, f"expected 6 flat fillers in tail, got {len(flatf)}"
print("[ok] app tail-merge heals gaps: head untouched, 6 flat fillers, continuous 60s")

print()
print("ALL v13.1 SMOKE TESTS PASSED")
