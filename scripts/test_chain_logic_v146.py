#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار تشغيلي لمنطق الواجهة (v14.6) بلا Qt:
يستخرج الدوال الحقيقية من BadiChartsStudio_live.py عبر AST وينفذها كما هي
على Backend وهمي + محرك وهمي، ويجري 4 سيناريوهات:
1) دفعة أقدم تُرفع للصفحة فوراً وتُدمج في الغذاء والمحرك
2) حماية الشمعة الحية: دفعة تحمل الشمعة الحالية لا تعيدها للخلف
3) سد الثغرات: الثقب يُسد ويُعاد الخط الكامل (لا يقص لآخر 1000)
4) seal لا يتجمد بعد محاولة فاشلة واحدة (المحاولات التحقيقية)
"""
import ast
import asyncio
import json
import time
import types

APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
src = open(APP, encoding="utf-8").read()
tree = ast.parse(src)

WANT = {"_fmt_engine_candles", "_qx_gap_holes", "_qx_chain_push_message",
        "_qx_seal_gaps", "_qx_chain_final_merge"}
collected = {}


class Visitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        for st in node.body:
            if isinstance(st, ast.FunctionDef) and st.name in WANT:
                collected[st.name] = ast.get_source_segment(src, st)
        self.generic_visit(node)


Visitor().visit(tree)
assert set(collected) == WANT, f"missing: {WANT - set(collected)}"

# نطاق تنفيذ يحاكي التبعيات المتاحة داخل التطبيق
ns = {"json": json, "time": time, "asyncio": asyncio}

# محرك وهمي يستبدل qx_server_v14 (نفس التواقيع المستعملة في الدوال)
PERIOD_SECONDS = 60
ASSET_MAX_CANDLES = 45000


def _align_time(raw_ts, period_seconds=None):
    p = period_seconds or PERIOD_SECONDS
    return ((int(raw_ts)) // p) * p


def _fill_missing_slots(candles, period_seconds=None, max_gap=1440):
    p = period_seconds or PERIOD_SECONDS
    if len(candles) < 2:
        return list(candles)
    candles = sorted(candles, key=lambda x: x['time'])
    out = [dict(candles[0])]
    for i in range(1, len(candles)):
        prev = out[-1]
        curr = candles[i]
        gap = (curr['time'] - prev['time']) // p
        if 0 < gap <= max_gap:
            slot = prev['time'] + p
            while slot < curr['time']:
                out.append({'time': slot, 'open': prev['close'], 'high': prev['close'],
                            'low': prev['close'], 'close': prev['close'], 'volume': 0})
                slot += p
        out.append(dict(curr))
    return out


class FakeAsset:
    def __init__(self, symbol):
        self.symbol = symbol
        self.api_symbol = symbol
        self.candles = []
        self.price = 0.0


STORE = {}


def _get_or_create_asset(sym):
    if sym not in STORE:
        STORE[sym] = FakeAsset(sym)
    return STORE[sym]


def _format_raw_candles(res):
    out = []
    for c in res or []:
        if not isinstance(c, dict):
            continue
        try:
            ts = int(float(c.get("time", c.get("timestamp", 0))))
            if ts <= 0:
                continue
            aligned = _align_time(ts, PERIOD_SECONDS)
            o = float(c.get("open", 0)); h = float(c.get("high", c.get("max", 0)))
            l = float(c.get("low", c.get("min", 0))); cl = float(c.get("close", 0))
            if o > 0 and h > 0 and l > 0 and cl > 0:
                out.append({'time': aligned, 'open': o, 'high': h, 'low': l,
                            'close': cl, 'volume': 5})
        except Exception:
            continue
    seen, unique = set(), []
    for c in out:
        if c['time'] not in seen:
            seen.add(c['time'])
            unique.append(c)
    unique.sort(key=lambda x: x['time'])
    return unique


def _apply_candles_to_asset(asset, candles):
    candles = _fill_missing_slots(list(candles), PERIOD_SECONDS, max_gap=1440)
    asset.candles = list(candles)
    if candles:
        asset.price = float(candles[-1]['close'])


class FakeStore:
    def __init__(self):
        self.frozen = set()

    def is_gap_filled(self, sym):
        return (sym in self.frozen, 0.0)

    def set_gap_filled(self, sym, flag, at):
        if flag:
            self.frozen.add(sym)
        else:
            self.frozen.discard(sym)


CLEAR_COUNT = {"n": 0}
FILL_CALLS = {"n": 0}


def clear_gap_flag_any(variants):
    n = 0
    for v in variants:
        if v in FROZEN_DB:
            n += 1
            FROZEN_DB.discard(v)
        # في النظام الحقيقي العلامة في الـ db فقط — هنا المصدران يتزامنان
        MT4_WRITER.store.frozen.discard(v)
    CLEAR_COUNT["n"] += 1
    return n


FROZEN_DB = set()


class FakeMT4Writer:
    def __init__(self):
        self._gap_filled = {}
        self._gap_filled_at = {}
        self.store = FakeStore()

    def load_snapshot(self, sym):
        return None

    def save_snapshot(self, sym, candles):
        pass

    def write_to_file(self, sym, period, candles):
        pass

    async def fill_gap_once(self, client, asset_obj, period):
        """نسخة مصغّرة من سلوك الآلة الأصلية: تجمّد + جلب 10 شموع + سد الناقص."""
        sym = asset_obj.symbol
        if self.store.is_gap_filled(sym)[0]:
            return
        if self._gap_filled.get(sym) and time.time() - self._gap_filled_at.get(sym, 0) < 300:
            return
        FILL_CALLS["n"] += 1
        if sym not in asset_obj.__dict__.get("_sync", {}):
            asset_obj._sync = True
        state = {"candles": list(asset_obj.candles)}
        candles = getattr(client, "recent_candles", None)
        current_period_start = _align_time(int(time.time()))
        candle_map = {c['time']: c for c in state['candles']}
        for c in candles or []:
            t = _align_time(int(c.get('time', 0)))
            if t >= current_period_start:
                continue
            if t not in candle_map:
                candle_map[t] = dict(c)
            else:
                candle_map[t] = dict(c)
        merged = sorted(candle_map.values(), key=lambda x: x['time'])[-1000:]
        merged = _fill_missing_slots(merged, PERIOD_SECONDS, max_gap=1440)
        asset_obj.candles = merged
        self._gap_filled[sym] = True
        self._gap_filled_at[sym] = time.time()
        self.store.set_gap_filled(sym, True, time.time())


class FakeClient:
    recent_candles = []


MT4_WRITER = FakeMT4Writer()
CLIENT = FakeClient()

# حلقة أحداث حقيقية في خيط خلفي (run_coroutine_threadsafe يحتاجها)
import threading
_LOOP = asyncio.new_event_loop()
threading.Thread(target=_LOOP.run_forever, daemon=True).start()


def _qx_module():
    return types.SimpleNamespace(
        _align_time=_align_time, _format_raw_candles=_format_raw_candles,
        _get_or_create_asset=_get_or_create_asset,
        _apply_candles_to_asset=_apply_candles_to_asset,
        ASSET_MAX_CANDLES=ASSET_MAX_CANDLES, PERIOD_SECONDS=PERIOD_SECONDS,
        PERIOD=1, MT4_WRITER=MT4_WRITER, CLIENT=CLIENT,
        clear_gap_flag_any=clear_gap_flag_any, ASYNC_LOOP=_LOOP)


ns.update({"_qx_module": _qx_module, "TFS": [("1m", 60)], "PERIOD_SECONDS": PERIOD_SECONDS,
           "ASSET_MAX_CANDLES": ASSET_MAX_CANDLES})

# تنفيذ الدوال الحقيقية داخل النطاق
for name, code in collected.items():
    exec(compile(code, APP, "exec"), ns)


class FakeSignal:
    def emit(self):
        pass


class Backend:
    _QX_FEED_CAP = 45000
    _QX_FEED_TRIM = 44000

    def __init__(self):
        self._candles = []
        self._qx_last_sig = None
        self._asset = "EUR/CAD (OTC)"
        self._tf = "1m"
        self._qx_symbols = {self._asset: "EURCAD_otc"}
        self._emitted = []
        self.candlesChanged = FakeSignal()
        self._logs = []

    def _emit_qx(self, obj):
        self._emitted.append(obj)

    def _log(self, kind, msg):
        self._logs.append((kind, msg))

    def _api_from_display(self, name):
        return self._qx_symbols.get(name)

    def _hist_days(self):
        return 2.0


# ربط الدوال الحقيقية بالـ Backend (الدوال الثابتة بدون ديكوريتورها في AST)
for name in WANT:
    if name in ("_fmt_engine_candles", "_qx_gap_holes"):
        setattr(Backend, name, staticmethod(ns[name]))
    else:
        setattr(Backend, name, ns[name])

b = Backend()
NOW = int(time.time())
CUR = _align_time(NOW)

# ===== السيناريو 1: دفعة أقدم (ثغرة 500 شمعة) تُرفع فوراً =====
feed = [{"t": CUR - i * 60, "o": 1.5, "h": 1.5, "l": 1.5, "c": 1.5, "v": 1}
        for i in range(0, 300)]           # آخر 300 شمعة
b._candles = feed
horizon = b._candles[0]["t"]
batch = [{"time": CUR - 800 * 60 + i * 60, "open": 1.4, "close": 1.4, "high": 1.4, "low": 1.4}
         for i in range(200)]             # دفعة أقدم بثقب ~500 شمعة
pushed_t = set()
n = b._qx_chain_push_message("EURCAD_otc", "1m", 60, batch, horizon, pushed_t,
                             lambda: True)
older_msgs = [e for e in b._emitted if e.get("type") == "older"]
assert n == 200, f"scenario1: pushed {n} != 200"
assert len(older_msgs) == 1 and len(older_msgs[0]["candles"]) == 200, "scenario1: page got batch immediately"
assert b._candles[0]["t"] == CUR - 800 * 60, "scenario1: python feed prepends batch"
assert b._qx_last_sig is not None, "scenario1: tail sig updated"
# دفعة مكررة — لا شيء يُرفع (pushed_t)
n2 = b._qx_chain_push_message("EURCAD_otc", "1m", 60, batch, horizon, pushed_t,
                              lambda: True)
assert n2 == 0, "scenario1: duplicate batch re-pushed!"
print("scenario 1 (live batch push + dedupe) PASSED")

# ===== السيناريو 2: حماية الشمعة الحية =====
a = _get_or_create_asset("EURCAD_otc")
live_candle = {"time": CUR, "open": 2.0, "high": 2.1, "low": 1.95, "close": 2.05, "volume": 9}
a.candles = [{"time": CUR - i * 60, "open": 1.5, "high": 1.5, "low": 1.5, "close": 1.5, "volume": 1}
             for i in range(1, 50)] + [live_candle]
live_batch = [{"time": CUR - 10 * 60 + i * 60, "open": 1.6, "close": 1.6, "high": 1.7, "low": 1.55}
              for i in range(10)]
live_batch.append({"time": CUR, "open": 1.0, "close": 1.0, "high": 1.0, "low": 1.0})  # لقطة قديمة للشمعة الحية
b2 = Backend()
b2._qx_chain_push_message("EURCAD_otc", "1m", 60, live_batch, 0, set(), lambda: True)
a2 = _get_or_create_asset("EURCAD_otc")
times2 = {c["time"]: c for c in a2.candles}
assert times2[CUR]["close"] == 2.05, f"scenario2 FAILED: live candle regressed to {times2[CUR]['close']}"
print("scenario 2 (live candle guard) PASSED")

# ===== السيناريو 3: سد الثغرات + إعادة الخط الكامل =====
a3 = _get_or_create_asset("USDBRL_otc")
base = [{"time": CUR - i * 60, "open": 5.0, "high": 5.0, "low": 5.0, "close": 5.0, "volume": 1}
        for i in range(0, 40)]
with_hole = [c for c in base if c["time"] != CUR - 20 * 60]   # ثقب شمعة واحدة
a3.candles = with_hole
CLIENT.recent_candles = [{"time": CUR - 20 * 60, "open": 4.9, "high": 4.95, "low": 4.85,
                          "close": 4.92, "volume": 3}]
FROZEN_DB.add("USDBRL_otc")           # علامة تجمّد قديمة بصيغة الرمز نفسه
MT4_WRITER.store.frozen.add("USDBRL_otc")
b3 = Backend()
holes_before = b3._qx_gap_holes(list(a3.candles), 60)
assert holes_before == 1, f"scenario3: holes_before={holes_before}"
b3._qx_seal_gaps("USDBRL_otc")
holes_after = b3._qx_gap_holes(list(a3.candles), 60)
assert holes_after == 0, f"scenario3 FAILED: holes after seal = {holes_after}"
tset = {c["time"] for c in a3.candles}
assert len(tset) >= 39, "scenario3: history truncated by seal!"
assert "USDBRL_otc" not in FROZEN_DB, "scenario3: freeze flag not lifted"
assert any(c["time"] == CUR - 20 * 60 and c["close"] == 4.92 for c in a3.candles), \
    "scenario3: real candle not used in seal"
print("scenario 3 (seal + full restore) PASSED")

# ===== السيناريو 4: رمز مخزّن بصيغة أخرى + محاولة فاشلة ثم نجاح =====
a4 = _get_or_create_asset("AUDCAD_otc")   # رمز الذاكرة
a4.candles = with_hole[:]                  # ثقب
FROZEN_DB.add("AUDCAD-OTC")                # العلامة بصيغة مختلفة (شرطة)
MT4_WRITER.store.frozen.clear()
MT4_WRITER._gap_filled.clear()
CLIENT.recent_candles = [{"time": CUR - 20 * 60, "open": 4.9, "high": 4.95, "low": 4.85,
                          "close": 4.92, "volume": 3}]
b4 = Backend()
b4._qx_seal_gaps("AUDCAD_otc")
assert "AUDCAD-OTC" not in FROZEN_DB, "scenario4 FAILED: variant flag not lifted"
holes4 = b4._qx_gap_holes(list(a4.candles), 60)
assert holes4 == 0, f"scenario4 FAILED: holes after seal = {holes4}"
print("scenario 4 (variant symbols) PASSED")

# ===== السيناريو 5: الدمج النهائي لا يقص التاريخ المجلوب =====
a5 = _get_or_create_asset("GBPJPY_otc")
a5.candles = [{"time": CUR - i * 60, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1}
              for i in range(0, 2000)]     # أكثر من 1000 شمعة
b5 = Backend()
b5._qx_chain_final_merge(_qx_module(), "GBPJPY_otc")
assert len(a5.candles) >= 2000 - 2, f"scenario5 FAILED: final merge truncated to {len(a5.candles)}"
print("scenario 5 (final merge keeps full history) PASSED")

print("ALL CHART-LOGIC SCENARIOS PASSED")
