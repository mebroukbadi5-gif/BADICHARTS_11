# -*- coding: utf-8 -*-
"""Apply remaining edits to quotex_hst_server_v9_1.py with exact-match verification."""
import sys

PATH = "/home/z/my-project/download/quotex_hst_server_v9_1.py"

data = open(PATH, "r", encoding="utf-8").read()

REPLACEMENTS = []

# E2: instruments_pending init in QuotexAPI.__init__
REPLACEMENTS.append((
    """        self.instruments = None
        self.host = host""",
    """        self.instruments = None
        self.instruments_pending = False   # ASSETS: \u064a\u0646\u062a\u0638\u0631 \u0625\u0637\u0627\u0631 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0628\u0639\u062f placeholder \u0627\u0644\u062e\u0627\u0635 \u0628\u0640 instruments/list
        self.host = host""",
))

# E3: on_message capture branch
REPLACEMENTS.append((
    """            message = None
            if len(msg_str) > 1 and msg_str[1] in ('[', '{'):
                try:
                    message = json.loads(msg_str[1:])
                except Exception:
                    pass

            if message is not None:
                self._process_message_and_raise_events(message)""",
    """            message = None
            if len(msg_str) > 1 and msg_str[1] in ('[', '{'):
                try:
                    message = json.loads(msg_str[1:])
                except Exception:
                    pass

            # ===== ASSETS LIST + PAYOUT + OPEN/CLOSED (\u0622\u0644\u064a\u0629 \u0627\u0644\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0631\u0633\u0645\u064a\u0629 pyquotex) =====
            # \u0627\u0644\u0633\u064a\u0631\u0641\u0631 \u064a\u0631\u062f \u0639\u0644\u0649 42["instruments/get"] \u0628\u0640:
            #   451-["instruments/list",[...]]  (\u0625\u0637\u0627\u0631 \u0645\u0628\u0627\u0634\u0631)
            #   \u0623\u0648 51-["instruments/list",{"_placeholder":true,...}] \u062b\u0645 \u0625\u0637\u0627\u0631 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0628\u0639\u062f\u0647
            # \u0645\u0644\u0627\u062d\u0638\u0629: on_open \u0648 keepalive_loop \u064a\u0631\u0633\u0644\u0627\u0646 instruments/get \u0623\u0635\u0644\u0627\u064b \u2014
            # \u0627\u0644\u0643\u0648\u062f \u0627\u0644\u0642\u062f\u064a\u0645 \u0643\u0627\u0646 \u064a\u062a\u062c\u0627\u0647\u0644 \u0627\u0644\u0631\u062f \u062a\u0645\u0627\u0645\u0627\u064b\u061b \u0627\u0644\u0622\u0646 \u0646\u0644\u062a\u0637\u0642\u0647 \u0648\u0646\u0633\u062a\u062e\u0631\u062c \u0645\u0646\u0647:
            # \u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0639\u0645\u0644\u0627\u062a \u0627\u0644\u0643\u0627\u0645\u0644\u0629 + \u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 (payout) + \u062d\u0627\u0644\u0629 \u0627\u0644\u0632\u0648\u062c (\u0645\u0641\u062a\u0648\u062d/\u0645\u063a\u0644\u0642)
            try:
                if "instruments/list" in msg_str:
                    if "_placeholder" in msg_str:
                        if self.api is not None:
                            self.api.instruments_pending = True
                    else:
                        self._capture_instruments_frame(msg_str, message)
            except Exception:
                pass

            if message is not None:
                self._process_message_and_raise_events(message)""",
))

