#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v15_original.py — «الأصل هو الخادم» (طلب المستخدم الحرفي)

يستبدل المحرك المضمّن في BadiChartsStudio_live.py بملف الخادم الأصلي المُلصق
من المستخدم (qx_mt4_original.py) **بايت ببايت دون أي تغيير**، ويضيف بعده فقط
طبقة ربط التطبيق (qx_compat_v15.py — جسور بلا منطق جديد)، ثم يطبّق تعديلات
الواجهة الخلفية القليلة:
  1) تاريخ افتراضي 0.80 يوم (طلب المستخدم)
  2) تطبيق الأيام عبر apply_history_days (آلية قائمة الأصل نفسها) — 3 مواضع
  3) سلسلة التاريخ عبر qx_get_historical_batches (نفس _fetch_historical_batch الأصلية)
  4) استيعاب بلا تقليص في 3 مواضع (حماية شموع التاريخ من نافذة البث القصيرة)
  5) مؤقّت التحديث: كل تيك يصل (فاتح 40ms + بوابة بصمة التيك) بدل 400ms

تحققات صارمة: py_compile + roundtrip بايت-ب-بايت + فحص AST لأسماء الواجهة
+ فحص مراجع qx.* في التطبيق + لا وجود لأي import resource.
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
APP_OUT = os.path.join(ROOT, "download", "BadiChartsStudio_live.py")
BACKUP = os.path.join(ROOT, "scripts", "BadiChartsStudio_live.v14.8.bak.py")

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

# ─── 0) سلامة الحقن: لا ''' في المصدرين ───
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

# ─── 2) تعديلات الواجهة الخلفية (مثبّتة بمراسي فريدة) ───
edits = []

def edit(old, new, name):
    edits.append((old, new, name))

# (1) الافتراضي 0.80 يوم — قراءة الإعدادات
edit(
    '            _hd = float(str(cfg.get("hist_days", 2.0)).replace(",", "."))',
    '            _hd = float(str(cfg.get("hist_days", 0.80)).replace(",", "."))',
    "hist default cfg")

edit(
    "        except Exception:\n            _hd = 2.0\n        self._hist_days = max(0.5, min(30.0, _hd))",
    "        except Exception:\n            _hd = 0.80\n        self._hist_days = max(0.5, min(30.0, _hd))",
    "hist default fallback")

# (2a) setHistDays — تطبيق آلية الأصل
edit(
    '                qx.QX_HISTORY_DAYS = d\n'
    '            except Exception:\n'
    '                pass\n'
    '        self._log("ok", T[self._lang].get("histSaved", "History days saved"))',
    '                qx.QX_HISTORY_DAYS = d\n'
    '                qx.apply_history_days(d)   # آلية قائمة الأصل نفسها (هامش +15% + INITIAL_CANDLES + FETCH_DURATION)\n'
    '            except Exception:\n'
    '                pass\n'
    '        self._log("ok", T[self._lang].get("histSaved", "History days saved"))',
    "apply_history_days @ setHistDays")

# (2b) سلسلة التاريخ — تطبيق آلية الأصل
edit(
    "                qx.QX_HISTORY_DAYS = days\n"
    "            except Exception:\n"
    "                pass\n"
    "            if _stale():",
    "                qx.QX_HISTORY_DAYS = days\n"
    "                qx.apply_history_days(days)   # آلية قائمة الأصل نفسها\n"
    "            except Exception:\n"
    "                pass\n"
    "            if _stale():",
    "apply_history_days @ chain worker")

# (2c) دخول الخادم — تطبيق آلية الأصل
edit(
    "                qx.QX_HISTORY_DAYS = self._hist_days_cfg()\n"
    "            except Exception:\n"
    "                pass\n",
    "                qx.QX_HISTORY_DAYS = self._hist_days_cfg()\n"
    "                qx.apply_history_days(self._hist_days_cfg())   # آلية قائمة الأصل نفسها\n"
    "            except Exception:\n"
    "                pass\n",
    "apply_history_days @ login worker")

