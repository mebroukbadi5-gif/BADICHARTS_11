# -*- coding: utf-8 -*-
"""التحقق من صحة جافاسكربت الصفحة والجسور في النسخة الحية"""
import re
import subprocess
import os

src = open("/home/z/my-project/gh_repo/BadiChartsStudio_live.py", encoding="utf-8").read()

# استخراج STUDIO_HTML
m = re.search(r"STUDIO_HTML = r'''(.*?)'''", src, re.S)
assert m, "STUDIO_HTML not found"
html = m.group(1)

# استخراج BRIDGE_PRE و BRIDGE_POST
mp = re.search(r'BRIDGE_PRE = r"""(.*?)"""', src, re.S)
mq = re.search(r'BRIDGE_POST = r"""(.*?)"""', src, re.S)
assert mp and mq, "bridges not found"

os.makedirs("/tmp/jscheck", exist_ok=True)
blocks = []

# سكربتات الصفحة المضمنة (بدون src)
for i, sm in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)):
    body = sm.group(1).strip()
    if body:
        blocks.append(("page_" + str(i), body))

blocks.append(("bridge_pre", mp.group(1)))
blocks.append(("bridge_post", mq.group(1)))

def strip_tags(s):
    s = re.sub(r"^\s*<script[^>]*>", "", s)
    s = re.sub(r"</script>\s*$", "", s)
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
