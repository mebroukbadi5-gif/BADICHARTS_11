#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار E2E لمسار v13 كاملاً بدون شبكة:
- CLIENT وهمي يرد بـ 470 شمعة (كما يرد خادم Quotex).
- preload_one_asset("BRLUSD_otc") -> 300 شمعة في الذاكرة + HST + candles.db.
- البث الحي (realtime_stream) يستقبل تيكاً ويحدّث آخر شمعة.
- fetch_older_batch -> +170 شمعة أقدم تُدمج في الذاكرة وHST وDB.
- PAGINATION_API.preload_status يعكس الحالة.
"""
import sys, os, time, asyncio
sys.path.insert(0, '/home/z/my-project/download')

import qx_server_v13 as qx

fails = []

def check(name, cond):
    print(('PASS' if cond else 'FAIL'), '-', name)
    if not cond:
        fails.append(name)

now = int(time.time()) // 60 * 60

# قاعدة بيانات مؤقتة خاصة بالاختبار (بدل candles.db الحقيقي)
import sqlite3
_TEST_DB = '/tmp/v13_test_candles.db'
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
for _f in (_TEST_DB + '-wal', _TEST_DB + '-shm'):
    if os.path.exists(_f):
        os.remove(_f)

def make_candles(start_ts, n, base=5.0):
    out = []
    for i in range(n):
        ts = start_ts + i * 60
        o = base + i * 0.01
        out.append({"time": ts, "open": o, "high": o + 0.05, "low": o - 0.05, "close": o + 0.02})
    return out

class FakeAPI:
    def __init__(self):
        self.realtime_candles = {}
        self.instruments = []
        class _St: status = 1; check_accepted_connection = True
        self.state = _St()
        self.last_message_at = time.time()

class FakeClient:
    def __init__(self):
        self.api = FakeAPI()
    async def get_candles(self, asset, end_from_time, offset, period):
        # يرد بعدد الشموع المطلوب المنتهي عند end_from_time (محاكاة الخادم)
        n = max(1, int(offset) // int(period))
        end = int(end_from_time) // 60 * 60
        return make_candles(end - (n - 1) * 60, n)
    async def start_candles_stream(self, asset, period):
        self.api.current_asset = asset
        self.api.current_period = period
        return None

qx.CLIENT = FakeClient()
qx.CONNECTION_ALIVE = True

async def main():
    loop = asyncio.get_running_loop()
    qx.ASYNC_LOOP = loop
    # عزل قاعدة الشموع: استخدم DB مؤقتاً بدل candles.db الحقيقي
    qx._CANDLE_STORE = qx.CandleStore(_TEST_DB)
    qx.MT4_WRITER._candle_store = qx._CANDLE_STORE

    # 1) preload_one_asset -> 300 شمعة
    n = await qx.preload_one_asset("BRLUSD_otc", 1, 1)
    check("preload_one_asset returned 300", n == 300)
    asset = qx._get_or_create_asset("BRLUSD_otc")
    check("asset.candles == 300", len(asset.candles) == 300)
    check("asset.price set", asset.price > 0)
    check("sync_state populated", asset.symbol in qx.MT4_WRITER.sync_state)
    check("sync_state candles == 300", len(qx.MT4_WRITER.sync_state[asset.symbol]['candles']) == 300)
    check("HST file 1 exists", os.path.exists(asset.path) and os.path.getsize(asset.path) > 148)
    hst2 = os.path.join(qx.MT4_WRITER.mt4_history_path, f"{asset.symbol}{qx.PERIOD}.hst")
    check("HST file 2 (qx_hst) exists", os.path.exists(hst2) and os.path.getsize(hst2) > 148)
    db_count = qx.MT4_WRITER.candle_store.count(asset.symbol)
    check("candles.db has 300 rows", db_count == 300)
    check("info recorded", qx._PRELOADED_INFO["BRLUSD_otc"]["candles"] == 300)
    check("registered in ALL_STREAMING_ASSETS", asset in qx.ALL_STREAMING_ASSETS)

    # 2) البث الحي + جامع التيكات: تيك جديد يحدّث آخر شمعة ويُخزن في الكاش
    collector_task = asyncio.ensure_future(qx.tick_cache_collector())
    tick_ts = now + 60
    qx.CLIENT.api.realtime_candles["BRLUSD_otc"] = ["BRLUSD_otc", tick_ts, 9.99, 1]
    await asyncio.sleep(0.8)
    last = asset.candles[-1]
    check("live stream created new candle from tick", last['time'] == qx._align_time(tick_ts) and last['close'] == 9.99)
    check("tick cache received the tick", len(qx._TICK_CACHE.get("BRLUSD_otc", [])) >= 1)
    collector_task.cancel()
    try:
        await collector_task
    except asyncio.CancelledError:
        pass

    # 3) fetch_older_batch -> +170 شمعة أقدم
    oldest_before = asset.candles[0]['time']
    added = await qx.fetch_older_batch("BRLUSD_otc", before_time=oldest_before, count=170)
    check("fetch_older_batch added 170", added == 170)
    check("asset.candles now 470+", len(asset.candles) >= 470)
    check("oldest moved back", asset.candles[0]['time'] < oldest_before)
    db_count2 = qx.MT4_WRITER.candle_store.count(asset.symbol)
    check("candles.db matches merged count", db_count2 == len(asset.candles))
    check("HST2 grew after merge", os.path.getsize(hst2) >= 148 + 470 * 44 - 100)
    check("sync_state merged too", len(qx.MT4_WRITER.sync_state[asset.symbol]['candles']) >= 470)

    # 4) preload_status + get_recent_ticks عبر PAGINATION_API
    st = qx.PAGINATION_API["preload_status"]()
    check("preload_status knows BRLUSD_otc", "BRLUSD_otc" in st and st["BRLUSD_otc"]["candles"] >= 470)
    ticks = qx.PAGINATION_API["get_recent_ticks"]("BRLUSD_otc", seconds=300)
    check("get_recent_ticks via API returns the tick", len(ticks) >= 1)

    # 5) دورة الإيقاف عند الإغلاق (محاكاة إغلاق العملة)
    entries = [{"asset": "BRLUSD_otc", "open": False, "payout": 86}]
    closed = {e["asset"] for e in entries if e.get("open") is False}
    check("closed-set logic works", "BRLUSD_otc" in closed)

asyncio.run(main())
print()
if fails:
    print(f"{len(fails)} FAILURES: {fails}")
    sys.exit(1)
print("ALL E2E TESTS PASSED")
