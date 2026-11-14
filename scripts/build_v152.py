#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v152.py — v15.2 (طلب المستخدم حرفياً):
  1) «لا نريده ان يحمل العملات في الخلفية نريده ان يقوم بتحميل بطريقة عندما
     نفتح العملة من قائمة العملات» — التحميل المسبق المتسلسل لكل العملات
     أُلغي تماماً (لا preload_all_assets بعد الدخول). الشموع تُجلب فقط عند
     فتح العملة (switch/_qx_load_feed/ensure_asset_loaded — الآلة القائمة
     نفسها بلا أي تغيير فيها).
  2) «تلك دائرة تحميل لي ضفتها في جنب لماذا ضفتها هناك وايضا لماذا ضفتها حتا
     انتهى من جلب الشموع يجب عند بداية جلب الشموع تضيفها حتا ينتهي يضهر
     الشارت» — شارة الزاوية أُزيلت. الدائرة الوسطى تصبح غطاء تحميل كامل:
     تظهر عند بداية جلب شموع العملة المفتوحة وتبقى حتى ينتهي الجلب فيظهر
     الشارت (مع مهلة أمان 60 ثانية). الربط عبر حدث chartload + خاصية
     chartLoading الصريحة (بدل الاشتقاق القديم «دخول وبلا شموع»).
  3) «ميزة حفض الايميل لماذا لا تعمل لكي يضهر مرة اخرى في واجهة تسجيل دخول» —
     السبب الجذري (مُثبت بالتشخيص): SessionManager._save_state في الأصل يمرر
     7 قيم لعبارة بها 6 علامات ؟ فتفشل الكتابة صامتة. الإصلاح في طبقة الربط
     (qx_compat_v15.py) بعدد روابط صحيح — الأصل لم يُمَس بايت واحد. مع
     «تذكّرني»: محدد → البريد محفوظ ويظهر معبأ في واجهة الدخول عند الإقلاع
     التالي؛ غير محدد → لا يُحفظ. خاصية savedEmail أصبحت notify-based
     وواجهة الدخول تعيد التعبئة في كل ظهور للصفحة.

المحرك المضمّن = upload/qx_mt4_original.py (الأصل بايت ببايت)
                + scripts/qx_compat_v15.py (طبقة الربط داخل المحرك)
تعديلات الواجهة (بمراسي فريدة — كل مرساة يجب أن تكون موجودة مرة واحدة):
  A) إنقاذ التحميل المسبق: لا نداء preload_all_assets بعد الدخول
  B) دائرة التحميل: تبديل مشتق chartLoading الصريح + arm/clear + حدث chartload
     + مراقب في المضخة (إخفاء عند وصول الشموع أو مهلة 60 ثانية)
  C) JS: إزالة شارة الزاوية (PRELOAD/PREBADGE/setPreload) + غطاء الدائرة
     الوسطى + اسم العملة في نص الدائرة
  D) تذكّرني: savedEmail notify-based + بيانات الدخول حسب «تذكّرني» + تعبئة
     البريد في كل ظهور لواجهة الدخول

