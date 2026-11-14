#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""فحص نهائي شامل للملف المبني v15"""
import re

P = '/home/z/my-project/download/BadiChartsStudio_live.py'
src = open(P, encoding='utf-8').read()
Q3 = chr(39) * 3
MARK = "_QX_ENGINE_SOURCE = r" + Q3
ok = True

def check(name, cond, extra=""):
    global ok
    print(("PASS" if cond else "FAIL"), "-", name, extra)
    if not cond:
        ok = False

# 1) لا import resource نهائياً (سبب انهيار ويندوز)
res_hits = [i for i, ln in enumerate(src.splitlines(), 1)
            if re.match(r"\s*import\s+resource\b", ln)]
check("لا import resource في الملف كله", not res_hits, str(res_hits[:4]))

# 2) حدود المحرك: الأصل حرفياً
n_mark = src.count(MARK)
check("علامة المحرك واحدة", n_mark == 1, f"count={n_mark}")
i0 = src.index(MARK) + len(MARK)
j0 = src.index("\n" + Q3, i0)
embedded = src[i0:j0]
paste = open('/home/z/my-project/upload/qx_mt4_original.py', encoding='utf-8').read().rstrip("\n")
check("المحرك يبدأ بالأصل المُلصق حرفياً", embedded.startswith(paste + "\n"),
      f"engine_len={len(embedded):,}")
check("المحرك يبدأ ب#! من سطر الأصل", embedded.startswith("#!/usr/bin/env python3"))
check("main-guard الأصل موجود داخل المحرك", 'if __name__ == "__main__":' in embedded)
check("لا import resource داخل المحرك", "import resource" not in embedded)

# 3) طبقة الربط موجودة في نهاية المحرك
for name in ["preload_all_assets", "ensure_asset_loaded", "qx_get_historical_batches",
             "apply_history_days", "QX_HISTORY_DAYS = 0.80", "PRELOAD_CANDLES = 700",
             "PAGINATION_BATCH = 700", "instruments/list", "v14_deep_gap_seal",
             "tick_cache_collector", "fetch_older_batch", "resolve_qx_host"]:
    check("طبقة الربط: " + name, name in embedded)

# 4) تعديلات الواجهة الخلفية الـ12
checks_app = [
    ('cfg.get("hist_days", 0.80)', "الافتراضي 0.80 يوم"),
    ("_hd = 0.80", "fallback الافتراضي"),
    ("qx.apply_history_days(d)", "apply @ setHistDays"),
    ("qx.apply_history_days(days)", "apply @ chain worker"),
    ("qx.apply_history_days(self._hist_days_cfg())", "apply @ login worker"),
    ("qx.qx_get_historical_batches(", "السلسلة عبر _fetch_historical_batch الأصلية"),
    ("self._qx_absorb_engine_no_shrink(eng)", "استيعاب بلا تقليص @ resync"),
    ("self._qx_absorb_engine_no_shrink(candles)", "استيعاب بلا تقليص @ deep-seal"),
    ("self._qx_absorb_engine_no_shrink(self._qx_engine_candles(api))", "استيعاب بلا تقليص @ older"),
    ("self._qxT.setInterval(40)", "مؤقّت فاتح 40ms"),
    ("_qx_tick_stamp", "بوابة بصمة التيك"),
]
for needle, name in checks_app:
    check("الخلفية: " + name, needle in src)

# 5) لا مؤقّت 400/500ms قديم للمضخة
check("لا setInterval(400) للمضخة", "self._qxT.setInterval(400)" not in src)

# 6) _qx_module كما هو (التحميل المدمج)
check("_qx_module تُنفّذ المصدر في وحدة معزولة",
      'exec(compile(_QX_ENGINE_SOURCE, "qx_embedded_engine", "exec"), _mod.__dict__)' in src)

# 7) عدد الأسطر والحجم
lines = src.count("\n") + 1
print(f"INFO - الحجم: {len(src):,} بايت | الأسطر: {lines:,}")

print("\nRESULT:", "ALL FINAL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
