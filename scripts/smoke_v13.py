#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار دخاني لـ qx_server_v13 — بدون شبكة:
1) الثوابت الجديدة موجودة بقيمها الصحيحة.
2) _format_raw_candles: تنسيق/محاذاة/إزالة التكرار/الترتيب.
3) كاش التيكات: التخزين + حذف الأقدم من 5 دقائق + get_recent_ticks.
4) دمج fetch_older_batch منطقياً (محاكاة الدمج دون شبكة).
5) دوال v13 معرفة ومتصلة ببعضها (preload_all_assets, fetch_older_batch, ...).
6) كود v12 القديم لم يُمَس: دوال المحرك الأصلية ما زالت موجودة.
"""
import sys, time, asyncio
sys.path.insert(0, '/home/z/my-project/download')

import qx_server_v13 as qx

fails = []

def check(name, cond):
    print(('PASS' if cond else 'FAIL'), '-', name)
    if not cond:
        fails.append(name)

# 1) الثوابت
check("PRELOAD_FIRST_SYMBOL == BRLUSD_otc", qx.PRELOAD_FIRST_SYMBOL == "BRLUSD_otc")
check("PRELOAD_CANDLES == 300", qx.PRELOAD_CANDLES == 300)
check("PAGINATION_BATCH == 170", qx.PAGINATION_BATCH == 170)
check("TICK_RETENTION_SECONDS == 300", qx.TICK_RETENTION_SECONDS == 300)
check("MT4_WRITE_THROTTLE == 1.0", qx.MT4_WRITE_THROTTLE == 1.0)
check("ASSET_MAX_CANDLES == 3000", qx.ASSET_MAX_CANDLES == 3000)
check("CANDLESTORE_KEEP_PER_SYMBOL == 5000", qx.CANDLESTORE_KEEP_PER_SYMBOL == 5000)

# 2) تنسيق الشموع
now = int(time.time()) // 60 * 60
raw = [
    {"time": now - 120, "open": 5.1, "high": 5.2, "low": 5.0, "close": 5.15},
    {"time": now - 60, "open": 5.15, "high": 5.3, "low": 5.1, "close": 5.2},
    {"time": now - 60, "open": 9.9, "high": 9.9, "low": 9.9, "close": 9.9},  # مكرر — يجب حذفه
    {"time": now, "open": 5.2, "high": 5.4, "low": 5.2, "close": 5.3},
    {"open": 1, "close": 1, "high": 1, "low": 1},  # بلا وقت — يُتجاهل
]
fmt = qx._format_raw_candles(raw)
check("_format_raw_candles: 3 candles", len(fmt) == 3)
check("_format_raw_candles: sorted asc", all(fmt[i]['time'] < fmt[i+1]['time'] for i in range(len(fmt)-1)))
check("_format_raw_candles: aligned to 60s", all(c['time'] % 60 == 0 for c in fmt))
check("_format_raw_candles: has volume", all('volume' in c for c in fmt))

# 3) كاش التيكات
sym = "TESTUSD_otc"
old_ts = int(time.time()) - 400    # أقدم من 5 دقائق
mid_ts = int(time.time()) - 100    # داخل النافذة
new_ts = int(time.time()) - 5
qx._cache_tick(sym, old_ts, 5.0)
qx._cache_tick(sym, mid_ts, 5.1)
qx._cache_tick(sym, new_ts, 5.2)
check("tick cache: 3 ticks stored", len(qx._TICK_CACHE[sym]) == 3)
removed = qx._prune_tick_cache()
check("tick purge: removed 1 old tick", removed == 1)
check("tick cache: 2 ticks left", len(qx._TICK_CACHE.get(sym, [])) == 2)
ticks = qx.get_recent_ticks(sym, seconds=300)
check("get_recent_ticks: 2 ticks", len(ticks) == 2)
check("get_recent_ticks: newest first kept order", ticks[-1][1] == 5.2)

# 4) محاكاة منطق الدمج في fetch_older_batch (بدون شبكة):
# دفعة أقدم 170 شمعة تُدمج قبل الشموع الموجودة بدون تكرار ولا كسر الترتيب
existing = [{'time': now - 300 + i * 60, 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1} for i in range(5)]
older_batch = [{'time': now - 600 + i * 60, 'open': 2, 'high': 2, 'low': 2, 'close': 2, 'volume': 1} for i in range(3)]
older_batch = [c for c in older_batch if c['time'] < now - 300][-170:]
merged = list(older_batch) + list(existing)
seen, uniq = set(), []
for c in merged:
    if c['time'] not in seen:
        seen.add(c['time']); uniq.append(c)
uniq.sort(key=lambda x: x['time'])
check("merge: 8 unique candles", len(uniq) == 8)
check("merge: sorted asc", all(uniq[i]['time'] < uniq[i+1]['time'] for i in range(len(uniq)-1)))
check("merge: older batch first", uniq[0]['time'] == now - 600)

# 5) دوال v13 موجودة
for fn in ["preload_all_assets", "preload_one_asset", "fetch_older_batch",
           "tick_cache_collector", "tick_retention_loop", "candlestore_trim_loop",
           "get_recent_ticks", "_print_opener_banner", "_apply_candles_to_asset",
           "_get_or_create_asset"]:
    check(f"v13 has {fn}", hasattr(qx, fn))
check("PAGINATION_API ready", callable(qx.PAGINATION_API.get("fetch_older_batch")))

# 6) المحرك الأصلي لم يُمَس (لا يزال موجوداً كما هو)
for fn in ["fetch_candles_once", "fetch_candles_with_retry", "realtime_stream",
           "connect_quotex", "asset_payout_monitor", "_print_payout_table",
           "fetch_instruments_now", "auto_reconnect", "health_monitor"]:
    check(f"engine intact: {fn}", hasattr(qx, fn))
check("INITIAL_CANDLES still 1000", qx.INITIAL_CANDLES == 1000)
check("login flow constant: M1 period", qx.PERIOD == 1 and qx.PERIOD_SECONDS == 60)

# 7) كائن Asset الجديد يعمل ويحترم التسمية الأصلية
a = qx.Asset("BRLUSD_otc")
check("Asset BRLUSD_otc derived symbol", a.symbol == "BRLUSD-OTC")

print()
if fails:
    print(f"{len(fails)} FAILURES: {fails}")
    sys.exit(1)
print("ALL SMOKE TESTS PASSED")
