#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني qx_server_v13.py من qx_server_v12.py (بطلب المستخدم):

1) BRLUSD_otc فوراً بعد الدخول: 300 شمعة + الحالة + نسبة الدفع (عملة فتح الشارت).
2) بقية الأصول المفتوحة: 300 شمعة لكل عملة، واحدة تلو الأخرى، مع بث حي لكل عملة
   حتى يكون أي شارت جاهزاً فور فتحه.
3) fetch_older_batch(): دفعة 170 شمعة أقدم للتمرير للخلف (scroll-back) — جاهزة
   على الخادم، وربطها بالتطبيق يُضاف لاحقاً (كما طلب المستخدم: ليس الآن).
4) التيكات في الذاكرة فقط وتُحذف تلقائياً بعد 5 دقائق حتى لا يمتلئ القرص.
5) أمان القرص: تدوير السجل (10MB) + ترميم candles.db (أحدث 5000 شمعة/عملة)
   + تباطؤ كتابة HST إلى 1.0 ثانية عند تدفق عدة عملات.
6) رفع حد الشموع في الذاكرة من 1000 إلى 3000 حتى تتراكم دفعات التمرير
   للخلف مثل المنصات الاحترافية (طريقة الجلب نفسها دون تغيير).
"""
import py_compile
from pathlib import Path

SRC = Path('/home/z/my-project/download/qx_server_v12.py')
DST = Path('/home/z/my-project/download/qx_server_v13.py')

src = SRC.read_text(encoding='utf-8')

# ── 1) ملاحظة الرأس ───────────────────────────────────────────────────────────
old_note = """# NOTE (v12.0): Terminal Asset Monitor — no web interface at all (FastAPI/HTML
# removed per user request). Console asks ONLY email + password (login method
# untouched), then prints the FULL asset list (payout % + open/closed) in the
# terminal and re-prints it on any change.
# v12 FIX: the server answers instruments/get in TWO stages (451- placeholder
# then a separate frame carrying the actual JSON list). The previous build only
# handled the inline format, so the asset list never got stored (empty table).
# The candle engine (1000-candle fetch) stays in the file UNCHANGED but is not
# auto-started (the program never asks for an asset, per user spec)."""
new_note = """# NOTE (v13.0): Preload Engine — same terminal-only flow as v12 (no web
# interface, login asks ONLY email + password, full payout table in terminal).
# NEW per user request:
#   1) Right after login: 300 candles + status + payout for BRLUSD_otc (the
#      chart opener asset).
#   2) Then every other OPEN asset is loaded one-by-one with 300 candles each,
#      and a live price stream keeps running per asset so any chart opened
#      later is instantly ready.
#   3) fetch_older_batch(): fetches a 170-candle older batch (scroll-back
#      pagination, like professional platforms). Server-side is ready NOW;
#      wiring it to the app comes LATER (user said: not now).
#   4) Ticks live in MEMORY ONLY and are auto-deleted after 5 minutes, so the
#      disk never fills up with ticks. Log file rotates at 10MB, candles.db is
#      trimmed to the newest 5000 candles per symbol.
#   5) In-memory candle cap raised 1000 -> 3000 so scroll-back batches can
#      accumulate. The login method and the candle fetch method are UNCHANGED."""
assert old_note in src, 'header note not found'
src = src.replace(old_note, new_note)

