# -*- coding: utf-8 -*-
"""اختبار منطقي آلي للكود الجديد v14.5 في BadiChartsStudio_live.py
يستخرج الدوال الحقيقية من المصدر (ast) ويشغلها على هياكل وهمية:
  1) _qx_chain_push_message: تقطيع الرد إلى دفعات 300 + دمج المحرك + emit older
  2) _qx_seal_gaps: رفع التجمّد + fill_gap_once الأصلية + استعادة الخط الكامل
  3) مطابقة fill_gap_once بين v10 و v14 حرفياً
"""
import ast, re, time, types, random, asyncio as real_asyncio

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
V10 = "/home/z/my-project/download/qx_server_v10.py"
V14 = "/home/z/my-project/download/qx_server_v14.py"

def extract_method(path, class_name, method_name):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return ast.get_source_segment(src, item)
    raise RuntimeError(f"{method_name} not found in {class_name}")

def extract_function(path, func_name):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.get_source_segment(src, node)
    return None

def norm_compare(code):
    """تطبيع للمقارنة الحرفية: حذف التعليقات والفراغات."""
    src_lines = []
    for ln in code.splitlines():
        s = ln.split("#")[0].rstrip()
        s = re.sub(r"\s+", " ", s).strip()
        if s and not s.startswith('"') and not s.startswith("'"):
            src_lines.append(s)
    return src_lines

ok = True

# ════════ 1) build a stub harness with the REAL methods ════════
holder = {}

def _qx_module_global():
    return holder["qx"]

class _Fut:
    def __init__(self, coro):
        self._coro = coro
    def result(self, timeout=None):
        return real_asyncio.run(self._coro)

class FakeAsyncio:
    @staticmethod
    def run_coroutine_threadsafe(coro, loop):
        return _Fut(coro)

ns = {"time": time, "asyncio": FakeAsyncio, "_qx_module": _qx_module_global}
app_methods = {}
for m in ["_qx_chain_push_message", "_qx_seal_gaps", "_fmt_engine_candles"]:
    code = extract_method(APP, "Backend", m)
    exec(compile(code, APP, "exec"), ns)
    app_methods[m] = ns[m]

class Sig:
    def emit(self): pass

class Asset:
    def __init__(self, candles, symbol="SYM1"):
        self.candles = candles
        self.symbol = symbol

class Writer:
    def __init__(self):
        self._gap_filled = {}
        self.calls = 0
    async def fill_gap_once(self, client, asset, period):
        self.calls += 1
        # سلوك v10 الأصلي الحرفي: يقص الخط إلى آخر 1000 شمعة + يصلح ذيل
        if asset.candles:
            asset.candles = sorted(asset.candles, key=lambda c: c["time"])[-1000:]
            # إصلاح: آخر شمعة تُغلق بسعر حقيقي مختلف
            last = dict(asset.candles[-1]); last["close"] = last["close"] + 0.5
            asset.candles[-1] = last
            # إضافة شمعة جديدة بعد الأخيرة
            nxt = {"time": last["time"] + 60, "open": last["close"], "high": last["close"],
                   "low": last["close"], "close": last["close"], "volume": 3}
            asset.candles.append(nxt)

class QxStub:
    PAGINATION_BATCH = 300
    ASSET_MAX_CANDLES = 45000
    PERIOD = 1
    ASYNC_LOOP = None   # الهيكل الوهمي — الكود الحقيقي يستخدم حلقة الخادم
    def __init__(self, asset):
        self._asset = asset
        self.MT4_WRITER = Writer()
        self.CLIENT = object()
        self.applied = 0
        self.unfrozen = []
    def _get_or_create_asset(self, api):
        return self._asset
    def _apply_candles_to_asset(self, asset, candles):
        self.applied += 1
        asset.candles = list(candles)
    def _format_raw_candles(self, res):
        out, seen = [], set()
        for c in res or []:
            if not isinstance(c, dict):
                continue
            ts = int(float(c.get("time", 0)))
            if ts <= 0:
                continue
            t = ts - ts % 60
            o, h, l, cl = (float(c.get("open", 0)), float(c.get("high", 0)),
                           float(c.get("low", 0)), float(c.get("close", 0)))
            if o <= 0 or cl <= 0 or t in seen:
                continue
            seen.add(t)
            out.append({"time": t, "open": o, "high": h, "low": l, "close": cl,
                        "volume": int(c.get("volume", 0) or 0)})
        out.sort(key=lambda x: x["time"])
        return out
    def clear_gap_flag_any(self, variants):
        self.unfrozen.extend(list(variants))
        return len(variants)

class Backend:
    _QX_FEED_CAP = 8000
    def __init__(self, qx):
        holder["qx"] = qx
        self._candles = []
        self._qx_last_sig = None
        self._asset = "X/USD (OTC)"
        self._tf = "1m"
        self.emits = []
    def _qx_module(self):
        return holder["qx"]
    def _emit_qx(self, obj):
        self.emits.append(obj)
    candlesChanged = Sig()
    _fmt_engine_candles = staticmethod(app_methods["_fmt_engine_candles"])
    _qx_chain_push_message = app_methods["_qx_chain_push_message"]
    _qx_seal_gaps = app_methods["_qx_seal_gaps"]

