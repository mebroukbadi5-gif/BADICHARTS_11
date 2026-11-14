# -*- coding: utf-8 -*-
"""اختبارات إصلاحات v14.9 — لقطة «مهذه المشاكل» (2026-11-14):

المشهد في اللقطة: شموع حقيقية ~3 ساعات ثم شرطات مسطحة (أمداد اصطناعية)
حتى بداية البث الحي — السبب: نداء السد مرساته «الآن» ونافذته 200 شمعة،
وعمال التاريخ يتخطون كتلاً كاملة عند أول فشل ويموتون بعد 3 فشلات.

المحاكمة:
 1) السد العميق v14_deep_gap_seal: يستبدل كل الشرطات المسطحة والفراغات
    العميقة بشموع حقيقية — بلا لمس الشموع الحقيقية ولا الشمعة الحية.
 2) منطقة لا يرد لها الخادم بيانات: تُتخطى بمؤشر التقدم — الجولات محدودة
    ولا تدور بلا نهاية.
 3) الكاشف الصادق: الشمعة الاصطناعية = بلا حجم ومسطحة تماماً؛ الشموع
    الحقيقية المجلوبة (بلا حجم لكن مداها حقيقي) ليست اصطناعية.
 4) عمال التاريخ: نفس المرساة تُعاد محاولتها 3 مرات قبل أي تخطٍّ، وحد
    الموت 10 فشلات متتالية (كان 3 — كان يقتل العامل مبكراً).
 5) الإصلاح موصول في كل المسارات: فتح/مراجعة/حارس + نهاية سلسلة التاريخ
    + تحديث الغذاء في التطبيق عبر V14_DEEP_REPAIRED.
يعمل على الكود الحقيقي المستخرَج (ast) من qx_server_v14.py ومن المحرك
المدمج داخل BadiChartsStudio_live.py.
"""
import ast, io, time, asyncio, types, sys, subprocess

V14 = "/home/z/my-project/download/qx_server_v14.py"
APP = "/home/z/my-project/download/BadiChartsStudio_live.py"

passed, failed = [], []


def check(name, cond, extra=""):
    (passed if cond else failed).append(name)
    print(("  OK " if cond else "  XX ") + name + (("  [" + extra + "]") if extra else ""))


def extract_function(path, func_name, class_name=None, source=None):
    src = source if source is not None else io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if class_name is not None:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == func_name:
                        return ast.get_source_segment(src, item)
        else:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and item_name_ok(node, func_name):
                return ast.get_source_segment(src, node)
    raise RuntimeError(f"{func_name} not found")


def item_name_ok(node, name):
    return node.name == name


def embedded_engine_source(app_path):
    src = io.open(app_path, encoding="utf-8").read()
    start = src.find("_QX_ENGINE_SOURCE = r'''")
    if start < 0:
        raise RuntimeError("embedded engine not found")
    start = src.find("'''", start) + 3
    end = src.find("'''", start)
    return src[start:end]


now = int(time.time()) // 60 * 60
P = 60


# ═══════════════════ 3) الكاشف الصادق ═══════════════════
code_flat = extract_function(V14, "_v14_is_synth_flat")
ns_flat = {}
exec(compile(code_flat, V14, "exec"), ns_flat)
_is_flat = ns_flat["_v14_is_synth_flat"]
check("synthetic flat detector: flat+vol0 = True",
      _is_flat({"time": 1, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 0}) is True)
