# Smoke tests for the new FIX L mechanisms in quotex_mt4_server_v10.py
import sys, json, asyncio, types
sys.path.insert(0, '/home/z/my-project/download')

import importlib.util
spec = importlib.util.spec_from_file_location("qxsrv", '/home/z/my-project/download/quotex_mt4_server_v10.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("[1] module imported OK")

ws = mod.WebsocketClient.__new__(mod.WebsocketClient)  # bypass __init__ (needs api)

# --- official replay-server sample row (tests/fakes/ws_replay_server.py) ---
sample = '42["instruments/list",[[1,"EURUSD","EUR/USD","forex",4,84,60,30,3,1,0,0,[],1,true]]]'
rows = ws._normalize_instrument_rows(json.loads(sample[2:])[1])
assert len(rows) == 1 and rows[0][1] == "EURUSD", rows
parts = mod.Quotex._row_parts(rows[0])
assert parts[0] == "EURUSD" and parts[2] == 84 and parts[4] is True, parts
print(f"[2] array row OK -> symbol={parts[0]} payout={parts[2]} open={parts[4]}")

# --- dict form (quotex.com interceptor shape) ---
dict_payload = [{"asset": "USDARS_otc", "profit": 92, "enabled": True},
                {"asset": "EURUSD_otc", "profit": 87, "enabled": False}]
rows2 = ws._normalize_instrument_rows(dict_payload)
p2 = mod.Quotex._row_parts(rows2[1])
assert p2[0] == "EURUSD_otc" and p2[2] == 87 and p2[4] is False, p2
assert len(rows2[1]) == 19  # canonical length
print(f"[3] dict row OK -> symbol={p2[0]} payout={p2[2]} open={p2[4]}")

# --- get_payment report ---
class FakeAPI:
    instruments = rows2
    _instruments_expected = False
    _temp_status = ""
    _async_loop = None
class FakeQuotex:
    api = FakeAPI()
    codes_asset = {}
    _row_parts = staticmethod(mod.Quotex._row_parts)
fq = FakeQuotex()
import types as _t
fq.get_payment = _t.MethodType(mod.Quotex.get_payment, fq)
fq.get_payout = _t.MethodType(mod.Quotex.get_payout, fq)
report = fq.get_payment()
assert report["USDARS_otc"]["payout"] == 92 and report["USDARS_otc"]["open"] is True
assert report["EURUSD_otc"]["payout"] == 87 and report["EURUSD_otc"]["open"] is False
assert fq.get_payout("USDARS_otc") == 92
assert fq.get_payout("UNKNOWN") == 0
print(f"[4] get_payment OK -> {report}")

# --- full capture pipeline with a live event loop + real EventRegistry ---
async def capture_pipeline():
    reg = mod.EventRegistry()
    api = types.SimpleNamespace(
        instruments=None, _instruments_expected=False, _temp_status="",
        _async_loop=asyncio.get_running_loop(), event_registry=reg)
    ws.api = api

    # placeholder announcement then payload frame (451- pattern)
    ws._capture_instruments_text('451-["instruments/list",{"_placeholder":true,"num":0}]')
    assert api._instruments_expected is True
    ws._capture_instruments_text('0[[1,"EURUSD","EUR/USD","forex",4,84,60,30,3,1,0,0,[],1,true]]')
    got = await reg.wait_event('instruments_ready', timeout=2)
    assert got and got[0][1] == "EURUSD" and got[0][5] == 84, got
    assert api._instruments_expected is False
    print("[5] placeholder -> payload OK")

    # direct event frame
    await reg.clear_event('instruments_ready')
    api.instruments = None
    ws._capture_instruments_text('42["instruments/list",[[2,"GBPUSD_otc","GBP/USD OTC\\n","forex",5,91,60,30,3,1,0,0,[],1,true]]]')
    got2 = await reg.wait_event('instruments_ready', timeout=2)
    assert got2 and got2[0][1] == "GBPUSD_otc", got2
    print("[6] direct frame OK")

    # binary frame with 0x04 marker (quotex.com style)
    await reg.clear_event('instruments_ready')
    api.instruments = None
    api._instruments_expected = False
    bin_payload = b'\x04[[3,"XAUUSD_otc","GOLD OTC","commodity",3,86,60,30,3,1,0,0,[],1,false]]'
    ws._capture_instruments_binary(bin_payload)
    got3 = await reg.wait_event('instruments_ready', timeout=2)
    assert got3 and got3[0][1] == "XAUUSD_otc" and got3[0][5] == 86, got3
    print("[7] binary 0x04 frame OK")

    # candle dict must NOT be stored while expecting instruments
    await reg.clear_event('instruments_ready')
    api.instruments = None
    api._instruments_expected = True
    ws._capture_instruments_text('{"asset":"EURUSD_otc","candles":[[1,2,3,4,5]]}')
    assert api.instruments is None, "candle dict wrongly stored as instruments!"
    print("[8] candle dict NOT captured as instruments OK")

asyncio.run(capture_pipeline())

# --- geographic detection (country-level only) ---
code = mod.detect_country_code(timeout=6)
print(f"[9] detect_country_code -> {code!r}")
host = mod.auto_select_domain("market-qx.info")
print(f"[10] auto_select_domain -> {host}")
if code == "BD":
    assert host == "market-qx.info"
elif code:
    assert host == "quotex.com"
else:
    assert host == "market-qx.info"  # detection failed -> saved host fallback
print("[11] domain logic consistent with country")

# --- frame timeframes sanity ---
tf = [t[1] for t in mod.TIMEFRAMES]
assert tf == [60,120,180,300,600,900,1800,3600,14400,86400,5,10,15,30]
labels = [t[2].split()[0] for t in mod.TIMEFRAMES]
print(f"[12] TIMEFRAMES OK -> {labels}")

print("\nALL SMOKE TESTS PASSED")