# E4: fulfillment gate inside _process_message_and_raise_events
REPLACEMENTS.append((
    """    def _process_message_and_raise_events(self, message):
        try:
            loop = self.api._async_loop
            if loop is None or not loop.is_running():
                return""",
    """    def _process_message_and_raise_events(self, message):
        try:
            loop = self.api._async_loop
            if loop is None or not loop.is_running():
                return

            # ===== ASSETS: \u0625\u0637\u0627\u0631 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0630\u064a \u064a\u0644\u064a placeholder \u0627\u0644\u062e\u0627\u0635 \u0628\u0640 instruments/list =====
            # (\u0646\u0641\u0633 \u0645\u0646\u0637\u0642 pyquotex \u0627\u0644\u0631\u0633\u0645\u064a: _temp_status \u064a\u062d\u0645\u0644 \u0646\u0648\u0639 \u0627\u0644\u062d\u062f\u062b \u062b\u0645 \u0627\u0644\u0625\u0637\u0627\u0631 \u0627\u0644\u062a\u0627\u0644\u064a \u064a\u062d\u0645\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a)
            if getattr(self.api, "instruments_pending", False):
                data = None
                if isinstance(message, list) and len(message) == 1 and isinstance(message[0], list):
                    data = message[0]
                elif isinstance(message, list) and message and isinstance(message[0], list):
                    data = message
                elif isinstance(message, dict) and "list" in message:
                    data = message["list"]
                if data and isinstance(data, list) and data:
                    first = data[0]
                    # \u0625\u062f\u062e\u0627\u0644 instruments: \u0642\u0627\u0626\u0645\u0629 >= 19 \u0639\u0646\u0635\u0631\u0627\u064b \u0648\u0639\u0646\u0635\u0631\u0647\u0627 \u0627\u0644\u062b\u0627\u0646\u064a \u0631\u0645\u0632 \u0646\u0635\u064a (\u0645\u062b\u0644 "EURUSD_otc")
                    # \u0625\u0637\u0627\u0631\u0627\u062a \u0627\u0644\u0634\u0645\u0648\u0639 \u0627\u0644\u062d\u064a\u0629 \u0639\u0646\u0627\u0635\u0631\u0647\u0627 \u0628\u0637\u0648\u0644 4 \u0641\u0642\u0637 \u2014 \u0644\u0627 \u062a\u062a\u0637\u0627\u0628\u0642 \u0645\u0639 \u0647\u0630\u0627 \u0627\u0644\u0634\u0631\u0637
                    if isinstance(first, (list, tuple)) and len(first) >= 19 and isinstance(first[1], str):
                        self._store_instruments(data)""",
))

# E5: capture/store methods on WebsocketClient
REPLACEMENTS.append((
    """        except Exception as e:
            logger.debug(f"Error processing message: {e}")

    def on_error(self, wss, error):""",
    """        except Exception as e:
            logger.debug(f"Error processing message: {e}")

    # ===== ASSETS LIST + PAYOUT + OPEN/CLOSED (\u0646\u0641\u0633 \u0622\u0644\u064a\u0629 \u0627\u0644\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0631\u0633\u0645\u064a\u0629 pyquotex) =====
    def _capture_instruments_frame(self, msg_str, message):
        \"\"\"\u0627\u0644\u062a\u0642\u0627\u0637 \u0631\u062f instruments/list \u0627\u0644\u0645\u0628\u0627\u0634\u0631 (\u0645\u062b\u0644 451-["instruments/list",[...]]).\"\"\"
        data = None
        if isinstance(message, list) and len(message) >= 2 and isinstance(message[0], str) and message[0] == "instruments/list":
            data = message[1]
        else:
            start_idx = -1
            for idx, ch in enumerate(msg_str):
                if ch in ("[", "{"):
                    start_idx = idx
                    break
            if start_idx != -1:
                try:
                    parsed = json.loads(msg_str[start_idx:])
                except Exception:
                    return
                if isinstance(parsed, list) and len(parsed) >= 2 and isinstance(parsed[0], str) and parsed[0] == "instruments/list":
                    data = parsed[1]
        if data is not None:
            self._store_instruments(data)

    def _store_instruments(self, data):
        \"\"\"\u062a\u062e\u0632\u064a\u0646 \u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0623\u0635\u0648\u0644 \u0648\u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0645\u0646\u0647\u0627: \u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 + \u062d\u0627\u0644\u0629 \u0627\u0644\u0632\u0648\u062c (\u0645\u0641\u062a\u0648\u062d/\u0645\u063a\u0644\u0642).\"\"\"
        if isinstance(data, dict) and "list" in data:
            data = data["list"]
        if isinstance(data, list) and data:
            entries = [i for i in data if isinstance(i, (list, tuple)) and len(i) >= 19 and isinstance(i[1], str)]
            if entries:
                if self.api is not None:
                    self.api.instruments = entries
                    self.api.instruments_pending = False
                capture_assets_info(entries)

    def on_error(self, wss, error):""",
))

