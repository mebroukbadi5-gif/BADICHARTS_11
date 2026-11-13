#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""محاكاة تشغيلية لآلية الدفعات في get_historical_candles (v14.6):
خادم وهمي يرد على كل history/load بـ 200 شمعة حسب المرساة، ونتحقق:
1) batch_callback يُنادى عدة مرات (دفعات ترفع فور وصولها)
2) النتيجة الكاملة تغطي المدى المطلوب بلا تكرار ولا ثغرات
3) المرساة المتحركة تعمل (كل طلب يجلب شموعاً مختلفة)
"""
import asyncio
import importlib.util
import threading
import time

spec = importlib.util.spec_from_file_location('qxv14', '/home/z/my-project/download/qx_server_v14.py')
qx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qx)

PERIOD = 60
CANDLES_PER_BATCH = 200


class FakeCandlesHolder:
    def __init__(self):
        self.__candles_data = None

    @property
    def candles_data(self):
        return self.__candles_data

    @candles_data.setter
    def candles_data(self, v):
        self.__candles_data = v


class FakeAPI:
    def __init__(self, loop):
        self.loop = loop
        self.state = type('S', (), {'check_accepted_connection': True})()
        self.event_registry = qx.EventRegistry()
        self.candles = FakeCandlesHolder()
        self.candle_v2_data = {}
        self.current_asset = None
        self.current_period = None
        self.requests_seen = []

    def send_websocket_request(self, msg):
        # محاكاة الخادم: يحلل 42["history/load",{...}] ويرد بدفعة 200 شمعة
        assert msg.startswith('42["history/load"')
        body = msg[msg.index('{'):msg.rindex('}') + 1]
        import json
        payload = json.loads(body)
        asset = payload["asset"]
        index = payload["index"]
        t_end = int(payload["time"])
        offset = int(payload["offset"])
        period = int(payload["period"])
        self.requests_seen.append((t_end, offset))
        # الرد في خيط منفصل بعد مهلة شبكة واقعية قصيرة
        def _reply():
            time.sleep(0.05)
            candles = []
            t0 = t_end - offset
            t = t0 - (t0 % period)
            while t < t_end:
                candles.append({"time": t, "open": 1.0 + t % 7 / 100.0,
                                "close": 1.0 + (t + 1) % 7 / 100.0,
                                "high": 1.0 + (t % 7 + 2) / 100.0,
                                "low": 1.0 + max(0, t % 7 - 2) / 100.0})
                t += period
            message = {"asset": asset, "index": index, "candles": candles[:CANDLES_PER_BATCH]}
            asyncio.run_coroutine_threadsafe(
                self.event_registry.set_event(f'candles_ready_{asset}', message), self.loop)
            asyncio.run_coroutine_threadsafe(
                self.event_registry.set_event(f'candles_ready_{asset}_{index}', message), self.loop)
        threading.Thread(target=_reply, daemon=True).start()

    def subscribe_realtime_candle(self, asset, period):
        pass

    def chart_notification(self, asset):
        pass

    def follow_candle(self, asset):
        pass


async def main():
    loop = asyncio.get_running_loop()
    client = qx.Quotex.__new__(qx.Quotex)
    client.api = FakeAPI(loop)

    # ==== المرصد: كل دفعة تُسجَّل فور وصولها ====
    batch_events = []

    def on_batch(batch, worker_id):
        batch_events.append((time.time(), len(batch), worker_id))

    t_start = time.time()
    amount = 7200  # ساعتان من شموع الدقيقة = 120 شمعة ... نستخدم 3 أيام لضمان عدة دفعات
    amount = 3 * 86400
    res = await client.get_historical_candles('EURUSD_otc', amount_of_seconds=amount,
                                              period=PERIOD, max_workers=5,
                                              batch_callback=on_batch)
    elapsed = time.time() - t_start

    times = sorted(c['time'] for c in res)
    n = len(times)
    dup = n - len(set(times))
    gaps = 0
    for i in range(1, n):
        if times[i] - times[i - 1] > PERIOD:
            gaps += 1
    distinct_anchors = len(set(q[0] for q in client.api.requests_seen))

    print(f"candles returned      : {n} (expected ~{amount // PERIOD})")
    print(f"duplicates            : {dup}")
    print(f"gap slots (>60s)      : {gaps}")
    print(f"distinct request anchors: {distinct_anchors} of {len(client.api.requests_seen)} requests")
    print(f"batch_callback fires  : {len(batch_events)} batches (live pushed)")
    if batch_events:
        first_delay = batch_events[0][0] - t_start
        print(f"first batch arrived at: {first_delay:.2f}s")
        print(f"total elapsed         : {elapsed:.2f}s")
    coverage = (times[-1] - times[0]) if n else 0
    print(f"time coverage         : {coverage / 3600:.1f}h (target {amount / 3600:.0f}h)")

    ok = True
    assert dup == 0, "FAILED: duplicate candles"
    assert len(batch_events) >= 5, f"FAILED: batches not streamed live ({len(batch_events)})"
    assert first_delay < 2.0, f"FAILED: first batch too slow ({first_delay:.2f}s)"
    assert gaps <= 2, f"FAILED: {gaps} gaps in coverage"
    assert distinct_anchors >= len(client.api.requests_seen) - 2, "FAILED: same anchor reused (same batch would repeat)"
    assert coverage >= amount * 0.95, f"FAILED: coverage {coverage/3600:.1f}h < target"
    print("ALL RUNTIME CHECKS PASSED")


asyncio.run(main())
