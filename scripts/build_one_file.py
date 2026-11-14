# -*- coding: utf-8 -*-
"""
build_one_file.py — يبني ملفاً واحداً BadiChartsStudio_live.py:
  1) يرقّع نسخة المحرك qx_server_v14.py بالإصلاحات الثمانية من تقرير الفحص
     (قائمة انتظار التيكات + الرد الفارغ يرفع الحدث + فهرس طلب فريد بلا
     إعادة اشتراك + علامة تجميد صادقة + نافذة سد حتى أقدم شمعة اصطناعية
     + الدفعة القصيرة لا تمحو الذاكرة).
  2) يدمج المحرك المرقّع داخل BadiChartsStudio_live.py كنص خام
     `_QX_ENGINE_SOURCE = r'''...'''` (المحرك لا يحتوي ''' إطلاقاً — تحقق).
  3) يعيد كتابة _qx_module ليُنفّذ المحرك المدمج — التطبيق لا يحمّل أي
     ملف ثانٍ (طلب المستخدم: «يجب ان يكون كود واحد وليس يحمل كود ثاني»).
كل رقعة لها مرساة واحدة فريدة مع تحقق صارم — أي مرساة مفقودة/مكررة = فشل فوري.
"""
import sys, io, re

BASE = "/home/z/my-project/download"
ENGINE_IN = BASE + "/qx_server_v14.py"
APP_IN = BASE + "/BadiChartsStudio_live.py"
APP_OUT = BASE + "/BadiChartsStudio_live.py"
ENGINE_TMP = "/tmp/qx_engine_patched.py"


def patch(text, anchor, repl, name, count=1):
    n = text.count(anchor)
    if n != count:
        raise SystemExit(f"[FAIL] anchor '{name}' found {n} times (expected {count})")
    out = text.replace(anchor, repl, count)
    print(f"[ok] {name}")
    return out


# ═══════════════════════════════════════════════════════════════════
# الجزء 1 — رقع المحرك
# ═══════════════════════════════════════════════════════════════════
eng = io.open(ENGINE_IN, encoding="utf-8").read()
assert "'''" not in eng, "engine contains ''' — cannot embed as r''' raw string"

# --- P0: استيراد deque ---
eng = patch(
    eng,
    "from collections import OrderedDict, defaultdict",
    "from collections import OrderedDict, defaultdict, deque as _v14_deque",
    "P0 deque import",
)

# --- P0b: تهيئة قائمة انتظار التيكات في __init__ للم_api ---
eng = patch(
    eng,
    "        self._history_pending: Dict[str, tuple] = {}",
    """        self._history_pending: Dict[str, tuple] = {}
        # v14.8 (تقرير الفحص): قائمة انتظار التيكات لكل عملة — كل تيك يُحفظ
        # ويُعالَج، والتيكات بين قراءتين لا تضيع فتبقى قمم الشموع وقيعانها.
        self._tick_queue: Dict[str, _v14_deque] = {}
        self._tick_last_done: Dict[str, tuple] = {}""",
    "P0b tick queue init",
)

# --- P1+P2: كل تيكات الرسالة تُحفظ في قائمة الانتظار ---
eng = patch(
    eng,
    """            if isinstance(message, list) and len(message) > 0 and isinstance(message[0], list) and len(message[0]) == 4:
                asset = message[0][0]
                self.api.realtime_candles[asset] = message[0]""",
    """            if isinstance(message, list) and len(message) > 0 and isinstance(message[0], list) and len(message[0]) == 4:
                asset = message[0][0]
                self.api.realtime_candles[asset] = message[0]
                # v14.8 (تقرير الفحص — سبب «أجسام الشموع صغيرة وقممها تضيع»):
                # كل تيكات الرسالة تُحفظ في قائمة انتظار لكل عملة — التيكات
                # التي تصل بين قراءتين لا تضيع بعد الآن والبث يقرؤها كلها
                # (الشرط القديم message[0] كان يتجاهل بقية التيكات).
                try:
                    _tq = self.api._tick_queue.setdefault(asset, _v14_deque(maxlen=4096))
                    for _tk in message:
                        if isinstance(_tk, list) and len(_tk) == 4:
                            _tq.append(_tk)
                except Exception:
                    pass""",
    "P1/P2 all ticks queued",
)

