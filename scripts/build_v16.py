#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v16.py — «الدمج الأصلي البسيط» (طلب المستخدم الحرفي):

  «عليك ان تدمج هذا الكود بالتطبيق انزع اي جزء محرك شموع اخر او الية سد
   ثغرات اخرى فقط ابقي اكتشاف اي نطاق يعمل به وابقي طريقة جلب قائمة العملات
   وادمج هذا به ونزع جزء mt4 وفقط دون تعقيد»

المحرك الأصلي المدمج يبقى حرفياً (تم التحقق أن دوال الجلب والسد كلها مطابقة
byte-by-byte للكود المرفوع). هذه النسخة تنزع فقط:
  - جزء MT4 (نافذة/HST/WriterThread/mt4_config/mt4_digits)
  - المحركات الأخرى وآليات السد الأخرى المضافة في طبقة الربط
كل تعديل مشروط بمرساة فريدة — مرساة مفقودة أو مكررة تُفشل البناء فوراً.
"""
import re
import sys
from pathlib import Path

SRC = Path("/home/z/my-project/download/BadiChartsStudio_live.py")
BAK = Path("/home/z/my-project/scripts/BadiChartsStudio_live.v15.4.bak.py")

text = SRC.read_text(encoding="utf-8")
edits_done = []


def fail(msg):
    print("BUILD FAILED:", msg)
    sys.exit(1)


def replace_span(name, start_marker, end_marker, new_text, occurrence=1):
    """يستبدل [start_marker .. end_marker) — مرساة النهاية تبقى كما هي."""
    global text
    starts = [m.start() for m in re.finditer(re.escape(start_marker), text)]
    if len(starts) < occurrence:
        fail(f"[{name}] start marker not found ({len(starts)} < {occurrence}):\n{start_marker[:120]}")
    s = starts[occurrence - 1]
    e = text.find(end_marker, s + len(start_marker))
    if e < 0:
        fail(f"[{name}] end marker not found after start:\n{end_marker[:120]}")
    removed = e - s
    text = text[:s] + new_text + text[e:]
    edits_done.append(f"{name}: span {removed} -> {len(new_text)} chars")


def replace_once(name, old, new, occurrence=1):
    global text
    idxs = [m.start() for m in re.finditer(re.escape(old), text)]
    if len(idxs) < occurrence:
        fail(f"[{name}] exact text not found ({len(idxs)} < {occurrence}):\n{old[:120]}")
    s = idxs[occurrence - 1]
    text = text[:s] + new + text[s + len(old):]
    edits_done.append(f"{name}: exact replace")


def insert_after(name, anchor, new_text, occurrence=1):
    global text
    idxs = [m.start() for m in re.finditer(re.escape(anchor), text)]
    if len(idxs) < occurrence:
        fail(f"[{name}] anchor not found ({len(idxs)} < {occurrence}):\n{anchor[:120]}")
    s = idxs[occurrence - 1] + len(anchor)
    text = text[:s] + new_text + text[s:]
    edits_done.append(f"{name}: inserted after anchor")


def must_absent(name, snippet):
    if snippet in text:
        fail(f"[{name}] snippet must be absent after build:\n{snippet[:120]}")
    edits_done.append(f"{name}: absent OK")


def must_present(name, snippet):
    if snippet not in text:
        fail(f"[{name}] snippet must be present after build:\n{snippet[:120]}")
    edits_done.append(f"{name}: present OK")


# ═══════════════════════════════════════════════════════════════════════
# 1) نزع MT4 — نافذة MT4 (EnumWindows/PostMessage/WM_COMMAND) ← دوال فارغة
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "mt4-window",
    "_MT4_HWND = None\n_MT4_HWND_LAST_SEARCH = 0",
    "class Colors:",
    """# MT4 part removed (user request «نزع جزء mt4»): the app never talks to an
# MT4 terminal — no window enumeration, no WM_COMMAND chart refresh.
def find_mt4_window():
    return None

