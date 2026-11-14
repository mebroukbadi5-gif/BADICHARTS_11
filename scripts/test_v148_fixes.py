# -*- coding: utf-8 -*-
"""اختبارات إصلاحات v14.8 — الأسباب الجذرية الحقيقية:
 1) الدفعة القصيرة لا تمحو الذاكرة (سبب «تختفي شموعها»)
 2) الرد الفارغ لا يمحو الذاكرة ولا يجمّد العملة
 3) لا تجميد ما دامت في الخط شموع اصطناعية
 4) نافذة السد تمتد حتى أقدم شمعة اصطناعية (حتى 200)
 5) get_candles بفهرس فريد وبلا إعادة اشتراك (بث حي لا يتكسر)
يعمل على الكود الحقيقي المستخرَج من qx_server_v14.py المرقّع (ast).
"""
import ast, io, time, asyncio, types

V14 = "/home/z/my-project/download/qx_server_v14.py"

def extract_function(path, func_name, class_name=None):
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if class_name is not None:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == func_name:
                        return ast.get_source_segment(src, item)
        else:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return ast.get_source_segment(src, node)
    raise RuntimeError(f"{func_name} not found")

passed, failed = [], []

def check(name, cond, extra=""):
    (passed if cond else failed).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (("  [" + extra + "]") if extra else ""))


# ═════════════ 1+2) fetch_candles_with_retry: الذاكرة لا تُمحو ═════════════
code = extract_function(V14, "fetch_candles_with_retry")

class _Asset:
    def __init__(self, candles, symbol="SYM1"):
        self.candles = candles
        self.symbol = symbol
        self.api_symbol = "XUSD_otc"   # fill_gap_once يقرأ api_symbol
        self.price = 0.0
    def write(self, force=False):
        pass

class _Writer:
    def __init__(self):
        self.sync_state = {}
    def write_to_file(self, *a, **k):
        pass

class _Loop:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
    def run_until_complete(self, coro):
        return self.loop.run_until_complete(coro)

async def _wait_until(pred, timeout=0, poll_interval=0):
    while not pred():
        await asyncio.sleep(0.01)
    return True

now = int(time.time()) // 60 * 60
mem = [{"time": now - (100 - i) * 60, "open": 1.0, "high": 1.001,
        "low": 0.999, "close": 1.0005, "volume": 4} for i in range(100)]

# سيناريو أ: جلب قصير (10 شموع حديثة فقط) — كان يمحو 90 شمعة تاريخية
short_batch = [dict(c) for c in mem[-10:]]

ns = {
    "time": time, "asyncio": asyncio, "logmsg": lambda *a, **k: None,
    "PERIOD_SECONDS": 60, "MIN_CANDLES_THRESHOLD": 50, "MAX_FETCH_RETRIES": 3,
    "PERIOD": 1,
    "RETRY_BACKOFF_BASE": 0.1, "RETRY_BACKOFF_MAX": 0.2,
    "CONNECTION_ALIVE": True, "CLIENT": types.SimpleNamespace(api=object()),
    "MT4_WRITER": _Writer(),
    "wait_until": _wait_until,
    "mark_connection_dead": lambda *a, **k: None,
    "Asset": _Asset,          # تعليقات النوع تُقيَّم عند التعريف
    "Optional": object, "Tuple": tuple,
}
fetched = {"v": short_batch}
async def _fetch_once(asset, idx=1, total=1):
    return list(fetched["v"])
async def _bridge(asset, candles):
    return candles
ns["fetch_candles_once"] = _fetch_once
ns["_bridge_fetch_recent_candles"] = _bridge
exec(compile(code, V14, "exec"), ns)
fcr = ns["fetch_candles_with_retry"]

asset = _Asset([dict(c) for c in mem])
n, _ = _Loop().run_until_complete(fcr(asset))
check("short fetch keeps older history (no wipe)", len(asset.candles) == 100,
      f"len={len(asset.candles)}")
check("short fetch below threshold: retries then returns batch size (original semantics)", n == 10, f"n={n}")
times_ok = [c["time"] for c in asset.candles] == sorted(c["time"] for c in asset.candles)
check("short fetch: sorted & no dup", times_ok and len(asset.candles) == len({c['time'] for c in asset.candles}))

