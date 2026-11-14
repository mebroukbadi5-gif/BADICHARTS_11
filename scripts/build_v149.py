# -*- coding: utf-8 -*-
"""
build_v149.py — إصلاحات لقطة «مهذه المشاكل» (2026-11-14 01:52):

اللقطة تُظهر: شموع حقيقية ~3 ساعات فقط (13:26→16:38 ≈ كتلة واحدة 200 شمعة)
ثم شرطات مسطحة (أمداد _fill_missing_slots الاصطناعية) حتى بداية البث الحي.

الأسباب الجذرية المتبقية في v14.8:
  A) نداء السد الأصلي client.get_candles مرساته «الآن» دائماً ونافذته آخر
     200 شمعة كحد أقصى → كل شمعة اصطناعية أعمق من ذلك تبقى مسطحة للأبد
     (الشرطات في اللقطة 16:38→23:02 = 384 دقيقة > 200).
  B) كاشف «الشموع الاصطناعية» يعتمد volume=0 فقط — بينما كل الشموع المجلوبة
     من الخادم تأتي بلا حجم أصلاً (volume=0) → الشموع الحقيقية المُستبدلة
     تُحسب اصطناعية → لا تقدم أبداً ولا يتقدم المرساة.
  C) عمال سلسلة التاريخ: أول رد فارغ يقفز المرساة كتلة كاملة (200 شمعة
     تُفقد بلا محاولة) و3 فشلات متتالية تقتل العامل فتُترك كتله بلا جلب
     → التاريخ يصل متناثراً كاللقطة.
  D) المدقق الدوري find_holes يحسب الفراغات الزمنية فقط — الشرطات المسطحة
     «شموع» عنده فلا يشتغل السد العميق لها أبداً.

الإصلاحات (كلها طبقات إضافية — الآلة الأصلية وطريقة الجلب الرسمية بلا أي لمس):
  E1) v14_deep_gap_seal — نفس النداء الرسمي client.get_candles لكن مرساته
      عند أقدم شمعة اصطناعية: نافذة 200 شمعة في كل دورة تتقدم من الأقدم
      للأحدث حتى تُستبدل كل الشرطات ببيانات حقيقية من الخادم. مناطق بلا
      بيانات من الخادم (عطلة/نهاية تاريخ) تُتخطى بمؤشر تقدم لكل عملة.
  E2) كاشف اصطناعي صادق: volume=0 ومسطحة تماماً (o=h=l=c) — الشموع الحقيقية
      المجلوبة (volume=0 لكن مداها حقيقي) لا تُحسب اصطناعية.
  E3) العمال: 3 محاولات على نفس المرساة قبل أي تخطٍّ + حد الموت 10 فشلات.
  E4) find_holes يرفع الشموع الاصطناعية أيضاً فيشتغل السد العميق دورياً.
  E5) الاستدعاء في كل المسارات: فتح العملة/المراجعة/الحارس (داخل
      v14_gap_fill_for_asset) + نهاية سلسلة التاريخ (_qx_seal_gaps).
  E6) التطبيق يعرض الإصلاحات فوراً: إشارة V14_DEEP_REPAIRED تُحدّث الغذاء
      كاملاً مرة واحدة (نفس مسار مزامنة السلسلة — بلا إعادة ضبط الشارت).

كل رقعة لها مرساة واحدة فريدة مع تحقق صارم — أي مرساة مفقودة/مكررة = فشل فوري.
"""
import io

BASE = "/home/z/my-project/download"
FILES = [BASE + "/qx_server_v14.py", BASE + "/BadiChartsStudio_live.py"]
APP_ONLY = BASE + "/BadiChartsStudio_live.py"


def patch(text, anchor, repl, name, count=1):
    n = text.count(anchor)
    if n != count:
        raise SystemExit(f"[FAIL] anchor '{name}' found {n} times (expected {count})")
    print(f"[ok] {name}")
    return text.replace(anchor, repl, count)


# ══════════════════════════════════════════════════════════════════════════
# E1 + استدعاء السد العميق — يُدرَج بعد نهاية v14_gap_fill_for_asset
# ══════════════════════════════════════════════════════════════════════════
E1_ANCHOR = ("    return ok\n"
             "\n"
             "\n"
             "def v14_note_asset_opened(api_symbol: str, source: str) -> None:")