# E6: implement get_all_assets + get_payment + check_asset_open + get_payout
REPLACEMENTS.append((
    """    async def get_all_assets(self):
        return {}""",
    """    async def get_all_assets(self):
        # ASSETS: \u0646\u0641\u0633 \u0633\u0644\u0648\u0643 pyquotex \u0627\u0644\u0631\u0633\u0645\u064a get_all_assets -> {\u0627\u0644\u0631\u0645\u0632: \u0627\u0644\u0643\u0648\u062f \u0627\u0644\u062f\u0627\u062e\u0644\u064a}
        if self.api and self.api.instruments:
            for i in self.api.instruments:
                if isinstance(i, (list, tuple)) and len(i) > 1 and i[0] != "":
                    self.codes_asset[i[1]] = i[0]
            return dict(self.codes_asset)
        return {}

    def get_payment(self):
        # ASSETS: \u0646\u0633\u0628 \u0627\u0644\u062f\u0641\u0639 + \u062d\u0627\u0644\u0629 \u0643\u0644 \u0627\u0644\u0623\u0635\u0648\u0644 \u0645\u0646 \u0642\u0627\u0626\u0645\u0629 instruments (\u0646\u0641\u0633 \u0633\u0644\u0648\u0643 pyquotex \u0627\u0644\u0631\u0633\u0645\u064a get_payment)
        if self.api is None or not self.api.instruments:
            return {}
        assets_data = {}
        for i in self.api.instruments:
            try:
                if not isinstance(i, (list, tuple)) or len(i) < 19:
                    continue
                name = i[2].replace("\\n", "") if isinstance(i[2], str) else str(i[1])
                assets_data[name] = {
                    "turbo_payment": i[18],
                    "payment": i[5],
                    "profit": {"1M": i[-9], "5M": i[-8]},
                    "open": i[14],
                }
            except Exception:
                continue
        return assets_data

    async def check_asset_open(self, asset_name):
        # ASSETS: \u0641\u062d\u0635 \u062d\u0627\u0644\u0629 \u0632\u0648\u062c \u0645\u062d\u062f\u062f -> (\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0632\u0648\u062c \u0627\u0644\u0643\u0627\u0645\u0644\u0629\u060c (\u0627\u0644\u0643\u0648\u062f\u060c \u0627\u0644\u0627\u0633\u0645\u060c \u0645\u0641\u062a\u0648\u062d\u061f))
        # (\u0646\u0641\u0633 \u0633\u0644\u0648\u0643 pyquotex \u0627\u0644\u0631\u0633\u0645\u064a check_asset_open)
        instruments = self.api.instruments if (self.api and self.api.instruments) else []
        for i in instruments:
            if isinstance(i, (list, tuple)) and len(i) > 14 and asset_name == i[1]:
                if self.api:
                    self.api.current_asset = asset_name
                display = i[2].replace("\\n", "") if isinstance(i[2], str) else i[2]
                return i, (i[0], display, i[14])
        return None, (None, None, None)

    async def get_payout(self, asset=None):
        # ASSETS: \u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 \u0644\u0632\u0648\u062c \u0645\u062d\u062f\u062f\u060c \u0623\u0648 \u0642\u0627\u0645\u0648\u0633 {\u0627\u0644\u0631\u0645\u0632: payout} \u0644\u0643\u0644 \u0627\u0644\u0623\u0632\u0648\u0627\u062c \u0625\u0630\u0627 \u0644\u0645 \u064a\u064f\u062d\u062f\u062f
        if asset:
            raw, _ = await self.check_asset_open(asset)
            if raw is not None:
                return _assets_num(raw[5])
            return 0
        return {s: v["payout"] for s, v in ASSETS_INFO.items()}""",
))