REFRESH_INTERVAL = 1.0

def refresh_mt4():
    return False

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 1b) نزع MT4 — كتلة ctypes/normals win32 للنافذة ← علامة واحدة فقط
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "mt4-ctypes-block",
    'WINAPI_AVAILABLE = False\nif platform.system() == "Windows":',
    "# MT4 part removed (user request «نزع جزء mt4»): the app never talks to an",
    """WINAPI_AVAILABLE = False   # MT4 part removed (user request «نزع جزء mt4»)

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 2) نزع MT4 — mt4_config.json + mt4_digits.json ← لا قراءة ملفات
#    (الحساب الذاتي للأرقام في _resolve_digits يبقى كما هو حرفياً)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "mt4-digits-file",
    'MT4_CONFIG_FILE = Path("mt4_config.json")',
    "def _resolve_digits(symbol: str, price: float = 0.0) -> int:",
    """# MT4 part removed (user request «نزع جزء mt4»): no mt4_config.json and no
# mt4_digits.json files. The pure auto-calculation in _resolve_digits below
# is kept exactly as-is (it never read any file itself).
DIGITS_CONFIG_FILE = Path("mt4_digits.json")   # legacy name only — never read
_digits_config_cache = None
_digits_config_loaded = False

def load_digits_config() -> dict:
    # MT4 part removed (user request): no external digits file.
    return {}

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 3) نزع MT4 — فحص مجلدات الترمينال ← مجلد محلي بسيط (لا كتابة HST أصلاً)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "mt4-history-scan",
    'SYSTEM_FOLDERS = {"default", "downloads", "mailbox", "signals", "symbolsets", "deleted", "templates", "profiles", "mql4", "logs", "config", "history_backup"}',
    "# Credentials, session state and login state now live in app_data.db",
    """# MT4 part removed (user request «نزع جزء mt4»): no MT4 terminal scanning,
# no mt4_config.json, no Desktop fallback. A local folder keeps legacy path
# references valid without ever writing HST files.
MT4_HISTORY_PATH = os.path.join(str(Path.cwd()), "hst_out")
os.makedirs(MT4_HISTORY_PATH, exist_ok=True)

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 4) نزع MT4 — Asset.write (كتابة HST) + WriterThread ← لا كتابة ملفات
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "asset-write-writerthread",
    "    def write(self, force=False):",
    "async def connect_quotex(email, password, force_fresh=False, max_attempts=3):",
    """    def write(self, force=False):
        # MT4 part removed (user request «نزع جزء mt4»): no HST file writing.
        # Candle state keeps flowing in memory exactly like the original server
        # (fetch_candles_with_retry / fill_gap_once / realtime_stream untouched).
        return False

# WriterThread (the MT4 HST writer thread) removed (user request) — it belonged
# to the MT4 part. Nothing writes HST files anymore.
writer_thread = None

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 5) نزع MT4 — MT4Writer.write_to_file ← فراغ (آلة السد تبقى حرفياً)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "mt4writer-write-to-file",
    "    def write_to_file(self, asset: str, period: int, candles: list):",
    "    async def seed_history(self, client, asset_obj, period: int, days: float = 0.75):",
    """    def write_to_file(self, asset: str, period: int, candles: list):
        # MT4 part removed (user request «نزع جزء mt4»): no HST writing.
        # fill_gap_once still runs exactly the same — only the MT4 file output
        # is gone; the candle merge logic and its call sites are untouched.
        return

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 6) نزع MT4 — _subsecond_write_hst ← فراغ (مسار الثواني لا يعمل أصلاً)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "subsecond-hst",
    "def _subsecond_write_hst(asset_symbol: str, candles: list):",
    "async def fetch_subsecond_history(asset: Asset, idx=1, total=1):",
    """def _subsecond_write_hst(asset_symbol: str, candles: list):
    # MT4 part removed (user request «نزع جزء mt4»): no HST writing.
    return

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 7) نزع المحرك الآخر — qx_fetch_window_raw (بوابة مضافة) ← نداء أصلي مباشر
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-qx-fetch-window-raw",
    "async def qx_fetch_window_raw(api, end_ts, seconds, tf_sec, foreground=False, timeout=45.0):",
    "async def fetch_older_batch(api, before_ts, batch=300):",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 8) نزع المحرك الآخر — qx_get_historical_batches (نسخة معدلة من الجلب الأصلي)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-qx-get-historical-batches",
    "async def qx_get_historical_batches(asset, amount_of_seconds, period, timeout=30,",
    'async def v14_deep_gap_seal(api, reason=""):',
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 9) نزع آلية السد الأخرى — v14_deep_gap_seal
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-v14-deep-gap-seal",
    'async def v14_deep_gap_seal(api, reason=""):',
    "async def tick_cache_collector():",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 10) نزع آلية السد الأخرى — clear_gap_flag_any (تُستبدل بـ clear_symbol الأصلية)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-clear-gap-flag-any",
    "def clear_gap_flag_any(variants):",
    "def reset_gap_flags():",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 11) نزع التحميل المسبق — حالته + preload_all_assets (التحميل عند الفتح فقط)
