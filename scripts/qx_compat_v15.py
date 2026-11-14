# ═══════════════════════════════════════════════════════════════════════════
# ═══ طبقة ربط التطبيق (APP GLUE) — v15.0 «الأصل هو الخادم»                  ═══
# ═══════════════════════════════════════════════════════════════════════════
# هذا القسم يُضاف **فوق** كود الخادم الأصلي (الملصق حرفياً) دون تعديل أي سطر
# فيه. كل ما يلي ليس منطقاً جديداً ولا منطقاً معدّلاً — إنه مجرد جسور تمرّر
# طلبات التطبيق إلى آلة الخادم الأصلية نفسها كما هي حرفياً:
#   fetch_candles_with_retry / realtime_stream / MT4_WRITER.fill_gap_once /
#   _fill_missing_slots / _align_time / CLIENT.get_candles /
#   CLIENT._fetch_historical_batch / WriterThread / mt4_gap_filler ...
# (كود الخادم الأصلي أعلاه لم يُمَس بايت واحد — وهذا القسم يبدأ بعده مباشرة)
# ═══════════════════════════════════════════════════════════════════════════

# ─── استيرادات الطبقة فقط (المحرك الأصلي لم يُمَس) ───
from collections import deque as _qx_deque

# ═══ 1) النطاقات + البلد (نفس كتلة v10 الرسمية حرفياً) ═══
DEFAULT_DOMAIN_GLOBAL = "quotex.com"
DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
_GEO_CACHE = {"country": None, "checked_at": 0.0}

def detect_country_code(timeout: float = 4.0):
    """يرجع رمز البلد فقط (مثل BD / SA / EG) عبر IP العام. لا يجلب أي موقع دقيق."""
    if _GEO_CACHE["country"] and time.time() - _GEO_CACHE["checked_at"] < 3600:
        return _GEO_CACHE["country"]
    endpoints = [
        ("http://ip-api.com/json/?fields=status,countryCode", lambda d: (d or {}).get("countryCode")),
        ("https://ipapi.co/json/", lambda d: (d or {}).get("country_code")),
        ("https://api.ip.sb/geoip", lambda d: (d or {}).get("country_code")),
    ]
    for url, extract in endpoints:
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
            code = extract(r.json())
            if code:
                _GEO_CACHE["country"] = str(code).upper()
                _GEO_CACHE["checked_at"] = time.time()
                return _GEO_CACHE["country"]
        except Exception:
            continue
    return None

def resolve_qx_host() -> str:
    """يحدد النطاق تلقائياً حسب البلد ويضبط QX_HOST العام:
    بنغلاديش -> market-qx.info ، أي دولة أخرى (أو فشل التعرف) -> quotex.com."""
    global QX_HOST
    country = detect_country_code()
    if country == "BD":
        QX_HOST = DEFAULT_DOMAIN_BANGLADESH
    else:
        QX_HOST = DEFAULT_DOMAIN_GLOBAL
    return QX_HOST

# ═══ 2) قائمة العملات الكاملة + الدفع + الحالة (نفس كتلة v10 حرفياً) ═══
PAYOUT_REFRESH_INTERVAL = 60
try:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")
except Exception:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")

def _instruments_snapshot():
    """يبني قائمة الأصول الكاملة (الاسم + نسبة الدفع + الحالة) من instruments."""
    if CLIENT is None or CLIENT.api is None:
        return []
    insts = getattr(CLIENT.api, "instruments", None) or []
    out = []
    for i in insts:
        try:
            if not isinstance(i, (list, tuple)) or len(i) < 6:
                continue
            entry = {
                "asset": str(i[1]) if len(i) > 1 else "",
                "name": str(i[2]).replace("\n", " ").strip() if len(i) > 2 else "",
                "payout": i[5] if len(i) > 5 else None,
            }
            try:
                entry["id"] = str(i[0])
            except Exception:
                entry["id"] = ""
            try:
                entry["turbo_payout"] = i[18] if len(i) > 18 else None
            except Exception:
                entry["turbo_payout"] = None
            try:
                entry["open"] = bool(i[14]) if len(i) > 14 else None
            except Exception:
                entry["open"] = None
            try:
                entry["profit_24h"] = i[-10]
            except Exception:
                entry["profit_24h"] = None
            try:
                entry["profit_1m"] = i[-9]
            except Exception:
                entry["profit_1m"] = None
            try:
                entry["profit_5m"] = i[-8]
            except Exception:
                entry["profit_5m"] = None
            out.append(entry)
        except Exception:
            continue
    return out