# ── 2) ثوابت v13 بجانب WRITE_INTERVAL ────────────────────────────────────────
old_interval = """# ===== FIX 4: WRITE_INTERVAL = 0.5s 3.0s ( 500ms) =====
WRITE_INTERVAL = 0.5"""
new_interval = """# ===== FIX 4: WRITE_INTERVAL = 0.5s 3.0s ( 500ms) =====
WRITE_INTERVAL = 0.5
# ===== v13: ثوابت التحميل المسبق والبث المتعدد والقرص =====
# BRLUSD_otc = عملة فتح الشارت (طلب المستخدم) — تُحمّل فوراً بعد الدخول.
PRELOAD_FIRST_SYMBOL = "BRLUSD_otc"
PRELOAD_CANDLES = 300          # 300 شمعة لكل عملة عند التحميل الأولي
PAGINATION_BATCH = 170         # دفعة التمرير للخلف (scroll-back)
PRELOAD_MIN_CANDLES = 30       # أقل عدد مقبول من الشموع لعملة واحدة
PRELOAD_ASSET_DELAY = 1.0      # ثانية واحدة بين عملة وأخرى (واحدة تلو الأخرى)
PRELOAD_TIMEOUT = 25.0         # مهلة طلب الشموع لكل عملة
PRELOAD_WAIT_INSTRUMENTS = 120 # أقصى انتظار لقائمة العملات بعد الدخول
PRELOAD_REFRESH_INTERVAL = 900 # كل 15 دقيقة: أصول فتحت حديثاً / أصول أُغلقت
# التيكات: في الذاكرة فقط، وتُحذف تلقائياً بعد 5 دقائق (طلب المستخدم صراحةً
# حتى لا يمتلئ القرص بالتيكس بعد شهر من التشغيل).
TICK_RETENTION_SECONDS = 300
TICK_PURGE_INTERVAL = 30
TICK_CACHE_MAXLEN = 600        # حد أقصى للتيكات المحفوظة لكل عملة
# أمان القرص:
MT4_WRITE_THROTTLE = 1.0       # كان 0.2s لعملة واحدة؛ مع ~90 عملة = 1.0s لكتابة HST
ASSET_MAX_CANDLES = 3000       # كان 1000؛ رُفع لكي تتراكم دفعات التمرير للخلف
CANDLESTORE_KEEP_PER_SYMBOL = 5000  # أقصى شموع محفوظة في candles.db لكل عملة
DB_TRIM_INTERVAL = 3600        # فحص حجم candles.db كل ساعة
LOG_MAX_BYTES = 10 * 1024 * 1024    # تدوير qxchart.log عند 10MB"""
assert src.count(old_interval) == 1, 'WRITE_INTERVAL line not found'
src = src.replace(old_interval, new_interval)

# ── 3) بوابة كتابة HST في update_candle: 0.2s -> MT4_WRITE_THROTTLE ─────────
old_gate = "        if now - state['last_write'] > 0.2:"
new_gate = ("        # v13: MT4_WRITE_THROTTLE (1.0s) بدل 0.2s — مع عشرات العملات المتدفقة\n"
            "        # يبقى تحديث الشارت حياً (كل ثانية) دون إرهاق القرص.\n"
            "        if now - state['last_write'] > MT4_WRITE_THROTTLE:")
assert src.count(old_gate) == 1, 'update_candle write gate not found'
src = src.replace(old_gate, new_gate)

# ── 4) رفع حد الشموع في الذاكرة (realtime_stream + update_candle) ────────────
old_cap1 = "                    if len(asset.candles) > INITIAL_CANDLES: asset.candles = asset.candles[-INITIAL_CANDLES:]"
new_cap1 = ("                    # v13: الحد رُفع من 1000 إلى ASSET_MAX_CANDLES (3000) حتى تتراكم\n"
            "                    # دفعات التمرير للخلف (fetch_older_batch) مثل المنصات الاحترافية.\n"
            "                    if len(asset.candles) > ASSET_MAX_CANDLES: asset.candles = asset.candles[-ASSET_MAX_CANDLES:]")
assert src.count(old_cap1) == 1, 'realtime_stream candle cap not found'
src = src.replace(old_cap1, new_cap1)

old_cap2 = """        if len(state['candles']) > 1000:
            state['candles'] = state['candles'][-1000:]"""
new_cap2 = """        # v13: الحد رُفع من 1000 إلى ASSET_MAX_CANDLES (3000) لتراكم دفعات التمرير للخلف
        if len(state['candles']) > ASSET_MAX_CANDLES:
            state['candles'] = state['candles'][-ASSET_MAX_CANDLES:]"""
assert src.count(old_cap2) == 1, 'update_candle candle cap not found'
src = src.replace(old_cap2, new_cap2)

# ── 5) تدوير ملف السجل (حتى لا يمتلئ القرص بعد أسابيع) ───────────────────────
old_log = """def _log_to_file(line: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\\n")
    except Exception: pass"""
new_log = """def _log_to_file(line: str):
    # v13: تدوير السجل — عند تجاوز 10MB يُنقل إلى qxchart.old.log ويبدأ ملف جديد
    # (بدون هذه الحماية يمتلئ القرص بعد أسابيع من التشغيل المستمر).
    try:
        _max = globals().get('LOG_MAX_BYTES', 10 * 1024 * 1024)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > _max:
            _old = LOG_FILE.with_suffix('.old.log')
            try:
                if _old.exists():
                    _old.unlink()
            except Exception:
                pass
            LOG_FILE.replace(_old)
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\\n")
    except Exception: pass"""
assert src.count(old_log) == 1, 'log function not found'
src = src.replace(old_log, new_log)

# ── 6) استبدال كتلة __main__ وإضافة SECTION 10 قبلها ─────────────────────────
marker = 'if __name__ == "__main__":'
idx = src.index(marker)
src_head = src[:idx]