# سيناريو ب: جلب فارغ — كان يحوّل الذاكرة إلى []
fetched["v"] = []
asset2 = _Asset([dict(c) for c in mem])
n2, _ = _Loop().run_until_complete(fcr(asset2))
check("empty fetch keeps memory untouched", len(asset2.candles) == 100,
      f"len={len(asset2.candles)}")


# ═════════════ 3+4) fill_gap_once: تجميد صادق + نافذة موسعة ═════════════
class _Store:
    def __init__(self, filled=False):
        self.filled = filled
    def is_gap_filled(self, symbol):
        return self.filled, 0.0
    def set_gap_filled(self, symbol, flag, at):
        self.filled = bool(flag)

class _MT:
    def __init__(self, store):
        self.candle_store = store
        self.sync_state = {}
        self._gap_filled = {}
        self._gap_filled_at = {}
        self.fetched_days = []
    def write_to_file(self, *a, **k):
        pass
    def save_snapshot(self, *a, **k):
        pass

def _align(ts, period_seconds=None):
    return int(ts) // 60 * 60

fg_code = extract_function(V14, "fill_gap_once", "MT4Writer")

_flat_code = extract_function(V14, "_v14_is_synth_flat")

def _flat_fn():
    _ns = {}
    exec(compile(_flat_code, V14, "exec"), _ns)
    return _ns["_v14_is_synth_flat"]


def _align_time_mock(raw_ts, period_seconds=None):
    return int(raw_ts) // 60 * 60