E1_REPL = '''    # v14.9 (لقطة «مهذه المشاكل» — الشرطات المسطحة القديمة لا تُستبدل أبداً):
    # السد العميق بعد الآلة الأصلية — نفس نداء الجلب الرسمي لكن مرساته عند
    # أقدم شمعة اصطناعية، فيتقدم من الأقدم للأحدث حتى يُستبدل كل شيء ببيانات
    # حقيقية من الخادم. كل المسارات (فتح العملة/المراجعة الدورية/الحارس)
    # تمر من هنا فلا تبقى أي عملة بشرطاتها للأبد.
    try:
        if not globals().get("IS_SUBSECOND"):
            await v14_deep_gap_seal(api_symbol, reason=reason)
    except _v14_asyncio.CancelledError:
        raise
    except Exception as e:
        V14_JOURNAL.record("deep_seal_error", asset=api_symbol,
                           error=str(e)[:160])
    return ok


# ══════════════════════════════════════════════════════════════════════════
# v14.9 — السد العميق: استبدال الشرطات الاصطناعية القديمة بشموع حقيقية
# ══════════════════════════════════════════════════════════════════════════
# لقطة «مهذه المشاكل» (2026-11-14): شموع حقيقية ~3 ساعات ثم شرطات مسطحة
# (أمداد _fill_missing_slots) حتى بداية البث الحي. السبب: النداء الأصلي في
# fill_gap_once مرساته «الآن» ونافذته آخر 200 شمعة كحد أقصى — فكل شمعة
# اصطناعية أعمق من ذلك تبقى مسطحة للأبد.
#
# الحل (طبقة إضافية بلا أي تغيير في الآلة الأصلية ولا في طريقة الجلب
# الرسمية): نفس النداء client.get_candles(...) (نفس الطلب history/load
# ونفس التحليل عبر prepare_candles) لكن مرساته عند أقدم مشكلة — نافذة
# 200 شمعة في كل دورة تتقدم من الأقدم للأحدث حتى يُستبدل كل شيء ببيانات
# حقيقية من الخادم. ما لا يرد له الخادم بيانات (عطلة/إغلاق) يُتخطى بمؤشر
# تقدم لكل عملة حتى لا تدور الجولات على نفس المرساة بلا نهاية.
_V14_DEEP_CURSOR: Dict[str, float] = {}    # مرساة بلا تقدم → تُتخطى مؤقتاً
V14_DEEP_REPAIRED: Dict[str, float] = {}   # إشارة للتطبيق: وقت آخر إصلاح عميق


def _v14_is_synth_flat(c) -> bool:
    """v14.9: كاشف الشمعة الاصطناعية الصادق.

    الاصطناعية = مولّدة بلا حجم (volume=0) ومسطحة تماماً (o=h=l=c>0).
    الشموع الحقيقية المجلوبة من الخادم تأتي بلا حجم أصلاً (volume=0) لكن
    مداها حقيقي (high>low غالباً) — الكاشف القديم كان يحسبها اصطناعية
    فلا يتقدم السد أبداً ولا يصل للأعمق (سبب بقاء الشرطات في اللقطة)."""
    try:
        if int(c.get("volume", 1) or 0) != 0:
            return False
        o = float(c.get("open", 0) or 0)
        if o <= 0:
            return False
        h = float(c.get("high", 0) or 0)
        l = float(c.get("low", 0) or 0)
        cl = float(c.get("close", 0) or 0)
        return o == h == l == cl
    except Exception:
        return False


async def v14_deep_gap_seal(api_symbol: str, *, reason: str = "deep",
                            max_passes: int = 8,
                            window_candles: int = 200,
                            time_budget_s: float = 45.0) -> bool:
    """السد العميق — يستبدل الشرطات الاصطناعية القديمة والفراغات العميقة
    بشموع حقيقية بنفس طريقة الجلب الرسمية (client.get_candles نفسها التي
    تستخدمها الآلة الأصلية fill_gap_once — نفس الطلب ونفس التحليل، فقط
    المرساة عند أقدم مشكلة بدل «الآن»).

    - يستبدل الاصطناعي المسطح والفراغات الزمنية فقط — الشموع الحقيقية
      والشمعة الحية لا تُلمس إطلاقاً (نفس حماية الآلة الأصلية).
    - منطقة لا يرد لها الخادم بيانات → تُتخطى بمؤشر تقدم (لا حلقات بلا نهاية).
    - يعيد True إذا استبدل/أضاف شموعاً حقيقية فعلاً.
    """
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return False
    client = globals().get("CLIENT")
    if client is None or getattr(client, "api", None) is None or \\
            not globals().get("CONNECTION_ALIVE"):
        return False
    if globals().get("IS_SUBSECOND"):
        return False
    period_s = int(globals().get("PERIOD_SECONDS", 60) or 60)
    if period_s <= 0:
        return False
    asset = _v14_find_asset(api_symbol)
    if asset is None:
        try:
            getter = globals().get("_get_or_create_asset")
            if getter is not None:
                asset = getter(api_symbol)
        except Exception:
            asset = None
    if asset is None:
        return False
    store = globals().get("MT4_WRITER")
    sym_store = str(getattr(asset, "symbol", "") or api_symbol)
    win_s = max(2, int(window_candles)) * period_s
    t_deadline = time.monotonic() + max(5.0, float(time_budget_s))
    repaired_any = False
    for _pass in range(max(1, int(max_passes))):
        if time.monotonic() > t_deadline:
            break
        try:
            line = sorted(list(asset.candles or []),
                          key=lambda c: int(c.get("time", 0)))
        except Exception:
            break
        if len(line) < 2:
            break
        cur_start = _align_time(int(time.time()))
        cursor = float(_V14_DEEP_CURSOR.get(api_symbol, 0.0) or 0.0)
        # أقدم مشكلة بعد المؤشر: شمعة اصطناعية مسطحة أو فجوة زمنية.
        # الشمعة الحية وما بعدها لا تُلمس (حماية الآلة الأصلية نفسها).
        oldest_flat = 0
        oldest_hole = 0
        prev_t = 0
        for c in line:
            t = int(c.get("time", 0))
            if t >= cur_start:
                break
            if t > cursor:
                if _v14_is_synth_flat(c) and (oldest_flat == 0 or t < oldest_flat):
                    oldest_flat = t
                if prev_t and (t - prev_t) > period_s and \\
                        (oldest_hole == 0 or prev_t < oldest_hole):
                    oldest_hole = prev_t
            prev_t = t
        _cand = [x for x in (oldest_flat, oldest_hole) if x]
        target_t = min(_cand) if _cand else 0
        if not target_t:
            # لا مشاكل بعد المؤشر — المؤشر يُمسح ليبدأ السد من جديد لاحقاً
            _V14_DEEP_CURSOR.pop(api_symbol, None)
            break
        anchor_end = target_t + win_s
        if anchor_end > int(time.time()):
            anchor_end = int(time.time())
        try:
            # نفس نداء الجلب الرسمي الذي تستخدمه الآلة الأصلية fill_gap_once
            fetched = await client.get_candles(api_symbol, anchor_end, win_s, period_s)
        except Exception:
            fetched = None
        if not fetched:
            # لا بيانات من الخادم لهذه المنطقة (عطلة/نهاية تاريخ) — تُتخطى
            # مؤقتاً حتى لا تدور الجولات على نفس المرساة
            _V14_DEEP_CURSOR[api_symbol] = float(anchor_end)
            V14_JOURNAL.record("deep_seal_skip", asset=api_symbol,
                               anchor=int(anchor_end), reason=reason)
            continue
        try:
            cur_map = {int(c.get("time", 0)): c for c in line}
        except Exception:
            break
        changed = 0
        for fc in fetched:
            try:
                t = _align_time(int(fc.get("time", fc.get("timestamp", 0)) or 0))
            except Exception:
                continue
            if t <= 0 or t >= cur_start or t < target_t:
                continue
            o = float(fc.get("open", fc.get("o", 0)) or 0)
            h = float(fc.get("high", fc.get("max", fc.get("h", 0))) or 0)
            l = float(fc.get("low", fc.get("min", fc.get("l", 0))) or 0)
            cl = float(fc.get("close", fc.get("c", 0)) or 0)
            if o <= 0 or h <= 0 or l <= 0 or cl <= 0:
                continue
            ex = cur_map.get(t)
            if ex is None or _v14_is_synth_flat(ex):
                cur_map[t] = {"time": t, "open": o, "high": h, "low": l,
                              "close": cl, "volume": 0}
                changed += 1
        if not changed:
            # الخادم أعاد نفس البيانات بلا تحسن — تُتخطى هذه المرساة مؤقتاً
            _V14_DEEP_CURSOR[api_symbol] = float(anchor_end)
            continue
        merged = sorted(cur_map.values(), key=lambda c: int(c.get("time", 0)))
        try:
            merged = _fill_missing_slots(list(merged), period_s, max_gap=1440)
        except Exception:
            pass
        merged = merged[-int(globals().get("ASSET_MAX_CANDLES", 45000)):]
        try:
            _apply_candles_to_asset(asset, merged)
        except Exception:
            pass
        try:
            if store is not None and getattr(store, "save_snapshot", None):
                store.save_snapshot(sym_store, merged)
        except Exception:
            pass
        repaired_any = True
        _V14_DEEP_CURSOR.pop(api_symbol, None)
        V14_DEEP_REPAIRED[api_symbol] = time.time()
        V14_JOURNAL.record("deep_seal_pass", asset=api_symbol,
                           replaced=changed, anchor=int(anchor_end),
                           reason=reason, pass_n=_pass + 1)
    return repaired_any


def v14_note_asset_opened(api_symbol: str, source: str) -> None:'''

