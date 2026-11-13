#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات v14.1:
1) توجيه رد الجلب: لقطة البث الحي لا تسرق candles_ready أثناء انتظار history/load
   والرد الحقيقي (بـ index) يرفعه.
2) fetch_older_batch: دمج دفعة أقدم + إعادة المحاولة عند الرد بلا شموع أقدم.
3) سد الثغرات: علامة التجمد تُرفع تلقائياً عند وجود فجوات (الطريقة الأصلية تعمل)،
   وتبقى فعالة عند خط سليم.
4) الأعلام: كل زوج له علمان.
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, "/home/z/my-project/download")
os.chdir("/home/z/my-project/work")

import qx_server_v14 as qx  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, note=""):
    (PASS if ok else FAIL).append((name, note))
    print(f"  {'✓' if ok else '✗'} {name}" + (f"  [{note}]" if note else ""))


def mk_candles(start_ts, n, period=60):
    out = []
    for i in range(n):
        t = start_ts + i * period
        p = 1.10 + (i % 7) * 0.0005
        out.append({"time": t, "open": p, "high": p + 0.0004,
                    "low": p - 0.0004, "close": p + 0.0002, "volume": 100})
    return out


class FakeAPI:
    def __init__(self):
        self._history_pending = {}
        self._history_reply_count = 0
        self._history_stolen_suppressed = 0
        self.candle_v2_data = {}
        self.candles = qx.CandlesObj()
        self.event_registry = qx.EventRegistry()
        self._async_loop = None


class FakeClient:
    def __init__(self):
        self.api = FakeAPI()


class FakeAsset:
    def __init__(self, symbol):
        self.api_symbol = symbol
        self.symbol = symbol.replace("_otc", "-OTC")
        self.candles = []
        self.price = 0.0


async def test_router():
    print("1) توجيه رد الجلب (لا سرقة اللقطة الحية)")
    api = FakeAPI()
    loop = asyncio.get_running_loop()
    api._async_loop = loop
    # في النظام الحقيقي WebsocketClient.api هو كائن QuotexAPI نفسه
    ws = qx.WebsocketClient.__new__(qx.WebsocketClient)
    ws.api = api

    asset = "TESTUSD_otc"
    # طلب history معلّق (كما يسجّله send_websocket_request)
    api._history_pending[asset] = (12345, time.time())

    # (أ) لقطة بث حية بلا index أثناء انتظار الرد → يجب أن تُسقَط
    snap = {"asset": asset, "candles": [[1700000000, 1.1, 1.1, 1.1, 1.1]]}
    ws._process_message_and_raise_events(snap)
    await asyncio.sleep(0.15)
    ev = await api.event_registry.wait_event(f"candles_ready_{asset}", timeout=0.3)
    check("router.snapshot_suppressed", ev is None,
          f"got={'snapshot (BAD)' if ev else 'nothing (OK)'}")
    check("router.suppress_counter", api._history_stolen_suppressed == 1)

    # (ب) الرد الحقيقي بـ index → يرفع الحدثين
    reply = {"asset": asset, "index": 12345, "candles":
             [[1700000000, 1.1, 1.1005, 1.0995, 1.1002]]}
    ws._process_message_and_raise_events(reply)
    await asyncio.sleep(0.15)
    got = await api.event_registry.wait_event(f"candles_ready_{asset}", timeout=2.0)
    got_idx = await api.event_registry.wait_event(f"candles_ready_{asset}_12345", timeout=2.0)
    check("router.real_reply_fires", got is not None and got_idx is not None)
    check("router.pending_cleared", asset not in api._history_pending)
    check("router.reply_counter", api._history_reply_count == 1)

    # (ج) لقطة بث حية بلا أي طلب معلّق → سلوك أصلي متوافق (تُرفع)
    api._history_pending.pop(asset, None)
    ws._process_message_and_raise_events(snap)
    await asyncio.sleep(0.15)
    ev2 = await api.event_registry.wait_event(f"candles_ready_{asset}", timeout=2.0)
    check("router.snapshot_passes_when_idle", ev2 is not None)