# --- P3a: الرد الفارغ يرفع الحدث ---
eng = patch(
    eng,
    """            if isinstance(message, dict):
                asset = message.get("asset")
                if asset and (message.get("candles") or message.get("data") or message.get("history")):
                    self.api.candle_v2_data[asset] = message
                    self.api.candles.candles_data = message.get("candles") or message.get("data") or message.get("history")""",
    """            if isinstance(message, dict):
                asset = message.get("asset")
                # v14.8 (تقرير الفحص): الرد الفارغ (candles: []) ردٌّ حقيقي
                # من الخادم عند فجوة أو عطلة نهاية أسبوع — يُرفع الحدث له
                # أيضاً حتى لا ينتظر الجالب 30 ثانية كاملة ثم يفشل الجلب
                # كلها بعد 3 فشلات متتالية وتبقى فجوات في التاريخ.
                _payload_key = None
                for _k in ("candles", "data", "history"):
                    if _k in message:
                        _payload_key = _k
                        break
                if asset and _payload_key is not None:
                    self.api.candle_v2_data[asset] = message
                    self.api.candles.candles_data = message.get("candles") or message.get("data") or message.get("history")""",
    "P3a empty response raises event",
)

# --- P3b: get_candles بفهرس فريد وبلا إعادة اشتراك ---
eng = patch(
    eng,
    """    async def get_candles(self, asset, end_from_time, offset, period, progressive=False, timeout=30, use_cache=False):
        if self.api is None: return None
        if end_from_time is None: end_from_time = time.time()
        index = calendar.timegm(time.gmtime())
        self.api.candles.candles_data = None
        await self.api.event_registry.clear_event(f'candles_ready_{asset}')
        await self.start_candles_stream(asset, period)
        self.api.get_candles_ws(asset, index, int(end_from_time), offset, period)
        try:
            history_data = await self.api.event_registry.wait_event(f'candles_ready_{asset}', timeout=timeout)
        except Exception:
            return None""",
    """    async def get_candles(self, asset, end_from_time, offset, period, progressive=False, timeout=30, use_cache=False):
        if self.api is None: return None
        if end_from_time is None: end_from_time = time.time()
        # v14.8 (تقرير الفحص): رقم الطلب فريد من عدّاد الطلبات — طلبان في
        # الثانية نفسها لم يكنا يحملان الرقم نفسه فيتداخل ردّاهما، وكل نداء
        # ينتظر ردَّه هو فقط عبر الحدث المفهرس (نفس توجيه _fetch_historical_batch).
        index = next(_request_counter)
        self.api.candles.candles_data = None
        _indexed_event = f'candles_ready_{asset}_{index}'
        await self.api.event_registry.clear_event(_indexed_event)
        # v14.8: لا إعادة اشتراك في كل نداء — إعادة الاشتراك كانت تغيّر فترة
        # البث الحي وتتسابق مع رد التاريخ. يُشترَك فقط إذا لم يكن البث الحي
        # يعمل لهذه العملة أصلاً.
        try:
            _already_streaming = False
            for _sa in ALL_STREAMING_ASSETS:
                if getattr(_sa, "api_symbol", None) == asset and getattr(_sa, "streaming", False):
                    _already_streaming = True
                    break
        except Exception:
            _already_streaming = False
        if not _already_streaming:
            await self.start_candles_stream(asset, period)
        self.api.get_candles_ws(asset, index, int(end_from_time), offset, period)
        try:
            history_data = await self.api.event_registry.wait_event(_indexed_event, timeout=timeout)
        except Exception:
            history_data = None
        if history_data is None:
            # تراجع آمن: الحدث العام (يُرفع دائماً لأي رد يحمل index)
            try:
                history_data = await self.api.event_registry.wait_event(f'candles_ready_{asset}', timeout=3)
            except Exception:
                return None""",
    "P3b get_candles unique index",
)