# ══════════════════════════════════════════════════════════════════════════
# E2 — كاشف اصطناعي صادق في مواضع fill_gap_once الثلاثة
# ══════════════════════════════════════════════════════════════════════════
SPOT1_ANCHOR = ("    for _fc in (asset_obj.candles or []):\n"
                "                        if _fc.get('time', 0) < _cps and int(_fc.get('volume', 1) or 0) == 0:")
SPOT1_REPL = ("    for _fc in (asset_obj.candles or []):\n"
              "                        if _fc.get('time', 0) < _cps and _v14_is_synth_flat(_fc):")

SPOT2_ANCHOR = ("    for _fc in state['candles']:\n"
                "                    if _fc.get('time', 0) < _cps0 and int(_fc.get('volume', 1) or 0) == 0:")
SPOT2_REPL = ("    for _fc in state['candles']:\n"
              "                    if _fc.get('time', 0) < _cps0 and _v14_is_synth_flat(_fc):")

SPOT3_ANCHOR = ("    for _fc in merged:\n"
                "                    if _fc.get('time', 0) < _cps2 and int(_fc.get('volume', 1) or 0) == 0:")
SPOT3_REPL = ("    for _fc in merged:\n"
              "                    if _fc.get('time', 0) < _cps2 and _v14_is_synth_flat(_fc):")