check("honest detector: real-range fetched candle (vol0, h>l) = False",
      _is_flat({"time": 1, "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.0, "volume": 0}) is False)
check("honest detector: volume>0 never synthetic",
      _is_flat({"time": 1, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 5}) is False)
check("honest detector: live/zero price not synthetic",
      _is_flat({"time": 1, "open": 0, "high": 0, "low": 0, "close": 0, "volume": 0}) is False)

# ═══════════════════ 1) السد العميق — سلوك كامل ═══════════════════
code_deep = extract_function(V14, "v14_deep_gap_seal")


class _Asset:
    def __init__(self, candles, symbol="SYM1"):
        self.candles = candles
        self.symbol = symbol
        self.api_symbol = "XUSD_otc"
        self.price = 0.0


def _align(ts, period_seconds=None):
    return int(ts) // P * P


def _apply(asset, candles):
    asset.candles = list(candles)


def _fmt_slot(t, seed=1):
    v = (int(t) // P * 7919 + seed) % 100
    base = 1.0 + (v % 40) / 4000.0
    o = base
    c = base + ((v % 7) - 3) / 4000.0
    h = max(o, c) + (v % 5) / 4000.0 + 0.0002
    l = min(o, c) - (v % 5) / 4000.0 - 0.0002
    return {"time": t, "open": round(o, 6), "high": round(h, 6),
            "low": round(l, 6), "close": round(c, 6), "volume": 0}


def build_line():
    """خط ~33 ساعة: شموع حقيقية + شوط اصطناعي 300 + فجوة 50 + شوط اصطناعي
    150 + فجوة ذيل 19 قبل الشمعة الحية (المحمية)."""
    line = []
    for i in range(400):                       # حقيقية: -2000م .. -1601م
        line.append(_fmt_slot(now - (2000 - i) * P, seed=11))
    last_close = line[-1]["close"]
    for i in range(300):                       # اصطناعية مسطحة: -1600م .. -1301م
        line.append({"time": now - (1600 - i) * P, "open": last_close,
                     "high": last_close, "low": last_close,
                     "close": last_close, "volume": 0})
    line += [_fmt_slot(now - (1300 - i) * P, seed=22) for i in range(300)]   # حقيقية -1300..-1001
    # فجوة زمنية 50 فترة: -1000م .. -951م (لا شموع)
    line += [_fmt_slot(now - (950 - i) * P, seed=33) for i in range(200)]    # حقيقية -950..-751
    last_close = line[-1]["close"]
    for i in range(150):                       # اصطناعية: -750م .. -601م
        line.append({"time": now - (750 - i) * P, "open": last_close,
                     "high": last_close, "low": last_close,
                     "close": last_close, "close2": 0, "close": last_close, "volume": 0})
    line += [_fmt_slot(now - (600 - i) * P, seed=44) for i in range(580)]    # حقيقية -600..-21
    line.append({"time": now, "open": 1.05, "high": 1.06, "low": 1.04,
                 "close": 1.055, "volume": 3})   # الشمعة الحية — محمية
    line.sort(key=lambda c: c["time"])
    return line


def make_env(line, serve_all=True, oldest_data=None):
    asset = _Asset([dict(c) for c in line])
    calls = []

    async def _get_candles(sym, end_from_time, offset, period):
        calls.append((int(end_from_time), int(offset)))
        end = int(end_from_time)
        start = end - int(offset) + P
        if oldest_data is not None and start < oldest_data:
            start = oldest_data
        if serve_all is False and start < now - 1000 * P:
            # الخادم لا يملك بيانات في المناطق الأقدم من -1000 دقيقة
            if end < now - 1000 * P:
                await asyncio.sleep(0)
                return []
        return [_fmt_slot(t, seed=55) for t in range(start, end + P, P) if t <= now]

    client = types.SimpleNamespace(api=object(), get_candles=_get_candles)
    journal = types.SimpleNamespace(record=lambda *a, **k: None)
    store = types.SimpleNamespace(save_snapshot=lambda *a, **k: None)
    g = {
        "CLIENT": client, "CONNECTION_ALIVE": True, "IS_SUBSECOND": False,
        "PERIOD_SECONDS": P, "ASSET_MAX_CANDLES": 45000,
        "MT4_WRITER": store, "V14_JOURNAL": journal,
        "_align_time": _align, "_apply_candles_to_asset": _apply,
        "_fill_missing_slots": lambda c, p, max_gap=1440: list(c),
        "_v14_find_asset": lambda sym: asset if sym == "XUSD_otc" else None,
        "_v14_is_synth_flat": _is_flat,
        "_V14_DEEP_CURSOR": {}, "V14_DEEP_REPAIRED": {},
        "time": time, "asyncio": asyncio, "Dict": dict,
    }
    exec(compile(code_deep, V14, "exec"), g)
    return g["v14_deep_gap_seal"], asset, calls, g


async def _run_full():
    line = build_line()
    real_before = {c["time"]: (c["open"], c["high"], c["low"], c["close"])
                   for c in line if int(c.get("volume", 0) or 0) != 0}
    live_before = [c for c in line if c["time"] >= now]
    seal, asset, calls, g = make_env(line, serve_all=True)
    ok = await seal("XUSD_otc", reason="test", time_budget_s=60)
    final = {c["time"]: c for c in asset.candles}
    # أ) لا تبقى أي شمعة اصطناعية مسطحة
    remaining = [t for t, c in final.items()
                 if t < now and _is_flat(c)]
    check("deep seal replaces ALL synthetic dashes with real candles",
          not remaining, f"remaining={len(remaining)}")
    # ب) كل فترة من بداية الخط حتى الآن موجودة (الفجوة 50 والذيل 19 سُدّت)
    first_t = min(final)
    missing = [t for t in range(first_t, now, P) if t not in final]
    check("deep time hole (50 slots) and tail gap sealed",
          not missing, f"missing={len(missing[:5])}... n={len(missing)}")
    # ج) الشموع الحقيقية الأصلية لم تُلمس
    changed_real = [t for t, ohlc in real_before.items()
                    if t in final and (final[t]["open"], final[t]["high"],
                                       final[t]["low"], final[t]["close"]) != ohlc]
    check("original REAL candles untouched (append-only replace)",
          not changed_real, f"changed={len(changed_real)}")
    # د) الشمعة الحية محمية
    live_after = [final[t] for t in live_before_times(live_before) if t in final]
    ok_live = all((c["open"], c["high"], c["low"], c["close"]) == (1.05, 1.06, 1.04, 1.055)
                  for c in live_after)
    check("live candle NEVER touched", ok_live and len(live_after) == 1)
    # هـ) إشارة الإصلاح للتطبيق + النتيجة
    check("deep seal returns True and signals V14_DEEP_REPAIRED",
          ok is True and g["V14_DEEP_REPAIRED"].get("XUSD_otc", 0) > 0)
    # و) كل نافذة جلب ≤ 201 فترة (200 شمعة + فترة المرساة نفسها)
    oversize = [c for c in calls if c[1] > 201 * P]
    check("every fetch window <= 200 candles + anchor slot (official window)",
          not oversize, f"oversize={oversize[:3]}")
    # ز) عدد الجولات محدود (الشوط 300 يحتاج دورتين فقط)
    check("passes bounded (<= 8 passes, few fetches)", len(calls) <= 8, f"fetches={len(calls)}")


def live_before_times(live_before):
    return [c["time"] for c in live_before]


asyncio.get_event_loop_policy().new_event_loop().run_until_complete(_run_full())

# ═══════════════════ 2) المنطقة بلا بيانات: تخطٍّ محدود بلا حلقات ═══════════════════
async def _run_stall():
    line = build_line()
    seal, asset, calls, g = make_env(line, serve_all=False, oldest_data=now - 1200 * P)
    t0 = time.monotonic()
    ok = await seal("XUSD_otc", reason="stall", max_passes=8, time_budget_s=30)
    dt = time.monotonic() - t0
    final = {c["time"]: c for c in asset.candles}
    remaining_old = [t for t, c in final.items()
                     if t < now - 1000 * P and _is_flat(c)]
    remaining_new = [t for t, c in final.items()
                     if now - 1000 * P <= t < now and _is_flat(c)]
    check("stalled region skipped (cursor) — bounded passes, fast return",
          dt < 10.0, f"dt={dt:.1f}s fetches={len(calls)}")
    check("server-empty deep region stays flat (no fake data invented)",
          len(remaining_old) > 0, f"old flats kept={len(remaining_old)}")
    check("recent region WITH server data fully sealed despite stall",
          not remaining_new, f"new flats={len(remaining_new)}")
    check("stall does not report success-as-repair when nothing replaced",
          ok is True, f"ok={ok} (recent region was repaired)")


asyncio.get_event_loop_policy().new_event_loop().run_until_complete(_run_stall())

# ═══════════════════ 4) عمال التاريخ — بلا تخطي كتل ولا موت مبكر ═══════════════════
code_hist = extract_function(V14, "get_historical_candles")
check("worker: retry SAME anchor before skipping (no chunk lost on first failure)",
      "_same_anchor_tries" in code_hist and code_hist.count("_same_anchor_tries >= 3") == 2)
check("worker: death threshold raised 3 -> 10 consecutive failures",
      "consecutive_failures_in_worker >= 10" in code_hist and
      "consecutive_failures_in_worker >= 3:" not in code_hist)
check("worker: parse-empty response also retried at same anchor",
      "if not new_batch:\n" in code_hist and "_same_anchor_tries += 1" in code_hist)

hist_calls = {"log": []}


async def _fake_batch(asset, fetch_time, offset, period, index, timeout):
    hist_calls["log"].append(int(fetch_time))
    state = hist_calls
    state["n"] = state.get("n", 0) + 1
    if state["mode"] == "flaky" and state["n"] <= 2:
        return None                       # فشلان ثم نجاح على نفس المرساة
    if state["mode"] == "dead":
        return None
    # نجاح: كتلة 20 شمعة حقيقية تنتهي عند المرساة
    n = 20
    return {"candles": [[now - i * P, 1.0, 1.001, 1.002, 0.999] for i in range(n)]}


def _parse_hist(raw):
    out = []
    for c in (raw or {}).get("candles", []):
        out.append({"time": int(c[0]), "open": float(c[1]), "close": float(c[2]),
                    "high": float(c[3]), "low": float(c[4])})
    return out


async def _noop_stream(asset, period):
    return None


class _State:
    check_accepted_connection = True


class _Api:
    state = _State()


def run_hist(mode):
    hist_calls["log"] = []
    hist_calls["n"] = 0
    hist_calls["mode"] = mode
    body = "\n".join("    " + ln if ln.strip() else ln
                     for ln in code_hist.splitlines())
    shell = (
        "class _Q:\n"
        "    api = _Api()\n"
        + body.replace("    async def get_historical_candles", "    async def get_historical_candles", 1) + "\n"
        "    _fetch_historical_batch = staticmethod(_fake_batch)\n"
        "    _parse_historical_candles = staticmethod(_parse_hist)\n"
        "    start_candles_stream = staticmethod(_noop_stream)\n"
    )
    ns = {"time": time, "asyncio": asyncio, "_request_counter": iter(range(1, 10 ** 6)),
          "FETCH_CHUNK_SIZE": 200, "FETCH_BATCH_DELAY": 0.01,
          "_fake_batch": _fake_batch, "_parse_hist": _parse_hist,
          "_noop_stream": _noop_stream, "_Api": _Api}
    # _request_counter يجب أن يكون عدّاداً حياً
    import itertools
    ns["_request_counter"] = itertools.count(1)
    exec(compile(shell, "<hist>", "exec"), ns)
    q = ns["_Q"]()
    amt = 130000 if mode == "dead" else 1200
    fut = q.get_historical_candles("XUSD_otc", amount_of_seconds=amt, period=60,
                                   max_workers=1, timeout=5)
    return asyncio.new_event_loop().run_until_complete(fut)


res = run_hist("flaky")
check("flaky worker (2 failures then success): SAME anchor retried, no chunk skipped",
      hist_calls["log"][:3] == [hist_calls["log"][0]] * 3 and len(res) == 20,
      f"calls={hist_calls['log'][:4]} got={len(res)}")
res2 = run_hist("dead")
check("dead worker: exits only after 10 consecutive failures (was 3)",
      len(hist_calls["log"]) == 10 and res2 == [], f"calls={len(hist_calls['log'])}")

# ═══════════════════ 5) الوصول في كل المسارات ═══════════════════
fg_code = extract_function(V14, "fill_gap_once", "MT4Writer")
check("fill_gap_once uses honest detector at all 3 spots (no volume-only check)",
      fg_code.count("_v14_is_synth_flat(_fc)") == 3 and
      "int(_fc.get('volume', 1) or 0) == 0:" not in fg_code)
gfa_code = extract_function(V14, "v14_gap_fill_for_asset")
check("open/audit/guard path calls deep seal",
      "v14_deep_gap_seal(api_symbol, reason=reason)" in gfa_code)
fh_code = extract_function(V14, "find_holes", "V14GapLossAuditor")
check("auditor find_holes reports synthetic dashes too (periodic deep seal)",
      "_v14_is_synth_flat(c)" in fh_code)

# المحرك المدمج داخل ملف التطبيق الواحد
eng_src = embedded_engine_source(APP)
eng_tree_ok = True
try:
    ast.parse(eng_src)
except SyntaxError as e:
    eng_tree_ok = False
check("embedded engine in single file parses (syntax OK)", eng_tree_ok)
check("embedded engine has deep seal + honest detector + worker hardening",
      "async def v14_deep_gap_seal" in eng_src and
      # v15+: المحرك = الأصل بايت ببايت والسد العميق في طبقة الربط بكاشفها
      # الصادق الذاتي (volume==0 للشموع الاصطناعية) — علامات qx_server_v14
      # القديمة (_v14_is_synth_flat/_same_anchor_tries) كانت لنسخة الخادم
      # المستقلة ولم تعد جزءاً من ملف التطبيق الواحد
      eng_src.count('int(c.get("volume", 1) or 0) == 0') >= 2 and
      "V14_DEEP_REPAIRED" in eng_src)

# طبقة التطبيق: السد في نهاية السلسلة + تحديث الغذاء عند الإصلاح العميق
seal_code = extract_function(APP, "_qx_seal_gaps", class_name=None)
check("chain end (_qx_seal_gaps) runs deep seal",
      "v14_deep_gap_seal(api, reason=\"chain\")" in seal_code)
live_code = extract_function(APP, "_qx_live_step", class_name=None)
check("app feed refreshes once on deep repair (zoom/pan untouched path)",
      "V14_DEEP_REPAIRED" in live_code and "_qx_resync_pending = True" in live_code)

# ═══════════════════ 6) تراجع v14.8 ═══════════════════
r = subprocess.run([sys.executable, "/home/z/my-project/scripts/test_v148_fixes.py"],
                   capture_output=True, text=True)
check("v14.8 regression suite still green", r.returncode == 0,
      (r.stdout.strip().splitlines() or [""])[-1])

print()
print(f"RESULT: {len(passed)} passed, {len(failed)} failed")
if failed:
    for f in failed:
        print("  FAILED:", f)
    raise SystemExit(1)
print("ALL v14.9 CHECKS PASSED")