# E7: get_saved_host default + set_saved_host
REPLACEMENTS.append((
    """    def get_saved_host(self) -> str:
        # FIX K:
        return self.state.get("host", "qxbroker.com")""",
    """    def get_saved_host(self) -> str:
        # FIX K:
        return self.state.get("host", "quotex.com")

    def set_saved_host(self, host: str):
        # DOMAIN: \u062d\u0641\u0638 \u0627\u0644\u0646\u0637\u0627\u0642 \u0627\u0644\u0645\u062e\u062a\u0627\u0631 \u062a\u0644\u0642\u0627\u0626\u064a\u0627\u064b \u062d\u0633\u0628 \u0627\u0644\u0628\u0644\u062f \u062d\u062a\u0649 \u062a\u062a\u0637\u0627\u0628\u0642 \u0645\u0639\u0647 \u0625\u0639\u0627\u062f\u0629 \u0627\u0644\u0627\u062a\u0635\u0627\u0644 \u0644\u0627\u062d\u0642\u0627\u064b
        try:
            self.state["host"] = host
            self._save_state()
        except Exception:
            pass""",
))

# E8: SessionManager state default host
REPLACEMENTS.append((
    """        return {"last_login": 0, "last_success": False, "failed_auth_count": 0, "email": "", "host": "qxbroker.com"}""",
    """        return {"last_login": 0, "last_success": False, "failed_auth_count": 0, "email": "", "host": "quotex.com"}""",
))

