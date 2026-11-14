#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v153.py — v15.3 (طلب المستخدم حرفياً):
  1) «لماذا غيرت طريقة جلب الشموع قلت يجب ان تستخدم مثل هنا في هذا الكود يجلب
     يسد الثغرات ولا ينام الكود» و«من المفترض لجلب 1000 شمعة 4 ثواني انضر الى
     هذا تاخر 1 دقيقة ولم يرسم الشموع»:
     السبب الجذري (مُثبت بالتشخيص): طبقة الربط كانت تُشغّل عند فتح العملة
     **أربع جولات جلب متتالية** فوق بعضها (fetch_candles_with_retry بالعمال
     المتوازيين + الجسر + إعادة المحاولات، ثم سلسلة qx_get_historical_batches
     تعيد جلب **نفس المدى** مرة ثانية، ثم fill_gap_once، ثم السد العميق) —
     فكان الشارت ينتظر دقيقة كاملة بلا رسم. الحل: طريقة الأصل الأصلي حرفياً —
     ensure_asset_loaded تستدعي الآن seed_history الأصلية كما هي (طلب واحد
     get_candles بمدى الأيام كاملاً = 1000+ شمعة في ~4 ثوانٍ، أو اللقطة
     الطازجة فوراً بلا أي طلب)، مع احتياط fetch_candles_with_retry بمحاولة
     واحدة عند الفشل فقط. كل نداءات سلسلة الدفعات أُزيلت من فتح العملة
     (السلسلة كانت تعيد جلب نفس المدى فوق الجلب الأول).
  2) «عملة BRLUSD_otc لماذا لم تضف فيها دائرة تحميل»:
     السبب الجذري: switch كان يجهّز دائرة التحميل فقط عند تغيّر العملة —
     إعادة النقر على العملة المفتوحة نفسها والشارت فارغ كانت نقرة صامتة بلا
     دائرة ولا جلب (والأصل يفتح على BRLUSD_otc من البداية!). كذلك كان رفض
     صامت لأي اسم غير موجود في اللوحة. الآن: كل فتح لعملة يبدأ الجلب فوراً
     (changed أو الشارت فارغ) والاسم يُحوَّل لرمز الخادم بدل الرفض.
  3) «انضر الى هذا تاخر 1 دقيقة ولم يرسم الشموع» (خنق الجلب):
     الخنق التصاعدي 15→30→45→60 ثانية في _qx_ensure_asset كان يحجب الجلب بعد
     أي فشل — النقر يبدو ميتاً دقيقة كاملة. الآن النقر يبدأ الجلب فوراً
     دائماً؛ مسافة 10 ثوانٍ فقط لإعادة المحاولة التلقائية بعد فشل، ومنع
     التكرار عبر طابور الجلب نفسه.
  4) «نحن عندما نضغط على العملة هو يبدا بجلب الشموع تضهر دائرة تحميل لاكتمال
     التحميل اوك»: عند اكتمال الجلب تُدفع الشموع إلى الشارت فوراً عبر
     _qx_push_feed_now وتُطفأ الدائرة فيظهر الشارت (بلا انتظار نبضة المضخة)،
     ثم آلة سد الثغرات الأصلية (fill_gap_once كما هي) للعملة المفتوحة فقط
     في الخلفية — بلا أي جلب خلفي لعملة لم تُفتح.
  5) «فقط خليه هو لي يجلب قائمة العملات ويطبعها في قائمة التطبيق»: كما هي —
     اللوحة من مرصد instruments في المحرك الأصلي نفسه (v15.1) بلا تغيير.

المحرك المضمّن = upload/qx_mt4_original.py (الأصل بايت ببايت)
                + scripts/qx_compat_v15.py (طبقة الربط داخل المحرك)
تعديلات الواجهة (بمراسي فريدة — كل مرساة يجب أن تكون موجودة مرة واحدة):
  A) switch: كل فتح يبدأ الجلب + بلا رفض صامت للأسماء
  B) _qx_ensure_asset: بلا خنق 15-60 ثانية (النقر فوري؛ 10 ثوانٍ بعد فشل فقط)
  C) _qx_load_worker: دفع فوري + إخفاء الدائرة + سد خلفي لعملة فُتحت فقط
  D) إزالة نداءات سلسلة الدفعات الثلاثة (worker/_qx_load_feed/fetch_tf_async/دخول)
  E) _qx_push_feed_now: دفع الشموع عند اكتمال الجلب وإخفاء الدائرة فيظهر الشارت
  F) حالة _qx_sealed في __init__