async def test_older_batch():
    print("2) fetch_older_batch — دمج دفعة أقدم")
    qx.CLIENT = FakeClient()
    qx.CONNECTION_ALIVE = True
    # بذرة 300 شمعة حديثة
    now = int(time.time()) // 60 * 60
    seed = mk_candles(now - 300 * 60, 300)
    asset = qx._get_or_create_asset("OLDUSD_otc")
    qx._apply_candles_to_asset(asset, seed)

    calls = []

    async def fake_window(sym, end_time, seconds, foreground=False):
        calls.append((sym, int(end_time), int(seconds), bool(foreground)))
        # نافذة تنتهي عند before_time: 300 شمعة أقدم من end_time
        return mk_candles(int(end_time) - 300 * 60, 300)

    orig = qx._fetch_candle_window
    qx._fetch_candle_window = fake_window
    try:
        before = int(asset.candles[0]["time"])
        n = await qx.fetch_older_batch("OLDUSD_otc", before, 300)
        check("older.return_count", n == 300, f"n={n}")
        check("older.foreground", calls and calls[0][3] is True)
        check("older.merged_len", len(asset.candles) == 600, f"len={len(asset.candles)}")
        oldest = asset.candles[0]["time"]
        check("older.oldest_extended", oldest < before, f"oldest={oldest} < {before}")
        check("older.no_gaps", all(
            asset.candles[i + 1]["time"] - asset.candles[i]["time"] == 60
            for i in range(len(asset.candles) - 1)))

        # (ب) الرد بلا شموع أقدم (لقطة مسرقة — شموع حديثة حول الآن) ثم رد حقيقي
        stolen = {"hit": 0}
        now2 = int(time.time()) // 60 * 60

        async def fake_window2(sym, end_time, seconds, foreground=False):
            stolen["hit"] += 1
            if stolen["hit"] == 1:
                return mk_candles(now2 - 30, 10)   # لقطة حية: شموع حديثة فقط
            return mk_candles(int(end_time) - 300 * 60, 300)

        qx._fetch_candle_window = fake_window2
        qx._FETCH_GATE_CACHE.clear()
        before2 = int(asset.candles[0]["time"])
        n2 = await qx.fetch_older_batch("OLDUSD_otc", before2, 300)
        check("older.retry_on_stolen", n2 == 300 and stolen["hit"] == 2,
              f"n={n2} attempts={stolen['hit']}")

        # (ج) لا تاريخ فعلاً — لقطة حية دائماً → محاولتان ثم 0
        now3 = int(time.time()) // 60 * 60

        async def fake_window3(sym, end_time, seconds, foreground=False):
            return mk_candles(now3 - 30, 10)

        qx._fetch_candle_window = fake_window3
        qx._FETCH_GATE_CACHE.clear()
        before3 = int(asset.candles[0]["time"])
        n3 = await qx.fetch_older_batch("OLDUSD_otc", before3, 300)
        check("older.exhausted_returns_zero", n3 == 0, f"n={n3}")
    finally:
        qx._fetch_candle_window = orig


