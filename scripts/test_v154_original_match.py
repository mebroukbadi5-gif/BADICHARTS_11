# -*- coding: utf-8 -*-
"""التحقق الحرفي — طريقة الجلب وطريقة سد الثغرات في التطبيق هي نفسها في
الكود الأصلي المرجعي qx_server_v10.py حرفياً (طلب المستخدم:
«طريقة جلب الشموع قلنا لا تغيرها ... وايضا طريقة سد الثغرات ايضا»).

المقارنة: تجاهل التعليقات والفراغات فقط — كل سطر كود فعلي يجب أن يطابق.
  1) fetch_candles_with_retry  (الجلب: التاريخي + الجسر + الدمج)
  2) fetch_candles_once        (نداء get_historical_candles المتوازي)
  3) MT4Writer.fill_gap_once   (آلة سد الثغرات الأصلية)
  4) MT4Writer.seed_history    (تبقى في المحرك كما هي — لكن لم تعد مسار الفتح)
"""
import ast, io, re

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
V10 = "/home/z/my-project/download/qx_server_v10.py"

app_src = io.open(APP, encoding="utf-8").read()
app_lines = app_src.split("\n")
_start = _end = None
for i, l in enumerate(app_lines):
    if l.startswith("_QX_ENGINE_SOURCE = r"):
        _start = i + 1
        break
for i in range(_start, len(app_lines)):
    if app_lines[i].strip() == "'''":
        _end = i
        break
ENGINE = "\n".join(app_lines[_start:_end])

def norm(code):
    """أسطر الكود الفعلي فقط: بلا تعليقات، بلا فراغات زائدة، بلا docstrings."""
    tree = ast.parse(code)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            src = ast.get_source_segment(code, node)
            if doc:
                # احذف الـ docstring فقط (أول تعبير نصي بعد التوقيع)
                body = node.body
                if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                    seg_lines = src.split("\n")
                    # احذف أول سطر docstring وفأسطره حتى إغلاق الاقتباس الثلاثي
                    cleaned, skip = [], False
                    for ln in seg_lines[1:]:
                        if skip:
                            if "'''" in ln or '"""' in ln:
                                skip = False
                            continue
                        if ln.strip().startswith('"""') and ln.strip().rstrip().endswith(('"""',),) and ln.count('"""') < 2:
                            skip = True
                            continue
                        if ln.strip().startswith("'''") and ln.strip().rstrip().endswith("'''") is False:
                            skip = True
                            continue
                        cleaned.append(ln)
                    src = "\n".join([seg_lines[0]] + cleaned)
            out.append((node.name, src))
    return dict(out)

def lines_only(code):
    res = []
    for ln in code.split("\n"):
        s = ln.split("#")[0].rstrip()
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            res.append(s)
    return res

def norm_lines(code):
    """أسطر الكود الفعلي بلا docstrings كلياً."""
    tree = ast.parse(code)
    # احذف كل عقد docstring من الشجرة ثم أعد توليد المصدر بالتعليقات؟
    # أبسط: استخدم lines_only ثم استبعد الأسطر داخل docstrings عبر تتبع الاقتباس
    res, in_doc = [], False
    for ln in code.split("\n"):
        t = ln.strip()
        if in_doc:
            if "'''" in t or '"""' in t:
                in_doc = False
            continue
        if t.startswith('"""') or t.startswith("'''"):
            q = t[:3]
            if t.count(q) >= 2 and len(t) > 3:
                continue      # docstring بسطر واحد
            in_doc = True
            continue
        s = ln.split("#")[0].rstrip()
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            res.append(s)
    return res

def get_fn(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(src, node)
    return None

def get_method(src, cls, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return ast.get_source_segment(src, item)
    return None

V10_SRC = io.open(V10, encoding="utf-8").read()

pairs = [
    ("fetch_candles_with_retry", get_fn(V10_SRC, "fetch_candles_with_retry"),
                                  get_fn(ENGINE, "fetch_candles_with_retry")),
    ("fetch_candles_once",       get_fn(V10_SRC, "fetch_candles_once"),
                                  get_fn(ENGINE, "fetch_candles_once")),
    ("MT4Writer.fill_gap_once",  get_method(V10_SRC, "MT4Writer", "fill_gap_once"),
                                  get_method(ENGINE, "MT4Writer", "fill_gap_once")),
    ("mt4_gap_filler",           get_fn(V10_SRC, "mt4_gap_filler"),
                                  get_fn(ENGINE, "mt4_gap_filler")),
]

allok = True
for name, orig, emb in pairs:
    if orig is None or emb is None:
        print(f"[FAIL] {name}: missing (orig={orig is not None}, embedded={emb is not None})")
        allok = False
        continue
    a, b = norm_lines(orig), norm_lines(emb)
    if a == b:
        print(f"[ok] {name}: line-for-line IDENTICAL to original v10 ({len(a)} code lines)")
    else:
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        n_diff = sum(1 for _ in __import__("difflib").unified_diff(a, b, lineterm="")) 
        print(f"[DIFF] {name}: {len(a)} vs {len(b)} code lines ({len(diff)} aligned-line diffs)")
        for x, y in diff[:10]:
            print("   v10:", x[:130])
            print("   app:", y[:130])
        allok = allok and len(diff) == 0

# seed_history لم يعد في مسار الفتح — تأكيد نهائي
ensure_code = get_fn(ENGINE, "ensure_asset_loaded")
seed_calls = [ln for ln in norm_lines(ensure_code) if "seed_history" in ln]
print(f"[{'ok' if not seed_calls else 'FAIL'}] ensure_asset_loaded: no seed_history call "
      f"({'clean' if not seed_calls else seed_calls})")
allok = allok and not seed_calls

print("\nRESULT:", "ALL ORIGINAL-MATCH CHECKS PASSED" if allok else "DIFFS FOUND")
import sys
sys.exit(0 if allok else 1)