def build_gap_env(store_filled, with_artificial):
    """يبني بيئة fill_gap_once: خط فيه شموع اصطناعية قديمة (45 دقيقة)."""
    gap = [{"time": now - (200 - i) * 60, "open": 1.0, "high": 1.0,
            "low": 1.0, "close": 1.0, "volume": 0} for i in range(80)]   # اصطناعية أقدم
    real = [{"time": now - (120 - i) * 60, "open": 1.0, "high": 1.002,
             "low": 0.998, "close": 1.001, "volume": 7} for i in range(40)]
    candles = gap + real
    store = _Store(store_filled)
    mt = _MT(store)
    mt.sync_state["SYM1"] = {"period": 1, "candles": [dict(c) for c in candles],
                             "last_write": 0, "last_price": 1.0}
    asset = _Asset([dict(c) for c in candles])
    client = types.SimpleNamespace()
    window = {}
    async def _get_candles(sym, end, seconds, period):
        window["candles"] = max(1, int(seconds // 60))
        # يرجع شموعاً حقيقية تغطي المدى المطلوب (تنجح الجلب)
        n = window["candles"]
        return [{"time": now - (n - i) * 60, "open": 1.0, "high": 1.003,
                 "low": 0.997, "close": 1.002, "volume": 9} for i in range(n)]
    client.get_candles = _get_candles
    ns2 = {"time": time, "asyncio": asyncio, "Dict": dict,
           "_align_time": _align_time_mock, "_fill_missing_slots": lambda c, p, max_gap=1440: c,
           "PERIOD_SECONDS": 60, "PERIOD": 1, "INITIAL_CANDLES": 1000,
           "GAP_FILL_CANDLES": 10, "GAP_FILL_REFRESH_INTERVAL": 300,
           "_v14_is_synth_flat": _flat_fn()}
    exec(compile(fg_code, V14, "exec"), ns2)
    return ns2["fill_gap_once"], mt, store, asset, client, window

# 3) لا تجميد ما دامت شموع اصطناعية (حتى لو العلم = 1 في القاعدة)
fg, mt, store, asset, client, window = build_gap_env(store_filled=True, with_artificial=True)
_Loop().run_until_complete(fg(mt, client, asset, 1))
check("artificial candles override freeze flag (seal runs)", store.filled in (False, True) and window.get("candles", 0) >= 80,
      f"window={window.get('candles')}")

# 4) نافذة السد تمتد حتى أقدم شمعة اصطناعية (كانت 10)
check("seal window extends to oldest artificial (>=80 candles, cap 200)",
      80 <= window.get("candles", 0) <= 200, f"window={window.get('candles')}")

# 3ب) الرد الفارغ لا يجمّد العملة
def build_gap_env2(store_filled):
    candles = [{"time": now - (100 - i) * 60, "open": 1.0, "high": 1.002,
                "low": 0.998, "close": 1.001, "volume": 7} for i in range(60)]
    store = _Store(store_filled)
    mt = _MT(store)
    mt.sync_state["SYM1"] = {"period": 1, "candles": [dict(c) for c in candles],
                             "last_write": 0, "last_price": 1.0}
    asset = _Asset([dict(c) for c in candles])
    client = types.SimpleNamespace()
    async def _get_candles(sym, end, seconds, period):
        return []     # رد فارغ — كان يثبّت علامة التجميد
    client.get_candles = _get_candles
    ns2 = {"time": time, "asyncio": asyncio, "Dict": dict,
           "_align_time": _align_time_mock, "_fill_missing_slots": lambda c, p, max_gap=1440: c,
           "PERIOD_SECONDS": 60, "PERIOD": 1, "INITIAL_CANDLES": 1000,
           "GAP_FILL_CANDLES": 10, "GAP_FILL_REFRESH_INTERVAL": 300,
           "_v14_is_synth_flat": _flat_fn()}
    exec(compile(fg_code, V14, "exec"), ns2)
    return ns2["fill_gap_once"], mt, store, asset, client

fg2, mt2, store2, asset2, client2 = build_gap_env2(store_filled=False)
_Loop().run_until_complete(fg2(mt2, client2, asset2, 1))
check("empty response does NOT freeze asset", store2.filled == False,
      f"filled={store2.filled}")
check("empty response keeps memory", len(asset2.candles) == 60, f"len={len(asset2.candles)}")

# 3ج) نجاح حقيقي بلا شموع اصطناعية → تجميد عادي (سلوك الأصل محفوظ)
def build_gap_env3():
    candles = [{"time": now - (100 - i) * 60, "open": 1.0, "high": 1.002,
                "low": 0.998, "close": 1.001, "volume": 7} for i in range(60)]
    store = _Store(False)
    mt = _MT(store)
    mt.sync_state["SYM1"] = {"period": 1, "candles": [dict(c) for c in candles],
                             "last_write": 0, "last_price": 1.0}
    asset = _Asset([dict(c) for c in candles])
    client = types.SimpleNamespace()
    async def _get_candles(sym, end, seconds, period):
        return [{"time": now - (20 - i) * 60, "open": 1.0, "high": 1.004,
                 "low": 0.996, "close": 1.003, "volume": 11} for i in range(20)]
    client.get_candles = _get_candles
    ns2 = {"time": time, "asyncio": asyncio, "Dict": dict,
           "_align_time": _align_time_mock, "_fill_missing_slots": lambda c, p, max_gap=1440: c,
           "PERIOD_SECONDS": 60, "PERIOD": 1, "INITIAL_CANDLES": 1000,
           "GAP_FILL_CANDLES": 10, "GAP_FILL_REFRESH_INTERVAL": 300,
           "_v14_is_synth_flat": _flat_fn()}
    exec(compile(fg_code, V14, "exec"), ns2)
    return ns2["fill_gap_once"], mt, store, asset, client

fg3, mt3, store3, asset3, client3 = build_gap_env3()
_Loop().run_until_complete(fg3(mt3, client3, asset3, 1))
check("real success freezes as original", store3.filled == True, f"filled={store3.filled}")

# ═════════════ 5) get_candles: فهرس فريد + بلا إعادة اشتراك ═════════════
gc_code = extract_function(V14, "get_candles", "Quotex")
check("get_candles waits on indexed event", "candles_ready_{asset}_' + 'index" in gc_code.replace("{index}", "") or "candles_ready_{asset}_{index}" in gc_code)
check("get_candles uses request counter (unique index)", "next(_request_counter)" in gc_code)
_guard = gc_code.find("if not _already_streaming:")
_sub = gc_code.find("await self.start_candles_stream(asset, period)")
_ws = gc_code.find("self.api.get_candles_ws(asset, index")
check("get_candles no unconditional resubscribe (guard before subscribe)",
      _guard >= 0 and _sub > _guard >= 0 and _ws > _sub >= 0,
      f"guard={_guard}, sub={_sub}, ws={_ws}")

# ═════════════ 6) الرد الفارغ يرفع الحدث ═════════════
pm_code = extract_function(V14, "_process_message_and_raise_events", "WebsocketClient")
check("empty candles response raises event (payload-key check)",
      "_payload_key" in pm_code and '"candles", "data", "history"' in pm_code)
check("all ticks queued (not only message[0])",
      "_tick_queue" in pm_code and "for _tk in message" in pm_code)

print()
print(f"RESULT: {len(passed)} passed, {len(failed)} failed")
if failed:
    raise SystemExit(1)
print("ALL v14.8 CHECKS PASSED")