def _save_assets_payout_file(entries):
    """يحفظ لقطة كاملة إلى qx_assets_payouts.json بجانب الملف."""
    try:
        payload = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "host": QX_HOST,
            "count": len(entries),
            "open_count": sum(1 for e in entries if e.get("open")),
            "closed_count": sum(1 for e in entries if e.get("open") is False),
            "assets": entries,
        }
        ASSETS_PAYOUT_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        logmsg(f"[payout] failed to save {ASSETS_PAYOUT_FILE}: {e}")
        return False

async def fetch_instruments_now(timeout: float = 12.0):
    """طريقة pyquotex الرسمية: إرسال 42["instruments/get"] عبر نفس WebSocket
    والانتظار حتى وصول 451-["instruments/list"] ثم تخزينها في CLIENT.api.instruments.
    طريقة الدخول وطريقة جلب الشموع لا تتأثر إطلاقاً."""
    if CLIENT is None or CLIENT.api is None:
        return []
    try:
        await CLIENT.api.event_registry.clear_event("instruments_ready")
    except Exception:
        pass
    try:
        CLIENT.api.send_websocket_request('42["instruments/get"]')
    except Exception as e:
        logmsg(f"[payout] instruments request failed: {e}")
    data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=timeout)
    if isinstance(data, dict) and data.get("_placeholder"):
        data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=5.0)
    if isinstance(data, list) and data:
        CLIENT.api.instruments = data
    return list(getattr(CLIENT.api, "instruments", None) or [])

def _print_payout_table(entries):
    """طباعة الجدول الكامل: العملة / نسبة الدفع / الحالة (مفتوح أو مغلق)."""
    open_entries = [e for e in entries if e.get("open")]
    closed_entries = [e for e in entries if e.get("open") is False]
    print(f"\n{Colors.CYAN}{'═' * 72}{Colors.RESET}")
    print(f"{Colors.BOLD}  FULL ASSET LIST — PAYOUT % — OPEN/CLOSED{Colors.RESET}")
    print(f"  Total: {len(entries)}  |  {Colors.GREEN}OPEN: {len(open_entries)}{Colors.RESET}"
          f"  |  {Colors.RED}CLOSED: {len(closed_entries)}{Colors.RESET}"
          f"  |  Domain: {QX_HOST}")
    print(f"{Colors.CYAN}{'─' * 72}{Colors.RESET}")
    print(f"  {'ASSET':<16}{'PAYOUT':>7}  {'TURBO':>6}  {'1M':>5}  {'5M':>5}  STATUS")
    print(f"{Colors.DIM}{'─' * 72}{Colors.RESET}")
    for e in entries:
        name = (e.get("asset") or "?")[:16]
        payout = e.get("payout")
        turbo = e.get("turbo_payout")
        p1 = e.get("profit_1m")
        p5 = e.get("profit_5m")
        payout_str = f"{payout}%" if isinstance(payout, (int, float)) else "-"
        turbo_str = f"{turbo}%" if isinstance(turbo, (int, float)) else "-"
        p1_str = f"{p1}%" if isinstance(p1, (int, float)) else "-"
        p5_str = f"{p5}%" if isinstance(p5, (int, float)) else "-"
        if e.get("open"):
            status = f"{Colors.GREEN}OPEN{Colors.RESET}"
        else:
            status = f"{Colors.RED}CLOSED{Colors.RESET}"
        print(f"  {name:<16}{payout_str:>7}  {turbo_str:>6}  {p1_str:>5}  {p5_str:>5}  {status}")
    print(f"{Colors.CYAN}{'═' * 72}{Colors.RESET}")

