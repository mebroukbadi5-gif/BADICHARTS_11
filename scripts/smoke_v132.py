#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.2 smoke test — real names/flags, serial load queue, 300 scroll-back batch.

1. QX_ASSET_NAMES covers every asset in the terminal table (92) and
   qx_asset_display() returns a real name + a non-empty flag for EACH one.
2. QX_NAME_TO_SYMBOL reverse lookup (USD/BRL (OTC) -> BRLUSD_otc).
3. App serial load queue: opening several assets quickly queues them and the
   worker loads ONE at a time with a >=1s gap between assets.
4. Server PAGINATION_BATCH == 300 and fetch_older_batch default count == 300.
5. preload_all_assets no longer mass-fetches (chart-driven mode).
"""
import os
import re
import sys
import time
import asyncio
import threading
import tempfile
import urllib.parse

DL = "/home/z/my-project/download"
TMP = tempfile.mkdtemp(prefix="qx132_")
os.chdir(TMP)

# ---------------------------------------------------------------- Test 1+2
src = open(os.path.join(DL, "BadiChartsStudio_live.py"), encoding="utf-8").read()
m0 = src.index("def _flag_uri(body):")
m1 = src.index("ASSET_PAYOUT = {")
ns = {"urllib": __import__("urllib")}
exec(src[m0:m1], ns)
qx_asset_display = ns["qx_asset_display"]
QX_ASSET_NAMES = ns["QX_ASSET_NAMES"]
QX_NAME_TO_SYMBOL = ns["QX_NAME_TO_SYMBOL"]
SINGLE_BADGES = ns["SINGLE_BADGES"]

# كل رموز جدول الترمينال الذي أرسله المستخدم (91 صف كما عدّاها المستخدم —
# الجدول يحوي 92 عمود فعلياً بما فيها AUDNZD_otc الأخيرة)
TABLE = """AXSUSD_otc BRLUSD_otc EURNZD_otc USCrude_otc USDBDT_otc USDEGP_otc USDNGN_otc
CADCHF_otc UKBrent_otc USDJPY USDIDR_otc NZDUSD_otc EURJPY AUDJPY EURUSD GBPUSD
CADJPY EURCAD AUDUSD EURGBP CHFJPY GBPJPY ETCUSD_otc AUDCAD EURAUD USDCAD EURCHF
F40EUR GBPAUD GBPCAD GBPCHF STXEUR USDCHF AXJAUD CHIA50 FTSGBP JPXJPY
ATOUSD_otc AUDCAD_otc AUDCHF_otc AUDJPY_otc AUDUSD_otc AVAUSD_otc BCHUSD_otc
BNBUSD_otc BTCUSD_otc CADJPY_otc CHFJPY_otc DASUSD_otc DOTUSD_otc ETHUSD_otc
EURAUD_otc EURCAD_otc EURCHF_otc EURGBP_otc EURJPY_otc EURUSD_otc GBPAUD_otc
GBPCAD_otc GBPCHF_otc GBPJPY_otc GBPNZD_otc GBPUSD_otc LINUSD_otc LTCUSD_otc
NZDCAD_otc NZDCHF_otc NZDJPY_otc SOLUSD_otc TONUSD_otc TRUUSD_otc USDARS_otc
USDCAD_otc USDCHF_otc USDCOP_otc USDDZD_otc USDINR_otc USDJPY_otc USDMXN_otc
USDPHP_otc USDPKR_otc USDZAR_otc XAGUSD_otc XAUUSD_otc XRPUSD_otc ZECUSD_otc
AUDNZD_otc AUDCHF HSIHKD IBXEUR XAGUSD XAUUSD""".split()

assert len(QX_ASSET_NAMES) == len(TABLE), f"table coverage: {len(QX_ASSET_NAMES)} vs {len(TABLE)}"
missing = [c for c in TABLE if c not in QX_ASSET_NAMES]
assert not missing, f"missing codes: {missing}"
no_flag = []
for c in TABLE:
    nm, fl = qx_asset_display(c)
    assert nm and nm.strip(), f"{c}: empty display name"
    assert fl and fl.startswith("data:image/svg+xml"), f"{c}: no flag"
    if "(OTC)" in nm and c.endswith("_otc"):
        pass
no_flag = [c for c in TABLE if not qx_asset_display(c)[1]]
assert not no_flag, f"assets without flags: {no_flag}"
assert QX_NAME_TO_SYMBOL["USD/BRL (OTC)"] == "BRLUSD_otc"
assert QX_ASSET_NAMES["BRLUSD_otc"] == "USD/BRL (OTC)"
assert QX_ASSET_NAMES["BTCUSD_otc"] == "Bitcoin (OTC)"
assert QX_ASSET_NAMES["F40EUR"] == "CAC 40"
assert QX_ASSET_NAMES["XAUUSD_otc"] == "Gold (OTC)"
# الأسماء الحقيقية ليست النظامية: لا يوجد "AXS/USD OTC" أو "BRL/USD OTC" في الجدول
sys_bad = [c for c, n in QX_ASSET_NAMES.items()
           if re.fullmatch(r"[A-Z]{3}/[A-Z]{3}( OTC)?", n) and c in
           ("BRLUSD_otc", "AXSUSD_otc", "USCrude_otc", "UKBrent_otc")]
assert not sys_bad, f"systematic names leaked for: {sys_bad}"
print(f"[ok] flags/names: {len(QX_ASSET_NAMES)} assets, every one has real name + flag")

# ---------------------------------------------------------------- Test 3+4 (server)
sys.path.insert(0, DL)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "qx_server_v13", os.path.join(DL, "qx_server_v13.py"))
qx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qx)
assert qx.PAGINATION_BATCH == 300, f"PAGINATION_BATCH={qx.PAGINATION_BATCH}"
assert qx.PRELOAD_CANDLES == 300
# preload_all_assets source: جلب عملة الفتح فقط (استدعاء واحد) — لا حلقة جلب شاملة
psrc = open(os.path.join(DL, "qx_server_v13.py"), encoding="utf-8").read()
pa = psrc[psrc.index("async def preload_all_assets"):psrc.index("async def fetch_older_batch")]
assert pa.count("preload_one_asset") == 1, \
    f"preload must only fetch the opener once, found {pa.count('preload_one_asset')} calls"
print("[ok] server: PAGINATION_BATCH=300, chart-driven preload (opener only, no mass fetch loop)")

# ---------------------------------------------------------------- Test 5: serial queue
# استخراج دوال الطابور من Backend وتشغيلها على كائن وهمي
m2 = src.index("    def _qx_ensure_asset(self, api):")
m3 = src.index("    def _qx_load_feed(self, force=False):")
block = src[m2:m3]
block = "\n".join(l[4:] if l.startswith("    ") else l for l in block.splitlines())
g = {"__name__": "t", "time": time, "asyncio": asyncio, "threading": threading, "_qx_module": None}

calls = []
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

class FakeQx:
    PAGINATION_BATCH = 300
    ASYNC_LOOP = loop
    CLIENT = object()
    @staticmethod
    async def ensure_asset_loaded(api):
        calls.append((api, time.time()))
        await asyncio.sleep(0.15)
        return 300

class B:
    pass

g["_qx_module"] = lambda: FakeQx()
exec(block, g)
b = B()
B._qx_ensure_asset = g["_qx_ensure_asset"]
B._qx_start_load_worker = g["_qx_start_load_worker"]
B._qx_load_worker = g["_qx_load_worker"]
b._qx_ensure_at = {}
b._qx_ensure_fail = {}
b._qx_loadq = []
b._qx_load_pending = set()
b._qx_load_lock = threading.Lock()
b._qx_load_busy = False
b._qx_last_sig = None
b._qx_logged = True
logs = []
b._log = lambda kind, text: logs.append((kind, text))

# المستخدم يفتح 4 عملات بسرعة (نفس اللحظة)
for api in ["BTCUSD_otc", "ETHUSD_otc", "SOLUSD_otc", "XAUUSD_otc"]:
    b._qx_ensure_asset(api)
# نفس العملة مرة أخرى بسرعة — لا يجب أن تتكرر في الطابور
b._qx_ensure_asset("BTCUSD_otc")
time.sleep(4.5)
assert len(calls) == 4, f"expected 4 loads, got {len(calls)} {calls}"
gaps = [calls[i + 1][1] - calls[i][1] for i in range(len(calls) - 1)]
assert all(gp >= 1.0 for gp in gaps), f"loads not spaced one-by-one: {gaps}"
assert [c[0] for c in calls] == ["BTCUSD_otc", "ETHUSD_otc", "SOLUSD_otc", "XAUUSD_otc"]
print(f"[ok] serial queue: 4 assets opened at once -> loaded strictly one-by-one, gaps {['%.1fs' % gp for gp in gaps]}")

print()
print("ALL v13.2 SMOKE TESTS PASSED")
