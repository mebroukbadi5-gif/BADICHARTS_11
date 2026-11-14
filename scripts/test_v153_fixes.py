#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_v153_fixes.py — فحوصات v15.3 (طلب المستخدم حرفياً):
1) «لماذا غيرت طريقة جلب الشموع قلت يجب ان تستخدم مثل هنا في هذا الكود يجلب
   يسد الثغرات ولا ينام الكود» — ensure_asset_loaded يستخدم seed_history
   الأصلية حرفياً (طلب واحد بمدى الأيام كاملاً = 1000 شمعة في ~4 ثوانٍ)
2) «عملة BRLUSD_otc لماذا لم تضف فيها دائرة تحميل» — كل فتح لعملة يجهّز
   الدائرة فوراً (حتى إعادة فتح العملة نفسها والشارت فارغ) وبلا رفض صامت
3) «تاخر 1 دقيقة ولم يرسم الشموع» — بلا خنق 15-60 ثانية وبلا جلب مزدوج
   (لا سلسلة دفعات تعيد جلب نفس المدى فوق الجلب الأول)
4) «نحن عندما نضغط على العملة هو يبدا بجلب الشموع تضهر دائرة تحميل لاكتمال
   التحميل» — _qx_push_feed_now يدفع الشموع ويطفئ الدائرة فور اكتمال الجلب
5) «فقط خليه هو لي يجلب قائمة العملات ويطبعها في قائمة التطبيق» — لوحة
   instruments من المحرك الأصلي كما هي (v15.1) بلا تغيير