#     النطاق يشمل: _PRELOADED_INFO + V14_DEEP_REPAIRED + _QX_WINDOW_BUSY +
#     تعليق v15.1 + _QX_PRELOAD_STATUS
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-preload-state",
    "_PRELOADED_INFO = {}\n",
    "def apply_history_days(days_val):",
    "",
)
replace_span(
    "drop-preload-all",
    "async def preload_all_assets():",
    "def v14_print_banner():",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 12) نزع طبقة v14 المضافة (banner + loops + supervise) — مع إبقاء إصلاح
#     حفظ البريد v15.2 (الدالة نفسها) كما هو
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-v14-helpers",
    "def v14_print_banner():",
    "def _v152_session_save_state(self):",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 13) آلية الجلب الأصلية — apply_candles_target (نفس آلية STAGE 3 الأصلية:
#     INITIAL_CANDLES + هامش +15% على FETCH_DURATION_SECONDS)
# ═══════════════════════════════════════════════════════════════════════
insert_after(
    "add-apply-candles-target",
    "    QX_HISTORY_DAYS = d\n    return QX_HISTORY_DAYS\n",
    """

def apply_candles_target(n):
    \"\"\"حجم الجلب عند فتح العملة — نفس آلية الأصل (STAGE 3) حرفياً:
    INITIAL_CANDLES = العدد المطلوب (700 افتراضياً، حتى 1000 من بطاقة الإعدادات)
    وFETCH_DURATION_SECONDS بمعامل الهامش +15% الأصلي. الجلب الأصلي
    fetch_candles_with_retry يقرأ هذين المتغيرين لحظة التنفيذ كما هو.\"\"\"
    global INITIAL_CANDLES, FETCH_DURATION_SECONDS
    try:
        n = max(100, min(1000, int(n)))
    except Exception:
        n = 700
    INITIAL_CANDLES = n
    FETCH_DURATION_SECONDS = int(n * max(1, int(PERIOD_SECONDS)) * 1.15)
    return INITIAL_CANDLES
""",
)

# ═══════════════════════════════════════════════════════════════════════
# 14) Backend — عامل التحميل: مسار واحد أصلي (جلب ← سد ← دفع) بلا نوم مضاف
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "rewrite-load-worker",
    "    def _qx_load_worker(self):",
    "    # ---------- v14.3: دفعات التاريخ عند فتح العملة (دفعة مباشرة) ----------",
    """    def _qx_load_worker(self):
        \"\"\"عامل التحميل — المسار الأصلي الواحد حرفياً (v16 «محرك واحد بلا طبقات»،
        طلب المستخدم: «انزع اي جزء محرك شموع اخر او الية سد ثغرات اخرى فقط
        دون تعقيد» و«يجلب يسد الثغرات ولا ينام الكود»):

        لكل عملة يُفتح شارتها، واحدة تلو الأخرى:
          1) realtime_stream الأصلية (البث يجمع التيك أثناء الجلب — كما في الأصل)
          2) fetch_candles_with_retry الأصلية (get_historical_candles المتوازية
             5 عمال × دفعة 200 + جسر آخر 15 شمعة + دمج التيك الحي) — نفس
             نداءات الخادم الأصلي حرفياً، 700/1000 شمعة في ثوانٍ
          3) سد الثغرات الأصلي fill_gap_once — نداء واحد كما في الخادم الأصلي
             (تصفير علامة التجمّد بنفس طريقة refetch_all_candles الأصلية:
             candle_store.clear_symbol)
          4) بعد اكتمال الجلب **والسد** فقط تُدفع الشموع إلى الشارت وتُطفأ
             دائرة التحميل (طلب المستخدم حرفياً — لا شموع قبل اكتمال الاثنين).

        لا نوم مضاف ولا خنق ولا طبقات سد أخرى — المحرك الأصلي كما هو.\"\"\"
        qx = _qx_module()
        while True:
            api = None
            with self._qx_load_lock:
                if self._qx_loadq:
                    api = self._qx_loadq.pop(0)
                else:
                    self._qx_load_busy = False
                    return
            if not qx:
                continue
            # حجم الجلب من بطاقة الإعدادات (700 افتراضياً حتى 1000) —
            # نفس آلية الأصل INITIAL_CANDLES + هامش +15% (STAGE 3)
            try:
                qx.apply_candles_target(self._batch_candles)
            except Exception:
                pass
            try:
                fut = asyncio.run_coroutine_threadsafe(
                    qx.ensure_asset_loaded(api), qx.ASYNC_LOOP)
                n = fut.result(timeout=180)
                if n:
                    self._log("ok", f"{api}: {n} candles (original fetch) + live stream ON")
                    self._qx_ensure_fail[api] = 0
                    self._qx_last_sig = None   # المضخة تدفع الغذاء الجديد فوراً
                    # سد الثغرات — آلة الأصل نفسها fill_gap_once قبل أي دفع للشارت
                    try:
                        if (api, "1m") not in getattr(self, "_qx_sealed", set()):
                            self._qx_sealed.add((api, "1m"))
                            self._qx_seal_gaps(api)
                    except Exception:
                        pass
                    self._qx_push_feed_now(api)
                else:
                    self._qx_ensure_fail[api] = self._qx_ensure_fail.get(api, 0) + 1
                    self._log("info", f"{api}: no candles from fetch — retry on next open")
                    self._qx_push_feed_now(api)   # إخفاء الدائرة — لا شموع تُعرض
            except Exception as e:
                self._qx_ensure_fail[api] = self._qx_ensure_fail.get(api, 0) + 1
                self._log("err", f"ensure {api}: {str(e)[:100]}")
                self._qx_push_feed_now(api)       # إخفاء الدائرة عند الفشل أيضاً
            finally:
                with self._qx_load_lock:
                    self._qx_load_pending.discard(api)
            # فاصل الأصل بين عملة وأخرى (FETCH_ASSET_DELAY = 0.1s) — لا نوم مضاف
            time.sleep(0.1)

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 15) Backend — حذف سلسلة التاريخ المضافة (start_history_chain + set_active +
#     chain_push_message) — المحرك الآخر
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-history-chain-head",
    '    def _qx_start_history_chain(self, api, tf_label="1m"):',
    "    def _qx_seal_gaps(self, api):",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 16) Backend — سد الثغرات: آلة الأصل نفسها، نداء واحد، بلا طبقات
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "rewrite-seal-gaps",
    "    def _qx_seal_gaps(self, api):",
    "    def _qx_chain_worker(self, api, tf_label, gen):",
    """    def _qx_seal_gaps(self, api):
        \"\"\"سد ثغرات العملة — آلة الأصل حرفياً (MT4_WRITER.fill_gap_once كما هي،
        نفس نداء mt4_gap_filler الأصلي) — نداء واحد بلا أي طبقات إضافية:

        - تصفير علامة التجمّد بنفس طريقة refetch_all_candles الأصلية
          (candle_store.clear_symbol للرمز) حتى يعمل السد عند كل فتح
        - نداء fill_gap_once واحد: يجلب آخر 10 شموع حقيقية (GAP_FILL_CANDLES)،
          يستبدل المغلقة الناقصة، يضيف المفقود، ويملأ الأمداد بـ
          _fill_missing_slots الأصلية (سقف يوم كامل) — كل ذلك داخل الآلة
          الأصلية نفسها دون أي تغيير.

        (v16 طلب المستخدم: «انزع اي جزء محرك شموع اخر او الية سد ثغرات اخرى
        فقط دون تعقيد» — السد العميق v14 ومحاولات التحقق الثلاث ودمج
        الاستعادة كلها أُزيلت؛ هذه هي آلية السد الأصلية الوحيدة).\"\"\"
        qx = _qx_module()
        if not qx or getattr(qx, "CLIENT", None) is None:
            return
        try:
            asset = qx._get_or_create_asset(api)
        except Exception:
            return
        if asset is None:
            return
        sym = str(getattr(asset, "symbol", "") or api)
        # تصفير علامة التجمّد — نفس ما تفعله refetch_all_candles الأصلية
        try:
            qx.MT4_WRITER._gap_filled[sym] = False
        except Exception:
            pass
        try:
            qx.MT4_WRITER._gap_filled_at.pop(sym, None)
        except Exception:
            pass
        try:
            qx.MT4_WRITER.candle_store.clear_symbol(sym)
        except Exception:
            pass
        # نداء الآلة الأصلية الواحد (نفس نداء mt4_gap_filler الأصلي)
        try:
            fut = asyncio.run_coroutine_threadsafe(
                qx.MT4_WRITER.fill_gap_once(qx.CLIENT, asset,
                                            int(getattr(qx, "PERIOD", 1))),
                qx.ASYNC_LOOP)
            fut.result(timeout=30)
        except Exception as e:
            self._log("info", f"seal {api}: {str(e)[:80]}")

