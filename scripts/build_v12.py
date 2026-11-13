#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني qx_server_v12.py من qx_server_v10.py:

1) نزع واجهة FastAPI/HTML بالكامل (طلب المستخدم: العرض في الترمينال).
2) إصلاح جلب قائمة العملات: الخادم يرد على مرحلتين (451- placeholder ثم
   إطار منفصل يحمل البيانات) — السابق كان يعالج الصيغة المضمّنة فقط،
   ولذلك كانت القائمة تظهر فارغة أبداً.
3) جدول العملات الكامل يُطبع في الترمينال (المرة الأولى فوراً، ثم عند أي تغيير).
4) طريقة الدخول وجلب 1000 شمعة كما هي دون أي تغيير (المحرك موجود ولا يُشغَّل تلقائياً).
"""
import py_compile
from pathlib import Path

SRC = Path('/home/z/my-project/download/qx_server_v10.py')
DST = Path('/home/z/my-project/download/qx_server_v12.py')

src = SRC.read_text(encoding='utf-8')

# ── 1) ملاحظة الرأس ───────────────────────────────────────────────────────────
old_note = """# NOTE: Flask web dashboard REMOVED (v10.0) — replaced by console output +
# MT4 .hst files + qx_assets_payouts.json. No web server in this build."""
new_note = """# NOTE (v12.0): Terminal Asset Monitor — no web interface at all (FastAPI/HTML
# removed per user request). Console asks ONLY email + password (login method
# untouched), then prints the FULL asset list (payout % + open/closed) in the
# terminal and re-prints it on any change.
# v12 FIX: the server answers instruments/get in TWO stages (451- placeholder
# then a separate frame carrying the actual JSON list). The previous build only
# handled the inline format, so the asset list never got stored (empty table).
# The candle engine (1000-candle fetch) stays in the file UNCHANGED but is not
# auto-started (the program never asks for an asset, per user spec)."""
assert old_note in src, 'header note not found'
src = src.replace(old_note, new_note)

# ── 2) إصلاح on_message: مرحلتا الرد (placeholder + الإطار المنفصل) ─────────
old_instruments = '''            # ===== INSTRUMENTS LIST (طريقة pyquotex الرسمية) =====
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
'''
new_instruments = '''            # ===== INSTRUMENTS LIST (طريقة pyquotex الرسمية — على مرحلتين) =====
            # الرد على 42["instruments/get"] يصل كما يلي (نفس سلوك المكتبة الرسمية):
            #   المرحلة 1: 451-["instruments/list",{...,"_placeholder":true,"num":0}]
            #              (رسالة تحكم تحمل placeholder فقط — بلا بيانات)
            #   المرحلة 2: إطار منفصل (غالباً binary) يحتوي JSON القائمة الفعلية
            # v12 FIX: السابق كان يعالج الصيغة المضمّنة فقط (451- مع القائمة داخلها)،
            # ولذلك عندما يرد الخادم بأسلوب placeholder + إطار منفصل لم تُخزن القائمة
            # أبداً وكانت تظهر فارغة. الآن نطبّق المسارين معاً.
            if "instruments/list" in msg_str and "_placeholder" in msg_str:
                # المرحلة 1: نتذكر أننا ننتظر الإطار التالي الذي يحمل البيانات الفعلية
                try:
                    self.api._temp_status = msg_str
                except Exception:
                    pass
                self.state.ssl_Mutual_exclusion = False
                return

            if "instruments/list" in msg_str:
                # الصيغة المضمّنة (القائمة كاملة داخل نفس الرسالة) — خطة بديلة
                try:
                    _idx = msg_str.find('["')
                    if _idx != -1:
                        _payload = json.loads(msg_str[_idx:])
                        _data = _payload[1] if isinstance(_payload, list) and len(_payload) >= 2 else None
                        if isinstance(_data, dict) and "list" in _data:
                            _data = _data["list"]
                        if isinstance(_data, list) and _data:
                            self.api.instruments = _data
                            try:
                                self.api._temp_status = ""
                            except Exception:
                                pass
                            _loop = getattr(self.api, "_async_loop", None)
                            if _loop is not None and _loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    self.api.event_registry.set_event("instruments_ready", _data),
                                    _loop,
                                )
                            logger.info(f"Instruments list received: {len(_data)} assets")
                except Exception as _e:
                    logger.debug(f"instruments/list parse error: {_e}")

            # المرحلة 2: تسليم القائمة الفعلية بعد placeholder (نفس سلوك المكتبة الرسمية)
            try:
                if self.api._temp_status and "instruments/list" in self.api._temp_status:
                    _first_char = msg_str[0] if msg_str else ""
                    if _first_char and not _first_char.isdigit():
                        _sidx = -1
                        for _ci, _cc in enumerate(msg_str):
                            if _cc in ("[", "{"):
                                _sidx = _ci
                                break
                        if _sidx != -1:
                            _payload = json.loads(msg_str[_sidx:])
                            if (isinstance(_payload, list) and len(_payload) == 1
                                    and isinstance(_payload[0], (list, dict))):
                                _payload = _payload[0]
                            if isinstance(_payload, dict) and "list" in _payload:
                                _payload = _payload["list"]
                            if isinstance(_payload, list) and _payload:
                                self.api.instruments = _payload
                                self.api._temp_status = ""
                                _loop = getattr(self.api, "_async_loop", None)
                                if _loop is not None and _loop.is_running():
                                    asyncio.run_coroutine_threadsafe(
                                        self.api.event_registry.set_event("instruments_ready", _payload),
                                        _loop,
                                    )
                                logger.info(f"Instruments list received: {len(_payload)} assets")
            except Exception as _e:
                logger.debug(f"instruments payload fulfillment error: {_e}")
'''
assert src.count(old_instruments) == 1, 'instruments block not found'
src = src.replace(old_instruments, new_instruments)