# (3) سلسلة التاريخ عبر نفس _fetch_historical_batch الأصلية
edit(
    "            fut = asyncio.run_coroutine_threadsafe(\n"
    "                qx.CLIENT.get_historical_candles(\n"
    "                    api, amount_of_seconds=target, period=tf_sec,\n"
    "                    max_workers=5, batch_callback=_on_batch),\n"
    "                qx.ASYNC_LOOP)",
    "            fut = asyncio.run_coroutine_threadsafe(\n"
    "                qx.qx_get_historical_batches(\n"
    "                    api, amount_of_seconds=target, period=tf_sec,\n"
    "                    max_workers=5, batch_callback=_on_batch),\n"
    "                qx.ASYNC_LOOP)",
    "chain via original _fetch_historical_batch")

# (4a) مزامنة ما بعد السلسلة: استيعاب بلا تقليص
edit(
    "                        eng = self._qx_engine_candles(api)\n"
    "                        if eng:\n"
    "                            self._candles = eng[-self._QX_FEED_CAP:]\n"
    "                            self._qx_last_sig = None   # المضخة تدفع الغذاء المُصلَح فوراً",
    "                        eng = self._qx_engine_candles(api)\n"
    "                        if eng:\n"
    "                            # v15: استيعاب بلا تقليص — نافذة البث الأصلية (INITIAL_CANDLES)\n"
    "                            # لا تُقصّ شموع دفعات التاريخ من الشارت أبداً\n"
    "                            self._qx_absorb_engine_no_shrink(eng)\n"
    "                            self._qx_last_sig = None   # المضخة تدفع الغذاء المُصلَح فوراً",
    "resync absorb no-shrink")

# (4b) السد العميق في الخطوة الحية: استيعاب بلا تقليص
edit(
    "                        self._qx_deep_seen = _ds_t\n"
    "                        self._candles = candles[-self._QX_FEED_CAP:]\n"
    "                        self._qx_last_sig = None",
    "                        self._qx_deep_seen = _ds_t\n"
    "                        self._qx_absorb_engine_no_shrink(candles)\n"
    "                        self._qx_last_sig = None",
    "deep-seal absorb no-shrink")

# (4c) دفعة التمرير: استيعاب بلا تقليص
edit(
    "                    if tf_sec == 60:\n"
    "                        self._candles = self._qx_engine_candles(api)\n"
    "                        if len(self._candles) > self._QX_FEED_CAP:\n"
    "                            self._candles = self._candles[-self._QX_FEED_TRIM:]\n"
    "                    else:",
    "                    if tf_sec == 60:\n"
    "                        self._qx_absorb_engine_no_shrink(self._qx_engine_candles(api))\n"
    "                    else:",
    "older-batch absorb no-shrink")

# (5a) المؤقّت: فاتح 40ms — التحديث الفعلي عند كل تيك
edit(
    "        self._qxT = QTimer(self)\n"
    "        self._qxT.setInterval(400)\n"
    "        self._qxT.timeout.connect(self._qx_poll)\n"
    "        self._qxT.start()",
    "        self._qxT = QTimer(self)\n"
    "        # v15 (طلب المستخدم حرفياً): التحديث ليس كل 400/500 ميلي ثانية بل كل\n"
    "        # تيك يصل — المؤقّت فاتح فقط (40ms) و_qx_poll تخرج فوراً بلا تيك جديد\n"
    "        self._qxT.setInterval(40)\n"
    "        self._qxT.timeout.connect(self._qx_poll)\n"
    "        self._qxT.start()",
    "timer 40ms tick gate")

