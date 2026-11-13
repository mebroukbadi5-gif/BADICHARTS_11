#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبار وحدة لإصلاح v12: جلب قائمة العملات (آلية placeholder على مرحلتين)."""
import asyncio
import json
import os
import sys

os.chdir('/home/z/my-project/download')
sys.path.insert(0, '/home/z/my-project/download')
import qx_server_v12 as m  # noqa: E402


class StubState:
    def __init__(self):
        self.ssl_Mutual_exclusion = True
        self.ssl_Mutual_exclusion_write = False
        self.check_websocket_if_connect = 1
        self.check_accepted_connection = False


class StubAPI:
    def __init__(self):
        self.instruments = None
        self._temp_status = ""
        self._async_loop = None
        self.candle_v2_data = {}
        self.candles = m.CandlesObj()
        self.realtime_candles = {}
        self.event_registry = m.EventRegistry()
        self.last_message_at = 0.0


class StubClient:
    def __init__(self):
        self.api = StubAPI()


def make_row(asset="EURUSD_otc", name="EUR/USD (OTC)", payout=92, open_=True, turbo=88):
    """صف يشبه عناصر الخادم: i[1]=asset i[2]=name i[5]=payout i[14]=open i[18]=turbo i[-10..-8]=profits"""
    row = ["1", asset, name, 0, 0, payout]
    row += [0] * 5                      # i[6..10]
    row += [90, 89, 87]                 # i[11..13] -> i[-10], i[-9], i[-8]
    row += [open_]                      # i[14] -> open
    row += [0] * 3                      # i[15..17]
    row += [turbo]                      # i[18] -> turbo
    row += [0, 0]                       # i[19..20]
    return row


async def main():
    loop = asyncio.get_running_loop()
    cli = StubClient()
    cli.api._async_loop = loop
    m.CLIENT = cli
    ws = object.__new__(m.WebsocketClient)
    ws.api = cli.api
    ws.state = StubState()
    ws.wss = None

    inst1 = make_row("EURUSD_otc", "EUR/USD (OTC)", 92, True, 88)
    inst2 = make_row("GBPUSD_otc", "GBP/USD (OTC)", 75, False, 70)

    # ── اختبار 1: placeholder ثم إطار ثنائي يحمل القائمة (السلوك الفعلي للخادم) ──
    ph = '451-["instruments/list",{"id":"z","nsp":"/","_placeholder":true,"num":0}]'
    ws.on_message(None, ph)
    assert ws.api._temp_status != "", "FAIL 1a: placeholder not registered"
    assert ws.api.instruments is None, "FAIL 1b: placeholder wrongly stored as data"
    payload = json.dumps([inst1, inst2]).encode("utf-8")   # binary frame
    ws.on_message(None, payload)
    assert ws.api.instruments is not None and len(ws.api.instruments) == 2, \
        f"FAIL 1c: attachment not stored -> {ws.api.instruments}"
    ev = await ws.api.event_registry.wait_event("instruments_ready", timeout=2.0)
    assert isinstance(ev, list) and len(ev) == 2, f"FAIL 1d: event data wrong -> {ev}"
    assert ws.api._temp_status == "", "FAIL 1e: pending not cleared"
    print("PASS 1: placeholder + binary attachment -> stored + event fired")

    # ── اختبار 2: الصيغة المضمّنة (451- مع القائمة كاملة داخل نفس الرسالة) ──
    await ws.api.event_registry.clear_event("instruments_ready")
    ws.api.instruments = None
    inline = '451-["instruments/list",' + json.dumps([inst1, inst2, inst1]) + ']'
    ws.on_message(None, inline)
    await asyncio.sleep(0.1)  # إتاحة الفرصة للحلقة لتنفيذ set_event المجدول
    assert ws.api.instruments and len(ws.api.instruments) == 3, "FAIL 2a: inline not stored"
    ev = await ws.api.event_registry.wait_event("instruments_ready", timeout=2.0)
    assert isinstance(ev, list) and len(ev) == 3, "FAIL 2b: inline event wrong"
    print("PASS 2: inline 451- full list -> stored + event fired")

    # ── اختبار 3: إطار منفصل بصيغة {"list":[...]} ──
    await ws.api.event_registry.clear_event("instruments_ready")
    ws.api.instruments = None
    ws.api._temp_status = '451-["instruments/list",{"_placeholder":true}]'
    ws.on_message(None, json.dumps({"list": [inst1]}).encode("utf-8"))
    assert ws.api.instruments and len(ws.api.instruments) == 1, "FAIL 3: dict-list not stored"
    print("PASS 3: dict-wrapped {list:[...]} attachment")

    # ── اختبار 4: إطار منفصل بصيغة [data] (عنصر واحد) ──
    await ws.api.event_registry.clear_event("instruments_ready")
    ws.api.instruments = None
    ws.api._temp_status = '451-["instruments/list",{"_placeholder":true}]'
    ws.on_message(None, json.dumps([[inst1, inst2]]).encode("utf-8"))
    assert ws.api.instruments and len(ws.api.instruments) == 2, "FAIL 4: wrapped single not unwrapped"
    print("PASS 4: single-element wrapper unwrapped")

    # ── اختبار 5: fetch_instruments_now ترسل الطلب وتستلم عبر الحدث ──
    await ws.api.event_registry.clear_event("instruments_ready")
    sent = []
    ws.api.send_websocket_request = lambda d, no_force_send=True: sent.append(d)
    got = await m.fetch_instruments_now(timeout=3.0)
    assert '42["instruments/get"]' in sent, "FAIL 5a: request not sent"
    assert isinstance(got, list) and got, f"FAIL 5b: fetch empty -> {got}"
    print(f"PASS 5: fetch_instruments_now -> {len(got)} instruments")

    # ── اختبار 6: بناء اللقطة (payout/open/profits من المواضع الصحيحة) ──
    cli.api.instruments = [make_row("EURUSD_otc", "EUR/USD (OTC)", 92, True, 88)]
    snap = m._instruments_snapshot()
    assert snap, "FAIL 6a: empty snapshot"
    e = snap[0]
    assert e["asset"] == "EURUSD_otc", f"FAIL 6b: {e}"
    assert e["payout"] == 92 and e["turbo_payout"] == 88, f"FAIL 6c: {e}"
    assert e["open"] is True, f"FAIL 6d: {e}"
    assert e["profit_24h"] == 90 and e["profit_1m"] == 89 and e["profit_5m"] == 87, f"FAIL 6e: {e}"
    print("PASS 6: snapshot fields correct (payout/turbo/open/profits)")

    # ── اختبار 7: حفظ اللقطة + طباعة الجدول في الترمينال ──
    ok = m._save_assets_payout_file(snap)
    assert ok, "FAIL 7a: snapshot not saved"
    print("PASS 7a: qx_assets_payouts.json saved")
    print("--- terminal table preview ---")
    m._print_payout_table(snap, updated_at="2026-11-13 01:00:00")

    print("\nALL TESTS PASSED")


asyncio.run(main())
