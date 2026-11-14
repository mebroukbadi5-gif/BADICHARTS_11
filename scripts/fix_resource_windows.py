# -*- coding: utf-8 -*-
"""
fix_resource_windows.py — إصلاح «No module named 'resource'» على ويندوز.

السبب: سطر استيراد مستوى الملف `import resource as _v14_resource` في محرك
v14 — وحدة `resource` موجودة على لينكس/ماك فقط. على ويندوز كان هذا السطر
يقتل تحميل المحرك كاملاً:
  - في النسخ القديمة (حمّال importlib مع تراجع لـ v13) كان التحميل يفشل
    بصمت والتطبيق يعمل بمحرك v13 القديم دون خصائص v14 (لهذا «لم يتغير ولا شيئ»
    في جولات سابقة رغم كل التحديثات!).
  - في v14.8 (المحرك المدمج بلا تراجع) يظهر:
    «[QX] embedded engine init failed: No module named 'resource'».

الإصلاح: الاستيراد شرطي (لينكس/ماك فقط) وNone على ويندوز — المتغير غير
مستخدم في أي مكان آخر (استيراد ميت). يُطبَّق على الملفين:
  1) qx_server_v14.py (الخادم المستقل)
  2) النسخة المدمجة داخل BadiChartsStudio_live.py (_QX_ENGINE_SOURCE)
"""
import io

BASE = "/home/z/my-project/download"

ANCHOR = "import resource as _v14_resource  # noqa: F401  (غير متاح على ويندوز — مستخدم بحذر أدناه)"
REPL = (
    "if os.name != \"nt\":                     # resource غير متاح على ويندوز — لينكس/ماك فقط\n"
    "    import resource as _v14_resource  # noqa: F401\n"
    "else:\n"
    "    _v14_resource = None               # لا يُستخدم في أي مكان آخر — استيراد ميت"
)

for path in (BASE + "/qx_server_v14.py", BASE + "/BadiChartsStudio_live.py"):
    src = io.open(path, encoding="utf-8").read()
    n = src.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"[FAIL] {path}: anchor found {n} times (expected 1)")
    src = src.replace(ANCHOR, REPL, 1)
    io.open(path, "w", encoding="utf-8").write(src)
    print(f"[ok] patched: {path}")
print("DONE")
