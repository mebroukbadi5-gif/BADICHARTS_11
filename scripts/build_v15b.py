#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v15b.py — v15.1 إصلاح قائمة العملات + دائرة تحميل الشموع

يُعيد بناء المحرك المضمّن في BadiChartsStudio_live.py من:
  upload/qx_mt4_original.py (الأصل بايت ببايت) + scripts/qx_compat_v15.py (v15.1)
حيث تحديثات v15.1 في طبقة الربط فقط (الأصل لم يُمَس بايت واحد):
  1) مرصد instruments على مرحلتين (placeholder ثم إطار البيانات) — نفس كتلة
     v14 المُجرّبة حرفياً. سبب «قائمة العملات لم تُجلب» في v15.0: المرصد كان
     يعالج الصيغة المضمّنة فقط بينما الخادم يرد بالمرحلتين.
  2) حالة التحميل المسبق المتسلسل _QX_PRELOAD_STATUS (92 عملة واحدة تلو الأخرى).

تعديلات الواجهة (بمراسي فريدة):
  A) المضخة تدفع حالة التحميل المسبق للواجهة (دائرة تحميل الشموع حتى الانتهاء)
  B) QML يمرر حدث preload للصفحة
  C) JS: setPreload + شارة دائرة تحميل في زاوية الشارت + الدائرة الوسطى
     تبقى أثناء التحميل المسبق حتى ينتهي جلب الشموع

تحققات صارمة: py_compile + roundtrip بايت-ب-بايت + AST لأسماء الواجهة
+ مراجع qx.* + اختبار دخان يشمل اختبار المرصد على المرحلتين.
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
BACKUP = os.path.join(ROOT, "scripts", "BadiChartsStudio_live.v15.0.bak.py")

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

# (A1) بوابة المضخة: نبضة الدائرة أثناء التحميل المسبق حتى بلا تيك جديد
edit(
    '''        _board_due = (_now - getattr(self, "_qx_board_at", 0.0)) >= 2.0
        if not _tick_new and not _board_due and not getattr(self, "_qx_resync_pending", False):
            return
        if _board_due:
            self._qx_board_at = _now''',
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
    "poll gate preload pulse")

# (A2) المضخة: قسم جديد — دفع حالة الدائرة للواجهة عند التغيير + نبضة كل ثانية
edit(
    '''                    self._log("info", msg)
        except Exception:
            pass

    def _qx_live_step(self):''',
    '''                    self._log("info", msg)
        except Exception:
            pass
        # 4) v15.1 (طلب المستخدم): حالة دائرة تحميل الشموع — التحميل المسبق
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
            pass

    def _qx_live_step(self):''',
    "poll preload event")

# (B) QML: تمرير حدث preload للصفحة
edit(
    '''            if (e.type === "board") {
                win.webCall("__badiApp.setBoard(" + JSON.stringify(e.board) + ")")
                return
            }''',
    '''            if (e.type === "board") {
                win.webCall("__badiApp.setBoard(" + JSON.stringify(e.board) + ")")
                return
            }
            if (e.type === "preload") {
                /* v15.1 (طلب المستخدم): دائرة تحميل عند تحميل الشموع — تبقى
                   ظاهرة حتى ينتهي الخادم من جلب شموع كل العملات واحدة تلو
                   الأخرى، ثم تختفي */
                win.webCall("__badiApp.setPreload(" + JSON.stringify(
                    { active: !!e.active, idx: e.idx || 0,
                      total: e.total || 0, loaded: e.loaded || 0 }) + ")")
                return
            }''',
    "qml preload route")

# (C1) JS: حالة التحميل المسبق + شارة الدائرة في زاوية الشارت + الدائرة الوسطى
edit(
    '''function renderChartLoading() {
  try {
    var pr = window.__badiPrimary ? window.__badiPrimary() : null;
    var empty = !pr || !pr.dataArr || pr.dataArr.length === 0;
    var el = chartLoadEl(pr);
    if (el) el.hidden = !(CHLOAD.on && empty);
  } catch (e) {}
}''',
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
    "js preload badge + renderChartLoading")

# (C2) JS: setPreload — نقطة الاستقبال من سطح المكتب
edit(
    '''    setChartLoading: function (on) {
      /* v13.2 (طلب المستخدم): دائرة تحميل داخل الشارت — تظهر عندما تكون شموع
         العملة الحالية تُجلب من الخادم وتختفي فور وصولها — لا شارت أسود فارغ */
      try {
        CHLOAD.on = !!on;
        renderChartLoading();
      } catch (e) {}
    },''',
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
    "js setPreload")

# (C3) JS: النص الفرعي للدائرة الوسطى يعكس التقدم الحقيقي والدفعة 700
edit(
    '''    CHLOAD.el.innerHTML = '<div class="bl-ring"></div><div class="bl-txt">'
      + (ar ? "جارٍ جلب الشموع من الخادم…" : "Loading candles from server…")
      + '</div><div class="bl-sub">300 candles</div>';''',
    '''    var _sub = (PRELOAD.active && PRELOAD.total > 0)
      ? ((ar ? "العملة " : "asset ") + Math.max(1, PRELOAD.idx) + "/" + PRELOAD.total)
      : "700 candles";
    CHLOAD.el.innerHTML = '<div class="bl-ring"></div><div class="bl-txt">'
      + (ar ? "جارٍ جلب الشموع من الخادم…" : "Loading candles from server…")
      + '</div><div class="bl-sub">' + _sub + '</div>';''',
    "js loading sub text")