async def asset_payout_monitor():
    """يجلب قائمة العملات الكاملة + نسبة الدفع + حالة الزوج (مفتوح/مغلق) مباشرة
    بعد تسجيل الدخول، يطبع الجدول مرة واحدة، يحفظ لقطة JSON، ثم يحدّث بهدوء
    كل PAYOUT_REFRESH_INTERVAL ثانية."""
    await asyncio.sleep(2.0)
    first = True
    last_signature = None
    while True:
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = []
            try:
                await fetch_instruments_now(timeout=12.0)
                entries = _instruments_snapshot()
            except Exception as e:
                logmsg(f"[payout] refresh failed: {e}")
            if entries:
                _save_assets_payout_file(entries)
                signature = tuple(sorted(
                    (e.get("asset"), str(e.get("payout")), str(e.get("open")))
                    for e in entries))
                if first:
                    try:
                        _print_payout_table(entries)
                    except Exception:
                        pass
                    first = False
                elif signature != last_signature:
                    open_n = sum(1 for e in entries if e.get("open"))
                    closed_n = sum(1 for e in entries if e.get("open") is False)
                    logmsg(f"[payout] updated: {len(entries)} assets "
                           f"({open_n} open / {closed_n} closed) — snapshot saved")
                last_signature = signature
        except Exception as e:
            log_exception("asset_payout_monitor", e)
        await asyncio.sleep(PAYOUT_REFRESH_INTERVAL)

# ═══ 3) مرصد instruments فوق on_message الأصلي ═══
# الأصل يعمل كاملاً أولاً حرفياً (_qx_orig_on_message(self, wss, msg)) ثم نلتقط
# فقط 451-["instruments/list",[...]] لنوقظ من ينتظره — نفس كتلة v10 حرفياً.
_qx_orig_on_message = WebsocketClient.on_message

def _qx_on_message_with_instruments(self, wss, msg):
    _qx_orig_on_message(self, wss, msg)      # الأصل حرفياً — كل شيء كما هو
    try:
        msg_str = msg.decode("utf-8", errors="ignore") if isinstance(msg, bytes) else str(msg)
        if "instruments/list" not in msg_str:
            return
        _idx = msg_str.find('["')
        if _idx == -1:
            return
        _payload = json.loads(msg_str[_idx:])
        _data = _payload[1] if isinstance(_payload, list) and len(_payload) >= 2 else None
        if isinstance(_data, dict) and "list" in _data:
            _data = _data["list"]
        if isinstance(_data, list) and _data:
            self.api.instruments = _data
            _loop = getattr(self.api, "_async_loop", None)
            if _loop is not None and _loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.api.event_registry.set_event("instruments_ready", _data),
                    _loop,
                )
            logger.info(f"Instruments list received: {len(_data)} assets")
    except Exception as _e:
        logger.debug(f"instruments/list parse error: {_e}")

WebsocketClient.on_message = _qx_on_message_with_instruments

# ═══ 4) إعدادات التطبيق على المحرك (نفس آلية قائمة الأصل نفسها) ═══
# القيم الافتراضية حسب طلب المستخدم: دفعة 700 شمعة (حتى 1000 من الإعدادات)
# وتاريخ 0.80 يوم لكل عملة.
PRELOAD_CANDLES = 700
PAGINATION_BATCH = 700
QX_HISTORY_DAYS = 0.80
ASSET_MAX_CANDLES = 45000
PRELOAD_FIRST_SYMBOL = ASSET_LIST[0] if ASSET_LIST else "BRLUSD_otc"
_PRELOADED_INFO = {}
V14_DEEP_REPAIRED = {}
_QX_WINDOW_BUSY = False