""",
)

# ═══════════════════════════════════════════════════════════════════════
# 17) Backend — حذف chain worker + final merge + tail repaired (الطبقات الأخرى)
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-chain-worker",
    "    def _qx_chain_worker(self, api, tf_label, gen):",
    "    def _qx_load_feed(self, force=False):",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 18) Backend — _qx_live_step: نزع امتصاص السد العميق وtail_repaired
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "simplify-live-step",
    '                # v14.9 (لقطة «مهذه المشاكل»): السد العميق استبدل شرطات قديمة',
    "                else:\n                    self._qx_merge_tail_full(candles, tf_sec)",
    """                if not self._candles or self._qx_feed_key != key:
                    self._candles = candles[-self._QX_FEED_CAP:]
                    self._qx_feed_key = key
""",
)

# ═══════════════════════════════════════════════════════════════════════
# 19) Backend — histChainActive ← False (السلسلة أُزيلت — محرك واحد أصلي)
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "hist-chain-active-false",
    """        (لا syncFull) — الزوم والموضع يبقيان حرين والشموع لا تُفقد.\"\"\"
        return bool(self._qx_chain_active)""",
    """        (لا syncFull) — الزوم والموضع يبقيان حرين والشموع لا تُفقد.\"\"\"
        return False   # v16: سلسلة دفعات التاريخ أُزيلت — محرك جلب واحد أصلي فقط""",
)

