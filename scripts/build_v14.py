#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني qx_server_v14.py = qx_server_v13.py (كما هو حرفياً) + طبقة التقوية
v14 (الجزء A + B + C) تُدرج قبل if __name__ == "__main__" + تعديلات __main__
الإضافية (بانر + تشغيل الحلقات المشرفة) — دون أي تغيير على الكود الأساسي."""
import py_compile
import re
import sys

SRC = "/home/z/my-project/download/qx_server_v13.py"
OUT = "/home/z/my-project/download/qx_server_v14.py"
A = "/home/z/my-project/scripts/v14_part_a.py"
B = "/home/z/my-project/scripts/v14_part_b.py"
C = "/home/z/my-project/scripts/v14_part_c.py"
D = "/home/z/my-project/scripts/v14_part_d.py"


def main() -> int:
    with open(SRC, "r", encoding="utf-8") as f:
        src = f.read()

    parts = []
    for p in (A, B, C, D):
        with open(p, "r", encoding="utf-8") as f:
            parts.append(f.read().rstrip("\n") + "\n")
    layer = "\n\n".join(parts)

    # ── 1) إدراج الطبقة قبل __main__ ──
    marker = 'if __name__ == "__main__":'
    count = src.count(marker)
    assert count == 1, f"__main__ marker count = {count} (expected 1)"
    head, tail = src.split(marker, 1)
    merged = head.rstrip("\n") + "\n\n\n" + layer + "\n\n" + marker + tail

    # ── 2) بانر __main__: v13.2 → v14.0 (نص الطباعة فقط) ──
    old_banner = ('    print(f"{Colors.BOLD}  QX SERVER v13.2 — Chart-Driven '
                  'Loading{Colors.RESET}")')
    new_banner = ('    print(f"{Colors.BOLD}  QX SERVER v14.0 — Chart-Driven '
                  'Loading + Strengthened Server (طبقة تقوية){Colors.RESET}")')
    assert old_banner in merged, "old banner not found"
    merged = merged.replace(old_banner, new_banner, 1)

    # ── 3) تشغيل حلقات v14 المشرفة بعد حلقات v13 الأصلية (إضافة خالصة) ──
    anchor = ("    # v13: ترميم candles.db (أحدث 5000 شمعة لكل عملة) — القرص "
              "لا يمتلئ أبداً:\n"
              "    asyncio.run_coroutine_threadsafe(candlestore_trim_loop(), "
              "ASYNC_LOOP)\n")
    assert anchor in merged, "schedule anchor not found"
    v14_block = (
        anchor
        + "\n"
        + "    # ════════ v14.0: طبقة التقوية — كل الحلقات الجديدة تحت المشرف ════════\n"
        + "    # (دون انهيار الخوادم): تفرز الطلبات + سد الثغرات على كل مفتوح +\n"
        + "    # التكس لا ينام + تقوي النقاط + مشرف الحلقات + النبضة — والكود\n"
        + "    # الأساسي أعلاه كما هو حرفياً.\n"
        + "    try:\n"
        + "        for _v14_name, _v14_factory in v14_build_background_loops():\n"
        + "            asyncio.run_coroutine_threadsafe(\n"
        + "                v14_supervise(_v14_name, _v14_factory), ASYNC_LOOP)\n"
        + "        v14_print_banner()\n"
        + "    except Exception as _v14e:\n"
        + "        logmsg(f\"[v14] layer issue (server continues unchanged): {_v14e}\")\n"
    )
    merged = merged.replace(anchor, v14_block, 1)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(merged)

    # ── 4) فحص الترجمة ──
    py_compile.compile(OUT, doraise=True)

    n_src = src.count("\n") + 1
    n_out = merged.count("\n") + 1
    print(f"OK  {OUT}")
    print(f"    source v13 : {n_src:,} lines")
    print(f"    output v14 : {n_out:,} lines")
    print(f"    layer added: {n_out - n_src:,} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