# --- P4a: لا تجميد ما دامت شموع اصطناعية (فحص الدخول) ---
eng = patch(
    eng,
    """        try:
            is_filled, _last_at = self.candle_store.is_gap_filled(derived_symbol)
            if is_filled:
                return    # frozen - keep candles exactly as they were
        except Exception:
            pass""",
    """        try:
            is_filled, _last_at = self.candle_store.is_gap_filled(derived_symbol)
            if is_filled:
                # v14.8 (تقرير الفحص): لا تجميد ما دامت في الخط شموع اصطناعية
                # (volume=0 خارج الشمعة الحية) — السد الحقيقي يبقى محاولاً
                # حتى تُستبدل كل الشموع الاصطناعية بشموع حقيقية، فلا تبقى
                # عملة مجمّدة بثغراتها للأبد.
                _has_artificial = False
                try:
                    _cps = _align_time(int(time.time()))
                    for _fc in (asset_obj.candles or []):
                        if _fc.get('time', 0) < _cps and int(_fc.get('volume', 1) or 0) == 0:
                            _has_artificial = True
                            break
                except Exception:
                    _has_artificial = False
                if not _has_artificial:
                    return    # frozen - keep candles exactly as they were
        except Exception:
            pass""",
    "P4a freeze check honesty",
)

# --- P4b: الرد الفارغ ليس نجاحاً — لا تجميد ---
eng = patch(
    eng,
    """                self._gap_filled[derived_symbol] = True
                self._gap_filled_at[derived_symbol] = now_ts
                self.save_snapshot(derived_symbol, merged)
                # mark as permanently filled in the DB so the next cycle skips
                self.candle_store.set_gap_filled(derived_symbol, True, now_ts)
                return""",
    """                self.save_snapshot(derived_symbol, merged)
                # v14.8 (تقرير الفحص): الرد الفارغ ليس نجاحاً — لا علامة
                # تجميد هنا (كانت تُثبَّت حتى عند فشل الجلب أو رد فارغ فتبقى
                # العملة مجمّدة حتى بعد إعادة التشغيل ولا تُسدّ ثغراتها أبداً).
                return""",
    "P4b no freeze on empty",
)

# --- P4c: علامة التجميد فقط إذا خرج الخط من الشموع الاصطناعية ---
eng = patch(
    eng,
    """            # 9) mark gap as filled
            self._gap_filled[derived_symbol] = True
            self._gap_filled_at[derived_symbol] = now_ts
            # 10) persist candles to the SQLite store (so the next restart
            # loads them from the DB instead of re-fetching from the API).
            self.save_snapshot(derived_symbol, merged)
            # 11) set the permanent freeze flag - subsequent fill_gap_once
            # calls for this asset will return immediately without touching
            # the candles. This is the entire fix for the 'flicker' symptom.
            self.candle_store.set_gap_filled(derived_symbol, True, now_ts)""",
    """            # 9) mark gap as filled
            # v14.8 (تقرير الفحص): علامة التجميد تُثبَّت فقط إذا خرج الخط من
            # الشموع الاصطناعية — ما دامت فيه شموع مسطحة (volume=0) يبقى السد
            # الحقيقي محاولاً في الدورات التالية حتى تُستبدل كلها.
            _still_artificial = False
            try:
                _cps2 = _align_time(int(time.time()))
                for _fc in merged:
                    if _fc.get('time', 0) < _cps2 and int(_fc.get('volume', 1) or 0) == 0:
                        _still_artificial = True
                        break
            except Exception:
                _still_artificial = False
            self.save_snapshot(derived_symbol, merged)
            if not _still_artificial:
                self._gap_filled[derived_symbol] = True
                self._gap_filled_at[derived_symbol] = now_ts
                # 11) set the permanent freeze flag - subsequent fill_gap_once
                # calls for this asset will return immediately without touching
                # the candles. This is the entire fix for the 'flicker' symptom.
                self.candle_store.set_gap_filled(derived_symbol, True, now_ts)""",
    "P4c freeze only when clean",
)