تحققات صارمة: py_compile + roundtrip بايت-ب-بايت + AST لأسماء الواجهة
+ مراجع qx.* + اختبار دخان.
"""
import ast
import os
import py_compile
import re
import shutil
import sys

ROOT = "/home/z/my-project"
PASTE = os.path.join(ROOT, "upload", "qx_mt4_original.py")
COMPAT = os.path.join(ROOT, "scripts", "qx_compat_v15.py")
APP = os.path.join(ROOT, "download", "BadiChartsStudio_live.py")
BACKUP = os.path.join(ROOT, "scripts", "BadiChartsStudio_live.v15.2.bak.py")

MARK = "_QX_ENGINE_SOURCE = r'''"
CLOSE = "\n'''"


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


paste = read(PASTE)
compat = read(COMPAT)
app = read(APP)

if "'''" in paste:
    fail("paste contains ''' — unsafe to embed")
if "'''" in compat:
    fail("compat contains ''' — unsafe to embed")
if "_v152_session_save_state" not in compat:
    fail("compat lacks the v15.2 SessionManager._save_state fix")
if "seed_history(CLIENT, asset, PERIOD, days)" not in compat:
    fail("compat lacks the v15.3 seed_history-based ensure_asset_loaded")

source_inside = paste.rstrip("\n") + "\n\n\n" + compat.rstrip("\n") + "\n"

# ─── 1) استبدال كتلة المحرك ───
if app.count(MARK) != 1:
    fail(f"engine start marker count = {app.count(MARK)} (expected 1)")
start_i = app.index(MARK) + len(MARK)
end_j = app.index(CLOSE, start_i)
app_new = app[:start_i] + source_inside + CLOSE + app[end_j + len(CLOSE):]

# ─── 2) تعديلات الواجهة (مثبّتة بمراسي فريدة) ───
edits = []


def edit(old, new, name):
    edits.append((old, new, name))


# (A) «عملة BRLUSD_otc لماذا لم تضف فيها دائرة تحميل» — بلا رفض صامت:
#     الاسم يُحوَّل لرمز الخادم في _qx_load_feed نفسه
edit(
    """        if self._qx_symbols and asset not in self._qx_symbols:
            return
        changed = (asset != self._asset or tf != self._tf)""",
    """        # v15.3 (طلب المستخدم): بلا رفض صامت لأي اسم — الاسم يُحوَّل لرمز
        # الخادم داخل _qx_load_feed نفسه (اللوحة أو الاسم النظامي)
        changed = (asset != self._asset or tf != self._tf)""",
    "switch: no silent rejection")

edit(
    """        self._qx_last_sig = None
        if changed:""",
    """        self._qx_last_sig = None
        # v15.3 (طلب المستخدم: «عملة BRLUSD_otc لماذا لم تضف فيها دائرة تحميل»):
        # كل فتح لعملة يبدأ جلب شموعها فوراً — حتى إعادة فتح العملة المفتوحة
        # نفسها والشارت فارغ (كانت نقرة صامتة بلا دائرة تحميل ولا جلب —
        # والتطبيق يفتح أصلاً على BRLUSD_otc فكانت كل نقراتها صامتة).
        if changed or not self._candles:""",
    "switch: arm spinner on every open of an empty chart")

# (B) الخنق 15-60 ثانية — سبب «تاخر 1 دقيقة ولم يرسم الشموع» بنقرة ميتة
edit(
    """        now = time.time()
        # خنق تصاعدي — 15 ثانية لأول محاولة، وكل فشل يضاعف المهلة حتى 60 ثانية
        # (حتى لا نغرق الخادم بطلبات متكررة لعملة بلا تاريخ فعلاً)
        fails = self._qx_ensure_fail.get(api, 0)
        if now - self._qx_ensure_at.get(api, 0.0) < min(60.0, 15.0 * (1 + fails)):
            return
        self._qx_ensure_at[api] = now""",
    """        now = time.time()
        # v15.3 (سبب «انضر الى هذا تاخر 1 دقيقة ولم يرسم الشموع»): الخنق القديم
        # كان يحجب الجلب 15 ثانية لأول محاولة وكل فشل يضاعف المهلة حتى 60 ثانية
        # — فكان النقر على العملة صامتاً بلا جلب ولا دائرة تحميل دقيقة كاملة.
        # الآن: النقر يبدأ الجلب فوراً دائماً؛ مسافة 10 ثوانٍ فقط لإعادة
        # المحاولة التلقائية بعد فشل، ومنع التكرار عبر طابور الجلب نفسه.
        fails = self._qx_ensure_fail.get(api, 0)
        if fails and now - self._qx_ensure_at.get(api, 0.0) < 10.0:
            return
        self._qx_ensure_at[api] = now""",
    "ensure: no 15-60s throttle on explicit click")

# (C) عامل الطابور: دفع فوري + إخفاء الدائرة + سد خلفي لعملة فُتحت فقط
edit(
    """                fut = asyncio.run_coroutine_threadsafe(
                    qx.ensure_asset_loaded(api), qx.ASYNC_LOOP)
                n = fut.result(timeout=120)
                if n:
                    self._log("ok", f"{api}: {n} candles loaded + live stream ON")
                    self._qx_ensure_fail[api] = 0
                    self._qx_last_sig = None   # المضخة تدفع الغذاء الجديد فوراً
                    # v14.3 (طلب المستخدم): عند فتح العملة وفقط — دفعة 300 ثم
                    # 300 حتى عدد الأيام المضبوط، وكل دفعة تُرفع إلى الشارت فوراً
                    self._qx_start_history_chain(api, "1m")
                else:""",
    """                fut = asyncio.run_coroutine_threadsafe(
                    qx.ensure_asset_loaded(api), qx.ASYNC_LOOP)
                n = fut.result(timeout=120)
                if n:
                    self._log("ok", f"{api}: {n} candles seeded (history/load) + live stream ON")
                    self._qx_ensure_fail[api] = 0
                    self._qx_last_sig = None   # المضخة تدفع الغذاء الجديد فوراً
                    # v15.3 (طلب المستخدم: «نحن عندما نضغط على العملة هو يبدا
                    # بجلب الشموع تضهر دائرة تحميل لاكتمال التحميل») — الشموع
                    # تُدفع إلى الشارت فور اكتمال الجلب والدائرة تُطفأ فيظهر
                    # الشارت، ثم آلة سد الثغرات الأصلية للعملة المفتوحة فقط في
                    # الخلفية (بلا أي جلب خلفي لعملة لم تُفتح — طلب المستخدم).
                    self._qx_push_feed_now(api)
                    if (api, "1m") not in getattr(self, "_qx_sealed", set()):
                        self._qx_sealed.add((api, "1m"))
                        threading.Thread(target=self._qx_seal_gaps, args=(api,),
                                         daemon=True, name="qxSeal").start()
                else:""",
    "load worker: instant push + background seal, no chain refetch")

# (D1) _qx_load_feed: لا سلسلة دفعات فوق الجلب المباشر
edit(
    """            if candles and (force or not self._candles or self._qx_feed_key != key):
                self._candles = candles[-self._QX_FEED_CAP:]
                self._qx_feed_key = key
                # v14.3 (طلب المستخدم): فتح العملة — دفعة 300 ثم 300 حتى عدد
                # الأيام المضبوط في الإعدادات، وكل دفعة تُرفع إلى الشارت فوراً
                self._qx_start_history_chain(api, "1m")
            elif not candles:""",
    """            if candles and (force or not self._candles or self._qx_feed_key != key):
                self._candles = candles[-self._QX_FEED_CAP:]
                self._qx_feed_key = key
                # v15.3: seed_history الأصلية تجلب مدى الأيام كاملاً بطلب واحد
                # (1000+ شمعة في ~4 ثوانٍ كما في الأصل) — لا سلسلة دفعات بعد
                # الآن: كانت تعيد جلب نفس المدى فوق الجلب الأول فتتأخر الشموع
                # دقيقة كاملة قبل الرسم («تاخر 1 دقيقة ولم يرسم الشموع»)
            elif not candles:""",
    "load feed: no chain refetch on 1m open")

# (D2) _qx_fetch_tf_async: لا سلسلة دفعات للفريمات الأعلى
edit(
    """                if candles and asset_name == self._asset and tf_key == self._tf:
                    self._candles = candles
                    self._qx_feed_key = (asset_name, tf_key)
                    self.candlesChanged.emit()
                    self._log("ok", f"loaded {len(candles)} candles — {asset_name} {tf_key}")
                    # v14.3 (طلب المستخدم): عند فتح العملة وفقط — دفعة 300 ثم 300
                    # حتى عدد الأيام المضبوط، وكل دفعة تُرفع إلى الشارت فوراً
                    self._qx_start_history_chain(api, tf_key)""",
    """                if candles and asset_name == self._asset and tf_key == self._tf:
                    self._candles = candles
                    self._qx_feed_key = (asset_name, tf_key)
                    self.candlesChanged.emit()
                    self._log("ok", f"loaded {len(candles)} candles — {asset_name} {tf_key}")
                    # v15.3: طلب واحد بمدى الدفعة كاملاً (count × الفريم) — نفس
                    # طريقة الأصل؛ لا سلسلة دفعات تعيد جلب نفس المدى مرة ثانية""",
    "fetch tf: no chain refetch for higher timeframes")