# (5b) بوابة بصمة التيك داخل المضخة نفسها
edit(
    '    def _qx_poll(self):\n'
    '        """مضخة الخادم: لوحة العملات + التغذية الحية + حالة التحميل المسبق."""\n'
    '        if not self._qx_logged:\n'
    '            return\n'
    '        qx = _qx_module()\n'
    '        if qx is None or getattr(qx, "CLIENT", None) is None:\n'
    '            return\n',
    '    def _qx_poll(self):\n'
    '        """مضخة الخادم: لوحة العملات + التغذية الحية + حالة التحميل المسبق."""\n'
    '        if not self._qx_logged:\n'
    '            return\n'
    '        qx = _qx_module()\n'
    '        if qx is None or getattr(qx, "CLIENT", None) is None:\n'
    '            return\n'
    '        # ═══ v15 (طلب المستخدم حرفياً): التحديث عند وصول كل تيك ═══\n'
    '        # realtime_stream الأصلية تحدّث last_update_time عند كل تيك يصل —\n'
    '        # لا تيك جديد → خروج فوري بلا أي عمل. اللوحة والحالة كل ثانيتين.\n'
    '        try:\n'
    '            _api_now = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)\n'
    '        except Exception:\n'
    '            _api_now = None\n'
    '        _stamp = None\n'
    '        try:\n'
    '            _a = qx._get_or_create_asset(_api_now) if _api_now else None\n'
    '            if _a is not None:\n'
    '                _stamp = (float(getattr(_a, "last_update_time", 0) or 0),\n'
    '                          float(getattr(_a, "price", 0) or 0),\n'
    '                          len(getattr(_a, "candles", []) or []))\n'
    '        except Exception:\n'
    '            _stamp = None\n'
    '        _now = time.time()\n'
    '        _tick_new = (_stamp is not None and _stamp != getattr(self, "_qx_tick_stamp", None))\n'
    '        if _tick_new:\n'
    '            self._qx_tick_stamp = _stamp\n'
    '        _board_due = (_now - getattr(self, "_qx_board_at", 0.0)) >= 2.0\n'
    '        if not _tick_new and not _board_due and not getattr(self, "_qx_resync_pending", False):\n'
    '            return\n'
    '        if _board_due:\n'
    '            self._qx_board_at = _now\n',
    "tick-gate in _qx_poll")

# (6) توثيق الافتراضي في docstring القارئ
edit(
    '        """عدد أيام شموع التاريخ المضبوط من الإعدادات (0.5 حتى 30، الافتراضي 2).',
    '        """عدد أيام شموع التاريخ المضبوط من الإعدادات (0.5 حتى 30، الافتراضي 0.80 — طلب المستخدم).',
    "hist docstring")

applied = 0
for old, new, name in edits:
    n = app_new.count(old)
    if n != 1:
        fail(f"anchor '{name}' count = {n} (expected 1)")
    app_new = app_new.replace(old, new, 1)
    applied += 1

print(f"[build] engine replaced + {applied}/{len(edits)} backend edits applied")

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
rt_base_ok = embedded.startswith(paste.rstrip("\n") + "\n")
rt_compat_ok = embedded.endswith(compat.rstrip("\n") + "\n")
if not (rt_base_ok and rt_compat_ok):
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
    # أسماء الأصل المستخدمة من التطبيق
    "connect_quotex", "health_monitor", "auto_reconnect", "keepalive_loop",
    "stale_message_watchdog", "mt4_gap_filler", "fetch_candles_with_retry",
    "realtime_stream", "refetch_all_candles", "Asset", "_align_time",
    "_fill_missing_slots", "session_manager", "MT4_WRITER", "ASYNC_LOOP",
    "CLIENT", "ALL_STREAMING_ASSETS", "QX_HOST", "PERIOD", "PERIOD_SECONDS",
    "INITIAL_CANDLES", "HISTORY_DAYS", "FETCH_DURATION_SECONDS",
    "MIN_CANDLES_THRESHOLD", "MAX_FETCH_RETRIES", "FETCH_ASSET_DELAY",
    "_parse_raw_candles", "_request_counter", "WebsocketClient",
    # أسماء طبقة الربط
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
]
missing = [n for n in REQUIRED if n not in enames]
if missing:
    fail("missing engine names: " + ", ".join(missing))
print(f"[build] AST OK: all {len(REQUIRED)} interface names present in engine")

# ─── 6) كل مراجع qx.* في التطبيق (خارج المحرك) موجودة فعلاً ───
app_outside = app_new[:app_new.index(MARK)] + app_new[app_new.index(CLOSE, app_new.index(MARK) + len(MARK)) + len(CLOSE):]
refs = set(re.findall(r"\bqx\.([A-Za-z_][A-Za-z0-9_]*)", app_outside))
refs |= set(re.findall(r'getattr\(qx, "([A-Za-z_][A-Za-z0-9_]*)"', app_outside))
code_lines = []
for ln in app_outside.splitlines():
    st = ln.strip()
    if st.startswith("#"):
        continue
    code_lines.append(ln)
