#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار إقلاع التطبيق كاملاً (شاشة افتراضية) — يثبت أن:
1) الملف يُستورد ويعمل بلا أخطاء
2) المحرك المدمج (الأصل) يُنفَّذ فعلاً داخل التطبيق (_qx_module)
3) حلقة المحرك حية وطبقة الربط تعمل داخل نفس العملية
"""
import os
import subprocess
import sys

TEST = r'''
import os, sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu"
sys.argv = ["BadiChartsStudio_live.py"]

import importlib.util
spec = importlib.util.spec_from_file_location("badi_app", r"{APP}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("APP_IMPORT_OK")

# نفّذ المحرك المدمج عبر _qx_module نفسها (نفس مسار التطبيق الحقيقي)
qx = mod._qx_module()
assert qx is not None, "engine failed to load inside app: " + repr(mod._QX_MOD)
assert qx.ASYNC_LOOP is not None and qx.ASYNC_LOOP.is_running(), "engine loop dead"
assert hasattr(qx, "preload_all_assets") and hasattr(qx, "ensure_asset_loaded")
assert hasattr(qx, "qx_get_historical_batches") and hasattr(qx, "apply_history_days")
qx.apply_history_days(0.80)
assert qx.FETCH_DURATION_SECONDS == int(86400 * 0.80 * 1.15)
print("ENGINE_IN_APP_OK", "loop=alive", "days=0.80")
print("BOOT_ALL_OK")
'''.replace("{APP}", "/home/z/my-project/download/BadiChartsStudio_live.py")

r = subprocess.run([sys.executable, "-c", TEST], capture_output=True, text=True,
                   timeout=180, cwd="/tmp")
print("returncode:", r.returncode)
out = (r.stdout or "").strip()
err = (r.stderr or "").strip()
for ln in out.splitlines()[-15:]:
    print("OUT:", ln[:160])
if err:
    print("ERR tail:", err[-1500:])
print("BOOT:", "PASS" if ("APP_IMPORT_OK" in out and "ENGINE_IN_APP_OK" in out
                           and "BOOT_ALL_OK" in out) else "FAIL")