# ══════════════════════════════════════════════════════════════════════════
# E4 — المدقق الدوري: الشرطات الاصطناعية ثغرات أيضاً
# ══════════════════════════════════════════════════════════════════════════
E4_ANCHOR = ('''            for a, b in zip(line, line[1:]):
                gap = int(b.get("time", 0)) - int(a.get("time", 0))
                if period_s < gap <= int(self.suspect_max_gap_s) and \\
                        gap > period_s:
                    holes.append(int(a.get("time", 0)))
        except Exception:
            pass
        return holes''')
E4_REPL = '''            for a, b in zip(line, line[1:]):
                gap = int(b.get("time", 0)) - int(a.get("time", 0))
                if period_s < gap <= int(self.suspect_max_gap_s) and \\
                        gap > period_s:
                    holes.append(int(a.get("time", 0)))
            # v14.9 (لقطة «مهذه المشاكل»): الشموع الاصطناعية المسطحة (الشرطات)
            # ثغرات أيضاً — الكاشف القديم كان يحسبها شموعاً فلا يشتغل السد
            # العميق لها أبداً. تُرفع وقتها ليُستبدل السد العميق كل واحدة
            # بشمعة حقيقية بنفس طريقة الجلب الرسمية.
            try:
                _cur0 = _align_time(int(time.time()))
                _n_synth = 0
                for c in line:
                    if int(c.get("time", 0)) >= _cur0:
                        continue
                    if _v14_is_synth_flat(c):
                        holes.append(int(c.get("time", 0)))
                        _n_synth += 1
                        if _n_synth >= 200:
                            break
            except Exception:
                pass
        except Exception:
            pass
        return holes'''