applied = 0
for old, new, name in edits:
    n = app_new.count(old)
    if n != 1:
        fail(f"anchor '{name}' count = {n} (expected 1)")
    app_new = app_new.replace(old, new, 1)
    applied += 1

print(f"[build] engine replaced + {applied}/{len(edits)} app edits applied")

# ─── 3) فحص: لا import resource في الملف كله ───
if re.search(r"^\s*import\s+resource\b", app_new, re.M):
    fail("built file still imports resource")

# ─── 4) roundtrip: المصدر المضمّن == الأصل + الطبقة بايت ببايت ───
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

# ─── 5) فحص AST لأسماء الواجهة داخل المحرك ───
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
    # v15.1: حالة دائرة التحميل + المرصد على المرحلتين
    "_QX_PRELOAD_STATUS", "_qx_on_message_with_instruments",
]
missing = [n for n in REQUIRED if n not in enames]
if missing:
    fail("missing engine names: " + ", ".join(missing))
print(f"[build] AST OK: all {len(REQUIRED)} interface names present in engine")

# ─── 6) كل مراجع qx.* في التطبيق موجودة فعلاً ───
mark0 = app_new.index(MARK)
close0 = app_new.index(CLOSE, mark0 + len(MARK))
app_outside = app_new[:mark0] + app_new[close0 + len(CLOSE):]
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

# ─── 7) كتابة الملف + py_compile ───
if not os.path.exists(BACKUP):
    shutil.copyfile(APP, BACKUP)
    print("[build] backup saved: " + BACKUP)
with open(APP, "w", encoding="utf-8", newline="") as f:
    f.write(app_new)
py_compile.compile(APP, doraise=True)
print(f"[build] py_compile OK — {APP} ({os.path.getsize(APP):,} bytes, "
      f"{len(app_new.splitlines()):,} lines)")

# ─── 8) اختبار دخان: تنفيذ المحرك كاملاً + اختبار المرصد على المرحلتين ───
tmp = tempfile.mkdtemp(prefix="qx_engine_smoke_")
eng_path = os.path.join(tmp, "qx_engine_test.py")
with open(eng_path, "w", encoding="utf-8") as f:
    f.write(embedded)
smoke = r'''
import os, sys, time, json, types
os.chdir(r"{tmp}")
src = open(r"{eng}", encoding="utf-8").read()
mod = {{"__name__": "qx_embedded_engine", "__file__": r"{eng}"}}
exec(compile(src, "qx_embedded_engine", "exec"), mod)
assert mod["ASYNC_LOOP"] is not None and mod["ASYNC_LOOP"].is_running(), "engine loop dead"
assert hasattr(mod["Asset"], "write"), "Asset missing"
st0 = mod["_QX_PRELOAD_STATUS"]
assert st0["active"] is False and st0["idx"] == 0 and st0["total"] == 0, "preload status broken"
d = mod["apply_history_days"](0.80)
assert abs(d - 0.80) < 1e-9, "history days mismatch"
assert mod["FETCH_DURATION_SECONDS"] == int(86400 * 0.80 * 1.15), "FETCH_DURATION mismatch"

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

# (أ) البروتوكول الرسمي: مرحلة 1 placeholder ثم مرحلة 2 إطار البيانات
c = _ClientStub()
on_msg(c, None, '451-["instruments/list",{{"asset_id":1,"_placeholder":true,"num":0}}]'.encode())
assert c.api.instruments is None, "phase1 must not store"
assert "instruments/list" in c.api._temp_status, "phase1 must remember"
on_msg(c, None, json.dumps([INST]).encode())
assert isinstance(c.api.instruments, list) and len(c.api.instruments) == 2, "phase2 must store"
assert c.api._temp_status == "", "phase2 must clear"
mod["CLIENT"] = c
snap = mod["_instruments_snapshot"]()
assert [e["asset"] for e in snap] == ["EURUSD_otc", "XAUUSD_otc"], "snapshot assets wrong"
assert snap[0]["payout"] == 92 and snap[0]["open"] is True, "snapshot fields wrong"

# (ب) الصيغة المضمّنة أيضاً تعمل (خطة بديلة)
c2 = _ClientStub()
on_msg(c2, None, ('451-["instruments/list",' + json.dumps(INST) + "]").encode())
assert isinstance(c2.api.instruments, list) and len(c2.api.instruments) == 2, "embedded format broken"

# (ج) رسالة عادية لا تُخرب المرصد ولا تُخزن شيئاً
c3 = _ClientStub()
on_msg(c3, None, '42["tick"]'.encode())
on_msg(c3, None, '[["EURUSD_otc",1700000000.0,1.23]]'.encode())
assert c3.api.instruments is None, "unrelated frames must not store"

print("SMOKE_OK loop=alive days=0.80 two_phase_instruments=ok embedded_instruments=ok preload_status=ok")
'''.replace("{tmp}", tmp).replace("{eng}", eng_path).replace("{{", "{").replace("}}", "}")
r = subprocess.run([sys.executable, "-c", smoke], capture_output=True, text=True, timeout=180)
ok = r.returncode == 0 and "SMOKE_OK" in r.stdout
print("[smoke] stdout:", r.stdout.strip()[-600:] if r.stdout else "(empty)")
if r.stderr.strip():
    print("[smoke] stderr tail:", r.stderr.strip()[-900:])
if not ok:
    fail("engine smoke test failed")
print("[smoke] OK — engine executes standalone, two-phase instruments verified")

shutil.rmtree(tmp, ignore_errors=True)
print("\nALL BUILD CHECKS PASSED")
