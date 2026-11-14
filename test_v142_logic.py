#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v14.2 logic test — يحاكي المسار الحقيقي بالكامل:
1) fetch_older_batch: نفس نداء التطبيق عند التمرير للخلف (300 شمعة أقدم)
2) fill_gap_once: الطريقة الأصلية — فجوات حقيقية تُسدّ
3) قصّ الدفعة في جانب التطبيق: batch = engine < before
"""
import os, sys, time, types, asyncio, importlib

SERVER = "/home/z/my-project/download/qx_server_v14.py"
sys.path.insert(0, os.path.dirname(SERVER))

mod = importlib.import_module("qx_server_v14")

PERIOD = mod.PERIOD_SECONDS  # 60
NOW = int(time.time()) // 60 * 60


def make_raw_candles(end_time, n, period=PERIOD, missing=()):
    """شموع خام بصيغة Quotex (dict) — تنتهي عند end_time."""
    out = []
    t0 = end_time - n * period + period
    for i in range(n):
        t = t0 + i * period
        if t in missing:
            continue
        o = 1.0 + (i % 10) / 100.0
        out.append({"time": t, "open": o, "close": o + 0.005,
                    "high": o + 0.01, "low": o - 0.01, "volume": 100})
    return out


class FakeAsset:
    def __init__(self, symbol):
        self.symbol = symbol
        self.api_symbol = symbol
        self.candles = []
        self.price = 0.0
        self.streaming = False
        self.stream_task = None

    def write(self, force=False):
        pass


class FakeAPI:
    def __init__(self):
        self.state = types.SimpleNamespace(check_accepted_connection=True)
        self._history_pending = {}


class FakeClient:
    def __init__(self):
        self.api = FakeAPI()
        self.get_candles_calls = []

    async def get_candles(self, asset, end_from_time, offset, period, **kw):
        """محاكاة خادم Quotex: يعيد حتى 199 شمعة منتهية عند end_from_time
        (حسب توثيق pyquotex الرسمي)."""
        self.get_candles_calls.append((asset, int(end_from_time), int(offset), int(period)))
        end = int(end_from_time)
        n = min(199, offset // period)
        return make_raw_candles(end, n, period)


async def main():
    ok = True

    # ------------------------------------------------- 1) fetch_older_batch
    print("=" * 60)
    print("TEST 1: fetch_older_batch (scroll-back path)")
    print("=" * 60)
    # زرع شموع أولية (300 شمعة تنتهي الآن) كما في التحميل الأولي
    seed = mod._format_raw_candles(make_raw_candles(NOW, 300))
    mod._ASSETS = {}
    asset = mod._get_or_create_asset("BRLUSD_otc")
    mod._apply_candles_to_asset(asset, seed)
    oldest = asset.candles[0]["time"]
    print(f"seed: {len(asset.candles)} candles, oldest={oldest}")

    # استبدال نافذة الجلب بـ FakeClient عبر CLIENT.get_candles داخل البوابة
    fake = FakeClient()
    mod.CLIENT = fake
    mod.CONNECTION_ALIVE = True
    mod.ALL_STREAMING_ASSETS = [asset]
    mod.ASYNC_LOOP = asyncio.get_running_loop()   # حلقة الاختبار نفسها

    # التمرير للخلف: before = أقدم شمعة حالية
    before = oldest
    try:
        n_older = await mod.fetch_older_batch("BRLUSD_otc", before, mod.PAGINATION_BATCH)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  !! fetch_older_batch raised: {e}")
        ok = False
        n_older = 0
    total = len(asset.candles)
    new_oldest = asset.candles[0]["time"]
    print(f"fetch_older_batch -> +{n_older} | total now {total} | oldest {new_oldest}")
    got_older = [c for c in asset.candles if c["time"] < before]
    if n_older <= 0 or not got_older:
        print("  !! FAIL: no older candles merged")
        ok = False
    else:
        print(f"  OK: {len(got_older)} candles older than before are in memory")

    # ------------------------------------------------- 2) fill_gap_once
    print("=" * 60)
    print("TEST 2: fill_gap_once (original method with real holes)")
    print("=" * 60)
    # زرع فجوات حقيقية في وسط الخط: نحذف 5 شموع متتالية
    line = [dict(c) for c in asset.candles]
    mid = len(line) // 2
    hole_ts = [line[i]["time"] for i in range(mid, mid + 5)]
    with_holes = [c for c in line if c["time"] not in hole_ts]
    asset.candles = with_holes
    mod.MT4_WRITER.sync_state["BRLUSD_otc"] = {
        "period": mod.PERIOD, "candles": list(with_holes),
        "last_write": 0, "last_price": float(with_holes[-1]["close"]),
    }
    mod.MT4_WRITER._gap_filled["BRLUSD_otc"] = True   # تجمد سابق
    # محاكاة واقعية: آخر سد ناجح قبل 301 ثانية (خارج فترة التحديث 300s —
    # نفس الشرط الأصلي في الكود المرجعي)
    mod.MT4_WRITER._gap_filled_at["BRLUSD_otc"] = time.time() - 301
    try:
        mod.MT4_WRITER.candle_store.set_gap_filled("BRLUSD_otc", True, time.time())
    except Exception as e:
        print(f"  (candle_store unavailable: {e})")

    class FA:
        symbol = "BRLUSD_otc"
        api_symbol = "BRLUSD_otc"
        candles = with_holes
        price = 1.0
        def write(self, force=False):
            pass

    fake2 = FakeClient()
    mod.CLIENT = fake2
    await mod.MT4_WRITER.fill_gap_once(fake2, FA(), mod.PERIOD)
    after = [c["time"] for c in mod.MT4_WRITER.sync_state["BRLUSD_otc"]["candles"]]
    filled = [t for t in hole_ts if t in after]
    if len(filled) == len(hole_ts):
        print(f"  OK: all {len(hole_ts)} holes filled via original method "
              f"(fetch calls: {len(fake2.get_candles_calls)})")
    else:
        print(f"  !! FAIL: filled {len(filled)}/{len(hole_ts)} holes")
        ok = False

    print("=" * 60)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