# --- P5: نافذة السد حتى أقدم شمعة اصطناعية (حتى 200 شمعة) ---
eng = patch(
    eng,
    """            # Fetch last GAP_FILL_CANDLES (10) recent candles to replace incomplete ones
            small_days = (GAP_FILL_CANDLES * PERIOD_SECONDS) / 86400.0""",
    """            # Fetch last GAP_FILL_CANDLES (10) recent candles to replace incomplete ones
            # v14.8 (تقرير الفحص): النافذة تمتد حتى أقدم شمعة اصطناعية في
            # الخط (بحد أقصى 200 شمعة) — أي ثغرة أقدم من 10 شموع كانت
            # مستحيلة الإصلاح في النسخة السابقة لأن السدّ يجلب آخر 10 شموع فقط.
            _oldest_artificial = 0
            try:
                _cps0 = _align_time(int(time.time()))
                for _fc in state['candles']:
                    if _fc.get('time', 0) < _cps0 and int(_fc.get('volume', 1) or 0) == 0:
                        if _oldest_artificial == 0 or _fc['time'] < _oldest_artificial:
                            _oldest_artificial = _fc['time']
            except Exception:
                _oldest_artificial = 0
            _window_candles = GAP_FILL_CANDLES
            if _oldest_artificial:
                try:
                    _span = int((time.time() - _oldest_artificial) // PERIOD_SECONDS) + 2
                    _window_candles = min(200, max(GAP_FILL_CANDLES, _span))
                except Exception:
                    _window_candles = GAP_FILL_CANDLES
            small_days = (_window_candles * PERIOD_SECONDS) / 86400.0""",
    "P5 seal window extends",
)

# --- P6a: الدمج في المسار الناجح — الدفعة لا تمحو التاريخ الأقدم ---
eng = patch(
    eng,
    """            live_candles = []
            if asset.candles:
                hist_times = set(c['time'] for c in candles)
                for c in asset.candles:
                    if c['time'] not in hist_times and c['time'] > (candles[-1]['time'] if candles else 0):
                        live_candles.append(c)
            asset.candles = candles + live_candles
            if asset.candles: asset.price = asset.candles[-1]['close']
            asset.write(force=True)
            # Update MT4_WRITER.sync_state with the full historical + live candles
            # so update_candle doesn't overwrite HST with only the few live candles""",
    """            # v14.8 (سبب «تختفي شموعها»): الدفعة القصيرة لا تمحو التاريخ
            # المجلوب — كل شمعة أقدم من الدفعة تبقى في الذاكرة كما هي
            # (لا فقدان للشموع أبداً) والجديد يُدمج فقط.
            _old_all = list(asset.candles or [])
            _btimes = set(c['time'] for c in candles)
            _b_lo = min(c['time'] for c in candles) if candles else 0
            _b_hi = max(c['time'] for c in candles) if candles else 0
            _kept_old = [c for c in _old_all if c['time'] < _b_lo and c['time'] not in _btimes]
            _live_c2 = [c for c in _old_all if c['time'] > _b_hi and c['time'] not in _btimes]
            asset.candles = sorted(_kept_old + list(candles) + _live_c2, key=lambda x: x['time'])
            if asset.candles: asset.price = asset.candles[-1]['close']
            asset.write(force=True)
            # Update MT4_WRITER.sync_state with the full historical + live candles
            # so update_candle doesn't overwrite HST with only the few live candles""",
    "P6a merge keeps history (success)",
)

# --- P6b: الرد الفارغ/القصير في المسار المنخفض لا يمحو الذاكرة ---
eng = patch(
    eng,
    """        # Merge even for low counts
        live_candles = []
        if asset.candles:
            hist_times = set(c['time'] for c in candles)
            for c in asset.candles:
                if c['time'] not in hist_times and c['time'] > (candles[-1]['time'] if candles else 0):
                    live_candles.append(c)
        asset.candles = candles + live_candles
        if asset.candles: asset.price = asset.candles[-1]['close']
        asset.write(force=True)""",
    """        # Merge even for low counts
        # v14.8 (سبب «تختفي شموعها»): الرد الفارغ أو القصير لا يمحو الذاكرة —
        # الشموع الموجودة تبقى كما هي ولا يُستبدل التاريخ بشيء أقل منه.
        if candles:
            _old_all = list(asset.candles or [])
            _btimes = set(c['time'] for c in candles)
            _b_lo = min(c['time'] for c in candles)
            _b_hi = max(c['time'] for c in candles)
            _kept_old = [c for c in _old_all if c['time'] < _b_lo and c['time'] not in _btimes]
            _live_c2 = [c for c in _old_all if c['time'] > _b_hi and c['time'] not in _btimes]
            asset.candles = sorted(_kept_old + list(candles) + _live_c2, key=lambda x: x['time'])
            if asset.candles: asset.price = asset.candles[-1]['close']
            asset.write(force=True)""",
    "P6b merge keeps history (low counts)",
)