# E9: ASSETS_INFO globals + capture functions before ASSET_LIST
REPLACEMENTS.append((
    """session_manager = SessionManager()

# ==============================================================================
# UPDATED ASSET LIST & CANDLE COUNT SETTINGS
# ==============================================================================""",
    """session_manager = SessionManager()

# ==============================================================================
# ASSETS LIST + PAYOUT + OPEN/CLOSED \u2014 \u0622\u0644\u064a\u0629 \u0627\u0644\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0631\u0633\u0645\u064a\u0629 pyquotex
# ==============================================================================
# \u0627\u0644\u0633\u064a\u0631\u0641\u0631 \u064a\u0631\u0633\u0644 \u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0623\u0635\u0648\u0644 \u0627\u0644\u0643\u0627\u0645\u0644\u0629 \u0639\u0628\u0631 \u062d\u062f\u062b WebSocket "instruments/list"
# (\u0631\u062f\u0627\u064b \u0639\u0644\u0649 42["instruments/get"] \u0627\u0644\u062a\u064a \u064a\u0631\u0633\u0644\u0647\u0627 on_open \u0648 keepalive_loop \u0643\u0644 15 \u062b\u0627\u0646\u064a\u0629).
# \u0628\u0646\u064a\u0629 \u0643\u0644 \u0625\u062f\u062e\u0627\u0644 (\u0643\u0645\u0627 \u0641\u064a pyquotex \u0627\u0644\u0631\u0633\u0645\u064a _api/assets.py):
#   i[1]   = \u0631\u0645\u0632 \u0627\u0644\u0632\u0648\u062c (\u0645\u062b\u0627\u0644: EURUSD_otc)
#   i[2]   = \u0627\u0644\u0627\u0633\u0645 \u0627\u0644\u0638\u0627\u0647\u0631
#   i[5]   = \u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 payout %
#   i[14]  = \u062d\u0627\u0644\u0629 \u0627\u0644\u0632\u0648\u062c: 1 = \u0645\u0641\u062a\u0648\u062d / 0 = \u0645\u063a\u0644\u0642
#   i[18]  = \u062f\u0641\u0639 \u0627\u0644\u062a\u0631\u0628\u0648 turbo %
#   i[-10], i[-9], i[-8] = \u0646\u0633\u0628 \u0627\u0644\u0623\u0631\u0628\u0627\u062d 24H / 1M / 5M
ASSETS_INFO = {}              # {symbol: {"display","payout","turbo_payout","profit_24h","profit_1m","profit_5m","open"}}
ASSETS_UPDATED_AT = 0.0
ASSETS_FIRST_CAPTURE = False
ASSETS_JSON_FILE = Path("assets_payout.json")
_ASSETS_LAST_JSON = None
_ASSETS_LAST_LOG = 0.0

def _assets_num(val, default=0):
    try:
        return int(round(float(val))) if val is not None else default
    except (TypeError, ValueError):
        return default

def _assets_profit(row, idx):
    try:
        v = row[idx]
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None

def capture_assets_info(entries):
    \"\"\"
\u064a\u062e\u0632\u0646 \u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0639\u0645\u0644\u0627\u062a \u0627\u0644\u0643\u0627\u0645\u0644\u0629 + \u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 + \u062d\u0627\u0644\u0629 \u0627\u0644\u0632\u0648\u062c (\u0645\u0641\u062a\u0648\u062d/\u0645\u063a\u0644\u0642).

    - \u064a\u062d\u062f\u0651\u062b \u0627\u0644\u0642\u0627\u0645\u0648\u0633 \u0627\u0644\u0639\u0627\u0645 ASSETS_INFO \u0644\u0644\u0627\u0633\u062a\u062e\u062f\u0627\u0645 \u062f\u0627\u062e\u0644 \u0627\u0644\u0643\u0648\u062f
    - \u064a\u062d\u0641\u0638 \u0646\u0633\u062e\u0629 \u0643\u0627\u0645\u0644\u0629 \u0641\u064a assets_payout.json (\u0641\u0642\u0637 \u0639\u0646\u062f \u062a\u063a\u064a\u0651\u0631 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a)
    - \u0639\u0646\u062f \u0623\u0648\u0644 \u0627\u0633\u062a\u0644\u0627\u0645 \u064a\u0637\u0628\u0639 \u062d\u0627\u0644\u0629 \u0627\u0644\u0623\u0632\u0648\u0627\u062c \u0627\u0644\u062a\u064a \u064a\u063a\u0630\u064a\u0647\u0627 \u0627\u0644\u0633\u0631\u0641\u0631 \u0644\u0640 MT4
    \"\"\"
    global ASSETS_UPDATED_AT, ASSETS_FIRST_CAPTURE, _ASSETS_LAST_JSON, _ASSETS_LAST_LOG
    if not isinstance(entries, list) or not entries:
        return False
    parsed = {}
    for i in entries:
        try:
            if not isinstance(i, (list, tuple)) or len(i) < 19:
                continue
            symbol = str(i[1] or "").strip()
            if not symbol:
                continue
            open_flag = i[14]
            if isinstance(open_flag, str):
                open_flag = open_flag.strip().lower() not in ("", "0", "false")
            else:
                open_flag = bool(open_flag)
            parsed[symbol] = {
                "display": str(i[2] or "").replace("\\n", " ").strip(),
                "payout": _assets_num(i[5]),
                "turbo_payout": _assets_num(i[18]),
                "profit_24h": _assets_profit(i, -10),
                "profit_1m": _assets_profit(i, -9),
                "profit_5m": _assets_profit(i, -8),
                "open": open_flag,
            }
        except Exception:
            continue
    if not parsed:
        return False
    now = time.time()
    ASSETS_INFO.clear()
    ASSETS_INFO.update(parsed)
    ASSETS_UPDATED_AT = now
    n_open = sum(1 for v in ASSETS_INFO.values() if v["open"])
    n_closed = len(ASSETS_INFO) - n_open
    try:
        payload_text = json.dumps(parsed, ensure_ascii=False, indent=2)
        if payload_text != _ASSETS_LAST_JSON:
            snapshot = {
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "epoch": int(now),
                "total": len(parsed),
                "open": n_open,
                "closed": n_closed,
                "assets": parsed,
            }
            ASSETS_JSON_FILE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
            logmsg(f"[assets] full list saved: {len(parsed)} assets | open={n_open} | closed={n_closed} -> {ASSETS_JSON_FILE.name}")
            _ASSETS_LAST_LOG = now
        elif now - _ASSETS_LAST_LOG >= 600:
            logmsg(f"[assets] payout status unchanged (open={n_open}, closed={n_closed})")
            _ASSETS_LAST_LOG = now
        _ASSETS_LAST_JSON = payload_text
    except Exception as e:
        logmsg(f"[assets] failed to save {ASSETS_JSON_FILE.name}: {e}")
    if not ASSETS_FIRST_CAPTURE:
        ASSETS_FIRST_CAPTURE = True
        _log_fed_assets_status()
    return True

def _log_fed_assets_status():
    \"\"\"
\u0637\u0628\u0627\u0639\u0629 \u062d\u0627\u0644\u0629 (\u0646\u0633\u0628\u0629 \u0627\u0644\u062f\u0641\u0639 + \u0645\u0641\u062a\u0648\u062d/\u0645\u063a\u0644\u0642) \u0644\u0644\u0623\u0632\u0648\u0627\u062c \u0627\u0644\u062a\u064a \u064a\u063a\u0630\u064a\u0647\u0627 \u0627\u0644\u0633\u0631\u0641\u0631 \u0625\u0644\u0649 MT4 \u2014 \u0645\u0631\u0629 \u0648\u0627\u062d\u062f\u0629 \u0639\u0646\u062f \u0623\u0648\u0644 \u0627\u0633\u062a\u0644\u0627\u0645.\"\"\"
    try:
        rows = []
        for s in ASSET_LIST:
            info = ASSETS_INFO.get(s)
            if info:
                state = "OPEN" if info["open"] else "CLOSED"
                rows.append(f"{s}={info['payout']}%[{state}]")
        for chunk_start in range(0, len(rows), 8):
            logmsg("[assets] fed pairs: " + " ".join(rows[chunk_start:chunk_start + 8]))
    except Exception:
        pass

# ==============================================================================
# UPDATED ASSET LIST & CANDLE COUNT SETTINGS
# ==============================================================================""",
))

