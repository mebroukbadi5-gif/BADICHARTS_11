#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""فحص مواضع ''' داخل كتلة المحرك القديمة"""
Q = chr(39) * 3
app = open('/home/z/my-project/download/BadiChartsStudio_live.py', encoding='utf-8').read()
MARK = "_QX_ENGINE_SOURCE = r" + Q
start = app.index(MARK) + len(MARK)
pos = start
hits = []
while True:
    i = app.find(Q, pos)
    if i == -1:
        break
    line_no = app.count("\n", 0, i) + 1
    ctx = app[max(0, i - 70):i + 25].replace("\n", " ⏎ ")
    hits.append((i, line_no, ctx))
    pos = i + 3
print("total", Q, "after engine start:", len(hits))
for h in hits[:8]:
    print("line", h[1], ":", h[2][:110])
