#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transform the original QX server code (v9.0) into v10.0:
  1. Flask web dashboard fully removed.
  2. WRITE_HST_FILES_ENABLED = True (HST is now the only output channel).
  3. Geo domain: BD -> market-qx.info, else -> quotex.com (auto, country-level only).
  4. Full asset list + payout % + open/closed status (official pyquotex method:
     42["instruments/get"] -> 451-["instruments/list", [...]]).
  5. Single authority for marking connection dead (anti false-disconnect race).
Nothing else touched: login method, candle fetching (1000 candles), gap bridge,
MT4 writer, timeframes (S5..D1) all remain exactly as they were.
"""
import sys
from pathlib import Path

SRC = Path("/home/z/my-project/upload/Pasted Content_1794506150057.txt")
DST = Path("/home/z/my-project/download/qx_server_v10.py")

lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
orig_count = len(lines)

def L(i):
    """1-based line access (returns the raw line)."""
    return lines[i - 1]

def check(i, expected_sub, desc):
    if expected_sub not in L(i):
        print(f"ANCHOR FAIL at line {i} ({desc}):\n  expected substring: {expected_sub!r}\n  actual: {L(i)!r}")
        sys.exit(1)

# ----------------------------------------------------------------------------
# Phase A: line-range operations, applied BOTTOM-UP (descending start lines)
# ----------------------------------------------------------------------------

def del_range(start, end, verify_first=None, verify_last=None):
    if verify_first:
        check(start, verify_first, f"del {start}-{end} first")
    if verify_last:
        check(end, verify_last, f"del {start}-{end} last")
    del lines[start - 1:end]

def replace_range(start, end, new_text, verify_first=None, verify_last=None):
    if verify_first:
        check(start, verify_first, f"repl {start}-{end} first")
    if verify_last:
        check(end, verify_last, f"repl {start}-{end} last")
    lines[start - 1:end] = [new_text]

# --- a: main() fetch-loop web pushes (bottom-up) ---
del_range(5741, 5744, "try:", "pass")
del_range(5734, 5738, "Push to web dashboard immediately after successful fetch", "pass")
del_range(5719, 5722, "try:", "pass")
del_range(5712, 5716, "Push to web dashboard", "pass")
del_range(5609, 5613, "Push to web dashboard", "pass")
del_range(5514, 5517, "try:", "pass")
del_range(5507, 5511, "Push to web dashboard immediately after successful fetch", "pass")

# --- a: _start_web_server() call in main ---
check(5403, "Start embedded web dashboard", "web server call first")
check(5404, "_start_web_server()", "web server call")
del_range(5403, 5405)

# --- a: STAGE 4 manual domain menu -> automatic geo detection ---
STAGE4_NEW = '''    # ════════════════════════════════════════════════════════════════════
    # STAGE 4: Domain — التعرف التلقائي على البلد عبر IP (بدون قائمة يدوية)
    #   بنغلاديش (BD)   -> market-qx.info   (نطاق بنغلاديش)
    #   أي دولة أخرى    -> quotex.com       (النطاق الرسمي العالمي)
    # يتم التعرف على "البلد فقط" وليس الموقع الدقيق.
    # ════════════════════════════════════════════════════════════════════
    print()
    print(f"{Colors.BOLD}  Domain: detecting country automatically ...{Colors.RESET}")
    resolve_qx_host()
    globals()['QX_HOST'] = QX_HOST
    _geo_country = _GEO_CACHE.get("country") or "unknown"
    print(f"{Colors.GREEN}  Country: {_geo_country}  ->  Domain: {QX_HOST}{Colors.RESET}\\n")
'''
check(5338, "STAGE 4", "STAGE 4 header")
replace_range(5337, 5367, STAGE4_NEW, None, "Using domain:")

# --- a: web server section + web_candle_refresher + print_dashboard (one big cut) ---
del_range(4364, 5121,
          "WEB_PUSH_INTERVAL = 30",
          "")  # 5121 is blank; verify line 5122 separately below
if not L(4364).startswith("if __name__"):
    # after deletion of 4364-5121, the line that follows (old 5122) shifted into 4364
    pass
# sanity: the first line right after the cut must be the main guard
# (old line 5122 'if __name__...' shifted to position 4364 after deleting 758 lines)
if not L(4364).startswith("if __name__"):
    print(f"ANCHOR FAIL: line after big cut is not 'if __name__': {L(4364)!r}")
    sys.exit(1)

# --- a: realtime_stream web push block ---
del_range(3382, 3390, "v9.0: Update web dashboard on every live tick", "pass")
check(3382, "asset.mark_dirty", "realtime_stream trailing comment")

# --- a: WriterThread web pushes ---
replace_range(2156, 2163,
'''                    if asset.dirty and (now - asset.last_write >= WRITE_INTERVAL):
                        if asset.write():
                            dirty_count += 1
''',
              "if asset.dirty and (now - asset.last_write >= WRITE_INTERVAL):", "pass")
replace_range(2149, 2155,
'''                    if asset.symbol in MT4_WRITER.sync_state:
                        continue
''',
              "if asset.symbol in MT4_WRITER.sync_state:", "continue")

# --- a: DOMAINS block -> geo detection + mark_connection_dead + payout module ---
GEO_BLOCK = '''# ==============================================================================
# ===== GEO DOMAIN (التعرف التلقائي على البلد عبر IP) — v10.0 =====
# ==============================================================================
# القاعدة (طلب المستخدم):
#   بنغلاديش (BD)  -> market-qx.info   (نطاق بنغلاديش)
#   أي دولة أخرى   -> quotex.com       (النطاق الرسمي العالمي)
# يتم التعرف على "البلد فقط" (وليس الموقع الدقيق) عبر IP عند كل تشغيل.
DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
DEFAULT_DOMAIN_GLOBAL = "quotex.com"
QX_HOST = DEFAULT_DOMAIN_GLOBAL
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

# ==============================================================================
# ===== SINGLE AUTHORITY FOR CONNECTION DEATH (منع الانقطاعات الوهمية) =====
# ==============================================================================
# المشكلة السابقة: on_error و on_close و stale_message_watchdog و health_monitor
# كانوا يكتبون CONNECTION_ALIVE = False كلٌّ على حدة (سباق حالة + سجلات مكررة +
# كتابة مكررة لـ LAST_CONNECTION_DROP_TIME). الآن كل الطرق تمر من هنا وحدها.
_CONN_DEATH_LOCK = threading.Lock()

def mark_connection_dead(source: str):
    """السلطة الوحيدة للإعلان عن موت الاتصال: تكتب العلم تحت قفل، تسقط وقت
    الانقطاع مرة واحدة فقط، وتسجل مصدر الإعلان."""
    global CONNECTION_ALIVE, LAST_CONNECTION_DROP_TIME
    was_alive = True
    try:
        with _CONN_DEATH_LOCK:
            was_alive = CONNECTION_ALIVE
            CONNECTION_ALIVE = False
            if LAST_CONNECTION_DROP_TIME == 0:
                LAST_CONNECTION_DROP_TIME = time.time()
    except Exception:
        pass
    if was_alive:
        try:
            logmsg(f"[connection] marked DEAD by {source}")
        except Exception:
            pass

# ==============================================================================
# ===== FULL ASSET LIST + PAYOUT % + OPEN/CLOSED (طريقة pyquotex الرسمية) =====
# ==============================================================================
# الطريقة الرسمية من مستودع pyquotex (cleitonleonel/pyquotex):
#   1) الإرسال عبر نفس WebSocket:  42["instruments/get"]
#   2) الرد يصل بصيغة:             451-["instruments/list", [ ... ]]
#   3) كل عنصر في القائمة يحتوي:
#        i[1]  = اسم الأصل (EURUSD_otc)     i[2]  = الاسم المعروض
#        i[5]  = نسبة الدفع payout %        i[14] = الحالة (True=مفتوح / False=مغلق)
#        i[18] = نسبة دفع التيربو turbo     i[-10],i[-9],i[-8] = أرباح 24H/1M/5M
PAYOUT_REFRESH_INTERVAL = 60
try:
    ASSETS_PAYOUT_FILE = Path(__file__).resolve().parent / "qx_assets_payouts.json"
except Exception:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")

def _instruments_snapshot():
    """يبني قائمة الأصول الكاملة (الاسم + نسبة الدفع + الحالة) من instruments."""
    if CLIENT is None or CLIENT.api is None:
        return []
    insts = CLIENT.api.instruments or []
    out = []
    for i in insts:
        try:
            if not isinstance(i, (list, tuple)) or len(i) < 6:
                continue
            entry = {
                "asset": str(i[1]) if len(i) > 1 else "",
                "name": str(i[2]).replace("\\n", " ").strip() if len(i) > 2 else "",
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
            # أرباح الفريمات (طريقة get_payment الرسمية): -10=24H ، -9=1M ، -8=5M
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
        # الرد كان placeholder — ننتظر الرد الحقيقي (نفس سلوك المكتبة الرسمية)
        data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=5.0)
    if isinstance(data, list) and data:
        CLIENT.api.instruments = data
    return list(CLIENT.api.instruments or [])

def _print_payout_table(entries):
    """طباعة الجدول الكامل: العملة / نسبة الدفع / الحالة (مفتوح أو مغلق)."""
    open_entries = [e for e in entries if e.get("open")]
    closed_entries = [e for e in entries if e.get("open") is False]
    print(f"\\n{Colors.CYAN}{'═' * 72}{Colors.RESET}")
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
    print(f"{Colors.DIM}  Full snapshot saved to: {ASSETS_PAYOUT_FILE}{Colors.RESET}\\n")

async def asset_payout_monitor():
    """يجلب قائمة العملات الكاملة + نسبة الدفع + حالة الزوج (مفتوح/مغلق) مباشرة
    بعد تسجيل الدخول، يطبع الجدول مرة واحدة، يحفظ لقطة JSON، ثم يحدّث بهدوء
    كل PAYOUT_REFRESH_INTERVAL ثانية."""
    await asyncio.sleep(2.0)  # مهلة قصيرة حتى يستقر WebSocket بعد الدخول
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
                    _print_payout_table(entries)
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
'''
replace_range(1904, 1912, GEO_BLOCK, "FIX K: Quotex", 'QX_HOST = "qxbroker.com"')

# --- a: WRITE_HST_FILES_ENABLED back on (Flask removed => HST is the only output) ---
replace_range(1718, 1722,
'''# v10.0: Flask web dashboard REMOVED — MT4 .hst files are the ONLY output channel.
# WRITE_HST_FILES_ENABLED must stay True, otherwise the server produces no output.
WRITE_HST_FILES_ENABLED = True
''',
              "WRITE_HST_FILES_ENABLED = False", "WRITE_HST_FILES_ENABLED = False")

# --- a: Flask import block removed ---
check(48, "WEB SERVER IMPORTS", "flask import header")
check(52, "HAS_FLASK = True", "flask import try")
check(54, "HAS_FLASK = False", "flask import except")
replace_range(47, 54, None or '''# ==============================================================================
# NOTE: Flask web dashboard REMOVED (v10.0) — replaced by console output +
# MT4 .hst files + qx_assets_payouts.json. No web server in this build.
# ==============================================================================
''')

# ----------------------------------------------------------------------------
# Phase B: exact-string replacements (unique anchors)
# ----------------------------------------------------------------------------

def repl(old, new, desc):
    text = "".join(lines)
    n = text.count(old)
    if n != 1:
        print(f"REPL FAIL ({desc}): found {n} occurrences of anchor:\n{old[:200]!r}")
        sys.exit(1)
    text = text.replace(old, new, 1)
    lines[:] = text.splitlines(keepends=True)

# B1: instruments/list handler in WebsocketClient.on_message
repl('''                self.state.signal_auth_accepted()

            message = None
''',
     '''                self.state.signal_auth_accepted()

            # ===== INSTRUMENTS LIST (طريقة pyquotex الرسمية) =====
            # الرد على 42["instruments/get"] يصل بصيغة 451-["instruments/list",[...]]
            # — نلتقطه، نخزنه في self.api.instruments ونوقظ كل من ينتظر instruments_ready.
            if "instruments/list" in msg_str:
                try:
                    _idx = msg_str.find('["')
                    if _idx != -1:
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

            message = None
''', "B1 instruments handler")

# B2: Quotex.get_all_assets stub -> real official methods
repl('''    async def get_all_assets(self):
        return {}
''',
     '''    async def get_instruments(self, timeout: float = 12.0):
        """طريقة pyquotex الرسمية: طلب قائمة instruments الكاملة عبر WebSocket
        والانتظار حتى وصولها (event: instruments_ready)."""
        if self.api is None:
            return []
        if self.api.instruments and len(self.api.instruments) > 0:
            return self.api.instruments
        try:
            await self.api.event_registry.clear_event("instruments_ready")
        except Exception:
            pass
        try:
            self.api.send_websocket_request('42["instruments/get"]')
        except Exception as e:
            logmsg(f"[instruments] request failed: {e}")
            return []
        data = await self.api.event_registry.wait_event("instruments_ready", timeout=timeout)
        if isinstance(data, dict) and data.get("_placeholder"):
            data = await self.api.event_registry.wait_event("instruments_ready", timeout=5.0)
        if isinstance(data, list) and data:
            self.api.instruments = data
        return list(self.api.instruments or [])

    async def get_all_assets(self):
        """طريقة pyquotex الرسمية: خريطة اسم الأصل -> كوده الداخلي."""
        if self.api is None:
            return {}
        try:
            await self.get_instruments()
        except Exception:
            pass
        for i in (self.api.instruments or []):
            try:
                if isinstance(i, (list, tuple)) and i[0] != "":
                    self.codes_asset[i[1]] = i[0]
            except Exception:
                continue
        return self.codes_asset

    def get_payment(self):
        """طريقة pyquotex الرسمية get_payment: نسبة الدفع + الحالة لكل الأصول."""
        if self.api is None or not self.api.instruments:
            return {}
        assets_data = {}
        for i in self.api.instruments:
            try:
                assets_data[str(i[2]).replace("\\n", "")] = {
                    "turbo_payment": i[18],
                    "payment": i[5],
                    "profit": {"24H": i[-10], "1M": i[-9], "5M": i[-8]},
                    "open": i[14],
                }
            except Exception:
                continue
        return assets_data

    def get_payout_by_asset(self, asset_name: str, timeframe: str = "1"):
        """طريقة pyquotex الرسمية get_payout_by_asset: نسبة الدفع لأصل محدد.
        timeframe: "1" (1M) أو "5" (5M) أو "24" (24H) أو "all"."""
        if self.api is None or not self.api.instruments:
            return None
        data = None
        for i in self.api.instruments:
            try:
                if isinstance(i, (list, tuple)) and len(i) > 1 and asset_name == i[1]:
                    data = {
                        "turbo_payment": i[18] if len(i) > 18 else None,
                        "payment": i[5] if len(i) > 5 else None,
                        "profit": {"24H": i[-10], "1M": i[-9], "5M": i[-8]},
                        "open": i[14] if len(i) > 14 else None,
                    }
                    break
            except Exception:
                continue
        if data is None:
            return None
        if timeframe == "all":
            return data.get("profit")
        profit = data.get("profit")
        if profit:
            if str(timeframe) == "24":
                return profit.get("24H")
            return profit.get(f"{timeframe}M")
        return None
''', "B2 official asset methods")

# B3: on_error -> mark_connection_dead
repl('''        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_error()
        try:
            CONNECTION_ALIVE = False
        except Exception:
            pass
''',
     '''        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_error()
        mark_connection_dead(f"ws_error: {str(error)[:80]}")
''', "B3 on_error")

# B4: on_close -> mark_connection_dead
repl('''        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_closed()
        try:
            CONNECTION_ALIVE = False
        except Exception:
            pass
''',
     '''        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_closed()
        mark_connection_dead("ws_closed")
''', "B4 on_close")

# B5: async engine restart
repl('''            if gen > 1:
                logmsg(f"[AsyncEngine] event loop recreated (gen {gen}). Rescheduling tasks...")
                CONNECTION_ALIVE = False
''',
     '''            if gen > 1:
                logmsg(f"[AsyncEngine] event loop recreated (gen {gen}). Rescheduling tasks...")
                mark_connection_dead(f"async engine restart (gen {gen})")
''', "B5 engine restart")

# B6: async engine crash
repl('''        except Exception as e:
            log_exception(f"AsyncEngine (gen {ASYNC_ENGINE_GENERATION})", e)
            CONNECTION_ALIVE = False
            time.sleep(1)
''',
     '''        except Exception as e:
            log_exception(f"AsyncEngine (gen {ASYNC_ENGINE_GENERATION})", e)
            mark_connection_dead("async engine crash")
            time.sleep(1)
''', "B6 engine crash")

# B7: stale watchdog -> single authority
repl('''                if LAST_CONNECTION_DROP_TIME == 0:
                    LAST_CONNECTION_DROP_TIME = time.time()
                    logmsg(f"[stale_watchdog] drop time recorded at {LAST_CONNECTION_DROP_TIME:.0f}")
                CONNECTION_ALIVE = False
''',
     '''                mark_connection_dead(f"stale_watchdog: silent {silent_for:.1f}s > {STALE_MESSAGE_TIMEOUT}s")
''', "B7 stale watchdog")

# B8: health monitor -> single authority
repl('''        if is_dead:
            logmsg(f"[health_monitor] marking connection DEAD: {dead_reason}")
            CONNECTION_ALIVE = False
            consecutive_dead_checks = 0
''',
     '''        if is_dead:
            mark_connection_dead(f"health_monitor: {dead_reason}")
            consecutive_dead_checks = 0
''', "B8 health monitor")

# B9: auto_reconnect saved-host override removed (geo is authoritative)
repl('''            # FIX K:
            _saved_host = session_manager.get_saved_host()
            if _saved_host and QX_HOST != _saved_host:
                QX_HOST = _saved_host
                logmsg(f"[reconnect] using saved host: {QX_HOST}")
''',
     '''            # GEO-DOMAIN (v10.0): QX_HOST تم تحديده تلقائياً عند التشغيل من البلد
            # (بنغلاديش -> market-qx.info ، غير ذلك -> quotex.com).
            # لم نعد نتجاوزه بالنطاق المحفوظ القديم حتى لا يخالف قاعدة التعرف الجغرافي.
''', "B9 saved-host override")

# B10: connect_quotex final failure
repl('''            if attempt < max_attempts: await asyncio.sleep(5 * attempt)
    CONNECTION_ALIVE = False
    return False
''',
     '''            if attempt < max_attempts: await asyncio.sleep(5 * attempt)
    mark_connection_dead("connect_quotex: all attempts failed")
    return False
''', "B10 connect_quotex")

# B11: schedule the payout monitor with the other watchdogs in main()
repl('''    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
''',
     '''    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # ===== ASSETS / PAYOUT / OPEN-CLOSED MONITOR (طريقة pyquotex الرسمية) =====
    asyncio.run_coroutine_threadsafe(asset_payout_monitor(), ASYNC_LOOP)
''', "B11 payout monitor scheduling")

# B12: banner prints
repl('''    print(f"  HST Files: {'ENABLED (every %ss)' % WRITE_INTERVAL if WRITE_HST_FILES_ENABLED else 'DISABLED — web dashboard only'}")
''',
     '''    print(f"  HST Files: {'ENABLED (every %ss)' % WRITE_INTERVAL if WRITE_HST_FILES_ENABLED else 'DISABLED'}")
''', "B12 HST banner")

repl('''    print(f"  {Colors.CYAN}Web Updates: LIVE per-tick (no background refetch){Colors.RESET}")
''',
     '''    print(f"  {Colors.CYAN}Payout Monitor: full asset list + payout % + open/closed (refresh every {PAYOUT_REFRESH_INTERVAL}s){Colors.RESET}")
''', "B12 payout banner")

# B13: comments
repl('''        # v9.0: skip HST writing entirely when WRITE_HST_FILES_ENABLED is False.
        # The web dashboard (Flask) is the only output channel.
''',
     '''        # v10.0: skip HST writing entirely when WRITE_HST_FILES_ENABLED is False.
        # HST files are now the ONLY output channel (Flask dashboard removed).
''', "B13 asset.write comment")

repl('''        # The web dashboard (Flask) is now the ONLY output — no disk writes.
''',
     '''        # HST files are the ONLY output (Flask dashboard removed) — no web writes.
''', "B13 mt4writer comment")

# ----------------------------------------------------------------------------
# Finalize
# ----------------------------------------------------------------------------
text = "".join(lines)
DST.write_text(text, encoding="utf-8")
print(f"OK: wrote {DST}  ({orig_count} -> {len(text.splitlines())} lines)")
