#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تشخيص: لماذا لا يبقى البريد في app_data.db بعد record_success؟"""
import os, sys, types, sqlite3, tempfile, shutil, traceback

BUILT = "/home/z/my-project/download/BadiChartsStudio_live.py"

def extract_engine_source():
    with open(BUILT, "r", encoding="utf-8") as f:
        txt = f.read()
    marker = "_QX_ENGINE_SOURCE = r'''"
    i = txt.index(marker) + len(marker)
    j = txt.index("'''", i)
    return txt[i:j]

src = extract_engine_source()
d1 = tempfile.mkdtemp(prefix="qx_dbg_")
old = os.getcwd(); os.chdir(d1)
try:
    mod = types.ModuleType("qx_embedded_engine")
    mod.__file__ = os.path.abspath(BUILT)
    mod.__name__ = "qx_embedded_engine"
    exec(compile(src, "qx_embedded_engine", "exec"), mod.__dict__)
finally:
    os.chdir(old)

print("DB_PATH =", mod.DB_PATH, "exists:", mod.DB_PATH.exists())

# 1) هل الجداول موجودة؟
conn = sqlite3.connect(str(mod.DB_PATH))
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("tables:", tables)
try:
    rows = conn.execute("SELECT * FROM app_state").fetchall()
    print("app_state rows BEFORE record_success:", rows)
except Exception as e:
    print("app_state SELECT err:", e)
conn.close()

# 2) استدعاء record_success مباشرة وطباعة أي استثناء داخلي
sm = mod.session_manager
print("state before:", sm.state)
sm.record_success("dbg@example.com", password="pw", host="quotex.com")
print("state after:", sm.state)

# 3) مندوب _save_state اليدوي بمحاكاة نفس الكود لكن بلا swallowing
conn = sqlite3.connect(str(mod.DB_PATH), timeout=15)
try:
    conn.execute("""
        INSERT OR REPLACE INTO app_state
        (id, email, password, host, last_login, last_success, failed_auth_count)
        VALUES (1, ?, ?, ?, ?, ?, ?)
    """, (1, "manual@example.com", "pw", "quotex.com", 1.0, 1, 0))
    conn.commit()
    print("manual INSERT OK")
except Exception as e:
    print("manual INSERT FAILED:", type(e).__name__, e)
rows = conn.execute("SELECT id,email FROM app_state").fetchall()
print("app_state rows AFTER:", rows)
conn.close()

# 4) get_saved_email بعد القراءة اليدوية
print("get_saved_email now:", repr(sm.get_saved_email()))
shutil.rmtree(d1, ignore_errors=True)