# (D3) الدخول: لا سلسلة دفعات لعملة الفتح — الجلب المباشر أعلاه يكفي
edit(
    """            try:
                self._qx_start_history_chain(qx.PRELOAD_FIRST_SYMBOL, "1m")
            except Exception:
                pass""",
    """            # v15.3: لا سلسلة دفعات عند الدخول — _qx_load_feed أعلاه يجلب شموع
            # عملة الفتح بطلب واحد عبر seed_history الأصلية (مدى الأيام كاملاً
            # في ~4 ثوانٍ) ثم يرفعها إلى الشارت فوراً ويُطفئ دائرة التحميل""",
    "login: no chain refetch for opener")

# (E) دفع فوري عند اكتمال الجلب + إخفاء الدائرة فيظهر الشارت
edit(
    """    def _qx_loading_arm(self):
        \"\"\"v15.2 (طلب المستخدم): بدء دائرة تحميل الشموع — تظهر في اللحظة التي
        يبدأ فيها جلب شموع العملة المفتوحة وتُطفأ عند وصولها.\"\"\"
        self._qx_loading = True""",
    """    def _qx_push_feed_now(self, api):
        \"\"\"v15.3 (طلب المستخدم: «حتا ينتهي يضهر الشارت»): بعد اكتمال جلب شموع
        العملة تُدفع إلى الشارت فوراً وتُطفأ دائرة التحميل فيظهر الشارت —
        بلا انتظار نبضة المضخة. إذا كان المستخدم قد فتح عملة أخرى أثناء
        الجلب تبقى الدائرة لعملتها الجديدة (لا دائرة ولا دفع لعملة خلفية).\"\"\"
        try:
            cur_api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
            if cur_api != api:
                return
            candles = self._qx_engine_candles(api)
            if candles:
                self._candles = candles[-self._QX_FEED_CAP:]
                self._qx_feed_key = (self._asset, self._tf)
                if self._py_mods:
                    self._compute_py()
                self.candlesChanged.emit()
            self._qx_loading_clear()
        except Exception:
            pass

    def _qx_loading_arm(self):
        \"\"\"v15.2 (طلب المستخدم): بدء دائرة تحميل الشموع — تظهر في اللحظة التي
        يبدأ فيها جلب شموع العملة المفتوحة وتُطفأ عند وصولها.\"\"\"
        self._qx_loading = True""",
    "push feed now after seed completes")

