# -*- coding: utf-8 -*-
"""اختبار سلوكي آلي لتدفق v15.4 في BadiChartsStudio_live.py
(طلب المستخدم: دائرة تحميل لكل عملة + الجلب الأصلي حرفياً + سد الأصل حرفياً
+ لا شموع إلى الشارت قبل اكتمال الجلب والسد)

يستخرج الدوال الحقيقية من المصدر (ast) ويشغلها على هياكل وهمية:
  1) المحرك ensure_asset_loaded — الجلب الأصلي fetch_candles_with_retry بلا
     أي طلب بديل، والعملة الممتلئة أصلاً لا تعاد
  2) عامل الجلب — السد الأصلي يكتمل قبل الدفع للشارت وإخفاء الدائرة
  3) مسارات فتح العملة كلها تُشعل الدائرة (وقبول الدفع فقط للعملة المسدودة)
  4) المضخة الحية لا تدفع شيئاً للشارت أثناء الدائرة
  5) حارس الفريم — شموع الدقيقة لا تُعرض على فريم آخر
"""
import ast, io, time, types, threading, asyncio as real_asyncio

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"

def extract_method(path, class_name, method_name, src_override=None):
    src = src_override if src_override is not None else io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return ast.get_source_segment(src, item)
    raise RuntimeError(f"{method_name} not found in {class_name}")

def extract_function(path, func_name, src_override=None):
    src = src_override if src_override is not None else io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.get_source_segment(src, node)
    return None

# ─── استخراج نص المحرك المدمج ───
app_src = io.open(APP, encoding="utf-8").read()
app_lines = app_src.split("\n")
_start = _end = None
for i, l in enumerate(app_lines):
    if l.startswith("_QX_ENGINE_SOURCE = r"):
        _start = i + 1
        break
for i in range(_start, len(app_lines)):
    if app_lines[i].strip() == "'''":
        _end = i
        break
engine_src = "\n".join(app_lines[_start:_end])
assert "async def ensure_asset_loaded" in engine_src
print(f"[ok] engine source extracted ({len(engine_src)} chars)")

ok_count = 0

# ═══════════ 1) المحرك: ensure_asset_loaded = الجلب الأصلي حرفياً ═══════════
class FakeTask:
    def __init__(self, coro):
        self._coro = coro
        try:
            self._coro.close()
        except Exception:
            pass
    def done(self):
        return True

class FakeAsyncioMod:
    @staticmethod
    def ensure_future(coro):
        return FakeTask(coro)

calls_engine = {"fetch": 0, "seed": 0}

async def fake_fetch(asset, max_retries=3, idx=1, total=1):
    calls_engine["fetch"] += 1
    # سلوك الجلب الأصلي: يملأ asset.candles من الخادم
    if not asset.candles:
        asset.candles = [{"time": 1000 + i * 60, "open": 1.0, "high": 1.1, "low": 0.9,
                          "close": 1.05, "volume": 5} for i in range(1000)]
    return len(asset.candles), 1

async def fake_seed(*a, **k):
    calls_engine["seed"] += 1
    return True

eng_ns = {
    "asyncio": FakeAsyncioMod,
    "CLIENT": types.SimpleNamespace(api=object()),   # اتصال حي
    "MIN_CANDLES_THRESHOLD": 100,
    "MAX_FETCH_RETRIES": 5,
    "fetch_candles_with_retry": fake_fetch,
    "MT4_WRITER": types.SimpleNamespace(seed_history=fake_seed),
    "realtime_stream": lambda asset: fake_fetch(asset),
    "logmsg": lambda m: None,
    "time": time,
    "_get_or_create_asset": None,   # يُملأ لكل حالة
}

class EAsset:
    def __init__(self, candles):
        self.candles = list(candles)
        self.symbol = "BRLUSD_otc"
        self.api_symbol = "BRLUSD_otc"
        self.streaming = False
        self.stream_task = FakeTask(None)   # مهمة «تعمل» — لا بث جديد

exec(compile(extract_function(APP, "ensure_asset_loaded", src_override=engine_src),
             "engine", "exec"), eng_ns)
ensure_loaded = eng_ns["ensure_asset_loaded"]

# 1a — عملة بلا شموع: الجلب الأصلي يُستدعى ولا seed_history
eng_ns["_get_or_create_asset"] = lambda api: EAsset([])
n = real_asyncio.run(ensure_loaded("BRLUSD_otc"))
assert n == 1000 and calls_engine["fetch"] == 1 and calls_engine["seed"] == 0, \
    f"engine fetch path broken: n={n} fetch={calls_engine}"
ok_count += 1
print(f"TEST1a OK: empty asset -> original fetch_candles_with_retry ran once "
      f"(n={n}), seed_history NEVER called")

