#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تحديث قسم v15.1 في README — استبدال صفّي الجدول 2 و3 بسطر واحد (أُلغيا في v15.2)"""
P = "/home/z/my-project/download/README_BadiCharts_live.md"
lines = open(P, encoding="utf-8").read().splitlines(keepends=True)

# تحديد المواضع بالبحث عن بدايات الصفوف (وليس مطابقة نصية كاملة)
i2 = i3 = None
for i, ln in enumerate(lines):
    if ln.startswith("| 2 | **دائرة تحميل عند تحميل الشموع**"):
        i2 = i
    if ln.startswith("| 3 | **نبضة الدائرة حتى بلا تيك**"):
        i3 = i
assert i2 is not None and i3 is not None, f"rows not found: {i2}, {i3}"
assert i3 == i2 + 1, f"rows not adjacent: {i2}, {i3}"

replacement = ("| 2 | — | *(التحميل المسبق لكل العملات ودائرته الزاويّة من v15.1 "
               "أُلغيا في v15.2 بناء على طلب المستخدم — انظر قسم v15.2 أعلاه)* |\n")
lines[i2:i3 + 1] = [replacement]

txt = "".join(lines)
txt = txt.replace(
    "## ما الجديد في v15.1 (إصلاح قائمة العملات + دائرة تحميل الشموع)",
    "## ما الجديد في v15.1 (إصلاح قائمة العملات — المرصد على المرحلتين)")
txt = txt.replace(
    "طبقة الربط داخله (v15.1)**",
    "طبقة الربط داخله (v15.2)**")

open(P, "w", encoding="utf-8", newline="").write(txt)
print("README v15.1 section updated OK")