# ── 3) جدول الطباعة: عمود الاسم + وقت التحديث + ترتيب المفتوحة أولاً ────────
old_table = '''def _print_payout_table(entries):
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
'''
new_table = '''def _print_payout_table(entries, updated_at=None):
    """طباعة الجدول الكامل في الترمينال: العملة / الاسم / الدفع / الحالة.
    v12 (طلب المستخدم: العرض في الترمينال): يُعاد رسم الجدول عند أي تغيير،
    والترتيب: المفتوحة أولاً ثم حسب نسبة الدفع الأعلى."""
    open_entries = [e for e in entries if e.get("open")]
    closed_entries = [e for e in entries if e.get("open") is False]

    def _payout_val(e):
        p = e.get("payout")
        return p if isinstance(p, (int, float)) else -1

    entries_sorted = sorted(
        entries,
        key=lambda e: (0 if e.get("open") else 1, -_payout_val(e)),
    )
    print(f"\\n{Colors.CYAN}{'═' * 92}{Colors.RESET}")
    print(f"{Colors.BOLD}  FULL ASSET LIST — PAYOUT % — OPEN/CLOSED{Colors.RESET}")
    _updated_str = f"  |  Updated: {updated_at}" if updated_at else ""
    print(f"  Total: {len(entries)}  |  {Colors.GREEN}OPEN: {len(open_entries)}{Colors.RESET}"
          f"  |  {Colors.RED}CLOSED: {len(closed_entries)}{Colors.RESET}"
          f"  |  Domain: {QX_HOST}{_updated_str}")
    print(f"{Colors.CYAN}{'─' * 92}{Colors.RESET}")
    print(f"  {'ASSET':<16}{'NAME':<20}{'PAYOUT':>7}  {'TURBO':>6}  {'1M':>5}  {'5M':>5}  STATUS")
    print(f"{Colors.DIM}{'─' * 92}{Colors.RESET}")
    for e in entries_sorted:
        name = (e.get("asset") or "?")[:16]
        dname = ((e.get("name") or "").replace("\\n", " ").strip() or "-")[:20]
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
        print(f"  {name:<16}{dname:<20}{payout_str:>7}  {turbo_str:>6}  {p1_str:>5}  {p5_str:>5}  {status}")
    print(f"{Colors.CYAN}{'═' * 92}{Colors.RESET}")
    print(f"{Colors.DIM}  Full snapshot saved to: {ASSETS_PAYOUT_FILE}{Colors.RESET}\\n")
'''
assert src.count(old_table) == 1, 'payout table not found'
src = src.replace(old_table, new_table)

# ── 4) مراقب الجلب: إعادة محاولة + إعادة رسم الجدول عند أي تغيير ────────────
old_monitor = '''async def asset_payout_monitor():
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
new_monitor = '''async def asset_payout_monitor():
    """يجلب قائمة العملات الكاملة + نسبة الدفع + حالة الزوج (مفتوح/مغلق) بعد
    تسجيل الدخول، يطبع الجدول الكامل في الترمينال فوراً، يحفظ لقطة JSON، ثم
    يعيد طباعة الجدول في الترمينال عند أي تغيير (كل PAYOUT_REFRESH_INTERVAL ثانية).
    v12: يعيد المحاولة حتى 3 مرات قبل الانتظار للدورة التالية."""
    await asyncio.sleep(1.5)  # مهلة قصيرة حتى يستقر WebSocket بعد الدخول
    first = True
    last_signature = None
    while True:
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = []
            # v12: حتى 3 محاولات قبل الانتظار للدورة التالية
            for _attempt in range(1, 4):
                try:
                    await fetch_instruments_now(timeout=12.0)
                    entries = _instruments_snapshot()
                except Exception as e:
                    logmsg(f"[payout] refresh failed: {e}")
                if entries:
                    break
                logmsg(f"[payout] attempt {_attempt}: empty list, retrying...")
                await asyncio.sleep(3.0)
            if entries:
                _save_assets_payout_file(entries)
                _updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                signature = tuple(sorted(
                    (e.get("asset"), str(e.get("payout")), str(e.get("open")))
                    for e in entries))
                if first:
                    _print_payout_table(entries, updated_at=_updated_at)
                    first = False
                elif signature != last_signature:
                    # v12 (طلب المستخدم): العرض في الترمينال — إعادة رسم الجدول عند أي تغيير
                    _print_payout_table(entries, updated_at=_updated_at)
                    open_n = sum(1 for e in entries if e.get("open"))
                    closed_n = sum(1 for e in entries if e.get("open") is False)
                    logmsg(f"[payout] updated: {len(entries)} assets "
                           f"({open_n} open / {closed_n} closed) — snapshot saved")
                last_signature = signature
            else:
                logmsg("[payout] no instruments response from server — will retry next cycle")
        except Exception as e:
            log_exception("asset_payout_monitor", e)
        await asyncio.sleep(PAYOUT_REFRESH_INTERVAL)