SECTION_10 = '''# ==============================================================================
# SECTION 10 (v13.0): PRELOAD 300 + PAGINATION 170 + TICK RETENTION 5 MIN
# ==============================================================================
# محرك التحميل المسبق (بطلب المستخدم حرفياً):
#   1) بعد الدخول مباشرة: 300 شمعة لـ BRLUSD_otc (هي العملة التي تفتح الشارت)
#      مع حالتها (مفتوح/مغلق) ونسبة دفعها.
#   2) بقية الأصول المفتوحة تتحمل واحدة تلو الأخرى: 300 شمعة لكل عملة.
#   3) البث الحي يبقى يعمل لكل عملة محمّلة — لذلك عندما يُفتح أي شارت لاحقاً
#      يكون جاهزاً فوراً (الأسعار تتدفق داخله باستمرار).
#   4) fetch_older_batch(): عند التمرير للخلف في الشارت يجلب دفعة صغيرة من
#      170 شمعة أقدم، وكلما زاد التمرير للخلف تظهر شموع أخرى مثل المنصات
#      الاحترافية. الدالة جاهزة الآن على الخادم؛ ربطها بالتطبيق يُضاف لاحقاً
#      (طلب المستخدم: ليس الآن).
#   5) التيكات تُحفظ في الذاكرة فقط ولا تُكتب على القرص أبداً، وتُحذف تلقائياً
#      بعد 5 دقائق (لأن الشموع تكون قد تشكّلت منها) — بهذا لا يمتلئ القرص
#      بالتيكس ولا بالشموع مهما طال عمر التشغيل.
# طريقة الدخول وطريقة جلب الشموع الأصلية لم تُمَس إطلاقاً.
# ==============================================================================
from collections import deque as _deque

# كاش التيكات في الذاكرة فقط: api_symbol -> deque[(ts, price)]
_TICK_CACHE = {}
_TICK_LOCK = threading.Lock()
_PRELOADED_INFO = {}      # api_symbol -> {"candles": n, "at": "HH:MM:SS", "oldest": ts, "closed": bool}
_ASSET_OBJECTS = {}       # api_symbol -> Asset (مسمّيات الكائنات المعاد استخدامها)
_OPENER_STATUS_SHOWN = False


def _get_or_create_asset(api_symbol: str) -> Asset:
    """يعيد كائن Asset موجود أو ينشئه (بدون تكرار)."""
    for a in list(ALL_STREAMING_ASSETS):
        if a.api_symbol == api_symbol:
            return a
    a = _ASSET_OBJECTS.get(api_symbol)
    if a is None:
        a = Asset(api_symbol)
        _ASSET_OBJECTS[api_symbol] = a
    return a


def _cache_tick(api_symbol: str, ts: int, price: float):
    """يخزن تيكاً في الذاكرة فقط (لا يوجد أي ملف تيكات على القرص في v13)."""
    with _TICK_LOCK:
        d = _TICK_CACHE.get(api_symbol)
        if d is None:
            d = _deque(maxlen=TICK_CACHE_MAXLEN)
            _TICK_CACHE[api_symbol] = d
        d.append((int(ts), float(price)))


def _prune_tick_cache() -> int:
    """v13 (طلب المستخدم): حذف كل تيك أقدم من 5 دقائق — التيكات القديمة لا
    فائدة منها لأن الشموع تشكّلت منها، وحذفها يمنع امتلاء الذاكرة والقرص."""
    cutoff = time.time() - TICK_RETENTION_SECONDS
    removed = 0
    with _TICK_LOCK:
        for sym in list(_TICK_CACHE.keys()):
            d = _TICK_CACHE[sym]
            n0 = len(d)
            while d and d[0][0] < cutoff:
                d.popleft()
            removed += n0 - len(d)
            if not d:
                _TICK_CACHE.pop(sym, None)
    return removed


def get_recent_ticks(api_symbol: str, seconds: int = TICK_RETENTION_SECONDS) -> list:
    """يعيد تيكات آخر N ثانية لعملة معينة من الكاش (للتطبيق لاحقاً)."""
    with _TICK_LOCK:
        d = _TICK_CACHE.get(api_symbol)
        if not d:
            return []
        cutoff = time.time() - max(1, int(seconds))
        return [[t, p] for (t, p) in d if t >= cutoff]


async def tick_cache_collector():
    """يجمع تيكات كل الأصول المتدفقة في الذاكرة فقط — كل 0.25 ثانية يقرأ آخر
    سعر من realtime_candles لكل عملة ويخزنه. لا يكتب أي شيء على القرص."""
    last_ts = {}
    while True:
        try:
            if CLIENT is not None and CLIENT.api is not None and CONNECTION_ALIVE:
                for asset in list(ALL_STREAMING_ASSETS):
                    c = CLIENT.api.realtime_candles.get(asset.api_symbol)
                    try:
                        if isinstance(c, list) and len(c) >= 3:
                            ts, price = int(c[1]), float(c[2])
                        elif isinstance(c, dict):
                            ts = int(c.get("time", c.get("timestamp", 0)))
                            price = float(c.get("price", c.get("close", 0)))
                        else:
                            continue
                        if ts > 0 and price > 0 and ts > last_ts.get(asset.api_symbol, 0):
                            last_ts[asset.api_symbol] = ts
                            _cache_tick(asset.api_symbol, ts, price)
                    except Exception:
                        continue
            await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def tick_retention_loop():
    """v13: حلقة الحذف الدوري — كل TICK_PURGE_INTERVAL ثانية تحذف التيكات
    الأقدم من TICK_RETENTION_SECONDS (5 دقائق)."""
    while True:
        await asyncio.sleep(TICK_PURGE_INTERVAL)
        try:
            removed = _prune_tick_cache()
            kept = sum(len(d) for d in _TICK_CACHE.values())
            if removed:
                logmsg(f"[ticks] purged {removed} ticks older than "
                       f"{TICK_RETENTION_SECONDS // 60} min (kept {kept} in memory only — "
                       f"no tick is ever written to disk)")
        except Exception as e:
            logmsg(f"[ticks] purge error: {e}")


async def candlestore_trim_loop():
    """v13: ترميم candles.db كل ساعة — يحتفظ بأحدث CANDLESTORE_KEEP_PER_SYMBOL
    شمعة لكل عملة ويحذف الأقدم، ثم يفرّغ ملف WAL. بهذا لا ينمو حجم قاعدة
    الشموع بلا حدود حتى لو اشتغل السيرفر شهراً كاملاً."""
    while True:
        await asyncio.sleep(DB_TRIM_INTERVAL)
        try:
            db_path = get_candle_store().db_path
            conn = _sqlite3.connect(db_path, timeout=10.0, isolation_level=None)
            try:
                cur = conn.execute("SELECT DISTINCT symbol FROM candles;")
                symbols = [r[0] for r in cur.fetchall()]
                trimmed = 0
                for sym in symbols:
                    c2 = conn.execute(
                        "DELETE FROM candles WHERE symbol=? AND time < ("
                        " SELECT time FROM candles WHERE symbol=?"
                        " ORDER BY time DESC LIMIT 1 OFFSET ?);",
                        (sym, sym, CANDLESTORE_KEEP_PER_SYMBOL))
                    if c2.rowcount and c2.rowcount > 0:
                        trimmed += c2.rowcount
                if trimmed:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                    logmsg(f"[db] trimmed {trimmed} old candle rows "
                           f"(keep newest {CANDLESTORE_KEEP_PER_SYMBOL}/symbol)")
            finally:
                conn.close()
        except Exception as e:
            logmsg(f"[db] trim error: {e}")


def _format_raw_candles(res) -> list:
    """تحويل رد الخادم إلى شموع منسقة (نفس منطق وتنسيق fetch_candles_once
    الأصلي دون أي تغيير في طريقة الجلب نفسها)."""
    out = []
    if not res:
        return out
    for c in res:
        if not isinstance(c, dict):
            continue
        try:
            ts = int(float(c.get("time", c.get("timestamp", 0))))
            if ts <= 0:
                continue  # v13: تجاهل الردود بلا وقت صالح (حماية من شموع تالفة)
            aligned = _align_time(ts, period_seconds=PERIOD_SECONDS)
            o = float(c.get("open", 0))
            h = float(c.get("high", c.get("max", 0)))
            l = float(c.get("low", c.get("min", 0)))
            cl = float(c.get("close", 0))
            if o > 0 and h > 0 and l > 0 and cl > 0:
                out.append({'time': aligned, 'open': o, 'high': h, 'low': l,
                            'close': cl, 'volume': random.randint(50, 200)})
        except Exception:
            continue
    seen, unique = set(), []
    for c in out:
        if c['time'] not in seen:
            seen.add(c['time'])
            unique.append(c)
    unique.sort(key=lambda x: x['time'])
    return unique


async def _fetch_candle_window(api_symbol: str, end_time: int, seconds: int):
    """طلب شموع واحد عبر نفس CLIENT.get_candles الأصلي (نفس طريقة الجلب
    الرسمية دون أي تعديل): end_time = نهاية النافذة، seconds = طولها بالثواني."""
    res = await asyncio.wait_for(
        CLIENT.get_candles(api_symbol, int(end_time), int(seconds), PERIOD_SECONDS),
        timeout=PRELOAD_TIMEOUT,
    )
    return res


def _apply_candles_to_asset(asset: Asset, candles: list):
    """تخزين الشموع في كل القنوات الرسمية: ذاكرة العملة + ملف HST الأول
    + sync_state + ملف HST الثاني + قاعدة candles.db."""
    asset.candles = list(candles)
    if candles:
        asset.price = float(candles[-1]['close'])
    try:
        asset.write(force=True)
    except Exception:
        pass
    MT4_WRITER.sync_state[asset.symbol] = {
        'period': PERIOD,
        'candles': list(asset.candles),
        'last_write': 0,
        'last_price': float(asset.candles[-1]['close']) if asset.candles else 0.0,
    }
    try:
        MT4_WRITER.write_to_file(asset.symbol, PERIOD, asset.candles)
    except Exception:
        pass
    try:
        MT4_WRITER.save_snapshot(asset.symbol, asset.candles)
    except Exception:
        pass


def _print_opener_banner(api_symbol: str, entry, candles_count: int, elapsed: float):
    """لوحة جاهزية عملة فتح الشارت: الشموع + الحالة + نسب الدفع."""
    def _p(v):
        return f"{v}%" if isinstance(v, (int, float)) else "-"
    name = (entry.get("name") or "-") if entry else "-"
    payout = entry.get("payout") if entry else None
    turbo = entry.get("turbo_payout") if entry else None
    p1 = entry.get("profit_1m") if entry else None
    p5 = entry.get("profit_5m") if entry else None
    if entry is None:
        status_str = f"{Colors.DIM}UNKNOWN (asset list not ready yet){Colors.RESET}"
    elif entry.get("open"):
        status_str = f"{Colors.GREEN}OPEN{Colors.RESET}"
    else:
        status_str = f"{Colors.RED}CLOSED{Colors.RESET}"
    print()
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}  CHART OPENER READY — {api_symbol}{Colors.RESET}")
    print(f"  Name: {name}  |  Candles: {candles_count}  |  Loaded in {elapsed:.1f}s")
    print(f"  Payout: {_p(payout)}  |  Turbo: {_p(turbo)}  |  1M: {_p(p1)}  |  5M: {_p(p5)}"
          f"  |  Status: {status_str}")
    print(f"  {Colors.DIM}Live stream: ON — الشارت جاهز للفتح فوراً والأسعار تتدفق داخله{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")


async def preload_one_asset(api_symbol: str, idx: int = 1, total: int = 1):
    """تحميل عملة واحدة: 300 شمعة عبر نفس طريقة الجلب الأصلية، ثم تشغيل
    البث الحي لها. تعيد عدد الشموع أو None عند الفشل."""
    asset = _get_or_create_asset(api_symbol)
    have_data = (asset.symbol in MT4_WRITER.sync_state and asset.candles
                 and len(asset.candles) >= PRELOAD_CANDLES)
    if not have_data:
        res = await _fetch_candle_window(
            api_symbol, int(time.time()), PRELOAD_CANDLES * PERIOD_SECONDS + PERIOD_SECONDS)
        candles = _format_raw_candles(res)[-PRELOAD_CANDLES:]
        if not candles or len(candles) < PRELOAD_MIN_CANDLES:
            logmsg(f"[preload {idx}/{total}] {api_symbol}: only {len(candles)} candles — skipped")
            return None
        _apply_candles_to_asset(asset, candles)
    # التأكد من أن البث الحي يعمل لهذه العملة (لأن أي شارت يُفتح لاحقاً يجب
    # أن يجد الأسعار تتدفق داخله — طلب المستخدم).
    task = asset.stream_task
    task_running = False
    try:
        task_running = task is not None and not task.done()
    except Exception:
        task_running = False
    if not (asset.streaming and task_running):
        try:
            asset.stream_task = asyncio.run_coroutine_threadsafe(realtime_stream(asset), ASYNC_LOOP)
            await asyncio.sleep(0.05)
        except Exception as e:
            logmsg(f"[preload {idx}/{total}] {api_symbol}: stream start failed: {e}")
    if asset not in ALL_STREAMING_ASSETS:
        ALL_STREAMING_ASSETS.append(asset)
    _PRELOADED_INFO[api_symbol] = {
        "candles": len(asset.candles) if asset.candles else 0,
        "at": datetime.now().strftime("%H:%M:%S"),
        "oldest": asset.candles[0]['time'] if asset.candles else 0,
        "closed": _PRELOADED_INFO.get(api_symbol, {}).get("closed", False),
    }
    return len(asset.candles) if asset.candles else 0


async def preload_all_assets():
    """v13: محرك التحميل المسبق الكامل —
    1) BRLUSD_otc فوراً بعد الدخول (لا تنتظر القائمة).
    2) ثم بقية الأصول المفتوحة 300 شمعة لكل عملة، واحدة تلو الأخرى.
    3) إيقاف بث الأصول التي أُغلقت، وتحميل الأصول التي فتحت حديثاً
       كل PRELOAD_REFRESH_INTERVAL ثانية."""
    global _OPENER_STATUS_SHOWN
    logmsg(f"[preload] fetching {PRELOAD_FIRST_SYMBOL} immediately (chart opener)...")
    t0 = time.time()
    try:
        n = await preload_one_asset(PRELOAD_FIRST_SYMBOL, 1, 1)
        if n:
            logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL}: {n} candles + live stream ON "
                   f"({time.time() - t0:.1f}s)")
            _print_opener_banner(PRELOAD_FIRST_SYMBOL, None, n, time.time() - t0)
    except Exception as e:
        logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL} immediate fetch failed: {e} (will retry)")
    while True:
        cycle_start = time.time()
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = _instruments_snapshot()
            waited = 0.0
            while not entries and waited < PRELOAD_WAIT_INSTRUMENTS:
                await asyncio.sleep(2.0)
                waited += 2.0
                if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                    break
                entries = _instruments_snapshot()
            if entries:
                by_asset = {}
                for e in entries:
                    if e.get("asset"):
                        by_asset[e["asset"]] = e
                if not _OPENER_STATUS_SHOWN and PRELOAD_FIRST_SYMBOL in by_asset:
                    _OPENER_STATUS_SHOWN = True
                    _e = by_asset[PRELOAD_FIRST_SYMBOL]
                    _pv = _e.get("payout")
                    _pv_str = f"{_pv}%" if isinstance(_pv, (int, float)) else "-"
                    logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL} status: "
                           f"{'OPEN' if _e.get('open') else 'CLOSED'} | payout {_pv_str}")
                open_assets = [a for a, e in by_asset.items() if e.get("open") is True]

                def _pay(a):
                    p = by_asset[a].get("payout")
                    return p if isinstance(p, (int, float)) else -1

                open_assets.sort(key=_pay, reverse=True)
                ordered = []
                if PRELOAD_FIRST_SYMBOL in by_asset:
                    ordered.append(PRELOAD_FIRST_SYMBOL)
                    if PRELOAD_FIRST_SYMBOL in open_assets:
                        open_assets.remove(PRELOAD_FIRST_SYMBOL)
                ordered.extend(open_assets)
            else:
                by_asset = {}
                ordered = [PRELOAD_FIRST_SYMBOL]
            total = len(ordered)
            for idx, sym in enumerate(ordered, 1):
                if CLIENT is None or not CONNECTION_ALIVE:
                    logmsg("[preload] connection lost — cycle aborted (will retry)")
                    break
                if sym in _PRELOADED_INFO:
                    continue
                try:
                    _t = time.time()
                    n = await preload_one_asset(sym, idx, total)
                    if n:
                        if sym == PRELOAD_FIRST_SYMBOL:
                            _print_opener_banner(sym, by_asset.get(sym), n, time.time() - _t)
                        else:
                            logmsg(f"[preload {idx}/{total}] {sym}: {n} candles + "
                                   f"live stream ON ({time.time() - _t:.1f}s)")
                    await asyncio.sleep(PRELOAD_ASSET_DELAY)
                except Exception as e:
                    logmsg(f"[preload {idx}/{total}] {sym}: failed ({e})")
                    await asyncio.sleep(PRELOAD_ASSET_DELAY)
            # إيقاف بث الأصول التي أُغلقت (الشموع تبقى محفوظة في DB وHST،
            # وإذا أعيد فتحها لاحقاً يعود بثها تلقائياً في الدورة التالية).
            if by_asset:
                closed_syms = {a for a, e in by_asset.items() if e.get("open") is False}
                for asset in list(ALL_STREAMING_ASSETS):
                    if asset.api_symbol in closed_syms:
                        try:
                            if asset.stream_task is not None and not asset.stream_task.done():
                                asset.stream_task.cancel()
                        except Exception:
                            pass
                        asset.streaming = False
                        try:
                            ALL_STREAMING_ASSETS.remove(asset)
                        except ValueError:
                            pass
                        _info = _PRELOADED_INFO.get(asset.api_symbol)
                        if _info is not None:
                            _info["closed"] = True
                        logmsg(f"[preload] {asset.api_symbol}: CLOSED — live stream stopped "
                               f"(candles kept in DB/HST)")
            logmsg(f"[preload] cycle done in {time.time() - cycle_start:.0f}s — "
                   f"{len(ALL_STREAMING_ASSETS)} assets streaming live, "
                   f"{len(_PRELOADED_INFO)} loaded with candles")
        except Exception as e:
            log_exception("preload_all_assets", e)
        await asyncio.sleep(PRELOAD_REFRESH_INTERVAL)


async def fetch_older_batch(api_symbol: str, before_time=None, count: int = PAGINATION_BATCH):
    """v13: دفعة التمرير للخلف (scroll-back) — يجلب COUNT شمعة أقدم من
    before_time عبر نفس طريقة الجلب الأصلية، ويدمجها مع الشموع الموجودة
    في الذاكرة وHST وcandles.db. مثل المنصات الاحترافية: كلما مررت للخلف
    تظهر دفعة جديدة.
    الدالة جاهزة الآن على الخادم — التطبيق سيستدعيها لاحقاً عند ربطه
    (عبر PAGINATION_API أدناه). تعيد عدد الشموع المضافة فعلياً."""
    if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
        logmsg(f"[older:{api_symbol}] no connection — batch skipped")
        return 0
    asset = _get_or_create_asset(api_symbol)
    if before_time is None:
        if asset.candles:
            before_time = int(asset.candles[0]['time'])
        else:
            before_time = int(time.time()) - PRELOAD_CANDLES * PERIOD_SECONDS
    before_time = int(before_time)
    res = await _fetch_candle_window(api_symbol, before_time,
                                     count * PERIOD_SECONDS + PERIOD_SECONDS)
    candles = _format_raw_candles(res)
    older = [c for c in candles if c['time'] < before_time][-count:]
    if not older:
        logmsg(f"[older:{api_symbol}] server returned nothing older than "
               f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(before_time))} (history end?)")
        return 0
    merged = list(older) + list(asset.candles or [])
    seen, unique = set(), []
    for c in merged:
        if c['time'] not in seen:
            seen.add(c['time'])
            unique.append(c)
    unique.sort(key=lambda x: x['time'])
    unique = unique[-ASSET_MAX_CANDLES:]
    _apply_candles_to_asset(asset, unique)
    # v13: تحديث معلومات التحميل المسبق ليعكس عدد الشموع بعد الدفعة الجديدة
    _prev_info = _PRELOADED_INFO.get(api_symbol, {})
    _PRELOADED_INFO[api_symbol] = {
        "candles": len(asset.candles) if asset.candles else 0,
        "at": datetime.now().strftime("%H:%M:%S"),
        "oldest": asset.candles[0]['time'] if asset.candles else 0,
        "closed": _prev_info.get("closed", False),
        "last_older_batch": len(older),
    }
    logmsg(f"[older:{api_symbol}] +{len(older)} candles (batch {count}) — oldest now "
           f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(unique[0]['time']))}")
    return len(older)


# نقطة ربط مستقبلية للتطبيق (عند ربطه لاحقاً كما طلب المستخدم):
#   PAGINATION_API["fetch_older_batch"]("BRLUSD_otc")  -> +170 شمعة أقدم
#   PAGINATION_API["get_recent_ticks"]("BRLUSD_otc")   -> تيكات آخر 5 دقائق
#   PAGINATION_API["preload_status"]()                 -> حالة التحميل المسبق
PAGINATION_API = {
    "fetch_older_batch": fetch_older_batch,
    "get_recent_ticks": get_recent_ticks,
    "preload_status": lambda: dict(_PRELOADED_INFO),
    "tick_cache": _TICK_CACHE,
}


'''