# 1b — عملة ممتلئة أصلاً (>= العتبة): لا جلب مكرر
eng_ns["_get_or_create_asset"] = lambda api: EAsset(
    [{"time": 1000 + i * 60, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05,
      "volume": 5} for i in range(150)])
n2 = real_asyncio.run(ensure_loaded("BRLUSD_otc"))
assert n2 == 150 and calls_engine["fetch"] == 1, "already-loaded asset re-fetched!"
ok_count += 1
print(f"TEST1b OK: already-loaded asset ({n2} candles) -> no re-fetch, no extra requests")

# ═══════════ 2-5) التطبيق: الدائرة لكل عملة + السد قبل الدفع + البوابات ═══════════
app_ns = {"time": time, "threading": threading, "json": __import__("json")}

_holder = {"qx": None}

def _qx_module_global():
    return _holder["qx"]

app_ns["_qx_module"] = _qx_module_global

class Sig:
    def __init__(self):
        self.n = 0
    def emit(self):
        self.n += 1

METHODS = ["_qx_ensure_asset", "_qx_start_load_worker", "_qx_load_worker",
           "_qx_load_feed", "_qx_push_feed_now", "_qx_live_step",
           "_qx_loading_arm", "_qx_loading_clear", "_qx_engine_candles",
           "_fmt_engine_candles", "_qx_fetch_tf_async"]
for m in METHODS:
    code = extract_method(APP, "Backend", m)
    exec(compile(code, APP, "exec"), app_ns)

class WAsset:
    def __init__(self, candles):
        self.candles = list(candles)
        self.price = 1.05

class QxW:
    """محرك وهمي: شموع جاهزة في الذاكرة + الجلب يعيد العدد فوراً."""
    ASYNC_LOOP = None
    PAGINATION_BATCH = 700
    _TICK_CACHE = {}
    CLIENT = types.SimpleNamespace(api=object())
    def __init__(self, candles):
        self._asset = WAsset(candles)
        self.ensure_calls = 0
    async def ensure_asset_loaded(self, api):
        self.ensure_calls += 1
        return len(self._asset.candles)
    def _get_or_create_asset(self, api):
        return self._asset

class _Fut:
    def __init__(self, coro):
        self._coro = coro
    def result(self, timeout=None):
        return real_asyncio.run(self._coro)

class FakeAsyncio2:
    @staticmethod
    def run_coroutine_threadsafe(coro, loop):
        return _Fut(coro)

app_ns["asyncio"] = FakeAsyncio2

class Backend:
    _QX_FEED_CAP = 45000
    def __init__(self, qx, tf="1m"):
        _holder["qx"] = qx
        self._qx = qx
        self._candles = []
        self._asset = "USD/BRL (OTC)"
        self._tf = tf
        self._market = "otc"
        self._qx_symbols = {"USD/BRL (OTC)": "BRLUSD_otc"}
        self._qx_feed_key = ("", "")
        self._qx_last_sig = None
        self._qx_loading = False
        self._qx_loading_at = 0.0
        self._qx_loading_echo_at = 0.0
        self._qx_sealed = set()
        self._qx_load_pending = set()
        self._qx_loadq = []
        self._qx_load_lock = threading.Lock()
        self._qx_load_busy = False
        self._qx_ensure_fail = {}
        self._qx_ensure_at = {}
        self._qx_logged = True
        self._py_mods = []
        self._qx_deep_seen = 0
        self._qx_resync_pending = False
        self._qx_tick_stamp = None
        self._qx_board_at = 0.0
        self._qx_pre_log = 0.0
        self.candlesChanged = Sig()
        self.emits = []
        self.logs = []
        self.calls = []          # تسلسل الأحداث: seal قبل push أم لا
    def _qx_module(self):
        return self._qx
    def _emit_qx(self, obj):
        self.emits.append(obj)
    def _log(self, kind, msg):
        self.logs.append((kind, msg))
    def _tf_sec(self):
        return {"1m": 60, "5m": 300, "5s": 5}.get(self._tf, 60)
    def _api_from_display(self, name):
        return self._qx_symbols.get(name, "")
    def _compute_py(self):
        pass
    def _qx_seal_gaps(self, api):
        self.calls.append(("seal", api))
    def _qx_push_feed_now_rec(self, api):
        self.calls.append(("push", api))
        return app_ns["_qx_push_feed_now"](self, api)
    # دوال الشموع الحقيقية من التطبيق
    _fmt_engine_candles = staticmethod(app_ns["_fmt_engine_candles"])
    _qx_engine_candles = app_ns["_qx_engine_candles"]
    _qx_loading_arm = app_ns["_qx_loading_arm"]
    _qx_loading_clear = app_ns["_qx_loading_clear"]
    _qx_ensure_asset = app_ns["_qx_ensure_asset"]
    _qx_load_worker = app_ns["_qx_load_worker"]
    _qx_load_feed = app_ns["_qx_load_feed"]
    _qx_push_feed_now = _qx_push_feed_now_rec
    _qx_live_step = app_ns["_qx_live_step"]

    def _qx_start_load_worker(self):
        # في الاختبار: نفس عامل التشغيل الحقيقي — متزامن أو محاكاة غير متزامنة
        if getattr(self, "_sync_worker", True):
            self._qx_load_worker()
        else:
            self._worker_started = True   # الخيط الحقيقي يجري بالخلفية