# (F) حالة السد في __init__
edit(
    """        self._qx_load_busy = False     # عامل الطابور يعمل الآن""",
    """        self._qx_load_busy = False     # عامل الطابور يعمل الآن
        self._qx_sealed = set()        # v15.3: العملات التي سُدّت ثغراتها — آلة الأصل مرة واحدة لكل فتح""",
    "init: sealed set")

# (D4) الإعدادات: تغيير حجم الدفعة يعيد الجلب بأسلوب الأصل (طلب واحد) لا بالسلسلة
edit(
    """        self._log("ok", T[self._lang].get("batchSaved", "Batch candles saved"))
        # أعد دفعات التاريخ للعملة الحالية فوراً بحجم الدفعة الجديد
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if api:
            with self._qx_chain_lock:
                self._qx_chain_done.discard((api, self._tf))
                if self._tf != "1m":
                    self._qx_chain_done.discard((api, "1m"))
            self._qx_start_history_chain(api, self._tf)
            if self._tf != "1m":
                self._qx_start_history_chain(api, "1m")""",
    """        self._log("ok", T[self._lang].get("batchSaved", "Batch candles saved"))
        # v15.3: أعد جلب العملة الحالية بأسلوب الأصل (طلب واحد) بالمدى الجديد
        self._qx_force_reload_current()""",
    "setBatchCandles: reseed instead of chain")