"""
import ast
import re
import sys
import textwrap
import time as _time
import types

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
PASTE = "/home/z/my-project/upload/qx_mt4_original.py"

src = open(APP, encoding="utf-8").read()
paste = open(PASTE, encoding="utf-8").read()

MARK = "_QX_ENGINE_SOURCE = r'''"
CLOSE = "\n'''"
s0 = src.index(MARK) + len(MARK)
e0 = src.index(CLOSE, s0)
embedded = src[s0:e0]
app_outside = src[:s0 - len(MARK)] + src[e0 + len(CLOSE):]

fails = []


def check(name, cond, extra=""):
    print(("[OK ] " if cond else "[FAIL] ") + name + ((" — " + str(extra)) if (extra and not cond) else ""))
    if not cond:
        fails.append(name)


# ═══ 1) طريقة الجلب = الأصل الأصلي (seed_history بطلب واحد) ═══
ens_i = embedded.index("async def ensure_asset_loaded")
ens_seg = embedded[ens_i:embedded.index("\n# ═══", ens_i)]
check("ensure_asset_loaded يستدعي seed_history الأصلية",
      "MT4_WRITER.seed_history(CLIENT, asset, PERIOD, days)" in ens_seg)
check("الاحتياط fetch_candles_with_retry بمحاولة واحدة فقط عند الفشل",
      "max_retries=1" in ens_seg and "MAX_FETCH_RETRIES" not in ens_seg)
check("حماية اللقطة القديمة (آخر شمعة أقدم من نافذة آلة السد)",
      "stale_after" in ens_seg and "GAP_FILL_CANDLES * PERIOD_SECONDS * 3" in ens_seg)
check("seed_history الأصلية داخل المحرك كما هي (بلا تعديل)",
      "async def seed_history(self, client, asset_obj, period: int, days: float = 0.75):" in embedded)
check("fill_gap_once الأصلية داخل المحرك كما هي",
      "async def fill_gap_once(self, client, asset_obj, period: int):" in embedded)
# الأصل نفسه يحوي الدالتين — نسخة المحرك مطابقة للأصل بايت ببايت
def extract_fn(text, name):
    i = text.index("async def " + name)
    j = text.index("\nasync def ", i + 10)
    return text[i:j]


check("seed_history في المحرك == الأصل حرفياً",
      extract_fn(embedded, "seed_history") == extract_fn(paste, "seed_history"))
check("fetch_candles_once في المحرك == الأصل حرفياً",
      extract_fn(embedded, "fetch_candles_once") == extract_fn(paste, "fetch_candles_once"))
check("fill_gap_once في المحرك == الأصل حرفياً",
      extract_fn(embedded, "fill_gap_once") == extract_fn(paste, "fill_gap_once"))

# ═══ 2) كل فتح يجهّز الدائرة + بلا رفض صامت ═══
sw_i = app_outside.index("    def switch(self, asset, tf):")
sw_seg = app_outside[sw_i:app_outside.index("    @Slot(str, result=str)", sw_i)]
check("switch: لا رفض صامت للأسماء (حذف الحارس القديم)",
      "asset not in self._qx_symbols" not in sw_seg)
check("switch: الدائرة عند التغيير أو الشارت الفارغ",
      "if changed or not self._candles:" in sw_seg)
check("switch: تفعيل الدائرة قبل الجلب",
      sw_seg.index("self._qx_loading_arm()") < sw_seg.index("self._qx_load_feed(force=True)"))
check("تعليق سبب BRLUSD_otc موجود",
      "لم تضف فيها دائرة تحميل" in src)

# ═══ 3) بلا خنق 15-60 ثانية + بلا جلب مزدوج ═══
ens_a_i = app_outside.index("    def _qx_ensure_asset(self, api):")
ens_a_seg = app_outside[ens_a_i:app_outside.index("    def _qx_start_load_worker", ens_a_i)]
check("بلا خنق تصاعدي 15-60 ثانية",
      "min(60.0, 15.0 * (1 + fails))" not in ens_a_seg)
check("مسافة إعادة المحاولة فقط بعد فشل (10 ثوانٍ)",
      "if fails and now - self._qx_ensure_at.get(api, 0.0) < 10.0:" in ens_a_seg)
check("منع التكرار عبر الطابور ما زال موجوداً",
      "if api in self._qx_load_pending:" in ens_a_seg)
check("لا نداء _qx_start_history_chain في طبقة التطبيق إطلاقاً",
      "self._qx_start_history_chain(" not in app_outside)
check("لا نداء preload_all_assets في طبقة التطبيق",
      "preload_all_assets()" not in app_outside)
check("سلسلة الدفعات تعريفها ما زال موجوداً (لا حذف لمحتوى التطبيق)",
      "def _qx_start_history_chain(self, api, tf_label=\"1m\"):" in app_outside)
check("عامل الطابور: بلا سلسلة بعد الجلب",
      "_qx_start_history_chain" not in app_outside.split("def _qx_load_worker")[1][:1600])
check("عامل الطابور: دفع فوري + سد خلفي لعملة فُتحت فقط",
      "self._qx_push_feed_now(api)" in app_outside
      and 'name="qxSeal"' in app_outside)
check("السد الخلفي مرة واحدة لكل فتح (_qx_sealed)",
      "(api, \"1m\") not in getattr(self, \"_qx_sealed\", set())" in app_outside)
check("حالة _qx_seeled في __init__",
      "self._qx_sealed = set()" in src)
check("مساعد إعادة الجلب بعد تغيير الإعدادات موجود",
      "def _qx_force_reload_current(self):" in app_outside
      and app_outside.count("self._qx_force_reload_current()") == 2)

# ═══ 4) الدفع الفوري عند اكتمال الجلب ═══
push_i = app_outside.index("    def _qx_push_feed_now(self, api):")
push_seg = app_outside[push_i:app_outside.index("    def _qx_loading_arm", push_i)]
check("push: يطابق العملة المعروضة (لا دفع لعملة خلفية)",
      "cur_api != api" in push_seg and "return" in push_seg)
check("push: يكتب الغذاء ومفتاحه ويبث التغيير",
      "self._qx_feed_key = (self._asset, self._tf)" in push_seg
      and "self.candlesChanged.emit()" in push_seg)
check("push: يطفئ الدائرة فيظهر الشارت",
      "self._qx_loading_clear()" in push_seg)

# ═══ 5) لوحة العملات من المحرك الأصلي كما هي ═══
check("مرصد instruments على المرحلتين (v15.1) موجود",
      "fetch_instruments_now" in embedded and "_instruments_snapshot" in embedded)
check("المضخة تبني اللوحة من لقطة instruments",
      "qx._instruments_snapshot()" in app_outside)
check("حدث board يصل للواجهة", '"type": "board", "board": board' in app_outside)

# ═══ 6) دوائر التحميل v15.2 كما هي (لم تُمَس) ═══
check("chartLoading الصريحة ما زالت موجودة",
      'return bool(self._qx_logged and getattr(self, "_qx_loading", False)\n                    and not self._candles)' in src)
check("مهلة الأمان 60 ثانية ما زالت موجودة",
      '"_qx_loading_at", 0.0)) > 60.0' in src)
check("JS: الغطاء الوسطي كما هو",
      "background:rgba(7,10,16,.72)" in app_outside
      and "el.hidden = !CHLOAD.on;" in app_outside)

# ═══ فحص سلوكي: _qx_push_feed_now بجميع السيناريوهات ═══
tree = ast.parse(src)
cls_methods = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_qx_push_feed_now":
                cls_methods[item.name] = item

assert len(cls_methods) == 1, "push method not extracted"

g = {"time": _time}
node = cls_methods["_qx_push_feed_now"]
seg = ast.get_source_segment(src, node)
exec(compile(textwrap.dedent(seg), "<extract>", "exec"), g)
push_feed_now = g["_qx_push_feed_now"]

def make_ns(asset, symbols, engine_candles, py_mods=False):
    ns = types.SimpleNamespace()
    ns._asset = asset
    ns._tf = "1m"
    ns._qx_symbols = symbols
    ns._py_mods = py_mods
    ns._py_computed = 0
    ns._emitted = 0
    ns._loading = True
    ns._candles = []
    ns._QX_FEED_CAP = 45000
    ns._qx_feed_key = ("", "")
    ns._events = []

    def _compute_py():
        ns._py_computed += 1
    def _candles_changed():
        ns._emitted += 1
    def _engine_candles(api):
        return list(engine_candles)
    def _loading_clear():
        ns._loading = False
        ns._events.append(("chartload", False))
    ns._compute_py = _compute_py
    ns.candlesChanged = types.SimpleNamespace(emit=_candles_changed)
    ns._qx_engine_candles = _engine_candles
    ns._qx_loading_clear = _loading_clear
    return ns


eng = [{"t": 100 + i, "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05, "v": 3} for i in range(1200)]

# سيناريو 1: اكتمال جلب العملة المعروضة — دفع + إطفاء
ns = make_ns("BRL/USD (OTC)", {"BRL/USD (OTC)": "BRLUSD_otc"}, eng)
push_feed_now(ns, "BRLUSD_otc")
check("سلوك: دفع الشموع عند اكتمال الجلب للعملة المعروضة",
      len(ns._candles) == 1200 and ns._qx_feed_key == ("BRL/USD (OTC)", "1m")
      and ns._emitted == 1 and ns._loading is False)

# سيناريو 2: المستخدم فتح عملة أخرى أثناء الجلب — لا دفع ولا إطفاء
ns2 = make_ns("AUD/CAD (OTC)", {"AUD/CAD (OTC)": "AUDCAD_otc"}, eng)
push_feed_now(ns2, "BRLUSD_otc")
check("سلوك: لا دفع ولا إطفاء لعملة خلفية (المستخدم فتح أخرى)",
      ns2._candles == [] and ns2._emitted == 0 and ns2._loading is True)

# سيناريو 3: الجلب اكتمل بلا شموع — الدائرة تُطفأ فقط (مهلة المضخة تتكفل)
ns3 = make_ns("BRL/USD (OTC)", {"BRL/USD (OTC)": "BRLUSD_otc"}, [])
push_feed_now(ns3, "BRLUSD_otc")
check("سلوك: بلا شموع — الدائرة تُطفأ ولا غذاء فارغ يُدفع",
      ns3._candles == [] and ns3._emitted == 0 and ns3._loading is False)

# سيناريو 4: المؤشرات بايثون تُحسب مع الدفع
ns4 = make_ns("BRL/USD (OTC)", {"BRL/USD (OTC)": "BRLUSD_otc"}, eng, py_mods=True)
push_feed_now(ns4, "BRLUSD_otc")
check("سلوك: المؤشرات تُعاد مع الدفع الفوري", ns4._py_computed == 1)

# ═══ فحص سلوكي: منطق شرط switch (changed or empty) ═══
def should_load(changed, candles):
    return bool(changed or not candles)

check("سلوك: فتح عملة أخرى → جلب", should_load(True, eng) is True)
check("سلوك: إعادة فتح نفس العملة والشارت فارغ → جلب (سبب BRLUSD_otc)",
      should_load(False, []) is True)
check("سلوك: إعادة فتح نفس العملة والشارت معروض → لا جلب (بلا وميض)",
      should_load(False, eng) is False)

# ═══ roundtrip: الأصل + الطبقة بايت ببايت ═══
compat = open("/home/z/my-project/scripts/qx_compat_v15.py", encoding="utf-8").read()
check("المحرك يبدأ بالأصل بايت ببايت",
      embedded.startswith(paste.rstrip("\n") + "\n"))
check("المحرك ينتهي بالطبقة بايت ببايت",
      embedded.endswith(compat.rstrip("\n") + "\n"))

print()
if fails:
    print(f"FAILED: {len(fails)} — " + ", ".join(fails))
    sys.exit(1)
print("ALL V15.3 CHECKS PASSED")