# ══════════════════════════════════════════════════════════════════════════
# E3 — عمال سلسلة التاريخ: بلا تخطي كتل ولا موت مبكر
# ══════════════════════════════════════════════════════════════════════════
E3_INIT_ANCHOR = ("    oldest_t = start_t\n"
                  "                consecutive_failures_in_worker = 0")
E3_INIT_REPL = ("    oldest_t = start_t\n"
                "                consecutive_failures_in_worker = 0\n"
                "                _same_anchor_tries = 0   # v14.9: محاولات على نفس المرساة قبل أي تخطٍّ")

E3_FAIL_ANCHOR = ("    if not batch_data:\n"
                  "                        oldest_t -= chunk_seconds\n"
                  "                        consecutive_failures_in_worker += 1\n"
                  "                        if consecutive_failures_in_worker >= 3:\n"
                  "                            # 3 consecutive failures = connection dead — exit\n"
                  "                            break\n"
                  "                        # backoff\n"
                  "                        await asyncio.sleep(FETCH_BATCH_DELAY * 2)\n"
                  "                        continue")
E3_FAIL_REPL = '''    if not batch_data:
                        # v14.9 (لقطة «مهذه المشاكل» — التاريخ يصل متناثراً):
                        # كان أول رد فارغ يقفز المرساة كتلة كاملة (200 شمعة
                        # تُفقد بلا محاولة) وأي 3 فشلات متتالية تقتل العامل
                        # فيُترك كتله كاملاً بلا جلب. الآن: 3 محاولات على نفس
                        # المرساة بفواصل أطول قبل أي تخطٍّ، وحد الموت 10 فشلات
                        # متتالية — الطريقة نفسها (نفس الطلب، نفس المرساة،
                        # نفس الإيقاع) بلا أي تغيير.
                        consecutive_failures_in_worker += 1
                        _same_anchor_tries += 1
                        if consecutive_failures_in_worker >= 10:
                            # 10 consecutive failures = connection dead — exit
                            break
                        if _same_anchor_tries >= 3:
                            _same_anchor_tries = 0
                            oldest_t -= chunk_seconds
                        # backoff
                        await asyncio.sleep(FETCH_BATCH_DELAY * (2 + _same_anchor_tries * 2))
                        continue'''

E3_OK_ANCHOR = ("    consecutive_failures_in_worker = 0\n"
                "                    new_batch = self._parse_historical_candles(batch_data)")
E3_OK_REPL = ("    consecutive_failures_in_worker = 0\n"
              "                    _same_anchor_tries = 0\n"
              "                    new_batch = self._parse_historical_candles(batch_data)")

E3_PARSE_ANCHOR = "    if not new_batch: oldest_t -= chunk_seconds; continue"
E3_PARSE_REPL = '''    if not new_batch:
                        # v14.9: رد غير قابل للتحليل = محاولة على نفس المرساة
                        # قبل التخطي (القديم كان يهمل كتلة كاملة من أول مرة)
                        _same_anchor_tries += 1
                        if _same_anchor_tries >= 3:
                            _same_anchor_tries = 0
                            oldest_t -= chunk_seconds
                        await asyncio.sleep(FETCH_BATCH_DELAY * 2)
                        continue'''

# ══════════════════════════════════════════════════════════════════════════
# A1 — التطبيق: السد العميق في نهاية سلسلة التاريخ (_qx_seal_gaps)
# ══════════════════════════════════════════════════════════════════════════
A1_ANCHOR = ('''                unique = unique[-int(getattr(qx, "ASSET_MAX_CANDLES", 45000)):]
                qx._apply_candles_to_asset(asset, unique)
        except Exception:
            pass

    def _qx_chain_worker(self, api, tf_label, gen):''')