# E10: Quotex.__init__ default host
REPLACEMENTS.append((
    """    def __init__(self, email=None, password=None, host="qxbroker.com", lang="en", proxies=None, user_data_dir="browser", asset_default="EURUSD", period_default=60):""",
    """    def __init__(self, email=None, password=None, host="quotex.com", lang="en", proxies=None, user_data_dir="browser", asset_default="EURUSD", period_default=60):""",
))

# E11a: DOMAINS block -> geo selection (ASCII part)
REPLACEMENTS.append((
    """# ===== FIX K: Quotex =====
# Domain list. Labels are intentionally NEUTRAL (no country/region labels) so
# no user feels singled out. Just the domain name as the broker publishes it.
DOMAINS = [
    ("qxbroker.com",    "qxbroker.com"),
    ("market-qx.info",  "market-qx.info"),
]""",
    """# ===== FIX K: Quotex =====
# \u0627\u062e\u062a\u064a\u0627\u0631 \u0627\u0644\u0646\u0637\u0627\u0642 \u062a\u0644\u0642\u0627\u0626\u064a\u0627\u064b \u062d\u0633\u0628 \u0627\u0644\u0628\u0644\u062f (\u0643\u0634\u0641 \u0639\u0628\u0631 IP \u0639\u0644\u0649 \u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062f\u0648\u0644\u0629 \u0641\u0642\u0637 \u2014 \u0628\u062f\u0648\u0646 \u0623\u064a \u0645\u0648\u0642\u0639 \u062f\u0642\u064a\u0642)
#   \u0628\u0646\u063a\u0644\u0627\u062f\u064a\u0634       -> market-qx.info
#   \u0623\u064a \u062f\u0648\u0644\u0629 \u0623\u062e\u0631\u0649   -> quotex.com (\u0627\u0644\u0631\u0633\u0645\u064a \u0627\u0644\u0639\u0627\u0644\u0645\u064a)
# \u062a\u062c\u0627\u0648\u0632 \u064a\u062f\u0648\u064a \u0627\u062e\u062a\u064a\u0627\u0631\u064a \u0628\u062f\u0648\u0646 \u062a\u0639\u062f\u064a\u0644 \u0627\u0644\u0643\u0648\u062f (\u0645\u062a\u063a\u064a\u0631\u0627\u062a \u0628\u064a\u0626\u0629):
#   set QX_FORCE_DOMAIN=market-qx.info
#   set QX_FORCE_COUNTRY=BD
DOMAIN_BANGLADESH = "market-qx.info"
DOMAIN_GLOBAL = "quotex.com"
FORCE_DOMAIN = os.environ.get("QX_FORCE_DOMAIN", "").strip().lower().replace("https://", "").replace("http://", "").strip("/")
FORCE_COUNTRY = os.environ.get("QX_FORCE_COUNTRY", "").strip().upper()

# \u0645\u0632\u0648\u0651\u062f\u0648 \u0643\u0634\u0641 \u0627\u0644\u0628\u0644\u062f \u0639\u0628\u0631 IP \u2014 \u064a\u064f\u0642\u0631\u0623 \u0631\u0645\u0632 \u0627\u0644\u062f\u0648\u0644\u0629 (\u062d\u0631\u0641\u0627\u0646) \u0641\u0642\u0637 \u0648\u0644\u0627 \u064a\u064f\u0637\u0644\u0628 \u0623\u064a \u0645\u0648\u0642\u0639 \u062f\u0642\u064a\u0642
_GEO_PROVIDERS = (
    ("https://ipapi.co/json/", "country_code"),
    ("https://ipinfo.io/json", "country"),
    ("http://ip-api.com/json/?fields=status,countryCode", "countryCode"),
)

def detect_country_code(timeout=6):
    \"\"\"
\u0643\u0634\u0641 \u0627\u0644\u0628\u0644\u062f \u0639\u0628\u0631 IP \u2014 \u064a\u0639\u064a\u062f \u0631\u0645\u0632 \u0627\u0644\u062f\u0648\u0644\u0629 (\u0645\u062b\u0644 BD) \u0623\u0648 \u0646\u0635 \u0641\u0627\u0631\u063a \u0639\u0646\u062f \u0627\u0644\u0641\u0634\u0644.\"\"\"
    for url, field in _GEO_PROVIDERS:
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
            if resp.status_code != 200:
                continue
            data = resp.json()
            cc = data.get(field, "") or ""
            if isinstance(cc, dict):
                cc = cc.get("country", "") or ""
            cc = str(cc).strip().upper()
            if len(cc) == 2 and cc.isalpha():
                return cc
        except Exception:
            continue
    return ""

def select_domain():
    \"\"\"
\u064a\u0639\u064a\u062f (\u0627\u0644\u0646\u0637\u0627\u0642\u060c \u0631\u0645\u0632 \u0627\u0644\u0628\u0644\u062f):
\u0628\u0646\u063a\u0644\u0627\u062f\u064a\u0634 -> market-qx.info / \u0623\u064a \u062f\u0648\u0644\u0629 \u0623\u062e\u0631\u0649 -> quotex.com (\u0627\u0644\u0631\u0633\u0645\u064a \u0627\u0644\u0639\u0627\u0644\u0645\u064a).\"\"\"
    if FORCE_DOMAIN:
        return FORCE_DOMAIN, "manual"
    country = FORCE_COUNTRY or detect_country_code()
    if country == "BD":
        return DOMAIN_BANGLADESH, country
    return DOMAIN_GLOBAL, (country or "unknown")""",
))