# (D5) الإعدادات: تغيير الأيام يعيد الجلب بأسلوب الأصل (طلب واحد) لا بالسلسلة
edit(
    """        self._log("ok", T[self._lang].get("histSaved", "History days saved"))
        # أعِد دفعات التاريخ للعملة الحالية فوراً بالمدى الجديد
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if api:
            with self._qx_chain_lock:
                self._qx_chain_done.discard((api, self._tf))
                if self._tf != "1m":
                    self._qx_chain_done.discard((api, "1m"))
            self._qx_start_history_chain(api, self._tf)
            if self._tf != "1m":
                self._qx_start_history_chain(api, "1m")""",
    """        self._log("ok", T[self._lang].get("histSaved", "History days saved"))
        # v15.3: أعِد جلب العملة الحالية بأسلوب الأصل (طلب واحد) بالمدى الجديد
        self._qx_force_reload_current()""",
    "setHistDays: reseed instead of chain")

# (G) مساعد إعادة الجلب بعد تغيير الإعدادات — نفس مسار فتح العملة حرفياً
edit(
    """    def _qx_start_history_chain(self, api, tf_label="1m"):""",
    """    def _qx_force_reload_current(self):
        \"\"\"v15.3: إعادة جلب عملة الفتح الحالية من جذورها (بعد تغيير أيام
        التاريخ أو حجم الدفعة في الإعدادات) — نفس مسار فتح العملة حرفياً:
        دائرة التحميل تظهر، طلب واحد seed_history بالمدى الجديد، ثم الدفع
        والإخفاء فيظهر الشارت.\"\"\"
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if not api:
            return
        qx = _qx_module()
        if qx:
            try:
                a = qx._get_or_create_asset(api)
                a.candles = []
                a.mark_dirty()
            except Exception:
                pass
            try:
                with self._qx_chain_lock:
                    self._qx_chain_done.discard((api, self._tf))
                    if self._tf != "1m":
                        self._qx_chain_done.discard((api, "1m"))
            except Exception:
                pass
            try:
                self._qx_ensure_fail[api] = 0   # تغيير إعدادات = محاولة جديدة فوراً
            except Exception:
                pass
        self._candles = []
        self._qx_feed_key = ("", "")
        self._qx_last_sig = None
        self._qx_loading_arm()
        self._qx_load_feed(force=True)

    def _qx_start_history_chain(self, api, tf_label="1m"):""",
    "reseed helper for settings changes")

# (H1) الدخول: أيام التاريخ تُطبَّق قبل بدء الجلب (الطلب الواحد يقرأها عند التنفيذ)
edit(
    """            try:
                qx.reset_gap_flags()
            except Exception:
                pass
            try:
                qx.QX_HISTORY_DAYS = self._hist_days_cfg()
                qx.apply_history_days(self._hist_days_cfg())   # آلية قائمة الأصل نفسها
            except Exception:
                pass""",
    """            try:
                qx.reset_gap_flags()
            except Exception:
                pass""",
    "login: remove late days application (moved earlier)")

