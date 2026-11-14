#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_v153_flow.py — محاكاة وظيفية كاملة لمسار فتح العملة الجديد (v15.3):

  نقر المستخدم على عملة → ensure_asset_loaded → seed_history الأصلية (طلب واحد)
  → دفع فوري عبر _qx_push_feed_now → إطفاء دائرة التحميل فيظهر الشارت
  → سد خلفي واحد لعملة فُتحت فقط.

تُستخرج الدوال من الملف المبني وتُشغَّل على فضاء أسماء مزيّف (نفس أسلوب
الاختبارات السابقة) — بلا شبكة وبلا PySide6.
"""
import asyncio
import sys
import time
import types

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
src = open(APP, encoding="utf-8").read()

MARK = "_QX_ENGINE_SOURCE = r'''"
CLOSE = "\n'''"
s0 = src.index(MARK) + len(MARK)
e0 = src.index(CLOSE, s0)
embedded = src[s0:e0]

fails = []


def check(name, cond, extra=""):
    print(("[OK ] " if cond else "[FAIL] ") + name + ((" — " + str(extra)) if (extra and not cond) else ""))
    if not cond:
        fails.append(name)


def extract_async_fn(text, name):
    i = text.index("async def " + name)
    j = text.index("\nasync def ", i + 10)
    return text[i:j]


def extract_fn(text, name):
    i = text.index("def " + name)
    j = text.index("\ndef ", i + 10)
    return text[i:j]


# ═══ 1) محاكاة ensure_asset_loaded: seed ناجح ═══
g = {
    "asyncio": asyncio, "time": time, "types": types,
    "CLIENT": None, "MT4_WRITER": None, "MIN_CANDLES_THRESHOLD": 100,
    "QX_HISTORY_DAYS": 0.80, "PERIOD": 1, "PERIOD_SECONDS": 60,
    "GAP_FILL_CANDLES": 10, "logmsg": lambda m: None,
    "fetch_candles_with_retry": None, "realtime_stream": None,
    "_get_or_create_asset": None, "Asset": None,
    "ALL_STREAMING_ASSETS": [], "ASSET_MAX_CANDLES": 45000,
    "_apply_candles_to_asset": None, "MARK_CANDLES_MIN": 100,
}

seed_calls = []
fallback_calls = []
stream_started = []


class FakeAsset:
    def __init__(self):
        self.candles = []
        self.price = 0.0
        self.streaming = False
        self.stream_task = None
        self.symbol = "BRLUSD-OTC"
        self.api_symbol = "BRLUSD_otc"


class FakeWriter:
    async def seed_history(self, client, asset, period, days):
        seed_calls.append((days,))
        # محاكاة الأصل: طلب واحد يعيد ~1150 شمعة (0.80 يوم M1)
        t0 = int(time.time()) - int(days * 86400)
        asset.candles = [{"time": t0 + i * 60, "open": 1.0, "high": 1.1,
                          "low": 0.9, "close": 1.05, "volume": 5}
                         for i in range(int(days * 86400 // 60))]
        asset.price = asset.candles[-1]["close"]
        return True


async def fake_stream(asset):
    stream_started.append(asset.api_symbol)
    asset.streaming = True


fake_asset = FakeAsset()
g["CLIENT"] = types.SimpleNamespace(api=types.SimpleNamespace(state=None))
g["MT4_WRITER"] = FakeWriter()
g["realtime_stream"] = fake_stream
g["_get_or_create_asset"] = lambda api: fake_asset
g["fetch_candles_with_retry"] = None

code = extract_async_fn(embedded, "ensure_asset_loaded")
exec(compile(code, "<extract>", "exec"), g)
ensure_asset_loaded = g["ensure_asset_loaded"]

n = asyncio.run(ensure_asset_loaded("BRLUSD_otc"))
check("المسار: البث الحي بدأ", stream_started == ["BRLUSD_otc"])
check("المسار: طلب واحد seed_history بأيام الإعدادات (0.80)",
      len(seed_calls) == 1 and abs(seed_calls[0][0] - 0.80) < 1e-9)
check("المسار: الاحتياط لم يُستدعِ (الجلب نجح)", fallback_calls == [])
check("المسار: عدد الشموع المعاد = شموع الطلب الواحد",
      n == int(0.80 * 86400 // 60), f"n={n}")
check("المسار: الذاكرة ممتلئة (1000+ شمعة في طلب واحد)", len(fake_asset.candles) >= 1000)

# ═══ 2) محاكاة: فشل seed → الاحتياط مرة واحدة ═══
class FakeWriterFail:
    async def seed_history(self, client, asset, period, days):
        seed_calls.append(("fail",))
        return False


async def fake_fallback(asset, max_retries=1, idx=1, total=1):
    fallback_calls.append(max_retries)
    asset.candles = [{"time": int(time.time()) - i * 60, "open": 1.0,
                      "high": 1.1, "low": 0.9, "close": 1.05, "volume": 5}
                     for i in range(1150)]
    return len(asset.candles), 1


fake_asset2 = FakeAsset()
g["MT4_WRITER"] = FakeWriterFail()
g["fetch_candles_with_retry"] = fake_fallback
g["_get_or_create_asset"] = lambda api: fake_asset2

n2 = asyncio.run(ensure_asset_loaded("AUDCAD_otc"))
check("المسار: فشل الطلب الواحد → الاحتياط الأصلي مرة واحدة",
      fallback_calls == [1])
check("المسار: الشموع وصلت عبر الاحتياط", n2 == 1150)

# ═══ 3) محاكاة: العملة لديها شموع كافية → بلا أي طلب ═══
seed_calls.clear()
fake_asset3 = FakeAsset()
fake_asset3.candles = [{"time": int(time.time()) - i * 60, "open": 1.0,
                        "high": 1.1, "low": 0.9, "close": 1.05, "volume": 5}
                       for i in range(150)]
g["MT4_WRITER"] = FakeWriter()
g["_get_or_create_asset"] = lambda api: fake_asset3
n3 = asyncio.run(ensure_asset_loaded("EURUSD_otc"))
check("المسار: شموع كافية في الذاكرة → بلا أي طلب شبكة",
      len(seed_calls) == 0 and n3 == 150)

# ═══ 4) محاكاة: لقطة قديمة (آخر شمعة أقدم من 30 دقيقة) → جلب حقيقي ═══
class FakeWriterStale:
    async def seed_history(self, client, asset, period, days):
        seed_calls.append(("stale",))
        # اللقطة القديمة: آخر شمعة قبل 10 ساعات
        old_t = int(time.time()) - 10 * 3600
        asset.candles = [{"time": old_t - i * 60, "open": 1.0, "high": 1.1,
                          "low": 0.9, "close": 1.05, "volume": 5}
                         for i in range(900)]
        return True


fallback_calls.clear()
fake_asset4 = FakeAsset()
g["MT4_WRITER"] = FakeWriterStale()
g["fetch_candles_with_retry"] = fake_fallback
g["_get_or_create_asset"] = lambda api: fake_asset4
n4 = asyncio.run(ensure_asset_loaded("USDJPY_otc"))
check("المسار: اللقطة القديمة تتجاوز (آخر شمعة أقدم من نافذة السد)",
      fallback_calls == [1] and n4 == 1150)

print()
if fails:
    print(f"FAILED: {len(fails)} — " + ", ".join(fails))
    sys.exit(1)
print("ALL V15.3 FLOW CHECKS PASSED")
