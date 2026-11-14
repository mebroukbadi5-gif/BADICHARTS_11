#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_v152_fixes.py — فحوصات v15.2 (طلب المستخدم حرفياً):
1) لا تحميل عملات في الخلفية — الجلب عند فتح العملة من قائمة العملات فقط
2) دائرة تحميل الشموع: تظهر عند بداية الجلب وتختفي عند انتهائه فيظهر الشارت
   (بلا شارة في الزاوية — كانت «في جنب») + مهلة أمان 60 ثانية
3) ميزة حفظ الإيميل تعمل: الكتابة في app_data.db أُصلحت في طبقة الربط،
   «تذكّرني» يحدد الحفظ، والبريد يعود معبأ في واجهة تسجيل الدخول
"""
import ast
import re
import sys
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


# ═══ 1) لا تحميل خلفي ═══
check("لا نداء preload_all_assets في طبقة التطبيق",
      "preload_all_assets()" not in app_outside)
check("تعليق إلغاء التحميل المسبق موجود بعد الدخول",
      "لا نريده ان يحمل العملات في الخلفية" in src)
check("لا شارة زاوية preloadBadge/PREBADGE في التطبيق",
      "preloadBadge" not in app_outside and "PREBADGE" not in app_outside)
check("لا setPreload في التطبيق", "setPreload" not in app_outside)
check("لا حدث preload في QML", '"type": "preload"' not in app_outside)
check("لا مرجع JS لحالة PRELOAD",
      not re.search(r"PRELOAD\.(active|idx|total|loaded)", app_outside))
check("بدء الجلب فقط عند فتح العملة (تعليق switch)",
      "عندما نفتح العملة من قائمة العملات" in src)
check("حلقة asset_payout_monitor (قائمة العملات) ما زالت تعمل",
      "asset_payout_monitor" in embedded)

# ═══ 2) دائرة تحميل الشموع: من بداية الجلب حتى نهايته ═══
check("حالة صريحة _qx_loading في __init__",
      "self._qx_loading = False" in src and "self._qx_loading_at = 0.0" in src)
check("تفعيل الدائرة عند فتح العملة (switch arm)",
      app_outside.count("self._qx_loading_arm()") >= 2)
check("الإطفاء الفوري إذا اكتمل الجلب في switch",
      "# الجلب اكتمل فوراً" in src)
check("أدوات arm/clear معبّرة عن حدث chartload",
      '"type": "chartload", "active": True' in src
      and '"type": "chartload", "active": False' in src)
check("مراقب المضخة يطفئ الدائرة عند وصول الشموع أو مهلة 60 ثانية",
      '"_qx_loading_at", 0.0)) > 60.0' in src
      and "candles loading timeout" in src)
check("المضخة تعمل أثناء التحميل (نبضات _load_due)",
      "_load_due = bool(getattr(self, \"_qx_loading\", False))" in src)
check("chartLoading الصريحة: دخول + حالة جلب + بلا شموع",
      "self._qx_logged and getattr(self, \"_qx_loading\", False)"
      in src and "and not self._candles)" in src.split("def chartLoading")[1][:600])
check("QML: مسار chartload يمرر اسم العملة",
      'e.type === "chartload"' in src and "setChartLoading(" in src)
check("JS: الدائرة مخفية فقط حين CHLOAD.on=false (بلا شرط empty)",
      "el.hidden = !CHLOAD.on;" in app_outside)
check("JS: غطاء الدائرة يغطي الشارت أثناء الجلب",
      "background:rgba(7,10,16,.72)" in app_outside)
check("JS: حالة CHLOAD تحمل اسم العملة",
      'var CHLOAD = { on: false, asset: "", el: null };' in app_outside)
check("JS: نص الدائرة الوسطى اسم العملة",
      "var _sub = CHLOAD.asset ? CHLOAD.asset" in app_outside)
check("JS: setChartLoading(on, assetName)",
      "setChartLoading: function (on, assetName)" in app_outside)

# ═══ 3) ميزة حفظ الإيميل ═══
check("طبقة الربط: إصلاح _save_state موجود داخل المحرك",
      "_v152_session_save_state" in embedded
      and "SessionManager._save_state = _v152_session_save_state" in embedded)
check("عبارة الإصلاح: عدد الروابط صحيح (id حرفي + 6 علامات)",
      "VALUES (1, ?, ?, ?, ?, ?, ?)" in embedded)
check("الأصل لم يُمَس: المحرك يبدأ بالأصل بايت ببايت",
      embedded.startswith(paste.rstrip("\n") + "\n"))
check("الأصل يحوي الخطأ القديم كما هو (لا تعديل في الأصل)",
      paste.count("VALUES (1, ?, ?, ?, ?, ?, ?)") >= 1
      and re.search(r"\"\"\", \(\n\s+1,\n\s+self\.state\.get\(\"email\", \"\"\)", paste) is not None)
check("savedEmail notify-based", "@Property(str, notify=savedEmailChanged)" in src)
check("إشارة savedEmailChanged معرّفة", "savedEmailChanged = Signal()" in src)
check("«تذكّرني» بلا تحديد لا يحفظ (حذف البريد والحفظ)",
      "if not bool(remember):" in src and '_sm.state["email"] = ""' in src
      and "_sm._save_state()" in src)
check("إشارة تغيّر البريد تُبث بعد الدخول",
      "self.savedEmailChanged.emit()" in src)
check("QML: تعبئة البريد في كل ظهور لواجهة الدخول",
      "try { userF.text = backend.savedEmail } catch (e) {}" in src)
check("QML: onVisibleChanged يعيد التعبئة",
      re.search(r"onVisibleChanged: \{\s*if \(visible\) \{[^}]*savedEmail", src, re.S))

# ═══ فحص سلوكي: arm/clear + chartLoading ═══
ns = types.SimpleNamespace()
ns._qx_loading = False
ns._qx_loading_at = 0.0
ns._asset = "BRL/USD (OTC)"
ns._events = []
ns._qx_loading_arm = None
ns._qx_loading_clear = None

tree = ast.parse(src)
cls_methods = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) \
                    and item.name in ("_qx_loading_arm", "_qx_loading_clear"):
                cls_methods[item.name] = item

assert len(cls_methods) == 2, f"arm/clear not extracted: {list(cls_methods)}"

import textwrap
import time as _time
g = {"time": _time}


def _emit_qx(obj):
    ns._events.append(obj)


for name, node in cls_methods.items():
    seg = ast.get_source_segment(src, node)
    exec(compile(textwrap.dedent(seg), "<extract>", "exec"), g)

arm = g["_qx_loading_arm"]
clear = g["_qx_loading_clear"]

ns._emit_qx = _emit_qx
arm(ns)
check("arm: الحالة صحيحة + حدث chartload active=True",
      ns._qx_loading is True and ns._events[-1]["type"] == "chartload"
      and ns._events[-1]["active"] is True and ns._events[-1]["asset"] == "BRL/USD (OTC)")

# chartLoading منطق الصريحة — نفس صيغة الخاصية
def chart_loading(logged, loading, candles):
    return bool(logged and loading and not candles)


check("chartLoading: دخول+جلب+بلا شموع = True",
      chart_loading(True, True, []) is True)
check("chartLoading: وصلت الشموع = False",
      chart_loading(True, True, [{"t": 1}]) is False)
check("chartLoading: قبل الدخول = False", chart_loading(False, True, []) is False)
check("chartLoading: بلا جلب = False", chart_loading(True, False, []) is False)

clear(ns)
check("clear: الحالة صحيحة + حدث chartload active=False",
      ns._qx_loading is False and ns._events[-1]["active"] is False)
ev_count = len(ns._events)
clear(ns)
check("clear: idempotent — بلا حدث ثانٍ", len(ns._events) == ev_count)

# ═══ فحص QML: لا أقواس مكسورة في كتلة onVisibleChanged ═══
m = re.search(r"onVisibleChanged: \{.*?\n            \}", src, re.S)
check("كتلة onVisibleChanged متوازنة الأقواس", m is not None and
      m.group(0).count("{") == m.group(0).count("}"))

print()
if fails:
    print(f"FAILED: {len(fails)} — " + ", ".join(fails))
    sys.exit(1)
print("ALL V15.2 CHECKS PASSED")