async def test_gap_freeze():
    print("3) سد الثغرات — الطريقة الأصلية حرفياً (تجمد أصل + سد أصل)")
    qx.CLIENT = FakeClient()
    qx.CONNECTION_ALIVE = True
    writer = qx.MT4_WRITER
    # v14.2: قاعدة مؤقتة نظيفة — اختبار حتمي بلا تلوث من candles.db المحلية
    import tempfile
    _tmpdb = os.path.join(tempfile.mkdtemp(prefix="gap_state_test_"), "candles.db")
    writer._candle_store = qx.CandleStore(_tmpdb)   # تحت الخاصية مباشرة
    sym = "GAPUSD_otc"
    derived = sym.replace("_otc", "-OTC")
    fa = FakeAsset(sym)
    now = int(time.time()) // 60 * 60

    # مسح حالة التجمد القديمة إن وجدت
    try:
        writer.candle_store.set_gap_filled(derived, False, time.time())
    except Exception:
        pass
    writer._gap_filled.pop(derived, None)
    writer._gap_filled_at.pop(derived, None)
    writer.sync_state.pop(derived, None)

    # خط سليم (بلا فجوات)
    clean = mk_candles(now - 100 * 60, 100)
    # خط به فجوة 5 دقائق
    holed = mk_candles(now - 100 * 60, 90) + mk_candles(now - 5 * 60, 5)

    # (أ) خط مجمد (filled=1 في القاعدة) → fill_gap_once يخرج فوراً —
    #     السلوك الأصلي حرفياً: «frozen - keep candles exactly as they were»
    fa.candles = list(clean)
    writer.sync_state[derived] = {"period": 1, "candles": list(clean),
                                  "last_write": 0, "last_price": clean[-1]["close"]}
    writer.candle_store.set_gap_filled(derived, True, time.time())

    fetch_calls = []

    class PatchedClient:
        api = FakeClient().api
        async def get_candles(self, asset, end_from_time, offset, period, **kw):
            fetch_calls.append(1)
            return mk_candles(int(end_from_time) - 10 * 60, 10)

    patched = PatchedClient()
    try:
        await writer.fill_gap_once(patched, fa, 1)
        check("freeze.frozen_skips", len(fetch_calls) == 0,
              f"fetches={len(fetch_calls)} (يجب 0 — الأصل يخرج فوراً)")

        # (ب) غير مجمد + فجوات حقيقية + خارج فترة التحديث (301s) →
        #     الخوارزمية الأصلية نفسها تنفذ وتسدّ الفجوات
        writer.candle_store.set_gap_filled(derived, False, time.time())
        writer._gap_filled[derived] = True
        writer._gap_filled_at[derived] = time.time() - 301
        fa.candles = list(holed)
        writer.sync_state[derived] = {"period": 1, "candles": list(holed),
                                      "last_write": 0, "last_price": holed[-1]["close"]}
        fetch_calls.clear()
        await writer.fill_gap_once(patched, fa, 1)
        check("freeze.unfrozen_runs", len(fetch_calls) >= 1,
              f"fetches={len(fetch_calls)} (الأصل نفذ بعد انقضاء فترة التحديث)")
        merged = writer.sync_state[derived]["candles"]
        has_hole = writer._scan_line_holes(merged, 60)
        check("freeze.holes_fixed", has_hole is False,
              f"candles={len(merged)} holes={'yes (BAD)' if has_hole else 'no (OK)'}")
        filled_flag, _ = writer.candle_store.is_gap_filled(derived)
        check("freeze.refrozen_after_fix", bool(filled_flag))
    finally:
        try:
            writer.candle_store.set_gap_filled(derived, False, time.time())
        except Exception:
            pass

def test_flags():
    print("4) الأعلام — زوجان = علمان")
    import re
    import urllib
    import urllib.parse
    src = open("/home/z/my-project/download/BadiChartsStudio_live.py", encoding="utf-8").read()
    ns = {"re": re, "urllib": urllib}
    m = re.search(r'(FLAGS = \{.*?def pair_flag_uri.*?'
                  r'return "data:image/svg\+xml;utf8," \+ urllib\.parse\.quote\(svg\))',
                  src, re.S)
    exec(compile(m.group(1), "<flags>", "exec"), ns)
    for k, v in re.findall(r'FLAGS\["([A-Z]{3})"\]\s*=\s*\'(.*?)\'\n', src, re.S):
        ns["FLAGS"][k] = v
    pf = ns["pair_flag_uri"]
    cases = ["USD/BRL (OTC)", "EUR/USD OTC", "USD/JPY", "GBP/JPY (OTC)",
             "AUD/NZD (OTC)", "USD/DZD (OTC)", "USD/BDT (OTC)", "USD/IDR (OTC)"]
    ok = True
    for t in cases:
        svg = urllib.parse.unquote(pf(t).split("utf8,", 1)[1])
        cells = svg.count('<g transform="translate(')
        if cells != 2:
            ok = False
            print(f"    BAD {t}: cells={cells}")
    check("flags.pairs_have_two_cells", ok)
    # الاسم الحقيقي القادم من الخادم (الأهم — كان يظهر علم واحد)
    u1 = urllib.parse.unquote(pf("USD/BRL (OTC)").split("utf8,", 1)[1])
    u2 = urllib.parse.unquote(pf("USD/BRL OTC").split("utf8,", 1)[1])
    check("flags.paren_and_plain_same_cells",
          u1.count('<g transform="translate(') == 2
          and u2.count('<g transform="translate(') == 2)



async def main():
    print("=== qx_server v14.1 tests ===")
    await test_router()
    await test_older_batch()
    await test_gap_freeze()
    test_flags()
    print()
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for name, note in FAIL:
            print(f"  FAILED: {name} [{note}]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