refs_code = set()
for ln in code_lines:
    refs_code |= set(re.findall(r"\bqx\.([A-Za-z_][A-Za-z0-9_]*)", ln))
    refs_code |= set(re.findall(r'getattr\(qx, "([A-Za-z_][A-Za-z0-9_]*)"', ln))
unresolved = sorted(n for n in refs_code if n not in enames)
if unresolved:
    fail("app references unknown engine names: " + ", ".join(unresolved))
print(f"[build] interface check OK: {len(refs_code)} qx.* references all resolve")

# ─── 7) كتابة الملف + py_compile ───
shutil.copyfile(APP, BACKUP)
with open(APP_OUT, "w", encoding="utf-8", newline="") as f:
    f.write(app_new)
py_compile.compile(APP_OUT, doraise=True)
print(f"[build] py_compile OK — {APP_OUT} ({os.path.getsize(APP_OUT):,} bytes, "
      f"{len(app_new.splitlines()):,} lines)")

# ─── 8) اختبار دخان: تنفيذ المحرك كاملاً في subprocess نظيف ───
tmp = tempfile.mkdtemp(prefix="qx_engine_smoke_")
eng_path = os.path.join(tmp, "qx_engine_test.py")
with open(eng_path, "w", encoding="utf-8") as f:
    f.write(embedded)
smoke = r'''
import os, sys, time
os.chdir(r"{tmp}")
src = open(r"{eng}", encoding="utf-8").read()
mod = {{"__name__": "qx_embedded_engine", "__file__": r"{eng}"}}
exec(compile(src, "qx_embedded_engine", "exec"), mod)
# المحرك يعمل: الحلقة حية + الأصول + الآلة
assert mod["ASYNC_LOOP"] is not None and mod["ASYNC_LOOP"].is_running(), "engine loop dead"
assert hasattr(mod["Asset"], "write"), "Asset missing"
# طبقة الربط: آلية الأيام الأصلية
d = mod["apply_history_days"](0.80)
assert abs(d - 0.80) < 1e-9, "history days mismatch"
assert mod["FETCH_DURATION_SECONDS"] == int(86400 * 0.80 * 1.15), "FETCH_DURATION mismatch"
assert mod["INITIAL_CANDLES"] == max(int(0.80 * 86400 // 60), 100), "INITIAL_CANDLES mismatch"
# تنسيق الرد الرسمي
fmt = mod["_format_raw_candles"]([{{"time": 1700000000, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15}}])
assert fmt and fmt[0]["close"] == 1.15, "format_raw_candles broken"
# سجل الأصول عبر Asset الأصلي حرفياً
a = mod["_get_or_create_asset"]("EURUSD_otc")
assert a.api_symbol == "EURUSD_otc" and a.candles == [], "asset registry broken"
assert mod["_get_or_create_asset"]("EURUSD_otc") is a, "asset registry not deduped"
# علامات السد عبر مخازن الأصل حرفياً
mod["clear_gap_flag_any"](["EURUSD_otc", "EURUSD-OTC"])
mod["reset_gap_flags"]()
# الطباعة الرسمية للوحة
snap = mod["_instruments_snapshot"]()
assert snap == [], "instruments snapshot must be empty before connect"
print("SMOKE_OK", "loop=alive", "days=0.80", "assets_registry=ok", "gap_flags=ok")
'''.replace("{tmp}", tmp).replace("{eng}", eng_path)
smoke = smoke.replace('mod["ASYNC_LOOP"]', 'mod["ASYNC_LOOP"]').replace("{{", "{").replace("}}", "}")
r = subprocess.run([sys.executable, "-c", smoke], capture_output=True, text=True, timeout=180)
ok = r.returncode == 0 and "SMOKE_OK" in r.stdout
print("[smoke] stdout:", r.stdout.strip()[-500:] if r.stdout else "(empty)")
if r.stderr.strip():
    print("[smoke] stderr tail:", r.stderr.strip()[-800:])
if not ok:
    fail("engine smoke test failed")
print("[smoke] OK — engine executes standalone (threads alive, glue works)")

shutil.rmtree(tmp, ignore_errors=True)
print("\nALL BUILD CHECKS PASSED")