def fmt_candles(n, start=None):
    now60 = int(time.time()) // 60 * 60
    s = start if start is not None else now60 - n * 60
    return [{"time": s + i * 60, "open": 1.0, "high": 1.1, "low": 0.9,
             "close": 1.05, "volume": 5} for i in range(n)]

# ─── 2) عامل الجلب: الجلب الأصلي → سد الأصل → الدفع → إخفاء الدائرة ───
qxw = QxW(fmt_candles(800))
b = Backend(qxw)
b._qx_ensure_asset("BRLUSD_otc")   # العامل الحقيقي يعمل متزامناً حتى الاكتمال
assert qxw.ensure_calls == 1, "engine ensure not called"
assert b.calls == [("seal", "BRLUSD_otc"), ("push", "BRLUSD_otc")], \
    f"order broken: {b.calls}"   # السد قبل الدفع — طلب المستخدم الحرفي
_emits = [e for e in b.emits if e.get("type") == "chartload"]
assert _emits and _emits[0].get("active") is True and _emits[-1].get("active") is False, \
    f"spinner events wrong: {_emits}"   # الدائرة أُشعلت أولاً وأُخفت أخيراً
assert b._candles and len(b._candles) > 0, "candles NOT pushed after seal"
assert b._qx_feed_key == (b._asset, "1m"), "feed key not set after push"
assert b._qx_loading is False, "spinner NOT cleared after push"
assert ("BRLUSD_otc", "1m") in b._qx_sealed, "asset not marked sealed"
ok_count += 1
print(f"TEST2 OK: worker sequence = fetch(original) -> seal -> push -> spinner off "
      f"({len(b._candles)} candles on chart, spinner armed+cleared)")

# ─── 3) _qx_load_feed: غير مسدودة لا تُدفع من الذاكرة (تمر بالعامل)، مسدودة تُعرض فوراً ───
qx2 = QxW(fmt_candles(500))
b2 = Backend(qx2)
b2._sync_worker = False          # محاكاة العامل الحقيقي (خيط خلفي — لا اكتمال فوري)
b2._qx_load_feed(force=True)          # غير مسدودة
assert not b2._candles, "unsealed asset was pushed directly from memory!"
assert b2._qx_loadq == ["BRLUSD_otc"], "unsealed asset not routed to worker"
assert b2._qx_loading is True, "spinner not armed for unsealed route"
assert getattr(b2, "_worker_started", False), "load worker not started"
assert not [c for c in b2.calls if c[0] == "push"], "push happened before fetch+seal!"
ok_count += 1
print("TEST3a OK: unsealed asset with engine candles -> NOT pushed, routed to "
      "fetch+seal worker, spinner on")

b3 = Backend(qx2)
b3._sync_worker = False
b3._qx_sealed.add(("BRLUSD_otc", "1m"))
b3._qx_load_feed(force=True)          # مسدودة سابقاً
assert b3._candles, "sealed asset not pushed instantly"
assert b3._qx_feed_key == (b3._asset, "1m")
assert b3._qx_loading is False, "spinner not cleared for instant ready feed"
ok_count += 1
print("TEST3b OK: already sealed asset -> instant push + spinner off")

# ─── 4) المضخة الحية أثناء الدائرة: لا دفع إطلاقاً ───
qx4 = QxW(fmt_candles(300))
b4 = Backend(qx4)
b4._qx_loading = True
b4._qx_loading_at = time.time()
b4._qx_live_step()
assert not b4._candles, "live pump pushed candles WHILE loading spinner on!"
ok_count += 1
print("TEST4a OK: live pump pushes NOTHING while loading circle is on")

b4._qx_loading = False
b4._qx_live_step()
assert b4._candles, "live pump did not feed chart after loading completed"
ok_count += 1
print(f"TEST4b OK: live pump feeds chart after loading done ({len(b4._candles)} candles)")

# ─── 5) حارس الفريم: شموع الدقيقة لا تُدفع لفريم 5m ───
qx5 = QxW(fmt_candles(400))
b5 = Backend(qx5, tf="5m")
b5._qx_loading = True
b5._qx_push_feed_now("BRLUSD_otc")
assert not b5._candles, "1m candles leaked into 5m chart!"
assert b5._qx_loading is True, "spinner wrongly cleared for non-1m feed"
ok_count += 1
print("TEST5 OK: tf guard — engine 1m candles never pushed to 5m chart")

print(f"\nALL {ok_count} TESTS PASSED (v15.4 flow)")