# ═══════════════════════════════════════════════════════════════════════
# 20) Backend — إزالة تصريحات حالة السلسلة من __init__
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-chain-init-state",
    "        # v14.5 (طلب المستخدم): طلب واحد بمدى الأيام كاملاً — الخادم يجيبه على",
    "        self._files = self._load_files()",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 21) Backend — _qx_force_reload_current: إزالة لمس حالة السلسلة المحذوفة
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-force-reload-chain-discard",
    "            try:\n                with self._qx_chain_lock:\n                    self._qx_chain_done.discard((api, self._tf))",
    "            try:\n                self._qx_ensure_fail[api] = 0   # تغيير إعدادات = محاولة جديدة فوراً",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 22) Backend — تسجيل الدخول: نزع كتلة حلقات v14 المضافة
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-login-v14-block",
    '            if hasattr(qx, "v14_build_background_loops"):',
    "            self._qx_logged = True",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 23) Backend — تسجيل الدخول: تطبيق حجم الجلب من بطاقة الإعدادات (آلية الأصل)
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "login-apply-candles-target",
    """            try:
                qx.PRELOAD_CANDLES = int(self._batch_candles)
                qx.PAGINATION_BATCH = int(self._batch_candles)
            except Exception:
                pass""",
    """            try:
                qx.PRELOAD_CANDLES = int(self._batch_candles)
                qx.PAGINATION_BATCH = int(self._batch_candles)
            except Exception:
                pass
            try:
                # حجم الجلب الأصلي عند فتح العملة (700 افتراضياً حتى 1000) —
                # نفس آلية الأصل INITIAL_CANDLES + هامش +15% (STAGE 3)
                qx.apply_candles_target(self._batch_candles)
            except Exception:
                pass""",
)