def apply_history_days(days_val):
    """تطبيق عدد أيام التاريخ بنفس آلية قائمة الأصل حرفياً (STAGE 3 وقائمة
    «Change History days» في الكود الأصلي): هامش +15% على المدى، INITIAL_CANDLES
    من الأيام، وFETCH_DURATION_SECONDS من المدى مع الهامش — نفس الثلاثي الأصلي."""
    global HISTORY_DAYS, INITIAL_CANDLES, FETCH_DURATION_SECONDS, QX_HISTORY_DAYS
    try:
        d = float(days_val)
    except Exception:
        d = 0.80
    d = max(0.05, d)
    days_with_margin = d * 1.15
    try:
        INITIAL_CANDLES = max(int((d * 86400) / max(1, PERIOD_SECONDS)), 100)
    except Exception:
        INITIAL_CANDLES = 1000
    HISTORY_DAYS = days_with_margin
    FETCH_DURATION_SECONDS = int(86400 * days_with_margin)
    QX_HISTORY_DAYS = d
    return QX_HISTORY_DAYS

# ═══ 5) سجل الأصول: نفس Asset الأصلي حرفياً (بلا أي حقن) ═══
def _get_or_create_asset(api):
    """يجلب أصل العملة من سجل البث أو ينشئه بـ Asset الأصلي نفسه."""
    sym = str(api or "").strip()
    if not sym:
        return None
    for a in ALL_STREAMING_ASSETS:
        try:
            if a.api_symbol == sym:
                return a
        except Exception:
            continue
    a = Asset(sym)
    ALL_STREAMING_ASSETS.append(a)
    return a

def _apply_candles_to_asset(asset, unique):
    """كتابة الخط الكامل في ذاكرة الأصل (Asset الأصلي) + السعر الحي."""
    try:
        asset.candles = list(unique or [])
        if asset.candles:
            asset.price = asset.candles[-1]["close"]
        asset.mark_dirty()
    except Exception:
        pass

async def ensure_asset_loaded(api):
    """عملة فُتح شارتها: البث الحي فوراً (realtime_stream الأصلية) ثم الجلب
    المباشر الأصلي fetch_candles_with_retry (كل ما يجلب فيه الأصل من تاريخ +
    جسر + سد فجوات + كتابة HST كما هي حرفياً). تعيد عدد الشموع في الذاكرة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None:
        return 0
    try:
        st = getattr(asset, "stream_task", None)
        if st is not None and hasattr(st, "done") and not st.done():
            pass
        else:
            asset.streaming = False
            asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
    except Exception:
        try:
            asset.streaming = False
            asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
        except Exception:
            pass
    if len(asset.candles) >= MIN_CANDLES_THRESHOLD:
        return len(asset.candles)
    try:
        await fetch_candles_with_retry(asset, max_retries=MAX_FETCH_RETRIES, idx=1, total=1)
    except Exception as e:
        logmsg(f"[ensure:{api}] fetch failed: {e}")
    return len(asset.candles)

# ═══ 6) جسور الجلب — نفس دوال الأصل حرفياً ═══
def _format_raw_candles(raw):
    """تنسيق رد الخادم الرسمي: تحليل _parse_raw_candles الأصلي + محاذاة
    _align_time الأصلية + إزالة تكرار وترتيب — نفس حلقة التنسيق في
    fetch_candles_once الأصلية."""
    if not raw:
        return []
    parsed = _parse_raw_candles(raw)          # الأصل حرفياً
    formatted = []
    for c in parsed:
        try:
            aligned = _align_time(int(c["time"]))
            formatted.append({"time": aligned, "open": c["open"], "high": c["high"],
                              "low": c["low"], "close": c["close"],
                              "volume": int(c.get("volume", 0) or 0)})
        except Exception:
            continue
    seen, unique = set(), []
    for c in formatted:
        if c["time"] not in seen:
            seen.add(c["time"])
            unique.append(c)
    unique.sort(key=lambda x: x["time"])
    return unique

async def qx_fetch_window_raw(api, end_ts, seconds, tf_sec, foreground=False, timeout=45.0):
    """بوابة الجلب الأمامية الواحدة — نداء CLIENT.get_candles الأصلي نفسه
    (المُجرّب والآمن). foreground يمنع اختلاط طلب العرض الحالي مع التحميل المسبق."""
    global _QX_WINDOW_BUSY
    if CLIENT is None or CLIENT.api is None:
        return []
    if foreground:
        for _ in range(int(max(1.0, float(timeout) * 10))):
            if not _QX_WINDOW_BUSY:
                break
            await asyncio.sleep(0.1)
    _QX_WINDOW_BUSY = True
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, int(end_ts), int(max(60, seconds)), int(tf_sec)),
            timeout=float(timeout))
        return list(res or [])
    except Exception:
        return []
    finally:
        _QX_WINDOW_BUSY = False

async def fetch_older_batch(api, before_ts, batch=300):
    """دفعة أقدم للتمرير للخلف — نداء CLIENT.get_candles الأصلي بمرساة before_ts،
    والدمج في ذاكرة الأصل بلا تقليص (setdefault: القديم الناقص فقط يُضاف)."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    psec = max(1, int(PERIOD_SECONDS))
    batch = max(50, int(batch or 300))
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, int(before_ts), batch * psec, psec), timeout=45.0)
    except Exception:
        return 0
    if not res:
        return 0
    candles = [c for c in res
               if isinstance(c, dict) and int(c.get("time", 0) or 0) < int(before_ts)]
    if not candles:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None:
        return 0
    merged_map = {c["time"]: c for c in asset.candles}
    for c in candles:
        merged_map.setdefault(c["time"], c)
    merged = sorted(merged_map.values(), key=lambda x: x["time"])
    asset.candles = merged[-int(ASSET_MAX_CANDLES):]
    if asset.candles:
        asset.price = asset.candles[-1]["close"]
    asset.mark_dirty()
    return len(candles)

