# -*- coding: utf-8 -*-
"""build_v149_fix1.py — تصحيح نافذة السد العميق:

نافذة get_candles(end, offset) هي (end-offset, end] — لا تشمل نقطة المرساة
نفسها! فكانت أقدم شمعة اصطناعية (المرساة) لا تدخل النافذة أبداً: يهدر
السد جولات على نفس المرساة (الخادم يعيد شموعاً حقيقية موجودة أصلاً =
بلا تقدم = مؤشر تخطٍّ) وتبقى الشمعة الاصطناعية الأولى + تُقصّر التغطية
فترة واحدة. الإصلاح: offset = win_s + period_s فتصير النافذة
[المرساة، المرساة + 200 شمعة] — كل جولة تسد كامل 200 شمعة بلا هدر."""
import io

BASE = "/home/z/my-project/download"
FILES = [BASE + "/qx_server_v14.py", BASE + "/BadiChartsStudio_live.py"]

ANCHOR = ("        try:\n"
          "            # نفس نداء الجلب الرسمي الذي تستخدمه الآلة الأصلية fill_gap_once\n"
          "            fetched = await client.get_candles(api_symbol, anchor_end, win_s, period_s)\n"
          "        except Exception:\n"
          "            fetched = None")

REPL = ("        try:\n"
        "            # نفس نداء الجلب الرسمي الذي تستخدمه الآلة الأصلية fill_gap_once\n"
        "            # (+ فترة واحدة: نافذة get_candles هي (end-offset, end] — بلا\n"
        "            # الفترة الإضافية تبقى شمعة المرساة نفسها خارج النافذة أبداً\n"
        "            # فيُهدر جولة كاملة بلا تقدم وتبقى أقدم شرطة كما هي)\n"
        "            fetched = await client.get_candles(api_symbol, anchor_end,\n"
        "                                               win_s + period_s, period_s)\n"
        "        except Exception:\n"
        "            fetched = None")

for path in FILES:
    src = io.open(path, encoding="utf-8").read()
    n = src.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"[FAIL] {path}: anchor found {n} times (expected 1)")
    io.open(path, "w", encoding="utf-8").write(src.replace(ANCHOR, REPL, 1))
    print(f"[ok] deep seal window includes anchor: {path.rsplit('/', 1)[-1]}")
print("DONE")
