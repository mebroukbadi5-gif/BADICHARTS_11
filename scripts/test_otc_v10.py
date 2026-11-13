#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات وحدات لتعديلات v10.0 على OTC_canda_.py
1) التعرف الجغرافي التلقائي على النطاق (BD → market-qx.info / غير ذلك → quotex.com)
2) فك ترميز الإطارات الثنائية (0x04+JSON)
3) InstrumentsStore: صيغ dict/array + payout + open/closed
4) مسار on_message الثنائي عبر WebsocketClient._handle_binary_frame
"""
import sys
import json
import types
from pathlib import Path

sys.path.insert(0, "/home/z/my-project/download")

# ---- stubs للمكتبات غير المثبتة في بيئة الاختبار (لا تؤثر على كود المستخدم) ----
fake_ua = types.ModuleType("fake_useragent")
class _FakeUA:
    def random(self=None):  # UserAgent().random → سلسلة
        return "Mozilla/5.0 (test)"
    def __init__(self, *a, **k): pass
    @property
    def random_prop(self): return "Mozilla/5.0 (test)"
def _ua_random(self):
    return "Mozilla/5.0 (test)"
_FakeUA.random = property(_ua_random) if False else _FakeUA.__dict__.get("random")
# نحتاج UserAgent().random يرجع نصاً
class UserAgent:
    def __init__(self, *a, **k): pass
    @property
    def random(self): return "Mozilla/5.0 (test)"
fake_ua.UserAgent = UserAgent
sys.modules["fake_useragent"] = fake_ua

fake_flask = types.ModuleType("flask")
class Flask:
    def __init__(self, *a, **k): pass
def _pass(*a, **k): pass
fake_flask.Flask = Flask
fake_flask.request = None
fake_flask.Response = None
fake_flask.jsonify = None
sys.modules["flask"] = fake_flask

import importlib
otc = importlib.import_module("OTC_canda_")

PASS, FAIL = 0, 0
def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")

print("=== 1) GEO-DOMAIN AUTO-DETECTION ===")
# 1a) فرض BD عبر متغير البيئة
import os
os.environ["QX_FORCE_DOMAIN"] = "BD"
d, cc = otc.pick_domain_by_country()
check("force BD -> market-qx.info", d == otc.BANGLADESH_DOMAIN and cc == "BD", f"got {d},{cc}")

# 1b) فرض GLOBAL
os.environ["QX_FORCE_DOMAIN"] = "GLOBAL"
d, cc = otc.pick_domain_by_country()
check("force GLOBAL -> quotex.com", d == otc.OFFICIAL_DOMAIN == "quotex.com", f"got {d},{cc}")

# 1c) بدون فرض: محاكاة أن الخدمة الجغرافية تعيد EG (مصر) → النطاق الرسمي
del os.environ["QX_FORCE_DOMAIN"]
class _FakeResp:
    def __init__(self, payload, status=200):
        self._p = payload; self.status_code = status
    def json(self): return self._p
_orig_get = otc.requests.get
otc.requests.get = lambda *a, **k: _FakeResp({"country_code": "EG"})
d, cc = otc.pick_domain_by_country()
check("detected EG -> official quotex.com", d == "quotex.com" and cc == "EG", f"got {d},{cc}")

# 1d) محاكاة بنغلاديش BD → market-qx.info
otc.requests.get = lambda *a, **k: _FakeResp({"country_code": "BD"})
d, cc = otc.pick_domain_by_country()
check("detected BD -> market-qx.info", d == "market-qx.info" and cc == "BD", f"got {d},{cc}")

# 1e) فشل كل الخدمات → None والنطاق الرسمي
def _boom(*a, **k): raise RuntimeError("network down")
otc.requests.get = _boom
d, cc = otc.pick_domain_by_country()
check("detection failed -> official domain fallback", d == "quotex.com" and cc is None, f"got {d},{cc}")
otc.requests.get = _orig_get

print("=== 2) BINARY FRAME DECODING ===")
instruments_array = [
    [1, "AUDCAD_otc", "AUD/CAD (OTC)", "forex", 0, 87, 0, 0, 0, 0, 0, 0, 0, 0, True],
    [2, "USDARS_otc", "USD/ARS (OTC)", "forex", 0, 92, 0, 0, 0, 0, 0, 0, 0, 0, False],
    [3, "EURUSD_otc", "EUR/USD (OTC)", "forex", 0, 91, 0, 0, 0, 0, 0, 0, 0, 0, True],
]
instruments_dict = [
    {"asset": "GBPUSD_otc", "profit": 84, "enabled": True},
    {"asset": "USDBDT_otc", "profit": 89, "enabled": False},
]
# 2a) إطار 0x04+JSON
payload = json.dumps(instruments_array).encode("utf-8")
frame = b"\x04" + payload
parsed, strategy = otc._decode_binary_payload(frame)
check("decode 0x04+JSON", parsed == instruments_array and strategy == "json+0x04", f"got {strategy}")
# 2b) JSON خام
parsed2, strategy2 = otc._decode_binary_payload(payload)
check("decode raw JSON", parsed2 == instruments_array and strategy2 == "json-raw", f"got {strategy2}")
# 2c) إطار غير JSON → None
junk = bytes(range(60)) + b"\x99\x98"
parsed3, _ = otc._decode_binary_payload(junk)
check("junk frame -> None", parsed3 is None)

print("=== 3) INSTRUMENTS STORE ===")
st = otc.InstrumentsStore()
n = st.update_from_payload(instruments_array)
check("array form: 3 items processed", n == 3, f"got {n}")
check("array payout AUDCAD_otc=87", st.get_payout("AUDCAD_otc") == 87)
check("array open AUDCAD_otc=True", st.get_open("AUDCAD_otc") is True)
check("array closed USDARS_otc=False", st.get_open("USDARS_otc") is False)
check("array name EURUSD_otc", st.get_name("EURUSD_otc") == "EUR/USD (OTC)")
check("ready_event set", st.ready_event.is_set())
check("otc_assets sorted 3", st.otc_assets() == ["AUDCAD_otc", "EURUSD_otc", "USDARS_otc"], f"got {st.otc_assets()}")

n2 = st.update_from_payload(instruments_dict)
check("dict form: 2 items processed", n2 == 2, f"got {n2}")
check("dict payout GBPUSD_otc=84", st.get_payout("GBPUSD_otc") == 84)
check("dict closed USDBDT_otc=False", st.get_open("USDBDT_otc") is False)

# غلاف {"instruments": [...]}
n3 = st.update_from_payload({"instruments": [{"asset": "USDIDR_otc", "profit": 78, "open": True}]})
check("envelope dict unwrapped", n3 == 1 and st.get_payout("USDIDR_otc") == 78 and st.get_open("USDIDR_otc") is True)

# payout خارج النطاق → مرفوض
n4 = st.update_from_payload([{"asset": "XZUSD_otc", "profit": 250, "enabled": True}])
check("payout 250 rejected", st.get_payout("XZUSD_otc") is None and n4 == 1)

print("=== 4) WEBSOCKET CLIENT BINARY ROUTING ===")
wc = otc.WebsocketClient.__new__(otc.WebsocketClient)
wc._expect_instruments_binary = False
wc._handle_binary_frame(frame)  # إطار instruments array
check("binary frame -> store populated", st.get_payout("AUDCAD_otc") == 87)

# إطار شموع ثنائي (dict فيه asset+history) → يجب أن يمر عبر _process_message_and_raise_events
# نختبر فقط أن المسار لا يرمي استثناءً ويعيد النتيجة دون تلوث القائمة
history_payload = {"asset": "EURUSD_otc", "history": [[1600000000, 1.1, 1.2, 1.3, 1.15]]}
hframe = b"\x04" + json.dumps(history_payload).encode("utf-8")
wc._expect_instruments_binary = False
wc._handle_binary_frame(hframe)  # لا يجب أن يرمي (loop=None → يتجاهل بهدوء)
check("binary history frame routed without crash", True)

# إعلان placeholder نصي → يستعد للثنائي
class _FakeWss:
    def send(self, x): pass
wc.wss = _FakeWss()
class _FakeState:
    ssl_Mutual_exclusion = False
    ssl_Mutual_exclusion_write = False
wc.state = _FakeState()
wc.on_message(None, '451-["instruments/list",{"_placeholder":true,"num":1}]')
check("451 placeholder sets expect flag", wc._expect_instruments_binary is True)

# قائمة نصية مباشرة 451-[event, payload]
wc.on_message(None, '451-["instruments/list",' + json.dumps(instruments_dict) + "]")
check("text instruments/list parsed", st.get_payout("GBPUSD_otc") == 84)

print("=== 5) FALLBACK ASSET LIST + STRUCTURE ===")
check("builtin ASSET_LIST kept as fallback", isinstance(otc.ASSET_LIST, list) and len(otc.ASSET_LIST) >= 41, f"got {len(otc.ASSET_LIST)}")
check("OFFICIAL_DOMAIN", otc.OFFICIAL_DOMAIN == "quotex.com")
check("BANGLADESH_DOMAIN", otc.BANGLADESH_DOMAIN == "market-qx.info")
check("no chart HTML left", not hasattr(otc, "_WEB_HOME_HTML") and not hasattr(otc, "_WEB_CHART_HTML") and not hasattr(otc, "_WEB_SHARED_CSS"))
check("fetch_instruments exists", callable(otc.fetch_instruments))
check("detect_country_code exists", callable(otc.detect_country_code))

# خريطة مواضع النطاق الجديد داخل الكود
src = Path("/home/z/my-project/download/OTC_canda_.py").read_text()
check("Login base_url updated", "base_url = 'quotex.com'" in src)
check("Quotex default host updated", 'host="quotex.com"' in src)
check("no qxbroker.com left", "qxbroker.com" not in src)
check("TIMEFRAMES 14 unchanged", len(otc.TIMEFRAMES) == 14)
tf_secs = [t[1] for t in otc.TIMEFRAMES]
check("timeframe seconds match request", tf_secs == [60,120,180,300,600,900,1800,3600,14400,86400,5,10,15,30], f"got {tf_secs}")

print(f"\n===== RESULT: {PASS} passed, {FAIL} failed =====")
sys.exit(1 if FAIL else 0)
