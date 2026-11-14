# -*- coding: utf-8 -*-
"""build_v149_fix2.py — كشف فجوة الذيل بين آخر شمعة مغلقة والشمعة الحية.

حلقة كشف المشاكل في v14_deep_gap_seal كانت تقطع (break) عند أول شمعة حية
قبل أن تقيس الفجوة بين آخر شمعة مغلقة وبداية الفترة الحية — فتبقى الفجوة
الذيلية (مثلاً 20 فترة قبل الشمعة الحية) غير مكتشفة ولا مسددة. الإصلاح:
قياس الفجوة إلى cur_start ثم القطع — الشمعة الحية نفسها تبقى محمية."""
import io

BASE = "/home/z/my-project/download"
FILES = [BASE + "/qx_server_v14.py", BASE + "/BadiChartsStudio_live.py"]

ANCHOR = ("        for c in line:\n"
          "            t = int(c.get(\"time\", 0))\n"
          "            if t >= cur_start:\n"
          "                break\n"
          "            if t > cursor:")

REPL = ("        for c in line:\n"
        "            t = int(c.get(\"time\", 0))\n"
        "            if t >= cur_start:\n"
        "                # v14.9-fix: فجوة الذيل بين آخر شمعة مغلقة والفترة الحية\n"
        "                # تُقاس قبل القطع — الشمعة الحية نفسها تبقى محمية دائماً\n"
        "                if prev_t and (cur_start - prev_t) > period_s and \\\n"
        "                        (oldest_hole == 0 or prev_t < oldest_hole):\n"
        "                    oldest_hole = prev_t\n"
        "                break\n"
        "            if t > cursor:")

for path in FILES:
    src = io.open(path, encoding="utf-8").read()
    n = src.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"[FAIL] {path}: anchor found {n} times (expected 1)")
    io.open(path, "w", encoding="utf-8").write(src.replace(ANCHOR, REPL, 1))
    print(f"[ok] tail-gap detection: {path.rsplit('/', 1)[-1]}")
print("DONE")