# E11b: QX_HOST default line
REPLACEMENTS.append((
    """QX_HOST = "qxbroker.com\"""",
    """QX_HOST = DOMAIN_GLOBAL""",
))

# E12: STAGE 4 menu -> auto selection
REPLACEMENTS.append((
    """    saved_host = session_manager.get_saved_host()
    print()
    print(f"{Colors.BOLD}  Select Domain{Colors.RESET}")
    for i, (host, label) in enumerate(DOMAINS, 1):
        marker = f" {Colors.GREEN}(saved){Colors.RESET}" if host == saved_host else ""
        print(f"  {Colors.CYAN}{i}{Colors.RESET} - {label}{marker}")
    _saved_idx = next((i for i, (h, l) in enumerate(DOMAINS) if h == saved_host), 0)
    _default_choice = str(_saved_idx + 1)
    while True:
        try:
            choice = input(f"{Colors.CYAN}  Choose 1-{len(DOMAINS)} (default={_default_choice}): {Colors.RESET}").strip()
            if not choice:
                QX_HOST = saved_host if saved_host else DOMAINS[0][0]
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(DOMAINS):
                    QX_HOST = DOMAINS[idx][0]
                else:
                    print(f"{Colors.RED}  Invalid choice.{Colors.RESET}")
                    continue
            break
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.RED}  Invalid input.{Colors.RESET}")
        except EOFError:
            QX_HOST = saved_host if saved_host else DOMAINS[0][0]
            break
    globals()['QX_HOST'] = QX_HOST
    print(f"{Colors.GREEN}  Using domain: {QX_HOST}{Colors.RESET}\\n")""",
    """    QX_HOST, _selected_country = select_domain()
    globals()['QX_HOST'] = QX_HOST
    session_manager.set_saved_host(QX_HOST)
    print()
    print(f"{Colors.BOLD}  Domain (auto by country){Colors.RESET}")
    if _selected_country == "manual":
        print(f"  {Colors.DIM}Country: manual override (QX_FORCE_DOMAIN={QX_HOST}){Colors.RESET}")
    elif _selected_country == "unknown":
        print(f"  {Colors.DIM}Country: not detected -> using global domain{Colors.RESET}")
    else:
        print(f"  {Colors.DIM}Country: {_selected_country}{Colors.RESET}")
    print(f"  {Colors.GREEN}Using domain: {QX_HOST}{Colors.RESET}\\n")""",
))