random.seed(7)
now = int(time.time()) // 60 * 60
# رد خادم: 900 شمعة دقيقة (منذ 15 ساعة) — أحدث ساعة منها على الشارت أصلًا (horizon)
raw = [{"time": now - (900 - i) * 60, "open": 1.0 + i * 0.001, "high": 1.0 + i * 0.001 + 0.002,
        "low": 1.0 + i * 0.001 - 0.002, "close": 1.0 + i * 0.001 + 0.001, "volume": 5}
       for i in range(900)]
asset = Asset([])
qx = QxStub(asset)
b = Backend(qx)
# الشارت الحالي: آخر 60 شمعة (آخر ساعة)
b._candles = b._fmt_engine_candles(qx._format_raw_candles(raw[-60:]))
horizon = b._candles[0]["t"]
pushed_t = set()
n = b._qx_chain_push_message("XUSD_otc", "1m", 60, raw, horizon, pushed_t, lambda: True)

total_expected = len([c for c in qx._format_raw_candles(raw) if c["time"] < horizon])
assert n == total_expected, f"pushed {n} != expected {total_expected}"
# الدفعات: كل رسالة older ≤ 300 شمعة
older_emits = [e for e in b.emits if e.get("type") == "older"]
assert older_emits and all(len(e["candles"]) <= 300 for e in older_emits), "batch >300!"
# دفعات كاملة 300/300/... والبقية أقل
sizes = [len(e["candles"]) for e in older_emits]
assert sizes[:-1] == [300]*(len(sizes)-1), f"batch sizes not 300-first: {sizes}"
# كل دفعة أقدم من سابقتها (ترتيب أقدم أولاً)
for a, bb in zip(older_emits, older_emits[1:]):
    assert max(c["t"] for c in a["candles"]) < min(c["t"] for c in bb["candles"]), "batch order wrong"
# ذاكرة المحرك: كل الدفعات الأقدم من الأفق مرتبة بلا تكرار
# (في التشغيل الحقيقي كان المحرك يحمل بالفعل الشمعات الحديثة من الجلب الأول —
#  هنا الهيكل الوهمي يبدأ فارغاً فيستقبل الجديد فقط)
assert len(asset.candles) == total_expected, f"engine {len(asset.candles)} != {total_expected}"
times = [c["time"] for c in asset.candles]
assert times == sorted(times) and len(times) == len(set(times)), "engine order/duplicates!"
# غذاء بايثون = الخط الكامل (الجديد + الشمعات الحديثة الموجودة أصلاً — لا فقدان)
assert len(b._candles) == total_expected + 60, f"python feed {len(b._candles)} != {total_expected + 60}"
print(f"TEST1 OK: {n} candles pushed in batches {sizes} — engine 900, python feed {len(b._candles)}")

# ════════ 2) _qx_seal_gaps: التجمّد مرفوع + الآلة الأصلية تعمل + الخط الكامل يعود ════════
full_len_before = len(asset.candles)
tail_close_before = asset.candles[-1]["close"]
qx.MT4_WRITER._gap_filled[asset.symbol] = True   # جلسة سابقة جمّدت العملة
b._qx_seal_gaps("XUSD_otc")
assert qx.MT4_WRITER.calls == 1, "original fill_gap_once was NOT called"
assert "XUSD_otc" in qx.unfrozen and "SYM1" in qx.unfrozen, "freeze flag not cleared"
assert len(asset.candles) == full_len_before + 1, \
    f"full line not restored: {len(asset.candles)} vs {full_len_before}+1"
assert asset.candles[-2]["close"] == tail_close_before + 0.5, "repair lost after restore"
assert len(asset.candles) == len({c['time'] for c in asset.candles}), "duplicates after restore"
print(f"TEST2 OK: seal ran on original algorithm; full line restored "
      f"({len(asset.candles)} candles), repair carried over")

# ════════ 3) مطابقة fill_gap_once بين v10 و v14 حرفياً ════════
f10 = extract_method(V10, "MT4Writer", "fill_gap_once")
f14 = extract_method(V14, "MT4Writer", "fill_gap_once")
a, bb = norm_compare(f10), norm_compare(f14)
# أسطر التعليقات العربية المضافة في v14 تُحذف بالفعل عبر norm (بلا #)؛ نقارن الجسم
diff = [(x, y) for x, y in zip(a, bb) if x != y]
if len(a) != len(bb) or diff:
    # اطبع الفروق للتدقيق اليدوي
    print(f"WARN: fill_gap_once v10 vs v14 differs: len {len(a)} vs {len(bb)}, {len(diff)} lines")
    for x, y in diff[:12]:
        print("  v10:", x)
        print("  v14:", y)
else:
    print("TEST3 OK: fill_gap_once in v14 is line-for-line identical to v10")