async def qx_get_historical_batches(asset, amount_of_seconds, period, timeout=30,
                                    max_workers=5, batch_callback=None):
    """نفس طريقة الأصل get_historical_candles بكل تفاصيلها (نفس
    CLIENT._fetch_historical_batch الأصلية، نفس chunk=period×FETCH_CHUNK_SIZE،
    نفس عدد العمال max_workers، نفس الرجوع للخلف ونفس قاعدة 3 فشل، نفس
    FETCH_BATCH_DELAY) — الفرق الوحيد: كل دفعة تُسلَّم فور وصولها عبر
    batch_callback(batch, worker_id) ليرفعها التطبيق إلى الشارت حية."""
    if CLIENT is None or CLIENT.api is None:
        return []
    max_workers = max_workers or 1
    chunk_seconds = period * FETCH_CHUNK_SIZE
    all_candles = {}
    current_time = int(time.time())
    target_start_time = current_time - amount_of_seconds
    block_size = max(1, amount_of_seconds // max_workers)
    semaphore = asyncio.Semaphore(max_workers)

    async def worker(start_t, end_t, worker_id):
        worker_candles = {}
        async with semaphore:
            oldest_t = start_t
            consecutive_failures_in_worker = 0
            while oldest_t > end_t:
                if not CLIENT or not getattr(getattr(CLIENT, "api", None), "state", None) \
                        or not getattr(CLIENT.api.state, "check_accepted_connection", False):
                    break
                index = next(_request_counter)
                batch_data = await CLIENT._fetch_historical_batch(
                    asset, oldest_t, chunk_seconds, period, index, timeout)
                if not batch_data:
                    oldest_t -= chunk_seconds
                    consecutive_failures_in_worker += 1
                    if consecutive_failures_in_worker >= 3:
                        break
                    await asyncio.sleep(FETCH_BATCH_DELAY * 2)
                    continue
                consecutive_failures_in_worker = 0
                new_batch = CLIENT._parse_historical_candles(batch_data)
                if not new_batch:
                    oldest_t -= chunk_seconds
                    continue
                batch_times = []
                for c in new_batch:
                    ts = c["time"]
                    if ts >= end_t and ts <= start_t:
                        worker_candles[ts] = c
                        batch_times.append(ts)
                if not batch_times:
                    oldest_t -= chunk_seconds
                    continue
                batch_times.sort()
                new_oldest = batch_times[0]
                if batch_callback:
                    try:
                        batch_callback([worker_candles[t] for t in batch_times], worker_id)
                    except Exception:
                        pass
                oldest_t = new_oldest if new_oldest < oldest_t else oldest_t - chunk_seconds
                await asyncio.sleep(FETCH_BATCH_DELAY)
        return list(worker_candles.values())

    try:
        await CLIENT.start_candles_stream(asset, period)
    except Exception:
        pass
    tasks = []
    for i in range(max_workers):
        s = current_time - (i * block_size)
        e = max(target_start_time, s - block_size)
        tasks.append(worker(s, e, i))
    results = await asyncio.gather(*tasks)
    for batch in results:
        for c in batch:
            all_candles[c["time"]] = c
    return sorted(all_candles.values(), key=lambda x: x["time"])

async def v14_deep_gap_seal(api, reason=""):
    """السد العميق: مرساة عند أقدم شمعة اصطناعية (volume==0) — نداء الجلب
    الأصلي CLIENT.get_candles يعيد شموعاً حقيقية تُستبدل بالشرطات المسطحة داخل
    نافذة محدودة (حتى 200 شمعة) دون لمس الشمعة الحية ولا تقليص الذاكرة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None or len(asset.candles) < 2:
        return 0
    psec = max(1, int(PERIOD_SECONDS))
    cur_start = _align_time(int(time.time()))
    art = [c for c in asset.candles
           if int(c.get("volume", 1) or 0) == 0 and c["time"] < cur_start]
    if not art:
        return 0
    oldest = min(c["time"] for c in art)
    span = max(1, (cur_start - oldest) // psec)
    window = min(200, span + 10)
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, cur_start + psec, window * psec, psec),
            timeout=30.0)
    except Exception:
        return 0
    if not res:
        return 0
    real = {}
    for c in res:
        if isinstance(c, dict) and int(c.get("time", 0) or 0) > 0:
            real[int(c["time"])] = c
    if not real:
        return 0
    merged = []
    for c in asset.candles:
        if c["time"] >= cur_start:
            merged.append(c)                      # الشمعة الحية لا تُلمس
            continue
        r = real.get(c["time"])
        if r is not None and int(c.get("volume", 1) or 0) == 0:
            merged.append(dict(r))
        else:
            merged.append(c)
    have = {c["time"] for c in merged}
    for t, r in real.items():
        if t not in have and t < cur_start:
            merged.append(dict(r))
    merged.sort(key=lambda x: x["time"])
    asset.candles = merged[-int(ASSET_MAX_CANDLES):]
    if asset.candles:
        asset.price = asset.candles[-1]["close"]
    asset.mark_dirty()
    V14_DEEP_REPAIRED[api] = time.time()
    return len(real)

# ═══ 7) التيكات في الذاكرة (فريمات الثواني S5..S30) — الأصل لم يُمَس ═══
_TICK_CACHE = {}
_TICK_QUEUE_MAX = 4096
_TICK_MAX_AGE = 300.0      # 5 دقائق — ذاكرة فقط

async def tick_cache_collector():
    """يلتقط كل تيك يصل (realtime_candles الأصلية — يتحدث عند كل تيك) في ذاكرة
    كل عملة بث حي، بلا أي كتابة على القرص. يبني منه التطبيق فريمات الثواني."""
    while True:
        try:
            if CLIENT is not None and getattr(CLIENT, "api", None) is not None:
                rc = getattr(CLIENT.api, "realtime_candles", {}) or {}
                for sym, tick in list(rc.items()):
                    if not isinstance(tick, (list, tuple)) or len(tick) < 3:
                        continue
                    try:
                        ts, price = int(tick[1]), float(tick[2])
                    except Exception:
                        continue
                    if price <= 0 or ts <= 0:
                        continue
                    q = _TICK_CACHE.get(sym)
                    if q is None:
                        q = _qx_deque(maxlen=_TICK_QUEUE_MAX)
                        _TICK_CACHE[sym] = q
                    if q and q[-1][0] == ts and q[-1][1] == price:
                        continue
                    q.append((ts, price))
        except Exception:
            pass
        await asyncio.sleep(0.05)

async def tick_retention_loop():
    """حذف التيكات الأقدم من 5 دقائق (ذاكرة فقط)."""
    while True:
        try:
            now = time.time()
            for sym, q in list(_TICK_CACHE.items()):
                while q and (now - q[0][0]) > _TICK_MAX_AGE:
                    q.popleft()
                if not q:
                    _TICK_CACHE.pop(sym, None)
        except Exception:
            pass
        await asyncio.sleep(30.0)

async def candlestore_trim_loop():
    """تشذيب candles.db بهدوء: الاحتفاظ بأحدث 5000 شمعة لكل رمز معروف
    + نقطة تحقق WAL كل ساعات — حماية القرص دون أي مساس بالجلب."""
    while True:
        try:
            store = MT4_WRITER.candle_store
            conn = store._get_write_conn()
            try:
                syms = set()
                try:
                    syms.update(str(k) for k in MT4_WRITER._gap_filled.keys())
                except Exception:
                    pass
                for a in list(ALL_STREAMING_ASSETS):
                    try:
                        syms.add(str(a.symbol))
                    except Exception:
                        pass
                for sym in syms:
                    try:
                        conn.execute(
                            "DELETE FROM candles WHERE symbol=? AND time <= "
                            "(SELECT time FROM candles WHERE symbol=? "
                            "ORDER BY time DESC LIMIT 1 OFFSET 5000)",
                            (sym, sym))
                    except Exception:
                        pass
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(6 * 3600.0)

# ═══ 8) علامات تجمّد السد — نفس مخازن الأصل حرفياً ═══
def clear_gap_flag_any(variants):
    """رفع علامة التجمّد عن رمز بأي صيغة تخزين ممكنة (الذاكرة + candles.db)."""
    syms = [str(v or "").strip() for v in (variants or []) if str(v or "").strip()]
    for sym in syms:
        try:
            MT4_WRITER._gap_filled[sym] = False
        except Exception:
            pass
        try:
            MT4_WRITER._gap_filled_at.pop(sym, None)
        except Exception:
            pass
        try:
            MT4_WRITER.candle_store.set_gap_filled(sym, False)
        except Exception:
            pass

def reset_gap_flags():
    """تصفير علامات التجمّد في الذاكرة (نفس مخازن MT4_WRITER الأصلية)."""
    try:
        for sym in list(MT4_WRITER._gap_filled.keys()):
            MT4_WRITER._gap_filled[sym] = False
    except Exception:
        pass
    try:
        MT4_WRITER._gap_filled_at.clear()
    except Exception:
        pass

# ═══ 9) التحميل المسبق المتسلسل — «ضع كل العملات واحدة تلو الأخرى» ═══
async def preload_all_assets():
    """التحميل المسبق المتسلسل لكل العملات المفتوحة **واحدة تلو الأخرى** —
    نفس تدفق الكتلة الرئيسية للأصل حرفياً لكل عملة:
      realtime_stream أولاً (يجمع التيك أثناء الجلب) ← fetch_candles_with_retry
      الأصلية (تاريخ FETCH_DURATION_SECONDS + الجسر + سد الفجوات + HST) ←
      فاصل بين عملة وأخرى.
    فاتحة الشارت أولاً (BRLUSD_otc) ثم بقية العملات المفتوحة من instruments
    بالترتيب. كل عملة تُسجَّل في _PRELOADED_INFO لحالة التحميل في الواجهة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    # اطلب قائمة instruments مرة واحدة (الطريقة الرسمية) وانتظر وصولها باختصار
    try:
        await fetch_instruments_now(timeout=12.0)
    except Exception:
        pass
    try:
        await wait_until(lambda: bool(_instruments_snapshot()),
                         timeout=15.0, poll_interval=0.5)
    except asyncio.TimeoutError:
        pass
    symbols, seen = [], set()
    opener = PRELOAD_FIRST_SYMBOL
    if opener:
        symbols.append(opener)
        seen.add(opener)
    entries = _instruments_snapshot()
    for e in entries:
        sym = str((e or {}).get("asset") or "").strip()
        if not sym or sym in seen:
            continue
        if e.get("open") is False:
            continue        # المغلقة الآن لا بث حي لها — تُحمّل عند فتح شارتها
        symbols.append(sym)
        seen.add(sym)
    if len(symbols) <= 1:
        # fallback: قائمة الأصل الافتراضية ASSET_LIST كما هي
        for sym in list(ASSET_LIST):
            if sym not in seen:
                symbols.append(sym)
                seen.add(sym)
    total = len(symbols)
    logmsg(f"[preload] sequential preload: {total} assets, ONE after another "
           f"(history window {FETCH_DURATION_SECONDS}s each)")
    loaded = 0
    streak = 0
    for idx, sym in enumerate(symbols, 1):
        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            logmsg(f"[preload] connection lost at {idx}/{total}; waiting reconnect…")
            try:
                await wait_until(
                    lambda: CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None,
                    timeout=30.0, poll_interval=0.5)
            except asyncio.TimeoutError:
                streak += 1
                if streak >= MAX_RECONNECTS_DURING_FETCH:
                    logmsg("[preload] giving up after repeated disconnects")
                    break
                continue
        streak = 0
        asset = _get_or_create_asset(sym)
        if asset is None:
            continue
        try:
            st = getattr(asset, "stream_task", None)
            if st is None or (hasattr(st, "done") and st.done()):
                asset.streaming = False
                asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
        except Exception:
            pass
        if len(asset.candles) < MIN_CANDLES_THRESHOLD:
            try:
                n, _att = await fetch_candles_with_retry(
                    asset, max_retries=MAX_FETCH_RETRIES, idx=idx, total=total)
                if n >= MIN_CANDLES_THRESHOLD:
                    loaded += 1
            except Exception as e:
                logmsg(f"[preload] {sym}: {str(e)[:80]}")
        else:
            loaded += 1
        _PRELOADED_INFO[sym] = {"candles": len(asset.candles), "at": time.time()}
        if idx % 10 == 0:
            logmsg(f"[preload] progress: {idx}/{total} assets ({loaded} loaded)")
        # فاصل بين عملة وأخرى — نفس الأصل: واحدة تلو الأخرى بلا تسرّع
        await asyncio.sleep(1.0 if PERIOD_SECONDS < 60 else FETCH_ASSET_DELAY)
    logmsg(f"[preload] done: {loaded}/{total} assets loaded sequentially")
    return loaded

def v14_print_banner():
    try:
        print("[QX] engine = الخادم الأصلي مدمجاً حرفياً + طبقة ربط التطبيق "
              "(منطق الخادم لم يُغيَّر)")
    except Exception:
        pass

def v14_build_background_loops():
    """كل حلقات الأصل الخلفية تعمل أصلاً (health_monitor/auto_reconnect/
    keepalive_loop/stale_message_watchdog/asset_payout_monitor/preload/
    mt4_gap_filler/tick_cache_collector/...) — لا حلقات إضافية هنا."""
    return []

def v14_supervise(name, factory):
    """مشرف مباشر: يُمرّر كوروتين الحلقة كما هو (احتياط — لا يُستدعى حالياً)."""
    async def _sup():
        try:
            coro = factory()
            if coro is not None:
                await coro
        except Exception as e:
            try:
                logmsg(f"[supervise:{name}] {e}")
            except Exception:
                pass
    return _sup()