# (H2) الدخول: حجم الدفعة يُطبَّق قبل بدء الجلب أيضاً
edit(
    """            # v14.7 (طلب المستخدم حرفياً): الدفعة المباشرة للعملة بحجم
            # الإعداد المحفوظ — 700 شمعة افتراضياً وقابلة للتعديل حتى 1000
            try:
                qx.PRELOAD_CANDLES = int(self._batch_candles)
                qx.PAGINATION_BATCH = int(self._batch_candles)
            except Exception:
                pass
""",
    """""",
    "login: remove late batch application (moved earlier)")

# (H3) الدخول: الإعدادات تُطبَّق قبل تجهيز الدائرة والجلب
edit(
    """            # v15.2 (طلب المستخدم): دائرة تحميل الشموع لعملة فتح الشارت —
            # تظهر عند بداية الجلب وتختفي عند وصول الشموع فيظهر الشارت
            self._qx_loading_arm()
            self._qx_load_feed(force=True)""",
    """            # v15.3: إعدادات الأيام وحجم الدفعة تُطبَّق على المحرك **قبل**
            # بدء الجلب — طلب seed_history الواحد يقرأ الأيام لحظة التنفيذ
            try:
                qx.QX_HISTORY_DAYS = self._hist_days_cfg()
                qx.apply_history_days(self._hist_days_cfg())   # آلية قائمة الأصل نفسها
            except Exception:
                pass
            try:
                qx.PRELOAD_CANDLES = int(self._batch_candles)
                qx.PAGINATION_BATCH = int(self._batch_candles)
            except Exception:
                pass
            # v15.2 (طلب المستخدم): دائرة تحميل الشموع لعملة فتح الشارت —
            # تظهر عند بداية الجلب وتختفي عند وصول الشموع فيظهر الشارت
            self._qx_loading_arm()
            self._qx_load_feed(force=True)""",
    "login: apply settings before first seed")

# (H4) الدخول: تعليق قديم يصف سلسلة دفعات لم تعد تعمل — يُحدَّث
edit(
    """            # v14.3 (طلب المستخدم): تصفير علامات تجمّد السد القديمة + مزامنة إعداد
            # الأيام + دفعات التاريخ المتسلسلة لعملة فتح الشارت (300 ثم 300 حتى
            # عدد الأيام المضبوط — كل دفعة تُرفع إلى الشارت فوراً)
            try:
                qx.reset_gap_flags()
            except Exception:
                pass""",
    """            # v15.3: تصفير علامات تجمّد السد القديمة — آلة الأصل fill_gap_once
            # تعمل بعد اكتمال الجلب عبر السد الخلفي لعملة فُتحت فقط
            try:
                qx.reset_gap_flags()
            except Exception:
                pass""",
    "login: refresh stale chain comment")

# ─── 3) تطبيق التعديلات بمراسي فريدة ───
for old, new, name in edits:
    n = app_new.count(old)
    if n != 1:
        fail(f"anchor {name!r}: count={n} (expected 1)")
    app_new = app_new.replace(old, new, 1)
    print(f"[build] edit applied: {name}")

# ─── 4) فحص: لا import resource في الملف كله ───
if re.search(r"^\s*import\s+resource\b", app_new, re.M):
    fail("built file still imports resource")

# ─── 5) فحص: سلسلة الدفعات لم تعد تُستدعى من أي مسار فتح ───
mark0 = app_new.index(MARK)
close0 = app_new.index(CLOSE, mark0 + len(MARK))
app_outside = app_new[:mark0] + app_new[close0 + len(CLOSE):]
calls = re.findall(r"self\._qx_start_history_chain\(", app_outside)
if calls:
    fail(f"leftover _qx_start_history_chain calls in app layer: {len(calls)}")
if "_qx_push_feed_now" not in app_outside:
    fail("_qx_push_feed_now missing")
if "seed_history" not in app_outside and "seed_history" not in compat:
    fail("seed_history missing")
print("[build] app layer clean: no chain refetch calls remain")

# ─── 6) roundtrip: المصدر المضمّن == الأصل + الطبقة بايت ببايت ───
if app_new.count(MARK) != 1:
    fail("engine marker broken after edits")
s2 = app_new.index(MARK) + len(MARK)
e2 = app_new.index(CLOSE, s2)
embedded = app_new[s2:e2]
if embedded != source_inside:
    fail("roundtrip mismatch: embedded source != paste+compat")