errors = []
for idx, (old, new) in enumerate(REPLACEMENTS, 1):
    n = data.count(old)
    if n != 1:
        errors.append(f"E{idx}: old text found {n} times (expected 1)")
if errors:
    print("ABORT — anchor problems:")
    for e in errors:
        print("  ", e)
    sys.exit(1)

for idx, (old, new) in enumerate(REPLACEMENTS, 1):
    data = data.replace(old, new, 1)
    print(f"E{idx}: applied OK")

# E13: STAGE 4 title comment line (Arabic — replace by line search)
lines = data.split("\n")
done13 = False
for i, line in enumerate(lines):
    if "STAGE 4: Select Domain" in line:
        lines[i] = "    # STAGE 4: Domain \u2014 \u0627\u062e\u062a\u064a\u0627\u0631 \u062a\u0644\u0642\u0627\u0626\u064a \u062d\u0633\u0628 \u0627\u0644\u0628\u0644\u062f (\u0643\u0634\u0641 \u0639\u0628\u0631 IP \u0639\u0644\u0649 \u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062f\u0648\u0644\u0629 \u0641\u0642\u0637)"
        done13 = True
        break
if done13:
    data = "\n".join(lines)
    print("E13: applied OK (STAGE 4 title updated)")
else:
    print("E13: WARNING — 'STAGE 4: Select Domain' line not found (left as is)")

open(PATH, "w", encoding="utf-8", newline="\n").write(data)
print("saved:", PATH)