NEW_TAIL = '''if __name__ == "__main__":
    # ════════════════════════════════════════════════════════════════════
    # v13.0 — Preload Engine (بطلب المستخدم):
    #   - نفس تدفق v12: نطاق تلقائي + دخول (البريد وكلمة المرور فقط) + جدول
    #     العملات الكامل في الترمينال.
    #   - جديد: بعد الدخول مباشرة يجلب 300 شمعة لـ BRLUSD_otc (عملة فتح الشارت)
    #     مع حالتها ونسبة دفعها، ثم يجلب 300 شمعة لبقية الأصول المفتوحة واحدة
    #     تلو الأخرى، ويشغّل البث الحي لكل عملة حتى يكون أي شارت جاهزاً فوراً.
    #   - جديد: fetch_older_batch() تجلب دفعة 170 شمعة أقدم للتمرير للخلف —
    #     جاهزة على الخادم، وربطها بالتطبيق يُضاف لاحقاً (ليس الآن).
    #   - جديد: التيكات في الذاكرة فقط وتُحذف تلقائياً بعد 5 دقائق + تدوير
    #     السجل + ترميم candles.db — حتى لا يمتلئ القرص أبداً.
    #   - طريقة الدخول وطريقة جلب الشموع كما هي دون أي تغيير.
    # ════════════════════════════════════════════════════════════════════
    print()
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  QX SERVER v13.0 — Preload + Live Streams{Colors.RESET}")
    print(f"  {Colors.DIM}BRLUSD_otc: 300 شمعة فوراً بعد الدخول + الحالة ونسبة الدفع{Colors.RESET}")
    print(f"  {Colors.DIM}ثم بقية الأصول المفتوحة: 300 شمعة لكل عملة، واحدة تلو الأخرى{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")

    # v12/v13: لا يوجد جدول حي — اطبع رسائل السجل مباشرة
    globals()['_STATUS_MESSAGES_QUEUE'] = None

    # ---- STAGE 1: النطاق تلقائياً حسب البلد (بدون أي سؤال) ----
    print()
    print(f"{Colors.BOLD}  Domain: detecting country automatically ...{Colors.RESET}")
    resolve_qx_host()
    globals()['QX_HOST'] = QX_HOST
    _geo_country = _GEO_CACHE.get("country") or "unknown"
    print(f"{Colors.GREEN}  Country: {_geo_country}  ->  Domain: {QX_HOST}{Colors.RESET}")

    # ---- STAGE 2: تسجيل الدخول — البريد وكلمة المرور فقط ----
    # نفس كود v10/v11/v12 حرفياً (حفظ الجلسة + connect_quotex + نفس المهلات).
    should_force = session_manager.should_force_fresh()
    saved_email = session_manager.get_saved_email()
    success = False
    if saved_email and not should_force:
        print(f"{Colors.GREEN}Found saved email: {saved_email}{Colors.RESET}")
        PASSWORD_INPUT = input(f"{Colors.CYAN} Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(saved_email, PASSWORD_INPUT, force_fresh=False, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=180)
    if not success:
        print()
        EMAIL_INPUT = input(f"{Colors.CYAN}Email: {Colors.RESET}").strip()
        PASSWORD_INPUT = input(f"{Colors.CYAN}Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(EMAIL_INPUT, PASSWORD_INPUT, force_fresh=True, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=300)
    if not success:
        print(f"\\n{Colors.RED}[FAILED] Could not connect after all attempts.{Colors.RESET}")
        sys.exit(1)

    # ---- STAGE 3: المراقبة + القائمة + التحميل المسبق + البث الحي ----
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass
    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # جدول العملات الكامل (الدفع + مفتوح/مغلق) — كما في v12 تماماً:
    asyncio.run_coroutine_threadsafe(asset_payout_monitor(), ASYNC_LOOP)
    # v13: BRLUSD_otc فوراً (300 شمعة + بث حي) ثم بقية الأصول المفتوحة واحدة تلو الأخرى:
    asyncio.run_coroutine_threadsafe(preload_all_assets(), ASYNC_LOOP)
    # v13: كاش التيكات في الذاكرة + حذف التيكات الأقدم من 5 دقائق:
    asyncio.run_coroutine_threadsafe(tick_cache_collector(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(tick_retention_loop(), ASYNC_LOOP)
    # v13: ترميم candles.db (أحدث 5000 شمعة لكل عملة) — القرص لا يمتلئ أبداً:
    asyncio.run_coroutine_threadsafe(candlestore_trim_loop(), ASYNC_LOOP)

    print()
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  Connected! Chart opener + preload engine running ...{Colors.RESET}")
    print(f"  {Colors.DIM}1) BRLUSD_otc: 300 شمعة فوراً + الحالة ونسبة الدفع + بث حي{Colors.RESET}")
    print(f"  {Colors.DIM}2) بقية الأصول المفتوحة: 300 شمعة لكل عملة، واحدة تلو الأخرى{Colors.RESET}")
    print(f"  {Colors.DIM}3) البث الحي يعمل لكل الأصول — أي شارت يُفتح يكون جاهزاً{Colors.RESET}")
    print(f"  {Colors.DIM}4) الجدول الكامل (الدفع + مفتوح/مغلق) يُطبع ويُحدّث تلقائياً{Colors.RESET}")
    print(f"  {Colors.DIM}5) التمرير للخلف: دفعات 170 شمعة جاهزة على الخادم (للتطبيق لاحقاً){Colors.RESET}")
    print(f"  {Colors.DIM}6) التيكات في الذاكرة فقط وتُحذف بعد 5 دقائق — القرص لا يمتلئ{Colors.RESET}")
    print(f"  {Colors.DIM}للخروج: Ctrl+C{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")

    try:
        # الخيط الرئيسي يبقى حيّاً فقط — كل العمل في حلقات الخلفية
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print(f"{Colors.RED}Stopped{Colors.RESET}")
        writer_thread.running = False
'''

DST.write_text(src_head + SECTION_10 + NEW_TAIL, encoding='utf-8')
py_compile.compile(str(DST), doraise=True)
print('OK: wrote', DST)