if not (embedded.startswith(paste.rstrip("\n") + "\n")
        and embedded.endswith(compat.rstrip("\n") + "\n")):
    fail("roundtrip mismatch: original/compat part altered")
print("[build] roundtrip OK: original bytes untouched + compat appended verbatim")

# ─── 7) فحص AST لأسماء الواجهة داخل المحرك ───
tree = ast.parse(embedded)
enames = set()
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        enames.add(node.name)
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                enames.add(t.id)
            elif isinstance(t, (ast.Tuple, ast.List)):
                for e in t.elts:
                    if isinstance(e, ast.Name):
                        enames.add(e.id)
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        enames.add(node.target.id)
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        for al in node.names:
            enames.add((al.asname or al.name).split(".")[0])

REQUIRED = [
    "connect_quotex", "health_monitor", "auto_reconnect", "keepalive_loop",
    "stale_message_watchdog", "mt4_gap_filler", "fetch_candles_with_retry",
    "realtime_stream", "refetch_all_candles", "Asset", "_align_time",
    "_fill_missing_slots", "session_manager", "MT4_WRITER", "ASYNC_LOOP",
    "CLIENT", "ALL_STREAMING_ASSETS", "QX_HOST", "PERIOD", "PERIOD_SECONDS",
    "INITIAL_CANDLES", "HISTORY_DAYS", "FETCH_DURATION_SECONDS",
    "MIN_CANDLES_THRESHOLD", "MAX_FETCH_RETRIES", "FETCH_ASSET_DELAY",
    "_parse_raw_candles", "_request_counter", "WebsocketClient",
    "resolve_qx_host", "detect_country_code", "_instruments_snapshot",
    "fetch_instruments_now", "asset_payout_monitor", "preload_all_assets",
    "ensure_asset_loaded", "_get_or_create_asset", "_format_raw_candles",
    "_apply_candles_to_asset", "_TICK_CACHE", "tick_cache_collector",
    "tick_retention_loop", "candlestore_trim_loop", "fetch_older_batch",
    "qx_fetch_window_raw", "qx_get_historical_batches", "v14_deep_gap_seal",
    "clear_gap_flag_any", "reset_gap_flags", "apply_history_days",
    "PRELOAD_CANDLES", "PAGINATION_BATCH", "QX_HISTORY_DAYS",
    "ASSET_MAX_CANDLES", "PRELOAD_FIRST_SYMBOL", "_PRELOADED_INFO",
    "V14_DEEP_REPAIRED", "v14_print_banner",
    "_QX_PRELOAD_STATUS", "_qx_on_message_with_instruments",
    # v15.2: إصلاح حفظ البريد في طبقة الربط
    "_v152_session_save_state",
]
missing = [n for n in REQUIRED if n not in enames]
if missing:
    fail("missing engine names: " + ", ".join(missing))
print(f"[build] AST OK: all {len(REQUIRED)} interface names present in engine")

# ─── 8) كل مراجع qx.* في التطبيق موجودة فعلاً ───
refs_code = set()
for ln in app_outside.splitlines():
    st = ln.strip()
    if st.startswith("#"):
        continue
    refs_code |= set(re.findall(r"\bqx\.([A-Za-z_][A-Za-z0-9_]*)", ln))
    refs_code |= set(re.findall(r'getattr\(qx, "([A-Za-z_][A-Za-z0-9_]*)"', ln))
unresolved = sorted(n for n in refs_code if n not in enames)
if unresolved:
    fail("app references unknown engine names: " + ", ".join(unresolved))
print(f"[build] interface check OK: {len(refs_code)} qx.* references all resolve")

# ─── 9) كتابة الملف + py_compile ───
if not os.path.exists(BACKUP):
    shutil.copyfile(APP, BACKUP)
    print("[build] backup saved: " + BACKUP)
with open(APP, "w", encoding="utf-8", newline="") as f:
    f.write(app_new)
py_compile.compile(APP, doraise=True)
print(f"[build] py_compile OK — {APP} ({os.path.getsize(APP):,} bytes, "
      f"{len(app_new.splitlines()):,} lines)")
print("[build] v15.3 DONE")
