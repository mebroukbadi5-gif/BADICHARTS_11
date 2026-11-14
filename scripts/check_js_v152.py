#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""فحص صحة جافاسكربت الصفحة والجسور في النسخة الحية (مسار v15 الحالي)"""
import re
import subprocess
import os

SRC = "/home/z/my-project/download/BadiChartsStudio_live.py"
src = open(SRC, encoding="utf-8").read()

m = re.search(r"STUDIO_HTML = r'''(.*?)'''", src, re.S)
assert m, "STUDIO_HTML not found"
html = m.group(1)

mp = re.search(r'BRIDGE_PRE = r"""(.*?)"""', src, re.S)
mq = re.search(r'BRIDGE_POST = r"""(.*?)"""', src, re.S)
assert mp and mq, "bridges not found"

os.makedirs("/tmp/jscheck", exist_ok=True)
blocks = []

for i, sm in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)):
    body = sm.group(1).strip()
    if body:
        blocks.append(("page_" + str(i), body))

blocks.append(("bridge_pre", mp.group(1)))
blocks.append(("bridge_post", mq.group(1)))


def strip_tags(s):
    # BRIDGE_PRE/BRIDGE_POST تبدأ بـ <script> وقد تليها وسوم HTML (style) بعد
    # </script> — نأخذ JS أول سكربت فقط (سلوك ثابت في v15.0/v15.1 أيضاً)
    s = re.sub(r"^\s*<script[^>]*>", "", s)
    end = s.find("</script>")
    if end >= 0:
        s = s[:end]
    return s.strip()


blocks = [(n, strip_tags(b) if n.startswith("bridge") else b) for n, b in blocks]

fails = 0
for name, body in blocks:
    p = f"/tmp/jscheck/{name}.js"
    open(p, "w", encoding="utf-8").write(body)
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    status = "OK " if r.returncode == 0 else "FAIL"
    if r.returncode != 0:
        fails += 1
        print(f"[{status}] {name} ({len(body)} chars)")
        print(r.stderr[:800])
    else:
        print(f"[{status}] {name} ({len(body)} chars)")

print("FAILS:", fails)
raise SystemExit(1 if fails else 0)
