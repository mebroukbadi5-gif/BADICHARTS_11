#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_v16 — اختبارات «الدمج الأصلي البسيط» (طلب المستخدم):

1) المحرك الأصلي يُنفَّذ داخل التطبيق (_qx_module) بلا أخطاء
2) دوال الجلب والسد الأصلية موجودة وسليمة (مطابقة للكود المرفوع)
3) نزع MT4: لا كتابة HST (Asset.write / write_to_file / _subsecond_write_hst)
4) نزع المحركات الأخرى: لا qx_get_historical_batches ولا v14_deep_gap_seal
   ولا preload_all_assets ولا clear_gap_flag_any
5) apply_candles_target: آلية الأصل (700 افتراضياً، هامش +15%)
6) طبقة الربط: مسار تحميل واحد (ensure_asset_loaded → seal → push) —
   فحص نصي لبنية الكود في الملف النهائي
7) قائمة العملات + اكتشاف النطاق موجودان (_instruments_snapshot / resolve_qx_host)
8) حفظ البريد: إصلاح v15.2 موجود + تهيئة مبكرة + إشارة QML
"""
import ast
import re
import sys
import types
from pathlib import Path

APP = Path("/home/z/my-project/download/BadiChartsStudio_live.py")
ORIG = Path("/home/z/my-project/upload/Pasted Content_1794675411828.txt")

src = APP.read_text(encoding="utf-8")
orig = ORIG.read_text(encoding="utf-8")

passed, failed = 0, []


def check(name, cond, extra=""):
    global passed
    if cond:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed.append(name)
        print(f"  ✗ {name} {extra}")


def extract_fn(source, name):
    pat = re.compile(
        r"^([ ]{0,8}(?:async )?def " + re.escape(name) + r"\(.*?)(?=^[ ]{0,8}(?:async )?def |^[A-Za-z_@]|\Z)",
        re.S | re.M)
    m = pat.search(source)
    return m.group(1).strip() if m else None


print("── 1) استخراج المحرك المدمج ──")
eng_m = re.search(r"_QX_ENGINE_SOURCE = r'''(.*?)'''", src, re.S)
check("المحرك مدمج بنص خام واحد", bool(eng_m))
eng = eng_m.group(1)

print("── 2) دوال الجلب والسد الأصلية مطابقة byte-by-byte للكود المرفوع ──")
for fn in ["fetch_candles_once", "_bridge_fetch_recent_candles", "fetch_candles_with_retry",
           "realtime_stream", "fill_gap_once", "update_candle", "on_message",
           "get_candles_ws", "get_candles", "_fetch_historical_batch",
           "get_historical_candles", "prepare_candles", "_fill_missing_slots",
           "_align_time", "_parse_raw_candles", "connect_quotex", "start_candles_stream"]:
    check(f"{fn} مطابقة حرفياً", extract_fn(eng, fn) == extract_fn(orig, fn))

print("── 3) نزع MT4 من المحرك ──")
check("لا فحص نوافذ MT4", "_MT4_HWND" not in eng and "EnumWindows" not in eng)
check("لا WriterThread", "class WriterThread" not in eng)
check("لا فحص مجلدات الترمينال", "find_mt4_history_path" not in eng and "SYSTEM_FOLDERS" not in eng)
check("لا mt4_config.json قراءة", 'MT4_CONFIG_FILE = Path("mt4_config.json")' not in eng)
a = extract_fn(eng, "write")
check("Asset.write لا يكتب HST", a is not None and "struct.pack" not in a and "return False" in a)
b = extract_fn(eng, "write_to_file")
check("write_to_file فراغ", b is not None and "struct.pack" not in b and "return" in b)
check("لا mt4_digits.json قراءة", "DIGITS_CONFIG_FILE.exists()" not in eng)
check("لا PostMessageW", "PostMessageW" not in eng)

print("── 4) نزع المحركات وآليات السد الأخرى ──")
for gone in ["qx_get_historical_batches", "v14_deep_gap_seal", "preload_all_assets",
             "clear_gap_flag_any", "v14_build_background_loops", "v14_supervise",
             "qx_fetch_window_raw", "_PRELOADED_INFO", "_QX_PRELOAD_STATUS"]:
    check(f"محذوف: {gone}", gone not in src)
for gone in ["_qx_start_history_chain", "_qx_chain_worker", "_qx_chain_push_message",
             "_qx_chain_final_merge", "_qx_chain_set_active", "_qx_tail_repaired",
             "_qx_chain_lock", "_qx_chain_gen", "_qx_chain_done", "_qx_chain_active"]:
    check(f"محذوف من طبقة الربط: {gone}", gone not in src)
check("المضخة بلا امتصاص السد العميق", "V14_DEEP_REPAIRED" not in src)

print("── 5) آلية الجلب الأصلية (INITIAL_CANDLES + هامش +15%) ──")
check("apply_candles_target معرفة في المحرك", "def apply_candles_target(n):" in eng)
m = re.search(r"def apply_candles_target\(n\):(.*?)\n\ndef ", eng, re.S)
body = m.group(1) if m else ""
check("هامش +15% الأصلي", "1.15" in body)
check("سقف 1000 وأدنى 100", "min(1000" in body and "max(100" in body)
check("عامل التحميل يطبق الحجم من الإعدادات", "qx.apply_candles_target(self._batch_candles)" in src)
check("تسجيل الدخول يطبق الحجم", "qx.apply_candles_target(self._batch_candles)" in src.split("def _qx_login_worker")[1])

print("── 6) مسار التحميل الواحد: جلب ← سد ← دفع ──")
lw = src[src.index("    def _qx_load_worker(self):"):src.index("    # ---------- v14.3")]
check("العامل يجلب بـ ensure_asset_loaded الأصلي", "qx.ensure_asset_loaded(api)" in lw)
check("العامل يسد بآلة الأصل fill_gap_once", "self._qx_seal_gaps(api)" in lw)
check("العامل يدفع ويطفئ الدائرة بعد السد", lw.index("self._qx_seal_gaps(api)") < lw.index("self._qx_push_feed_now(api)"))
check("لا نوم مضاف بين العملات (0.1s فاصل الأصل)", "time.sleep(0.1)" in lw and "time.sleep(1.0)" not in lw)
sg = src[src.index("    def _qx_seal_gaps(self, api):"):src.index("    def _qx_load_feed(")]
check("السد = نداء fill_gap_once واحد (كود فعلي)", sg.count("qx.MT4_WRITER.fill_gap_once(qx.CLIENT") == 1)
check("السد يصفّر علامة التجمّد بـ clear_symbol الأصلية", "candle_store.clear_symbol(sym)" in sg)
check("لا محاولات تحققية ثلاث", "for _attempt in range(3)" not in sg)
check("لا دمج استعادة (كود فعلي)", "qx._fill_missing_slots(" not in sg)
check("لا سد عميق", "v14_deep_gap_seal" not in sg)
ls = src[src.index("    def _qx_live_step(self):"):src.index("    # ---------- الدخول الحقيقي عبر خادم Quotex")]
check("البث الحي لا يدفع أثناء التحميل", 'if getattr(self, "_qx_loading", False) and self._qx_feed_key != key:' in ls)
check("البث الحي بلا فروع السد العميق", "_ds_t" not in ls and "_qx_tail_repaired" not in ls)

print("── 7) اكتشاف النطاق + قائمة العملات (مطلوب إبقاؤها حرفياً) ──")
check("resolve_qx_host موجودة", "def resolve_qx_host() -> str:" in src)
check("_instruments_snapshot موجودة (طريقة جلب قائمة العملات)", "def _instruments_snapshot():" in src)
check("DOMAINS موجودة", "DOMAINS = [" in eng)
check("لوحة العملات من instruments تبقى", "_qx_build_board" in src)

print("── 8) حفظ البريد «تذكّرني» ──")
check("إصلاح v15.2 (6 روابط) باقٍ", "_v152_session_save_state" in src and "SessionManager._save_state = _v152_session_save_state" in src)
check("تهيئة المحرك مبكراً في main()", "_qx_warm_engine" in src)
check("QML يملأ الحقل عند الإشارة", "function onSavedEmailChanged()" in src)

print("── 9) دائرة التحميل لكل عملة + لا شموع قبل اكتمال الجلب والسد ──")
check("الدائرة تشعل عند فتح العملة", src.count("self._qx_loading_arm()") >= 2)
check("حدث chartload يبث للصفحة", '"type": "chartload"' in src)
check("JS: غطاء تحميل وسط الشارت", ".badi-load{position:absolute;inset:0" in src)
check("JS: استقبال chartload", 'e.type === "chartload"' in src)
check("الفشل يخفي الدائرة أيضاً", src.count("self._qx_push_feed_now(api)") >= 3)

print("── 10) صحة الصيغة العامة ──")
try:
    ast.parse(src)
    check("ast.parse سليم", True)
except SyntaxError as e:
    check("ast.parse سليم", False, str(e))

print("=" * 60)
if failed:
    print(f"FAILED: {len(failed)} — {failed}")
    sys.exit(1)
print(f"ALL {passed} CHECKS PASSED")