# ═══════════════════════════════════════════════════════════════════════
# 24) Backend — المضخة: نزع كتلة سجل التحميل المسبق المحذوف
# ═══════════════════════════════════════════════════════════════════════
replace_span(
    "drop-pump-preload-log",
    "        # 3) حالة التحميل المسبق → سجل التطبيق (مخنوقة كل 3 ثوانٍ)",
    "        # 4) v15.4 (طلب المستخدم): دائرة تحميل الشموع لكل عملة",
    "",
)

# ═══════════════════════════════════════════════════════════════════════
# 25) Backend — setBatchCandles: تطبيق الحجم الجديد بآلية الأصل نفسها
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "setbatch-apply-target",
    """            try:
                qx.PAGINATION_BATCH = n     # حجم كل دفعة تُرفع إلى الشارت
            except Exception:
                pass""",
    """            try:
                qx.PAGINATION_BATCH = n     # حجم كل دفعة تُرفع إلى الشارت
            except Exception:
                pass
            try:
                qx.apply_candles_target(n)   # حجم الجلب الأصلي (STAGE 3: +15% هامش)
            except Exception:
                pass""",
)

# ═══════════════════════════════════════════════════════════════════════
# 26) Backend — جلب فريم أعلى: نداء CLIENT.get_candles الأصلي مباشرة
#     (بدل بوابة qx_fetch_window_raw المحذوفة)
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "tf-fetch-direct-get-candles",
    """                fut = asyncio.run_coroutine_threadsafe(
                    qx.qx_fetch_window_raw(api, end, count * tf_sec, tf_sec,
                                           foreground=True, timeout=45.0), qx.ASYNC_LOOP)""",
    """                fut = asyncio.run_coroutine_threadsafe(
                    qx.CLIENT.get_candles(api, int(end), int(count * tf_sec), int(tf_sec)),
                    qx.ASYNC_LOOP)""",
)

# ═══════════════════════════════════════════════════════════════════════
# 27) Backend — دفعة التمرير للخلف: نداء CLIENT.get_candles الأصلي مباشرة
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "older-fetch-direct-get-candles",
    """                    fut = asyncio.run_coroutine_threadsafe(
                        qx.qx_fetch_window_raw(api, before, _nb * tf_sec, tf_sec,
                                               foreground=True, timeout=45.0), qx.ASYNC_LOOP)""",
    """                    fut = asyncio.run_coroutine_threadsafe(
                        qx.CLIENT.get_candles(api, int(before), int(_nb * tf_sec), int(tf_sec)),
                        qx.ASYNC_LOOP)""",
)