'''
assert src.count(old_monitor) == 1, 'payout monitor not found'
src = src.replace(old_monitor, new_monitor)

# ── 5) استبدال كتلة __main__ بالكامل (تدفق ترمنال فقط، بدون أي واجهة ويب) ───
marker = 'if __name__ == "__main__":'
idx = src.index(marker)
src_head = src[:idx]

NEW_TAIL = '''if __name__ == "__main__":
    # ════════════════════════════════════════════════════════════════════
    # v12.0 — Terminal Asset Monitor (بطلب المستخدم):
    #   - لا توجد واجهة HTML إطلاقاً (FastAPI/HTML أُزيلت بالكامل).
    #   - عند التشغيل يسأل فقط عن البريد وكلمة المرور.
    #   - بعد الدخول يجلب قائمة العملات الكاملة (الدفع + مفتوح/مغلق) ويطبعها
    #     في الترمينال، ويعيد طباعتها عند أي تغيير.
    #   - إصلاح جلب القائمة: الخادم يرد على مرحلتين (placeholder ثم إطار
    #     منفصل) — السابق كان يعالج الصيغة المضمّنة فقط.
    #   - طريقة الدخول وجلب 1000 شمعة كما هي دون أي تغيير (المحرك موجود
    #     في الملف ولا يُشغَّل تلقائياً لأن البرنامج لا يسأل عن أي عملة).
    # ════════════════════════════════════════════════════════════════════
    print()
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  QX SERVER v12.0 — Terminal Asset Monitor{Colors.RESET}")
    print(f"  {Colors.DIM}الدخول ثم عرض قائمة العملات والدفع والحالة في الترمينال{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")

    # v12: لا يوجد جدول حي في هذه النسخة — اطبع رسائل السجل مباشرة
    globals()['_STATUS_MESSAGES_QUEUE'] = None

    # ---- STAGE 1: النطاق تلقائياً حسب البلد (بدون أي سؤال) ----
    print()
    print(f"{Colors.BOLD}  Domain: detecting country automatically ...{Colors.RESET}")
    resolve_qx_host()
    globals()['QX_HOST'] = QX_HOST
    _geo_country = _GEO_CACHE.get("country") or "unknown"
    print(f"{Colors.GREEN}  Country: {_geo_country}  ->  Domain: {QX_HOST}{Colors.RESET}")

    # ---- STAGE 2: تسجيل الدخول — البريد وكلمة المرور فقط ----
    # نفس كود v10/v11 حرفياً (حفظ الجلسة + connect_quotex + نفس المهلات).
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

    # ---- STAGE 3: مراقبة الاتصال + جلب قائمة العملات (حلقات v10 دون تغيير) ----
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass
    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # جلب قائمة العملات الكاملة + الدفع + الحالة وطباعتها في الترمينال:
    # المرة الأولى فوراً، ثم إعادة الطباعة عند أي تغيير كل 60 ثانية.
    asyncio.run_coroutine_threadsafe(asset_payout_monitor(), ASYNC_LOOP)

    print()
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  Connected! Full asset list will be printed here shortly ...{Colors.RESET}")
    print(f"  {Colors.DIM}القائمة الكاملة (الدفع + مفتوح/مغلق) تظهر خلال ثوانٍ{Colors.RESET}")
    print(f"  {Colors.DIM}وتُعاد طباعتها تلقائياً عند أي تغيير (كل {PAYOUT_REFRESH_INTERVAL} ثانية){Colors.RESET}")
    print(f"  {Colors.DIM}لقطة JSON تُحفظ في: qx_assets_payouts.json{Colors.RESET}")
    print(f"  {Colors.DIM}للخروج: Ctrl+C{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")

    try:
        # v12: الخيط الرئيسي يبقى حيّاً فقط — كل العمل في حلقات الخلفية
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print(f"{Colors.RED}Stopped{Colors.RESET}")
        writer_thread.running = False
'''

DST.write_text(src_head + NEW_TAIL, encoding='utf-8')
py_compile.compile(str(DST), doraise=True)
print('OK: wrote', DST)