# --- P7: البث يقرأ كل التيكات من قائمة الانتظار ---
eng = patch(
    eng,
    """            candle = None
            if not candle and hasattr(CLIENT, 'api') and CLIENT.api:
                candle = CLIENT.api.realtime_candles.get(internal)""",
    """            candle = None
            if hasattr(CLIENT, 'api') and CLIENT.api:
                # v14.8 (تقرير الفحص): تُقرأ كل التيكات المتراكمة من قائمة
                # الانتظار لكل عملة — لا تيك يضيع بين قراءتين فتبقى قمم
                # الشموع وقيعانها كاملة.
                try:
                    _tq = CLIENT.api._tick_queue.get(internal)
                    candle = _tq.popleft() if _tq else None
                except Exception:
                    candle = None
                if candle is None:
                    _rc = CLIENT.api.realtime_candles.get(internal)
                    try:
                        _sig = (int(_rc[1]), float(_rc[2])) if isinstance(_rc, list) and len(_rc) >= 3 else None
                    except Exception:
                        _sig = None
                    if _rc is not None and _sig is not None:
                        try:
                            _done = CLIENT.api._tick_last_done.get(internal)
                        except Exception:
                            _done = None
                        if _done != _sig:
                            candle = _rc""",
    "P7 stream drains tick queue",
)

# --- P7b: تسجيل آخر تيك مُعالَج ---
eng = patch(
    eng,
    """                if price > 0 and ts > 0:
                    # ===== FIX 10: MT4_WRITER.update_candle asset.mark_dirty =====""",
    """                if price > 0 and ts > 0:
                    try:
                        CLIENT.api._tick_last_done[internal] = (ts, price)
                    except Exception:
                        pass
                    # ===== FIX 10: MT4_WRITER.update_candle asset.mark_dirty =====""",
    "P7b last-done marker",
)

io.open(ENGINE_TMP, "w", encoding="utf-8").write(eng)
print(f"[ok] patched engine written -> {ENGINE_TMP} ({len(eng)} chars)")

# ═══════════════════════════════════════════════════════════════════
# الجزء 2 — الدمج في التطبيق (كود واحد)
# ═══════════════════════════════════════════════════════════════════
app = io.open(APP_IN, encoding="utf-8").read()

# --- A0: تعليق الرأس ---
app = patch(
    app,
    "# التطبيق يشغّل خادم Quotex الخاص بنا (qx_server_v14.py) الموجود بجانبه مباشرة:",
    "# المحرك مدمج داخل هذا الملف (كود واحد — v14.8): لا يحتاج أي ملف ثانٍ بجانبه.",
    "A0 header comment",
)

# --- A1: استبدال الحمّال بالحمّال المدمج + النص الخام للمحرك ---
LOADER_ANCHOR = """_QX_MOD = None


def _qx_module():
    \"\"\"تحميل محرك الخادم من بجانب التطبيق (يُحمَّل مرة واحدة).

    v14: يحمّل qx_server_v14 (الخادم المقوّى: تفرز الطلبات + سد الثغرات على
    كل عملة مفتوحة + التكس لا ينام + دون انهيار الخوادم) — ولو لم يوجد
    يرجع لـ qx_server_v13 كما كان تماماً (لا شيء محذوف من التطبيق).\"\"\"
    global _QX_MOD
    if _QX_MOD is not None:
        return _QX_MOD or None
    try:
        _app_dir = os.path.dirname(os.path.abspath(__file__))
        if _app_dir not in sys.path:
            sys.path.insert(0, _app_dir)
        try:
            # v14 أولاً: الخادم المقوّى (نفس الدخول ونفس جلب الشموع حرفياً)
            _QX_MOD = importlib.import_module("qx_server_v14")
        except Exception:
            # تراجع آمن للنسخة السابقة — نفس المسار القديم حرفياً
            _QX_MOD = importlib.import_module("qx_server_v13")
        try:
            _QX_MOD.DEBUG_LOGS = False
        except Exception:
            pass
    except Exception as _e:
        try:
            print("[QX] qx_server_v14/v13 load failed: " + str(_e))
        except Exception:
            pass
        _QX_MOD = False
    return _QX_MOD or None"""

