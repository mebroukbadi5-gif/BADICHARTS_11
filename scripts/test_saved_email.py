#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار ميزة «تذكّرني» — هل يحفظ المحرك المدمج البريد فعلاً ويقرأه في الإقلاع التالي؟"""
import os, sys, types, tempfile, shutil, traceback

BUILT = "/home/z/my-project/download/BadiChartsStudio_live.py"

def extract_engine_source():
    with open(BUILT, "r", encoding="utf-8") as f:
        txt = f.read()
    marker = "_QX_ENGINE_SOURCE = r'''"
    i = txt.index(marker) + len(marker)
    j = txt.index("'''", i)
    return txt[i:j]

def exec_engine(source, workdir):
    """نفس ما تفعله _qx_module() حرفياً — لكن داخل مجلد عمل معزول."""
    old_cwd = os.getcwd()
    os.chdir(workdir)
    try:
        mod = types.ModuleType("qx_embedded_engine")
        mod.__file__ = os.path.abspath(BUILT)
        mod.__name__ = "qx_embedded_engine"
        exec(compile(source, "qx_embedded_engine", "exec"), mod.__dict__)
        sys.modules["qx_embedded_engine"] = mod
        return mod
    finally:
        os.chdir(old_cwd)

def main():
    src = extract_engine_source()
    print("[1] engine source extracted:", len(src), "chars")
    d1 = tempfile.mkdtemp(prefix="qx_email_run1_")
    d2 = tempfile.mkdtemp(prefix="qx_email_run2_")
    try:
        # ── التشغيل الأول: دخول ناجح → record_success ──
        m1 = exec_engine(src, d1)
        sm = m1.session_manager
        print("[2] run1 DB_PATH:", m1.DB_PATH, "exists:", m1.DB_PATH.exists())
        sm.record_success("tester@example.com", password="pw123", host="quotex.com")
        got = sm.get_saved_email()
        print("[3] run1 get_saved_email() ->", repr(got))
        assert got == "tester@example.com", "run1: email not returned in-memory"
        assert m1.DB_PATH.exists(), "run1: DB file not created"
        print("[4] run1 saved OK — db at", m1.DB_PATH)

        # ── التشغيل الثاني (محاكاة إقلاع التطبيق مرة أخرى): القراءة فقط ──
        m2 = exec_engine(src, d2)
        sm2 = m2.session_manager
        print("[5] run2 (different cwd) DB_PATH:", m2.DB_PATH)
        got2 = sm2.get_saved_email()
        print("[6] run2 get_saved_email() ->", repr(got2))
        if got2 == "tester@example.com":
            print("[PASS] email persists across runs when cwd is the same")
        else:
            print("[FAIL] run2 read empty — DB written elsewhere or not committed")

        # ── التشغيل الثالث: نفس مجلد run1 بالضبط (نفس مجلد الملف) ──
        m3 = exec_engine(src, d1)
        got3 = m3.session_manager.get_saved_email()
        print("[7] run3 same-folder get_saved_email() ->", repr(got3))
        print("[PASS]" if got3 == "tester@example.com" else "[FAIL]", "same-cwd persistence")
    except Exception:
        traceback.print_exc()
        print("[ERROR] test crashed")
    finally:
        shutil.rmtree(d1, ignore_errors=True)
        shutil.rmtree(d2, ignore_errors=True)

if __name__ == "__main__":
    main()
