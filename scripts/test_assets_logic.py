# -*- coding: utf-8 -*-
"""Smoke-test the real capture_assets_info / select_domain code extracted from the modified file."""
import ast
import json
import os
import time
from datetime import datetime
from pathlib import Path

os.makedirs("/tmp/asset_test", exist_ok=True)
os.chdir("/tmp/asset_test")

SRC = "/home/z/my-project/download/quotex_hst_server_v9_1.py"
src = open(SRC, encoding="utf-8").read()
tree = ast.parse(src)

wanted = {"_assets_num", "_assets_profit", "capture_assets_info", "_log_fed_assets_status", "select_domain"}
ns = {
    "json": json, "time": time, "datetime": datetime, "Path": Path,
    "logmsg": lambda m: print("  LOG:", m),
    "ASSET_LIST": ["EURUSD_otc", "USDJPY_otc", "GBPUSD_otc", "USDBDT_otc"],
    "ASSETS_INFO": {}, "ASSETS_UPDATED_AT": 0.0, "ASSETS_FIRST_CAPTURE": False,
    "ASSETS_JSON_FILE": Path("assets_payout.json"),
    "_ASSETS_LAST_JSON": None, "_ASSETS_LAST_LOG": 0.0,
    "FORCE_DOMAIN": "", "FORCE_COUNTRY": "",
    "DOMAIN_BANGLADESH": "market-qx.info", "DOMAIN_GLOBAL": "quotex.com",
}
found = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        code = ast.get_source_segment(src, node)
        exec(compile(code, "<extract>", "exec"), ns)
        found.append(node.name)
print("extracted functions:", sorted(found))
assert set(found) == wanted, "missing functions!"

# --- synthetic instruments payload (same shape as Quotex instruments/list) ---
entries = [
    # open asset: i[1]=symbol, i[2]=display, i[5]=payout, i[14]=open, i[18]=turbo, i[-10..-8]=profits
    [157, "EURUSD_otc", "EUR/USD (OTC)\n", 0.00001, 5, 92, 30, 0, 1, "2026-01-01", 1, 0, 0, 0, 1, 0, 0, 0, 88, 85.5, 84.2, 83.1, 1, 2, 3, 4, 5, 6, 7],
    [158, "USDJPY_otc", "USD/JPY (OTC)\n", 0.001, 3, 87, 30, 0, 1, "2026-01-01", 1, 0, 0, 0, 0, 0, 0, 0, 83, 80.0, 79.5, 78.9, 1, 2, 3, 4, 5, 6, 7],
    # realtime-candle-like entry (len 6) must be skipped
    ["EURUSD_otc", 1760000000, 1.1, 1.2, 1.0, 1.15],
]
ok = ns["capture_assets_info"](entries)
print("capture returned:", ok)
assert ok is True
info = ns["ASSETS_INFO"]
assert set(info.keys()) == {"EURUSD_otc", "USDJPY_otc"}, info.keys()
assert info["EURUSD_otc"]["payout"] == 92 and info["EURUSD_otc"]["open"] is True
assert info["EURUSD_otc"]["display"] == "EUR/USD (OTC)"
assert info["EURUSD_otc"]["turbo_payout"] == 88
assert info["EURUSD_otc"]["profit_1m"] == 84.2 and info["EURUSD_otc"]["profit_5m"] == 83.1
assert info["USDJPY_otc"]["payout"] == 87 and info["USDJPY_otc"]["open"] is False
print("parsing assertions: OK")

# JSON file written?
data = json.loads(Path("assets_payout.json").read_text(encoding="utf-8"))
assert data["total"] == 2 and data["open"] == 1 and data["closed"] == 1
assert data["assets"]["EURUSD_otc"]["payout"] == 92
print("assets_payout.json written: OK (total=2, open=1, closed=1)")

# no-change second call must NOT rewrite and must return True
snap1 = Path("assets_payout.json").read_text(encoding="utf-8")
time.sleep(0.05)
assert ns["capture_assets_info"](entries) is True
snap2 = Path("assets_payout.json").read_text(encoding="utf-8")
print("unchanged data -> no rewrite:", snap1 == snap2)

# changed payout must rewrite
entries[0][5] = 95
assert ns["capture_assets_info"](entries) is True
data = json.loads(Path("assets_payout.json").read_text(encoding="utf-8"))
assert data["assets"]["EURUSD_otc"]["payout"] == 95
print("payout change detected + rewritten: OK")

# --- domain mapping logic ---
ns["FORCE_DOMAIN"] = ""
ns["FORCE_COUNTRY"] = "BD"
assert ns["select_domain"]() == ("market-qx.info", "BD")
ns["FORCE_COUNTRY"] = "SA"
assert ns["select_domain"]() == ("quotex.com", "SA")
ns["FORCE_COUNTRY"] = ""
ns["FORCE_DOMAIN"] = "market-qx.info"
assert ns["select_domain"]() == ("market-qx.info", "manual")
ns["FORCE_DOMAIN"] = ""
print("domain mapping assertions: OK (BD->market-qx.info, SA->quotex.com, manual override works)")

print("\nALL SMOKE TESTS PASSED")