print("PART 1+2 EDITS DONE — applying QML/main edits next")

# ═══════════════════════════════════════════════════════════════════════
# 28) QML — تعبئة البريد المحفوظ فور جاهزية المحرك (إشارة savedEmailChanged)
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "qml-savedemail-connections",
    """            onVisibleChanged: {
                if (visible) {
                    t = 0
                    enterAnim.restart()
                    try { userF.text = backend.savedEmail } catch (e) {}
                }
            }""",
    """            onVisibleChanged: {
                if (visible) {
                    t = 0
                    enterAnim.restart()
                    try { userF.text = backend.savedEmail } catch (e) {}
                }
            }
            /* v16 (طلب المستخدم «ميزة حفض الايميل»): محرك الخادم يهيأ في خيط
               خلفي عند الإقلاع — عند جاهزيته تُدفَق إشارة البريد المحفوظ فيُملأ
               الحقل فوراً حتى لو جاء المحرك بعد رسم شاشة الدخول */
            Connections {
                target: backend
                function onSavedEmailChanged() {
                    try { if (!userF.text) userF.text = backend.savedEmail } catch (e) {}
                }
            }""",
)

# ═══════════════════════════════════════════════════════════════════════
# 29) main() — تهيئة المحرك مبكراً في خيط خلفي + إشعار الواجهة بالبريد المحفوظ
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "main-warm-engine",
    """    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)""",
    """    backend = Backend()
    # v16 (طلب المستخدم «ميزة حفض الايميل لماذا لا تعمل»): محرك الخادم يُهيَّأ
    # مبكراً في خيط خلفي (exec الوحدة ثقيل)، وعند جاهزيته تُدفَق إشارة
    # savedEmailChanged فيمتلئ حقل البريد المحفوظ في شاشة تسجيل الدخول فوراً.
    import threading as _qx_warm_th

    def _qx_warm_engine():
        try:
            if _qx_module() is not None:
                try:
                    backend.savedEmailChanged.emit()
                except Exception:
                    pass
        except Exception:
            pass

    _qx_warm_th.Thread(target=_qx_warm_engine, daemon=True, name="qxWarm").start()
    engine.rootContext().setContextProperty("backend", backend)""",
)

# ═══════════════════════════════════════════════════════════════════════
# 29b) تحديث تعليق طبقة الربط (ذكر WriterThread المحذوفة)
# ═══════════════════════════════════════════════════════════════════════
replace_once(
    "glue-comment-writerthread",
    "#   CLIENT._fetch_historical_batch / WriterThread / mt4_gap_filler ...",
    "#   CLIENT._fetch_historical_batch / mt4_gap_filler ...",
)

# ═══════════════════════════════════════════════════════════════════════
# 30) التحققات النهائية — كل الرموز المنزوعة يجب أن تكون غائبة تماماً
# ═══════════════════════════════════════════════════════════════════════
for sym in [
    "qx_get_historical_batches",
    "v14_deep_gap_seal",
    "clear_gap_flag_any",
    "preload_all_assets",
    "_PRELOADED_INFO",
    "_QX_PRELOAD_STATUS",
    "v14_print_banner",
    "v14_build_background_loops",
    "v14_supervise",
    "qx_fetch_window_raw",
    "_qx_start_history_chain",
    "_qx_chain_worker",
    "_qx_chain_push_message",
    "_qx_chain_final_merge",
    "_qx_chain_set_active",
    "_qx_tail_repaired",
    "V14_DEEP_REPAIRED",
    "_qx_chain_lock",
    "_qx_chain_gen",
    "_qx_chain_done",
    "_qx_chain_active",
    "_qx_chain_running",
    "find_mt4_history_path",
    "_save_mt4_path",
    "_validate_mt4_path",
    "class WriterThread",
    "writer_thread = WriterThread",
    "_MT4_HWND",
    "MT4_REFRESH_CHART",
]:
    must_absent(f"absent:{sym}", sym)