LOADER_NEW = """# ═════════════ v14.8: كود واحد — المحرك مدمج داخل هذا الملف ═════════════
# طلب المستخدم حرفياً: «يجب ان يكون كود واحد وليس يحمل كود ثاني».
# كل كود محرك Quotex موجود أدناه في النص الخام _QX_ENGINE_SOURCE ويُنفَّذ
# في مساحة أسماء وحدّة عند الإقلاع — التطبيق لا يحمّل أي ملف ثانٍ ولا
# يحتاج qx_server_v14.py أو qx_server_v13.py بجانبه أبداً.
_QX_MOD = None


def _qx_module():
    \"\"\"المحرك المدمج (كود واحد): يُنفَّذ مرة واحدة في مساحة أسماء معزولة
    ويعيد وحدة تحمل كل رموز المحرك (CLIENT, ASYNC_LOOP, MT4_WRITER,
    get_historical_candles, _fill_missing_slots, ...) دون أي ملف خارجي.\"\"\"
    global _QX_MOD
    if _QX_MOD is not None:
        return _QX_MOD or None
    try:
        import types as _types
        _mod = _types.ModuleType("qx_embedded_engine")
        _mod.__file__ = os.path.abspath(__file__)
        _mod.__name__ = "qx_embedded_engine"
        exec(compile(_QX_ENGINE_SOURCE, "qx_embedded_engine", "exec"), _mod.__dict__)
        sys.modules["qx_embedded_engine"] = _mod
        try:
            _mod.DEBUG_LOGS = False
        except Exception:
            pass
        _QX_MOD = _mod
    except Exception as _e:
        try:
            print("[QX] embedded engine init failed: " + str(_e))
        except Exception:
            pass
        _QX_MOD = False
    return _QX_MOD or None


# ═══════════════════════ _QX_ENGINE_SOURCE ═══════════════════════
# المحرك الكامل (qx_server_v14 + إصلاحات تقرير الفحص v14.8) كنص خام —
# لا يحتوي ''' أبداً فالمحدد آمن. هذا هو «الكود الثاني» القديم أصبح جزءاً
# من هذا الملف الواحد."""

app = patch(app, LOADER_ANCHOR, LOADER_NEW, "A1 loader rewrite")

# --- A2: إدراج نص المحرك بعد الحمّال مباشرة ---
INSERT_AFTER = LOADER_NEW
assert app.count(INSERT_AFTER) == 1
app = app.replace(
    INSERT_AFTER,
    INSERT_AFTER + "\n\n_QX_ENGINE_SOURCE = r'''" + eng + "'''\n",
    1,
)
print("[ok] A2 engine source embedded")

# --- A3: رسالة qxFEngine الترجمة (لا ملف خارجي بعد الآن) ---
app = patch(
    app,
    '"qxEngine": "QX engine not found — keep qx_server_v14.py beside the app",',
    '"qxEngine": "QX engine error — restart the app",',
    "A3 en message",
)
app = patch(
    app,
    '"qxEngine": "محرك الخادم غير موجود — أبقِ qx_server_v14.py بجانب التطبيق",',
    '"qxEngine": "خطأ في محرك الخادم — أعد تشغيل التطبيق",',
    "A3 ar message",
)

