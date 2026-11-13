# -*- coding: utf-8 -*-
"""اختبار وظيفي للدوال الجديدة في النسخة الحية (بدون PySide6)"""
import ast
import json
import types
import textwrap

SRC = "/home/z/my-project/gh_repo/BadiChartsStudio_live.py"
src = open(SRC, encoding="utf-8").read()
tree = ast.parse(src)

# استخراج دوال Backend الجديدة
backend = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "Backend")
WANT = {"_api_from_display", "_display_from_api", "_fmt_engine_candles", "_qx_fmt_raw",
        "_ticks_to_candles", "_qx_merge_tail_full", "_qx_extend_tail", "_board_sig"}
ns = {}
for node in backend.body:
    if isinstance(node, ast.FunctionDef) and node.name in WANT:
        code = ast.get_source_segment(src, node)
        ns[node.name] = code

NS = {"json": json}
g = {"__name__": "t"}
exec("import json, time", g)
for name, code in ns.items():
    code = textwrap.dedent(code)
    code = code.replace("@staticmethod\n    ", "@staticmethod\n")
    code = code.replace("@Property(str, constant=True)\n    ", "")
    code = code.replace("@Slot(str, str, bool)\n    ", "")
    code = code.replace("@Slot(str)\n    ", "")
    # تقليم المسافات البادئة للدوال داخل الصف
    lines = code.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    body = "\n".join(l[4:] if l.startswith("    ") else l for l in lines)
    g[name] = None
    exec("def " + body.split("def ", 1)[1] if False else body, g)

self = types.SimpleNamespace(_candles=[], _QX_FEED_CAP=3000, _QX_FEED_TRIM=2600)

f_disp = g["_display_from_api"]
f_api = g["_api_from_display"]
f_fmt = g["_fmt_engine_candles"]
f_raw = g["_qx_fmt_raw"]
f_ticks = g["_ticks_to_candles"]
f_merge = g["_qx_merge_tail_full"]
f_ext = g["_qx_extend_tail"]

cases = [
    (f_disp("BRLUSD_otc"), "BRL/USD OTC"),
    (f_api("BRL/USD OTC"), "BRLUSD_otc"),
    (f_disp("EURUSD_otc"), "EUR/USD OTC"),
    (f_disp("BTCUSD_otc"), "BTC/USD OTC"),
    (f_disp("XAUUSD_otc"), "XAU/USD OTC"),
    (f_disp("DOGEUSD"), "DOGE/USD"),
    (f_disp("USDBDT_otc"), "USD/BDT OTC"),
    (f_api("EUR/USD OTC"), "EURUSD_otc"),
    (f_api("USD/PKR OTC"), "USDPKR_otc"),
    (f_api("BTC/USD"), "BTCUSD"),
    (f_api("BTC/USD OTC"), "BTCUSD_otc"),
    (f_api("DOGE/USD"), "DOGEUSD"),
    (f_api("BRL/USD OTC"), "BRLUSD_otc"),
]
ok = True
for got, want in cases:
    flag = "OK " if got == want else "FAIL"
    if got != want:
        ok = False
    print(f"[{flag}] {got!r} == {want!r}")

# الشموع من تيكات الخادم
ticks = [(1000, 1.0), (1001, 1.1), (1004, 1.2), (1005, 1.3), (1009, 1.25), (1010, 1.4)]
c = f_ticks(ticks, 5)
exp = [{"t": 1000, "o": 1.0, "h": 1.2, "l": 1.0, "c": 1.2, "v": 3},
       {"t": 1005, "o": 1.3, "h": 1.3, "l": 1.25, "c": 1.25, "v": 2},
       {"t": 1010, "o": 1.4, "h": 1.4, "l": 1.4, "c": 1.4, "v": 1}]
print("[{}] ticks_to_candles".format("OK " if c == exp else "FAIL"), c)
ok = ok and c == exp

# تنسيق رد الخادم لفريم 5 دقائق
res = [{"time": 3005, "open": 1.0, "high": 1.5, "low": 0.9, "close": 1.2},
       {"time": 3010, "open": 1.2, "high": 1.6, "low": 1.1, "close": 1.3},
       {"time": 3001, "open": 1.0, "high": 1.4, "low": 0.95, "close": 1.1}]
raw = f_raw(res, 300)
exp2 = [{"t": 3000, "o": 1.0, "h": 1.5, "l": 0.9, "c": 1.2, "v": 0}]
# 3001 و 3005 كلاهما على نفس حد 300 → الأول فقط (dedupe) — 3010 يبقى خارج القائمة؟ لا: 3010 % 300 = 3010-3000=10 → حد 3000 أيضاً؟ 3010 - (3010 % 300) = 3000 → نفس الدلو!
# إذاً النتيجة دلو واحد 3000 بأول قراءة (3001 يأتي ثانياً بعد 3005 بالفرز؟ لا — الفرز بعد التجميع)
print("[INFO] raw:", raw)
ok = ok and len(raw) == 1 and raw[0]["t"] == 3000

# الدمج من الذيل: لا تقصم الرأس، تحدّث آخر شمعة، تضيف الجديد
self._candles = [{"t": 100, "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 9}]
feed = [{"t": 100, "o": 1, "h": 2, "l": 0.5, "c": 1.6, "v": 9},
        {"t": 160, "o": 1.6, "h": 1.8, "l": 1.4, "c": 1.7, "v": 3}]
ch = f_merge(self, feed)
exp3 = [{"t": 100, "o": 1, "h": 2, "l": 0.5, "c": 1.6, "v": 9},
        {"t": 160, "o": 1.6, "h": 1.8, "l": 1.4, "c": 1.7, "v": 3}]
print("[{}] merge_tail_full".format("OK " if ch and self._candles == exp3 else "FAIL"), self._candles)
ok = ok and ch and self._candles == exp3

# لا تغيير → False
ch2 = f_merge(self, feed)
print("[{}] merge no-change = False".format("OK " if ch2 is False else "FAIL"))
ok = ok and ch2 is False

# مدّ الذيل: نفس الدلو تحديث، دلو جديد إضافة (ساعة وهمية عند 1035)
import types as _t
fake_time = _t.SimpleNamespace(time=lambda: 1035.0)
g["time"] = fake_time
self._candles = [{"t": 1000, "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05, "v": 1}]
e1 = f_ext(self, 1.2, 30)      # نفس الدلو (1020) → تحديث
e2 = f_ext(self, 1.3, 30)      # 1020 → نفس الدلو تحديث
g["time"] = _t.SimpleNamespace(time=lambda: 1051.0)
e3 = f_ext(self, 1.4, 30)      # 1050 → دلو جديد
exp4 = [{"t": 1000, "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05, "v": 1},
        {"t": 1020, "o": 1.05, "h": 1.3, "l": 1.05, "c": 1.3, "v": 0},
        {"t": 1050, "o": 1.3, "h": 1.4, "l": 1.3, "c": 1.4, "v": 0}]
print("[{}] extend_tail".format("OK " if e1 and e3 and self._candles == exp4 else "FAIL"), self._candles)
ok = ok and e1 and e3 and self._candles == exp4

# تنسيق شموع الخادم
eng = [{"time": 5000, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 10}]
fc = f_fmt(eng)
print("[{}] fmt_engine_candles".format("OK " if fc == [{"t": 5000, "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 10}] else "FAIL"))
ok = ok and fc == [{"t": 5000, "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 10}]

print("\nRESULT:", "ALL OK" if ok else "SOME FAILURES")