for sym in [
    "def _qx_seal_gaps(self, api):",
    "def _qx_load_worker(self):",
    "def apply_candles_target(n):",
    "MT4_WRITER.fill_gap_once(qx.CLIENT, asset,",
    "candle_store.clear_symbol(sym)",
    "qx.ensure_asset_loaded(api)",
    "_qx_push_feed_now(api)",
    "def find_mt4_window():",
    "def refresh_mt4():",
    "def write_to_file(self, asset: str, period: int, candles: list):",
    "def _v152_session_save_state(self):",
    "SessionManager._save_state = _v152_session_save_state",
    "function onSavedEmailChanged()",
    "_qx_warm_engine",
    "def ensure_asset_loaded(api):",
    "async def fetch_candles_with_retry(asset: Asset, max_retries=3, idx=1, total=1):",
    "async def _bridge_fetch_recent_candles(asset: Asset, existing_candles: list) -> list:",
    "async def fill_gap_once(self, client, asset_obj, period: int):",
    "async def get_historical_candles(self, asset, amount_of_seconds, period, timeout=30, max_workers=5, progress_callback=None):",
    "def _instruments_snapshot():",
    "def resolve_qx_host() -> str:",
    "async def mt4_gap_filler():",
    "async def realtime_stream(asset: Asset):",
    "async def tick_cache_collector():",
    "def reset_gap_flags():",
]:
    must_present(f"present:{sym}", sym)

# فحص بناء الصيغة
import py_compile, tempfile
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
    tf.write(text)
    tmpname = tf.name
try:
    py_compile.compile(tmpname, doraise=True)
    edits_done.append("py_compile: OK")
finally:
    import os as _os
    _os.unlink(tmpname)

# فحص roundtrip: دوال الجلب والسد الأصلية تبقى مطابقة byte-by-byte للكود المرفوع
eng_m = re.search(r"_QX_ENGINE_SOURCE = r'''(.*?)'''", text, re.S)
if not eng_m:
    fail("embedded engine source not found")
eng = eng_m.group(1)
orig = Path("/home/z/my-project/upload/Pasted Content_1794675411828.txt").read_text(encoding="utf-8")


def extract_fn(src, name):
    pat = re.compile(r"^([ ]{0,8}(?:async )?def " + re.escape(name) + r"\(.*?)(?=^[ ]{0,8}(?:async )?def |^[A-Za-z_@]|\Z)", re.S | re.M)
    m = pat.search(src)
    return m.group(1).strip() if m else None


for fn in ["fetch_candles_once", "_bridge_fetch_recent_candles", "fetch_candles_with_retry",
           "realtime_stream", "_fill_missing_slots", "_align_time", "_parse_raw_candles",
           "get_candles_ws", "get_candles", "_fetch_historical_batch", "get_historical_candles",
           "prepare_candles", "fill_gap_once", "update_candle", "on_message"]:
    a, b = extract_fn(eng, fn), extract_fn(orig, fn)
    if a is None:
        fail(f"roundtrip: {fn} missing in engine")
    if b is None:
        fail(f"roundtrip: {fn} missing in original")
    if a != b:
        fail(f"roundtrip: {fn} differs from the original upload")
edits_done.append("roundtrip: 15 original fetch/seal functions byte-identical OK")

# حفظ نسخة احتياطية ثم الكتابة
if not BAK.exists():
    BAK.write_text(SRC.read_text(encoding="utf-8"), encoding="utf-8")
    edits_done.append(f"backup: {BAK.name}")

SRC.write_text(text, encoding="utf-8")

print("=" * 70)
for e in edits_done:
    print(" ✓", e)
print("=" * 70)
print(f"OK — {len(edits_done)} edits applied. size {orig_len if False else 'n/a'} -> {len(text)} chars")