# --- A4: إصلاح الخلل القاتل — اسم واحد لمتغير ولدالة (_hist_days) ---
# في الواجهة كان self._hist_days متغير إعدادات (float) والدالة def _hist_days(self)
# تحملان الاسم نفسه — المتغير يحجب الدالة فكل نداء self._hist_days() يفشل
# بخطأ «float غير قابل للاستدعاء» وتسقط سلسلة جلب التاريخ من أساسها صامتة.
app = patch(
    app,
    """    # ---------- v14.3: دفعات التاريخ المتسلسلة عند فتح العملة (300 ثم 300) ----------
    def _hist_days(self):
        \"\"\"عدد أيام شموع التاريخ المضبوط من الإعدادات (0.5 حتى 30، الافتراضي 2).\"\"\"
        try:
            return max(0.5, min(30.0, float(self._hist_days)))
        except Exception:
            return 2.0""",
    """    # ---------- v14.3: دفعات التاريخ عند فتح العملة (دفعة مباشرة) ----------
    def _hist_days_cfg(self):
        \"\"\"عدد أيام شموع التاريخ المضبوط من الإعدادات (0.5 حتى 30، الافتراضي 2).

        v14.8 (سبب موت سلسلة جلب التاريخ من أساسها): كانت الدالة تحمل الاسم
        نفسه `_hist_days` الذي يحمله متغير الإعدادات، فكان المتغير يحجب
        الدالة وكل نداء `self._hist_days()` يفشل بخطأ «float غير قابل
        للاستدعاء» وتسقط سلسلة الجلب صامتة داخل try/except. الدالة الآن
        `_hist_days_cfg` والمتغير يبقى `_hist_days` — لا تعارض بعد الآن.\"\"\"
        try:
            return max(0.5, min(30.0, float(self._hist_days)))
        except Exception:
            return 2.0""",
    "A4 method rename",
)
app = patch(app, "            days = self._hist_days()", "            days = self._hist_days_cfg()", "A4 call site 1")
app = patch(app, "qx.QX_HISTORY_DAYS = self._hist_days()", "qx.QX_HISTORY_DAYS = self._hist_days_cfg()", "A4 call site 2")

# --- A5: الشارت — لا إعادة ضبط أبداً لنفس العملة/الفريم (سبب اختفاء الشموع) ---
app = patch(
    app,
    """        var diff = backend.candlesCount - win.lastLen
        if (diff < 0 || diff > 60) { win.syncFull(); return }""",
    """        var diff = backend.candlesCount - win.lastLen
        /* v14.8 (سبب اختفاء الشموع): لنفس العملة والفريم لا إعادة ضبط
           للشارت إطلاقاً (لا syncFull ولا setCandles):
           - نقص العدّاد = الصفحة تمتلك شموعاً أكثر من الغذاء المقتطع —
             العدّاد فقط يتزامن ولا يُلمس العرض.
           - زيادة كبيرة = دمج في مكانها عبر patchCandles — بلا setData.
           الزوم والموضع يبقيان حرين ولا تُفقد شمعة واحدة. */
        if (diff < 0) { win.lastLen = backend.candlesCount; return }
        if (diff > 60) { win.lastLen = backend.candlesCount;
            webCall("__badiApp.patchCandles(" + backend.candlesJson + ")"); return }""",
    "A5 no reset same asset",
)

# --- A6: دفعة تملأ ثغرة داخل المدى تُدمج في مكانها (لا دفعة تضيع) ---
app = patch(
    app,
    """                            function (res) {
                                /* مزامنة عدّاد الشموع حتى لا تُعاد تهيئة الشارت
                                   بعد دمج الدفعة — العرض يبقى ثابتاً تماماً */
                                var n = parseInt(res || "0", 10) || 0
                                if (n > 0) {
                                    win.prependAt = Date.now()
                                    win.lastLen = backend.candlesCount
                                }
                            })
                return""",
    """                            function (res) {
                                /* مزامنة عدّاد الشموع حتى لا تُعاد تهيئة الشارت
                                   بعد دمج الدفعة — العرض يبقى ثابتاً تماماً */
                                var n = parseInt(res || "0", 10) || 0
                                if (n > 0) {
                                    win.prependAt = Date.now()
                                    win.lastLen = backend.candlesCount
                                    return
                                }
                                /* v14.8: دفعة تملأ ثغرة داخل المدى (ليست
                                   أقدم من أول شمعة) — تُدمج في مكانها عبر
                                   patchCandles بلا setData ولا إعادة ضبط
                                   — لا دفعة تضيع بعد الآن */
                                win.webCall("__badiApp.patchCandles("
                                            + JSON.stringify(e.candles || []) + ")",
                                            function (res2) {
                                                var n2 = parseInt(res2 || "0", 10) || 0
                                                if (n2 > 0) {
                                                    win.prependAt = Date.now()
                                                    win.lastLen = backend.candlesCount
                                                }
                                            })
                            })
                return""",
    "A6 older fallback patchCandles",
)

io.open(APP_OUT, "w", encoding="utf-8").write(app)
print(f"[ok] ONE-FILE app written -> {APP_OUT} ({len(app)} chars)")
print("DONE")