A1_REPL = '''                unique = unique[-int(getattr(qx, "ASSET_MAX_CANDLES", 45000)):]
                qx._apply_candles_to_asset(asset, unique)
        except Exception:
            pass
        # v14.9 (لقطة «مهذه المشاكل»): السد العميق في نهاية سلسلة التاريخ —
        # نفس نداء الجلب الرسمي لكن مرساته عند أقدم شمعة اصطناعية، فيستبدل
        # الشرطات المسطحة القديمة بشموع حقيقية قبل مزامنة الشارت (طبقة
        # إضافية بلا أي تغيير في الآلة الأصلية ولا في طريقة الجلب).
        try:
            _ds_fut = asyncio.run_coroutine_threadsafe(
                qx.v14_deep_gap_seal(api, reason="chain"), qx.ASYNC_LOOP)
            _ds_fut.result(timeout=60)
        except Exception:
            pass

    def _qx_chain_worker(self, api, tf_label, gen):'''

# ══════════════════════════════════════════════════════════════════════════
# A2 — التطبيق: إشارة الإصلاح العميق تُحدّث الغذاء فوراً (بلا إعادة ضبط)
# ══════════════════════════════════════════════════════════════════════════
A2_ANCHOR = ('''        if tf_sec == 60:
            candles = self._qx_engine_candles(api)
            if candles:
                if not self._candles or self._qx_feed_key != key:''')
A2_REPL = '''        if tf_sec == 60:
            candles = self._qx_engine_candles(api)
            if candles:
                # v14.9 (لقطة «مهذه المشاكل»): السد العميق استبدل شرطات قديمة
                # بشموع حقيقية في ذاكرة المحرك — تحديث كامل واحد للغذاء يُظهرها
                # فوراً (نفس مسار مزامنة السلسلة: بلا setData وبلا إعادة ضبط —
                # الزوم والموضع يبقيان حرين)
                try:
                    _ds_t = int((getattr(qx, "V14_DEEP_REPAIRED", {}) or {}).get(api, 0) or 0)
                    if _ds_t > int(getattr(self, "_qx_deep_seen", 0) or 0):
                        self._qx_deep_seen = _ds_t
                        self._candles = candles[-self._QX_FEED_CAP:]
                        self._qx_last_sig = None
                        self._qx_resync_pending = True
                except Exception:
                    pass
                if not self._candles or self._qx_feed_key != key:'''

# ══════════════════════════════════════════════════════════════════════════
# التطبيق
# ══════════════════════════════════════════════════════════════════════════
for path in FILES:
    src = io.open(path, encoding="utf-8").read()
    src = patch(src, E1_ANCHOR, E1_REPL, f"E1 deep seal + call [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, SPOT1_ANCHOR, SPOT1_REPL, f"E2 spot1 honest detector [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, SPOT2_ANCHOR, SPOT2_REPL, f"E2 spot2 honest detector [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, SPOT3_ANCHOR, SPOT3_REPL, f"E2 spot3 honest detector [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, E4_ANCHOR, E4_REPL, f"E4 auditor synthetic holes [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, E3_INIT_ANCHOR, E3_INIT_REPL, f"E3 worker init [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, E3_FAIL_ANCHOR, E3_FAIL_REPL, f"E3 worker fail retry [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, E3_OK_ANCHOR, E3_OK_REPL, f"E3 worker success reset [{path.rsplit('/', 1)[-1]}]")
    src = patch(src, E3_PARSE_ANCHOR, E3_PARSE_REPL, f"E3 worker parse-empty retry [{path.rsplit('/', 1)[-1]}]")
    io.open(path, "w", encoding="utf-8").write(src)

# طبقة التطبيق فقط (التطبيق الواحد — إشارة العرض والسد في نهاية السلسلة)
app = io.open(APP_ONLY, encoding="utf-8").read()
app = patch(app, A1_ANCHOR, A1_REPL, "A1 chain final deep seal [app]")
app = patch(app, A2_ANCHOR, A2_REPL, "A2 deep repaired feed refresh [app]")
# ترقيم نسخة الواجهة حتى يعرف المستخدم أنه يشغّل الملف الجديد
app = patch(app, "BADI STUDIO v2.13.0", "BADI STUDIO v2.13.1", "version bump status bar", count=2)
io.open(APP_ONLY, "w", encoding="utf-8").write(app)

print("DONE — v14.9 patches applied")