تحققات صارمة: py_compile + roundtrip بايت-ب-بايت + AST لأسماء الواجهة
+ مراجع qx.* + اختبار دخان يشمل حفظ البريد عبر إقلاعين متتاليين.
"""
import ast
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = "/home/z/my-project"
PASTE = os.path.join(ROOT, "upload", "qx_mt4_original.py")
COMPAT = os.path.join(ROOT, "scripts", "qx_compat_v15.py")
APP = os.path.join(ROOT, "download", "BadiChartsStudio_live.py")
BACKUP = os.path.join(ROOT, "scripts", "BadiChartsStudio_live.v15.1.bak.py")

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


# (A) «لا نريده ان يحمل العملات في الخلفية» — لا تحميل مسبق بعد الدخول
edit(
    '''            # BRLUSD_otc فوراً (300 شمعة + الحالة + الدفع) ثم بقية العملات واحدة تلو الأخرى
            asyncio.run_coroutine_threadsafe(qx.preload_all_assets(), loop)''',
    '''            # v15.2 (طلب المستخدم): «لا نريده ان يحمل العملات في الخلفية
            # نريده ان يقوم بتحميل بطريقة عندما نفتح العملة من قائمة العملات» —
            # التحميل المسبق المتسلسل لكل العملات أُلغي تماماً. الشموع تُجلب
            # فقط عند فتح العملة: switch → _qx_load_feed → ensure_asset_loaded
            # وfetch_tf_async وسلسلة تاريخ العملة المفتوحة — نفس آلة الجلب
            # الفوري القائمة دون أي تحميل خلفي لأي عملة لم تُفتح.''',
    "login: no background preload")

# (B1) حالة دائرة التحميل في __init__
edit(
    '''        self._qx_resync_pending = False  # v14.3: مزامنة كاملة بعد إصلاح سد الثغرات
        self._qx_pre_log = 0.0         # خنق سجلات حالة التحميل المسبق''',
    '''        self._qx_resync_pending = False  # v14.3: مزامنة كاملة بعد إصلاح سد الثغرات
        self._qx_pre_log = 0.0         # خنق سجلات حالة التحميل المسبق
        # v15.2 (طلب المستخدم): دائرة تحميل الشموع — حالة صريحة تبدأ عند بداية
        # جلب شموع العملة المفتوحة وتنتهي عند وصولها (أو مهلة أمان 60 ثانية)
        self._qx_loading = False       # جلب شموع العملة الحالية جارٍ الآن
        self._qx_loading_at = 0.0      # لحظة بدء الجلب''',
    "init: loading state")

# (B2) إشارة تغيّر البريد المحفوظ
edit(
    '''    qxEvent = Signal(str)                  # LIVE SERVER EDITION: أحداث خادم QX (الدخول/لوحة العملات/دفعات التمرير)''',
    '''    qxEvent = Signal(str)                  # LIVE SERVER EDITION: أحداث خادم QX (الدخول/لوحة العملات/دفعات التمرير)
    savedEmailChanged = Signal()           # v15.2: تغيّر البريد المحفوظ («تذكّرني»)''',
    "signals: savedEmailChanged")

# (B3) chartLoading المشتق → الحالة الصريحة (بمهلة الأمان عبر _qx_loading)
edit(
    '''    @Property(bool, notify=candlesChanged)
    def chartLoading(self):
        """v13.2 (طلب المستخدم): دائرة تحميل في الشارت — True عندما يكون الدخول
        تم والعملة الحالية بلا شموع بعد (تُجلب الآن) — بدل شارت أسود فارغ."""
        return bool(self._qx_logged and not self._candles)''',
    '''    @Property(bool, notify=candlesChanged)
    def chartLoading(self):
        """v13.2/v15.2 (طلب المستخدم): دائرة تحميل في الشارت — True فقط أثناء
        جلب شموع العملة المفتوحة فعلاً (حالة صريحة تبدأ عند بداية الجلب
        وتنتهي عند وصول الشموع أو مهلة 60 ثانية) — بدل شارت أسود فارغ."""
        return bool(self._qx_logged and getattr(self, "_qx_loading", False)
                    and not self._candles)''',
    "chartLoading: explicit state")

# (B4) savedEmail: notify-based بدل constant
edit(
    '''    # ---------- الدخول الحقيقي عبر خادم Quotex (بديل تسجيل الدخول الوهمي) ----------
    @Property(str, constant=True)
    def savedEmail(self):
        """البريد المحفوظ لدى الخادم (للتذكير عند الدخول التالي)."""
        qx = _qx_module()
        try:
            return str(qx.session_manager.get_saved_email() or "")
        except Exception:
            return ""''',
    '''    # ---------- الدخول الحقيقي عبر خادم Quotex (بديل تسجيل الدخول الوهمي) ----------
    @Property(str, notify=savedEmailChanged)
    def savedEmail(self):
        """البريد المحفوظ («تذكّرني») — يظهر معبأ في واجهة تسجيل الدخول عند
        الإقلاع التالي. v15.2: الكتابة في app_data.db كانت تفشل صامتة في الأصل
        (عدد روابط خاطئ في _save_state — أُصلح في طبقة الربط داخل المحرك)."""
        qx = _qx_module()
        try:
            return str(qx.session_manager.get_saved_email() or "")
        except Exception:
            return ""''',
    "savedEmail: notify-based")

# (B5) الدخول: «تذكّرني» يحفظ/لا يحفظ + تفعيل دائرة التحميل لعملة فتح الشارت
edit(
    '''            self._qx_logged = True
            self._qx_load_feed(force=True)''',
    '''            self._qx_logged = True
            # v15.2 (طلب المستخدم): «ميزة حفض الايميل» — مع «تذكّرني» يبقى
            # البريد محفوظاً فيظهر معبأ في واجهة تسجيل الدخول عند الإقلاع
            # التالي؛ بلا تحديد لا يُحفظ شيء.
            try:
                _sm = qx.session_manager
                if not bool(remember):
                    _sm.state["email"] = ""
                    _sm.state["password"] = ""
                    _sm._save_state()
                self.savedEmailChanged.emit()
            except Exception:
                pass
            # v15.2 (طلب المستخدم): دائرة تحميل الشموع لعملة فتح الشارت —
            # تظهر عند بداية الجلب وتختفي عند وصول الشموع فيظهر الشارت
            self._qx_loading_arm()
            self._qx_load_feed(force=True)
            if self._qx_feed_key == (self._asset, self._tf) and self._candles:
                self._qx_loading_clear()''',
    "login: remember + loading arm")

# (C1) switch: دائرة التحميل عند فتح العملة من قائمة العملات
edit(
    '''            self._candles = []
            self._qx_feed_key = ("", "")
            self._qx_load_feed(force=True)''',
    '''            self._candles = []
            self._qx_feed_key = ("", "")
            # v15.2 (طلب المستخدم): «عندما نفتح العملة من قائمة العملات» —
            # دائرة تحميل تظهر عند بداية جلب الشموع وتبقى حتى ينتهي الجلب
            # فيظهر الشارت. لا تحميل خلفي — الجلب عند الفتح فقط.
            self._qx_loading_arm()
            self._qx_load_feed(force=True)
            # الجلب اكتمل فوراً (شموع العملة في ذاكرة المحرك أو تيكات جاهزة) —
            # الدائرة تُطفأ في نفس اللحظة
            if self._qx_feed_key == (self._asset, self._tf) and self._candles:
                self._qx_loading_clear()''',
    "switch: loading arm")

# (C2) أدوات الدائرة: arm/clear قبل _qx_live_step
edit(
    '''    def _qx_live_step(self):
        """خطوة التغذية الحية: تحديث شموع العملة الحالية من الخادم ثم الدفع للشارت."""''',
    '''    def _qx_loading_arm(self):
        """v15.2 (طلب المستخدم): بدء دائرة تحميل الشموع — تظهر في اللحظة التي
        يبدأ فيها جلب شموع العملة المفتوحة وتُطفأ عند وصولها."""
        self._qx_loading = True
        self._qx_loading_at = time.time()
        self._emit_qx({"type": "chartload", "active": True, "asset": self._asset})

    def _qx_loading_clear(self):
        """v15.2: انتهاء جلب شموع العملة الحالية — إخفاء الدائرة فيظهر الشارت."""
        if not getattr(self, "_qx_loading", False):
            return
        self._qx_loading = False
        self._emit_qx({"type": "chartload", "active": False, "asset": self._asset})

    def _qx_live_step(self):
        """خطوة التغذية الحية: تحديث شموع العملة الحالية من الخادم ثم الدفع للشارت."""''',
    "loading arm/clear helpers")

# (C3) بوابة المضخة: نبضات سريعة أثناء التحميل فقط (بلا نبضات التحميل المسبق)
edit(
    '''        _board_due = (_now - getattr(self, "_qx_board_at", 0.0)) >= 2.0
        # v15.1 (طلب المستخدم): دائرة تحميل الشموع — أثناء التحميل المسبق
        # المتسلسل المضخة تعمل (نبضة كل ثانية) حتى بلا تيك جديد، وبعدها 3 ثوانٍ
        # لتضمن إخفاء الدائرة.
        try:
            _ps0 = getattr(qx, "_QX_PRELOAD_STATUS", {}) or {}
            _pre_want = bool(_ps0.get("active")) or (
                _now - float(_ps0.get("finished_at") or 0.0) <= 3.0)
        except Exception:
            _pre_want = False
        if (not _tick_new and not _board_due and not _pre_want
                and not getattr(self, "_qx_resync_pending", False)):
            return
        if _board_due:
            self._qx_board_at = _now''',
    '''        _board_due = (_now - getattr(self, "_qx_board_at", 0.0)) >= 2.0
        # v15.2: أثناء جلب شموع العملة المفتوحة (دائرة التحميل) المضخة تعمل
        # دائماً حتى تختفي الدائرة فور وصول الشموع — بلا أي نبضات إضافية
        # في غير ذلك (التحميل المسبق الخلفي أُلغي — طلب المستخدم).
        _load_due = bool(getattr(self, "_qx_loading", False))
        if (not _tick_new and not _board_due and not _load_due
                and not getattr(self, "_qx_resync_pending", False)):
            return
        if _board_due:
            self._qx_board_at = _now''',
    "poll gate: loading pulse")

# (C4) قسم 4 في المضخة: مراقب الدائرة (إخفاء عند وصول الشموع / مهلة 60 ثانية)
edit(
    '''        # 4) v15.1 (طلب المستخدم): حالة دائرة تحميل الشموع — التحميل المسبق
        #    المتسلسل (92 عملة واحدة تلو الأخرى). تُدفع للواجهة عند أي تغيير
        #    + نبضة كل ثانية أثناء العمل، ونبضة أخيرة بعد الانتهاء حتى تختفي
        #    الدائرة فوراً.
        try:
            _pst = dict(getattr(qx, "_QX_PRELOAD_STATUS", {}) or {})
            _sig = (bool(_pst.get("active")), int(_pst.get("idx") or 0),
                    int(_pst.get("total") or 0), int(_pst.get("loaded") or 0))
            _emit_it = _sig != getattr(self, "_qx_pre_sig", None)
            if not _emit_it and _sig[0]:
                _emit_it = (_now - getattr(self, "_qx_pre_ev_at", 0.0)) >= 1.0
            if not _emit_it and not _sig[0]:
                _fin = float(_pst.get("finished_at") or 0.0)
                if (_fin and _now - _fin <= 3.0
                        and _now - getattr(self, "_qx_pre_ev_at", 0.0) >= 1.0):
                    _emit_it = True
            if _emit_it:
                self._qx_pre_ev_at = _now
                self._qx_pre_sig = _sig
                self._emit_qx({"type": "preload", "active": _sig[0],
                               "idx": _sig[1], "total": _sig[2], "loaded": _sig[3]})
        except Exception:
            pass''',
    '''        # 4) v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة — تُطفأ
        #    فور وصول شموع العملة الحالية (الشارت يظهر بعد انتهاء الجلب)، مع
        #    مهلة أمان 60 ثانية حتى لا تبقى الدائرة عالقة أبداً.
        try:
            if getattr(self, "_qx_loading", False):
                _ready = (self._qx_feed_key == (self._asset, self._tf)
                          and bool(self._candles))
                if _ready or (_now - getattr(self, "_qx_loading_at", 0.0)) > 60.0:
                    if not _ready:
                        self._log("info", "candles loading timeout — spinner hidden")
                    self._qx_loading_clear()
        except Exception:
            pass''',
    "poll: loading watcher")

# (D1) QML: مسار حدث chartload بدل preload
edit(
    '''            if (e.type === "preload") {
                /* v15.1 (طلب المستخدم): دائرة تحميل عند تحميل الشموع — تبقى
                   ظاهرة حتى ينتهي الخادم من جلب شموع كل العملات واحدة تلو
                   الأخرى، ثم تختفي */
                win.webCall("__badiApp.setPreload(" + JSON.stringify(
                    { active: !!e.active, idx: e.idx || 0,
                      total: e.total || 0, loaded: e.loaded || 0 }) + ")")
                return
            }''',
    '''            if (e.type === "chartload") {
                /* v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة من
                   قائمة العملات — تظهر عند بداية جلب الشموع وتبقى حتى ينتهي
                   الجلب فيظهر الشارت. بلا شارة في الزاوية وبلا تحميل خلفي. */
                win.webCall("__badiApp.setChartLoading(" + (e.active ? "true" : "false")
                            + "," + JSON.stringify(String(e.asset || "")) + ")")
                return
            }''',
    "qml: chartload route")

# (D2) JS: إزالة شارة الزاوية + الدائرة الوسطى غطاء تحميل كامل
edit(
    '''/* ═══ v15.1 (طلب المستخدم): دائرة تحميل حتى ينتهي الخادم من جلب الشموع ═══
   أثناء التحميل المسبق المتسلسل (92 عملة واحدة تلو الأخرى) تظهر دائرة صغيرة
   في زاوية الشارت مع التقدّم (12/92) وتختفي عند الانتهاء. وعندما يكون الشارت
   نفسه بلا شموع بعد تظهر دائرة الوسط أيضاً أثناء التحميل المسبق. */
var PRELOAD = { active: false, idx: 0, total: 0, loaded: 0 };
var PREBADGE = null;
function preloadBadge(pr) {
  try {
    if (!PREBADGE) {
      var st = document.createElement("style");
      st.textContent = ".badi-pre{position:absolute;top:8px;right:10px;display:flex;align-items:center;gap:8px;z-index:7;pointer-events:none;background:rgba(10,14,22,.55);border:1px solid rgba(128,140,170,.25);border-radius:999px;padding:5px 12px 5px 8px}"
        + ".badi-pre .bp-ring{width:18px;height:18px;border-radius:50%;border:2.5px solid rgba(128,140,170,.3);border-top-color:#3B8BFF;animation:badispin .9s linear infinite;flex:0 0 auto}"
        + ".badi-pre .bp-txt{font:600 11px/1 system-ui,-apple-system,Segoe UI,sans-serif;letter-spacing:.3px;opacity:.85;white-space:nowrap}"
        + "@keyframes badispin{to{transform:rotate(360deg)}}";
      document.head.appendChild(st);
      PREBADGE = document.createElement("div");
      PREBADGE.className = "badi-pre";
      PREBADGE.hidden = true;
    }
    var ar = window.__BADI_LANG__ === "ar";
    var txt = PRELOAD.total > 0
      ? (ar ? ("جارٍ جلب الشموع " + Math.max(1, PRELOAD.idx) + "/" + PRELOAD.total + "…")
            : ("Loading candles " + Math.max(1, PRELOAD.idx) + "/" + PRELOAD.total + "…"))
      : (ar ? "جارٍ جلب الشموع…" : "Loading candles…");
    PREBADGE.innerHTML = '<div class="bp-ring"></div><div class="bp-txt">' + esc(txt) + '</div>';
    var host = pr && pr.el ? pr.el.querySelector(".pane-cv") : null;
    if (host && PREBADGE.parentNode !== host) host.appendChild(PREBADGE);
    return PREBADGE;
  } catch (e) { return null; }
}
function renderChartLoading() {
  try {
    var pr = window.__badiPrimary ? window.__badiPrimary() : null;
    var empty = !pr || !pr.dataArr || pr.dataArr.length === 0;
    var el = chartLoadEl(pr);
    if (el) el.hidden = !((CHLOAD.on || PRELOAD.active) && empty);
    var bg = preloadBadge(pr);
    if (bg) bg.hidden = !PRELOAD.active;
  } catch (e) {}
}''',
    '''/* ═══ v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة ═══
   شارة الزاوية أُزيلت («تلك دائرة تحميل لي ضفتها في جنب لماذا ضفتها هناك»).
   الدائرة الوسطى فقط: تظهر عند بداية جلب شموع العملة المفتوحة من قائمة
   العملات وتبقى حتى ينتهي الجلب فيظهر الشارت — غطاء تحميل كامل فوق الشارت. */
function renderChartLoading() {
  try {
    var pr = window.__badiPrimary ? window.__badiPrimary() : null;
    var el = chartLoadEl(pr);
    if (el) el.hidden = !CHLOAD.on;
  } catch (e) {}
}''',
    "js: remove corner badge, full cover circle")

# (D3) JS: setChartLoading يحمل اسم العملة + حذف setPreload
edit(
    '''    setChartLoading: function (on) {
      /* v13.2 (طلب المستخدم): دائرة تحميل داخل الشارت — تظهر عندما تكون شموع
         العملة الحالية تُجلب من الخادم وتختفي فور وصولها — لا شارت أسود فارغ */
      try {
        CHLOAD.on = !!on;
        renderChartLoading();
      } catch (e) {}
    },
    setPreload: function (st) {
      /* v15.1 (طلب المستخدم): دائرة تحميل عند تحميل الشموع — تبقى حتى ينتهي
         الخادم من جلب شموع كل العملات واحدة تلو الأخرى ثم تختفي */
      try {
        st = st || {};
        PRELOAD.active = !!st.active;
        PRELOAD.idx = Number(st.idx || 0);
        PRELOAD.total = Number(st.total || 0);
        PRELOAD.loaded = Number(st.loaded || 0);
        renderChartLoading();
      } catch (e) {}
    },''',
    '''    setChartLoading: function (on, assetName) {
      /* v15.2 (طلب المستخدم): دائرة تحميل الشموع — تظهر عند بداية جلب شموع
         العملة المفتوحة من قائمة العملات وتبقى حتى ينتهي الجلب فيظهر الشارت */
      try {
        CHLOAD.on = !!on;
        CHLOAD.asset = String(assetName || "");
        renderChartLoading();
      } catch (e) {}
    },''',
    "js: setChartLoading(on, asset)")

# (D4) JS: نص الدائرة الوسطى — اسم العملة المجلوبة
edit(
    '''    var _sub = (PRELOAD.active && PRELOAD.total > 0)
      ? ((ar ? "العملة " : "asset ") + Math.max(1, PRELOAD.idx) + "/" + PRELOAD.total)
      : "700 candles";
    CHLOAD.el.innerHTML = '<div class="bl-ring"></div><div class="bl-txt">'
      + (ar ? "جارٍ جلب الشموع من الخادم…" : "Loading candles from server…")
      + '</div><div class="bl-sub">' + _sub + '</div>';''',
    '''    var _sub = CHLOAD.asset ? CHLOAD.asset : "";
    CHLOAD.el.innerHTML = '<div class="bl-ring"></div><div class="bl-txt">'
      + (ar ? "جارٍ جلب الشموع من الخادم…" : "Loading candles from server…")
      + '</div>' + (_sub ? '<div class="bl-sub">' + esc(_sub) + '</div>' : '');''',
    "js: circle sub text = asset name")

# (D5) JS: حالة CHLOAD تحمل اسم العملة
edit(
    '''var CHLOAD = { on: false, el: null };''',
    '''var CHLOAD = { on: false, asset: "", el: null };''',
    "js: CHLOAD asset field")

# (D6) JS: غطاء الدائرة يغطي الشارت أثناء الجلب (الشارت يظهر بعد الانتهاء)
edit(
    '''      st.textContent = ".badi-load{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;z-index:6;pointer-events:none}"''',
    '''      st.textContent = ".badi-load{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;z-index:6;pointer-events:none;background:rgba(7,10,16,.72)}"''',
    "js: circle cover background")

# (E1) QML: تعبئة البريد المحفوظ في كل ظهور لواجهة الدخول
edit(
    '''            onVisibleChanged: if (visible) { t = 0; enterAnim.restart() }''',
    '''            /* v15.2 (طلب المستخدم): البريد المحفوظ («تذكّرني») يظهر معبأ في
               واجهة تسجيل الدخول في كل مرة تظهر فيها الصفحة */
            onVisibleChanged: {
                if (visible) {
                    t = 0
                    enterAnim.restart()
                    try { userF.text = backend.savedEmail } catch (e) {}
                }
            }''',
    "qml: refill saved email on visible")

# ─── 3) تطبيق التعديلات بمراسي فريدة ───
applied = 0
for old, new, name in edits:
    n = app_new.count(old)
    if n != 1:
        fail(f"anchor '{name}' count = {n} (expected 1)")
    app_new = app_new.replace(old, new, 1)
    applied += 1

print(f"[build] engine replaced + {applied}/{len(edits)} app edits applied")

# ─── 4) فحص: لا import resource في الملف كله ───
if re.search(r"^\s*import\s+resource\b", app_new, re.M):
    fail("built file still imports resource")

# ─── 5) فحص: بقايا التحميل المسبق في الواجهة يجب أن تكون معدومة ───
mark0 = app_new.index(MARK)
close0 = app_new.index(CLOSE, mark0 + len(MARK))
app_outside = app_new[:mark0] + app_new[close0 + len(CLOSE):]
for bad in ["preloadBadge", "PREBADGE", "setPreload", '"type": "preload"',
            '"type": "preload"', "preload_all_assets()"]:
    if bad in app_outside:
        fail(f"leftover preload UI reference in app layer: {bad!r}")
if re.search(r"PRELOAD\.(active|idx|total|loaded)", app_outside):
    fail("leftover JS PRELOAD state reference")
print("[build] app layer clean: no background-preload UI references")

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

# ─── 10) اختبار دخان: تنفيذ المحرك + حفظ البريد عبر إقلاعين + المرصد ───
tmp = tempfile.mkdtemp(prefix="qx_engine_smoke_")
eng_path = os.path.join(tmp, "qx_engine_test.py")
with open(eng_path, "w", encoding="utf-8") as f:
    f.write(embedded)
smoke = r'''
import os, sys, time, json, types, sqlite3
os.chdir(r"{tmp}")
src = open(r"{eng}", encoding="utf-8").read()
mod = {{"__name__": "qx_embedded_engine", "__file__": r"{eng}"}}
exec(compile(src, "qx_embedded_engine", "exec"), mod)
assert mod["ASYNC_LOOP"] is not None and mod["ASYNC_LOOP"].is_running(), "engine loop dead"
assert hasattr(mod["Asset"], "write"), "Asset missing"
d = mod["apply_history_days"](0.80)
assert abs(d - 0.80) < 1e-9, "history days mismatch"
assert mod["FETCH_DURATION_SECONDS"] == int(86400 * 0.80 * 1.15), "FETCH_DURATION mismatch"

# (أ) v15.2: حفظ البريد يكتب في app_data.db فعلاً ويُقرأ في إقلاع ثانٍ
dbp = mod["DB_PATH"]
mod["session_manager"].record_success("tester@example.com", password="pw123", host="quotex.com")
conn = sqlite3.connect(str(dbp))
row = conn.execute("SELECT email, password FROM app_state WHERE id=1").fetchone()
conn.close()
assert row == ("tester@example.com", "pw123"), f"app_state row wrong: {{row!r}}"
mod2 = {{"__name__": "qx_embedded_engine", "__file__": r"{eng}"}}
exec(compile(src, "qx_embedded_engine", "exec"), mod2)
assert mod2["session_manager"].get_saved_email() == "tester@example.com", "email lost on reboot"
# «تذكّرني» بلا تحديد: لا يبقى بريد
mod2["session_manager"].state["email"] = ""
mod2["session_manager"].state["password"] = ""
mod2["session_manager"]._save_state()
conn = sqlite3.connect(str(dbp))
row2 = conn.execute("SELECT email FROM app_state WHERE id=1").fetchone()
conn.close()
assert row2 == ("",), f"forget failed: {{row2!r}}"

INST = [["a1", "EURUSD_otc", "EUR/USD (OTC)", 0, 0, 92, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 85],
        ["a2", "XAUUSD_otc", "Gold (OTC)", 0, 0, 86, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 80]]

class _Reg:
    async def set_event(self, name, val):
        self.last = (name, val)

class _ApiStub:
    def __init__(self):
        self.instruments = None
        self._temp_status = ""
        self._async_loop = None
        self.last_message_at = 0.0
        self.event_registry = _Reg()
        self.candle_v2_data = {{}}
        self.realtime_candles = {{}}

class _ClientStub:
    def __init__(self):
        self.api = _ApiStub()
        self.state = types.SimpleNamespace(ssl_Mutual_exclusion=False)
        self.wss = types.SimpleNamespace(send=lambda *a, **k: None)

on_msg = mod["WebsocketClient"].on_message
assert on_msg is mod["_qx_on_message_with_instruments"], "on_message observer not installed"

# (ب) البروتوكول الرسمي: مرحلة 1 placeholder ثم مرحلة 2 إطار البيانات
c = _ClientStub()
on_msg(c, None, '451-["instruments/list",{{"asset_id":1,"_placeholder":true,"num":0}}]'.encode())
assert c.api.instruments is None, "phase1 must not store"
assert "instruments/list" in c.api._temp_status, "phase1 must remember"
on_msg(c, None, json.dumps([INST]).encode())
assert isinstance(c.api.instruments, list) and len(c.api.instruments) == 2, "phase2 must store"
mod["CLIENT"] = c
snap = mod["_instruments_snapshot"]()
assert [e["asset"] for e in snap] == ["EURUSD_otc", "XAUUSD_otc"], "snapshot assets wrong"

print("SMOKE_OK loop=alive email_saved_and_reloaded=ok forget=ok two_phase_instruments=ok")
'''.replace("{tmp}", tmp).replace("{eng}", eng_path).replace("{{", "{").replace("}}", "}")
r = subprocess.run([sys.executable, "-c", smoke], capture_output=True, text=True, timeout=240)
ok = r.returncode == 0 and "SMOKE_OK" in r.stdout
print("[smoke] stdout:", r.stdout.strip()[-600:] if r.stdout else "(empty)")
if r.stderr.strip():
    print("[smoke] stderr tail:", r.stderr.strip()[-900:])
if not ok:
    fail("engine smoke test failed")
print("[smoke] OK — engine executes standalone; saved-email persists across two boots")
shutil.rmtree(tmp, ignore_errors=True)
print("\nALL BUILD CHECKS PASSED")
