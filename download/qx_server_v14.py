#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import ssl
import json
import time
import math
import struct
import logging
import asyncio
import calendar
import platform
import random
import re
import shutil
import threading
import traceback
import itertools
import configparser
import contextlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Awaitable, Callable, Dict, Generic, Hashable, List, Literal, Mapping, Optional, Tuple, TypeVar

import certifi
import requests
import websocket
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from bs4.element import AttributeValueList
from fake_useragent import UserAgent

try:
    import orjson as _orjson
    HAS_ORJSON = True
except ImportError:
    _orjson = None
    HAS_ORJSON = False

# ==============================================================================
# NOTE (v13.0): Preload Engine — same terminal-only flow as v12 (no web
# interface, login asks ONLY email + password, full payout table in terminal).
# NEW per user request:
#   1) Right after login: 300 candles + status + payout for BRLUSD_otc (the
#      chart opener asset).
#   2) Then every other OPEN asset is loaded one-by-one with 300 candles each,
#      and a live price stream keeps running per asset so any chart opened
#      later is instantly ready.
#   3) fetch_older_batch(): fetches a 300-candle older batch (scroll-back
#      pagination, like professional platforms). Server-side is ready NOW;
#      wiring it to the app comes LATER (user said: not now).
#   4) Ticks live in MEMORY ONLY and are auto-deleted after 5 minutes, so the
#      disk never fills up with ticks. Log file rotates at 10MB, candles.db is
#      trimmed to the newest 5000 candles per symbol.
#   5) In-memory candle cap raised 1000 -> 3000 so scroll-back batches can
#      accumulate. The login method and the candle fetch method are UNCHANGED.
# ==============================================================================

# ==============================================================================
# SECTION 1: LOGGING & SSL SETUP
# ==============================================================================
def _prepare_logging():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.INFO)
    websocket_logger.addHandler(logging.NullHandler())

_prepare_logging()
logger = logging.getLogger(__name__)

cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path
cacert = os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE')

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.load_verify_locations(cert_path)


# ==============================================================================
# SECTION 1.5: EVENT-DRIVEN WAIT PRIMITIVES (replaces asyncio.sleep polling)
# ==============================================================================
# pyquotex._api._waits — " " .
# polling timeout asyncio.sleep
# asyncio.Event .

async def wait_until(predicate: Callable[[], bool], *, timeout: float = 10.0,
                      poll_interval: float = 0.05) -> None:
    """ predicate() poll_interval True timeout.

 asyncio.TimeoutError . :
 while not condition:
 await asyncio.sleep(X)
 latency X poll_interval (50ms ).
 """
    async def _loop():
        while not predicate():
            await asyncio.sleep(poll_interval)
    await asyncio.wait_for(_loop(), timeout=timeout)


async def wait_for_first_event(*events: asyncio.Event, timeout: float = 10.0) -> int:
    """ event index. TimeoutError .

 :
 for _ in range(100):
 if cond_a: return A
 if cond_b: return B
 await asyncio.sleep(0.1)
 """
    if not events:
        raise ValueError("wait_for_first_event requires at least one event")
    tasks = [asyncio.ensure_future(e.wait()) for e in events]
    try:
        done, pending = await asyncio.wait(tasks, timeout=timeout,
                                           return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
        for i, t in enumerate(tasks):
            if t in done and t.result() and not t.cancelled():
                return i
        # timeout
        raise asyncio.TimeoutError()
    except asyncio.CancelledError:
        for t in tasks:
            if not t.done():
                t.cancel()
        raise


def _schedule_event_set(event: Optional[asyncio.Event],
                        loop: Optional[asyncio.AbstractEventLoop]) -> None:
    """ asyncio.Event thread ( websocket thread).

 run_coroutine_threadsafe coroutine 
 callback loop thread-safe loop.call_soon_threadsafe.
 """
    if event is None or loop is None:
        return
    try:
        if not loop.is_closed() and loop.is_running():
            loop.call_soon_threadsafe(event.set)
    except RuntimeError:
        # loop —
        pass


# ==============================================================================
# SECTION 2: CONSTANTS & SESSION
# ==============================================================================
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
base_dir = Path.cwd()
session_lock = threading.Lock()

def resource_path(relative_path: str) -> Path:
    global base_dir
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = Path(sys._MEIPASS)
    return base_dir / relative_path

def load_session(email: str, user_agent: str = None) -> dict:
    if user_agent is None:
        try: user_agent = UserAgent().random
        except Exception: user_agent = USER_AGENT
    output_file = Path(resource_path("session.json"))
    with session_lock:
        all_sessions = {}
        if output_file.exists():
            try: all_sessions = json.loads(output_file.read_text())
            except json.JSONDecodeError: pass
        else:
            output_file.parent.mkdir(exist_ok=True, parents=True)
        if email not in all_sessions:
            all_sessions[email] = {"cookies": None, "token": None, "user_agent": user_agent}
        output_file.write_text(json.dumps(all_sessions, indent=4))
        return all_sessions.get(email)

def update_session(email: str, d: dict) -> dict:
    output_file = Path(resource_path("session.json"))
    with session_lock:
        current_sessions = {}
        if output_file.exists():
            try: current_sessions = json.loads(output_file.read_text())
            except json.JSONDecodeError: pass
        else:
            output_file.parent.mkdir(exist_ok=True, parents=True)
        current_sessions[email] = d
        output_file.write_text(json.dumps(current_sessions, indent=4))
        return current_sessions.get(email)

# ==============================================================================
# SECTION 3: HTTP NAVIGATOR (PROVEN WORKING METHOD)
# ==============================================================================
retry_strategy = Retry(
    total=3, backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104],
    allowed_methods=["HEAD", "POST", "PUT", "GET", "OPTIONS"],
)

class CipherSuiteAdapter(HTTPAdapter):
    __attrs__ = ['ssl_context', 'max_retries', 'config', '_pool_connections', '_pool_maxsize', '_pool_block', 'source_address']
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        self.cipherSuite = kwargs.pop('cipherSuite', 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384')
        self.source_address = kwargs.pop('source_address', None)
        self.server_hostname = kwargs.pop('server_hostname', None)
        self.ecdhCurve = kwargs.pop('ecdhCurve', 'prime256v1')
        if not self.ssl_context:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.ssl_context.orig_wrap_socket = self.ssl_context.wrap_socket
            self.ssl_context.wrap_socket = self.wrap_socket
        if self.server_hostname:
            self.ssl_context.server_hostname = self.server_hostname
        if self.cipherSuite:
            self.ssl_context.set_ciphers(self.cipherSuite)
            self.ssl_context.set_ecdh_curve(self.ecdhCurve)
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        super().__init__(**kwargs)

    def wrap_socket(self, *args, **kwargs):
        if hasattr(self.ssl_context, 'server_hostname') and self.ssl_context.server_hostname:
            kwargs['server_hostname'] = self.ssl_context.server_hostname
            self.ssl_context.check_hostname = False
        else:
            self.ssl_context.check_hostname = True
        return self.ssl_context.orig_wrap_socket(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        kwargs['source_address'] = self.source_address
        return super().init_poolmanager(*args, **kwargs)

class Browser(Session):
    def __init__(self, *args, **kwargs):
        self.response = None
        self.default_headers = None
        self.ecdhCurve = kwargs.pop('ecdhCurve', 'prime256v1')
        self.cipherSuite = kwargs.pop('cipherSuite', 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384')
        self.source_address = kwargs.pop('source_address', None)
        self.server_hostname = kwargs.pop('server_hostname', None)
        self.proxies = kwargs.pop('proxies', None)
        super().__init__(*args, **kwargs)
        self.headers.update(self.get_headers())
        self.mount('https://', CipherSuiteAdapter(ecdhCurve=self.ecdhCurve, cipherSuite=self.cipherSuite, server_hostname=self.server_hostname, source_address=self.source_address, ssl_context=ssl_context, max_retries=retry_strategy))

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc_val, exc_tb): self.__exit__(exc_type, exc_val, exc_tb)

    def get_headers(self):
        self.default_headers = {"User-Agent": USER_AGENT}
        return self.default_headers

    def set_headers(self, headers=None):
        self.headers.update(self.default_headers)
        if headers: self.headers.update(headers)

    def get_cookies(self):
        return '; '.join(f'{i.name}={i.value}' for i in self.cookies)

    def get_soup(self):
        if self.response and not self.response.ok: raise RuntimeError(self.response.reason)
        return BeautifulSoup(self.response.content, "html.parser")

    def send_request(self, method, url, headers=None, **kwargs):
        merged_headers = self.headers.copy()
        if headers: merged_headers.update(headers)
        if self.proxies: kwargs['proxies'] = self.proxies
        self.response = self.request(method, url, headers=merged_headers, **kwargs)
        return self.response

# ==============================================================================
# SECTION 4: HTTP LOGIN & SETTINGS
# ==============================================================================
class Login(Browser):
    url = ""
    cookies = None
    ssid = None
    # FALLBACK default only - real value is set per-instance from api.host
    base_url = 'qxbroker.com'
    https_base_url = f'https://{base_url}'

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        # ---- DYNAMIC DOMAIN: follow the user-selected host -----------------
        # All HTTP login traffic now goes to the SAME domain that the WebSocket
        # will later connect to via ws2.<host>, so cookies/token stay valid.
        if not getattr(api, 'host', None):
            pass  # keep the hard-coded fallback
        else:
            self.base_url = api.host
            self.https_base_url = f'https://{self.base_url}'
        self.headers = self.get_headers()
        self.full_url = f"{self.https_base_url}/{api.lang}"

    def get_token(self):
        self.headers["Connection"] = "keep-alive"
        self.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.headers["Accept-Language"] = "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
        self.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        self.headers["Referer"] = f"{self.full_url}/sign-in"
        self.headers["Upgrade-Insecure-Requests"] = "1"
        self.headers["Sec-Ch-Ua-Mobile"] = "?0"
        self.headers["Sec-Ch-Ua-Platform"] = '"Linux"'
        self.headers["Sec-Fetch-Site"] = "same-origin"
        self.headers["Sec-Fetch-User"] = "?1"
        self.headers["Sec-Fetch-Dest"] = "document"
        self.headers["Sec-Fetch-Mode"] = "navigate"
        self.headers["Dnt"] = "1"
        self.send_request("GET", f"{self.full_url}/sign-in/modal/")
        html = self.get_soup()
        match = html.find("input", {"name": "_token"})
        return None if not match else match.get("value")

    async def awaiting_pin(self, data, input_message):
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Referer"] = f"{self.full_url}/sign-in/modal"
        data["keep_code"] = 1
        try:
            code = input(input_message)
            if not code.isdigit():
                print("Please enter a valid code.")
                await self.awaiting_pin(data, input_message)
            data["code"] = code
        except KeyboardInterrupt:
            print("\nClosing program.")
            sys.exit()
        await asyncio.sleep(1)
        self.send_request(method="POST", url=f"{self.full_url}/sign-in/modal", data=data)

    def get_profile(self):
        self.response = self.send_request(method="GET", url=f"{self.full_url}/trade")
        if self.response:
            script = self.get_soup().find_all("script", {"type": "text/javascript"})
            script = script[0].get_text() if script else "{}"
            match = script.strip().replace(";", "").replace("window.settings = ", "")
            self.cookies = self.get_cookies()
            try:
                settings_dict = json.loads(match)
                self.ssid = settings_dict.get("token")
            except json.JSONDecodeError:
                self.ssid = None
            self.api.session_data["cookies"] = self.cookies
            self.api.session_data["token"] = self.ssid
            self.api.session_data["user_agent"] = self.headers["User-Agent"]
            update_session(self.api.username, self.api.session_data)
            return self.response, settings_dict if self.ssid else None
        return None, None

    async def _post(self, data):
        self.response = self.send_request(method="POST", url=f"{self.full_url}/sign-in/", data=data)
        required_keep_code = self.get_soup().find("input", {"name": "keep_code"})
        if required_keep_code:
            auth_body = self.get_soup().find("main", {"class": "auth__body"})
            input_message = f'{auth_body.find("p").text}: ' if auth_body.find("p") else "Enter the PIN code sent to your email: "
            await self.awaiting_pin(data, input_message)
            await asyncio.sleep(1)
            return self.success_login()
        return self.success_login()

    def success_login(self):
        if "trade" in str(self.response.url):
            return True, "Login successful."
        soup = self.get_soup()
        not_available = soup.select_one("#tab-1 > div > div.modal-sign__not-avalible__title")
        if not_available: return False, f"Service unavailable: {not_available.get_text(strip=True)}"
        error = soup.select_one("#tab-1 form > div:nth-child(2) > div")
        msg = error.get_text(strip=True) if error else "Unknown error"
        return False, f"Login failed. {msg}"

    async def __call__(self, username, password, user_data_dir=None):
        data = {"_token": self.get_token(), "email": username, "password": password, "remember": 1}
        status, msg = await self._post(data)
        if status: self.get_profile()
        return status, msg

class Settings(Browser):
    def __init__(self, api):
        super().__init__()
        self.set_headers()
        self.api = api
        self.headers = self.get_headers()

    def get_settings(self):
        self.headers["content-type"] = "application/json"
        self.headers["referer"] = f"{self.api.https_url}/{self.api.lang}/trade"
        self.headers["cookie"] = self.api.session_data.get("cookies", "")
        self.headers["user-agent"] = self.api.session_data.get("user_agent", "")
        response = self.send_request("GET", f"{self.api.https_url}/api/v1/cabinets/digest")
        return response.json()

# ==============================================================================
# SECTION 5: WEBSOCKET CLIENT & STATE (SYNC + EVENT REGISTRY INTEGRATION)
# ==============================================================================
class WebsocketStatus(IntEnum):
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2
    ERROR = -1

class AuthStatus(IntEnum):
    NOT_AUTHENTICATED = 0
    AUTHENTICATING = 1
    AUTHENTICATED = 2
    FAILED = -1

class ConnectionState:
    def __init__(self):
        self.SSID = None
        self.status = WebsocketStatus.DISCONNECTED
        self.auth_status = AuthStatus.NOT_AUTHENTICATED
        self.ssl_Mutual_exclusion = False
        self.ssl_Mutual_exclusion_write = False
        self.check_rejected_connection = False
        self.check_accepted_connection = False
        self.check_websocket_if_error = False
        self.check_websocket_if_connect = None
        self.websocket_error_reason = None

        # ===== EVENT-DRIVEN ADDITIONS =====
        # asyncio polling. lazily async context
        # init_events() "no running event loop" .
        self.ws_connected_event: Optional[asyncio.Event] = None
        self.ws_closed_event: Optional[asyncio.Event] = None
        self.auth_accepted_event: Optional[asyncio.Event] = None
        self.auth_rejected_event: Optional[asyncio.Event] = None
        self.ws_error_event: Optional[asyncio.Event] = None
        # loop websocket thread
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def init_events(self) -> None:
        """ loop . async context."""
        if self.ws_connected_event is None:
            self.ws_connected_event = asyncio.Event()
        if self.ws_closed_event is None:
            self.ws_closed_event = asyncio.Event()
        if self.auth_accepted_event is None:
            self.auth_accepted_event = asyncio.Event()
        if self.auth_rejected_event is None:
            self.auth_rejected_event = asyncio.Event()
        if self.ws_error_event is None:
            self.ws_error_event = asyncio.Event()
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None

    def reset_events(self) -> None:
        """ ."""
        for ev in (self.ws_connected_event, self.ws_closed_event,
                   self.auth_accepted_event, self.auth_rejected_event,
                   self.ws_error_event):
            if ev is not None:
                ev.clear()

    # wrappers thread (websocket thread)
    def signal_ws_connected(self) -> None:
        _schedule_event_set(self.ws_connected_event, self._loop)

    def signal_ws_closed(self) -> None:
        _schedule_event_set(self.ws_closed_event, self._loop)

    def signal_auth_accepted(self) -> None:
        _schedule_event_set(self.auth_accepted_event, self._loop)

    def signal_auth_rejected(self) -> None:
        _schedule_event_set(self.auth_rejected_event, self._loop)

    def signal_ws_error(self) -> None:
        _schedule_event_set(self.ws_error_event, self._loop)

class WebsocketClient:
    def __init__(self, api):
        self.api = api
        self.state = api.state
        self.headers = {
            "User-Agent": self.api.session_data.get("user_agent", USER_AGENT),
            "Origin": self.api.https_url,
            "Host": f"ws2.{self.api.host}",
        }
        self.wss = websocket.WebSocketApp(
            self.api.wss_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            header=self.headers,
            cookie=self.api.session_data.get("cookies"),
        )

    def on_message(self, wss, msg):
        self.state.ssl_Mutual_exclusion = True
        # ===== STALE-WATCHDOG: =====
        # watchdog .
        try:
            if self.api is not None:
                self.api.last_message_at = time.time()
        except Exception:
            pass
        try:
            msg_str = msg.decode("utf-8", errors="ignore") if isinstance(msg, bytes) else str(msg)

            if msg_str == "2":
                try:
                    self.wss.send("3")
                except Exception:
                    pass
                self.state.ssl_Mutual_exclusion = False
                return
            if msg_str == "3":
                self.state.ssl_Mutual_exclusion = False
                return

            if "authorization/reject" in msg_str:
                logger.warning("Token rejected.")
                self.state.check_rejected_connection = True
                self.state.auth_status = AuthStatus.FAILED
                # ===== EVENT-DRIVEN FIX =====
                self.state.signal_auth_rejected()
            elif "s_authorization" in msg_str:
                self.state.check_accepted_connection = True
                self.state.check_rejected_connection = False
                self.state.auth_status = AuthStatus.AUTHENTICATED
                self.state.status = WebsocketStatus.CONNECTED
                print("\n" + "="*60)
                print("Connected to server successfully")
                print("="*60 + "\n")
                # ===== EVENT-DRIVEN FIX =====
                self.state.signal_auth_accepted()

            # ===== INSTRUMENTS LIST (طريقة pyquotex الرسمية — على مرحلتين) =====
            # الرد على 42["instruments/get"] يصل كما يلي (نفس سلوك المكتبة الرسمية):
            #   المرحلة 1: 451-["instruments/list",{...,"_placeholder":true,"num":0}]
            #              (رسالة تحكم تحمل placeholder فقط — بلا بيانات)
            #   المرحلة 2: إطار منفصل (غالباً binary) يحتوي JSON القائمة الفعلية
            # v12 FIX: السابق كان يعالج الصيغة المضمّنة فقط (451- مع القائمة داخلها)،
            # ولذلك عندما يرد الخادم بأسلوب placeholder + إطار منفصل لم تُخزن القائمة
            # أبداً وكانت تظهر فارغة. الآن نطبّق المسارين معاً.
            if "instruments/list" in msg_str and "_placeholder" in msg_str:
                # المرحلة 1: نتذكر أننا ننتظر الإطار التالي الذي يحمل البيانات الفعلية
                try:
                    self.api._temp_status = msg_str
                except Exception:
                    pass
                self.state.ssl_Mutual_exclusion = False
                return

            if "instruments/list" in msg_str:
                # الصيغة المضمّنة (القائمة كاملة داخل نفس الرسالة) — خطة بديلة
                try:
                    _idx = msg_str.find('["')
                    if _idx != -1:
                        _payload = json.loads(msg_str[_idx:])
                        _data = _payload[1] if isinstance(_payload, list) and len(_payload) >= 2 else None
                        if isinstance(_data, dict) and "list" in _data:
                            _data = _data["list"]
                        if isinstance(_data, list) and _data:
                            self.api.instruments = _data
                            try:
                                self.api._temp_status = ""
                            except Exception:
                                pass
                            _loop = getattr(self.api, "_async_loop", None)
                            if _loop is not None and _loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    self.api.event_registry.set_event("instruments_ready", _data),
                                    _loop,
                                )
                            logger.info(f"Instruments list received: {len(_data)} assets")
                except Exception as _e:
                    logger.debug(f"instruments/list parse error: {_e}")

            # المرحلة 2: تسليم القائمة الفعلية بعد placeholder (نفس سلوك المكتبة الرسمية)
            try:
                if self.api._temp_status and "instruments/list" in self.api._temp_status:
                    _first_char = msg_str[0] if msg_str else ""
                    if _first_char and not _first_char.isdigit():
                        _sidx = -1
                        for _ci, _cc in enumerate(msg_str):
                            if _cc in ("[", "{"):
                                _sidx = _ci
                                break
                        if _sidx != -1:
                            _payload = json.loads(msg_str[_sidx:])
                            if (isinstance(_payload, list) and len(_payload) == 1
                                    and isinstance(_payload[0], (list, dict))):
                                _payload = _payload[0]
                            if isinstance(_payload, dict) and "list" in _payload:
                                _payload = _payload["list"]
                            if isinstance(_payload, list) and _payload:
                                self.api.instruments = _payload
                                self.api._temp_status = ""
                                _loop = getattr(self.api, "_async_loop", None)
                                if _loop is not None and _loop.is_running():
                                    asyncio.run_coroutine_threadsafe(
                                        self.api.event_registry.set_event("instruments_ready", _payload),
                                        _loop,
                                    )
                                logger.info(f"Instruments list received: {len(_payload)} assets")
            except Exception as _e:
                logger.debug(f"instruments payload fulfillment error: {_e}")

            message = None
            if len(msg_str) > 1 and msg_str[1] in ('[', '{'):
                try:
                    message = json.loads(msg_str[1:])
                except Exception:
                    pass

            if message is not None:
                self._process_message_and_raise_events(message)

            if str(msg_str) == "41":
                self.state.check_websocket_if_connect = 0
        except Exception as e:
            logger.error("Unhandled error in on_message: %s", e)
        self.state.ssl_Mutual_exclusion = False

    def _process_message_and_raise_events(self, message):
        try:
            loop = self.api._async_loop
            if loop is None or not loop.is_running():
                return

            if isinstance(message, dict):
                asset = message.get("asset")
                if asset and (message.get("candles") or message.get("data") or message.get("history")):
                    self.api.candle_v2_data[asset] = message
                    self.api.candles.candles_data = message.get("candles") or message.get("data") or message.get("history")

                    # ===== FIX: توجيه حدث الجلب للرد الحقيقي فقط (v14.1) =====
                    # مشكلة سببت «الرجوع للخلف لا يجلب شموعاً»:
                    #   الحدث candles_ready_<asset> كان يُرفع لأي رسالة تحمل
                    #   شموعاً لنفس العملة — بما فيها لقطات البث الحي
                    #   (instruments/update) — فتسرق اللقطة الحية الحدث قبل وصول
                    #   رد history/load الحقيقي، فيأخذ الانتظار شموعاً حديثة
                    #   لا تنفع التمرير للخلف (تُفلتر كلها لأنها ليست أقدم من
                    #   before_time) وتظهر النتيجة فارغة دائماً.
                    # الحل (نفس بروتوكول pyquotex): رد history/load الحقيقي يرد
                    #   بـ«index» مطابق للطلب — لذلك:
                    #   - رسالة تحمل index = رد تاريخ حقيقي → ترفع الحدثين
                    #     (العام + المفهرس) كما كان تماماً — طريقة الجلب الأصلية
                    #     لم تُمَس حرفياً.
                    #   - رسالة بلا index = لقطة بث حي → تُحدّث الكاش فقط، ولا
                    #     ترفع حدث الجلب ما دام طلب history لهذه العملة معلّقاً
                    #     وحديثاً (سجل _history_pending يملؤه send_websocket_request
                    #     عند رؤية أي history/load صادر).
                    index = message.get("index")
                    pending = None
                    try:
                        pending = self.api._history_pending.get(asset)
                    except Exception:
                        pending = None
                    pending_fresh = False
                    if pending is not None:
                        try:
                            pending_fresh = (time.time() - float(pending[1])) < 15.0
                        except Exception:
                            pending_fresh = False
                    if index is not None:
                        # رد history/load الحقيقي — نفس السلوك الأصلي كاملاً
                        asyncio.run_coroutine_threadsafe(
                            self.api.event_registry.set_event(f'candles_ready_{asset}', message),
                            loop
                        )
                        asyncio.run_coroutine_threadsafe(
                            self.api.event_registry.set_event(f'candles_ready_{asset}_{index}', message),
                            loop
                        )
                        try:
                            self.api._history_pending.pop(asset, None)
                            self.api._history_reply_count += 1
                        except Exception:
                            pass
                    elif not pending_fresh:
                        # لقطة حية بلا أي طلب تاريخ معلّق — سلوك أصلي متوافق
                        asyncio.run_coroutine_threadsafe(
                            self.api.event_registry.set_event(f'candles_ready_{asset}', message),
                            loop
                        )
                    else:
                        # لقطة حية تحاول سرقة حدث جلب معلّق — تُسَقَط (الكاش تُحدّث أعلاه)
                        try:
                            self.api._history_stolen_suppressed += 1
                        except Exception:
                            pass

            if isinstance(message, dict) and (message.get("liveBalance") or message.get("demoBalance")):
                self.api.account_balance = message

            if isinstance(message, list) and len(message) > 0 and isinstance(message[0], list) and len(message[0]) == 4:
                asset = message[0][0]
                self.api.realtime_candles[asset] = message[0]
        except Exception as e:
            logger.debug(f"Error processing message: {e}")

    def on_error(self, wss, error):
        global CONNECTION_ALIVE
        logger.error(error)
        self.state.websocket_error_reason = str(error)
        self.state.check_websocket_if_error = True
        self.state.status = WebsocketStatus.ERROR
        self.state.check_accepted_connection = False
        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_error()
        mark_connection_dead(f"ws_error: {str(error)[:80]}")

    def on_open(self, wss):
        logger.info("Websocket client connected.")
        self.state.check_websocket_if_connect = 1
        self.state.status = WebsocketStatus.CONNECTED
        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_connected()
        asset_name = self.api.current_asset or "EURUSD"
        period = self.api.current_period or 60
        self.wss.send('42["tick"]')
        self.wss.send('42["indicator/list"]')
        self.wss.send('42["drawing/load"]')
        self.wss.send('42["pending/list"]')
        self.wss.send(f'42["instruments/update",{{"asset":"{asset_name}","period":{period}}}]')
        self.wss.send(f'42["depth/follow","{asset_name}"]')
        self.wss.send('42["chart_notification/get"]')
        self.wss.send('42["instruments/get"]')
        self.wss.send('42["tick"]')

    def on_close(self, wss, close_status_code, close_msg):
        global CONNECTION_ALIVE
        logger.info("Websocket connection closed.")
        self.state.check_websocket_if_connect = 0
        self.state.status = WebsocketStatus.DISCONNECTED
        self.state.check_accepted_connection = False
        # ===== EVENT-DRIVEN FIX =====
        self.state.signal_ws_closed()
        mark_connection_dead("ws_closed")

    def on_ping(self, wss, ping_msg): pass
    def on_pong(self, wss, pong_msg): pass

# ==============================================================================
# SECTION 6: QUOTEX API CORE
# ==============================================================================
class CandlesObj:
    def __init__(self): self.__candles_data = None
    @property
    def candles_data(self): return self.__candles_data
    @candles_data.setter
    def candles_data(self, candles_data): self.__candles_data = candles_data

class EventRegistry:
    def __init__(self):
        self._events: Dict[str, asyncio.Event] = {}
        self._data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get_event(self, key: str) -> asyncio.Event:
        async with self._lock:
            if key not in self._events:
                self._events[key] = asyncio.Event()
            return self._events[key]

    async def set_event(self, key: str, data: Any = None):
        async with self._lock:
            if key not in self._events:
                self._events[key] = asyncio.Event()
            self._data[key] = data
            self._events[key].set()

    async def wait_event(self, key: str, timeout: float = 30.0) -> Any:
        event = await self.get_event(key)
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            return self._data.get(key)
        except asyncio.TimeoutError:
            return None

    async def clear_event(self, key: str):
        async with self._lock:
            if key in self._events:
                self._events[key].clear()
            if key in self._data:
                del self._data[key]

class QuotexAPI:
    def __init__(self, host, username, password, lang, proxies=None, user_data_dir="."):
        self.state = ConnectionState()
        self.trace_ws = False
        self.current_asset = None
        self.current_period = None
        self.account_balance = None
        self.account_type = 1
        self.instruments = None
        self.host = host
        self.https_url = f"https://{host}"
        self.wss_url = f"wss://ws2.{host}/socket.io/?EIO=3&transport=websocket"
        self.websocket_thread = None
        self.websocket_client = None
        self.username = username
        self.password = password
        self.proxies = proxies
        self.lang = lang
        self.user_data_dir = user_data_dir
        self.session_data = {}
        self.browser = Browser()
        self.browser.set_headers()
        self.settings = Settings(self)
        self.candles = CandlesObj()
        self.candle_v2_data = {}
        self.realtime_price = defaultdict(list)
        self.realtime_candles = {}
        self.event_registry = EventRegistry()
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._temp_status = ""
        # ===== v14.1: سجل طلبات history/load المعلّقة (توجيه رد الجلب الحقيقي) =====
        # send_websocket_request يسجل هنا كل طلب history/load صادر:
        #   asset -> (index, time_sent)
        # وموجّه الرسائل يستخدمه لمنع لقطات البث الحي من سرقة حدث
        # candles_ready_<asset> قبل وصول رد history/load الحقيقي.
        self._history_pending: Dict[str, tuple] = {}
        self._history_reply_count: int = 0
        self._history_stolen_suppressed: int = 0
        # ===== STALE-WATCHDOG ADDITION =====
        # WS . watchdog
        # .
        self.last_message_at: float = time.time()
        # ===== FIX 7: Rate Limiter ( ) =====
        # . rate limiter
        # keepalive + watchdog.
        # rate limiter (15ms = ~66 req/s) bursts .
        self._ws_send_times: list[float] = []
        self._ws_min_interval: float = 0.015  # 15ms ( )
        self._ws_max_per_window: int = 100    # 100 / ()
        self._ws_window: float = 1.0          # 1
        self._throttle_multiplier: float = 1.0  # = 1.0 ( auto-throttle)
        self._last_send_at: float = 0.0

    @property
    def login(self): return Login(self)

    def _apply_rate_limit(self) -> None:
        """ rate limiting WS — .

 - (_ws_min_interval * _throttle_multiplier)
 - (_ws_max_per_window / _throttle_multiplier)
 """
        now = time.time()
        # 1)
        min_interval = self._ws_min_interval * self._throttle_multiplier
        if self._last_send_at > 0:
            elapsed = now - self._last_send_at
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
                now = time.time()
        # 2)
        window_size = self._ws_window * self._throttle_multiplier
        cutoff = now - window_size
        self._ws_send_times = [t for t in self._ws_send_times if t >= cutoff]
        # 3)
        if len(self._ws_send_times) >= self._ws_max_per_window:

            sleep_for = (self._ws_send_times[0] + window_size) - now
            if sleep_for > 0:
                time.sleep(sleep_for)
                now = time.time()
                cutoff = now - window_size
                self._ws_send_times = [t for t in self._ws_send_times if t >= cutoff]
        # 4)
        self._ws_send_times.append(now)
        self._last_send_at = now

    def increase_throttle(self, factor: float = 2.0, max_multiplier: float = 8.0) -> None:
        """ ( ).
 => => => .
 """
        new_multiplier = min(self._throttle_multiplier * factor, max_multiplier)
        if new_multiplier != self._throttle_multiplier:
            self._throttle_multiplier = new_multiplier
            logger.info(f" Throttle increased to {new_multiplier}x (rate limit stress)")

    def decrease_throttle(self, factor: float = 0.5, min_multiplier: float = 1.0) -> None:
        """ ( )."""
        new_multiplier = max(self._throttle_multiplier * factor, min_multiplier)
        if new_multiplier != self._throttle_multiplier:
            self._throttle_multiplier = new_multiplier
            logger.info(f" Throttle restored to {new_multiplier}x")

    def send_websocket_request(self, data, no_force_send=True):
        # ===== FIX: busy-wait -> sleep + try/finally =====
        if no_force_send:
            deadline = time.time() + 5.0  # 5s
            while (self.state.ssl_Mutual_exclusion or self.state.ssl_Mutual_exclusion_write):
                if time.time() > deadline:
                    # — . .
                    break
                time.sleep(0.001)  # `pass` — CPU
        # ===== FIX 6: rate limit =====
        # : heartbeat messages ("2" "42[\"tick\"]" "42[\"instruments/get\"]")
        # rate limit — keepalive.
        is_heartbeat = (
            data == "2" or
            data == '42["tick"]' or
            data == '42["instruments/get"]' or
            'pending/list' in data or
            'indicator/list' in data or
            'drawing/load' in data
        )
        if not is_heartbeat:
            try:
                self._apply_rate_limit()
            except Exception:
                # rate limiter
                pass
        self.state.ssl_Mutual_exclusion_write = True
        try:
            # ===== v14.1: سجّل أي طلب history/load صادر (توجيه رد الجلب الحقيقي) =====
            # لا يغيّر الرسالة ولا طريقة الجلب بأي شكل — مجرد دفتر انتظار يقرؤه
            # موجّه الرسائل لمنع لقطات البث من سرقة حدث candles_ready_<asset>.
            if isinstance(data, str) and '"history/load"' in data:
                try:
                    _pl_start = data.find("{")
                    _pl_end = data.rfind("}")
                    if _pl_start >= 0 and _pl_end > _pl_start:
                        _pl = json.loads(data[_pl_start:_pl_end + 1])
                        if isinstance(_pl, dict) and _pl.get("asset"):
                            self._history_pending[str(_pl["asset"])] = (
                                _pl.get("index"), time.time())
                except Exception:
                    pass
            if self.websocket_client and self.websocket_client.wss:
                self.websocket_client.wss.send(data)
        finally:
            # ===== FIX: flag =====
            self.state.ssl_Mutual_exclusion_write = False

    def subscribe_realtime_candle(self, asset, period):
        self.realtime_price[asset] = []
        self.realtime_candles[asset] = {}
        data = f'42["instruments/update", {json.dumps({"asset": asset, "period": period})}]'
        return self.send_websocket_request(data)

    def follow_candle(self, asset):
        return self.send_websocket_request(f'42["depth/follow", {json.dumps(asset)}]')

    def chart_notification(self, asset):
        return self.send_websocket_request(f'42["chart_notification/get", {json.dumps({"asset": asset, "version": "1.0.0"})}]')

    def get_candles_ws(self, asset, index, time_val, offset, period):
        payload = {"asset": asset, "index": index, "time": time_val, "offset": offset, "period": period}
        data = f'42["history/load",{json.dumps(payload)}]'
        return self.send_websocket_request(data)

    async def authenticate(self):
        async with self.login as login:
            status, msg = await login(self.username, self.password, self.user_data_dir)
        if status:
            self.state.SSID = self.session_data.get("token")
        return status, msg

    async def start_websocket(self):
        self.state.check_websocket_if_connect = None
        self.state.check_websocket_if_error = False
        self.state.websocket_error_reason = None
        # ===== EVENT-DRIVEN FIX =====
        # +
        self.state.init_events()
        self.state.reset_events()
        # loop ( reconnect)
        try:
            self.state._loop = asyncio.get_running_loop()
        except RuntimeError:
            self.state._loop = None

        if not self.state.SSID:
            await self.authenticate()
        self.websocket_client = WebsocketClient(self)
        payload = {
            "suppress_origin": True, "ping_interval": 24, "ping_timeout": 20, "ping_payload": "2",
            "origin": self.https_url, "host": f"ws2.{self.host}",
            "sslopt": {"check_hostname": True, "cert_reqs": ssl.CERT_REQUIRED, "ca_certs": cacert, "context": ssl_context},
        }
        if platform.system() == "Linux":
            payload["sslopt"]["ssl_version"] = ssl.PROTOCOL_TLS
        self.websocket_thread = threading.Thread(target=self.websocket_client.wss.run_forever, kwargs=payload)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        # ===== EVENT-DRIVEN FIX =====
        # polling:
        # for _ in range(100):
        # if self.state.check_websocket_if_error: return False, ...
        # elif self.state.check_websocket_if_connect == 1: return True, ...
        # elif self.state.check_rejected_connection: return False, "Token Rejected."
        # await asyncio.sleep(0.1)
        # : connected, rejected, error, closed
        try:
            idx = await wait_for_first_event(
                self.state.ws_connected_event,
                self.state.auth_rejected_event,
                self.state.ws_error_event,
                self.state.ws_closed_event,
                timeout=10.0,
            )
        except asyncio.TimeoutError:
            return False, "Timeout waiting for websocket open"

        if idx == 0:
            return True, "Websocket connected successfully!!!"
        elif idx == 1:
            self.state.SSID = None
            return False, "Websocket Token Rejected."
        elif idx == 2:
            return False, self.state.websocket_error_reason or "Websocket error"
        elif idx == 3:
            return False, "Websocket connection closed."
        return False, "Unknown websocket state"

    async def send_ssid(self, timeout=10):
        if not self.state.SSID: return False
        # ===== EVENT-DRIVEN FIX =====
        # ( send_ssid start_websocket )
        if self.state.auth_accepted_event is None:
            self.state.init_events()
        self.state.auth_accepted_event.clear()
        self.state.auth_rejected_event.clear()

        payload = {"session": self.state.SSID, "isDemo": self.account_type, "tournamentId": 0}
        data = f'42["authorization",{json.dumps(payload)}]'
        self.send_websocket_request(data)

        # ===== EVENT-DRIVEN FIX =====
        # polling:
        # while not check_accepted and not check_rejected:
        # if time.time() - start_time > timeout: return False
        # await asyncio.sleep(0.5)
        # accepted rejected .
        try:
            idx = await wait_for_first_event(
                self.state.auth_accepted_event,
                self.state.auth_rejected_event,
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            return False
        return idx == 0  # True accepted, False rejected

    async def connect(self, is_demo):
        self.account_type = 1 if is_demo else 0
        self.state.ssl_Mutual_exclusion = False
        self.state.ssl_Mutual_exclusion_write = False
        check_websocket, websocket_reason = await self.start_websocket()
        if not check_websocket: return check_websocket, websocket_reason
        check_ssid = await self.send_ssid()
        if not check_ssid:
            await self.authenticate()
            if self.state.SSID: await self.send_ssid()
        return check_websocket, websocket_reason

    async def close(self):
        if self.websocket_client and self.websocket_client.wss:
            self.websocket_client.wss.close()
            await asyncio.sleep(1)
        if self.websocket_thread and self.websocket_thread.is_alive():
            self.websocket_thread.join(timeout=5)
        return True

# ==============================================================================
# SECTION 7: QUOTEX STABLE API WITH FULL HISTORY MIXIN
# ==============================================================================
_request_counter = itertools.count(int(time.time() * 1000))

def group_by_period(data, period):
    grouped = defaultdict(list)
    for tick in data:
        timestamp = int(tick[0])
        timeframe = int(timestamp // period)
        grouped[timeframe].append(tick)
    return dict(grouped)

def calculate_candles(history, period):
    if not isinstance(history, list) or not history: return []
    grouped = group_by_period(history, period)
    candles = []
    for minute, ticks in grouped.items():
        open_price = ticks[0][1]
        close_price = ticks[-1][1]
        high_price = max(tick[1] for tick in ticks)
        low_price = min(tick[1] for tick in ticks)
        candle = {'time': minute * period, 'open': open_price, 'close': close_price, 'high': high_price, 'low': low_price, 'ticks': len(ticks)}
        candles.append(candle)
    return candles[:-1] if len(candles) > 1 else candles


# ===== FIX A: =====
# : calculate_candles "tick" [time, price]
# tick[1] open/high/low/close. Quotex
# "history/load" [time, open, close, high, low] (5 ).
# calculate_candles tick :
# open = high = low = close = open_price => !
# fill_gap_once => get_candles => prepare_candles.
# .
def _parse_raw_candles(raw_candles):
    """ WebSocket dicts OHLC .

 "history/load":
 1) [time, open, close, high, low] — Quotex (5 )
 2) [time, open, close, high, low, vol] — volume (6 )
 3) {"time", "open", "high", "low", "close", ...} — dict
 4) [time, price(, volume)] — tick ( )
 """
    if not raw_candles: return []
    parsed = []
    for c in raw_candles:
        try:
            if isinstance(c, dict) and 'time' in c:
                t = int(c.get('time', c.get('timestamp', 0)))
                o = float(c.get('open', 0) or 0)
                h = float(c.get('high', c.get('max', 0)) or 0)
                l = float(c.get('low', c.get('min', 0)) or 0)
                cl = float(c.get('close', c.get('c', 0)) or 0)
                v = int(c.get('volume', c.get('vol', 0)) or 0)
                if t > 0 and o > 0 and h > 0 and l > 0 and cl > 0:
                    parsed.append({'time': t, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v})
            elif isinstance(c, (list, tuple)) and len(c) >= 5:
                # Quotex WS: [time, open, close, high, low(, volume)]
                t = int(c[0])
                o = float(c[1])
                cl = float(c[2])
                h = float(c[3])
                l = float(c[4])
                v = int(c[5]) if len(c) >= 6 else 0
                if t > 0 and o > 0 and h > 0 and l > 0 and cl > 0:
                    parsed.append({'time': t, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v})
            elif isinstance(c, (list, tuple)) and len(c) >= 2:
                # tick format: [time, price(, volume)]
                t = int(c[0])
                p = float(c[1])
                v = int(c[2]) if len(c) >= 3 else 0
                if t > 0 and p > 0:
                    parsed.append({'time': t, 'open': p, 'high': p, 'low': p, 'close': p, 'volume': v})
        except (TypeError, ValueError):
            continue
    return parsed

def process_candles_v2(history, asset, data):
    if not history or not isinstance(history, dict): return data if data else []
    candles_data = history.get(asset, {})
    candles = candles_data.get("candles", [])[1:] if candles_data else []
    combined = candles + (data if data else [])
    if combined:
        candle_dict = {c.get('time'): c for c in combined if isinstance(c, dict) and 'time' in c}
        return list(candle_dict.values()) if candle_dict else []
    return combined

def merge_candles(candles_data):
    if not candles_data: return []
    candle_dict = {c['time']: c for c in candles_data if isinstance(c, dict) and 'time' in c}
    return sorted(candle_dict.values(), key=lambda x: x['time']) if candle_dict else []

class Quotex:
    def __init__(self, email=None, password=None, host="qxbroker.com", lang="en", proxies=None, user_data_dir="browser", asset_default="EURUSD", period_default=60):
        self.email = email
        self.password = password
        self.host = host
        self.lang = lang
        self.proxies = proxies
        self.user_data_dir = user_data_dir
        self.asset_default = asset_default
        self.period_default = period_default
        self.account_is_demo = 1
        self.codes_asset = {}
        self.api = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        session = load_session(self.email, USER_AGENT)
        self.session_data = session

    async def check_connect(self):
        if self.api is None: return False
        # ===== EVENT-DRIVEN FIX =====
        # :
        # await asyncio.sleep(1)
        # return self.api.state.check_accepted_connection == 1
        # . 2s 50ms
        # — latency 1000ms <100ms.
        try:
            await wait_until(
                lambda: self.api.state.check_accepted_connection == 1,
                timeout=2.0,
                poll_interval=0.05,
            )
            return True
        except asyncio.TimeoutError:
            return self.api.state.check_accepted_connection == 1

    async def connect(self):
        self.api = QuotexAPI(self.host, self.email, self.password, self.lang, proxies=self.proxies, user_data_dir=self.user_data_dir)
        self.api.session_data = self.session_data
        self.api.state.SSID = self.session_data.get("token")
        self.api._async_loop = asyncio.get_running_loop()
        if not self.session_data.get("token"):
            check, reason = await self.api.authenticate()
            if not check: return check, reason
        check, reason = await self.api.connect(self.account_is_demo == 1)
        if not check:
            self.session_data = {}
            return False, "Websocket connection rejected."
        return check, reason

    async def change_account(self, balance_mode: str):
        self.account_is_demo = 0 if balance_mode.upper() == "REAL" else 1
        self.api.account_type = self.account_is_demo
        payload = {"demo": self.api.account_type, "tournamentId": 0}
        self.api.send_websocket_request(f'42["account/change",{json.dumps(payload)}]')

    async def get_instruments(self, timeout: float = 12.0):
        """طريقة pyquotex الرسمية: طلب قائمة instruments الكاملة عبر WebSocket
        والانتظار حتى وصولها (event: instruments_ready)."""
        if self.api is None:
            return []
        if self.api.instruments and len(self.api.instruments) > 0:
            return self.api.instruments
        try:
            await self.api.event_registry.clear_event("instruments_ready")
        except Exception:
            pass
        try:
            self.api.send_websocket_request('42["instruments/get"]')
        except Exception as e:
            logmsg(f"[instruments] request failed: {e}")
            return []
        data = await self.api.event_registry.wait_event("instruments_ready", timeout=timeout)
        if isinstance(data, dict) and data.get("_placeholder"):
            data = await self.api.event_registry.wait_event("instruments_ready", timeout=5.0)
        if isinstance(data, list) and data:
            self.api.instruments = data
        return list(self.api.instruments or [])

    async def get_all_assets(self):
        """طريقة pyquotex الرسمية: خريطة اسم الأصل -> كوده الداخلي."""
        if self.api is None:
            return {}
        try:
            await self.get_instruments()
        except Exception:
            pass
        for i in (self.api.instruments or []):
            try:
                if isinstance(i, (list, tuple)) and i[0] != "":
                    self.codes_asset[i[1]] = i[0]
            except Exception:
                continue
        return self.codes_asset

    def get_payment(self):
        """طريقة pyquotex الرسمية get_payment: نسبة الدفع + الحالة لكل الأصول."""
        if self.api is None or not self.api.instruments:
            return {}
        assets_data = {}
        for i in self.api.instruments:
            try:
                assets_data[str(i[2]).replace("\n", "")] = {
                    "turbo_payment": i[18],
                    "payment": i[5],
                    "profit": {"24H": i[-10], "1M": i[-9], "5M": i[-8]},
                    "open": i[14],
                }
            except Exception:
                continue
        return assets_data

    def get_payout_by_asset(self, asset_name: str, timeframe: str = "1"):
        """طريقة pyquotex الرسمية get_payout_by_asset: نسبة الدفع لأصل محدد.
        timeframe: "1" (1M) أو "5" (5M) أو "24" (24H) أو "all"."""
        if self.api is None or not self.api.instruments:
            return None
        data = None
        for i in self.api.instruments:
            try:
                if isinstance(i, (list, tuple)) and len(i) > 1 and asset_name == i[1]:
                    data = {
                        "turbo_payment": i[18] if len(i) > 18 else None,
                        "payment": i[5] if len(i) > 5 else None,
                        "profit": {"24H": i[-10], "1M": i[-9], "5M": i[-8]},
                        "open": i[14] if len(i) > 14 else None,
                    }
                    break
            except Exception:
                continue
        if data is None:
            return None
        if timeframe == "all":
            return data.get("profit")
        profit = data.get("profit")
        if profit:
            if str(timeframe) == "24":
                return profit.get("24H")
            return profit.get(f"{timeframe}M")
        return None

    async def start_candles_stream(self, asset="EURUSD", period=60):
        if self.api:
            self.api.current_asset = asset
            self.api.current_period = period
            self.api.subscribe_realtime_candle(asset, period)
            self.api.chart_notification(asset)
            self.api.follow_candle(asset)

    async def get_realtime_candles(self, asset: str):
        if self.api: return self.api.realtime_candles.get(asset, [])
        return []

    async def get_candles(self, asset, end_from_time, offset, period, progressive=False, timeout=30, use_cache=False):
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
            return None
        if history_data is None: return None
        candles = self.prepare_candles(asset, period, history_data)
        if progressive: return self.api.historical_candles.get("data", {})
        return candles

    async def _fetch_historical_batch(self, asset, fetch_time, offset, period, index, timeout):
        if self.api is None: return None
        payload = {"asset": asset, "index": index, "time": fetch_time, "offset": offset, "period": period}
        ws_msg = f'42["history/load",{json.dumps(payload)}]'
        event_name = f'candles_ready_{asset}_{index}'
        await self.api.event_registry.clear_event(event_name)
        self.api.send_websocket_request(ws_msg)
        try:
            return await self.api.event_registry.wait_event(event_name, timeout=timeout)
        except Exception:
            return None

    def _parse_historical_candles(self, raw_data):
        if raw_data is None: return []
        raw_candles = raw_data.get("data", []) or raw_data.get("candles", [])
        if not raw_candles: return []
        parsed = []
        for c in raw_candles:
            if isinstance(c, list) and len(c) >= 5:
                parsed.append({"time": int(c[0]), "open": float(c[1]), "close": float(c[2]), "high": float(c[3]), "low": float(c[4])})
            elif isinstance(c, dict) and "time" in c:
                parsed.append(c)
        return parsed

    async def get_historical_candles(self, asset, amount_of_seconds, period, timeout=30, max_workers=5, progress_callback=None):
        # ===== FIX 7: (5 workers + chunk=200) =====
        # .
        # (keepalive + watchdog ).
        max_workers = max_workers or 1
        chunk_seconds = period * FETCH_CHUNK_SIZE  # period * 200 = 12000s batch
        all_candles = {}
        current_time = int(time.time())
        target_start_time = current_time - amount_of_seconds
        block_size = amount_of_seconds // max_workers
        semaphore = asyncio.Semaphore(max_workers)

        async def worker(start_t, end_t, worker_id):
            worker_candles = {}
            async with semaphore:
                oldest_t = start_t
                consecutive_failures_in_worker = 0
                while oldest_t > end_t:
                    # ===== FIX 3: batch =====
                    if not self.api or not getattr(self.api.state, 'check_accepted_connection', False):
                        # —
                        break
                    index = next(_request_counter)
                    batch_data = await self._fetch_historical_batch(asset, oldest_t, chunk_seconds, period, index, timeout)
                    if not batch_data:
                        oldest_t -= chunk_seconds
                        consecutive_failures_in_worker += 1
                        if consecutive_failures_in_worker >= 3:
                            # 3 consecutive failures = connection dead — exit
                            break
                        # backoff
                        await asyncio.sleep(FETCH_BATCH_DELAY * 2)
                        continue
                    consecutive_failures_in_worker = 0
                    new_batch = self._parse_historical_candles(batch_data)
                    if not new_batch: oldest_t -= chunk_seconds; continue
                    batch_times = []
                    for c in new_batch:
                        ts = c['time']
                        if ts >= end_t and ts <= start_t:
                            worker_candles[ts] = c
                            batch_times.append(ts)
                    if not batch_times: oldest_t -= chunk_seconds; continue
                    batch_times.sort()
                    new_oldest = batch_times[0]
                    if progress_callback: progress_callback(start_t - new_oldest, start_t - end_t, len(worker_candles), f"Worker-{worker_id}")
                    oldest_t = new_oldest if new_oldest < oldest_t else oldest_t - chunk_seconds
                    # batches (0.1s — )
                    await asyncio.sleep(FETCH_BATCH_DELAY)
            return list(worker_candles.values())

        await self.start_candles_stream(asset, period)
        tasks = []
        for i in range(max_workers):
            s = current_time - (i * block_size)
            e = max(target_start_time, s - block_size)
            tasks.append(worker(s, e, i))
        results = await asyncio.gather(*tasks)
        for batch in results:
            for c in batch: all_candles[c['time']] = c
        return sorted(all_candles.values(), key=lambda x: x['time'])

    def prepare_candles(self, asset, period, history=None):
        if self.api is None: return []
        history_data = history if history is not None else self.api.candles.candles_data
        if history_data is None: return []
        if isinstance(history_data, dict):
            candles_list = history_data.get("candles") or history_data.get("data") or history_data.get("history") or []
        else:
            candles_list = history_data
        if not candles_list: return []
        # ===== FIX A: _parse_raw_candles calculate_candles =====
        # calculate_candles tick [time, price]
        # tick[1] open/high/low/close — (open == high ==
        # low == close) history/load
        # [time, open, close, high, low]. _parse_raw_candles
        # .
        candles_data = _parse_raw_candles(candles_list)
        # grill period ( )
        for c in candles_data:
            c['time'] = (int(c['time']) // period) * period
        candles_v2_data = process_candles_v2(self.api.candle_v2_data, asset, candles_data)
        return merge_candles(candles_v2_data)

    async def close(self):
        if self.api: return await self.api.close()
        return True

# ==============================================================================
# SECTION 8: MT4 WRITER & ASSETS (COMPLETE)
# ==============================================================================
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

DEBUG_LOGS = False
def dbg(msg: str):
    if DEBUG_LOGS: print(f"  \033[2m   [debug] {msg}\033[0m")

LOG_FILE = Path("qxchart.log")
def _log_to_file(line: str):
    # v13: تدوير السجل — عند تجاوز 10MB يُنقل إلى qxchart.old.log ويبدأ ملف جديد
    # (بدون هذه الحماية يمتلئ القرص بعد أسابيع من التشغيل المستمر).
    try:
        _max = globals().get('LOG_MAX_BYTES', 10 * 1024 * 1024)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > _max:
            _old = LOG_FILE.with_suffix('.old.log')
            try:
                if _old.exists():
                    _old.unlink()
            except Exception:
                pass
            LOG_FILE.replace(_old)
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")
    except Exception: pass

def logmsg(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    _log_to_file(line)
    # If live table is active, queue the message instead of printing directly
    # to avoid corrupting the redrawn table
    if '_STATUS_MESSAGES_QUEUE' in globals() and globals()['_STATUS_MESSAGES_QUEUE'] is not None:
        try:
            globals()['_STATUS_MESSAGES_QUEUE'].append(line)
            # keep last 5 messages
            if len(globals()['_STATUS_MESSAGES_QUEUE']) > 5:
                globals()['_STATUS_MESSAGES_QUEUE'] = globals()['_STATUS_MESSAGES_QUEUE'][-5:]
        except Exception:
            pass
    else:
        print(f"  \033[2m[{ts}]\033[0m {msg}")

def log_exception(context: str, exc: BaseException):
    ts = datetime.now().strftime("%H:%M:%S")
    tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(f"  \033[91m[{ts}] FATAL in {context}: {exc}\033[0m")
    _log_to_file(f"[{ts}] FATAL in {context}: {exc}\n{tb_text}")

def _thread_excepthook(args):
    log_exception(f"thread '{args.thread.name}'", args.exc_value)
threading.excepthook = _thread_excepthook

def _main_excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt): sys.__excepthook__(exc_type, exc_value, exc_tb); return
    log_exception("main thread (top level)", exc_value)
sys.excepthook = _main_excepthook

class _NullHandler(logging.Handler):
    def emit(self, record): pass

@contextlib.contextmanager
def suppress_terminal_output():
    _loggers = [logging.getLogger(), logging.getLogger("pyquotex"), logging.getLogger("Quotex"), logging.getLogger("websockets"), logging.getLogger("websocket"), logging.getLogger("asyncio")]
    _old_levels = [(l, l.level, l.disabled) for l in _loggers]
    _old_handlers = [(l, list(l.handlers)) for l in _loggers]
    for l in _loggers:
        l.handlers = [_NullHandler()]; l.setLevel(logging.CRITICAL + 1); l.disabled = True
    with open(os.devnull, 'w') as devnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = devnull, devnull
        try: yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
            for l, lvl, dis in _old_levels: l.setLevel(lvl); l.disabled = dis
            for l, hs in _old_handlers: l.handlers = hs

WINAPI_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        WM_COMMAND = 0x0111
        MT4_REFRESH_CHART = 33324
        GA_ROOT = 2
        user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW.restype = wintypes.BOOL
        user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        user32.GetAncestor.restype = wintypes.HWND
        user32.IsWindowVisible.argtypes = [wintypes.HWND]
        user32.IsWindowVisible.restype = wintypes.BOOL
        user32.IsWindow.argtypes = [wintypes.HWND]
        user32.IsWindow.restype = wintypes.BOOL
        user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, wintypes.INT]
        user32.GetWindowTextW.restype = wintypes.INT
        user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        user32.GetWindowTextLengthW.restype = wintypes.INT
        WINAPI_AVAILABLE = True
    except Exception: pass

_MT4_HWND = None
_MT4_HWND_LAST_SEARCH = 0
_LAST_GLOBAL_REFRESH = 0
_ENUM_PROC_REF = None

def find_mt4_window():
    global _MT4_HWND, _MT4_HWND_LAST_SEARCH, _ENUM_PROC_REF
    if not WINAPI_AVAILABLE: return None
    now = time.time()
    if _MT4_HWND and (now - _MT4_HWND_LAST_SEARCH < 30):
        if user32.IsWindow(_MT4_HWND): return _MT4_HWND
    _MT4_HWND = None
    _MT4_HWND_LAST_SEARCH = now
    found = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def enum_callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                if "MetaTrader 4" in buf.value or "MetaTrader4" in buf.value: found.append(hwnd)
                return False
        return True
    _ENUM_PROC_REF = enum_callback
    user32.EnumWindows(enum_callback, 0)
    _MT4_HWND = found[0] if found else None
    return _MT4_HWND

REFRESH_INTERVAL = 1.0
def refresh_mt4():
    global _LAST_GLOBAL_REFRESH
    if not WINAPI_AVAILABLE: return False
    now = time.time()
    if now - _LAST_GLOBAL_REFRESH < REFRESH_INTERVAL: return False
    _LAST_GLOBAL_REFRESH = now
    hwnd = find_mt4_window()
    if not hwnd: return False
    root = user32.GetAncestor(hwnd, GA_ROOT)
    target = root if root else hwnd
    user32.PostMessageW(target, WM_COMMAND, MT4_REFRESH_CHART, 0)
    return True

class Colors:
    GREEN = '\033[92m'; RED = '\033[91m'; BLUE = '\033[94m'; YELLOW = '\033[93m'
    CYAN = '\033[96m'; BOLD = '\033[1m'; DIM = '\033[2m'; RESET = '\033[0m'; CLEAR_LINE = '\033[K'
    # ===== ألوان إضافية مطلوبة للواجهة الجديدة (v3 UI) =====
    WHITE = '\033[97m'      # أبيض ساطع
    MAGENTA = '\033[95m'    # بنفسجي ساطع
    GRAY = '\033[90m'       # رمادي

def _current_period_label() -> str:
    # Subsecond labels
    if IS_SUBSECOND and SUBSECOND_LABEL:
        return SUBSECOND_LABEL
    if PERIOD >= 1440 and PERIOD % 1440 == 0:
        d = PERIOD // 1440
        return f"D{d}" if d > 1 else "D1"
    if PERIOD >= 60 and PERIOD % 60 == 0:
        h = PERIOD // 60
        return f"H{h}" if h > 1 else "H1"
    return f"M{PERIOD}"

def pretty_asset_name(symbol: str, period_label: str = None) -> str:
    if period_label is None:
        period_label = _current_period_label()
    base = symbol
    suffix = ""
    if base.upper().endswith("_OTC"):
        base = base[:-4]
        suffix = " · OTC"
    if len(base) == 6 and base.isalpha():
        pretty = f"{base[:3].upper()}/{base[3:].upper()}{suffix}"
    else:
        pretty = f"{base.upper()}{suffix}"
    return f"({pretty}),{period_label}"

user_home = os.path.expanduser('~')
MT4_CONFIG_FILE = Path("mt4_config.json")
# ===== FIX J: digits — =====
# : " " —
# .
# mt4_digits.json:
# {
# "global_digits": null, // null = ; ( 5)
# "overrides": {
# "USDIDR-OTC": 4,
# "USDPKR-OTC": 5
# }
# }
DIGITS_CONFIG_FILE = Path("mt4_digits.json")
_digits_config_cache = None
_digits_config_loaded = False

def load_digits_config() -> dict:
    """ mt4_digits.json . ."""
    global _digits_config_cache, _digits_config_loaded
    try:
        if DIGITS_CONFIG_FILE.exists():
            mtime = DIGITS_CONFIG_FILE.stat().st_mtime
            if not _digits_config_loaded or _digits_config_cache.get('_mtime', 0) < mtime:
                _digits_config_cache = json.loads(DIGITS_CONFIG_FILE.read_text())
                _digits_config_cache['_mtime'] = mtime
                _digits_config_loaded = True
        elif _digits_config_loaded:
            # —
            _digits_config_cache = None
            _digits_config_loaded = False
    except Exception:
        return {}
    return _digits_config_cache if _digits_config_cache else {}

def _resolve_digits(symbol: str, price: float = 0.0) -> int:
    """ .
 
 :
 1) per-asset mt4_digits.json ("overrides")
 2) mt4_digits.json ("global_digits")
 3) ( )
 
 (FIX J):
 - JPY: 3 ()
 - < 0.5: 6 (was 6) — BRLUSD
 - < 1: 5 (was 5)
 - < 5: 5 (was 5)
 - < 10: 4 (was 4)
 - < 50: 4 (was 4)
 - < 100: 3 (was 3)
 - < 1000: 3 (was 2) ← FIX J: 100-1000
 - < 10000: 3 (was 2) ← FIX J
 - >= 10000: 3 (was 2) ← FIX J
 : >= 100 digits=2 (min grid 0.01) — .
 : >= 100 digits=3 (min grid 0.001) — 
 mt4_digits.json.
 """
    sym_upper = symbol.upper()
    # 1) per-asset override
    cfg = load_digits_config()
    if cfg:
        overrides = cfg.get('overrides', {}) or {}
        if sym_upper in overrides:
            try:
                d = int(overrides[sym_upper])
                if 0 <= d <= 8:
                    return d
            except (TypeError, ValueError):
                pass
        # 2) global override
        global_d = cfg.get('global_digits', None)
        if global_d is not None:
            try:
                d = int(global_d)
                if 0 <= d <= 8:
                    return d
            except (TypeError, ValueError):
                pass
    # 3) auto calculation (improved FIX J defaults)
    if "JPY" in sym_upper: return 3
    if price and price > 0:
        if price < 0.5:  return 6
        if price < 1:    return 5
        if price < 5:    return 5
        if price < 10:   return 4
        if price < 50:   return 4
        if price < 100:  return 3
        # FIX J: >= 100 digits=3 ( 2)
        # → (0.001 0.01)
        return 3
    # fallback when no price
    if any(x in sym_upper for x in ["IDR", "COP", "ARS", "NGN", "PKR", "DZD", "EGP", "MXN", "PHP", "INR", "BDT", "ZAR", "BRL"]):
        return 3  # FIX J: was 2
    return 5
SYSTEM_FOLDERS = {"default", "downloads", "mailbox", "signals", "symbolsets", "deleted", "templates", "profiles", "mql4", "logs", "config", "history_backup"}

def _validate_mt4_path(path: str) -> bool:
    if not path or not os.path.exists(path): return False
    try:
        test_file = os.path.join(path, ".write_test.tmp")
        with open(test_file, 'w') as f: f.write("test")
        os.remove(test_file)
        return True
    except Exception: return False

def _save_mt4_path(path: str):
    try:
        config = json.loads(MT4_CONFIG_FILE.read_text()) if MT4_CONFIG_FILE.exists() else {}
        config["mt4_history_path"] = path
        config["saved_at"] = int(time.time())
        MT4_CONFIG_FILE.write_text(json.dumps(config, indent=2))
    except Exception: pass

def find_mt4_history_path() -> str:
    appdata = os.environ.get('APPDATA', '') or os.environ.get('HOME', '')
    common_path = os.path.join(appdata, 'MetaQuotes', 'Terminal', 'Common', 'Files', 'qx_hst')
    try:
        os.makedirs(common_path, exist_ok=True)
        return common_path
    except Exception:
        pass
    
    base_terminal = os.path.join(user_home, "AppData", "Roaming", "MetaQuotes", "Terminal")
    if not os.path.exists(base_terminal): return ""
    all_servers = []
    try:
        for terminal_id in os.listdir(base_terminal):
            history_path = os.path.join(base_terminal, terminal_id, "history")
            if not os.path.exists(history_path): continue
            for server_name in os.listdir(history_path):
                server_lower = server_name.lower()
                if server_lower in SYSTEM_FOLDERS or server_lower.startswith(".") or server_lower.startswith("_"): continue
                server_path = os.path.join(history_path, server_name)
                if not os.path.isdir(server_path): continue
                try:
                    hst_files = [f for f in os.listdir(server_path) if f.endswith('.hst')]
                    all_servers.append({"terminal_id": terminal_id, "server_name": server_name, "full_path": server_path, "has_hst": len(hst_files) > 0, "hst_count": len(hst_files), "is_writable": _validate_mt4_path(server_path)})
                except Exception: pass
    except Exception: pass
    if not all_servers: return ""
    if MT4_CONFIG_FILE.exists():
        try:
            saved_path = json.loads(MT4_CONFIG_FILE.read_text()).get("mt4_history_path", "")
            if saved_path and os.path.exists(saved_path):
                for srv in all_servers:
                    if srv["full_path"] == saved_path and srv["is_writable"]: return saved_path
        except Exception: pass
    writable_servers = [s for s in all_servers if s["is_writable"]]
    if not writable_servers: return ""
    servers_with_hst = [s for s in writable_servers if s["has_hst"]]
    if servers_with_hst:
        servers_with_hst.sort(key=lambda x: (-x["hst_count"], x["server_name"]))
        chosen = servers_with_hst[0]
        _save_mt4_path(chosen["full_path"])
        return chosen["full_path"]
    chosen = writable_servers[0]
    _save_mt4_path(chosen["full_path"])
    return chosen["full_path"]

MT4_HISTORY_PATH = find_mt4_history_path()
if not MT4_HISTORY_PATH:
    MT4_HISTORY_PATH = os.path.join(user_home, "Desktop", "MT4_History_Fallback")
    os.makedirs(MT4_HISTORY_PATH, exist_ok=True)

SESSION_FILE = Path("session.json")
SESSION_STATE_FILE = Path("session_state.json")
EMAIL_FILE = Path("saved_email.txt")

class SessionManager:
    def __init__(self): self.state = self._load_state()
    def _load_state(self) -> dict:
        try:
            if SESSION_STATE_FILE.exists(): return json.loads(SESSION_STATE_FILE.read_text())
        except Exception: pass
        return {"last_login": 0, "last_success": False, "failed_auth_count": 0, "email": "", "host": "qxbroker.com"}
    def _save_state(self):
        try: SESSION_STATE_FILE.write_text(json.dumps(self.state, indent=2))
        except Exception: pass
    def should_force_fresh(self) -> bool:
        if not self.state.get("last_success", False): return True
        if self.state.get("failed_auth_count", 0) >= 2: return True
        if time.time() - self.state.get("last_login", 0) > 7 * 24 * 3600: return True
        return False
    def record_success(self, email: str, host: str = None):
        # FIX K:
        update_dict = {"last_login": time.time(), "last_success": True, "failed_auth_count": 0, "email": email}
        if host: update_dict["host"] = host
        self.state.update(update_dict)
        self._save_state()
        EMAIL_FILE.write_text(email)
    def record_failure(self, error: str):
        self.state["last_login"] = time.time()
        self.state["last_success"] = False
        self.state["failed_auth_count"] = self.state.get("failed_auth_count", 0) + 1
        self._save_state()
    def get_saved_email(self) -> str:
        email = self.state.get("email", "")
        return email if email else (EMAIL_FILE.read_text().strip() if EMAIL_FILE.exists() else "")

    def get_saved_host(self) -> str:
        # FIX K:
        return self.state.get("host", "qxbroker.com")
    @staticmethod
    def delete_session_file():
        if SESSION_FILE.exists():
            try: SESSION_FILE.unlink(); return True
            except Exception: pass
        return False
    @staticmethod
    def delete_browser_dir():
        browser_dir = Path("browser")
        if browser_dir.exists():
            try: shutil.rmtree(browser_dir, ignore_errors=True); return True
            except Exception: pass
        return False

session_manager = SessionManager()

# ==============================================================================
# UPDATED ASSET LIST & CANDLE COUNT SETTINGS
# ==============================================================================
ASSET_LIST = [
    "BRLUSD_otc", "USDARS_otc", "USDBDT_otc", "USDCOP_otc", "USDEGP_otc",
    "USDIDR_otc", "USDINR_otc", "USDMXN_otc", "USDNGN_otc", "USDPHP_otc",
    "USDPKR_otc", "USDZAR_otc", "AUDCAD_otc", "AUDCHF_otc", "AUDJPY_otc",
    "AUDNZD_otc", "AUDUSD_otc", "CADCHF_otc", "CADJPY_otc", "CHFJPY_otc",
    "EURAUD_otc", "EURCAD_otc", "EURCHF_otc", "EURGBP_otc", "EURJPY_otc",
    "EURNZD_otc", "EURUSD_otc", "GBPAUD_otc", "GBPCAD_otc", "GBPCHF_otc",
    "GBPJPY_otc", "GBPNZD_otc", "GBPUSD_otc", "NZDCAD_otc", "NZDCHF_otc",
    "NZDJPY_otc", "NZDUSD_otc", "USDCAD_otc", "USDCHF_otc", "USDDZD_otc", "USDJPY_otc",
]

TIMEFRAMES = [
    (1,    60,      "M1  - 1 minute",      False),
    (2,    120,     "M2  - 2 minutes",     False),
    (3,    180,     "M3  - 3 minutes",     False),
    (5,    300,     "M5  - 5 minutes",     False),
    (10,   600,     "M10 - 10 minutes",    False),
    (15,   900,     "M15 - 15 minutes",    False),
    (30,   1800,    "M30 - 30 minutes",    False),
    (60,   3600,    "H1  - 1 hour",        False),
    (240,  14400,   "H4  - 4 hours",       False),
    (1440, 86400,   "D1  - 1 day",         False),
    # Subsecond timeframes (aggregated locally from realtime ticks, no history API)
    (1,    5,       "S5  - 5 seconds",     True),
    (1,    10,      "S10 - 10 seconds",    True),
    (1,    15,      "S15 - 15 seconds",    True),
    (1,    30,      "S30 - 30 seconds",    True),
]

PERIOD = 1
PERIOD_SECONDS = 60
# Subsecond mode globals — set when user chooses S5/S10/S15/S30
IS_SUBSECOND = False
SUBSECOND_SECONDS = 0   # 5, 10, 15, or 30
SUBSECOND_LABEL = ""    # "5S", "10S", "15S", "30S"
SUBSECOND_MAX_CANDLES = 500  # v8.1: raised from 200 -> 500 to match SUBSECOND_HISTORY_CANDLES (user asked: keep >=500 5s candles in memory)
SUBSECOND_HISTORY_CANDLES = 500  # fetch up to 500 historical subsecond candles at startup (was 1000, reduced for speed)
# Semaphore to limit concurrent subsecond history fetches (3 at a time, not 41)
# Created lazily on first use to avoid event loop binding issues at import time
_SUBSECOND_FETCH_SEMAPHORE = None
# v8.1: explicit asset-to-asset delay for subsecond mode (user asked: ~1 second between currencies)
SUBSECOND_ASSET_DELAY = 2.0   # v8.3: raised from 1.0 -> 2.0 (server needs more breathing room between assets)
# v8.3: target fewer 1s candles -- the server throttles after ~5 chunks per asset, so 2.0x margin
# was pointless (we'd never reach it anyway). 1.3x targets 3250 1s = enough for 500 5s after dedup.
SUBSECOND_FETCH_MARGIN = 1.3  # v8.3: was 2.0 -- reduced to lower request count per asset
SUBSECOND_MAX_CHUNKS = 5      # v8.3: was 60 -- 5 chunks * 500s = 2500s = exactly 500 5s candles; more is wasted
# v8.3: user explicitly asked -- if the server returns >=85 5s candles from the first chunk, do not
# keep repeating the requests. Accept the server's per-asset history limit and move on.
SUBSECOND_EARLY_EXIT_CANDLES = 85  # stop fetching more chunks once we have >=85 aggregated 5s candles
# v8.3: graceful stop -- after this many consecutive zero-candle assets, the WebSocket is dead.
# Break the startup loop cleanly instead of burning 8 * 30s = 240s in reconnect attempts.
SUBSECOND_MAX_ZERO_STREAK = 3  # was effectively infinite (relied on MAX_RECONNECTS_DURING_FETCH=8)
# v8.4/v8.6: NEW feature for M1 timeframe -- fetch 1s candles first, aggregate
# to 1m, use them as the most granular bridge between the historical 1m fetch
# and the live stream. Disables the old _bridge_fetch_recent_candles for M1.
#
# v8.6 change: switched from 5s aggregation -> 1s aggregation. 1s is the most
# granular source -- if the server's 1s data is continuous, the aggregated 1m
# candle has NO gaps (60 consecutive 1s candles -> 1 perfect 1m candle). With
# 5s aggregation, a missing 5s candle leaves a partial gap in the 1m candle.
M1_USE_1S_BRIDGE = True       # set False to fall back to the old M1 bridge fetch
M1_1S_BRIDGE_TARGET = 750     # v8.6: target 1s candles for the bridge (=> ~12 1m candles)
M1_BRIDGE_TIMEOUT = 30        # seconds, bounded wait for the 1s fetch
# v8.11: delays to prevent server throttling in M1 bridge mode.
# User explicitly asked: "مهلات لكي لا لا يتوقف السرفر" (delays so the
# server doesn't stop). The pattern per asset is:
#   1s fetch -> M1_INTRA_ASSET_DELAY -> 1000 historical fetch -> M1_ASSET_DELAY -> next asset
M1_INTRA_ASSET_DELAY = 1.0    # v8.11: delay between 1s fetch and 1000 historical fetch (same asset)
M1_ASSET_DELAY = 1.0          # v8.11: delay between assets in M1 bridge mode (was 0.1s)
# v8.13: cap the bridge to the NEWEST N candles only, then REPLACE matching
# historical candles. User explicitly asked: "نربط 6 شموع الاولى فقط" (only
# bridge the first 6). The max gap between live stream and historical is 5
# candles, so 6 bridge candles guarantee full coverage. The server returns
# a variable count of 1s candles (8/12/13), so we always take the last 6.
M1_BRIDGE_REPLACE_COUNT = 6   # v8.13: only the newest N bridge candles replace historical
# v8.7: TEST MODE -- when True, for M1 timeframe, SKIP the 1000 historical
# 1m fetch entirely and display ONLY the 1s->1m aggregated candles on the chart.
# This lets us verify that the 1s aggregation produces valid 1m candles that MT4
# can render correctly. Once verified, set False to restore the full flow
# (historical 1000 1m + 1s->1m bridge merged).
# v8.10: TEST MODE disabled -- full flow is now active:
#   1) fetch 1s candles -> aggregate to 1m (8-13 bridge candles, no gaps)
#   2) fetch 1000 historical 1m candles via fetch_candles_with_retry
#   3) merge: [1000 historical] + [bridge where ts > last historical ts]
#   4) the bridge fills the 4-5 missing candles between historical and live
# Set to True to re-enter TEST MODE (1s->1m only, no historical fetch).
M1_TEST_1S_ONLY = False       # v8.10: TEST MODE disabled, full flow active
# ===== FIX 4: 1000 ( ) =====
# 500 1000 (4s).
# : workers=5 + chunk=200 ( ) .
INITIAL_CANDLES = 1000
MIN_CANDLES_THRESHOLD = 100
HISTORY_DAYS = 0.75
FETCH_DURATION_SECONDS = int(86400 * HISTORY_DAYS)
# v9.0: STREAM_POLL_INTERVAL reduced from 0.15s -> 0.05s for fastest possible tick updates.
# This is the loop inside realtime_stream / subsecond_stream that polls CLIENT.api.realtime_candles.
# Lower = faster live tick rendering on the chart.
STREAM_POLL_INTERVAL = 0.05
# v10.0: Flask web dashboard REMOVED — MT4 .hst files are the ONLY output channel.
# WRITE_HST_FILES_ENABLED must stay True, otherwise the server produces no output.
WRITE_HST_FILES_ENABLED = True
# ===== FIX 4: WRITE_INTERVAL = 0.5s 3.0s ( 500ms) =====
WRITE_INTERVAL = 0.5
# ===== v13: ثوابت التحميل المسبق والبث المتعدد والقرص =====
# BRLUSD_otc = عملة فتح الشارت (طلب المستخدم) — تُحمّل فوراً بعد الدخول.
PRELOAD_FIRST_SYMBOL = "BRLUSD_otc"
PRELOAD_CANDLES = 300          # 300 شمعة لكل عملة عند فتح شارتها (طلب المستخدم)
PAGINATION_BATCH = 300         # v13.2: دفعة التمرير للخلف 300 شمعة وليس 170 (طلب المستخدم)
PRELOAD_MIN_CANDLES = 30       # أقل عدد مقبول من الشموع لعملة واحدة
PRELOAD_ASSET_DELAY = 1.0      # ثانية واحدة بين عملة وأخرى (واحدة تلو الأخرى)
PRELOAD_TIMEOUT = 25.0         # مهلة طلب الشموع لكل عملة
PRELOAD_WAIT_INSTRUMENTS = 120 # أقصى انتظار لقائمة العملات بعد الدخول
PRELOAD_REFRESH_INTERVAL = 900 # كل 15 دقيقة: أصول فتحت حديثاً / أصول أُغلقت
# التيكات: في الذاكرة فقط، وتُحذف تلقائياً بعد 5 دقائق (طلب المستخدم صراحةً
# حتى لا يمتلئ القرص بالتيكس بعد شهر من التشغيل).
TICK_RETENTION_SECONDS = 300
TICK_PURGE_INTERVAL = 30
TICK_CACHE_MAXLEN = 600        # حد أقصى للتيكات المحفوظة لكل عملة
# أمان القرص:
MT4_WRITE_THROTTLE = 1.0       # كان 0.2s لعملة واحدة؛ مع ~90 عملة = 1.0s لكتابة HST
ASSET_MAX_CANDLES = 3000       # كان 1000؛ رُفع لكي تتراكم دفعات التمرير للخلف
CANDLESTORE_KEEP_PER_SYMBOL = 5000  # أقصى شموع محفوظة في candles.db لكل عملة
DB_TRIM_INTERVAL = 3600        # فحص حجم candles.db كل ساعة
LOG_MAX_BYTES = 10 * 1024 * 1024    # تدوير qxchart.log عند 10MB
STALE_DATA_TIMEOUT = 180
STALE_RATIO_TRIGGER = 0.8
# ===== FIX 7: KEEPALIVE_PING_INTERVAL = 5s =====
# : " ".
# 10s (5 workers × 41 )
# keepalive . 5s .
KEEPALIVE_PING_INTERVAL = 5
RECONNECT_CHECK_INTERVAL = 1
RECONNECT_BASE_DELAY = 2
RECONNECT_MAX_DELAY = 30
STATUS_REFRESH_INTERVAL = 0.5
# ===== FIX 7: watchdog =====
# .
# STALE_MESSAGE_TIMEOUT=45s + STALE_WATCHDOG_INTERVAL=5s
# => latency = 45-50s ( )
# FIX 7: STALE_MESSAGE_TIMEOUT=20s + STALE_WATCHDOG_INTERVAL=3s
# => latency = 20-23s ( ~2x)
STALE_MESSAGE_TIMEOUT = 20
STALE_WATCHDOG_INTERVAL = 3  # 3s (was 5s)
ENGINEIO_PING_INTERVAL = 20  # "2" (engine.io ping) 20s — Socket.IO EIO=3
# ===== FIX 4: 4s 1000 =====
# ( 4s 1000 ):
# max_workers=5, chunk=period*200 (12000s), delay=0.1s
# : :
# - FETCH_ASSET_DELAY (0.1s)
# - workers ( FIX 3)
# - exponential backoff retry ( FIX 3)
# - main loop ( FIX 3)
# : 4s + ( FIX 1+2 )
FETCH_MAX_WORKERS = 5          # 5 workers (reverted — 10 caused connection drops)
FETCH_CHUNK_SIZE = 200         # 200 candles per batch (reverted)
FETCH_BATCH_DELAY = 0.1        # 0.1s between batches (reverted)
FETCH_ASSET_DELAY = 0.1        # 0.1s between assets (reverted)
# ===== FIX 7: cooldown — =====
FETCH_COOLDOWN_EVERY = 0       # 0 =
FETCH_COOLDOWN_DURATION = 0.0  # 0 =
FETCH_TIMEOUT = 30             # 30s per batch (reverted)
RETRY_BACKOFF_BASE = 2         # exponential backoff base
RETRY_BACKOFF_MAX = 15         # max delay between retries (reverted)
MAX_FETCH_RETRIES = 5          # 5 attempts (reverted)

MAX_RECONNECTS_DURING_FETCH = 8
# ===== FIX L1: gap fill 120 () 20 =====
# : " "
# 20 (20 ) 20 — .
# 120 () /.
GAP_FILL_CANDLES = 10  # fetch 10 recent candles to replace incomplete ones
# ===== FIX L1: 5 ( ) =====
# : _gap_filled = True => .
# : GAP_FILL_REFRESH_INTERVAL .
GAP_FILL_REFRESH_INTERVAL = 300  # 5

# ==============================================================================
# ===== BRIDGE FETCH (سد فجوة 4-5 شموع بين التاريخي والبث المباشر) =====
# ==============================================================================
# المشكلة: بعد انتهاء الجلب التاريخي (الذي يستغرق 5-15 ثانية)، يكون البث قد بدأ
#   لكن الخادم يؤجل إرسال ticks بسبب ضغط طلبات history/load. النتيجة: فجوة 4-5 شموع.
# الحل: بعد اكتمال الجلب التاريخي، اطلب آخر شموع تنتهي عند time.time() الحالي
#   (وليس T0). هذا يملأ الفجوة بين آخر شمعة تاريخية وأول شمعة بث مباشر.
# الأمان:
#   - BRIDGE_FETCH_ENABLED=False يُعطّل الميزة فوراً دون أي تأثير جانبي
#   - كل الأعمدة محاطة بـ try/except (الخطأ لا يُكسر الجلب التاريخي)
#   - Semaphore يمنع إرهاق الخادم بطلبات جسر متزامنة
#   - يستخدم get_candles الموجودة (دالة مُجرّبة وآمنة)
BRIDGE_FETCH_ENABLED = True       # مفتاح التشغيل/الإيقاف الرئيسي
BRIDGE_FETCH_CANDLES = 15         # عدد الشموع لجلب الجسر (يكفي لفجوة كبيرة + هامش أمان)
BRIDGE_FETCH_TIMEOUT = 20         # مهلة الجلب الجسري (ثانية) — زادت من 15 إلى 20
BRIDGE_FETCH_SEMAPHORE_LIMIT = 2  # أقصى عدد طلبات جسر متزامنة (لمنع إرهاق الخادم)
_BRIDGE_FETCH_SEMAPHORE = None    # يُنشأ تلقائياً عند أول استخدام (lazy init)

# ===== FIX L2: — =====
# : _is_dst time.altzone/time.timezone
# Windows ( DST
# DST — Africa/Algiers).
# : / HST → MT4.
# : datetime.now().astimezone().utcoffset() ( )
# .
try:
    from datetime import datetime as _dt_naive
    _SYSTEM_TZ_OFFSET = int(_dt_naive.now().astimezone().utcoffset().total_seconds())
except Exception:
    _SYSTEM_TZ_OFFSET = -time.timezone  # fallback ( )
# ===== " " : =====
# :
# LOCAL_TZ_OFFSET_SECONDS = 3600 # UTC+1 ( )
# LOCAL_TZ_OFFSET_SECONDS = 0 # UTC ( )
# LOCAL_TZ_OFFSET_SECONDS = 7200 # UTC+2 ( )
# LOCAL_TZ_OFFSET_SECONDS = 10800 # UTC+3 ( )
# None .
LOCAL_TZ_OFFSET_SECONDS = None  # None = _SYSTEM_TZ_OFFSET

def _get_tz_offset() -> int:
    """ (UTC → ). ."""
    if LOCAL_TZ_OFFSET_SECONDS is not None:
        return LOCAL_TZ_OFFSET_SECONDS
    return _SYSTEM_TZ_OFFSET

def _align_time(raw_ts: int, period_seconds: int = None) -> int:
    """Aligns a raw timestamp to period boundary after applying TZ offset.

 period_seconds=None reads PERIOD_SECONDS global dynamically (multi-timeframe support).
 """
    if period_seconds is None:
        period_seconds = PERIOD_SECONDS
    tz = _get_tz_offset()
    return ((int(raw_ts) + tz) // period_seconds) * period_seconds

# Fill missing slots with flat candles. max_gap=1440 (full day) allows filling
# gaps up to 1 day. period_seconds=None reads PERIOD_SECONDS dynamically.
def _fill_missing_slots(candles: list, period_seconds: int = None,
                        max_gap: int = 1440) -> list:
    """Fills time gaps between candles with flat candles (previous close).

 - Added candles have volume=0 (marked synthetic).
 - max_gap: max number of periods to fill (1440 = 1 day for M1).
 - period_seconds=None reads PERIOD_SECONDS dynamically (multi-timeframe).
 """
    if period_seconds is None:
        period_seconds = PERIOD_SECONDS
    if len(candles) < 2:
        return list(candles)
    candles = sorted(candles, key=lambda x: x['time'])
    out = [dict(candles[0])]
    for i in range(1, len(candles)):
        prev = out[-1]
        curr = candles[i]
        gap = (curr['time'] - prev['time']) // period_seconds
        if 0 < gap <= max_gap:

            slot = prev['time'] + period_seconds
            while slot < curr['time']:
                out.append({
                    'time': slot,
                    'open': prev['close'],
                    'high': prev['close'],
                    'low': prev['close'],
                    'close': prev['close'],
                    'volume': 0,
                })
                slot += period_seconds
        out.append(dict(curr))
    return out

# Aggregate 1-second candles into target_period (5s, 10s, 15s, 30s) candles.
# Used for sub-60s timeframes: fetch period=1 from server, aggregate locally.
def _aggregate_sub_minute(candles: list, target_period: int) -> list:
    """Aggregate 1-second candles into target_period candles.

    For each group of (target_period) consecutive 1s candles:
    - time = first candle's time aligned to target_period boundary
    - open = first candle's open
    - high = max of all highs
    - low = min of all lows
    - close = last candle's close
    - volume = sum of all volumes
    """
    if not candles or target_period <= 1:
        return list(candles)
    candles = sorted(candles, key=lambda x: x['time'])
    buckets = OrderedDict()
    for c in candles:
        bucket_time = (c['time'] // target_period) * target_period
        if bucket_time not in buckets:
            buckets[bucket_time] = {
                'time': bucket_time,
                'open': c['open'],
                'high': c['high'],
                'low': c['low'],
                'close': c['close'],
                'volume': int(c.get('volume', 0) or 0),
            }
        else:
            b = buckets[bucket_time]
            b['high'] = max(b['high'], c['high'])
            b['low'] = min(b['low'], c['low'])
            b['close'] = c['close']
            b['volume'] += int(c.get('volume', 0) or 0)
    return list(buckets.values())

# ==============================================================================
# ===== GEO DOMAIN (التعرف التلقائي على البلد عبر IP) — v10.0 =====
# ==============================================================================
# القاعدة (طلب المستخدم):
#   بنغلاديش (BD)  -> market-qx.info   (نطاق بنغلاديش)
#   أي دولة أخرى   -> quotex.com       (النطاق الرسمي العالمي)
# يتم التعرف على "البلد فقط" (وليس الموقع الدقيق) عبر IP عند كل تشغيل.
DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
DEFAULT_DOMAIN_GLOBAL = "quotex.com"
QX_HOST = DEFAULT_DOMAIN_GLOBAL
_GEO_CACHE = {"country": None, "checked_at": 0.0}

def detect_country_code(timeout: float = 4.0):
    """يرجع رمز البلد فقط (مثل BD / SA / EG) عبر IP العام. لا يجلب أي موقع دقيق."""
    if _GEO_CACHE["country"] and time.time() - _GEO_CACHE["checked_at"] < 3600:
        return _GEO_CACHE["country"]
    endpoints = [
        ("http://ip-api.com/json/?fields=status,countryCode", lambda d: (d or {}).get("countryCode")),
        ("https://ipapi.co/json/", lambda d: (d or {}).get("country_code")),
        ("https://api.ip.sb/geoip", lambda d: (d or {}).get("country_code")),
    ]
    for url, extract in endpoints:
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
            code = extract(r.json())
            if code:
                _GEO_CACHE["country"] = str(code).upper()
                _GEO_CACHE["checked_at"] = time.time()
                return _GEO_CACHE["country"]
        except Exception:
            continue
    return None

def resolve_qx_host() -> str:
    """يحدد النطاق تلقائياً حسب البلد ويضبط QX_HOST العام:
    بنغلاديش -> market-qx.info ، أي دولة أخرى (أو فشل التعرف) -> quotex.com."""
    global QX_HOST
    country = detect_country_code()
    if country == "BD":
        QX_HOST = DEFAULT_DOMAIN_BANGLADESH
    else:
        QX_HOST = DEFAULT_DOMAIN_GLOBAL
    return QX_HOST

# ==============================================================================
# ===== SINGLE AUTHORITY FOR CONNECTION DEATH (منع الانقطاعات الوهمية) =====
# ==============================================================================
# المشكلة السابقة: on_error و on_close و stale_message_watchdog و health_monitor
# كانوا يكتبون CONNECTION_ALIVE = False كلٌّ على حدة (سباق حالة + سجلات مكررة +
# كتابة مكررة لـ LAST_CONNECTION_DROP_TIME). الآن كل الطرق تمر من هنا وحدها.
_CONN_DEATH_LOCK = threading.Lock()

def mark_connection_dead(source: str):
    """السلطة الوحيدة للإعلان عن موت الاتصال: تكتب العلم تحت قفل، تسقط وقت
    الانقطاع مرة واحدة فقط، وتسجل مصدر الإعلان."""
    global CONNECTION_ALIVE, LAST_CONNECTION_DROP_TIME
    was_alive = True
    try:
        with _CONN_DEATH_LOCK:
            was_alive = CONNECTION_ALIVE
            CONNECTION_ALIVE = False
            if LAST_CONNECTION_DROP_TIME == 0:
                LAST_CONNECTION_DROP_TIME = time.time()
    except Exception:
        pass
    if was_alive:
        try:
            logmsg(f"[connection] marked DEAD by {source}")
        except Exception:
            pass

# ==============================================================================
# ===== FULL ASSET LIST + PAYOUT % + OPEN/CLOSED (طريقة pyquotex الرسمية) =====
# ==============================================================================
# الطريقة الرسمية من مستودع pyquotex (cleitonleonel/pyquotex):
#   1) الإرسال عبر نفس WebSocket:  42["instruments/get"]
#   2) الرد يصل بصيغة:             451-["instruments/list", [ ... ]]
#   3) كل عنصر في القائمة يحتوي:
#        i[1]  = اسم الأصل (EURUSD_otc)     i[2]  = الاسم المعروض
#        i[5]  = نسبة الدفع payout %        i[14] = الحالة (True=مفتوح / False=مغلق)
#        i[18] = نسبة دفع التيربو turbo     i[-10],i[-9],i[-8] = أرباح 24H/1M/5M
PAYOUT_REFRESH_INTERVAL = 60
try:
    ASSETS_PAYOUT_FILE = Path(__file__).resolve().parent / "qx_assets_payouts.json"
except Exception:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")

def _instruments_snapshot():
    """يبني قائمة الأصول الكاملة (الاسم + نسبة الدفع + الحالة) من instruments."""
    if CLIENT is None or CLIENT.api is None:
        return []
    insts = CLIENT.api.instruments or []
    out = []
    for i in insts:
        try:
            if not isinstance(i, (list, tuple)) or len(i) < 6:
                continue
            entry = {
                "asset": str(i[1]) if len(i) > 1 else "",
                "name": str(i[2]).replace("\n", " ").strip() if len(i) > 2 else "",
                "payout": i[5] if len(i) > 5 else None,
            }
            try:
                entry["id"] = str(i[0])
            except Exception:
                entry["id"] = ""
            try:
                entry["turbo_payout"] = i[18] if len(i) > 18 else None
            except Exception:
                entry["turbo_payout"] = None
            try:
                entry["open"] = bool(i[14]) if len(i) > 14 else None
            except Exception:
                entry["open"] = None
            # أرباح الفريمات (طريقة get_payment الرسمية): -10=24H ، -9=1M ، -8=5M
            try:
                entry["profit_24h"] = i[-10]
            except Exception:
                entry["profit_24h"] = None
            try:
                entry["profit_1m"] = i[-9]
            except Exception:
                entry["profit_1m"] = None
            try:
                entry["profit_5m"] = i[-8]
            except Exception:
                entry["profit_5m"] = None
            out.append(entry)
        except Exception:
            continue
    return out

def _save_assets_payout_file(entries):
    """يحفظ لقطة كاملة إلى qx_assets_payouts.json بجانب الملف."""
    try:
        payload = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "host": QX_HOST,
            "count": len(entries),
            "open_count": sum(1 for e in entries if e.get("open")),
            "closed_count": sum(1 for e in entries if e.get("open") is False),
            "assets": entries,
        }
        ASSETS_PAYOUT_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        logmsg(f"[payout] failed to save {ASSETS_PAYOUT_FILE}: {e}")
        return False

async def fetch_instruments_now(timeout: float = 12.0):
    """طريقة pyquotex الرسمية: إرسال 42["instruments/get"] عبر نفس WebSocket
    والانتظار حتى وصول 451-["instruments/list"] ثم تخزينها في CLIENT.api.instruments.
    طريقة الدخول وطريقة جلب الشموع لا تتأثر إطلاقاً."""
    if CLIENT is None or CLIENT.api is None:
        return []
    try:
        await CLIENT.api.event_registry.clear_event("instruments_ready")
    except Exception:
        pass
    try:
        CLIENT.api.send_websocket_request('42["instruments/get"]')
    except Exception as e:
        logmsg(f"[payout] instruments request failed: {e}")
    data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=timeout)
    if isinstance(data, dict) and data.get("_placeholder"):
        # الرد كان placeholder — ننتظر الرد الحقيقي (نفس سلوك المكتبة الرسمية)
        data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=5.0)
    if isinstance(data, list) and data:
        CLIENT.api.instruments = data
    return list(CLIENT.api.instruments or [])

def _print_payout_table(entries, updated_at=None):
    """طباعة الجدول الكامل في الترمينال: العملة / الاسم / الدفع / الحالة.
    v12 (طلب المستخدم: العرض في الترمينال): يُعاد رسم الجدول عند أي تغيير،
    والترتيب: المفتوحة أولاً ثم حسب نسبة الدفع الأعلى."""
    open_entries = [e for e in entries if e.get("open")]
    closed_entries = [e for e in entries if e.get("open") is False]

    def _payout_val(e):
        p = e.get("payout")
        return p if isinstance(p, (int, float)) else -1

    entries_sorted = sorted(
        entries,
        key=lambda e: (0 if e.get("open") else 1, -_payout_val(e)),
    )
    print(f"\n{Colors.CYAN}{'═' * 92}{Colors.RESET}")
    print(f"{Colors.BOLD}  FULL ASSET LIST — PAYOUT % — OPEN/CLOSED{Colors.RESET}")
    _updated_str = f"  |  Updated: {updated_at}" if updated_at else ""
    print(f"  Total: {len(entries)}  |  {Colors.GREEN}OPEN: {len(open_entries)}{Colors.RESET}"
          f"  |  {Colors.RED}CLOSED: {len(closed_entries)}{Colors.RESET}"
          f"  |  Domain: {QX_HOST}{_updated_str}")
    print(f"{Colors.CYAN}{'─' * 92}{Colors.RESET}")
    print(f"  {'ASSET':<16}{'NAME':<20}{'PAYOUT':>7}  {'TURBO':>6}  {'1M':>5}  {'5M':>5}  STATUS")
    print(f"{Colors.DIM}{'─' * 92}{Colors.RESET}")
    for e in entries_sorted:
        name = (e.get("asset") or "?")[:16]
        dname = ((e.get("name") or "").replace("\n", " ").strip() or "-")[:20]
        payout = e.get("payout")
        turbo = e.get("turbo_payout")
        p1 = e.get("profit_1m")
        p5 = e.get("profit_5m")
        payout_str = f"{payout}%" if isinstance(payout, (int, float)) else "-"
        turbo_str = f"{turbo}%" if isinstance(turbo, (int, float)) else "-"
        p1_str = f"{p1}%" if isinstance(p1, (int, float)) else "-"
        p5_str = f"{p5}%" if isinstance(p5, (int, float)) else "-"
        if e.get("open"):
            status = f"{Colors.GREEN}OPEN{Colors.RESET}"
        else:
            status = f"{Colors.RED}CLOSED{Colors.RESET}"
        print(f"  {name:<16}{dname:<20}{payout_str:>7}  {turbo_str:>6}  {p1_str:>5}  {p5_str:>5}  {status}")
    print(f"{Colors.CYAN}{'═' * 92}{Colors.RESET}")
    print(f"{Colors.DIM}  Full snapshot saved to: {ASSETS_PAYOUT_FILE}{Colors.RESET}\n")

async def asset_payout_monitor():
    """يجلب قائمة العملات الكاملة + نسبة الدفع + حالة الزوج (مفتوح/مغلق) بعد
    تسجيل الدخول، يطبع الجدول الكامل في الترمينال فوراً، يحفظ لقطة JSON، ثم
    يعيد طباعة الجدول في الترمينال عند أي تغيير (كل PAYOUT_REFRESH_INTERVAL ثانية).
    v12: يعيد المحاولة حتى 3 مرات قبل الانتظار للدورة التالية."""
    await asyncio.sleep(1.5)  # مهلة قصيرة حتى يستقر WebSocket بعد الدخول
    first = True
    last_signature = None
    while True:
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = []
            # v12: حتى 3 محاولات قبل الانتظار للدورة التالية
            for _attempt in range(1, 4):
                try:
                    await fetch_instruments_now(timeout=12.0)
                    entries = _instruments_snapshot()
                except Exception as e:
                    logmsg(f"[payout] refresh failed: {e}")
                if entries:
                    break
                logmsg(f"[payout] attempt {_attempt}: empty list, retrying...")
                await asyncio.sleep(3.0)
            if entries:
                _save_assets_payout_file(entries)
                _updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                signature = tuple(sorted(
                    (e.get("asset"), str(e.get("payout")), str(e.get("open")))
                    for e in entries))
                if first:
                    _print_payout_table(entries, updated_at=_updated_at)
                    first = False
                elif signature != last_signature:
                    # v12 (طلب المستخدم): العرض في الترمينال — إعادة رسم الجدول عند أي تغيير
                    _print_payout_table(entries, updated_at=_updated_at)
                    open_n = sum(1 for e in entries if e.get("open"))
                    closed_n = sum(1 for e in entries if e.get("open") is False)
                    logmsg(f"[payout] updated: {len(entries)} assets "
                           f"({open_n} open / {closed_n} closed) — snapshot saved")
                last_signature = signature
            else:
                logmsg("[payout] no instruments response from server — will retry next cycle")
        except Exception as e:
            log_exception("asset_payout_monitor", e)
        await asyncio.sleep(PAYOUT_REFRESH_INTERVAL)

ASYNC_LOOP = None
ASYNC_ENGINE_GENERATION = 0
_ENGINE_READY = threading.Event()
CONNECTION_ALIVE = False
CLIENT = None
EMAIL = None
PASSWORD = None
RECONNECTING = False
ALL_STREAMING_ASSETS = []
LAST_HEALTH_CHECK = 0
HEALTH_CHECK_INTERVAL = 20
# ===== FIX B: =====
# : " ".
# —
# 1000 .
LAST_CONNECTION_DROP_TIME = 0            # 0 =
LONG_DISCONNECT_THRESHOLD = 3600        # 3600s = 1
# ===== FIX F: =====
# mt4_gap_filler print()
# 0.5s →
# . : .
GAP_FILL_SUMMARY = ""  # ( mt4_gap_filler)
_STATUS_MESSAGES_QUEUE = []  # queue for log messages during live table (avoid corrupting redraw)
GAP_FILL_ACTIVE = False  # True

def _asyncio_loop_exception_handler(loop, context):
    exc = context.get("exception")
    if exc: log_exception(f"asyncio loop (gen {ASYNC_ENGINE_GENERATION})", exc)

def start_async_engine():
    global ASYNC_LOOP, ASYNC_ENGINE_GENERATION, CONNECTION_ALIVE
    while True:
        try:
            ASYNC_ENGINE_GENERATION += 1
            gen = ASYNC_ENGINE_GENERATION
            new_loop = asyncio.new_event_loop()
            new_loop.set_exception_handler(_asyncio_loop_exception_handler)
            asyncio.set_event_loop(new_loop)
            ASYNC_LOOP = new_loop
            _ENGINE_READY.set()
            if gen > 1:
                logmsg(f"[AsyncEngine] event loop recreated (gen {gen}). Rescheduling tasks...")
                mark_connection_dead(f"async engine restart (gen {gen})")
                asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
                asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
                asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
                # ===== FIX: stale watchdog loop =====
                asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
                for asset in ALL_STREAMING_ASSETS:
                    asset.stream_task = None
                    asset.streaming = False
            new_loop.run_forever()
        except Exception as e:
            log_exception(f"AsyncEngine (gen {ASYNC_ENGINE_GENERATION})", e)
            mark_connection_dead("async engine crash")
            time.sleep(1)

async_thread = threading.Thread(target=start_async_engine, daemon=True, name="AsyncEngine")
async_thread.start()
_ENGINE_READY.wait(timeout=10)

class Asset:
    @staticmethod
    def _derive_mt4_symbol(raw_symbol: str) -> str:
        s = raw_symbol.strip()
        is_otc = s.upper().endswith("_OTC")
        if is_otc:
            base = s[:-4].upper()
            if PERIOD_SECONDS < 60:
                # Sub-minute: compact name "AUDUSDOTC5S" (11 chars, fits 12-byte header)
                result = f"{base}OTC{SUBSECOND_LABEL}"
            else:
                result = f"{base}-OTC"
        else:
            if PERIOD_SECONDS < 60:
                result = f"{s.upper()}{SUBSECOND_LABEL}"
            else:
                result = s.upper()
        return result[:12] if result else raw_symbol.upper()[:12]

    def __init__(self, symbol):
        self.api_symbol = symbol
        self.symbol = self._derive_mt4_symbol(symbol)
        self.period = PERIOD
        self.price = 0.0
        self.previous_price = 0.0
        # For sub-minute: filename = {symbol}1.hst (e.g., AUDUSD-5S1.hst)
        # symbol is "AUDUSD-5S" (compact, fits 12-byte HST header)
        # For 60s+: filename = {symbol}{PERIOD}.hst (e.g., AUDUSD-OTC5.hst)
        if PERIOD_SECONDS < 60:
            self.path = os.path.join(MT4_HISTORY_PATH, f"{self.symbol}1.hst")
        else:
            self.path = os.path.join(MT4_HISTORY_PATH, f"{self.symbol}{PERIOD}.hst")
        self.candles = []
        self.last_write = 0.0
        self.updates = 0
        self.streaming = False
        self.stream_task = None
        self.last_update_time = 0
        self.last_saved_close = 0.0
        self.last_saved_candle_time = 0
        self.last_saved_candle_count = 0
        self.dirty = False
        self._gap_filled = False

    def digits(self, price: float = None) -> int:
        # FIX J: _resolve_digits ( mt4_digits.json)
        p = price if price is not None else self.price
        return _resolve_digits(self.symbol, p or 0.0)

    def has_new_data(self):
        if not self.candles: return False
        c = self.candles[-1]
        return (c['close'] != self.last_saved_close or c['time'] != self.last_saved_candle_time or len(self.candles) != self.last_saved_candle_count)

    def mark_dirty(self): self.dirty = True

    def write(self, force=False):
        # v10.0: skip HST writing entirely when WRITE_HST_FILES_ENABLED is False.
        # HST files are now the ONLY output channel (Flask dashboard removed).
        if not WRITE_HST_FILES_ENABLED:
            return False
        if not force and not self.has_new_data(): return False
        temp = self.path + ".tmp"
        # For sub-minute timeframes, write period=1 (M1) in the header so MT4 opens it
        header_period = 1 if PERIOD_SECONDS < 60 else self.period
        try:
            with open(temp, 'wb') as f:
                f.write(struct.pack('<i', 400))
                f.write(b"(C)opyright 2003, MetaQuotes Software Corp.".ljust(64, b'\0'))
                f.write(self.symbol.encode('ascii').ljust(12, b'\0')[:12])
                f.write(struct.pack('<i', header_period))
                first_price = self.candles[0]['close'] if self.candles else self.price
                f.write(struct.pack('<i', self.digits(first_price)))
                f.write(struct.pack('<i', int(time.time())))
                f.write(struct.pack('<i', int(time.time())))
                f.write(b'\0' * 52)
                for c in self.candles:
                    f.write(struct.pack('<i', c['time']))
                    f.write(struct.pack('<d', c['open']))
                    f.write(struct.pack('<d', c['low']))
                    f.write(struct.pack('<d', c['high']))
                    f.write(struct.pack('<d', c['close']))
                    f.write(struct.pack('<q', int(c.get('volume', 0))))
            # ===== FIX 4: WinError 5 (Access Denied) + WinError 32 =====
            # WinError 32. WinError 5 (Access Denied)
            # MT4 ( ).
            # : retry WinError 5 + 32 + fallback.
            def _is_lock_error(err_str):
                err_str = err_str.lower()
                return (
                    "winerror 32" in err_str or
                    "used by another process" in err_str or
                    "winerror 5" in err_str or
                    "access denied" in err_str or
                    "accès refusé" in err_str or
                    "acces refusé" in err_str or
                    "permission" in err_str
                )
            replaced = False
            for attempt in range(8):  # 8 5
                try:
                    os.replace(temp, self.path)
                    replaced = True
                    break
                except (PermissionError, OSError) as e:
                    err_str = str(e)
                    if _is_lock_error(err_str):
                        # : 50ms, 100ms, 150ms, 200ms, 250ms...
                        time.sleep(0.05 + 0.05 * attempt)
                        continue
                    raise
            if not replaced:
                # ===== FIX 4: fallback — rename =====
                # os.replace 8 .
                try:
                    with open(self.path, 'wb') as f:
                        # (header + candles)
                        with open(temp, 'rb') as src:
                            f.write(src.read())
                    replaced = True
                except Exception as fallback_err:
                    if not _is_lock_error(str(fallback_err)):
                        logmsg(f"[write:{self.symbol}] fallback write failed: {fallback_err}")
            try:
                if os.path.exists(temp): os.remove(temp)
            except Exception: pass
            if replaced:
                self.last_write = time.time()
                if self.candles:
                    self.last_saved_close = self.candles[-1]['close']
                    self.last_saved_candle_time = self.candles[-1]['time']
                    self.last_saved_candle_count = len(self.candles)
                self.dirty = False
                return True
            return False
        except Exception as e:
            err_str = str(e).lower()
            # ===== FIX 8: WinError 2 (file not found) + WinError 5 + 32 =====
            # — retry .
            if not any(x in err_str for x in [
                'winerror 2', 'winerror 5', 'winerror 32', 'winerror 13',
                'introuvable', 'refusé', 'access', 'permission', 'used by another',
                'ebusy', 'eperm', 'no such file'
            ]):
                logmsg(f"[write:{self.symbol}] write failed: {e}")
            try:
                if os.path.exists(temp): os.remove(temp)
            except Exception: pass
            return False

class WriterThread(threading.Thread):
    """FIX 11: WriterThread — HST 500ms Asset.write.
 
 : (1000 4s).
 :
 - fetch_candles_with_retry (1000 )
 - Asset.write HST {derived_symbol}{PERIOD}.hst (AUDJPY-OTC1.hst)
 - WriterThread asset.dirty 100ms + HST 500ms
 
 FIX 10 ( ) realtime_stream MT4_WRITER.update_candle.
 Asset.write WriterThread MT4_WRITER
 .
 """
    def __init__(self):
        super().__init__(daemon=True, name="WriterThread")
        self.running = True
    def run(self):
        while self.running:
            try:
                now = time.time()
                dirty_count = 0
                for asset in ALL_STREAMING_ASSETS:
                    # ===== FIX 11: MT4_WRITER =====
                    # ( — )
                    if asset.symbol in MT4_WRITER.sync_state:
                        continue
                    if asset.dirty and (now - asset.last_write >= WRITE_INTERVAL):
                        if asset.write():
                            dirty_count += 1
                if dirty_count > 0: refresh_mt4()
                time.sleep(0.1)
            except Exception as e:
                logmsg(f"[WriterThread] loop error: {e}")
                time.sleep(0.5)

writer_thread = WriterThread()
writer_thread.start()

async def connect_quotex(email, password, force_fresh=False, max_attempts=3):
    global CLIENT, CONNECTION_ALIVE, EMAIL, PASSWORD
    EMAIL, PASSWORD = email, password
    for attempt in range(1, max_attempts + 1):
        try:
            if CLIENT:
                try:
                    close_task = asyncio.create_task(CLIENT.close())
                    await asyncio.wait([close_task], timeout=3.0)
                except Exception: pass
                finally: CLIENT = None
            await asyncio.sleep(0.3)
            if force_fresh or attempt > 1:
                session_manager.delete_session_file()
                session_manager.delete_browser_dir()
            # FIX K: QX_HOST ( )
            CLIENT = Quotex(email=email, password=password, host=QX_HOST, lang="en")
            with suppress_terminal_output():
                check, reason = await CLIENT.connect()
            if check:
                try:
                    await CLIENT.change_account("PRACTICE")
                    await asyncio.sleep(0.5)
                except Exception: pass
                try: await CLIENT.get_all_assets()
                except Exception: pass
                CONNECTION_ALIVE = True
                # FIX K:
                session_manager.record_success(email, host=QX_HOST)
                return True
            else:
                error_msg = str(reason) if reason else "Unknown error"
                session_manager.record_failure(error_msg)
        except Exception as e:
            error_msg = str(e)[:200]
            session_manager.record_failure(error_msg)
            if attempt < max_attempts: await asyncio.sleep(5 * attempt)
    mark_connection_dead("connect_quotex: all attempts failed")
    return False

async def keepalive_loop():
    # ===== FIX 7: keepalive (5s) + =====
    # : " ".
    # : keepalive_loop
    # `await asyncio.sleep(KEEPALIVE_PING_INTERVAL)` .
    # : `asyncio.sleep` (0.5s) .
    # keepalive .
    tick_count = 0
    last_ping_at = 0.0
    while True:
        await asyncio.sleep(0.5)  # 500ms ()
        now = time.time()
        # : ping
        if now - last_ping_at < KEEPALIVE_PING_INTERVAL:
            continue
        last_ping_at = now
        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None: continue
        try:
            # 1) engine.io ping ( Socket.IO EIO=3) —
            CLIENT.api.send_websocket_request("2", no_force_send=False)
            # 2) application-level tick —
            CLIENT.api.send_websocket_request('42["tick"]', no_force_send=False)
            # 3)
            if tick_count % 3 == 0:
                CLIENT.api.send_websocket_request('42["instruments/get"]', no_force_send=False)
            tick_count += 1
        except Exception:
            pass


async def stale_message_watchdog():
    # ===== FIX: watchdog + =====
    # WS STALE_MESSAGE_TIMEOUT (45s)
    # .
    # latency ~25s <5s.
    # FIX B: auto_reconnect
    # (> ) —
    # .
    global CONNECTION_ALIVE, LAST_CONNECTION_DROP_TIME
    while True:
        await asyncio.sleep(STALE_WATCHDOG_INTERVAL)
        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            continue
        try:
            silent_for = time.time() - CLIENT.api.last_message_at
            if silent_for > STALE_MESSAGE_TIMEOUT:
                logmsg(
                    f"[stale_watchdog] no messages for {silent_for:.1f}s "
                    f"(>{STALE_MESSAGE_TIMEOUT}s); recycling connection."
                )
                # ===== FIX B: =====
                # LONG_DISCONNECT_THRESHOLD (1h)
                # .
                mark_connection_dead(f"stale_watchdog: silent {silent_for:.1f}s > {STALE_MESSAGE_TIMEOUT}s")
                # WS close frame on_close
                try:
                    if CLIENT.api.websocket_client and CLIENT.api.websocket_client.wss:
                        CLIENT.api.websocket_client.wss.close()
                except Exception:
                    pass
                # auto_reconnect
        except Exception as e:
            logmsg(f"[stale_watchdog] error: {e}")

async def health_monitor():
    global LAST_HEALTH_CHECK, CONNECTION_ALIVE
    consecutive_dead_checks = 0
    while True:
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)
        now = time.time()
        LAST_HEALTH_CHECK = now
        if not CONNECTION_ALIVE or CLIENT is None:
            consecutive_dead_checks = 0
            continue
        is_dead = False
        dead_reason = ""
        stale_count = sum(1 for a in ALL_STREAMING_ASSETS if a.updates > 0 and (now - a.last_update_time) > STALE_DATA_TIMEOUT)
        if stale_count > len(ALL_STREAMING_ASSETS) * STALE_RATIO_TRIGGER:
            is_dead = True
            dead_reason = f"stale ratio {stale_count}/{len(ALL_STREAMING_ASSETS)} exceeded {STALE_RATIO_TRIGGER}"
        if is_dead:
            mark_connection_dead(f"health_monitor: {dead_reason}")
            consecutive_dead_checks = 0

async def auto_reconnect():
    # ===== FIX B: + =====
    # : " ".
    # ( stale_message_watchdog )
    # LONG_DISCONNECT_THRESHOLD (1h).
    # 1000 .
    # FIX K: QX_HOST
    global CLIENT, CONNECTION_ALIVE, RECONNECTING, LAST_CONNECTION_DROP_TIME, QX_HOST
    consecutive_failures = 0
    while True:
        await asyncio.sleep(RECONNECT_CHECK_INTERVAL)
        # ===== FIX B: ( ) =====
        # stale_message_watchdog
        # (on_close on_error connect_quotex ).
        # .
        if not CONNECTION_ALIVE and LAST_CONNECTION_DROP_TIME == 0:
            LAST_CONNECTION_DROP_TIME = time.time()
            logmsg(f"[reconnect] connection loss detected at {LAST_CONNECTION_DROP_TIME:.0f}; "
                   f"will re-fetch all candles if outage exceeds {LONG_DISCONNECT_THRESHOLD}s")
        if CONNECTION_ALIVE or RECONNECTING:
            consecutive_failures = 0
            continue
        RECONNECTING = True
        try:
            email = session_manager.get_saved_email()
            # ===== FIX: try RECONNECTING =====
            # : `if not (email and PASSWORD): continue`
            # => try RECONNECTING = True =>
            # => !
            if not (email and PASSWORD):
                # RECONNECTING
                RECONNECTING = False
                continue
            delay = 0 if consecutive_failures == 0 else min(RECONNECT_BASE_DELAY * (2 ** (consecutive_failures - 1)), RECONNECT_MAX_DELAY)
            if delay > 0:
                logmsg(f"[reconnect] connection lost, retrying in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                logmsg("[reconnect] connection lost, reconnecting immediately...")
            # GEO-DOMAIN (v10.0): QX_HOST تم تحديده تلقائياً عند التشغيل من البلد
            # (بنغلاديش -> market-qx.info ، غير ذلك -> quotex.com).
            # لم نعد نتجاوزه بالنطاق المحفوظ القديم حتى لا يخالف قاعدة التعرف الجغرافي.
            success = await connect_quotex(email, PASSWORD, force_fresh=True, max_attempts=1)
            if success:
                logmsg("[reconnect] reconnect successful, restarting streams...")
                consecutive_failures = 0
                # ===== FIX 7: auto-throttle ( ) =====
                # ===== FIX: last_message_at =====
                # stale_watchdog .
                if CLIENT is not None and CLIENT.api is not None:
                    CLIENT.api.last_message_at = time.time()
                # ===== FIX B: =====
                drop_duration = 0.0
                should_refetch_all = False
                if LAST_CONNECTION_DROP_TIME > 0:
                    drop_duration = time.time() - LAST_CONNECTION_DROP_TIME
                    if drop_duration > LONG_DISCONNECT_THRESHOLD:
                        should_refetch_all = True
                        logmsg(
                            f"[reconnect] LONG disconnect detected: {drop_duration/60:.1f} min "
                            f"> {LONG_DISCONNECT_THRESHOLD/60:.0f} min threshold — "
                            f"will re-fetch ALL candles from scratch"
                        )

                LAST_CONNECTION_DROP_TIME = 0
                if should_refetch_all:
                    # streams
                    try:
                        asyncio.run_coroutine_threadsafe(refetch_all_candles(), ASYNC_LOOP)
                    except Exception as e:
                        logmsg(f"[reconnect] failed to schedule full re-fetch: {e}")
                        # fallback: streams
                        for asset in ALL_STREAMING_ASSETS:
                            try:
                                if asset.stream_task and not asset.stream_task.done():
                                    asset.stream_task.cancel()
                                asset.streaming = False
                                asset.stream_task = asyncio.run_coroutine_threadsafe(subsecond_stream(asset) if IS_SUBSECOND else realtime_stream(asset), ASYNC_LOOP)
                                await asyncio.sleep(0.05)
                            except Exception as e2:
                                logmsg(f"[reconnect] failed to restart stream for {asset.symbol}: {e2}")
                else:
                    # (< ) — streams
                    if drop_duration > 0:
                        logmsg(f"[reconnect] short disconnect ({drop_duration:.1f}s) — restarting streams only")
                    for asset in ALL_STREAMING_ASSETS:
                        try:
                            if asset.stream_task and not asset.stream_task.done():
                                asset.stream_task.cancel()
                            asset.streaming = False
                            asset.stream_task = asyncio.run_coroutine_threadsafe(subsecond_stream(asset) if IS_SUBSECOND else realtime_stream(asset), ASYNC_LOOP)
                            await asyncio.sleep(0.05)
                        except Exception as e:
                            logmsg(f"[reconnect] failed to restart stream for {asset.symbol}: {e}")
            else:
                consecutive_failures += 1
        except Exception as e:
            logmsg(f"[reconnect] unexpected error: {e}")
            consecutive_failures += 1
        finally:
            RECONNECTING = False

def _make_progress_printer(symbol: str, start_ts: float, idx: int, total: int):
    display = pretty_asset_name(symbol)
    def on_progress(current, total, label=None, worker_label=None):
        total = total or FETCH_DURATION_SECONDS
        pct = min(current / total, 1.0) if total > 0 else 0
        bar_len = 20
        filled = int(bar_len * pct)
        bar = "#" * filled + "-" * (bar_len - filled)
        elapsed = time.time() - start_ts
        print(f"\r  {display:<25} [{bar}] {pct*100:4.1f}% {elapsed:>2.0f}s", end="", flush=True)
    return on_progress

async def fetch_candles_once(asset: Asset, idx=1, total=1):
    api_name = asset.api_symbol
    display_name = asset.symbol
    candles = []
    # Sub-minute timeframes: fetch period=1 (1s candles) then aggregate locally
    is_sub_minute = PERIOD_SECONDS < 60
    fetch_period = 1 if is_sub_minute else PERIOD_SECONDS
    if is_sub_minute:
        # Use get_candles (single request) — more reliable for period=1
        # Make staggered requests going backwards in time
        try:
            on_progress = _make_progress_printer(display_name, time.time(), idx, total)
            try: on_progress(FETCH_DURATION_SECONDS, FETCH_DURATION_SECONDS)
            except Exception: pass
            # الهدف: نحاول جلب ما يكفي لـ INITIAL_CANDLES شموع مجمّعة
            # INITIAL_CANDLES * PERIOD_SECONDS = عدد شموع 1s المطلوبة
            # هامش 1.5x (بدل 2x) لتقليل وقت الجلب وبالتالي تقليل الفجوة الزمنية
            # الفجوة الكبيرة = شموع مفقودة أكثر بين التاريخي والبث المباشر
            target_1s_count = int(INITIAL_CANDLES * PERIOD_SECONDS * 1.5)
            chunk_seconds = 500  # ~500 1s candles per request (server limit)
            all_candles_1s = []
            current_end = time.time()
            # زيادة max_chunks من 20 → 40 لضمان جلب كافٍ حتى للأصول البطيئة
            max_chunks = 40
            chunks_done = 0
            # تتبع الـ chunks الفارغة المتتالية (للإيقاف المبكر الذكي)
            empty_chunks_in_a_row = 0
            while len(all_candles_1s) < target_1s_count and chunks_done < max_chunks:
                chunk_end = current_end - (chunks_done * chunk_seconds)
                try:
                    # v13.1: عبر بوابة الجلب الواحدة — نفس الطلب نفسه بلا اختلاط
                    res_chunk = await asyncio.wait_for(
                        qx_fetch_window_raw(api_name, chunk_end, chunk_seconds, fetch_period,
                                            foreground=False, timeout=20, retries=0),
                        timeout=25,
                    )
                except Exception as e:
                    if chunks_done == 0:
                        logmsg(f"[fetch:{display_name}] get_candles(period=1) chunk {chunks_done+1} failed: {e}")
                    # retry once on transient error
                    if empty_chunks_in_a_row < 2:
                        empty_chunks_in_a_row += 1
                        await asyncio.sleep(0.2)
                        continue
                    break
                if not res_chunk or len(res_chunk) == 0:
                    empty_chunks_in_a_row += 1
                    # 3 chunks فارغة متتالية = نهاية التاريخ المتاح → توقف
                    if empty_chunks_in_a_row >= 3:
                        break
                    chunks_done += 1
                    continue
                # عتبة إيقاف أقل صرامة (من 50 → 10): بعض الأصول تُرجع 20-30 شمعة فقط في نهاية الأسبوع
                # هذا طبيعي ولا يعني أننا وصلنا لنهاية التاريخ
                if len(res_chunk) < 10 and chunks_done > 0:
                    all_candles_1s.extend(res_chunk)
                    break
                empty_chunks_in_a_row = 0
                all_candles_1s.extend(res_chunk)
                chunks_done += 1
                try:
                    pct = min(len(all_candles_1s) / target_1s_count, 1.0)
                    on_progress(pct * FETCH_DURATION_SECONDS, FETCH_DURATION_SECONDS)
                except Exception:
                    pass
                # delay صغير (0.03 بدل 0.05) لتسريع الجلب
                await asyncio.sleep(0.03)
            # De-duplicate by time
            seen_ts = set()
            unique_1s = []
            for c in all_candles_1s:
                if isinstance(c, dict):
                    ts = int(float(c.get('time', c.get('timestamp', 0))))
                    if ts not in seen_ts:
                        seen_ts.add(ts)
                        unique_1s.append(c)
            candles = unique_1s
            # No log message here — fetch_candles_with_retry prints the final count
        except Exception as e:
            print()
            logmsg(f"[fetch:{display_name}] get_candles(period=1) failed: {e}")
    else:
        # 60s+ timeframe — use parallel get_historical_candles
        if hasattr(CLIENT, 'get_historical_candles'):
            try:
                on_progress = _make_progress_printer(display_name, time.time(), idx, total)
                res = await asyncio.wait_for(
                    CLIENT.get_historical_candles(
                        api_name,
                        amount_of_seconds=FETCH_DURATION_SECONDS,
                        period=PERIOD_SECONDS,
                        max_workers=FETCH_MAX_WORKERS,
                        progress_callback=on_progress
                    ),
                    timeout=60,
                )
                if res and len(res) > 0: candles = res
            except Exception as e:
                print()
                logmsg(f"[fetch:{display_name}] get_historical_candles failed: {e}")
    if candles:
        formatted = []
        for c in candles:
            if not isinstance(c, dict): continue
            try:
                ts = int(float(c.get("time", c.get("timestamp", 0))))
                # Align to fetch_period (1s for sub-minute, PERIOD_SECONDS otherwise)
                aligned = _align_time(ts, period_seconds=fetch_period)
                o, h, l, cl = float(c.get("open", 0)), float(c.get("high", c.get("max", 0))), float(c.get("low", c.get("min", 0))), float(c.get("close", 0))
                if o > 0 and h > 0 and l > 0 and cl > 0:
                    formatted.append({'time': aligned, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': random.randint(50, 200)})
            except Exception: continue
        # Aggregate 1s candles into target subsecond timeframe
        if is_sub_minute and formatted:
            formatted = _aggregate_sub_minute(formatted, PERIOD_SECONDS)
        seen, unique = set(), []
        for c in formatted:
            if c['time'] not in seen:
                seen.add(c['time'])
                unique.append(c)
        unique.sort(key=lambda x: x['time'])
        return unique[-INITIAL_CANDLES:]
    return []


# ==============================================================================
# ===== BRIDGE FETCH HELPER (سد فجوة الشموع الأخيرة بين التاريخي والبث) =====
# ==============================================================================
# هذه الدالة المستقلة تُحاكي أسلوب كود 199 الشموع الذي يعمل بدون ثغرات:
#   1) طلب واحد (وليس متوازي) عبر CLIENT.get_candles
#   2) ينتهي عند time.time() الحالي (وليس T0 عند بداية الجلب التاريخي)
#   3) يستقبل آخر BRIDGE_FETCH_CANDLES شموع بما فيها الشمعة الحالية المتشكلة
#   4) يدمجها مع الشموع التاريخية (الشمعة الجسرية تستبدل التاريخية في نفس الفترة)
#
# الأمان:
#   - إذا فشلت لأي سبب، تُرجع existing_candles كما هي دون أي تغيير
#   - لا تُكسر أبداً سير عمل fetch_candles_with_retry
#   - تُحترم BRIDGE_FETCH_ENABLED=False (يمكن تعطيلها فوراً)
#   - تستخدم Semaphore لمنع إرهاق الخادم بطلبات متزامنة
# ==============================================================================
async def _bridge_fetch_recent_candles(asset: Asset, existing_candles: list) -> list:
    """جلب جسري لآخر BRIDGE_FETCH_CANDLES شمعة لسد فجوة 4-5 شموع.

    Args:
        asset: كائن Asset
        existing_candles: قائمة الشموع التاريخية المُجلبَة مسبقاً

    Returns:
        قائمة مدمجة (تاريخي + جسري) مرتبة ومُزالة التكرار، أو existing_candles
        كما هي عند فشل الجلب (الأمان: لا تُكسر العملية أبداً).
    """
    # ── فحوصات الأمان الأولية ─────────────────────────────────────────────
    if not BRIDGE_FETCH_ENABLED:
        return existing_candles
    if not existing_candles or len(existing_candles) == 0:
        return existing_candles
    if CLIENT is None or CLIENT.api is None:
        return existing_candles
    if not getattr(getattr(CLIENT, 'api', None), 'state', None):
        return existing_candles
    if not getattr(CLIENT.api.state, 'check_accepted_connection', False):
        return existing_candles

    # ── إنشاء Semaphore بأمان (lazy init على الـ loop الحالي) ──────────────
    global _BRIDGE_FETCH_SEMAPHORE
    if _BRIDGE_FETCH_SEMAPHORE is None:
        try:
            _BRIDGE_FETCH_SEMAPHORE = asyncio.Semaphore(BRIDGE_FETCH_SEMAPHORE_LIMIT)
        except RuntimeError:
            # الـ loop غير جاهز — تُرجع existing_candles دون كسر العمل
            return existing_candles

    try:
        async with _BRIDGE_FETCH_SEMAPHORE:
            is_sub_minute = PERIOD_SECONDS < 60
            # ✨ السر: استخدم time.time() الحالي (وليس T0 عند بداية الجلب التاريخي)
            bridge_end_time = int(time.time())
            bridge_candles = []

            if is_sub_minute:
                # ── للثواني الفرعية: جلب 1s ثم تجميع محلياً ──────────────────
                # هامش 5x لضمان تغطية كاملة للفجوة الزمنية الكبيرة المحتملة
                # (BRIDGE_FETCH_CANDLES=15 × PERIOD_SECONDS=5 × 5 = 375 ثانية من شموع 1s)
                # هذا يضمن أن الجسر يغطي 75 شمعة 5s — أكثر من كافٍ لأي فجوة
                bridge_1s_offset = BRIDGE_FETCH_CANDLES * PERIOD_SECONDS * 5
                try:
                    # v13.1: عبر بوابة الجلب الواحدة — نفس الطلب نفسه بلا اختلاط
                    bridge_1s = await asyncio.wait_for(
                        qx_fetch_window_raw(
                            asset.api_symbol,
                            bridge_end_time,
                            bridge_1s_offset,
                            1,  # period=1 (1s candles — مدعوم دائماً من الخادم)
                            foreground=False, timeout=BRIDGE_FETCH_TIMEOUT, retries=0,
                        ),
                        timeout=BRIDGE_FETCH_TIMEOUT + 5,
                    )
                except asyncio.TimeoutError:
                    logmsg(f"[bridge:{asset.symbol}] 1s fetch timeout (non-fatal)")
                    return existing_candles
                except Exception as e:
                    logmsg(f"[bridge:{asset.symbol}] 1s fetch failed (non-fatal): {e}")
                    return existing_candles

                if not bridge_1s:
                    return existing_candles

                # تنسيق شموع 1s
                bridge_formatted = []
                for c in bridge_1s:
                    if not isinstance(c, dict):
                        continue
                    try:
                        ts = int(float(c.get("time", c.get("timestamp", 0))))
                        aligned = _align_time(ts, period_seconds=1)
                        o = float(c.get("open", 0) or 0)
                        h = float(c.get("high", c.get("max", 0)) or 0)
                        l = float(c.get("low", c.get("min", 0)) or 0)
                        cl = float(c.get("close", c.get("c", 0)) or 0)
                        if o > 0 and h > 0 and l > 0 and cl > 0:
                            bridge_formatted.append({
                                'time': aligned, 'open': o, 'high': h,
                                'low': l, 'close': cl, 'volume': 1
                            })
                    except Exception:
                        continue

                # تجميع الـ 1s إلى الإطار الزمني المطلوب (5s/10s/15s/30s)
                bridge_candles = _aggregate_sub_minute(bridge_formatted, PERIOD_SECONDS)
            else:
                # ── لإطارات 60s+: استخدام _fetch_historical_batch مباشرة ──
                # لماذا؟ get_candles تُعيد subscribe للـ WebSocket مما يتعارض مع
                # realtime_stream الذي يعمل في الخلفية. _fetch_historical_batch
                # يستخدم event_name فريد (مع index) ولا يُعيد subscribe.
                # هذا يحل مشكلة "الفجوة عادت في M1+".
                bridge_offset = PERIOD_SECONDS * BRIDGE_FETCH_CANDLES
                # index فريد لتجنب التعارض مع get_historical_candles السابق
                _bridge_index = next(_request_counter)
                try:
                    bridge_raw = await asyncio.wait_for(
                        CLIENT._fetch_historical_batch(
                            asset.api_symbol,
                            bridge_end_time,
                            bridge_offset,
                            PERIOD_SECONDS,
                            _bridge_index,
                            BRIDGE_FETCH_TIMEOUT
                        ),
                        timeout=BRIDGE_FETCH_TIMEOUT + 5,  # هامش 5s إضافي
                    )
                except asyncio.TimeoutError:
                    logmsg(f"[bridge:{asset.symbol}] fetch timeout (non-fatal)")
                    return existing_candles
                except Exception as e:
                    logmsg(f"[bridge:{asset.symbol}] fetch failed (non-fatal): {e}")
                    return existing_candles

                if not bridge_raw:
                    return existing_candles

                # تحويل النتيجة عبر _parse_historical_candles (نفس آلية get_historical_candles)
                try:
                    bridge_parsed = CLIENT._parse_historical_candles(bridge_raw)
                except Exception:
                    bridge_parsed = []

                if not bridge_parsed:
                    return existing_candles

                # تنسيق شموع الجسر
                for c in bridge_parsed:
                    if not isinstance(c, dict):
                        continue
                    try:
                        ts = int(c.get("time", c.get("timestamp", 0)))
                        aligned = _align_time(ts, period_seconds=PERIOD_SECONDS)
                        o = float(c.get("open", 0) or 0)
                        h = float(c.get("high", 0) or 0)
                        l = float(c.get("low", 0) or 0)
                        cl = float(c.get("close", 0) or 0)
                        if o > 0 and h > 0 and l > 0 and cl > 0:
                            bridge_candles.append({
                                'time': aligned, 'open': o, 'high': h,
                                'low': l, 'close': cl, 'volume': 1
                            })
                    except Exception:
                        continue

            if not bridge_candles:
                return existing_candles

            # ── الدمج الآمن: الجسر يستبدل التاريخي في نفس الفترة الزمنية ───
            # (الشموع الجسرية أحدث وأدق، خاصة للشموع الأخيرة غير المكتملة)
            bridge_by_time = {c['time']: c for c in bridge_candles}
            merged_list = []
            for c in existing_candles:
                if c['time'] in bridge_by_time:
                    # استبدل الشمعة التاريخية بالجسرية الأحدث
                    merged_list.append(bridge_by_time.pop(c['time']))
                else:
                    merged_list.append(c)
            # أضف الشموع الجسرية المتبقية (جديدة، غير موجودة في التاريخي)
            merged_list.extend(bridge_by_time.values())

            # ── الترتيب وإزالة التكرار ─────────────────────────────────────
            seen = set()
            unique = []
            for c in sorted(merged_list, key=lambda x: x['time']):
                if c['time'] not in seen:
                    seen.add(c['time'])
                    unique.append(c)

            # قص إلى INITIAL_CANDLES (نفس سلوك الكود الأصلي)
            result = unique[-INITIAL_CANDLES:]

            # تسجيل بسيط (فقط إذا تم إضافة شموع جديدة فعلية)
            added = len(result) - len(existing_candles)
            if added > 0:
                logmsg(f"[bridge:{asset.symbol}] +{added} new candles bridged (total {len(result)})")

            return result

    except Exception as e:
        # ── الأمان النهائي: لا تُكسر الجلب التاريخي أبداً ──────────────────
        try:
            logmsg(f"[bridge:{asset.symbol}] bridge fetch error (non-fatal): {e}")
        except Exception:
            pass
        return existing_candles


async def fetch_candles_with_retry(asset: Asset, max_retries=3, idx=1, total=1):
    # For sub-minute, use lower threshold + 1 retry (server caps ~500-1000 1s candles)
    is_sub_minute = PERIOD_SECONDS < 60
    threshold = 20 if is_sub_minute else MIN_CANDLES_THRESHOLD
    max_retries = 1 if is_sub_minute else MAX_FETCH_RETRIES
    last_error = None
    for attempt in range(1, max_retries + 1):

        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            logmsg(f"[fetch_retry:{asset.symbol}] connection dead before attempt {attempt}; waiting for reconnect...")
            # (timeout 15s)
            try:
                await wait_until(
                    lambda: CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None,
                    timeout=15.0,
                    poll_interval=0.5,
                )
            except asyncio.TimeoutError:
                logmsg(f"[fetch_retry:{asset.symbol}] reconnect did not happen within 15s; giving up on this asset")
                return 0, attempt
        try:
            candles = await fetch_candles_once(asset, idx, total)
        except Exception as e:
            candles = []
            last_error = e
            logmsg(f"[fetch_retry:{asset.symbol}] attempt {attempt}/{max_retries} raised: {e}")
        # ===== BRIDGE FETCH: سد فجوة 4-5 شموع بين التاريخي والبث المباشر =====
        # استدعاء آمن: أي خطأ يُرجع candles كما هي دون كسر العملية.
        # يُجرّب آخر BRIDGE_FETCH_CANDLES شمعة تنتهي عند time.time() الحالي.
        if candles and len(candles) > 0:
            try:
                candles = await _bridge_fetch_recent_candles(asset, candles)
            except Exception as bridge_err:
                # الأمان التام: لا تُكسر الجلب التاريخي أبداً
                logmsg(f"[fetch_retry:{asset.symbol}] bridge skipped (non-fatal): {bridge_err}")
        if len(candles) >= threshold:
            # Merge historical candles with any live ticks collected during fetch
            # (realtime_stream may have appended live candles to asset.candles)
            live_candles = []
            if asset.candles:
                hist_times = set(c['time'] for c in candles)
                for c in asset.candles:
                    if c['time'] not in hist_times and c['time'] > (candles[-1]['time'] if candles else 0):
                        live_candles.append(c)
            asset.candles = candles + live_candles
            if asset.candles: asset.price = asset.candles[-1]['close']
            asset.write(force=True)
            # Update MT4_WRITER.sync_state with the full historical + live candles
            # so update_candle doesn't overwrite HST with only the few live candles
            MT4_WRITER.sync_state[asset.symbol] = {
                'period': PERIOD,
                'candles': list(asset.candles),
                'last_write': 0,
                'last_price': float(asset.candles[-1]['close']) if asset.candles else 0.0,
            }
            return len(asset.candles), attempt

        # Merge even for low counts
        live_candles = []
        if asset.candles:
            hist_times = set(c['time'] for c in candles)
            for c in asset.candles:
                if c['time'] not in hist_times and c['time'] > (candles[-1]['time'] if candles else 0):
                    live_candles.append(c)
        asset.candles = candles + live_candles
        if asset.candles: asset.price = asset.candles[-1]['close']
        asset.write(force=True)
        # Update sync_state even for low counts
        if asset.candles:
            MT4_WRITER.sync_state[asset.symbol] = {
                'period': PERIOD,
                'candles': list(asset.candles),
                'last_write': 0,
                'last_price': float(asset.candles[-1]['close']) if asset.candles else 0.0,
            }
        # ===== FIX 3: exponential backoff retries =====
        if attempt < max_retries:
            delay = min(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)), RETRY_BACKOFF_MAX)
            logmsg(f"[fetch_retry:{asset.symbol}] attempt {attempt}/{max_retries} got {len(candles)} candles; retry in {delay:.1f}s")
            await asyncio.sleep(delay)
    if last_error:
        logmsg(f"[fetch_retry:{asset.symbol}] all {max_retries} attempts failed. Last error: {last_error}")
    return len(candles), max_retries


# ==============================================================================
# SUBSECOND STREAM — separate system for 5s/10s/15s/30s timeframes
# Does NOT use fetch_candles_with_retry, MT4_WRITER.update_candle, or mt4_gap_filler.
# Aggregates realtime ticks into subsecond candles and writes HST directly.
# ==============================================================================

def _subsecond_align(ts: int) -> int:
    """Align timestamp to subsecond window boundary (with TZ offset for consistency)."""
    tz = _get_tz_offset()
    return ((int(ts) + tz) // SUBSECOND_SECONDS) * SUBSECOND_SECONDS

def _subsecond_write_hst(asset_symbol: str, candles: list):
    """Write subsecond HST file. Period field = 1 (MT4 minimum).
    Filename: {asset_symbol}1.hst (e.g., AUDUSD-5S-OTC1.hst)
    """
    if not candles:
        return
    file_name = f"{asset_symbol}1.hst"
    file_path = os.path.join(MT4_HISTORY_PATH, file_name)
    temp_path = file_path + '.tmp'
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass
    try:
        header = bytearray(148)
        struct.pack_into('<I', header, 0, 400)
        struct.pack_into('64s', header, 4, b'MetaQuotes Software Corp.'.ljust(64, b'\x00'))
        struct.pack_into('12s', header, 68, asset_symbol[:12].encode('ascii').ljust(12, b'\x00'))
        struct.pack_into('<I', header, 80, 1)  # period = 1 (M1, MT4 minimum)
        first_price = candles[0]['close'] if candles else 0.0
        digits = _resolve_digits(asset_symbol, first_price)
        struct.pack_into('<I', header, 84, digits)
        struct.pack_into('<I', header, 88, 0)
        struct.pack_into('<I', header, 92, 0)
        body_size = len(candles) * 44
        buffer = bytearray(148 + body_size)
        buffer[:148] = header
        offset = 148
        for c in candles:
            struct.pack_into('<I', buffer, offset, int(c['time']))
            struct.pack_into('<d', buffer, offset + 4, float(c['open']))
            struct.pack_into('<d', buffer, offset + 12, float(c['low']))
            struct.pack_into('<d', buffer, offset + 20, float(c['high']))
            struct.pack_into('<d', buffer, offset + 28, float(c['close']))
            struct.pack_into('<Q', buffer, offset + 36, int(c.get('volume', 0)))
            offset += 44
        with open(temp_path, 'wb') as f:
            f.write(buffer)
        # atomic replace with retry
        replaced = False
        for attempt in range(5):
            try:
                os.replace(temp_path, file_path)
                replaced = True
                break
            except (PermissionError, OSError):
                time.sleep(0.05)
                continue
        if not replaced:
            try:
                with open(file_path, 'wb') as f:
                    f.write(buffer)
            except Exception:
                pass
    except Exception:
        pass
    finally:
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception: pass

async def fetch_subsecond_history(
    asset: Asset,
    idx: int = 1,
    total: int = 1,
    subsecond_seconds: int = None,
    target_candles: int = None,
    label: str = None,
):
    """Fetch historical subsecond candles by fetching 1s candles and aggregating.

    Strategy (per Quotex server limitations):
    1. Use `get_candles` (single request, NOT parallel get_historical_candles)
       with period=1 -- server returns ~500 1s candles per request
    2. Make multiple staggered requests going backwards in time
    3. Stop when server returns 3 empty chunks in a row (hit history limit)
    4. Aggregate 1s candles locally into 5s/10s/15s/30s

    v8.4: added optional parameters subsecond_seconds/target_candles/label.
    They fall back to SUBSECOND_SECONDS / SUBSECOND_HISTORY_CANDLES / SUBSECOND_LABEL
    when None. This lets M1 mode call us with subsecond_seconds=5 even when
    IS_SUBSECOND is False.

    Uses a semaphore (3 concurrent) to avoid overwhelming server.
    """
    if CLIENT is None or not hasattr(CLIENT, 'get_candles'):
        logmsg(f"[subfetch:{asset.symbol}] CLIENT not ready")
        return []
    api_name = asset.api_symbol
    display_name = asset.symbol
    # v8.4: resolve optional parameters -- fall back to globals if not provided
    _sec = subsecond_seconds if subsecond_seconds is not None else SUBSECOND_SECONDS
    _target = target_candles if target_candles is not None else SUBSECOND_HISTORY_CANDLES
    _label = label if label is not None else (SUBSECOND_LABEL or f"{_sec}S")
    if _sec is None or _sec <= 0:
        logmsg(f"[subfetch:{display_name}] invalid subsecond_seconds={_sec}")
        return []
    # Target: target_candles aggregated candles
    # = target_candles * subsecond_seconds 1s candles (with SUBSECOND_FETCH_MARGIN margin)
    # v8.3: use SUBSECOND_FETCH_MARGIN (1.3x) -- was hardcoded 1.5x in v8.0, 2.0x in v8.1
    target_1s_count = int(_target * _sec * SUBSECOND_FETCH_MARGIN)
    chunk_seconds = 500  # ~500 1s candles per request (server limit)
    all_candles_1s = []
    current_end = time.time()
    # v8.3: use SUBSECOND_MAX_CHUNKS (5) -- was 40 in v8.0, 60 in v8.1, now 5
    max_chunks = SUBSECOND_MAX_CHUNKS
    chunks_done = 0
    empty_chunks_in_a_row = 0
    # Semaphore (3 concurrent fetches, not 41) — created lazily on the running loop
    global _SUBSECOND_FETCH_SEMAPHORE
    if _SUBSECOND_FETCH_SEMAPHORE is None:
        _SUBSECOND_FETCH_SEMAPHORE = asyncio.Semaphore(3)
    async with _SUBSECOND_FETCH_SEMAPHORE:
        logmsg(f"[subfetch:{display_name}] start: get_candles(period=1), target ~{target_1s_count} 1s candles")
        try:
            while len(all_candles_1s) < target_1s_count and chunks_done < max_chunks:
                if not CLIENT or not CLIENT.api or not getattr(CLIENT.api.state, 'check_accepted_connection', False):
                    logmsg(f"[subfetch:{display_name}] connection lost during fetch")
                    break
                chunk_end = current_end - (chunks_done * chunk_seconds)
                try:
                    res_chunk = await asyncio.wait_for(
                        CLIENT.get_candles(api_name, chunk_end, chunk_seconds, 1),
                        timeout=20,
                    )
                except Exception as e:
                    if chunks_done == 0:
                        logmsg(f"[subfetch:{display_name}] get_candles(period=1) chunk {chunks_done+1} failed: {e}")
                    # retry on transient error
                    if empty_chunks_in_a_row < 2:
                        empty_chunks_in_a_row += 1
                        await asyncio.sleep(0.2)
                        continue
                    break
                if not res_chunk or len(res_chunk) == 0:
                    empty_chunks_in_a_row += 1
                    # 3 chunks فارغة متتالية = نهاية التاريخ المتاح
                    if empty_chunks_in_a_row >= 3:
                        break
                    chunks_done += 1
                    continue
                # عتبة إيقاف أقل صرامة (من 50 → 10)
                if len(res_chunk) < 10 and chunks_done > 0:
                    all_candles_1s.extend(res_chunk)
                    break
                empty_chunks_in_a_row = 0
                all_candles_1s.extend(res_chunk)
                chunks_done += 1
                # v8.3: bigger inter-chunk delay (0.03 -> 0.15s) -- the server was
                # throttling us after a few assets because we hammered it at 30 req/s.
                await asyncio.sleep(0.15)
                # v8.3/v8.6: user explicitly asked: if we already have enough 1s
                # candles to cover >=425 seconds of data (the original "85 5s
                # candles" threshold = 425 seconds), stop fetching more chunks.
                # v8.6: made TIME-BASED so the threshold scales correctly for any
                # _sec value. For 5s mode: 425s/5 = 85 (matches the original
                # SUBSECOND_EARLY_EXIT_CANDLES). For 1s mode: 425s/1 = 425
                # 1s candles, which is the right scale (1 chunk yields ~700 1s
                # candles = ~12 1m candles, plenty for the M1 bridge).
                _projected = len(all_candles_1s) // max(1, _sec)
                _time_based_threshold = max(1, 425 // max(1, _sec))
                if chunks_done >= 1 and _projected >= _time_based_threshold:
                    logmsg(
                        f"[subfetch:{display_name}] early-exit: {_projected} projected {_label} candles "
                        f">= {_time_based_threshold} threshold ({425}s of data); stopping chunk requests"
                    )
                    break
        except Exception as e:
            logmsg(f"[subfetch:{display_name}] FAILED: {e}")
            return []
    # De-duplicate by time (chunks may overlap)
    seen_ts = set()
    unique_1s = []
    for c in all_candles_1s:
        if isinstance(c, dict):
            ts = int(float(c.get('time', c.get('timestamp', 0))))
            if ts not in seen_ts:
                seen_ts.add(ts)
                unique_1s.append(c)
    logmsg(f"[subfetch:{display_name}] got {len(unique_1s)} 1s candles from {chunks_done} chunks, aggregating to {_label}")
    # Format 1s candles with TZ offset
    formatted_1s = []
    for c in unique_1s:
        try:
            ts = int(float(c.get("time", c.get("timestamp", 0))))
            tz = _get_tz_offset()
            aligned = ((ts + tz) // 1) * 1  # align to 1s boundary with TZ
            o = float(c.get("open", 0) or 0)
            h = float(c.get("high", c.get("max", 0)) or 0)
            l = float(c.get("low", c.get("min", 0)) or 0)
            cl = float(c.get("close", 0) or 0)
            v = int(c.get("volume", c.get("vol", 0)) or 0)
            if o > 0 and h > 0 and l > 0 and cl > 0:
                formatted_1s.append({
                    'time': aligned, 'open': o, 'high': h, 'low': l,
                    'close': cl, 'volume': v
                })
        except Exception:
            continue
    formatted_1s.sort(key=lambda x: x['time'])
    # v8.4: aggregate into the resolved _sec (not SUBSECOND_SECONDS global) and
    # limit to the resolved _target (not SUBSECOND_HISTORY_CANDLES global).
    aggregated = _aggregate_sub_minute(formatted_1s, _sec)
    result = aggregated[-_target:]
    logmsg(f"[subfetch:{display_name}] DONE: {len(unique_1s)} 1s -> {len(result)} {_label} candles")
    # v8.1: explicit verification -- warn if below the requested 500 target
    if len(result) < SUBSECOND_HISTORY_CANDLES:
        logmsg(
            f"[subfetch:{display_name}] WARNING: only {len(result)} {SUBSECOND_LABEL} candles "
            f"(target={SUBSECOND_HISTORY_CANDLES}). Server history may be limited for this asset."
        )
    return result


async def fetch_1s_and_aggregate_to_1m(asset: Asset, idx: int = 1, total: int = 1) -> list:
    """v8.6: Fetch 1-second candles and aggregate them to 1-minute candles.

    This is used as the most granular bridge for M1 mode -- the resulting 1m candles
    fill the gap between the historical 1m fetch's last candle and the live stream's
    current candle. Because each 1m candle is built from 60 consecutive 1s candles,
    there are NO gaps in the aggregated 1m candle (assuming the server's 1s data is
    continuous, which it is for popular OTC pairs).

    Args:
        asset: the Asset to fetch 1s candles for
        idx, total: progress info for logging

    Returns:
        (candles_1m, n_1s) -- the aggregated 1m candles and the raw 1s source count
    """
    # v8.5: return (candles_1m, n_1s) tuple so the caller can print the 1s
    # source count in the console before the historical fetch begins.
    if not M1_USE_1S_BRIDGE:
        return [], 0
    _fetch_start = time.time()
    try:
        candles_1s = await asyncio.wait_for(
            fetch_subsecond_history(
                asset,
                idx=idx,
                total=total,
                subsecond_seconds=1,
                target_candles=M1_1S_BRIDGE_TARGET,
                label="1S",
            ),
            timeout=M1_BRIDGE_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logmsg(f"[1s_bridge:{asset.symbol}] 1s fetch timeout after {M1_BRIDGE_TIMEOUT}s")
        return [], 0
    except Exception as e:
        logmsg(f"[1s_bridge:{asset.symbol}] 1s fetch failed: {e}")
        return [], 0
    if not candles_1s:
        logmsg(f"[1s_bridge:{asset.symbol}] 1s returned 0 candles")
        return [], 0
    # Aggregate 1s -> 1m (every 60 consecutive 1s candles = 1 1m candle).
    # This is the most granular aggregation -- if the 1s data is continuous,
    # the resulting 1m candle has NO gaps (the user's explicit request).
    candles_1m = _aggregate_sub_minute(candles_1s, 60)
    _fetch_elapsed = time.time() - _fetch_start
    # v8.5/v8.6: print a clear console line showing the 1s fetch happened --
    # the user explicitly asked "must print the loading of those candles before
    # loading 1-minute candles". Use 'print' (not logmsg) so it shows on the
    # console, not just the verbose log. This print fires BEFORE the historical
    # 1m fetch begins.
    _display = pretty_asset_name(asset.symbol)
    print(
        f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{_display:<25}{Colors.RESET} "
        f"{Colors.DIM}fetched {len(candles_1s)} 1s candles in {_fetch_elapsed:.1f}s "
        f"-> {len(candles_1m)} 1m bridge{Colors.RESET}"
    )
    logmsg(
        f"[1s_bridge:{asset.symbol}] {len(candles_1s)} 1s -> {len(candles_1m)} 1m bridge candles"
    )
    return candles_1m, len(candles_1s)


async def subsecond_stream(asset: Asset):
    """Dedicated stream for subsecond timeframes (5s/10s/15s/30s).

    - Subscribes to realtime ticks (same WS subscription as normal)
    - Polls realtime_candles[asset] for tick data
    - Aggregates ticks into subsecond candle windows
    - Writes HST directly (bypasses MT4_WRITER.sync_state entirely)
    - Keeps last SUBSECOND_MAX_CANDLES (200) candles
    - NO gap filler, NO history fetch
    """
    internal = asset.api_symbol
    try:
        try:
            await wait_until(
                lambda: not (CONNECTION_ALIVE and CLIENT is None),
                timeout=10.0,
                poll_interval=0.2,
            )
        except asyncio.TimeoutError:
            pass
        if not CONNECTION_ALIVE or CLIENT is None:
            asset.streaming = False
            return
        # Subscribe to realtime 1-second ticks (period=1, always supported)
        # We aggregate locally into subsecond windows
        await CLIENT.start_candles_stream(internal, 1)
        await asyncio.sleep(0.5)
        asset.streaming = True
        asset.candles = []
        # Write empty HST immediately so MT4 can open the chart
        _subsecond_write_hst(asset.symbol, [{'time': _subsecond_align(int(time.time())), 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0}])
        last_write = time.time()
        # Fetch historical subsecond candles in the BACKGROUND using create_task
        # (run_coroutine_threadsafe doesn't work from inside the same loop)
        display_name = pretty_asset_name(internal)
        async def _background_history_fetch():
            try:
                historical = await asyncio.wait_for(fetch_subsecond_history(asset), timeout=60)
                if historical and len(historical) > 0:
                    # Merge: keep historical candles older than any tick-collected candles
                    if asset.candles:
                        oldest_tick_time = asset.candles[0]['time']
                        historical_to_keep = [c for c in historical if c['time'] < oldest_tick_time]
                        asset.candles = historical_to_keep + asset.candles
                    else:
                        asset.candles = historical
                    asset.candles = asset.candles[-SUBSECOND_MAX_CANDLES:]
                    if asset.candles and asset.price == 0:
                        asset.price = asset.candles[-1]['close']
                    # Write HST with merged data
                    _subsecond_write_hst(asset.symbol, asset.candles)
                    logmsg(f"[substream:{internal}] {len(historical)} history candles loaded + ticks active")
                else:
                    logmsg(f"[substream:{internal}] no history (ticks only)")
            except asyncio.TimeoutError:
                logmsg(f"[substream:{internal}] history fetch timeout (ticks only)")
            except Exception as e:
                logmsg(f"[substream:{internal}] background history fetch failed: {e}")
        # Schedule on the same loop — keep a strong reference to avoid GC
        _task = asyncio.create_task(_background_history_fetch())
        # Store on asset to prevent garbage collection
        if not hasattr(asset, '_bg_tasks'):
            asset._bg_tasks = set()
        asset._bg_tasks.add(_task)
        _task.add_done_callback(asset._bg_tasks.discard)
    except Exception as e:
        logmsg(f"[substream:{internal}] failed to start: {e}")
        asset.streaming = False
        return
    consecutive_errors = 0
    while CONNECTION_ALIVE:
        try:
            if CLIENT is None or not getattr(getattr(CLIENT, 'api', None), 'state', None) or getattr(CLIENT.api.state, 'status', None) != 1:
                await asyncio.sleep(0.2)
                continue
            candle = None
            if hasattr(CLIENT, 'api') and CLIENT.api:
                candle = CLIENT.api.realtime_candles.get(internal)
            if candle:
                consecutive_errors = 0
                if isinstance(candle, list) and len(candle) >= 3:
                    ts, price = int(candle[1]), float(candle[2])
                elif isinstance(candle, dict):
                    ts = int(candle.get("time", candle.get("timestamp", time.time())))
                    price = float(candle.get("price", candle.get("close", 0)))
                else:
                    await asyncio.sleep(STREAM_POLL_INTERVAL)
                    continue
                if price > 0 and ts > 0:
                    # Align to subsecond window
                    window_start = _subsecond_align(ts)
                    if asset.candles:
                        last_candle = asset.candles[-1]
                        if window_start < last_candle['time']:
                            # stale tick — ignore
                            pass
                        elif window_start == last_candle['time']:
                            # update current candle
                            last_candle['high'] = max(last_candle['high'], price)
                            last_candle['low'] = min(last_candle['low'], price)
                            last_candle['close'] = price
                            last_candle['volume'] += 1
                        else:
                            # new window — append
                            asset.candles.append({
                                'time': window_start, 'open': price, 'high': price,
                                'low': price, 'close': price, 'volume': 1
                            })
                    else:
                        asset.candles.append({
                            'time': window_start, 'open': price, 'high': price,
                            'low': price, 'close': price, 'volume': 1
                        })
                    # keep last SUBSECOND_MAX_CANDLES
                    if len(asset.candles) > SUBSECOND_MAX_CANDLES:
                        asset.candles = asset.candles[-SUBSECOND_MAX_CANDLES:]
                    # update price display
                    if asset.price != price:
                        asset.previous_price = asset.price
                    asset.price = price
                    asset.updates += 1
                    asset.last_update_time = time.time()
                    # write HST every 0.5s
                    now = time.time()
                    if now - last_write > 0.5:
                        _subsecond_write_hst(asset.symbol, asset.candles)
                        last_write = now
            await asyncio.sleep(STREAM_POLL_INTERVAL)
        except asyncio.CancelledError:
            asset.streaming = False
            raise
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            consecutive_errors += 1
            if consecutive_errors >= 10:
                logmsg(f"[substream:{internal}] too many consecutive errors, stopping")
                asset.streaming = False
                return
            await asyncio.sleep(0.2)
    asset.streaming = False


async def realtime_stream(asset: Asset):
    internal = asset.api_symbol
    try:
        # ===== EVENT-DRIVEN FIX =====
        # :
        # while CONNECTION_ALIVE and CLIENT is None: await asyncio.sleep(0.5)
        # timeout 200ms .
        try:
            await wait_until(
                lambda: not (CONNECTION_ALIVE and CLIENT is None),
                timeout=10.0,
                poll_interval=0.2,
            )
        except asyncio.TimeoutError:
            pass
        if not CONNECTION_ALIVE or CLIENT is None:
            asset.streaming = False
            return
        # For sub-minute timeframes, subscribe to period=1 (1s candles, always supported)
        # _align_time then buckets ticks into PERIOD_SECONDS (5s, 10s, 15s, 30s)
        #
        # v8.10: when M1_USE_1S_BRIDGE is True (which includes both TEST MODE
        # and the full flow), FORCE stream_period=1 even though PERIOD_SECONDS
        # == 60. This subscribes to 1s ticks (NOT 1m snapshots), so the server
        # doesn't send the 199-candle initial 1m burst. The 1s ticks are
        # bucketed into 1m candles by update_candle via _align_time, updating
        # the last candle for live price every second.
        if PERIOD_SECONDS == 60 and M1_USE_1S_BRIDGE:
            stream_period = 1  # 1s ticks, aggregate to 1m locally
        else:
            stream_period = 1 if PERIOD_SECONDS < 60 else PERIOD_SECONDS
        await CLIENT.start_candles_stream(internal, stream_period)
        await asyncio.sleep(0.3)  # reduced from 1.5s to minimize gap with historical fetch
        asset.streaming = True
        # ===== FIX 12: MT4_WRITER.sync_state 1000 =====
        # : MT4_WRITER.update_candle sync_state
        # => ~19 (1KB) 1000 (44KB)
        # : asset.candles (1000 ) sync_state[derived_symbol]
        # realtime_stream update_candle
        # sync_state 1000 .
        if asset.candles and asset.symbol not in MT4_WRITER.sync_state:
            MT4_WRITER.sync_state[asset.symbol] = {
                'period': PERIOD,
                'candles': list(asset.candles),  # 1000
                'last_write': 0,
                'last_price': float(asset.candles[-1]['close']) if asset.candles else 0.0,
            }
    except Exception as e:
        logmsg(f"[stream:{internal}] failed to start stream: {e}")
        asset.streaming = False
        return
    consecutive_errors = 0
    while CONNECTION_ALIVE:
        try:
            if CLIENT is None or not getattr(getattr(CLIENT, 'api', None), 'state', None) or getattr(CLIENT.api.state, 'status', None) != 1:
                # ===== EVENT-DRIVEN FIX =====
                # await asyncio.sleep(1) — polling (200ms)
                await asyncio.sleep(0.2)
                continue
            candle = None
            if not candle and hasattr(CLIENT, 'api') and CLIENT.api:
                candle = CLIENT.api.realtime_candles.get(internal)
            if candle:
                consecutive_errors = 0
                if isinstance(candle, list) and len(candle) >= 3:
                    ts, price = int(candle[1]), float(candle[2])
                elif isinstance(candle, dict):
                    ts = int(candle.get("time", candle.get("timestamp", time.time())))
                    price = float(candle.get("price", candle.get("close", 0)))
                else:
                    await asyncio.sleep(STREAM_POLL_INTERVAL)
                    continue
                if price > 0 and ts > 0:
                    # ===== FIX 10: MT4_WRITER.update_candle asset.mark_dirty =====
                    # HST MT4Writer.write_to_file ( )
                    # MT4_WRITER.update_candle sync_state[derived_symbol] + HST 200ms
                    try:
                        MT4_WRITER.update_candle(asset.symbol, PERIOD, {'time': ts, 'price': price})
                    except Exception:
                        pass
                    # asset.candles ( )
                    # FIX L5: _align_time ( tz_offset) asset.candles
                    # sync_state HST. (ts // 60 * 60)
                    # tz_offset => 1+ HST.
                    aligned_time = _align_time(ts)
                    # FIX STALE-CANDLE v2: same logic as update_candle
                    _is_new_candle = False
                    if asset.candles:
                        last_candle = asset.candles[-1]
                        if aligned_time < last_candle['time']:
                            pass  # tick for closed minute - ignore
                        elif last_candle['time'] == aligned_time:
                            last_candle['high'] = max(last_candle['high'], price)
                            last_candle['low'] = min(last_candle['low'], price)
                            last_candle['close'] = price
                        else:
                            # new candle - fill gap with flat candles first
                            _is_new_candle = True
                            period_secs = PERIOD_SECONDS if PERIOD_SECONDS > 0 else 60
                            gap = (aligned_time - last_candle['time']) // period_secs
                            if gap > 1:
                                last_close = last_candle['close']
                                fill_time = last_candle['time'] + period_secs
                                while fill_time < aligned_time:
                                    asset.candles.append({
                                        'time': fill_time,
                                        'open': last_close, 'high': last_close,
                                        'low': last_close, 'close': last_close, 'volume': 0,
                                    })
                                    fill_time += period_secs
                            asset.candles.append({'time': aligned_time, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': 1})
                    else:
                        _is_new_candle = True
                        asset.candles.append({'time': aligned_time, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': 1})
                    # v13: الحد رُفع من 1000 إلى ASSET_MAX_CANDLES (3000) حتى تتراكم
                    # دفعات التمرير للخلف (fetch_older_batch) مثل المنصات الاحترافية.
                    if len(asset.candles) > ASSET_MAX_CANDLES: asset.candles = asset.candles[-ASSET_MAX_CANDLES:]
                    # FIX G: ( )
                    if asset.price != price:
                        asset.previous_price = asset.price
                    asset.price = price
                    asset.updates += 1
                    asset.last_update_time = time.time()
                    # asset.mark_dirty() — MT4_WRITER.update_candle
            await asyncio.sleep(STREAM_POLL_INTERVAL)
        except asyncio.CancelledError:
            asset.streaming = False
            raise
        except asyncio.TimeoutError: continue
        except Exception as e:
            consecutive_errors += 1
            if consecutive_errors >= 10:
                logmsg(f"[stream:{internal}] too many consecutive errors, stopping stream")
                asset.streaming = False
                return
            # ===== EVENT-DRIVEN FIX =====
            # await asyncio.sleep(1) — polling (200ms)
            await asyncio.sleep(0.2)
    asset.streaming = False


# ===== FIX B: (> ) =====
# : " ".
# auto_reconnect
# LONG_DISCONNECT_THRESHOLD. 1000
# HST streams —
# .
async def refetch_all_candles():
    """ .

 :
 1. streams caches 
 2. sync_state MT4_WRITER ( HST)
 3. fetch_candles_with_retry ( 1000 )
 4. realtime_stream 
 5. mt4_gap_filler 
 """
    if not ALL_STREAMING_ASSETS:
        logmsg("[refetch_all] no assets to re-fetch")
        return
    print(f"\n{Colors.CYAN}{'═'*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  FULL RE-FETCH: long disconnect detected — refreshing all candles{Colors.RESET}")
    print(f"  • Assets: {len(ALL_STREAMING_ASSETS)}")
    print(f"  • Target per asset: {INITIAL_CANDLES} candles")
    print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")
    # 1) streams
    for asset in ALL_STREAMING_ASSETS:
        try:
            if asset.stream_task and not asset.stream_task.done():
                asset.stream_task.cancel()
        except Exception:
            pass
        asset.streaming = False
        asset.stream_task = None
        asset.candles = []
        asset.last_saved_close = 0.0
        asset.last_saved_candle_time = 0
        asset.last_saved_candle_count = 0
        asset.dirty = True
        asset._gap_filled = False
        asset.updates = 0
        asset.last_update_time = 0
        # sync_state MT4_WRITER
        if asset.symbol in MT4_WRITER.sync_state:
            try: del MT4_WRITER.sync_state[asset.symbol]
            except Exception: pass
        if asset.symbol in MT4_WRITER._gap_filled:
            MT4_WRITER._gap_filled[asset.symbol] = False
        # Clear the SQLite-side gap_state flag too so fill_gap_once will run
        # again for this asset after the full re-fetch.
        try:
            MT4_WRITER.candle_store.clear_symbol(asset.symbol)
        except Exception:
            pass
    # 2)
    total_loaded = 0
    total_assets = len(ALL_STREAMING_ASSETS)
    consecutive_disconnects = 0
    for idx, asset in enumerate(ALL_STREAMING_ASSETS, 1):

        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            logmsg(f"[refetch_all] connection lost again at asset {idx}/{total_assets}; aborting re-fetch")
            break
        display = pretty_asset_name(asset.api_symbol)
        start_time = time.time()
        if IS_SUBSECOND:
            # Subsecond mode: no history to re-fetch, just restart stream
            print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.CYAN}subsecond — no history to refetch{Colors.RESET}")
        else:
            try:
                candles_count, attempts = await fetch_candles_with_retry(
                    asset, max_retries=MAX_FETCH_RETRIES, idx=idx, total=total_assets
                )
                elapsed = time.time() - start_time
                if candles_count >= MIN_CANDLES_THRESHOLD:
                    total_loaded += candles_count
                    consecutive_disconnects = 0
                    attempts_str = "" if attempts == 1 else f" ({attempts} attempts)"
                    print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.GREEN}{candles_count} candles in {elapsed:.1f}s{attempts_str}{Colors.RESET}")
                else:
                    print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.RED}Only {candles_count} candles{Colors.RESET}")
            except Exception as e:
                print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.RED}Error: {str(e)[:30]}{Colors.RESET}")
                if "Connection" in str(e) or "closed" in str(e).lower():
                    consecutive_disconnects += 1
                    if consecutive_disconnects >= MAX_RECONNECTS_DURING_FETCH:
                        logmsg(f"[refetch_all] too many disconnects ({consecutive_disconnects}); aborting")
                        break
        # 3) restart stream
        try:
            asset.stream_task = asyncio.run_coroutine_threadsafe(subsecond_stream(asset) if IS_SUBSECOND else realtime_stream(asset), ASYNC_LOOP)
        except Exception as e:
            logmsg(f"[refetch_all] failed to restart stream for {asset.symbol}: {e}")
        await asyncio.sleep(FETCH_ASSET_DELAY)
    # 4)
    if CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None:
        try:
            asyncio.run_coroutine_threadsafe(mt4_gap_filler(), ASYNC_LOOP)
        except Exception as e:
            logmsg(f"[refetch_all] failed to schedule gap filler: {e}")
    print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")
    print(f"{Colors.GREEN}  Full re-fetch complete: {total_loaded} candles across {total_assets} assets{Colors.RESET}")
    print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}\n")

# ==============================================================================
# SECTION 9: MT4 SYNC ENGINE ( — )
# ==============================================================================

# ------------------------------------------------------------------------------
# CandleStore: SQLite-backed persistent candle storage.
# ------------------------------------------------------------------------------
# Why SQLite instead of JSON files:
#   - JSON is slow: full file rewrite on every save, full file load on every
#     read, no indexing. For ~1000 candles per asset across many assets this
#     wastes I/O and risks corruption if the process is killed mid-write.
#   - SQLite is transactional, atomic, indexed by (symbol, time), and
#     supports efficient range queries ("give me all candles for symbol X
#     from time A to time B") without loading the whole table into memory.
#   - Concurrent reads + a single writer are safe out of the box.
#
# Schema:
#   candles(symbol TEXT, time INTEGER, open REAL, high REAL, low REAL,
#           close REAL, volume INTEGER, PRIMARY KEY(symbol, time))
#   gap_state(symbol TEXT PRIMARY KEY, filled INTEGER, last_fill_at REAL)
#       - 'filled' is 0/1 and tracks whether fill_gap_once has already
#         succeeded for this asset. Once it is 1, MT4Writer.fill_gap_once
#         stops touching closed candles for this asset entirely.
# ------------------------------------------------------------------------------
import sqlite3 as _sqlite3
import threading as _threading

class CandleStore:
    """Thread-safe SQLite-backed candle persistence layer.

    All public methods are safe to call from any thread. A single write
    connection (guarded by a lock) serializes writes; reads use a short-lived
    read-only connection per call.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._write_lock = _threading.Lock()
        self._write_conn: Optional[_sqlite3.Connection] = None
        # Make sure parent dir exists
        try:
            parent = os.path.dirname(db_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
        except Exception as e:
            pass  # silenced - non-essential diagnostic
        # Init schema on a short-lived connection
        self._init_schema()

    def _init_schema(self):
        try:
            conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            try:
                conn.execute("PRAGMA journal_mode=WAL;")    # crash-safe, fast writes
                conn.execute("PRAGMA synchronous=NORMAL;")  # safe + fast
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS candles (
                        symbol TEXT NOT NULL,
                        time   INTEGER NOT NULL,
                        open   REAL NOT NULL,
                        high   REAL NOT NULL,
                        low    REAL NOT NULL,
                        close  REAL NOT NULL,
                        volume INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (symbol, time)
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_candles_symbol_time
                    ON candles(symbol, time)
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS gap_state (
                        symbol        TEXT PRIMARY KEY,
                        filled        INTEGER NOT NULL DEFAULT 0,
                        last_fill_at  REAL NOT NULL DEFAULT 0
                    )
                """)
            finally:
                conn.close()
        except Exception as e:
            pass  # silenced - non-essential diagnostic

    # ------------------------------------------------------------------ writes
    def _get_write_conn(self) -> _sqlite3.Connection:
        if self._write_conn is None:
            self._write_conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            self._write_conn.execute("PRAGMA journal_mode=WAL;")
            self._write_conn.execute("PRAGMA synchronous=NORMAL;")
        return self._write_conn

    def upsert_candles(self, symbol: str, candles: list) -> int:
        """Insert-or-replace a batch of candles for the given symbol.
        Returns the number of rows written."""
        if not candles:
            return 0
        with self._write_lock:
            conn = self._get_write_conn()
            rows = 0
            try:
                conn.execute("BEGIN IMMEDIATE;")
                for c in candles:
                    conn.execute(
                        "INSERT OR REPLACE INTO candles(symbol, time, open, high, low, close, volume) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);",
                        (symbol, int(c['time']), float(c['open']), float(c['high']),
                         float(c['low']), float(c['close']), int(c.get('volume', 0)))
                    )
                    rows += 1
                conn.execute("COMMIT;")
            except Exception:
                try: conn.execute("ROLLBACK;")
                except Exception: pass
                pass  # silenced - non-essential diagnostic
                return 0
            return rows

    def append_new_candles(self, symbol: str, candles: list, after_time: int = 0) -> int:
        """Append candles whose time > after_time. Existing candles with time
        <= after_time are left untouched (frozen). Returns number of rows
        actually inserted (not the number replaced)."""
        if not candles:
            return 0
        with self._write_lock:
            conn = self._get_write_conn()
            inserted = 0
            try:
                conn.execute("BEGIN IMMEDIATE;")
                for c in candles:
                    t = int(c['time'])
                    if t <= after_time:
                        continue    # frozen - skip
                    cur = conn.execute(
                        "INSERT OR IGNORE INTO candles(symbol, time, open, high, low, close, volume) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?);",
                        (symbol, t, float(c['open']), float(c['high']),
                         float(c['low']), float(c['close']), int(c.get('volume', 0)))
                    )
                    if cur.rowcount > 0:
                        inserted += 1
                conn.execute("COMMIT;")
            except Exception:
                try: conn.execute("ROLLBACK;")
                except Exception: pass
                pass  # silenced - non-essential diagnostic
                return 0
            return inserted

    def set_gap_filled(self, symbol: str, filled: bool = True, at_ts: float = None):
        if at_ts is None:
            at_ts = time.time()
        with self._write_lock:
            conn = self._get_write_conn()
            try:
                conn.execute("BEGIN IMMEDIATE;")
                conn.execute(
                    "INSERT INTO gap_state(symbol, filled, last_fill_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(symbol) DO UPDATE SET filled=excluded.filled, last_fill_at=excluded.last_fill_at;",
                    (symbol, 1 if filled else 0, float(at_ts))
                )
                conn.execute("COMMIT;")
            except Exception:
                try: conn.execute("ROLLBACK;")
                except Exception: pass

    def is_gap_filled(self, symbol: str) -> Tuple[bool, float]:
        """Returns (filled, last_fill_at)."""
        try:
            conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            try:
                cur = conn.execute(
                    "SELECT filled, last_fill_at FROM gap_state WHERE symbol=?;",
                    (symbol,)
                )
                row = cur.fetchone()
                if row is None:
                    return (False, 0.0)
                return (bool(row[0]), float(row[1]))
            finally:
                conn.close()
        except Exception as e:
            pass  # silenced - non-essential diagnostic
            return (False, 0.0)

    # ------------------------------------------------------------------- reads
    def get_candles(self, symbol: str, limit: Optional[int] = None) -> list:
        """Return all candles for the symbol, sorted by time ascending.
        If limit is given, return only the last `limit` candles."""
        try:
            conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            try:
                if limit is None:
                    cur = conn.execute(
                        "SELECT time, open, high, low, close, volume FROM candles "
                        "WHERE symbol=? ORDER BY time ASC;",
                        (symbol,)
                    )
                else:
                    # Use a subselect to get the last N rows by time, then sort ascending.
                    cur = conn.execute(
                        "SELECT time, open, high, low, close, volume FROM candles "
                        "WHERE symbol=? ORDER BY time DESC LIMIT ?;",
                        (symbol, int(limit))
                    )
                    rows = cur.fetchall()
                    rows.reverse()
                    return [{
                        'time': r[0], 'open': r[1], 'high': r[2],
                        'low': r[3], 'close': r[4], 'volume': r[5]
                    } for r in rows]
                rows = cur.fetchall()
                return [{
                    'time': r[0], 'open': r[1], 'high': r[2],
                    'low': r[3], 'close': r[4], 'volume': r[5]
                } for r in rows]
            finally:
                conn.close()
        except Exception as e:
            pass  # silenced - non-essential diagnostic
            return []

    def get_max_time(self, symbol: str) -> int:
        """Return the largest candle timestamp stored for the symbol, or 0."""
        try:
            conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            try:
                cur = conn.execute(
                    "SELECT MAX(time) FROM candles WHERE symbol=?;",
                    (symbol,)
                )
                row = cur.fetchone()
                return int(row[0]) if row and row[0] is not None else 0
            finally:
                conn.close()
        except Exception as e:
            pass  # silenced - non-essential diagnostic
            return 0

    def count(self, symbol: str) -> int:
        try:
            conn = _sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
            try:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM candles WHERE symbol=?;",
                    (symbol,)
                )
                row = cur.fetchone()
                return int(row[0]) if row else 0
            finally:
                conn.close()
        except Exception as e:
            pass  # silenced - non-essential diagnostic
            return 0

    def clear_symbol(self, symbol: str) -> int:
        """Delete all candles + gap_state for a symbol (used by full re-fetch)."""
        with self._write_lock:
            conn = self._get_write_conn()
            try:
                conn.execute("BEGIN IMMEDIATE;")
                cur = conn.execute("DELETE FROM candles WHERE symbol=?;", (symbol,))
                deleted = cur.rowcount
                conn.execute("DELETE FROM gap_state WHERE symbol=?;", (symbol,))
                conn.execute("COMMIT;")
                return deleted
            except Exception:
                try: conn.execute("ROLLBACK;")
                except Exception: pass
                return 0


# Module-level singleton (created lazily so the path can be picked once
# after APPDATA is available at runtime).
_CANDLE_STORE: Optional[CandleStore] = None
_CANDLE_STORE_LOCK = _threading.Lock()

def get_candle_store() -> CandleStore:
    """Lazy-init the global CandleStore.

    The DB lives NEXT TO THE SCRIPT / EXE (not in APPDATA) so it is easy to
    bundle with a PyInstaller exe and easy for the user to find / back up.
    - When run as a script: candles.db is created in the script's directory.
    - When frozen with PyInstaller (one-file): candles.db is created in the
      directory the exe runs from (sys.executable's parent).
    """
    global _CANDLE_STORE
    if _CANDLE_STORE is not None:
        return _CANDLE_STORE
    with _CANDLE_STORE_LOCK:
        if _CANDLE_STORE is None:
            # Resolve the directory the script / exe lives in.
            # When frozen with PyInstaller, sys.executable points to the exe
            # and we want the DB next to it (not inside the temp _MEIPASS dir).
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, 'candles.db')
            _CANDLE_STORE = CandleStore(db_path)
        return _CANDLE_STORE


# ==============================================================================
# SECTION 9.1: MT4 WRITER (uses CandleStore instead of JSON snapshots)
# ==============================================================================
class MT4Writer:
    """ MT4 .
 
 :
 - sync_state[asset] {period, candles, last_write, last_price}
 - seed_history: + HST 
 - update_candle: + HST 200ms
 - fill_gap_once: 20 + HST
 
 :
 - derived_symbol (AUDJPY-OTC) api_symbol 
 - PERIOD=1 (M1) 60 (H1) => AUDJPY-OTC1.hst
 - makedirs + retry + silent errors ( FIX 4/8)
 """
    def __init__(self):
        appdata = os.environ.get('APPDATA', '') or os.environ.get('HOME', '')
        self.mt4_history_path = os.path.join(appdata, 'MetaQuotes', 'Terminal', 'Common', 'Files', 'qx_hst')
        try:
            os.makedirs(self.mt4_history_path, exist_ok=True)
        except Exception as e:
            logmsg(f"Cannot create MT4 folder: {e}")
        # ===== FIX 10: sync_state derived_symbol ( AUDJPY-OTC) =====
        # seed_history + update_candle + fill_gap_once
        # => (AUDJPY-OTC1.hst)
        self.sync_state: Dict[str, Any] = {}
        self._writing_queue = set()
        self._gap_filled = {}
        # ===== FIX L8: =====
        # GAP_FILL_REFRESH_INTERVAL ( )
        # => .
        self._gap_filled_at: Dict[str, float] = {}
        # ---- PERSISTENT STORAGE: SQLite-backed candle store ----------------
        # CandleStore replaces the previous JSON snapshot approach. SQLite is
        # transactional, atomic, indexed by (symbol, time), and far faster than
        # writing/loading a 30 KB JSON file on every cycle. The DB lives at:
        #   %APPDATA%\MetaQuotes\Terminal\Common\Files\qx_hst_snapshots\candles.db
        # See SECTION 9 above for the CandleStore class definition.
        self._candle_store: Optional[CandleStore] = None   # lazy via get_candle_store()

    @property
    def candle_store(self) -> "CandleStore":
        """Lazy accessor so the DB connection is created after APPDATA is set."""
        if self._candle_store is None:
            self._candle_store = get_candle_store()
        return self._candle_store

    def load_snapshot(self, derived_symbol: str) -> Optional[list]:
        """Load candles for an asset from the SQLite store.
        Returns None if no candles exist (so seed_history falls back to the API).
        Also refreshes the in-memory gap_state from the DB."""
        try:
            stored = self.candle_store.get_candles(derived_symbol, limit=INITIAL_CANDLES)
            if not stored:
                return None
            # refresh in-memory gap_state from DB
            filled, last_at = self.candle_store.is_gap_filled(derived_symbol)
            self._gap_filled[derived_symbol] = filled
            self._gap_filled_at[derived_symbol] = last_at
            return stored
        except Exception as e:
            pass  # silenced - non-essential diagnostic
            return None

    def save_snapshot(self, derived_symbol: str, candles: list) -> None:
        """Persist the current candle list to the SQLite store.
        Called after seed_history + after each successful fill_gap_once."""
        try:
            self.candle_store.upsert_candles(derived_symbol, candles)
        except Exception as e:
            pass  # silenced - non-essential diagnostic

    def get_digits(self, symbol: str, price: float = 0.0) -> int:
        # FIX J: _resolve_digits ( mt4_digits.json)
        return _resolve_digits(symbol, price)

    def generate_hst_buffer(self, symbol: str, period: int, candles: list) -> bytes:
        # For sub-minute timeframes, write period=1 (M1) in the HST header
        # so MT4 opens it as a normal M1 file. The candles inside have actual
        # 5s/10s/15s/30s timestamps. For 60s+ timeframes, store the MT4 period int.
        header_period = 1 if PERIOD_SECONDS < 60 else period
        header = bytearray(148)
        struct.pack_into('<I', header, 0, 400)
        struct.pack_into('64s', header, 4, b'MetaQuotes Software Corp.'.ljust(64, b'\x00'))
        struct.pack_into('12s', header, 68, symbol[:12].encode('ascii').ljust(12, b'\x00'))
        struct.pack_into('<I', header, 80, header_period)
        first_price = candles[0]['close'] if candles else 0.0
        digits = self.get_digits(symbol, first_price)
        struct.pack_into('<I', header, 84, digits)
        struct.pack_into('<I', header, 88, 0)
        struct.pack_into('<I', header, 92, 0)
        body_size = len(candles) * 44
        buffer = bytearray(148 + body_size)
        buffer[:148] = header
        offset = 148
        for c in candles:
            struct.pack_into('<I', buffer, offset, int(c['time']))
            struct.pack_into('<d', buffer, offset + 4, float(c['open']))
            struct.pack_into('<d', buffer, offset + 12, float(c['low']))
            struct.pack_into('<d', buffer, offset + 20, float(c['high']))
            struct.pack_into('<d', buffer, offset + 28, float(c['close']))
            struct.pack_into('<Q', buffer, offset + 36, int(c.get('volume', 0)))
            offset += 44
        return bytes(buffer)

    def update_candle(self, asset: str, period: int, tick: dict):
        """ + HST 200ms ( ).

 Args:
 asset: derived_symbol ( "AUDJPY-OTC") — 
 period: MT4 timeframe (PERIOD=1 for M1) — 
 tick: {'time': int, 'price': float}
 """
        if asset not in self.sync_state:
            self.sync_state[asset] = {'period': period, 'candles': [], 'last_write': 0, 'last_price': 0.0}
        state = self.sync_state[asset]
        # ===== FIX L6: _align_time ( tz_offset + ) =====
        # —
        # seed_history fill_gap_once fetch_candles_once.
        aligned_time = _align_time(tick['time'])

        # FIX STALE-CANDLE v2: only the last candle (current/open) can be updated.
        # All candles before it are closed and must never be touched.
        if state['candles']:
            last_time = state['candles'][-1]['time']
            if aligned_time < last_time:
                # tick for a closed minute - ignore (protect closed candles)
                return
            elif aligned_time == last_time:
                last = state['candles'][-1]
                if tick['price'] == state['last_price']: return
                last['high'] = max(last['high'], tick['price'])
                last['low'] = min(last['low'], tick['price'])
                last['close'] = tick['price']
                last['volume'] += 1
            else:
                # new candle - check if there's a gap and fill it with flat candles
                period_secs = PERIOD_SECONDS if PERIOD_SECONDS > 0 else 60
                gap = (aligned_time - last_time) // period_secs
                if gap > 1:
                    # Fill gap with flat candles (use last close as price)
                    last_close = state['candles'][-1]['close']
                    fill_time = last_time + period_secs
                    while fill_time < aligned_time:
                        state['candles'].append({
                            'time': fill_time,
                            'open': last_close,
                            'high': last_close,
                            'low': last_close,
                            'close': last_close,
                            'volume': 0,
                        })
                        fill_time += period_secs
                # Now append the new candle (becomes the last)
                state['candles'].append({
                    'time': aligned_time, 'open': tick['price'], 'high': tick['price'],
                    'low': tick['price'], 'close': tick['price'], 'volume': 1,
                })
        else:
            state['candles'].append({
                'time': aligned_time, 'open': tick['price'], 'high': tick['price'],
                'low': tick['price'], 'close': tick['price'], 'volume': 1,
            })
        # v13: الحد رُفع من 1000 إلى ASSET_MAX_CANDLES (3000) لتراكم دفعات التمرير للخلف
        if len(state['candles']) > ASSET_MAX_CANDLES:
            state['candles'] = state['candles'][-ASSET_MAX_CANDLES:]
        state['last_price'] = tick['price']
        now = time.time()
        # v13: MT4_WRITE_THROTTLE (1.0s) بدل 0.2s — مع عشرات العملات المتدفقة
        # يبقى تحديث الشارت حياً (كل ثانية) دون إرهاق القرص.
        if now - state['last_write'] > MT4_WRITE_THROTTLE:
            self.write_to_file(asset, period, state['candles'])
            state['last_write'] = now

    def write_to_file(self, asset: str, period: int, candles: list):
        """ HST {asset}{period}.hst ( AUDJPY-OTC1.hst).

 Args:
 asset: derived_symbol ( "AUDJPY-OTC")
 period: MT4 timeframe (PERIOD=1 for M1)
"""
        # DISABLED: server no longer writes HST files (user request).
        # HST files are the ONLY output (Flask dashboard removed) — no web writes.
        if not WRITE_HST_FILES_ENABLED:
            return
        if asset in self._writing_queue: return
        self._writing_queue.add(asset)
        file_name = f"{asset}{period}.hst"
        file_path = os.path.join(self.mt4_history_path, file_name)
        temp_path = file_path + '.tmp'
        # / +
        def _is_silent_error(err_str):
            err_str = err_str.lower()
            return any(x in err_str for x in [
                'winerror 2', 'winerror 5', 'winerror 32', 'winerror 13',
                'introuvable', 'refusé', 'acces refusé', 'access denied',
                'permission', 'used by another', 'ebusy', 'eperm',
                'no such file', 'not found', 'does not exist'
            ])
        # ( WinError 2)
        try:
            os.makedirs(self.mt4_history_path, exist_ok=True)
        except Exception:
            pass
        try:
            buffer = self.generate_hst_buffer(asset, period, candles)
            with open(temp_path, 'wb') as f:
                f.write(buffer)
            # retry WinError 5 + 32
            replaced = False
            for attempt in range(8):
                try:
                    os.replace(temp_path, file_path)
                    replaced = True
                    break
                except (PermissionError, OSError) as e:
                    if _is_silent_error(str(e)):
                        time.sleep(0.05 + 0.05 * attempt)
                        continue
                    raise
            if not replaced:
                # fallback —
                try:
                    with open(file_path, 'wb') as f:
                        f.write(buffer)
                    replaced = True
                except Exception as fallback_err:
                    if not _is_silent_error(str(fallback_err)):
                        logmsg(f"MT4 Write Error for {asset} (fallback): {fallback_err}")
        except OSError as e:
            if not _is_silent_error(str(e)):
                logmsg(f"MT4 Write Error for {asset}: {e}")
        except Exception as e:
            if not _is_silent_error(str(e)):
                logmsg(f"MT4 Write Error for {asset}: {e}")
        finally:
            self._writing_queue.discard(asset)
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except Exception: pass

    async def seed_history(self, client, asset_obj, period: int, days: float = 0.75):
        """ + HST ( ).
 
 Args:
 client: Quotex
 asset_obj: Asset ( api_symbol symbol)
 period: MT4 timeframe (PERIOD=1 for M1) — get_candles PERIOD_SECONDS
 days: (default 0.75 = 18 )
 
 Returns:
 True False 
 """
        api_symbol = asset_obj.api_symbol
        derived_symbol = asset_obj.symbol

        # ---- SNAPSHOT FAST PATH ------------------------------------------------
        # If we have a previously-saved snapshot for this asset, use it directly.
        # This avoids re-fetching historical candles from the API on every restart
        # and prevents the "candles flicker / disappear and reappear" symptom
        # caused by the API returning slightly different candle data each call.
        # The streaming update_candle() path will simply append new candles as
        # they happen, and fill_gap_once() will only ADD new closed candles
        # (never replace existing ones, since the snapshot marks them as frozen).
        try:
            snap = self.load_snapshot(derived_symbol)
            if snap and len(snap) >= 2:
                snap = sorted(snap, key=lambda x: x['time'])[-INITIAL_CANDLES:]
                # v14.1: اللقطة نفسها قد تحمل فجوات (حُفظت في جلسة انقطع فيها
                # البث) — سدّها بنفس الطريقة الأصلية قبل العرض حتى لا يعود
                # الثغل من قاعدة البيانات إلى الشارت في كل إعادة تشغيل.
                try:
                    snap = _fill_missing_slots(snap, PERIOD_SECONDS, max_gap=1440)
                except Exception:
                    pass
                # populate sync_state from the snapshot
                self.sync_state[derived_symbol] = {
                    'period': period,
                    'candles': list(snap),
                    'last_write': 0,
                    'last_price': float(snap[-1]['close']) if snap else 0.0,
                }
                # write HST so MT4 picks them up immediately
                self.write_to_file(derived_symbol, period, snap)
                asset_obj.candles = list(snap)
                if snap:
                    asset_obj.price = snap[-1]['close']
                # gap is considered already filled (frozen) for the snapshot range
                self._gap_filled[derived_symbol] = True
                self._gap_filled_at[derived_symbol] = time.time()
                pass  # silenced - non-essential diagnostic
                return True
        except Exception as _se:
            pass  # silenced - non-essential diagnostic

        try:
            offset_seconds = int(days * 86400)
            # ===== FIX 10: get_candles PERIOD_SECONDS (60s ) =====
            # PERIOD (1 = M1 timeframe)
            # v13.1: عبر بوابة الجلب الواحدة — نفس الطلب نفسه بلا اختلاط
            candles = await qx_fetch_window_raw(api_symbol, time.time(), offset_seconds,
                                                PERIOD_SECONDS, foreground=False,
                                                timeout=FETCH_TIMEOUT, retries=1)
            if candles and len(candles) > 0:
                # ===== FIX L7: _align_time ( tz_offset + ) =====
                # `t = int(c.get('time', ...)) + _tz_offset` —
                # => API 22:36:30 22:36:30
                # update_candle 22:36:00 => => .
                # : _align_time tz_offset + => .
                formatted = []
                for c in candles:
                    t = _align_time(int(c.get('time', c.get('timestamp', 0))))
                    o = float(c.get('open', c.get('o', 0)) or 0)
                    h = float(c.get('high', c.get('max', c.get('h', 0))) or 0)
                    l = float(c.get('low', c.get('min', c.get('l', 0))) or 0)
                    cl = float(c.get('close', c.get('c', 0)) or 0)
                    if o > 0 and h > 0 and l > 0 and cl > 0:
                        formatted.append({
                            'time': t, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': 0,
                        })
                formatted.sort(key=lambda x: x['time'])
                seen = set()
                unique_candles = [c for c in formatted if not (c['time'] in seen or seen.add(c['time']))]
                # ===== FIX 10: 1000 + =====
                unique_candles = unique_candles[-INITIAL_CANDLES:]
                # ===== FIX 10: sync_state derived_symbol ( AUDJPY-OTC) =====
                self.sync_state[derived_symbol] = {
                    'period': period, 'candles': unique_candles, 'last_write': 0, 'last_price': 0.0,
                }
                # ===== FIX 10: HST derived_symbol + period (AUDJPY-OTC1.hst) =====
                self.write_to_file(derived_symbol, period, unique_candles)
                # asset_obj.candles ( )
                asset_obj.candles = unique_candles
                if unique_candles:
                    asset_obj.price = unique_candles[-1]['close']
                self._gap_filled[derived_symbol] = False
                # ---- Save the freshly-fetched candles as the snapshot so the next
                # restart uses them as-is and never re-fetches this range. ----
                self.save_snapshot(derived_symbol, unique_candles)
                return True
            return False
        except Exception as e:
            # ( spam)
            err_str = str(e).lower()
            if not any(x in err_str for x in ['winerror', 'permission', 'access', 'closed', 'connection']):
                pass  # — main fetch loop
            return False

    def _scan_line_holes(self, candles: list, period_seconds: int,
                         max_reasonable_gap_periods: int = 120) -> bool:
        """فحص قرائي فقط: هل خط الشموع يحتوي فجوات زمنية حقيقية؟

        v14.1 — يستعمله فرع علامة التجمد في fill_gap_once ليعرف إن كانت
        الطريقة الأصلية مطلوبة فعلاً. الفجوة «حقيقية» إذا فرق الوقت بين شمعتين
        متجاورتين أكثر من فترة واحدة وأقل من حد الإغلاق المعقول (120 فترة
        = ساعتين للفريم الدقيقة — إغلاقات الأسواق الحقيقية أطول من ذلك
        ولا تُعتبر فقداناً، نفس عتبة مدقق v14).
        """
        try:
            if not candles or len(candles) < 2:
                return False
            period_s = max(1, int(period_seconds or PERIOD_SECONDS))
            max_gap_s = period_s * int(max_reasonable_gap_periods)
            line = sorted(candles, key=lambda c: int(c.get('time', 0)))
            for a, b in zip(line, line[1:]):
                gap = int(b.get('time', 0)) - int(a.get('time', 0))
                if period_s < gap <= max_gap_s:
                    return True
            return False
        except Exception:
            return False

    async def fill_gap_once(self, client, asset_obj, period: int):
        """ GAP_FILL_CANDLES + .

 (FIX L9):
 1. _align_time tz_offset + => .
 2. GAP_FILL_REFRESH_INTERVAL => .
 3. _fill_missing_slots => .
 4. 0 (volume=0) => .

 (NEW - FREEZE AFTER FIRST SUCCESS):
 5. The original fill_gap_once algorithm is left intact. The ONLY new thing
    is a persistent freeze flag in the SQLite candle store (gap_state.filled).
    Once a successful fill has run for an asset, the flag is set to 1 and
    every subsequent call to fill_gap_once returns immediately without
    touching the candles. This preserves the candles exactly as they were
    after the first fill - no flicker, no replacement of closed candles.
    A 'full re-fetch' command can clear the flag and force a new fill.

 Args:
 client: Quotex
 asset_obj: Asset ( api_symbol symbol)
 period: MT4 timeframe (PERIOD=1 for M1)
 """
        api_symbol = asset_obj.api_symbol
        derived_symbol = asset_obj.symbol

        # 0) FREEZE CHECK: if a successful fill already happened for this asset
        # (gap_state.filled == 1 in the SQLite store), do NOT touch the candles
        # at all. This is the entire fix for the 'candles flicker' symptom -
        # the original algorithm is preserved 1:1, we only skip it after the
        # first successful run.
        #
        # ===== v14.1 FIX — «طريقة سد الثغرات صارت لا تعمل اطلاقاً» =====
        # سبب التعطيل: علامة التجمد (gap_state.filled=1 في candles.db) تبقى
        # مكتوبة للأبد بعد أول سد ناجح — حتى بعد إعادة تشغيل البرنامج — فكانت
        # كل نداءات fill_gap_once لاحقاً (من الحلقة الشاملة mt4_gap_filler ومن
        # مدقق الفقدان v14_gap_fill_for_asset) تخرج فوراً دون أي عمل، وأي فجوة
        # جديدة (انقطاع بث، فجوة خادم، دفعة تمرير أقدم) تبقى بلا سد للأبد.
        # الحل مع الحفاظ على الطريقة الأصلية حرفياً: عند وجود علامة تجمد نفحص
        # خط الشموع الحالي — إن كانت سليمة بلا فجوات نخرج كما كان، وإن كانت
        # فيها فجوات حقيقية نلغي التجمد وندع الخوارزمية الأصلية نفسها تنفذ
        # (نفس الأصل: جلب GAP_FILL_CANDLES شمعة حديثة + دمج + _fill_missing_slots).
        try:
            is_filled, _last_at = self.candle_store.is_gap_filled(derived_symbol)
            if is_filled:
                _hole_line = None
                if asset_obj is not None and getattr(asset_obj, "candles", None):
                    _hole_line = list(asset_obj.candles)
                elif isinstance(self.sync_state.get(derived_symbol), dict) \
                        and self.sync_state[derived_symbol].get("candles"):
                    _hole_line = list(self.sync_state[derived_symbol]["candles"])
                _holes_found = self._scan_line_holes(_hole_line, PERIOD_SECONDS)
                if not _holes_found:
                    return    # frozen - keep candles exactly as they were (original behaviour)
                # فجوات حقيقية موجودة — ألغِ التجمد ودع الطريقة الأصلية تسدّها
                try:
                    self.candle_store.set_gap_filled(derived_symbol, False, time.time())
                except Exception:
                    pass
                self._gap_filled[derived_symbol] = False
                self._gap_filled_at[derived_symbol] = 0.0
                try:
                    logmsg(f"[gap:{derived_symbol}] freeze lifted — "
                           f"{len(_hole_line or [])} candles scanned, holes found → "
                           f"original fill_gap_once runs again")
                except Exception:
                    pass
        except Exception:
            pass

        # 1) skip if filled recently (within GAP_FILL_REFRESH_INTERVAL)
        now_ts = time.time()
        last_fill = self._gap_filled_at.get(derived_symbol, 0)
        already_filled = self._gap_filled.get(derived_symbol, False)
        if already_filled and (now_ts - last_fill) < GAP_FILL_REFRESH_INTERVAL:
            return

        # 2) sync_state asset_obj.candles
        if derived_symbol not in self.sync_state:
            if not asset_obj.candles:
                # try to load from store first
                snap = self.load_snapshot(derived_symbol)
                if snap:
                    asset_obj.candles = snap
                else:
                    return
            self.sync_state[derived_symbol] = {
                'period': period,
                'candles': list(asset_obj.candles),
                'last_write': 0,
                'last_price': float(asset_obj.candles[-1]['close']) if asset_obj.candles else 0.0,
            }
        state = self.sync_state[derived_symbol]
        if not state['candles']:
            return

        try:
            # Fetch last GAP_FILL_CANDLES (10) recent candles to replace incomplete ones
            small_days = (GAP_FILL_CANDLES * PERIOD_SECONDS) / 86400.0
            # v13.1: عبر بوابة الجلب الواحدة — لا يختلط جلب سد الثغرات مع أي جلب آخر
            candles = await qx_fetch_window_raw(
                api_symbol, time.time(), int(small_days * 86400), PERIOD_SECONDS,
                foreground=False, timeout=BRIDGE_FETCH_TIMEOUT)
            if not candles:
                # Fill existing gaps even without new data
                merged = sorted(state['candles'], key=lambda x: x['time'])[-INITIAL_CANDLES:]
                merged = _fill_missing_slots(merged, PERIOD_SECONDS, max_gap=1440)
                state['candles'] = merged
                self.write_to_file(derived_symbol, period, merged)
                asset_obj.candles = merged
                self._gap_filled[derived_symbol] = True
                self._gap_filled_at[derived_symbol] = now_ts
                self.save_snapshot(derived_symbol, merged)
                # mark as permanently filled in the DB so the next cycle skips
                self.candle_store.set_gap_filled(derived_symbol, True, now_ts)
                return

            # Build candle_map: replace incomplete closed candles with real API data
            # - Current streaming candle (time >= current_period_start): SKIP (streaming handles it)
            # - Closed candles in the fetched range: REPLACE with real data (fixes small bodies)
            # - Missing candles: ADD them
            # - Synthetic candles (volume=0): REPLACE with real data
            current_period_start = _align_time(int(time.time()))
            candle_map: Dict[int, dict] = {}
            for c in state['candles']:
                candle_map[c['time']] = c
            new_count = 0
            replaced_count = 0
            for c in candles:
                t = _align_time(int(c.get('time', c.get('timestamp', 0))))
                o = float(c.get('open', c.get('o', 0)) or 0)
                h = float(c.get('high', c.get('max', c.get('h', 0))) or 0)
                l = float(c.get('low', c.get('min', c.get('l', 0))) or 0)
                cl = float(c.get('close', c.get('c', 0)) or 0)
                v = int(c.get('volume', c.get('vol', 0)) or 0)
                if o > 0 and h > 0 and l > 0 and cl > 0:
                    existing = candle_map.get(t)
                    if existing is None:
                        # genuinely missing candle (real gap) - add it
                        candle_map[t] = {
                            'time': t, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v,
                        }
                        new_count += 1
                    elif t >= current_period_start:
                        # current streaming candle - DON'T TOUCH (streaming handles it)
                        continue
                    else:
                        # closed candle in the fetched range - REPLACE with real data
                        # (fixes small/incomplete bodies from partial streaming)
                        candle_map[t] = {
                            'time': t, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v,
                        }
                        replaced_count += 1

            # sort + limit to INITIAL_CANDLES
            merged = sorted(candle_map.values(), key=lambda x: x['time'])[-INITIAL_CANDLES:]
            # fill remaining gaps with flat candles (max_gap=1440 = full day)
            merged = _fill_missing_slots(merged, PERIOD_SECONDS, max_gap=1440)
            state['candles'] = merged

            # write HST
            self.write_to_file(derived_symbol, period, merged)

            # update asset_obj.candles (for live price display)
            asset_obj.candles = merged
            if merged:
                asset_obj.price = merged[-1]['close']

            # 9) mark gap as filled
            self._gap_filled[derived_symbol] = True
            self._gap_filled_at[derived_symbol] = now_ts
            # 10) persist candles to the SQLite store (so the next restart
            # loads them from the DB instead of re-fetching from the API).
            self.save_snapshot(derived_symbol, merged)
            # 11) set the permanent freeze flag - subsequent fill_gap_once
            # calls for this asset will return immediately without touching
            # the candles. This is the entire fix for the 'flicker' symptom.
            self.candle_store.set_gap_filled(derived_symbol, True, now_ts)
        except Exception as e:
            err_str = str(e).lower()
            if not any(x in err_str for x in ['winerror', 'permission', 'access', 'closed', 'connection']):
                pass

MT4_WRITER = MT4Writer()

async def mt4_gap_filler():
    global GAP_FILL_SUMMARY, GAP_FILL_ACTIVE
    # Skip entirely for subsecond mode — no gap filler for 5s/10s/15s/30s
    if IS_SUBSECOND:
        GAP_FILL_SUMMARY = "GAP FILL: disabled (subsecond mode)"
        GAP_FILL_ACTIVE = False
        return
    total = len(ALL_STREAMING_ASSETS)
    GAP_FILL_SUMMARY = f"GAP FILL: waiting 60s before starting ({total} assets)..."
    await asyncio.sleep(60)
    cycle = 0
    while True:
        cycle += 1
        if not ALL_STREAMING_ASSETS:
            GAP_FILL_SUMMARY = "GAP FILL: no assets to fill"
            GAP_FILL_ACTIVE = False
            await asyncio.sleep(GAP_FILL_REFRESH_INTERVAL)
            continue
        GAP_FILL_ACTIVE = True
        filled_count = 0
        skipped_count = 0
        failed_count = 0
        failed_assets = []
        t0 = time.time()
        for i, asset in enumerate(ALL_STREAMING_ASSETS, 1):
            if not CLIENT or not CLIENT.api:
                GAP_FILL_SUMMARY = f"GAP FILL: ABORTED (connection lost) | {filled_count}/{total} filled | {skipped_count} skipped"
                GAP_FILL_ACTIVE = False
                await asyncio.sleep(5)
                break
            try:
                await MT4_WRITER.fill_gap_once(CLIENT, asset, PERIOD)
                if MT4_WRITER._gap_filled.get(asset.symbol, False):
                    filled_count += 1
                else:
                    skipped_count += 1
                await asyncio.sleep(0.3)
            except Exception:
                skipped_count += 1
                failed_count += 1
                failed_assets.append(asset.symbol)
            # live progress update in banner
            GAP_FILL_SUMMARY = (
                f"GAP FILL c{cycle}: {i}/{total} done | {filled_count} filled | "
                f"{skipped_count} skipped | {failed_count} failed | {time.time()-t0:.1f}s"
            )
        else:
            # loop completed normally (no connection loss break)
            elapsed = time.time() - t0
            fail_str = f" | Failed: {', '.join(failed_assets[:5])}" if failed_assets else ""
            GAP_FILL_SUMMARY = (
                f"GAP FILL c{cycle}: COMPLETE in {elapsed:.1f}s | {filled_count}/{total} filled | "
                f"{skipped_count} skipped{fail_str} | next in {GAP_FILL_REFRESH_INTERVAL}s"
            )
            GAP_FILL_ACTIVE = False
            await asyncio.sleep(GAP_FILL_REFRESH_INTERVAL)
            total = len(ALL_STREAMING_ASSETS)
            continue
        # reached here only on connection loss (break)
        GAP_FILL_ACTIVE = False
        await asyncio.sleep(GAP_FILL_REFRESH_INTERVAL)
        total = len(ALL_STREAMING_ASSETS)


# ==============================================================================
# SECTION 10 (v13.2): CHART-DRIVEN 300 + PAGINATION 300 + TICK RETENTION 5 MIN
# ==============================================================================
# محرك التحميل المسبق (بطلب المستخدم حرفياً):
#   1) بعد الدخول مباشرة: 300 شمعة لـ BRLUSD_otc (هي العملة التي تفتح الشارت)
#      مع حالتها (مفتوح/مغلق) ونسبة دفعها.
#   2) بقية الأصول المفتوحة تتحمل واحدة تلو الأخرى: 300 شمعة لكل عملة.
#   3) البث الحي يبقى يعمل لكل عملة محمّلة — لذلك عندما يُفتح أي شارت لاحقاً
#      يكون جاهزاً فوراً (الأسعار تتدفق داخله باستمرار).
#   4) fetch_older_batch(): عند التمرير للخلف في الشارت يجلب دفعة صغيرة من
#      300 شمعة أقدم، وكلما زاد التمرير للخلف تظهر شموع أخرى مثل المنصات
#      الاحترافية. الدالة جاهزة الآن على الخادم؛ ربطها بالتطبيق يُضاف لاحقاً
#      (طلب المستخدم: ليس الآن).
#   5) التيكات تُحفظ في الذاكرة فقط ولا تُكتب على القرص أبداً، وتُحذف تلقائياً
#      بعد 5 دقائق (لأن الشموع تكون قد تشكّلت منها) — بهذا لا يمتلئ القرص
#      بالتيكس ولا بالشموع مهما طال عمر التشغيل.
# طريقة الدخول وطريقة جلب الشموع الأصلية لم تُمَس إطلاقاً.
# ==============================================================================
from collections import deque as _deque

# كاش التيكات في الذاكرة فقط: api_symbol -> deque[(ts, price)]
_TICK_CACHE = {}
_TICK_LOCK = threading.Lock()
_PRELOADED_INFO = {}      # api_symbol -> {"candles": n, "at": "HH:MM:SS", "oldest": ts, "closed": bool}
_ASSET_OBJECTS = {}       # api_symbol -> Asset (مسمّيات الكائنات المعاد استخدامها)
_OPENER_STATUS_SHOWN = False


def _get_or_create_asset(api_symbol: str) -> Asset:
    """يعيد كائن Asset موجود أو ينشئه (بدون تكرار)."""
    for a in list(ALL_STREAMING_ASSETS):
        if a.api_symbol == api_symbol:
            return a
    a = _ASSET_OBJECTS.get(api_symbol)
    if a is None:
        a = Asset(api_symbol)
        _ASSET_OBJECTS[api_symbol] = a
    return a


# ==============================================================================
# SECTION 10.5 (v13.1): FETCH GATE — منع اختلاط عمليات الجلب (طلب المستخدم حرفياً)
# ==============================================================================
# ما أبلغ عنه المستخدم: «تعليق والاختلاط بين عمليات الجلب — يختلط بين اكتمال
# كل تلك العملات وجلب عملة نريد الرجوع للخلف فيها» — فراغات في الشموع،
# شارتات تُفتح بلا شموع، والتمرير للخلف لا يجلب شيئاً.
#
# السبب الجذري (من قراءة الكود): CLIENT.get_candles ينتظر الحدث
# candles_ready_<asset> — وعنصر هذا الحدث هو اسم العملة فقط. أي رسالة حية
# لنفس العملة تحمل candles (لقطات البث) تُشغّل الحدث قبل وصول رد
# history/load الحقيقي فيأخذ الانتظار رداً مكسوراً (شموع قليلة/خاطئة)،
# وطلبَان لنفس العملة في نفس اللحظة يستهلك كل منهما رد الآخر.
#
# الحل — وطريقة الجلب نفسها لم تُمَس حرفياً (نفس CLIENT.get_candles ونفس
# رسالة history/load):
#   1) بوابة واحدة: طلب جلب واحد فقط في كل لحظة على مستوى الخادم كله —
#      لا يوجد أي طلبان متزامنان بعد الآن.
#   2) أولوية أمامية: طلبات المستخدم (تمرير للخلف / جلب عملة فُتح شارتها
#      فارغة / فريم أعلى للعملة المعروضة) تحمل foreground=True، وحلقة
#      التحميل المسبق الخلفية تتوقف مؤقتاً ما دام هناك طلب أمامي معلّق.
#   3) تحقق وإعادة محاولة: إذا كان الرد أقل بوضوح من نافذة الزمن المطلوبة
#      (يعني رسالة حية سرقت الحدث) يُعاد الطلب بنفس الطريقة الأصلية.
#   4) debounce: نفس النافذة (عملة/فريم/نهاية) خلال 3 ثوانٍ يعيد النتيجة
#      المخزنة بدل إرسال طلب مكرر يختلط مع السابق.
_FETCH_GATE_LOCK: Optional[asyncio.Lock] = None   # تُنشأ في أول استدعاء
_FETCH_GATE_FG = 0                                # عدد الطلبات الأمامية المعلّقة
_FETCH_GATE_CACHE: Dict[tuple, tuple] = {}        # (asset,period,end,seconds) -> (ts, raw_res)
_FETCH_GATE_CACHE_TTL = 3.0                       # ثوانٍ


def _fetch_gate_lock() -> asyncio.Lock:
    global _FETCH_GATE_LOCK
    if _FETCH_GATE_LOCK is None:
        _FETCH_GATE_LOCK = asyncio.Lock()
    return _FETCH_GATE_LOCK


def fetch_gate_foreground_pending() -> int:
    """كم طلب أمامي (من المستخدم) معلّق الآن — حلقة التحميل المسبق تنتظرها."""
    return _FETCH_GATE_FG


async def _fetch_gate_wait_foreground(max_wait: float = 45.0):
    """ينتظر حتى لا يبقى أي طلب أمامي معلّق (تستعملها الحلقة الخلفية فقط)."""
    waited = 0.0
    while _FETCH_GATE_FG > 0 and waited < max_wait:
        await asyncio.sleep(0.4)
        waited += 0.4


async def qx_fetch_window_raw(api_symbol: str, end_time: int, seconds: int,
                              period: int, foreground: bool = False,
                              timeout: float = None, retries: int = 2):
    """نفس طريقة الجلب الأصلية حرفياً (CLIENT.get_candles → history/load)
    لكن عبر البوابة المرتبة: طلب واحد في كل لحظة + أولوية أمامية + تحقق.

    يعيد رد الخادم الخام كما هو (نفس عقد CLIENT.get_candles) — التنسيق
    يبقى في يد المستدعي كما كان تماماً قبل البوابة."""
    global _FETCH_GATE_FG
    if CLIENT is None or CLIENT.api is None:
        return None
    if timeout is None:
        timeout = PRELOAD_TIMEOUT
    end_time = int(end_time)
    seconds = max(int(period), int(seconds))
    # 4) debounce: نفس الطلب خلال ثوانٍ → نفس النتيجة بلا طلب مكرر يختلط
    key = (api_symbol, int(period), end_time, int(seconds))
    now = time.time()
    hit = _FETCH_GATE_CACHE.get(key)
    if hit is not None and (now - hit[0]) < _FETCH_GATE_CACHE_TTL:
        return hit[1]
    if foreground:
        _FETCH_GATE_FG += 1
    try:
        # 3) تحقق: الحد الأدنى المقبول من الشموع مقارنة بنافذة الزمن المطلوبة.
        #    طلب 300 شمعة لا يُقبل بـ 3 شموع — هذا رد حي مكسور يُعاد طلبه.
        expected = max(1, int(seconds) // max(1, int(period)))
        min_ok = max(3, min(PRELOAD_MIN_CANDLES, expected // 4))
        raw = None
        for attempt in range(max(1, int(retries) + 1)):
            # 1) البوابة: طلب واحد فقط في كل لحظة على مستوى الخادم كله
            async with _fetch_gate_lock():
                raw = await asyncio.wait_for(
                    CLIENT.get_candles(api_symbol, end_time, int(seconds), period),
                    timeout=float(timeout) + 5.0,
                )
            if raw is None:
                break
            try:
                n_ok = len(_quick_count_candles(raw, period))
            except Exception:
                n_ok = expected
            if n_ok >= min_ok:
                break
            # الرد مكسور (رسالة حية سرقت الحدث candles_ready) — أعد بنفس الطريقة
            logmsg(f"[gate:{api_symbol}] broken response ({n_ok} candles < {min_ok}) "
                   f"— retry {attempt + 1}/{max(1, int(retries) + 1)}")
            await asyncio.sleep(0.8)
        try:
            # v14.1: لا نخزّن رداً None في الكاش — الرد الفاشل المُخزَّن كان
            # يسمّم نفس نافذة التمرير للخلف لمدة TTL كاملة (كل إعادة طلب
            # لنفس before_time كانت ترجع None فوراً من الكاش بدل الخادم).
            if raw is not None:
                _FETCH_GATE_CACHE[key] = (time.time(), raw)
                if len(_FETCH_GATE_CACHE) > 96:
                    for _k in list(_FETCH_GATE_CACHE.keys())[:48]:
                        _FETCH_GATE_CACHE.pop(_k, None)
            elif key in _FETCH_GATE_CACHE:
                _FETCH_GATE_CACHE.pop(key, None)
        except Exception:
            pass
        return raw
    finally:
        if foreground:
            _FETCH_GATE_FG = max(0, _FETCH_GATE_FG - 1)


def _quick_count_candles(raw, period: int) -> list:
    """عدّاد سريع لشموع الرد الخام (للتحقق داخل البوابة فقط) — محاذاة على
    حدود الفريم المطلوب نفسها التي يستعملها التنسيق الرسمي."""
    out = []
    if not raw:
        return out
    for c in raw:
        if not isinstance(c, dict):
            continue
        try:
            ts = int(float(c.get("time", c.get("timestamp", 0))))
            if ts <= 0:
                continue
            out.append(ts - (ts % max(1, int(period))))
        except Exception:
            continue
    return set(out)


def _cache_tick(api_symbol: str, ts: int, price: float):
    """يخزن تيكاً في الذاكرة فقط (لا يوجد أي ملف تيكات على القرص في v13)."""
    with _TICK_LOCK:
        d = _TICK_CACHE.get(api_symbol)
        if d is None:
            d = _deque(maxlen=TICK_CACHE_MAXLEN)
            _TICK_CACHE[api_symbol] = d
        d.append((int(ts), float(price)))


def _prune_tick_cache() -> int:
    """v13 (طلب المستخدم): حذف كل تيك أقدم من 5 دقائق — التيكات القديمة لا
    فائدة منها لأن الشموع تشكّلت منها، وحذفها يمنع امتلاء الذاكرة والقرص."""
    cutoff = time.time() - TICK_RETENTION_SECONDS
    removed = 0
    with _TICK_LOCK:
        for sym in list(_TICK_CACHE.keys()):
            d = _TICK_CACHE[sym]
            n0 = len(d)
            while d and d[0][0] < cutoff:
                d.popleft()
            removed += n0 - len(d)
            if not d:
                _TICK_CACHE.pop(sym, None)
    return removed


def get_recent_ticks(api_symbol: str, seconds: int = TICK_RETENTION_SECONDS) -> list:
    """يعيد تيكات آخر N ثانية لعملة معينة من الكاش (للتطبيق لاحقاً)."""
    with _TICK_LOCK:
        d = _TICK_CACHE.get(api_symbol)
        if not d:
            return []
        cutoff = time.time() - max(1, int(seconds))
        return [[t, p] for (t, p) in d if t >= cutoff]


async def tick_cache_collector():
    """يجمع تيكات كل الأصول المتدفقة في الذاكرة فقط — كل 0.25 ثانية يقرأ آخر
    سعر من realtime_candles لكل عملة ويخزنه. لا يكتب أي شيء على القرص."""
    last_ts = {}
    while True:
        try:
            if CLIENT is not None and CLIENT.api is not None and CONNECTION_ALIVE:
                for asset in list(ALL_STREAMING_ASSETS):
                    c = CLIENT.api.realtime_candles.get(asset.api_symbol)
                    try:
                        if isinstance(c, list) and len(c) >= 3:
                            ts, price = int(c[1]), float(c[2])
                        elif isinstance(c, dict):
                            ts = int(c.get("time", c.get("timestamp", 0)))
                            price = float(c.get("price", c.get("close", 0)))
                        else:
                            continue
                        if ts > 0 and price > 0 and ts > last_ts.get(asset.api_symbol, 0):
                            last_ts[asset.api_symbol] = ts
                            _cache_tick(asset.api_symbol, ts, price)
                    except Exception:
                        continue
            await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def tick_retention_loop():
    """v13: حلقة الحذف الدوري — كل TICK_PURGE_INTERVAL ثانية تحذف التيكات
    الأقدم من TICK_RETENTION_SECONDS (5 دقائق)."""
    while True:
        await asyncio.sleep(TICK_PURGE_INTERVAL)
        try:
            removed = _prune_tick_cache()
            kept = sum(len(d) for d in _TICK_CACHE.values())
            if removed:
                logmsg(f"[ticks] purged {removed} ticks older than "
                       f"{TICK_RETENTION_SECONDS // 60} min (kept {kept} in memory only — "
                       f"no tick is ever written to disk)")
        except Exception as e:
            logmsg(f"[ticks] purge error: {e}")


async def candlestore_trim_loop():
    """v13: ترميم candles.db كل ساعة — يحتفظ بأحدث CANDLESTORE_KEEP_PER_SYMBOL
    شمعة لكل عملة ويحذف الأقدم، ثم يفرّغ ملف WAL. بهذا لا ينمو حجم قاعدة
    الشموع بلا حدود حتى لو اشتغل السيرفر شهراً كاملاً."""
    while True:
        await asyncio.sleep(DB_TRIM_INTERVAL)
        try:
            db_path = get_candle_store().db_path
            conn = _sqlite3.connect(db_path, timeout=10.0, isolation_level=None)
            try:
                cur = conn.execute("SELECT DISTINCT symbol FROM candles;")
                symbols = [r[0] for r in cur.fetchall()]
                trimmed = 0
                for sym in symbols:
                    c2 = conn.execute(
                        "DELETE FROM candles WHERE symbol=? AND time < ("
                        " SELECT time FROM candles WHERE symbol=?"
                        " ORDER BY time DESC LIMIT 1 OFFSET ?);",
                        (sym, sym, CANDLESTORE_KEEP_PER_SYMBOL))
                    if c2.rowcount and c2.rowcount > 0:
                        trimmed += c2.rowcount
                if trimmed:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                    logmsg(f"[db] trimmed {trimmed} old candle rows "
                           f"(keep newest {CANDLESTORE_KEEP_PER_SYMBOL}/symbol)")
            finally:
                conn.close()
        except Exception as e:
            logmsg(f"[db] trim error: {e}")


def _format_raw_candles(res) -> list:
    """تحويل رد الخادم إلى شموع منسقة (نفس منطق وتنسيق fetch_candles_once
    الأصلي دون أي تغيير في طريقة الجلب نفسها)."""
    out = []
    if not res:
        return out
    for c in res:
        if not isinstance(c, dict):
            continue
        try:
            ts = int(float(c.get("time", c.get("timestamp", 0))))
            if ts <= 0:
                continue  # v13: تجاهل الردود بلا وقت صالح (حماية من شموع تالفة)
            aligned = _align_time(ts, period_seconds=PERIOD_SECONDS)
            o = float(c.get("open", 0))
            h = float(c.get("high", c.get("max", 0)))
            l = float(c.get("low", c.get("min", 0)))
            cl = float(c.get("close", 0))
            if o > 0 and h > 0 and l > 0 and cl > 0:
                out.append({'time': aligned, 'open': o, 'high': h, 'low': l,
                            'close': cl, 'volume': random.randint(50, 200)})
        except Exception:
            continue
    seen, unique = set(), []
    for c in out:
        if c['time'] not in seen:
            seen.add(c['time'])
            unique.append(c)
    unique.sort(key=lambda x: x['time'])
    return unique


async def _fetch_candle_window(api_symbol: str, end_time: int, seconds: int,
                               foreground: bool = False):
    """طلب شموع واحد عبر نفس CLIENT.get_candles الأصلي (نفس طريقة الجلب
    الرسمية دون أي تعديل): end_time = نهاية النافذة، seconds = طولها بالثواني.

    v13.1: الطلب يمر الآن عبر بوابة الجلب الواحدة (fetch gate) حتى لا يختلط
    مع أي جلب آخر — foreground=True يعني طلب المستخدم الأمامي (تمرير للخلف
    أو عملة فُتح شارتها) فيتقدم على التحميل المسبق الخلفي."""
    res = await qx_fetch_window_raw(
        api_symbol, int(end_time), int(seconds), PERIOD_SECONDS,
        foreground=foreground, timeout=PRELOAD_TIMEOUT,
    )
    return res


def _apply_candles_to_asset(asset: Asset, candles: list):
    """تخزين الشموع في كل القنوات الرسمية: ذاكرة العملة + ملف HST الأول
    + sync_state + ملف HST الثاني + قاعدة candles.db.

    v13.1 (طلب المستخدم): آلية سد الثغرات مُشغَّلة الآن عند التخزين نفسه —
    _fill_missing_slots نفسها بلا أي تغيير تملأ أي فجوة زمنية بشموع مسطحة
    (إغلاق الشمعة السابقة) حتى لا يظهر فارغ في الشموع أبداً."""
    candles = _fill_missing_slots(list(candles), PERIOD_SECONDS, max_gap=1440)
    asset.candles = list(candles)
    if candles:
        asset.price = float(candles[-1]['close'])
    try:
        asset.write(force=True)
    except Exception:
        pass
    MT4_WRITER.sync_state[asset.symbol] = {
        'period': PERIOD,
        'candles': list(asset.candles),
        'last_write': 0,
        'last_price': float(asset.candles[-1]['close']) if asset.candles else 0.0,
    }
    try:
        MT4_WRITER.write_to_file(asset.symbol, PERIOD, asset.candles)
    except Exception:
        pass
    try:
        MT4_WRITER.save_snapshot(asset.symbol, asset.candles)
    except Exception:
        pass


def _print_opener_banner(api_symbol: str, entry, candles_count: int, elapsed: float):
    """لوحة جاهزية عملة فتح الشارت: الشموع + الحالة + نسب الدفع."""
    def _p(v):
        return f"{v}%" if isinstance(v, (int, float)) else "-"
    name = (entry.get("name") or "-") if entry else "-"
    payout = entry.get("payout") if entry else None
    turbo = entry.get("turbo_payout") if entry else None
    p1 = entry.get("profit_1m") if entry else None
    p5 = entry.get("profit_5m") if entry else None
    if entry is None:
        status_str = f"{Colors.DIM}UNKNOWN (asset list not ready yet){Colors.RESET}"
    elif entry.get("open"):
        status_str = f"{Colors.GREEN}OPEN{Colors.RESET}"
    else:
        status_str = f"{Colors.RED}CLOSED{Colors.RESET}"
    print()
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}  CHART OPENER READY — {api_symbol}{Colors.RESET}")
    print(f"  Name: {name}  |  Candles: {candles_count}  |  Loaded in {elapsed:.1f}s")
    print(f"  Payout: {_p(payout)}  |  Turbo: {_p(turbo)}  |  1M: {_p(p1)}  |  5M: {_p(p5)}"
          f"  |  Status: {status_str}")
    print(f"  {Colors.DIM}Live stream: ON — الشارت جاهز للفتح فوراً والأسعار تتدفق داخله{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 70}{Colors.RESET}")


async def preload_one_asset(api_symbol: str, idx: int = 1, total: int = 1):
    """تحميل عملة واحدة: 300 شمعة عبر نفس طريقة الجلب الأصلية، ثم تشغيل
    البث الحي لها. تعيد عدد الشموع أو None عند الفشل."""
    asset = _get_or_create_asset(api_symbol)
    have_data = (asset.symbol in MT4_WRITER.sync_state and asset.candles
                 and len(asset.candles) >= PRELOAD_CANDLES)
    if not have_data:
        res = await _fetch_candle_window(
            api_symbol, int(time.time()), PRELOAD_CANDLES * PERIOD_SECONDS + PERIOD_SECONDS)
        candles = _format_raw_candles(res)[-PRELOAD_CANDLES:]
        if not candles or len(candles) < PRELOAD_MIN_CANDLES:
            logmsg(f"[preload {idx}/{total}] {api_symbol}: only {len(candles)} candles — skipped")
            return None
        _apply_candles_to_asset(asset, candles)
    # التأكد من أن البث الحي يعمل لهذه العملة (لأن أي شارت يُفتح لاحقاً يجب
    # أن يجد الأسعار تتدفق داخله — طلب المستخدم).
    task = asset.stream_task
    task_running = False
    try:
        task_running = task is not None and not task.done()
    except Exception:
        task_running = False
    if not (asset.streaming and task_running):
        try:
            asset.stream_task = asyncio.run_coroutine_threadsafe(realtime_stream(asset), ASYNC_LOOP)
            await asyncio.sleep(0.05)
        except Exception as e:
            logmsg(f"[preload {idx}/{total}] {api_symbol}: stream start failed: {e}")
    if asset not in ALL_STREAMING_ASSETS:
        ALL_STREAMING_ASSETS.append(asset)
    _PRELOADED_INFO[api_symbol] = {
        "candles": len(asset.candles) if asset.candles else 0,
        "at": datetime.now().strftime("%H:%M:%S"),
        "oldest": asset.candles[0]['time'] if asset.candles else 0,
        "closed": _PRELOADED_INFO.get(api_symbol, {}).get("closed", False),
    }
    return len(asset.candles) if asset.candles else 0


async def ensure_asset_loaded(api_symbol: str) -> int:
    """v13.1 (طلب المستخدم): جلب فوري بأولوية أمامية لعملة فتح التطبيق شارتها
    ووجدها بلا شموع — السبب كان أن التحميل المسبق الخلفي يمر على كل العملات
    واحدة تلو الأخرى (قد يستغرق دقائق)، فتُفتح عملة لم يصل دورها بعد فيُعرض
    شارت فارغ. هذه الدالة تجلب العملة فوراً عبر نفس المسار الرسمي
    (preload_one_asset → _fetch_candle_window → البوابة الأمامية) وتشغّل
    بثها الحي، فتمتلئ الشارت خلال ثوانٍ. تعيد عدد الشموع أو 0."""
    if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
        return 0
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return 0
    asset = _get_or_create_asset(api_symbol)
    if asset.candles and len(asset.candles) >= PRELOAD_MIN_CANDLES:
        # الشموع موجودة — تأكد فقط أن البث الحي يعمل لها
        task = asset.stream_task
        try:
            running = task is not None and not task.done()
        except Exception:
            running = False
        if not (asset.streaming and running):
            try:
                asset.stream_task = asyncio.run_coroutine_threadsafe(
                    realtime_stream(asset), ASYNC_LOOP)
            except Exception:
                pass
        return len(asset.candles)
    try:
        n = await preload_one_asset(api_symbol, 1, 1)
        return int(n or 0)
    except Exception as e:
        logmsg(f"[ensure:{api_symbol}] failed: {e}")
        return 0


async def preload_all_assets():
    """v13.2 (طلب المستخدم حرفياً): لا تحميل مسبق شامل بعد الآن —
    «العملة اللي نفتح الشارت تبعها يتم جلب 300 شمعة منها، واللي لم نفتح
    شارتها لا تجلب»:
      1) BRLUSD_otc (عملة فتح الشارت) تُجلب فوراً بعد الدخول — 300 شمعة + بث حي.
      2) أي عملة أخرى تُجلب فقط عند فتح التطبيق شارتها عبر ensure_asset_loaded()
         (متصلة ببوابة الجلب الأمامية، واحدة تلو الأخرى بلا تسرّع).
      3) هذه الحلقة لا تجلب أي شموع — فقط تراقب الأصول التي أُغلقت لإيقاف
         بثها، وتعيد تشغيل بث الأصول المفتوحة التي كان التطبيق يعرضها."""
    global _OPENER_STATUS_SHOWN
    logmsg(f"[preload] fetching {PRELOAD_FIRST_SYMBOL} immediately (chart opener)...")
    t0 = time.time()
    try:
        n = await preload_one_asset(PRELOAD_FIRST_SYMBOL, 1, 1)
        if n:
            logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL}: {n} candles + live stream ON "
                   f"({time.time() - t0:.1f}s)")
            _print_opener_banner(PRELOAD_FIRST_SYMBOL, None, n, time.time() - t0)
    except Exception as e:
        logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL} immediate fetch failed: {e} (will retry)")
    while True:
        cycle_start = time.time()
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = _instruments_snapshot()
            waited = 0.0
            while not entries and waited < PRELOAD_WAIT_INSTRUMENTS:
                await asyncio.sleep(2.0)
                waited += 2.0
                if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                    break
                entries = _instruments_snapshot()
            if entries:
                by_asset = {}
                for e in entries:
                    if e.get("asset"):
                        by_asset[e["asset"]] = e
                if not _OPENER_STATUS_SHOWN and PRELOAD_FIRST_SYMBOL in by_asset:
                    _OPENER_STATUS_SHOWN = True
                    _e = by_asset[PRELOAD_FIRST_SYMBOL]
                    _pv = _e.get("payout")
                    _pv_str = f"{_pv}%" if isinstance(_pv, (int, float)) else "-"
                    logmsg(f"[preload] {PRELOAD_FIRST_SYMBOL} status: "
                           f"{'OPEN' if _e.get('open') else 'CLOSED'} | payout {_pv_str}")
            else:
                by_asset = {}
            # v13.2: لا جلب شامل — الشموع تجلب عند فتح الشارت فقط (طلب المستخدم).
            # الحفاظ فقط على بث الأصول التي يعرضها التطبيق فعلاً (ولا نلمس بث فاتح الشارت).
            n_stream = len(ALL_STREAMING_ASSETS)
            logmsg(f"[preload] chart-driven mode: {n_stream} asset(s) streaming — "
                   f"candles load on chart open (one by one), no mass preload")
            # إيقاف بث الأصول التي أُغلقت (الشموع تبقى محفوظة في DB وHST،
            # وإذا أعيد فتحها لاحقاً يعود بثها تلقائياً في الدورة التالية).
            if by_asset:
                closed_syms = {a for a, e in by_asset.items() if e.get("open") is False}
                for asset in list(ALL_STREAMING_ASSETS):
                    if asset.api_symbol in closed_syms:
                        try:
                            if asset.stream_task is not None and not asset.stream_task.done():
                                asset.stream_task.cancel()
                        except Exception:
                            pass
                        asset.streaming = False
                        try:
                            ALL_STREAMING_ASSETS.remove(asset)
                        except ValueError:
                            pass
                        _info = _PRELOADED_INFO.get(asset.api_symbol)
                        if _info is not None:
                            _info["closed"] = True
                        logmsg(f"[preload] {asset.api_symbol}: CLOSED — live stream stopped "
                               f"(candles kept in DB/HST)")
            logmsg(f"[preload] cycle done in {time.time() - cycle_start:.0f}s — "
                   f"{len(ALL_STREAMING_ASSETS)} assets streaming live, "
                   f"{len(_PRELOADED_INFO)} loaded with candles")
        except Exception as e:
            log_exception("preload_all_assets", e)
        await asyncio.sleep(PRELOAD_REFRESH_INTERVAL)


async def fetch_older_batch(api_symbol: str, before_time=None, count: int = PAGINATION_BATCH):
    """v13.2: دفعة التمرير للخلف (scroll-back) — تجلب 300 شمعة أقدم (وليس 170،
    طلب المستخدم) من before_time عبر نفس طريقة الجلب الأصلية، ويدمجها مع
    الشموع الموجودة في الذاكرة وHST وcandles.db مع سد أي فجوة بين الدفعة
    والرأس الحالي. مثل المنصات الاحترافية: كلما مررت للخلف تظهر دفعة جديدة."""
    if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
        logmsg(f"[older:{api_symbol}] no connection — batch skipped")
        return 0
    asset = _get_or_create_asset(api_symbol)
    if before_time is None:
        if asset.candles:
            before_time = int(asset.candles[0]['time'])
        else:
            before_time = int(time.time()) - PRELOAD_CANDLES * PERIOD_SECONDS
    before_time = int(before_time)
    # v13.1: التمرير للخلف = طلب أمامي بأولوية عالية (يتقدم على التحميل المسبق
    # ولا يختلط معه بعد الآن — البوابة الواحدة + أولوية المستخدم)
    # v14.1: تحقق وأعد المحاولة مرة واحدة — إن جاء الرد بلا شموع أقدم من
    # before_time فالمرجح أن لقطة حية سرقت الحدث أو الرد مكسور؛ إعادة الطلب
    # بنفس الطريقة الأصلية (نفس CLIENT.get_candles عبر البوابة) تعطي الفرصة
    # للرد الحقيقي أن يصل.
    older = []
    candles = []
    for _attempt in range(2):
        res = await _fetch_candle_window(api_symbol, before_time,
                                         count * PERIOD_SECONDS + PERIOD_SECONDS,
                                         foreground=True)
        candles = _format_raw_candles(res)
        older = [c for c in candles if c['time'] < before_time][-count:]
        if older:
            break
        # لا شموع أقدم في هذا الرد — سجّل وأعد المحاولة مرة واحدة قبل الاستسلام
        if _attempt == 0:
            got = len(candles)
            logmsg(f"[older:{api_symbol}] attempt 1 got {got} candles but none older "
                   f"than {time.strftime('%Y-%m-%d %H:%M', time.gmtime(before_time))} "
                   f"— retrying once (stolen/broken response guard)")
            await asyncio.sleep(0.6)
    if not older:
        logmsg(f"[older:{api_symbol}] server returned nothing older than "
               f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(before_time))} (history end?)")
        return 0
    merged = list(older) + list(asset.candles or [])
    seen, unique = set(), []
    for c in merged:
        if c['time'] not in seen:
            seen.add(c['time'])
            unique.append(c)
    unique.sort(key=lambda x: x['time'])
    unique = unique[-ASSET_MAX_CANDLES:]
    _apply_candles_to_asset(asset, unique)
    # v13: تحديث معلومات التحميل المسبق ليعكس عدد الشموع بعد الدفعة الجديدة
    _prev_info = _PRELOADED_INFO.get(api_symbol, {})
    _PRELOADED_INFO[api_symbol] = {
        "candles": len(asset.candles) if asset.candles else 0,
        "at": datetime.now().strftime("%H:%M:%S"),
        "oldest": asset.candles[0]['time'] if asset.candles else 0,
        "closed": _prev_info.get("closed", False),
        "last_older_batch": len(older),
    }
    logmsg(f"[older:{api_symbol}] +{len(older)} candles (batch {count}) — oldest now "
           f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(unique[0]['time']))}")
    return len(older)


# نقطة ربط مستقبلية للتطبيق (عند ربطه لاحقاً كما طلب المستخدم):
#   PAGINATION_API["fetch_older_batch"]("BRLUSD_otc")  -> +300 شمعة أقدم
#   PAGINATION_API["get_recent_ticks"]("BRLUSD_otc")   -> تيكات آخر 5 دقائق
#   PAGINATION_API["preload_status"]()                 -> حالة التحميل المسبق
PAGINATION_API = {
    "fetch_older_batch": fetch_older_batch,
    "get_recent_ticks": get_recent_ticks,
    "preload_status": lambda: dict(_PRELOADED_INFO),
    "tick_cache": _TICK_CACHE,
    # v13.1 (طلب المستخدم): واجهة الجلب المرتبة — التطبيق يستدعيها بدل
    # CLIENT.get_candles المباشر فلا يختلط أي جلب مع آخر:
    "ensure_asset_loaded": ensure_asset_loaded,      # جلب فوري لعملة فُتحت بشارت فارغ
    "fetch_window_raw": qx_fetch_window_raw,         # نفس get_candles عبر البوابة
    "fetch_gate_pending": fetch_gate_foreground_pending,
}


# ════════════════════════════════════════════════════════════════════════════
# ═══════════════════ QX SERVER v14 — STRENGTHENING LAYER (طبقة التقوية) ═════
# ════════════════════════════════════════════════════════════════════════════
#
# ─────────────────────────────── v14.1 (2026-11-14) ──────────────────────────
# إصلاح طلبات المستخدم الحرفية:
#
#   «الرجوع الى الخلف مزال لا يجلب الشموع ... كما تفعل المنصات الحديثة مثل
#    تريدنغ فيو»
#   «طريقة سد الثغرات يجب ان تاخذها من هذا الكود لانني رايت صارت لا تعمل
#    اطلاقا»
#
# 1) سبب «التمرير للخلف لا يجلب شموعاً» — الجذر الحقيقي (توجيه رد الجلب):
#    الحدث candles_ready_<asset> كان يُرفع لأي رسالة تحمل شموعاً لنفس
#    العملة — بما فيها لقطات البث الحي (instruments/update) — فتسرق اللقطة
#    الحية الحدث قبل وصول رد history/load الحقيقي، فيأخذ انتظار الجلب شموعاً
#    حديثة لا تنفع التمرير للخلف (تُفلتر كلها لأنها ليست أقدم من before_time)
#    فتظهر النتيجة فارغة دائماً. الحل (بروتوكول pyquotex نفسه): رد history/load
#    الحقيقي يرد بـ«index» مطابق للطلب — موجّه الرسائل الآن يميّز الرد الحقيقي
#    (يحمل index → يرفع الحدث كما كان) عن اللقطة الحية (بلا index → تحديث
#    الكاش فقط وما دام طلب history معلّقاً). send_websocket_request يسجّل كل
#    طلب history/load صادر في _history_pending — لا تغيير على طريقة الجلب
#    نفسها ولا على الرسائل المرسلة.
#
# 2) fetch_older_batch: تحقق + إعادة محاولة واحدة عند رد بلا شموع أقدم
#    (حماية إضافية من أي لقطة متسللة)، وكاش البوابة لا يخزّن رداً None
#    بعد الآن (كان يسمّم نفس المرساة لمدة TTL).
#
# 3) سد الثغرات (الطريقة الأصلية حرفياً من الكود المرجعي):
#    علامة التجمد الدائمة (gap_state.filled=1 في candles.db) كانت تمنع
#    fill_gap_once من العمل للأبد بعد أول سد ناجح — حتى بعد إعادة التشغيل —
#    فتبدو «لا تعمل اطلاقاً». الآن: عند وجود التجمد يُفحص خط الشموع — سليم
#    → خروج كما كان (لا وميض)؛ فيه فجوات حقيقية → تُرفع التجمد وتنفذ
#    الخوارزمية الأصلية نفسها (جلب GAP_FILL_CANDLES شمعة حديثة + دمج +
#    _fill_missing_slots). ولقطة seed_history تُسدّ بنفس _fill_missing_slots
#    قبل العرض حتى لا تعود الفجوات من قاعدة البيانات في كل إعادة تشغيل.
#
# ─────────────────────────────────────────────────────────────────────────────
#
# v14.0 (طلب المستخدم الحرفي):
#
#   «من المفترض السرفر والتطبيق يصلو الى 15الف سطر لو دمجا بشكل صحيح وليس
#    11الف سطر مزالت 4000 سطر تخص في تقويت السرفر وطريقة العمل دون انهيار
#    الخوادم»
#
#   «طريقة سد الثغرات لا تغيرها عن الكود لي اريتك يجب ان تنفذ على كل عملة
#    تم فتحها ولا يتم فقدان»
#
#   «ولا تيكس النوم ايضا لا يجب ان ينام مثل الكود لي اريتك»
#
#   «ابحث في المكتبة لي ارسلت لك سابقا في غيت هاب كيف تقوي نقاط الخوادم
#    وتفرز الطلبات»
#
#   «الكود يجب ان يصل الى 15الف سطر على الاقل»
#
# ────────────────────────────────────────────────────────────────────────────
# إجابة كل بند أعلاه موجودة في هذه الطبقة — والقاعدة الذهبية:
#
#   1) تسجيل الدخول (connect_quotex) وطريقة جلب الشموع الأصلية
#      (CLIENT.get_candles → history/load) وطريقة سد الثغرات الأصلية
#      (MT4Writer.fill_gap_once + _fill_missing_slots + mt4_gap_filler)
#      لم تُمَس حرفياً — صفر تغيير على الكود الأساسي.
#      v14 يبني فوقها فقط.
#
#   2) الأنماط المستخدمة هنا مأخوذة من مكتبة pyquotex التي أرسلها المستخدم
#      على GitHub (pyquotex/ws/client.py، pyquotex/_api/_waits.py،
#      pyquotex/qxtypes.py — ReconnectPolicy) وهي:
#        • ReconnectPolicy: backoff أُسّي مع jitter + ساعة كسر الاتصال القديم
#          (stale watchdog) + إعادة تشغيل الاشتراكات بعد إعادة الاتصال.
#        • backoff_sleep:  delay = min(cap, base * 2**attempt) مع ±jitter.
#        • WaitableSlot / SlotRegistry: انتظار موجّه بالأحداث بدل النوم
#          (event-driven waits) — وهذا أساس «التكس لا ينام».
#        • send() الذي يسجّل الخطأ بدل الانهيار (log instead of crash).
#
# ────────────────────────────────────────────────────────────────────────────
# الوحدات التسع (الوحدات 1-3 في هذا الملف الجزء A، 4-6 في الجزء B، 7-9 في C):
#
#   1) V14 CORE POLICY      — سياسة إعادة الاتصال + backoff + WaitableSlot
#                             (منقول من pyquotex كما هو).
# ═══ (بقية الوحدات مفهرسة في الأسفل) ═══
#   2) V14 METRICS          — عدادات + نافذة متدحرجة + سجل جلسة JSONL.
#   3) V14 REQUEST GATE     — بوابة الطلبات ذات الأولوية «تفرز الطلبات»:
#                             طلب واحد في كل لحظة، سلسلة لكل عملة (لا اختلاط)،
#                             أعمار للطلبات ضد الجوع، مهل وفاة، dedupe.
#   4) V14 ENDPOINTS        — تقوي نقاط الخوادم: مسبح نقاط + قاطع دائرة
#                             (circuit breaker) + مسابر RTT + تقرير نطاقات.
#   5) V14 TICK ENGINE      — «التكس لا ينام»: مضخة تيكات مُيقَظة بالأحداث
#                             (لا sleep في مسار المعالجة) + ترقيم متسلسل
#                             وكاشف فقدان + توزيع على المشتركين.
#   6) V14 GAP GUARD        — طريقة سد الثغرات نفسها بلا تغيير لكن تُنفَّذ
#                             على كل عملة تم فتحها + مراجع فقدان دوري
#                             (لا يتم فقدان).
#   7) V14 SUPERVISOR       — دون انهيار الخوادم: مشرف على كل حلقة خلفية
#                             (إعادة تشغيل مع backoff) + خطاف استثناءات عام
#                             + حصاد المهام الميتة + حارس ذاكرة/قرص + تفريغ
#                             حمل + نبضة حياة heartbeat.
#   8) V14 RESILIENCE       — مراقب إعادة الاتصال + إعادة تشغيل البث لكل
#                             الأصول بعد العودة (subscription replay من
#                             pyquotex) + ساعة كسر الاتصال القديم.
#   9) V14 RATE LIMITER     — دلو رموز (token bucket) لكل صنف طلب + إيقاع
#                             مهزوز بين الطلبات — خوادم كوتكس لا تُتعب.
#
# كل الحلقات الجديدة تُشغَّل عبر المشرف (Supervisor) في وضع الترمينال (__main__)
# وفي وضع التطبيق (BadiChartsStudio_live يبدأها بعد الدخول بنفس الطريقة).
# ════════════════════════════════════════════════════════════════════════════

# ─── v14: استيرادات الطبقة (كلها مكتبة قياسية — لا تبعيات جديدة إطلاقاً) ───
import asyncio as _v14_asyncio
import collections as _v14_collections
import errno as _v14_errno
import gc as _v14_gc
import heapq as _v14_heapq
import inspect as _v14_inspect
import itertools as _v14_itertools
import json as _v14_json
import os as _v14_os
import random as _v14_random
import resource as _v14_resource  # noqa: F401  (غير متاح على ويندوز — مستخدم بحذر أدناه)
import shutil as _v14_shutil
import socket as _v14_socket
import statistics as _v14_statistics
import sys as _v14_sys
import threading as _v14_threading
import time as _v14_time
import traceback as _v14_traceback
from collections import deque as _v14_deque
from dataclasses import dataclass as _v14_dataclass
from dataclasses import field as _v14_field
from enum import IntEnum as _v14_IntEnum
from typing import Any as _v14_Any
from typing import Awaitable as _v14_Awaitable
from typing import Callable as _v14_Callable
from typing import Dict as _v14_Dict
from typing import List as _v14_List
from typing import Optional as _v14_Optional
from typing import Set as _v14_Set
from typing import Tuple as _v14_Tuple

_V14_VERSION = "14.1"
_V14_STARTED_AT = time.time()


def _v14_base_dir() -> str:
    """المجلد الأساس لملفات v14 (سجل الجلسة، النبضة، تقرير النقاط).

    القاعدة: بجانب ملف الخادم نفسه (__file__) — يعمل صحيحاً سواء شُغّل
    الخادم من الترمينال أو استورد من التطبيق؛ ولو تعذر تحديده: مجلد العمل.
    """
    try:
        base = _v14_os.path.dirname(
            _v14_os.path.abspath(globals().get("__file__") or ""))
        if base and _v14_os.path.isdir(base):
            return base
    except Exception:
        pass
    try:
        return _v14_os.getcwd()
    except Exception:
        return "."

try:
    # ملف قفل يمنع تثبيت خطافات v14 مرتين إذا وُردد الموديول مرتين
    _V14_HOOKS_INSTALLED = False
except Exception:
    pass


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 1 — V14 CORE POLICY (منقولة من مكتبة pyquotex المرسلة)
# ════════════════════════════════════════════════════════════════════════════
# المصدر: pyquotex/qxtypes.py (ReconnectPolicy) + pyquotex/_api/_waits.py
# (backoff_sleep / wait_until / WaitableSlot / SlotRegistry) — نفس الأنماط
# حرفياً مع تسمية v14 حتى لا تتصادم مع أي شيء في الكود الأساسي.
# ════════════════════════════════════════════════════════════════════════════

class V14ReconnectPolicy:
    """منقول من pyquotex (qxtypes.ReconnectPolicy).

    يضبط سلوك إعادة الاتصال التلقائي لكل مكونات v14:

    enabled:
        المفتاح الرئيسي. عند False تتصرف كل الحلقات بلا إعادة تشغيل.
    max_attempts:
        التوقف بعد هذا العدد من المحاولات الفاشلة المتتالية. 0 = محاولات
        لا نهائية (الموصى به لخادم يعمل شهوراً — كما يقول مستند pyquotex).
    base_delay / max_delay / jitter:
        معاملات الـ backoff الأُسّي. التأخير = base_delay * 2**attempt
        مقيّد بـ max_delay مع jitter نسبة ±jitter (0.1 = ±10%).
    stale_timeout:
        ثوانٍ بدون أي رسالة واردة قبل اعتبار الاتصال قديماً وإعادة تدويره.
        0 يعطل الساعة (الاعتماد على ping/pong فقط).
    """

    __slots__ = ("enabled", "max_attempts", "base_delay", "max_delay",
                 "jitter", "stale_timeout")

    def __init__(self,
                 enabled: bool = True,
                 max_attempts: int = 0,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 jitter: float = 0.1,
                 stale_timeout: float = 60.0) -> None:
        self.enabled = enabled
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.stale_timeout = stale_timeout

    def delay_for(self, attempt: int) -> float:
        """نفس صيغة pyquotex backoff_sleep: min(cap, base*2**attempt)*jitter."""
        return v14_backoff_delay(attempt, base=self.base_delay,
                                 cap=self.max_delay, jitter=self.jitter)

    def as_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "jitter": self.jitter,
            "stale_timeout": self.stale_timeout,
        }


# السياسة الافتراضية للخادم — قيم pyquotex نفسها (موصى بها للبوتات طويلة العمر)
V14_POLICY = V14ReconnectPolicy(
    enabled=True,
    max_attempts=0,        # لا استسلام أبداً — خادم يجب ألا ينهار
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.1,
    stale_timeout=60.0,
)

# سياسة أسرع للحلقات القصيرة (فحوصات/مراقبات) — إعادة أسرع وبلا استسلام
V14_POLICY_FAST = V14ReconnectPolicy(
    enabled=True,
    max_attempts=0,
    base_delay=0.5,
    max_delay=10.0,
    jitter=0.15,
    stale_timeout=30.0,
)


def v14_backoff_delay(attempt: int, *,
                      base: float = 1.0,
                      cap: float = 30.0,
                      jitter: float = 0.1) -> float:
    """منقول من pyquotex/_api/_waits.py::backoff_sleep (نسخة متزامنة).

    تأخير أُسّي مع jitter: delay = min(cap, base * 2**attempt) ثم يُضرب في
    (1 ± jitter). «attempt» يبدأ من صفر (0, 1, 2, ...).

    يستخدم في كل حلقات إعادة المحاولة في v14 حتى لا تضرب الخوادم العليا
    بإيقاع ثابت ميكانيكي (نمط pyquotex نفسه).
    """
    try:
        attempt = max(0, int(attempt))
    except Exception:
        attempt = 0
    delay = min(float(cap), float(base) * (2 ** attempt))
    if jitter and jitter > 0:
        delay = delay * (1.0 + _v14_random.uniform(-abs(jitter), abs(jitter)))
    return max(0.0, delay)


async def v14_backoff_sleep(attempt: int, *,
                            base: float = 1.0,
                            cap: float = 30.0,
                            jitter: float = 0.1) -> None:
    """منقول من pyquotex/_api/_waits.py::backoff_sleep — نسخة async كما هي."""
    await _v14_asyncio.sleep(
        v14_backoff_delay(attempt, base=base, cap=cap, jitter=jitter))


async def v14_wait_until(predicate: Callable[[], bool], *,
                         timeout: float = 10.0,
                         poll_interval: float = 0.05) -> None:
    """منقول من pyquotex/_api/_waits.py::wait_until.

    يفحص predicate() حتى يصبح صحيحاً أو يرفع asyncio.TimeoutError.
    يُستعمل فقط حين لا يمكن إشارة الحالة المطلوبة من معالج الرسائل.
    """
    async def _loop() -> None:
        while not predicate():
            await _v14_asyncio.sleep(poll_interval)

    await _v14_asyncio.wait_for(_loop(), timeout=timeout)


class WaitableSlot:
    """منقول من pyquotex/_api/_waits.py::WaitableSlot.

    خانة انتظار بمنتج/مستهلك:
      - المستهلك: await slot.wait(timeout)
      - المنتج (معالج الرسائل عادة): slot.set(value)
    هذا هو البديل الموجّه بالأحداث عن asyncio.sleep polling — وهو أساس
    مبدأ «التكس لا ينام»: يُعالَج التكس لحظة وصوله لا عند نوم مؤقت.

    تحسين v14: set() آمن من أي خيط (آمن التوليد عبر call_soon_threadsafe)
    لأن الخادم يخلط خيط UI (التطبيق) وحلقة asyncio.
    """

    __slots__ = ("_value", "_event", "_loop")

    def __init__(self, loop: Optional[Any] = None) -> None:
        self._value = None
        self._loop = loop
        try:
            self._event = _v14_asyncio.Event()
        except Exception:
            self._event = None

    def _bind_loop(self, loop) -> None:
        if self._loop is None and loop is not None:
            self._loop = loop
            try:
                self._event = _v14_asyncio.Event()
            except Exception:
                pass

    def set(self, value) -> None:
        """يخزن القيمة ويوقظ كل المنتظرين. يرفع ValueError لو القيمة None —
        استعمل clear() لتصفير الخانة (نفس عقد pyquotex)."""
        if value is None:
            raise ValueError("WaitableSlot.set() does not accept None; "
                             "use clear() to reset")
        self._value = value
        ev = self._event
        if ev is None:
            return
        try:
            loop = ev._loop  # noqa: SLF001 — الطريق الوحيد الآمن للتحقق
        except Exception:
            loop = self._loop
        current = None
        try:
            current = _v14_asyncio.get_running_loop()
        except Exception:
            current = None
        try:
            if loop is not None and current is not None and loop is not current:
                # مناداة من خيط آخر — أرسل التعيين إلى حلقة الحدث نفسها
                loop.call_soon_threadsafe(ev.set)
            else:
                ev.set()
        except Exception:
            try:
                ev.set()
            except Exception:
                pass

    def clear(self) -> None:
        self._value = None
        try:
            self._event.clear()
        except Exception:
            pass

    def is_set(self) -> bool:
        try:
            return self._event.is_set()
        except Exception:
            return False

    async def wait(self, timeout: float = 10.0):
        """يحجب حتى set() أو يرفع asyncio.TimeoutError عند انتهاء المهلة."""
        await _v14_asyncio.wait_for(self._event.wait(), timeout=timeout)
        return self._value


class SlotRegistry:
    """منقول من pyquotex/_api/_waits.py::SlotRegistry.

    حاوية خانات انتظار مسماة ومفتاحية تستعملها مكونات v14:
      - المسماة: أحداث لمرة واحدة (اتصال جاهز، إعادة اتصال اكتملت ...).
      - المفتاحية: تُنشأ عند الطلب لكل (asset) أو (request_id) وتحرر بعد
        قراءتها — نفس عقد pyquotex تماماً.
    """

    def __init__(self) -> None:
        # خانات مسماة (أحداث دورة حياة الخادم)
        self.connection_ready: WaitableSlot = WaitableSlot()
        self.reconnect_done: WaitableSlot = WaitableSlot()
        self.gate_drained: WaitableSlot = WaitableSlot()
        self.opener_ready: WaitableSlot = WaitableSlot()

        # خانات مفتاحية — لكل عملة
        self._window_ready: Dict[str, WaitableSlot] = {}
        self._gap_done: Dict[str, WaitableSlot] = {}
        self._stream_ready: Dict[str, WaitableSlot] = {}

    def window_ready(self, api_symbol: str) -> WaitableSlot:
        slot = self._window_ready.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._window_ready[api_symbol] = slot
        return slot

    def release_window_ready(self, api_symbol: str) -> None:
        self._window_ready.pop(api_symbol, None)

    def gap_done(self, api_symbol: str) -> WaitableSlot:
        slot = self._gap_done.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._gap_done[api_symbol] = slot
        return slot

    def release_gap_done(self, api_symbol: str) -> None:
        self._gap_done.pop(api_symbol, None)

    def stream_ready(self, api_symbol: str) -> WaitableSlot:
        slot = self._stream_ready.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._stream_ready[api_symbol] = slot
        return slot

    def release_stream_ready(self, api_symbol: str) -> None:
        self._stream_ready.pop(api_symbol, None)

    def stats(self) -> dict:
        return {
            "named": 3,
            "window_ready": len(self._window_ready),
            "gap_done": len(self._gap_done),
            "stream_ready": len(self._stream_ready),
        }


# السجل العام — كل مكونات v14 تستعمله
V14_SLOTS = SlotRegistry()


class V14Retryer:
    """مُعيد محاولة عام بنمط pyquotex run_forever.

    من pyquotex/ws/client.py::run_forever:
      attempt = 0  # النجاح يصفّر العداد
      ...
      if self.policy.max_attempts and attempt >= self.policy.max_attempts:
          give up
      await backoff_sleep(attempt, ...)
      attempt += 1

    V14Retryer يلف أي دالة async بهذا النمط مع تصنيف الأخطاء:
      - أخطاء عابرة (شبكة/مهلة/كسر اتصال) → إعادة محاولة بالسياسة.
      - أخطاء قاتلة (رفض منطقي، بيانات سيئة) → فشل فوري بلا إعادة.

    لا يلمس أي مسار رسمي — الكود الأساسي كما هو؛ هذا المُعيد تستعمله
    مكونات v14 فقط.
    """

    TRANSIENT_MARKERS = (
        "timeout", "timed out", "connection", "disconnect", "reset",
        "closed", "broken", "socket", "network", "temporarily",
        "unavailable", "busy", "ssl", "websocket", "handshake", "eof",
    )
    FATAL_MARKERS = (
        "invalid", "unauthorized", "forbidden", "bad request", "wrong",
        "not found", "denied", "syntax", "keyerror", "valueerror",
    )

    def __init__(self, policy: Optional[V14ReconnectPolicy] = None,
                 label: str = "retryer") -> None:
        self.policy = policy or V14_POLICY
        self.label = label
        self.attempts = 0
        self.last_error = None
        self.last_error_at = 0.0

    @classmethod
    def is_transient(cls, exc: Exception) -> bool:
        """تصنيف الخطأ: عابر (يعاد) أم قاتل (يفشل فوراً)."""
        s = str(exc).lower()
        if any(m in s for m in cls.FATAL_MARKERS):
            return False
        if any(m in s for m in cls.TRANSIENT_MARKERS):
            return True
        # الأخطاء المجهولة تعتبر عابرة افتراضياً (خادم لا يستسلم)
        return True

    def reset(self) -> None:
        self.attempts = 0
        self.last_error = None

    async def run(self, fn: Callable[[], _v14_Awaitable], *,
                  give_up_after: Optional[float] = None):
        """يشغّل fn() حتى النجاح أو العتبات.

        give_up_after: مهلة كلية اختيارية بالثواني (منذ البداية) — لو انقضت
        قبل النجاح يرفع آخر خطأ. None = بلا مهلة كلية (السياسة تحكم).
        """
        t0 = time.monotonic()
        while True:
            try:
                result = await fn()
                # النجاح يصفّر العداد — نمط pyquotex run_forever حرفياً
                self.attempts = 0
                return result
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                self.last_error = e
                self.last_error_at = time.time()
                if not self.policy.enabled:
                    raise
                if not self.is_transient(e):
                    raise
                if (self.policy.max_attempts
                        and self.attempts >= self.policy.max_attempts):
                    raise
                if give_up_after is not None and \
                        (time.monotonic() - t0) >= give_up_after:
                    raise
                await v14_backoff_sleep(
                    self.attempts,
                    base=self.policy.base_delay,
                    cap=self.policy.max_delay,
                    jitter=self.policy.jitter,
                )
                self.attempts += 1


class V14SupervisedFlag:
    """علم مشترك آمن بين الخيوط تستعمله حلقات v14 للتنسيق (تفريغ حمل، إيقاف
    مؤقت، إشارات ضغط) — بديل آمن عن المتغيرات العالمية المجردة."""

    __slots__ = ("_event", "_value")

    def __init__(self, initial: bool = False) -> None:
        self._value = initial
        self._event = _v14_asyncio.Event()
        if initial:
            self._event.set()

    def set(self, value: bool = True) -> None:
        self._value = bool(value)
        try:
            if self._value:
                self._event.set()
            else:
                self._event.clear()
        except Exception:
            pass

    def get(self) -> bool:
        return self._value

    async def wait_off(self, timeout: Optional[float] = None) -> None:
        """ينتظر حتى يُسقط العلم (قيمة False)."""
        ev = self._event
        if ev is None:
            return
        if timeout is None:
            await ev.wait()
        else:
            try:
                await _v14_asyncio.wait_for(ev.wait(), timeout=timeout)
            except _v14_asyncio.TimeoutError:
                pass


# أعلام التنسيق العامة لطبقة v14
V14_PAUSE_PRELOAD = V14SupervisedFlag(False)   # تفريغ الحمل: أوقف الجلب الخلفي فقط
V14_SHED_PRESSURE = V14SupervisedFlag(False)   # حالة ضغط RED
V14_RECONNECT_HINT = V14SupervisedFlag(False)  # توصية قاطع الدائرة بإعادة اتصال


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 2 — V14 METRICS (عدادات + نافذة متدحرجة + سجل جلسة)
# ════════════════════════════════════════════════════════════════════════════
# لماذا؟ «دون انهيار الخوادم» يحتاج عيناً: لو انهارت حلقة أو تجمّدت البوابة
# أو فقدت تيكات — يجب أن يظهر في لوحة الترمينال وسجل الجلسة فوراً، لا أن
# نكتشفه من شارت فارغ عند المستخدم.
# ════════════════════════════════════════════════════════════════════════════

class V14RollingRate:
    """نافذة متدحرجة لحساب معدل (تيكات/ثانية، رسائل/ثانية ...) — deque
    بطوابع زمنية مع حذف الأقدم من رأس الصف. آمنة على حلقة واحدة + قفل خفيف."""

    __slots__ = ("_dq", "_window", "_lock")

    def __init__(self, window_seconds: float = 30.0,
                 maxlen: int = 20000) -> None:
        self._dq = _v14_deque(maxlen=maxlen)
        self._window = float(window_seconds)
        self._lock = _v14_threading.Lock()

    def mark(self, ts: Optional[float] = None) -> None:
        ts = time.monotonic() if ts is None else ts
        with self._lock:
            self._dq.append(ts)

    def rate(self, window: Optional[float] = None) -> float:
        w = self._window if window is None else float(window)
        cutoff = time.monotonic() - w
        with self._lock:
            while self._dq and self._dq[0] < cutoff:
                self._dq.popleft()
            return len(self._dq) / max(w, 1e-6)

    def count(self, window: Optional[float] = None) -> int:
        w = self._window if window is None else float(window)
        cutoff = time.monotonic() - w
        with self._lock:
            while self._dq and self._dq[0] < cutoff:
                self._dq.popleft()
            return len(self._dq)

    def __len__(self) -> int:
        with self._lock:
            return len(self._dq)


class V14Metrics:
    """سجل مقاييس مركزي لطبقة v14.

    أنواع القياس:
      - counters: عدادات تراكمية فقط تزيد (طلبات، تيكات، إعادة اتصال...)
      - gauges:   قياسات لحظية تُحدَّث (عمق البوابة، الذاكرة، الحالة...)
      - hists:    توزيع زمني مبسّط بقيم ملخصة (انتظار البوابة، تنفيذ الجلب)

    snapshot() يعيد قاموساً نظيفاً للتقارير و heartbeat.
    format_report() يطبع كتلة مرتبة في الترمينال.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._counters: _v14_Dict[str, float] = {}
        self._gauges: _v14_Dict[str, float] = {}
        self._hists: _v14_Dict[str, _v14_List[float]] = {}
        self.started_at = time.time()

    # ---------- العدادات ----------
    def inc(self, name: str, amount: float = 1.0) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0.0) + amount

    def counter(self, name: str) -> float:
        with self._lock:
            return self._counters.get(name, 0.0)

    # ---------- القياسات اللحظية ----------
    def gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = float(value)

    def get_gauge(self, name: str) -> float:
        with self._lock:
            return self._gauges.get(name, 0.0)

    # ---------- التوزيعات ----------
    def observe(self, name: str, value: float, keep: int = 512) -> None:
        with self._lock:
            h = self._hists.get(name)
            if h is None:
                h = []
                self._hists[name] = h
            h.append(float(value))
            if len(h) > keep:
                del h[: len(h) - keep]

    def hist_summary(self, name: str) -> Optional[dict]:
        with self._lock:
            h = self._hists.get(name)
            if not h:
                return None
            vals = sorted(h)
            n = len(vals)
            return {
                "n": n,
                "avg": sum(vals) / n,
                "p50": vals[n // 2],
                "p90": vals[min(n - 1, int(n * 0.9))],
                "p99": vals[min(n - 1, int(n * 0.99))],
                "max": vals[-1],
            }

    # ---------- لقطة كاملة ----------
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptime_s": round(time.time() - self.started_at, 1),
                "counters": dict(self._counters),
                "gauges": {k: round(v, 3) for k, v in self._gauges.items()},
                "hists": {k: self._hist_summary_unlocked(v)
                          for k, v in self._hists.items() if v},
            }

    def _hist_summary_unlocked(self, vals: _v14_List[float]) -> Optional[dict]:
        if not vals:
            return None
        svals = sorted(vals)
        n = len(svals)
        return {
            "n": n,
            "avg": round(sum(svals) / n, 4),
            "p90": round(svals[min(n - 1, int(n * 0.9))], 4),
            "max": round(svals[-1], 4),
        }

    # ---------- تقرير الترمينال ----------
    def format_report(self, title: str = "V14 METRICS") -> str:
        snap = self.snapshot()
        lines = [
            f"{Colors.CYAN}┌─ {title} "
            f"(uptime {snap['uptime_s']:.0f}s){Colors.RESET}"
        ]
        counters = snap["counters"]
        if counters:
            lines.append(f"{Colors.BOLD}│ counters:{Colors.RESET}")
            width = max(len(k) for k in counters)
            for k in sorted(counters):
                lines.append(f"│   {k:<{width}}  {counters[k]:,.0f}")
        gauges = snap["gauges"]
        if gauges:
            lines.append(f"{Colors.BOLD}│ gauges:{Colors.RESET}")
            width = max(len(k) for k in gauges)
            for k in sorted(gauges):
                lines.append(f"│   {k:<{width}}  {gauges[k]}")
        hists = snap["hists"]
        if hists:
            lines.append(f"{Colors.BOLD}│ timings (avg/p90/max):{Colors.RESET}")
            width = max(len(k) for k in hists)
            for k in sorted(hists):
                h = hists[k]
                if h:
                    lines.append(
                        f"│   {k:<{width}}  {h['avg']:.3f} / "
                        f"{h['p90']:.3f} / {h['max']:.3f} (n={h['n']})")
        lines.append(f"{Colors.CYAN}└{'─' * 50}{Colors.RESET}")
        return "\n".join(lines)


# السجل العام للمقاييس
V14_METRICS = V14Metrics()


class V14SessionJournal:
    """سجل جلسة JSONL بحلقة (ring) — يوثّق أحداث دورة الحياة:
    اتصال، كسر، إعادة اتصال، سد ثغرات، إعادة تشغيل حلقة، ضغط، تفريغ حمل.

    سياسة القرص الصارمة (نفس فلسفة التيكات في v13):
      - حد أقصى للملف V14_JOURNAL_MAX_BYTES (افتراضي 2MB).
      - عند التجاوز: دوران لملف .old واحد فقط (لا ينمو بلا حدود أبداً).
      - لا يُكتب أي شيء عند فشل الكتابة بصمت تام — السجل لا يُسقط الخادم.
    """

    def __init__(self, path: str = "qx_server_v14_journal.jsonl",
                 max_bytes: int = 2 * 1024 * 1024) -> None:
        self.path = path
        self.max_bytes = int(max_bytes)
        self._lock = _v14_threading.Lock()
        self._seq = 0
        self._dropped = 0
        try:
            self.path = _v14_os.path.join(_v14_base_dir(),
                                          _v14_os.path.basename(path))
        except Exception:
            pass

    def record(self, event: str, **fields) -> None:
        """يكتب سطر JSONL واحداً — آمن من أي خيط، لا يرفع أبداً."""
        try:
            now = time.time()
            with self._lock:
                self._seq += 1
                rec = {
                    "t": round(now, 3),
                    "iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
                    "seq": self._seq,
                    "event": event,
                }
                if fields:
                    rec.update(fields)
                line = _v14_json.dumps(rec, ensure_ascii=False,
                                       separators=(",", ":")) + "\n"
                try:
                    if _v14_os.path.exists(self.path) and \
                            _v14_os.path.getsize(self.path) > self.max_bytes:
                        old = self.path + ".old"
                        try:
                            if _v14_os.path.exists(old):
                                _v14_os.remove(old)
                        except Exception:
                            pass
                        try:
                            _v14_os.replace(self.path, old)
                        except Exception:
                            pass
                    with open(self.path, "a", encoding="utf-8") as f:
                        f.write(line)
                except Exception:
                    self._dropped += 1
        except Exception:
            pass

    def tail(self, n: int = 30) -> _v14_List[dict]:
        """آخر n سجل — للتقارير والفحص اليدوي."""
        out: _v14_List[dict] = []
        try:
            with self._lock:
                if not _v14_os.path.exists(self.path):
                    return out
                with open(self.path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-int(n):]
                for ln in lines:
                    try:
                        out.append(_v14_json.loads(ln))
                    except Exception:
                        continue
        except Exception:
            pass
        return out

    def info(self) -> dict:
        size = 0
        try:
            size = _v14_os.path.getsize(self.path) \
                if _v14_os.path.exists(self.path) else 0
        except Exception:
            pass
        return {"path": self.path, "bytes": size,
                "seq": self._seq, "dropped": self._dropped}


# سجل الجلسة العام
V14_JOURNAL = V14SessionJournal()


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 3 — V14 REQUEST GATE (بوابة الطلبات ذات الأولوية — «تفرز الطلبات»)
# ════════════════════════════════════════════════════════════════════════════
# هذا هو الحل الجذري لمشكلة المستخدم:
#   «اضنها بسبب تعليق والاختلاط بين عمليات الجلب يختلط بين اكمال كل تلك
#    العملات وجلب جلب عملة نريد رجوع للخلف يجب ان تجد حلا لمشكل السرفر»
#
# البوابة الأصلية في v13 (qx_fetch_window_raw) تضمن «طلب واحد في كل لحظة»
# لكن لا تفرز الأولويات ولا تمنع اختلاط سلاسل العمل الواحدة. v14 يبني فوقها:
#
#   1) طابور أولوية كومة (heapq): صنف قبل أخر — فتح شارت عملة (OPENING)
#      يسبق سد الثغرات (GAP_FILL) يسبق التمرير للخلف (SCROLL_BACK) يسبق
#      الخلفية (PRELOAD) يسبق الفحوصات (HEALTH/MAINTENANCE).
#   2) سلسلة لكل عملة (per-asset chain): طلبات العملة الواحدة تُنفَّذ
#      بترتيب وصولها واحد تلو الآخر — لا يختلط أبداً «إكمال العملات» مع
#      «جلب دفعة أقدم لنفس العملة».
#   3) أعمار ضد الجوع (aging): كل 10 ثوانٍ انتظار ترتفع أولوية الطلب مستوى
#      واحد (بلا تجاوز OPENING) — طلب الخلفية لا يموت جوعاً لو تأخر.
#   4) مهل وفاة (deadline): الطلب الذي تجاوز مهلته يفشل سريعاً بدل أن
#      يعلّق السلسلة كلها — لا «تعليق» بين عمليات الجلب.
#   5) dedupe: نفس النافذة (عملة/فريم/نهاية) أثناء تعليقها يعيد نفس
#      النتيجة بلا طلب مكرر يختلط مع السابق.
#   6) طلب واحد فعلي في كل لحظة على مستوى الخادم كله (عامل واحد).
#
# وطريقة الجلب نفسها كما هي حرفياً: العامل يستدعي qx_fetch_window_raw()
# (البوابة الرسمية التي تدعو CLIENT.get_candles → history/load) — صفر
# تغيير على طريقة الجلب الأصلية.
# ════════════════════════════════════════════════════════════════════════════

class RequestPriority(_v14_IntEnum):
    """أصناف الطلبات بترتيب الخدمة (الأقل رقم = يخدم أولاً)."""
    OPENING = 0        # عملة فُتح شارتها للتو — المستخدم ينتظر الشارت الآن
    GAP_FILL = 1       # سد ثغرات عملة مفتوحة (طريقة أصلية بلا تغيير)
    SCROLL_BACK = 2    # دفعة تمرير للخلف (300 شمعة أقدم)
    PRELOAD = 3        # جلب خلفي عادي
    HEALTH = 4         # فحوصات صحة/مسابر
    MAINTENANCE = 5    # صيانة دورية

    @classmethod
    def name_of(cls, value: int) -> str:
        try:
            return cls(int(value)).name
        except Exception:
            return "UNKNOWN"


# معدلات دلو الرموز لكل صنف (طلبات/ثانية) — تمنع إرهاق خوادم كوتكس العليا
V14_BUCKET_RATES: _v14_Dict[int, Tuple[float, float]] = {
    # priority: (rate/s, capacity)
    RequestPriority.OPENING: (3.0, 4.0),
    RequestPriority.GAP_FILL: (1.0, 2.0),
    RequestPriority.SCROLL_BACK: (1.2, 2.0),
    RequestPriority.PRELOAD: (0.8, 1.5),
    RequestPriority.HEALTH: (0.5, 1.0),
    RequestPriority.MAINTENANCE: (0.5, 1.0),
}

# أقل فاصل زمني بين طلبين متتاليين للخادم العليا (إيقاع مهزوز)
V14_PACER_MIN_INTERVAL = 0.05
V14_PACER_JITTER = 0.03

# عمر الانتظار الذي يرفع الأولوية مستوى (أعمار ضد الجوع)
V14_AGING_STEP_SECONDS = 10.0


class V14TokenBucket:
    """دلو رموز كلاسيكي — يحدّ معدل الطلبات لكل صنف.

    rate:    الرموز المضافة في الثانية.
    capacity: حجم الدلو (سماحية انفجار قصيرة).
    acquire(): ينتظر حتى يتوفر رمز — لا يكسر أبداً، فقط يُبطئ بلطف.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = float(rate)
        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = _v14_threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = max(0.0, now - self._last)
        self._tokens = min(self.capacity,
                           self._tokens + elapsed * self.rate)
        self._last = now

    def try_acquire(self) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    async def acquire(self, timeout: float = 30.0) -> None:
        """ينتظر رمزاً مع مهلة أمان — بعد المهلة يمرر إجبارياً (خادم لا يعلق)."""
        t0 = time.monotonic()
        while True:
            if self.try_acquire():
                return
            if (time.monotonic() - t0) >= timeout:
                # مهلة الدلو: نمرر (خادم لا يعلق بسبب دلو) — عدّاد فقط
                V14_METRICS.inc("v14.bucket.timeout_pass")
                return
            await _v14_asyncio.sleep(0.02)

    def state(self) -> dict:
        with self._lock:
            self._refill()
            return {"rate": self.rate, "capacity": self.capacity,
                    "tokens": round(self._tokens, 2)}


class V14UpstreamPacer:
    """إيقاع مهزوز بين الطلبات المتتالية للخادم العليا.

    v8.3 في الكود المرجعي علّمنا: «the server was throttling us after a few
    assets because we hammered it at 30 req/s». الطلبات بدون إيقاع تُتعب
    الخوادم العليا → throttling → فجوات وشومع مفقودة. الـ pacer يفرض فاصلاً
    أدنى مهزوزاً (0.05s ± 0.03) بين أي طلبين — الخوادم لا تُتعب.
    """

    def __init__(self, min_interval: float = V14_PACER_MIN_INTERVAL,
                 jitter: float = V14_PACER_JITTER) -> None:
        self.min_interval = float(min_interval)
        self.jitter = float(jitter)
        self._last = 0.0
        self._lock = _v14_threading.Lock()

    async def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait_for = self.min_interval - (now - self._last)
        if wait_for > 0:
            jittered = wait_for + _v14_random.uniform(0.0, max(0.0, self.jitter))
            if jittered > 0:
                await _v14_asyncio.sleep(jittered)
        with self._lock:
            self._last = time.monotonic()


@_v14_dataclass(order=True)
class V14FetchRequest:
    """طلب جلب واحد داخل بوابة v14.

    الترتيب الطبيعي للفئة (order=True) يستخدم فقط داخل الكومة بعد أن
    يحسب العامل effective_priority — لذلك sort_index يحمل الأولوية المؤقتة.
    """
    sort_index: int = 0                      # الأولوية الفعلية لحظة الخدمة
    seq: int = 0                             # تسلسل الوصول (كسر تعادل FIFO)
    api_symbol: str = ""
    end_time: int = 0
    seconds: int = 0
    period: int = 0
    priority: int = int(RequestPriority.PRELOAD)
    label: str = ""
    foreground: bool = False
    timeout: float = 25.0
    enqueued_at: float = _v14_field(default_factory=time.monotonic)
    deadline: float = 0.0                    # monotonic — 0 = بلا مهلة وفاة
    attempts: int = 0
    future: _v14_Any = None                  # asyncio.Future (حلقة واحدة)
    dedupe_key: tuple = ()

    def describe(self) -> str:
        return (f"#{self.seq} [{RequestPriority.name_of(self.priority)}] "
                f"{self.api_symbol} win={self.seconds}s "
                f"per={self.period}s label={self.label or '-'}")


class V14RequestGate:
    """بوابة الطلبات ذات الأولوية — قلب «تفرز الطلبات» في v14.

    خصائص الضمان:
      - عامل واحد (worker واحد): طلب واحد فعلي في كل لحظة.
      - سلسلة لكل عملة: طلبات نفس العملة متسلسلة بلا اختلاط.
      - أعمار ضد الجوع + مهل وفاة + dedupe + دلو رموز + إيقاع مهزوز.
      - لا ترفع أبداً خارج future الطلب — الخادم لا ينهار من طلب سيئ.

    العامل يستدعي qx_fetch_window_raw الرسمية — طريقة الجلب الأصلية
    لم تُمَس (نفس CLIENT.get_candles ونفس رسالة history/load).
    """

    def __init__(self) -> None:
        self._heap: _v14_List[_v14_List] = []       # [eff_priority, seq, req]
        self._counter = _v14_itertools.count(1)
        self._wake = _v14_asyncio.Event()
        self._worker_task: _v14_Any = None
        self._pending: _v14_Dict[tuple, _v14_Any] = {}   # dedupe key -> future
        self._asset_chains: _v14_Dict[str, _v14_asyncio.Lock] = {}
        self._buckets: _v14_Dict[int, V14TokenBucket] = {}
        for prio, (rate, cap) in V14_BUCKET_RATES.items():
            self._buckets[int(prio)] = V14TokenBucket(rate, cap)
        self._pacer = V14UpstreamPacer()
        self._running = False
        self._stats_lock = _v14_threading.Lock()
        self._submitted = 0
        self._deduped = 0
        self._expired = 0
        self._executed = 0
        self._failed = 0
        self._cancelled = 0
        # عائلات الانتظار المشتركة (نمط pyquotex SlotRegistry)
        self._done_slots = SlotRegistry()

    # ---------- سلاسل العملات ----------
    def _chain(self, api_symbol: str) -> _v14_asyncio.Lock:
        """قفل تسلسل لكل عملة — طلبات العملة الواحدة لا تتداخل أبداً."""
        lock = self._asset_chains.get(api_symbol)
        if lock is None:
            lock = _v14_asyncio.Lock()
            self._asset_chains[api_symbol] = lock
        return lock

    def _prune_chains(self) -> None:
        """تنظيف أقفال العملات غير المستعملة (منع نمو بلا حدود)."""
        if len(self._asset_chains) <= 512:
            return
        with self._stats_lock:
            locked = {s for s, lk in self._asset_chains.items() if lk.locked()}
        for sym in list(self._asset_chains.keys()):
            if sym not in locked:
                self._asset_chains.pop(sym, None)

    # ---------- الإرسال ----------
    def submit_nowait(self, api_symbol: str, end_time: int, seconds: int,
                      period: int, *,
                      priority: int = int(RequestPriority.PRELOAD),
                      label: str = "", foreground: bool = False,
                      timeout: float = 25.0,
                      wait_deadline: float = 90.0) -> _v14_Any:
        """يسجل الطلب في الطابور ويعيد Future فوراً (بلا انتظار).

        wait_deadline: مهلة انتظار داخل الطابور (ثوانٍ monotonic) — بعد
        رفضها يفشل الطلب سريعاً بدل تعليق السلسلة (مضاد «التعليق»).
        """
        loop = _v14_asyncio.get_running_loop()
        fut = loop.create_future()
        api_symbol = str(api_symbol or "").strip()
        key = (api_symbol, int(period), int(end_time), int(seconds))
        # dedupe: نفس الطلب معلّق بالفعل → نفس النتيجة (لا خلط)
        existing = self._pending.get(key)
        if existing is not None and not existing.done():
            self._deduped += 1
            V14_METRICS.inc("v14.gate.deduped")
            return existing
        req = V14FetchRequest(
            seq=next(self._counter),
            api_symbol=api_symbol,
            end_time=int(end_time),
            seconds=int(seconds),
            period=int(period),
            priority=int(priority),
            label=str(label or ""),
            foreground=bool(foreground),
            timeout=float(timeout),
            future=fut,
            dedupe_key=key,
            deadline=(time.monotonic() + wait_deadline) if wait_deadline else 0.0,
        )
        self._pending[key] = fut
        self._push(req)
        with self._stats_lock:
            self._submitted += 1
        V14_METRICS.inc("v14.gate.submitted")
        V14_METRICS.inc(f"v14.gate.submitted.{RequestPriority.name_of(req.priority)}")
        V14_JOURNAL.record("gate_submit", asset=api_symbol,
                           prio=req.priority, label=req.label,
                           seconds=req.seconds, seq=req.seq)
        self._wake.set()
        return fut

    async def submit(self, api_symbol: str, end_time: int, seconds: int,
                     period: int, *,
                     priority: int = int(RequestPriority.PRELOAD),
                     label: str = "", foreground: bool = False,
                     timeout: float = 25.0,
                     wait_deadline: float = 90.0):
        """يسجل ثم ينتظر النتيجة — يعيد الرد الخام كما تعيده البوابة الرسمية
        أو يرفع استثناء الطلب (المستدعي يعالجه كما يعالج رد البوابة الأصلية)."""
        fut = self.submit_nowait(api_symbol, end_time, seconds, period,
                                 priority=priority, label=label,
                                 foreground=foreground, timeout=timeout,
                                 wait_deadline=wait_deadline)
        return await fut

    def _push(self, req: V14FetchRequest) -> None:
        _v14_heapq.heappush(self._heap, [int(req.priority), req.seq, req])
        self._wake.set()

    def _next_request(self) -> _v14_Optional[V14FetchRequest]:
        """يسحب الطلب الأعلى أولوية مع تطبيق الأعمار وفحص المهل.

        الأعمار (aging): أولوية الطلب تتحسن مستوى كل AGING_STEP ثانية انتظار
        (بلا تجاوز OPENING) — ضد تجوع الطلبات الخلفية عند ضغط أمامي طويل.
        """
        now = time.monotonic()
        aged: _v14_List[_v14_List] = []
        chosen = None
        while self._heap:
            eff, seq, req = _v14_heapq.heappop(self._heap)
            if req.future is None or req.future.done():
                continue  # أُلغي أثناء الانتظار — تجاهل
            if req.deadline and now > req.deadline:
                # مهلة وفاة انقضت → فشل سريع (لا تعليق)
                self._expired += 1
                V14_METRICS.inc("v14.gate.expired")
                V14_JOURNAL.record("gate_expired", asset=req.api_symbol,
                                   label=req.label, waited_s=round(now - req.enqueued_at, 1))
                self._pop_pending(req)
                if not req.future.done():
                    req.future.set_exception(
                        TimeoutError(f"v14 gate: request expired after "
                                     f"{now - req.enqueued_at:.1f}s in queue "
                                     f"({req.describe()})"))
                continue
            # حساب الأولوية المؤقتة بالأعمار
            waited = now - req.enqueued_at
            aged_level = int(waited // V14_AGING_STEP_SECONDS)
            new_eff = max(int(RequestPriority.OPENING),
                          req.priority - aged_level)
            entry = [new_eff, seq, req]
            if chosen is None:
                chosen = entry
            else:
                aged.append(entry)
        if chosen is not None:
            aged.append(chosen)
        if aged:
            # أعِد الباقي للكومة بأولوياتهم المحدثة (الأعمار مكتوبة فعلياً)
            for entry in aged:
                if entry is not chosen:
                    _v14_heapq.heappush(self._heap, entry)
            if chosen is not None:
                return chosen[2]
        return None

    def _pop_pending(self, req: V14FetchRequest) -> None:
        try:
            if self._pending.get(req.dedupe_key) is req.future:
                self._pending.pop(req.dedupe_key, None)
        except Exception:
            pass

    # ---------- العامل ----------
    async def worker(self) -> None:
        """عامل البوابة — يعمل للأبد، طلب واحد فعلي في كل لحظة.

        كل خطأ يُسجل ويُحصَّد — العامل لا يموت أبداً (دون انهيار الخوادم).
        """
        self._running = True
        V14_JOURNAL.record("gate_worker_start")
        while True:
            try:
                req = self._next_request()
                if req is None:
                    self._wake.clear()
                    # انتظار موجّه بالأحداث — لا نوم دوري (نمط pyquotex)
                    await self._wake.wait()
                    continue
                await self._execute(req)
            except _v14_asyncio.CancelledError:
                self._running = False
                raise
            except Exception as e:
                # آخر خط دفاع: العامل لا يموت — سجّل واستمر
                V14_METRICS.inc("v14.gate.worker_errors")
                V14_JOURNAL.record("gate_worker_error", error=str(e)[:200])
                try:
                    logmsg(f"[v14-gate] worker caught: {e}")
                except Exception:
                    pass
                await v14_backoff_sleep(1, base=0.3, cap=2.0, jitter=0.2)

    async def _execute(self, req: V14FetchRequest) -> None:
        """ينفذ طلباً واحداً داخل سلسلة عملته — هنا يجتمع كل الضمانات."""
        t_wait = time.monotonic() - req.enqueued_at
        V14_METRICS.observe("v14.gate.wait_s", t_wait)
        try:
            bucket = self._buckets.get(req.priority) or \
                self._buckets[int(RequestPriority.PRELOAD)]
            await bucket.acquire()
            await self._pacer.wait()
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            pass  # الدلو/الإيقاع لا يمنعان التنفيذ أبداً — عدّادات فقط
        # سلسلة العملة: طلبات العملة الواحدة متسلسلة بلا اختلاط
        chain = self._chain(req.api_symbol)
        async with chain:
            if req.future.done():
                self._pop_pending(req)
                return
            t0 = time.monotonic()
            try:
                raw = await qx_fetch_window_raw(
                    req.api_symbol, req.end_time, req.seconds, req.period,
                    foreground=req.foreground, timeout=req.timeout)
                dt = time.monotonic() - t0
                V14_METRICS.observe("v14.gate.exec_s", dt)
                with self._stats_lock:
                    self._executed += 1
                V14_METRICS.inc("v14.gate.executed")
                V14_METRICS.inc(f"v14.gate.executed."
                                f"{RequestPriority.name_of(req.priority)}")
                V14_JOURNAL.record("gate_done", asset=req.api_symbol,
                                   label=req.label, exec_s=round(dt, 3),
                                   wait_s=round(t_wait, 3), seq=req.seq)
                if not req.future.done():
                    req.future.set_result(raw)
            except _v14_asyncio.CancelledError:
                with self._stats_lock:
                    self._cancelled += 1
                if not req.future.done():
                    req.future.cancel()
                raise
            except Exception as e:
                dt = time.monotonic() - t0
                with self._stats_lock:
                    self._failed += 1
                V14_METRICS.inc("v14.gate.failed")
                V14_METRICS.observe("v14.gate.fail_exec_s", dt)
                V14_JOURNAL.record("gate_fail", asset=req.api_symbol,
                                   label=req.label, error=str(e)[:200],
                                   exec_s=round(dt, 3))
                try:
                    logmsg(f"[v14-gate] request failed ({req.describe()}): {e}")
                except Exception:
                    pass
                if not req.future.done():
                    req.future.set_exception(e)
            finally:
                self._pop_pending(req)
                self._prune_chains()

    # ---------- إحصاءات ----------
    def depth(self) -> int:
        return len(self._heap)

    def depth_by_priority(self) -> dict:
        out: _v14_Dict[str, int] = {}
        for eff, seq, req in list(self._heap):
            name = RequestPriority.name_of(req.priority)
            out[name] = out.get(name, 0) + 1
        return out

    def stats(self) -> dict:
        with self._stats_lock:
            return {
                "submitted": self._submitted,
                "deduped": self._deduped,
                "executed": self._executed,
                "failed": self._failed,
                "expired": self._expired,
                "cancelled": self._cancelled,
                "depth": self.depth(),
                "depth_by_priority": self.depth_by_priority(),
                "buckets": {RequestPriority.name_of(p): b.state()
                            for p, b in self._buckets.items()},
            }

    @property
    def running(self) -> bool:
        return self._running


# البوابة العامة — تستعملها كل مكونات v14 (سد الثغرات، المدقق، المسابر)
V14_GATE = V14RequestGate()


async def v14_fetch(api_symbol: str, end_time: int, seconds: int, period: int, *,
                    priority: int = int(RequestPriority.PRELOAD),
                    label: str = "", timeout: float = 25.0,
                    wait_deadline: float = 90.0):
    """واجهة مريحة: جلب عبر بوابة الأولوية (نفس الرد الخام الرسمي)."""
    return await V14_GATE.submit(api_symbol, end_time, seconds, period,
                                 priority=priority, label=label,
                                 timeout=timeout,
                                 wait_deadline=wait_deadline)


def v14_fetch_foreground_pending() -> int:
    """عدد الطلبات الأمامية المعلقة في بوابة v14 (للتطبيق)."""
    return sum(1 for fut in V14_GATE._pending.values() if not fut.done())


def v14_gate_snapshot() -> dict:
    """لقطة حالة البوابة للـ heartbeat والتقارير."""
    st = V14_GATE.stats()
    st["worker_running"] = V14_GATE.running
    return st


# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء B — الوحدات 4 و 5 و 6:
#   4) V14 ENDPOINTS  — تقوي نقاط الخوادم (مسبح نقاط + قاطع دائرة + مسابر)
#   5) V14 TICK ENGINE — التكس لا ينام (مضخة مُيقَظة بالأحداث + كاشف فقدان)
#   6) V14 GAP GUARD  — سد الثغرات الأصلي على كل عملة مفتوحة + مراجع فقدان
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 4 — V14 ENDPOINTS (تقوي نقاط الخوادم)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم: «ابحث في المكتبة لي ارسلت لك سابقا في غيت هاب كيف تقوي نقاط
# الخوادم وتفرز الطلبات».
#
# ما وجدناه في مكتبة pyquotex المرسلة (الأنماط المعتمدة هنا):
#   • pyquotex/ws/client.py: مست回 watchdog يقيس صمت الاتصال (last_message_at)
#     ويعيد تدوير الاتصال القديم قسراً.
#   • pyquotex/ws/client.py: إعادة تشغيل الاشتراكات بعد كل إعادة اتصال ناجحة
#     (_replay_subscriptions — انتظار CONNECTED حتى 40×0.05s ثم إعادة كل اشتراك).
#   • pyquotex/_api/_waits.py: backoff أُسّي مهزوز بدل الإيقاع الميكانيكي.
#
# أسماء النطاقات الحقيقية فقط (من الكود الأساسي نفسه — لا نطاقات مُخترعة):
#   DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
#   DEFAULT_DOMAIN_GLOBAL     = "quotex.com"
# المسبح يراقب صحة النقطتين (TCP RTT + قاطع دائرة على أخطاء الجلب) ويكتب
# تقرير نطاقات + توصية. تبديل الاتصال الفعلي يبقى في مسار auto_reconnect
# الأصلي (لم يُمَس) — التقوية هنا: قياس، قاطع، تقرير، وتوصية موثقة.
# ════════════════════════════════════════════════════════════════════════════

class BreakerState:
    """حالات قاطع الدائرة (نمط صناعي قياسي)."""
    CLOSED = "CLOSED"        # سليم — يمر كل شيء
    OPEN = "OPEN"            # مفصول — يمنع ويبدأ عدّاد الاستشفاء
    HALF_OPEN = "HALF_OPEN"  # استشفاء — يمرر بروبات محدودة


class V14CircuitBreaker:
    """قاطع دائرة لكل نقطة خدمة.

    الفكرة (نمط صناعي — وهو نفس جوهر watchdog pyquotex): لا تضرب نقطة
    خدمة منهارة بطلبات متواصلة؛ افصلها (OPEN)، استشفها بروبة واحدة كل
    recovery_interval، وأعد فتحها بعد نجاحين متتاليين.

    آمن خيوطياً — يُستخدم من حلقة العامل ومن المسابر معاً.
    """

    def __init__(self, name: str, *,
                 failure_threshold: int = 5,
                 recovery_interval: float = 30.0,
                 half_open_successes: int = 2) -> None:
        self.name = name
        self.failure_threshold = int(failure_threshold)
        self.recovery_interval = float(recovery_interval)
        self.half_open_successes = int(half_open_successes)
        self._lock = _v14_threading.Lock()
        self._state = BreakerState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._opened_at = 0.0
        self._opened_count = 0
        self._last_error = ""
        self._last_transition_at = time.time()

    def _transition(self, state: str) -> None:
        self._state = state
        self._last_transition_at = time.time()
        self._opened_at = time.monotonic() if state == BreakerState.OPEN else 0.0
        V14_JOURNAL.record("breaker", name=self.name, state=state)
        try:
            logmsg(f"[v14-endpoint] circuit {self.name} -> {state}")
        except Exception:
            pass

    def allow_probe(self) -> bool:
        """هل تمرر هذه اللحظة طلباً؟ (OPEN يمرر فقط بروبة استشفاء بعد فترة)"""
        with self._lock:
            if self._state == BreakerState.CLOSED:
                return True
            if self._state == BreakerState.OPEN:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self.recovery_interval:
                    self._transition(BreakerState.HALF_OPEN)
                    self._consecutive_successes = 0
                    return True
                return False
            # HALF_OPEN: يمرر دائماً بروبة (العامل يحد من التزامن أصلاً)
            return True

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            if self._state == BreakerState.HALF_OPEN:
                self._consecutive_successes += 1
                if self._consecutive_successes >= self.half_open_successes:
                    self._transition(BreakerState.CLOSED)
            elif self._state == BreakerState.CLOSED:
                self._consecutive_successes += 1

    def record_failure(self, error: str = "") -> None:
        with self._lock:
            self._consecutive_successes = 0
            self._consecutive_failures += 1
            self._last_error = str(error)[:160]
            if self._state == BreakerState.HALF_OPEN:
                # البروبة فشلت — أعد الفصل فوراً
                self._opened_count += 1
                self._transition(BreakerState.OPEN)
            elif self._state == BreakerState.CLOSED and \
                    self._consecutive_failures >= self.failure_threshold:
                self._opened_count += 1
                self._transition(BreakerState.OPEN)

    def state(self) -> str:
        with self._lock:
            return self._state

    def info(self) -> dict:
        with self._lock:
            return {
                "state": self._state,
                "consecutive_failures": self._consecutive_failures,
                "opened_count": self._opened_count,
                "last_error": self._last_error,
                "last_transition": round(self._last_transition_at, 1),
            }


class V14EndpointState:
    """حالة نقطة خدمة واحدة (نطاق حقيقي من الكود الأساسي)."""

    def __init__(self, host: str, primary: bool = False) -> None:
        self.host = host
        self.primary = bool(primary)
        self.rtt_ms: _v14_Optional[float] = None     # EMA للمسابر الناجحة
        self.rtt_samples = 0
        self.probe_failures = 0
        self.last_probe_at = 0.0
        self.last_ok_at = 0.0
        self.breaker = V14CircuitBreaker(f"endpoint:{host}")
        self.fetch_ok = 0
        self.fetch_fail = 0

    def observe_rtt(self, ms: float) -> None:
        """EMA كلاسيكي — أحدث العينات أثقل (alpha يعتمد على عدد العينات)."""
        if ms is None or ms <= 0:
            return
        alpha = 0.4 if self.rtt_samples < 3 else 0.2
        if self.rtt_ms is None:
            self.rtt_ms = float(ms)
        else:
            self.rtt_ms = self.rtt_ms * (1 - alpha) + float(ms) * alpha
        self.rtt_samples += 1
        self.last_ok_at = time.time()
        self.probe_failures = 0

    def observe_probe_fail(self) -> None:
        self.probe_failures += 1

    def score(self) -> float:
        """درجة النقطة (أقل = أفضل) — تجمع RTT وحالة القاطع وأخطاء المسابر."""
        s = 0.0
        if self.breaker.state() == BreakerState.OPEN:
            s += 1000.0
        elif self.breaker.state() == BreakerState.HALF_OPEN:
            s += 300.0
        s += min(200.0, self.probe_failures * 25.0)
        if self.rtt_ms is not None:
            s += min(300.0, self.rtt_ms)
        else:
            s += 150.0  # مجهول RTT أسوأ من نتيجة معروفة
        if not self.primary:
            s += 10.0   # تفضيل طفيف للنقطة الأساسية عند تساوي كل شيء
        return round(s, 2)

    def info(self) -> dict:
        return {
            "host": self.host,
            "primary": self.primary,
            "rtt_ms": round(self.rtt_ms, 1) if self.rtt_ms else None,
            "rtt_samples": self.rtt_samples,
            "probe_failures": self.probe_failures,
            "last_probe_at": round(self.last_probe_at, 1),
            "breaker": self.breaker.info(),
            "fetch_ok": self.fetch_ok,
            "fetch_fail": self.fetch_fail,
            "score": self.score(),
        }


class V14EndpointPool:
    """مسبح نقاط الخدمة — «تقوي نقاط الخوادم».

    الوظائف:
      1) مسابر TCP RTT دورية خفيفة (كل V14_ENDPOINT_PROBE_INTERVAL ثانية)
         على النطاقات الحقيقية فقط (443) — قياس لا يزعج خوادم كوتكس.
      2) قاطع دائرة لكل نطاق يُغذى من نتائج الجلب الفعلية (report_ok/fail).
      3) تقرير نطاقات JSON (qx_endpoint_report.json) يُحدَّث كل دورة —
         التطبيق والمشغل يقرآن حالة النقاط لحظياً.
      4) توصية موثقة في السجل عند تدهور الأساسي: إن فُتح قاطع الأساسي
         بينما البديل سليم لمدة طويلة → توصية صريحة بإعادة الاتصال عبر
         المسار الرسمي (auto_reconnect الأصلي يبقى صاحب القرار الفعلي —
         نضع العلم V14_RECONNECT_HINT الذي تقرأه حلقات المراقبة).
    """

    def __init__(self) -> None:
        # النطاقات الحقيقية فقط من الكود الأساسي — الأساسي هو المُحلول جغرافياً
        primary_host = ""
        try:
            primary_host = (globals().get("QX_HOST") or
                            globals().get("DEFAULT_DOMAIN_GLOBAL") or "quotex.com")
        except Exception:
            primary_host = "quotex.com"
        alt_host = globals().get("DEFAULT_DOMAIN_BANGLADESH") or "market-qx.info"
        glob_host = globals().get("DEFAULT_DOMAIN_GLOBAL") or "quotex.com"
        self.endpoints: _v14_Dict[str, V14EndpointState] = {}
        self.endpoints[primary_host] = V14EndpointState(primary_host, primary=True)
        other = alt_host if primary_host != alt_host else glob_host
        if other != primary_host:
            self.endpoints[other] = V14EndpointState(other, primary=False)
        self.probe_interval = float(globals().get("_V14_ENDPOINT_PROBE_INTERVAL",
                                                  45.0))
        self.report_path = ""
        try:
            self.report_path = _v14_os.path.join(
                _v14_base_dir(), "qx_endpoint_report.json")
        except Exception:
            self.report_path = "qx_endpoint_report.json"
        self._last_report_write = 0.0
        self._lock = _v14_threading.Lock()

    # ---------- تغذية من نتائج الجلب الفعلية ----------
    def report_fetch(self, host: _v14_Optional[str], ok: bool,
                     error: str = "") -> None:
        """يسجل نتيجة جلب فعلي على النقطة (يُستدعى من حلقات v14 التي تعرف
        المضيف عبر QX_HOST). يحرك قاطع الدائرة."""
        with self._lock:
            ep = self.endpoints.get(host or "")
            if ep is None:
                return
            if ok:
                ep.fetch_ok += 1
                ep.breaker.record_success()
            else:
                ep.fetch_fail += 1
                ep.breaker.record_failure(error)

    # ---------- المسابر ----------
    async def probe_once(self, host: str, timeout: float = 3.0) -> _v14_Optional[float]:
        """مسحة TCP واحدة: قياس زمن فتح مقبس 443 — بلا أي ضغط على API."""
        loop = _v14_asyncio.get_running_loop()

        def _probe() -> _v14_Optional[float]:
            t0 = time.monotonic()
            sock = None
            try:
                sock = _v14_socket.create_connection((host, 443),
                                                     timeout=float(timeout))
                return (time.monotonic() - t0) * 1000.0
            except Exception:
                return None
            finally:
                try:
                    if sock is not None:
                        sock.close()
                except Exception:
                    pass

        try:
            return await _v14_asyncio.wait_for(loop.run_in_executor(None, _probe),
                                               timeout=timeout + 2.0)
        except Exception:
            return None

    async def probe_all(self) -> None:
        for host, ep in list(self.endpoints.items()):
            ms = await self.probe_once(host)
            ep.last_probe_at = time.time()
            if ms is not None:
                ep.observe_rtt(ms)
                V14_METRICS.gauge(f"v14.endpoint.{host}.rtt_ms", ms)
            else:
                ep.observe_probe_fail()
                V14_METRICS.inc("v14.endpoint.probe_failures")
            await _v14_asyncio.sleep(0.1)

    # ---------- الحلقة الدورية ----------
    async def monitor_loop(self) -> None:
        """حلقة المراقبة: مسحة + تقرير + توصيات. لا تمس الاتصال الفعلي."""
        await _v14_asyncio.sleep(5.0)   # اترك الاتصال يبدأ أولاً
        while True:
            try:
                await self.probe_all()
                await self._write_report()
                self._maybe_recommend()
                await _v14_asyncio.sleep(self.probe_interval)
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_METRICS.inc("v14.endpoint.monitor_errors")
                V14_JOURNAL.record("endpoint_monitor_error", error=str(e)[:200])
                await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)

    def _maybe_recommend(self) -> None:
        """توصية موثقة عند تدهور الأساسي مع بديل سليم — دون لمس الاتصال."""
        try:
            primary = next((e for e in self.endpoints.values() if e.primary), None)
            if primary is None:
                return
            others = [e for e in self.endpoints.values() if not e.primary]
            if not others:
                return
            pb = primary.breaker
            if pb.state() == BreakerState.OPEN and pb._opened_at and \
                    (time.monotonic() - pb._opened_at) > 120.0:
                healthy_alt = any(o.breaker.state() == BreakerState.CLOSED
                                  for o in others)
                if healthy_alt and not V14_RECONNECT_HINT.get():
                    V14_RECONNECT_HINT.set(True)
                    logmsg(f"[v14-endpoint] primary {primary.host} circuit OPEN "
                           f"for >120s while fallback healthy — reconnect hint "
                           f"SET (auto_reconnect owns the actual switch)")
                    V14_JOURNAL.record("endpoint_recommend",
                                       primary=primary.host,
                                       reason="primary_circuit_open")
        except Exception:
            pass

    async def _write_report(self) -> None:
        """يكتب تقرير النقاط ذرياً (tmp + rename) — القراءة آمنة دائماً."""
        try:
            report = {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "active_host": globals().get("QX_HOST", ""),
                "reconnect_hint": V14_RECONNECT_HINT.get(),
                "endpoints": [e.info() for e in self.endpoints.values()],
            }
            tmp = self.report_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                _v14_json.dump(report, f, ensure_ascii=False, indent=2)
            _v14_os.replace(tmp, self.report_path)
            self._last_report_write = time.time()
        except Exception:
            pass

    def info(self) -> dict:
        with self._lock:
            return {
                "active_host": globals().get("QX_HOST", ""),
                "endpoints": [e.info() for e in self.endpoints.values()],
                "report_path": self.report_path,
                "probe_interval_s": self.probe_interval,
            }


# مسبح النقاط العام
V14_ENDPOINTS = V14EndpointPool()


async def v14_endpoint_probe_loop() -> None:
    """حلقة مسابر النقاط — supervised."""
    await V14_ENDPOINTS.monitor_loop()


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 5 — V14 TICK ENGINE (التكس لا ينام)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم الحرفي: «ولا تيكس النوم ايضا لا يجب ان ينام مثل الكود لي اريتك».
#
# الفرق عن v13:
#   v13 كان يجمع التيكات بحلقة نائمة: tick_cache_collector → sleep(0.25)
#   كل دورة. أي أن التكس قد ينام حتى 250ms قبل أن يُخزّن، وينام مرة أخرى
#   قبل أن يصل للمشتركين — هذا هو «التكس النائم».
#
# v14 — نفس فلسفة الكود المرجعي (quotex_mt4_server_v10.realtime_stream:
# معالجة فورية لكل تيك داخل حلقة البث بلا نوم في مسار المعالجة):
#   1) مضخة مُيقَظة بالأحداث: تنتظر asyncio.Event يرفعه الالتقاط فور رؤية
#      تيك جديد — مسار المعالجة نفسه بلا أي sleep.
#   2) ملتقط مراقب 10ms كحماية عمق إضافية (لو فُقد رفع الحدث) — والملتقط
#      نفسه يستيقظ المضخة، فلا تيك يبقى راقداً أكثر من 10ms في أسوأ حال.
#   3) ترقيم متسلسل + كاشف فقدان: كل تيك يحمل seq، وأي قفزة زمنية شاذة
#      تُحسب «فقدان محتمل» — «ولا يتم فقدان».
#   4) توزيع فوري على المشتركين (بلا نوم بين التوزيعات — sleep(0) فقط
#      لتسليم الحلقة)، والمشترك البطيء يُساق بسياسة إسقاط الأقدم
#      مع عدّاد — البطيء لا يعيق السريع.
#   5) التخزين نفسه كما في v13 (ذاكرة فقط + TTL 5 دقائق + لا قرص).
# ════════════════════════════════════════════════════════════════════════════

class TickClassification:
    NEW = "NEW"          # تيك جديد فعلٍ
    DUPLICATE = "DUP"    # نفس الطابع الزمني — مكرر
    STALE = "STALE"      # أقدم من آخر تيك — تجاهل (نفس منطق الكود المرجعي)
    GAP = "GAP"          # قفزة زمنية شاذة — فقدان محتمل


class V14TickTracker:
    """متتبع تسلسل التيكات لعملة واحدة — يصنف كل تيك ويكشف الفقدان.

    منطق التصنيف مطابق لروح الكود المرجعي:
      - تيك أقدم من الأخير → STALE (تجاهل — «stale tick — ignore»).
      - نفس الطابع → DUPLICATE.
      - قفزة أكبر من V14_TICK_GAP_MULTIPLIER × الفاصل المتوسط → GAP
        (يُحسب فقدان محتمل — عدّاد + سجل، بلا أي تصرف هجومي).
    """

    def __init__(self, api_symbol: str, maxlen: int = 600) -> None:
        self.api_symbol = api_symbol
        self.ring = _v14_deque(maxlen=int(maxlen))   # [(seq, ts, price)]
        self.seq = 0
        self.last_ts = 0
        self.gap_intervals = _v14_deque(maxlen=30)   # متوسط الفواصل الطبيعية
        self.gap_events = 0
        self.last_price = 0.0
        self._lock = _v14_threading.Lock()

    def ingest(self, ts: int, price: float, *, gap_multiplier: float = 8.0,
               min_gap_s: float = 30.0) -> str:
        """يبتلع تيكاً ويعيد تصنيفه — آمن من الخيوط."""
        with self._lock:
            if ts <= 0 or price <= 0:
                return TickClassification.STALE
            if self.last_ts and ts < self.last_ts:
                return TickClassification.STALE
            if self.last_ts and ts == self.last_ts:
                # تحديث آخر سعر إن تغير (نفس الثانية قد تحمل سعراً أحدث)
                if price != self.last_price and self.ring:
                    seq, _, _ = self.ring[-1]
                    self.ring[-1] = (seq, ts, price)
                    self.last_price = price
                return TickClassification.DUPLICATE
            # تيك جديد — فحص القفزة (فقدان محتمل)
            if self.last_ts:
                interval = ts - self.last_ts
                # متوسط الفواصل الطبيعية السابقة فقط (قبل هذه الفجوة —
                # الفجوة نفسها لا تلوث خط الأساس وإلا أخفت كل ما بعدها)
                prev = list(self.gap_intervals)
                avg = (sum(prev) / len(prev)) if prev else interval
                if interval > max(min_gap_s, avg * gap_multiplier):
                    self.gap_events += 1
                    V14_METRICS.inc("v14.ticks.gap_events")
                    classification = TickClassification.GAP
                    # الفجوة لا تُضاف لنافذة الفواصل الطبيعية
                else:
                    classification = TickClassification.NEW
                    self.gap_intervals.append(interval)
            else:
                classification = TickClassification.NEW
            self.seq += 1
            self.ring.append((self.seq, ts, price))
            self.last_ts = ts
            self.last_price = price
            return classification

    def since(self, seconds: int) -> _v14_List[Tuple[int, int, float]]:
        cutoff = time.time() - max(1, int(seconds))
        with self._lock:
            return [(s, t, p) for (s, t, p) in self.ring if t >= cutoff]

    def silence_seconds(self) -> float:
        if not self.last_ts:
            return 0.0
        return max(0.0, time.time() - self.last_ts)

    def info(self) -> dict:
        with self._lock:
            return {
                "api_symbol": self.api_symbol,
                "count": len(self.ring),
                "seq": self.seq,
                "last_ts": self.last_ts,
                "last_price": self.last_price,
                "gap_events": self.gap_events,
                "silence_s": round(self.silence_seconds(), 1),
            }


class V14TickSubscriber:
    """مشترك تيكات — طابور محدود + سياسة إسقاط الأقدم للبطيء.

    البطيء لا يعيق السريع ولا يوقف المضخة أبداً (خادم لا ينهار بسبب مشترك).
    """

    def __init__(self, handle: int, symbols: _v14_Optional[_v14_Set[str]] = None,
                 maxsize: int = 2000) -> None:
        self.handle = handle
        self.symbols = set(symbols) if symbols else None
        # طابور خيوطي حقيقي مع إسقاط يدوي للأقدم عند الامتلاء
        from queue import Queue as _Queue
        self.q: _Queue = _Queue(maxsize=maxsize)
        self.dropped = 0
        self.delivered = 0
        self.created_at = time.time()

    def wants(self, api_symbol: str) -> bool:
        return self.symbols is None or api_symbol in self.symbols

    def offer(self, tick: tuple) -> None:
        """يضع التيك؛ لو امتلأ الطابور يُسقط الأقدم (drop-oldest)."""
        try:
            self.q.put_nowait(tick)
            self.delivered += 1
        except Exception:
            try:
                self.q.get_nowait()
                self.dropped += 1
                V14_METRICS.inc("v14.ticks.subscriber_dropped")
                self.q.put_nowait(tick)
                self.delivered += 1
            except Exception:
                self.dropped += 1
                V14_METRICS.inc("v14.ticks.subscriber_dropped")

    def drain(self, max_items: int = 500) -> _v14_List[tuple]:
        out = []
        for _ in range(max_items):
            try:
                out.append(self.q.get_nowait())
            except Exception:
                break
        return out


class V14TickEngine:
    """مضخة التيكات — «التكس لا ينام».

    البنية:
      - trackers: متتبع لكل عملة (ترقيم + فقدان + صمت).
      - notify(): يرفع حدث الاستيقاظ فور رؤية تيك جديد (من الالتقاط).
      - pump_loop(): ينتظر الحدث، يصرف كل جديد فوراً (بلا نوم في المسار)،
        يوزع على المشتركين، ثم يعود للانتظار الموجّه بالأحداث.
      - sampler_loop(): ملتقط 10ms حماية — يقرأ realtime_candles مباشرة
        ويستيقظ المضخة؛ لو لم يوجد رفع الحدث لأي سبب لن يُفقد تيك.
      - silence_watchdog(): يراقب صمت العملات المفتوحة — إعادة تشغيل بث
        عبر نفس نمط auto_reconnect الأصلي (إلغاء المهمة + إعادة التشغيل).

    التخزين: نفس _cache_tick الرسمي (ذاكرة فقط + TTL 5 دقائق كما في v13).
    """

    def __init__(self) -> None:
        self.trackers: _v14_Dict[str, V14TickTracker] = {}
        self.subscribers: _v14_List[V14TickSubscriber] = []
        self._lock = _v14_threading.RLock()
        self._wake: _v14_Optional[_v14_asyncio.Event] = None
        self._wake_loop: _v14_Optional[_v14_asyncio.AbstractEventLoop] = None
        # تيكات ملتهمة بانتظار التوزيع: {symbol: (ts, price, classification)}
        self._pending_map: _v14_Dict[str, tuple] = {}
        self._pump_running = False
        self._notify_from_thread = False
        self._loop_ref: _v14_Optional[Any] = None

    # ---------- الاستيقاظ ----------
    def _ensure_wake(self, loop) -> None:
        if self._wake is None or self._wake_loop is not loop:
            self._wake = _v14_asyncio.Event()
            self._wake_loop = loop

    def notify(self, api_symbol: str, loop=None) -> None:
        """يوقظ المضخة — آمن من أي خيط (call_soon_threadsafe عند الحاجة)."""
        try:
            if self._wake is None:
                if loop is not None:
                    self._ensure_wake(loop)
                else:
                    return  # المضخة لم تبدأ بعد — الملتقط سيشغلها
            ev = self._wake
            lp = self._wake_loop
            if ev is None or lp is None:
                return
            try:
                running = _v14_asyncio.get_running_loop()
            except Exception:
                running = None
            if running is lp:
                ev.set()
            else:
                try:
                    lp.call_soon_threadsafe(ev.set)
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- المتتبعات ----------
    def tracker(self, api_symbol: str) -> V14TickTracker:
        with self._lock:
            t = self.trackers.get(api_symbol)
            if t is None:
                t = V14TickTracker(api_symbol)
                self.trackers[api_symbol] = t
            return t

    def forget(self, api_symbol: str) -> None:
        with self._lock:
            self.trackers.pop(api_symbol, None)

    # ---------- الالتقاط (يستدعيه غلاف _cache_tick) ----------
    def ingest_tick(self, api_symbol: str, ts: int, price: float) -> None:
        """يبتلع تيكاً في المتتبع + يستيقظ المضخة. بلا أي نوم."""
        try:
            tr = self.tracker(api_symbol)
            cls = tr.ingest(int(ts), float(price))
            if cls in (TickClassification.NEW, TickClassification.GAP):
                V14_TICKS_RATE.mark()
                V14_METRICS.inc("v14.ticks.ingested")
                if cls == TickClassification.GAP:
                    V14_JOURNAL.record("tick_gap", asset=api_symbol,
                                       ts=ts, price=price)
                with self._lock:
                    self._pending_map[api_symbol] = (int(ts), float(price), cls)
                self.notify(api_symbol)
        except Exception:
            pass

    # ---------- المشتركون ----------
    def subscribe(self, symbols: _v14_Optional[_v14_Set[str]] = None,
                  maxsize: int = 2000) -> V14TickSubscriber:
        sub = V14TickSubscriber(len(self.subscribers) + 1, symbols, maxsize)
        with self._lock:
            self.subscribers.append(sub)
        V14_JOURNAL.record("ticks_subscribe", handle=sub.handle,
                           symbols=sorted(symbols) if symbols else "ALL")
        return sub

    def unsubscribe(self, sub: V14TickSubscriber) -> None:
        with self._lock:
            try:
                self.subscribers.remove(sub)
            except Exception:
                pass

    def _dispatch(self, api_symbol: str, ts: int, price: float,
                  classification: str) -> None:
        """توزيع فوري على المشتركين — بلا نوم، إسقاط أقدم للبطيء."""
        with self._lock:
            subs = list(self.subscribers)
        if not subs:
            return
        payload = (api_symbol, int(ts), float(price), classification,
                   time.time())
        for sub in subs:
            if sub.wants(api_symbol):
                sub.offer(payload)

    # ---------- قراءة المصدر الحي ----------
    def _read_live(self, api_symbol: str) -> _v14_Optional[Tuple[int, float]]:
        """قراءة آخر سعر حي من realtime_candles — نفس المصدر الرسمي الذي
        يقرأه الكود الأساسي في realtime_stream حرفياً."""
        try:
            client = globals().get("CLIENT")
            if client is None or getattr(client, "api", None) is None:
                return None
            c = client.api.realtime_candles.get(api_symbol)
            if isinstance(c, list) and len(c) >= 3:
                return int(c[1]), float(c[2])
            if isinstance(c, dict):
                ts = int(c.get("time", c.get("timestamp", 0)))
                price = float(c.get("price", c.get("close", 0)))
                if ts > 0 and price > 0:
                    return ts, price
        except Exception:
            pass
        return None

    # ---------- المضخة ----------
    async def pump_loop(self) -> None:
        """مضخة التيكات — تنتظر الحدث، تصرف كل جديد، تعود للانتظار.

        مسار المعالجة نفسه بلا sleep (فقط sleep(0) لتسليم الحلقة بين
        المشتركين) — «التكس لا ينام».
        """
        loop = _v14_asyncio.get_running_loop()
        self._ensure_wake(loop)
        self._pump_running = True
        V14_JOURNAL.record("tick_pump_start")
        while True:
            try:
                ev = self._wake
                if ev is None:
                    self._ensure_wake(loop)
                    continue
                # انتظار موجّه بالأحداث مع مهلة أمان قصيرة: أي تيك جديد يوقظ
                # فوراً عبر notify() — والمهلة تنظف ما تبقى لو فات رفع حدث.
                try:
                    await _v14_asyncio.wait_for(ev.wait(), timeout=1.0)
                except _v14_asyncio.TimeoutError:
                    pass
                ev.clear()
                # صرف كل ما هو معلق الآن — فوري، بلا نوم:
                # أولاً التيكات الملتهمة فعلاً عبر ingest_tick (غلاف
                # _cache_tick أو الملتقط) — لها طابع وسعر وتصنيف جاهز
                with self._lock:
                    pending = dict(self._pending_map)
                    self._pending_map.clear()
                for sym, (ts, price, cls) in pending.items():
                    self._dispatch(sym, ts, price, cls)
                    await _v14_asyncio.sleep(0)   # تسليم الحلقة — بلا نوم
                # ثانياً: مسح أمان للمصدر الحي (realtime_candles) لكل أصل
                # متدفق — يغطي أي تيك لم يمر عبر ingest_tick لأي سبب
                # مراقب إضافي: اسحب كل الأصول المتدفقة حتى لو فات رفع العلم
                assets = list(globals().get("ALL_STREAMING_ASSETS") or [])
                seen = set(pending)
                for a in assets:
                    try:
                        seen.add(a.api_symbol)
                    except Exception:
                        pass
                for sym in seen:
                    live = self._read_live(sym)
                    if live is not None:
                        ts, price = live
                        tr = self.tracker(sym)
                        cls = tr.ingest(ts, price)
                        if cls in (TickClassification.NEW,
                                   TickClassification.GAP,
                                   TickClassification.DUPLICATE):
                            # NEW/GAP: تيك جديد فعلٍ — DUPLICATE: سعر أحدث
                            # بنفس الثانية — كلاهما يوزع فوراً على المشتركين
                            self._dispatch(sym, ts, price, cls)
                    await _v14_asyncio.sleep(0)   # تسليم الحلقة — بلا نوم
                V14_METRICS.gauge("v14.ticks.trackers", len(self.trackers))
                # العودة للانتظار الموجّه بالأحداث في رأس الحلقة (مهلة أمان
                # 1s هناك تُنظف المتبقي لو فات رفع الحدث).
            except _v14_asyncio.CancelledError:
                self._pump_running = False
                raise
            except Exception as e:
                V14_METRICS.inc("v14.ticks.pump_errors")
                V14_JOURNAL.record("tick_pump_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=0.2, cap=2.0, jitter=0.2)

    def subs_len(self) -> int:
        with self._lock:
            return len(self.subscribers)

    # ---------- الملتقط المراقب ----------
    async def sampler_loop(self) -> None:
        """ملتقط 10ms — حماية عمق فوق notify(): يقرأ realtime_candles لكل
        عملة متدفقة ويستيقظ المضخة عند أي جديد. لو فات أي تيك لأي سبب،
        الملتقط يضبطه خلال 10ms كحد أقصى — لا تيك نائم ولا تيك مفقود.

        هذا ملتقط لا معالج: المعالجة الفعلية كلها في المضخة المُيقَظة.
        """
        V14_JOURNAL.record("tick_sampler_start")
        while True:
            try:
                woke = False
                for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
                    try:
                        sym = asset.api_symbol
                    except Exception:
                        continue
                    live = self._read_live(sym)
                    if live is None:
                        continue
                    ts, price = live
                    tr = self.tracker(sym)
                    if tr.last_ts and ts <= tr.last_ts:
                        continue   # لا جديد — بلا تخزين بلا إيقاظ
                    # جديد: خزّنه في الكاش الرسمي نفسه (ذاكرة فقط)
                    try:
                        _cache_tick(sym, ts, price)
                    except Exception:
                        pass
                    self.ingest_tick(sym, ts, price)
                    woke = True
                if woke:
                    self.notify()
                    V14_METRICS.inc("v14.ticks.sampler_wakes")
                await _v14_asyncio.sleep(0.01)   # 10ms — حماية لا نوم معالجة
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_METRICS.inc("v14.ticks.sampler_errors")
                V14_JOURNAL.record("tick_sampler_error", error=str(e)[:200])
                await _v14_asyncio.sleep(0.05)

    # ---------- ساعة صمت العملات المفتوحة ----------
    async def silence_watchdog(self) -> None:
        """مراقب صمت: عملة مفتوحة بلا تيك > عتبة → إعادة تشغيل بثها عبر
        نفس نمط auto_reconnect الأصلي (إلغاء + realtime_stream من جديد) —
        لا يخترع مسار اتصال جديداً."""
        restart_silence = float(globals().get("_V14_TICK_SILENCE_RESTART", 90.0))
        while True:
            try:
                await _v14_asyncio.sleep(10.0)
                client = globals().get("CLIENT")
                alive = bool(globals().get("CONNECTION_ALIVE"))
                if client is None or not alive:
                    continue
                loop = _v14_asyncio.get_running_loop()
                for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
                    try:
                        sym = asset.api_symbol
                        tr = self.trackers.get(sym)
                        if tr is None:
                            continue
                        silence = tr.silence_seconds()
                        V14_METRICS.gauge(f"v14.ticks.{sym}.silence_s", silence)
                        if silence >= restart_silence:
                            running = False
                            try:
                                task = getattr(asset, "stream_task", None)
                                running = task is not None and not task.done() \
                                    and bool(getattr(asset, "streaming", False))
                            except Exception:
                                running = False
                            if not running:
                                continue   # بثها متوقف أصلاً — ليس صمتاً شاذاً
                            tr.ring.clear()
                            tr.last_ts = 0
                            logmsg(f"[v14-ticks] {sym} silent {silence:.0f}s "
                                   f"> {restart_silence:.0f}s — restarting "
                                   f"stream (same pattern as auto_reconnect)")
                            V14_JOURNAL.record("tick_silence_restart",
                                               asset=sym, silence_s=round(silence, 1))
                            V14_METRICS.inc("v14.ticks.silence_restarts")
                            try:
                                old = getattr(asset, "stream_task", None)
                                if old is not None and not old.done():
                                    old.cancel()
                            except Exception:
                                pass
                            asset.streaming = False
                            try:
                                asset.stream_task = \
                                    asyncio.run_coroutine_threadsafe(
                                        subsecond_stream(asset)
                                        if globals().get("IS_SUBSECOND")
                                        else realtime_stream(asset), loop)
                            except Exception as e:
                                V14_JOURNAL.record("tick_restart_fail",
                                                   asset=sym, error=str(e)[:160])
                            await _v14_asyncio.sleep(0.05)  # نفس إيقاع الكود المرجعي
                    except _v14_asyncio.CancelledError:
                        raise
                    except Exception as e:
                        # خطأ في أصل واحد لا يوقف فحص بقية الأصول أبداً
                        V14_JOURNAL.record("tick_silence_asset_error",
                                           asset=getattr(asset, "api_symbol", "?"),
                                           error=str(e)[:160])
                        continue
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("tick_silence_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=1.0, cap=10.0, jitter=0.2)

    # ---------- تقارير ----------
    def snapshot(self, seconds: int = 300) -> dict:
        with self._lock:
            trackers = {k: t.info() for k, t in self.trackers.items()}
            subs = [{"handle": s.handle, "delivered": s.delivered,
                     "dropped": s.dropped,
                     "queued": s.q.qsize() if s.q else 0}
                    for s in self.subscribers]
        return {"trackers": trackers, "subscribers": subs,
                "rate_30s": round(V14_TICKS_RATE.rate(30.0), 2)}

    def recent_ticks(self, api_symbol: str, seconds: int = 300) -> _v14_List[list]:
        tr = self.trackers.get(api_symbol)
        if not tr:
            return []
        return [[t, p] for (_s, t, p) in tr.since(seconds)]

    def gap_summary(self) -> dict:
        with self._lock:
            return {k: t.gap_events for k, t in self.trackers.items()
                    if t.gap_events}


# محرك التيكات العام + معدل التيكات المتدحرج
V14_TICKS = V14TickEngine()
V14_TICKS_RATE = V14RollingRate(window_seconds=30.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 6 — V14 GAP GUARD (سد الثغرات الأصلي على كل عملة مفتوحة)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم الحرفي:
#   «طريقة سد الثغرات لا تغيرها عن الكود لي اريتك يجب ان تنفذ على كل عملة
#    تم فتحها ولا يتم فقدان»
#
# الضمانات هنا:
#   1) الطريقة نفسها حرفياً: MT4_WRITER.fill_gap_once(CLIENT, asset, PERIOD)
#      + _fill_missing_slots + علامة التجمد gap_state.filled — صفر تغيير.
#      الحلقة الشاملة mt4_gap_filler الأصلية تعمل كما هي أيضاً.
#   2) «على كل عملة تم فتحها»: سجل مفتوحات (OpenedAssetRegistry) يلاحظ كل
#      عملة فُتح شارتها (opener / ensure_asset_loaded / fetch_older_batch /
#      preload_one_asset) ويجدول لها سد ثغرات فوراً — لا انتظار دورة
#      الحلقة الشاملة، ولا عملة مفتوحة تفوتها الآلية.
#   3) «ولا يتم فقدان»: مدقق فقدان دوري (V14GapLossAuditor) يمسح خط زمن
#      كل عملة مفتوحة؛ أي فجوة مشبوهة تُعيد استدعاء نفس fill_gap_once
#      الأصلية لتلك العملة حتى تُسد — الطريقة نفسها، التغطية كاملة.
#   4) المدقق لا يكتب شموعاً بنفسه أبداً — الكتابة تبقى للطريقة الأصلية.
# ════════════════════════════════════════════════════════════════════════════

class OpenedAssetRegistry:
    """سجل كل عملة تم فتحها — مصدر الحقيقة لـ«سد الثغرات على كل مفتوح».

    لكل عملة: وقت الفتح الأول، آخر نشاط، عدد مرات الفتح، مصدر الفتح،
    حالة آخر سد ثغرات، وآخر نتيجة مدقق فقدان.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._opened: _v14_Dict[str, dict] = {}

    def note_open(self, api_symbol: str, source: str) -> None:
        api_symbol = str(api_symbol or "").strip()
        if not api_symbol:
            return
        now = time.time()
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is None:
                rec = {
                    "first_open_at": now,
                    "first_source": source,
                    "opens": 0,
                    "last_open_at": now,
                    "last_source": source,
                    "last_gap_fill_at": 0.0,
                    "gap_fill_runs": 0,
                    "gap_fill_errors": 0,
                    "last_audit_at": 0.0,
                    "last_audit_holes": 0,
                }
                self._opened[api_symbol] = rec
                V14_JOURNAL.record("asset_opened", asset=api_symbol,
                                   source=source)
            rec["opens"] += 1
            rec["last_open_at"] = now
            rec["last_source"] = source

    def note_gap_fill(self, api_symbol: str, ok: bool) -> None:
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is None:
                return
            rec["last_gap_fill_at"] = time.time()
            if ok:
                rec["gap_fill_runs"] += 1
            else:
                rec["gap_fill_errors"] += 1

    def note_audit(self, api_symbol: str, holes: int) -> None:
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is not None:
                rec["last_audit_at"] = time.time()
                rec["last_audit_holes"] = int(holes)

    def opened(self) -> _v14_List[str]:
        with self._lock:
            return list(self._opened.keys())

    def is_opened(self, api_symbol: str) -> bool:
        with self._lock:
            return api_symbol in self._opened

    def snapshot(self) -> dict:
        with self._lock:
            return {k: dict(v) for k, v in self._opened.items()}

    def __len__(self) -> int:
        with self._lock:
            return len(self._opened)


# سجل المفتوحات العام
V14_OPENED = OpenedAssetRegistry()


def _v14_find_asset(api_symbol: str):
    """يجد كائن Asset الرسمي للعملة من قائمة الأصول المتدفقة (بلا إنشاء
    جديد هنا — الإنشاء مسؤولية المسار الرسمي _get_or_create_asset)."""
    for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
        try:
            if asset.api_symbol == api_symbol:
                return asset
        except Exception:
            continue
    return None


async def v14_gap_fill_for_asset(api_symbol: str, *,
                                 reason: str = "opened") -> bool:
    """سد ثغرات عملة واحدة — بالطريقة الأصلية حرفياً.

    يستدعي MT4_WRITER.fill_gap_once(CLIENT, asset, PERIOD) — نفس الآلية
    التي تشغلها الحلقة الشاملة mt4_gap_filler، لكن مركزة على هذه العملة
    فور فتحها. لا شيء جديد في الطريقة — فقط تنفيذ فوري لكل مفتوح.
    """
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return False
    client = globals().get("CLIENT")
    alive = bool(globals().get("CONNECTION_ALIVE"))
    if client is None or getattr(client, "api", None) is None or not alive:
        V14_METRICS.inc("v14.gap.skipped_not_connected")
        return False
    # انتظار قصير موجّه حتى تجهز الأصول (نمط pyquotex wait_until)
    asset = _v14_find_asset(api_symbol)
    if asset is None:
        try:
            await v14_wait_until(
                lambda: _v14_find_asset(api_symbol) is not None,
                timeout=8.0, poll_interval=0.25)
            asset = _v14_find_asset(api_symbol)
        except _v14_asyncio.TimeoutError:
            asset = None
    if asset is None:
        # العملة ليست في قائمة البث بعد — حاول بالمسار الرسمي للإنشاء
        try:
            getter = globals().get("_get_or_create_asset")
            if getter is not None:
                asset = getter(api_symbol)
        except Exception:
            asset = None
    if asset is None:
        V14_JOURNAL.record("gap_fill_no_asset", asset=api_symbol, reason=reason)
        V14_OPENED.note_gap_fill(api_symbol, False)
        return False
    # الوضع تحت الثاني: الآلية الأصلية نفسها معطلة في وضع subsecond
    if globals().get("IS_SUBSECOND"):
        V14_METRICS.inc("v14.gap.skipped_subsecond")
        return False
    ok = False
    t0 = time.monotonic()
    try:
        await MT4_WRITER.fill_gap_once(client, asset,
                                       int(globals().get("PERIOD", 1)))
        ok = True
    except _v14_asyncio.CancelledError:
        raise
    except Exception as e:
        V14_METRICS.inc("v14.gap.fill_errors")
        V14_JOURNAL.record("gap_fill_error", asset=api_symbol,
                           error=str(e)[:200])
        try:
            logmsg(f"[v14-gap] fill error for {api_symbol}: {e}")
        except Exception:
            pass
    dt = time.monotonic() - t0
    V14_OPENED.note_gap_fill(api_symbol, ok)
    V14_METRICS.inc("v14.gap.fill_runs" if ok else "v14.gap.fill_failed")
    V14_METRICS.observe("v14.gap.fill_exec_s", dt)
    if ok:
        V14_JOURNAL.record("gap_fill_done", asset=api_symbol,
                           reason=reason, exec_s=round(dt, 3))
        try:
            logmsg(f"[v14-gap] gap fill done for {api_symbol} "
                   f"({reason}) in {dt:.1f}s — original method untouched")
        except Exception:
            pass
    return ok


def v14_note_asset_opened(api_symbol: str, source: str) -> None:
    """تسجيل فتح عملة + جدولة سد ثغرات فوري لها (من أي خيط).

    هذه هي نقطة «على كل عملة تم فتحها»: كل مسار رسمي يفتح شارتاً يمر
    هنا، ويحصل على سد ثغرات فوري بنفس الطريقة الأصلية.
    """
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return
    first_open = not V14_OPENED.is_opened(api_symbol)
    V14_OPENED.note_open(api_symbol, source)
    V14_METRICS.inc("v14.gap.asset_opened")
    # السد الفوري فقط للفتح الأول (الإعادة تعتمد علامة التجمد الأصلية
    # داخل fill_gap_once نفسها — لن تلمس الشموع المسددة)
    if not first_open:
        return
    try:
        loop = _v14_asyncio.get_running_loop()
    except Exception:
        loop = globals().get("ASYNC_LOOP")
    if loop is None or loop.is_closed():
        return
    try:
        _v14_asyncio.run_coroutine_threadsafe(
            v14_gap_fill_for_asset(api_symbol, reason=source), loop)
        V14_JOURNAL.record("gap_fill_scheduled", asset=api_symbol,
                           source=source)
    except Exception as e:
        V14_JOURNAL.record("gap_fill_schedule_fail", asset=api_symbol,
                           error=str(e)[:160])


class V14GapLossAuditor:
    """مدقق فقدان الشموع — «ولا يتم فقدان».

    المنهج (بلا أي كتابة شموع — الكتابة للطريقة الأصلية فقط):
      1) لكل عملة مفتوحة: خذ خط الشموع الرسمي (asset.candles أو لقطة
         قاعدة الشموع الرسمية).
      2) افحص استمرارية الخانات داخل نافذة الفحص (last slots).
      3) الفجوة المشبوهة (بين شمعتين متجاورتين فرق > فترة واحدة والفجوة
         أقل من عتبة إغلاق السوق) → استدعِ نفس fill_gap_once الأصلية
         لتلك العملة حتى تسد — عدّاد + سجل.
      4) عتبة إغلاق السوق: للفريمات الدقيقة نعتبر الفجوة > ساعتين خارج
         نطاق «فقدان» (إغلاق سوق حقيقي للعملات غير OTC — التعبئة المسطحة
         الأصلية تحدها max_gap=1440 كما هي).
    """

    def __init__(self, audit_interval: float = 120.0,
                 suspect_max_gap_s: float = 7200.0) -> None:
        self.audit_interval = float(audit_interval)
        self.suspect_max_gap_s = float(suspect_max_gap_s)
        self._running = False

    def _candle_line(self, api_symbol: str) -> _v14_List[dict]:
        """خط الشموع الرسمي: من الأصل الحي أولاً ثم من المتجر الرسمي."""
        asset = _v14_find_asset(api_symbol)
        candles = []
        try:
            if asset is not None and getattr(asset, "candles", None):
                candles = list(asset.candles)
        except Exception:
            candles = []
        if not candles:
            try:
                store = globals().get("MT4_WRITER")
                if store is not None and getattr(store, "load_snapshot", None):
                    snap = store.load_snapshot(api_symbol)
                    if snap:
                        candles = list(snap)
            except Exception:
                pass
        return candles

    def find_holes(self, api_symbol: str,
                   candles: _v14_List[dict]) -> _v14_List[int]:
        """يعيد مواضع الفجوات المشبوهة (طوابع بداية الفجوة) — قراءة فقط."""
        holes: _v14_List[int] = []
        period_s = max(1, int(globals().get("PERIOD_SECONDS", 60)))
        try:
            line = sorted(candles, key=lambda c: c.get("time", 0))
            if len(line) < 2:
                return holes
            for a, b in zip(line, line[1:]):
                gap = int(b.get("time", 0)) - int(a.get("time", 0))
                if period_s < gap <= int(self.suspect_max_gap_s) and \
                        gap > period_s:
                    holes.append(int(a.get("time", 0)))
        except Exception:
            pass
        return holes

    async def audit_once(self) -> dict:
        """مسحة واحدة لكل المفتوحات — يعيد ملخص المسحة."""
        result = {"audited": 0, "with_holes": 0, "refills": 0}
        period_s = max(1, int(globals().get("PERIOD_SECONDS", 60)))
        for sym in V14_OPENED.opened():
            try:
                result["audited"] += 1
                candles = self._candle_line(sym)
                if not candles:
                    V14_OPENED.note_audit(sym, 0)
                    continue
                holes = self.find_holes(sym, candles)
                V14_OPENED.note_audit(sym, len(holes))
                V14_METRICS.gauge(f"v14.gap.{sym}.holes", len(holes))
                if holes:
                    result["with_holes"] += 1
                    V14_METRICS.inc("v14.gap.holes_found", len(holes))
                    V14_JOURNAL.record("gap_holes", asset=sym,
                                       holes=len(holes),
                                       first=int(holes[0]) if holes else 0)
                    # إعادة السد بالطريقة الأصلية نفسها — حتى لا يُفقد شيء
                    ok = await v14_gap_fill_for_asset(sym, reason="audit")
                    if ok:
                        result["refills"] += 1
                        V14_METRICS.inc("v14.gap.audit_refills")
                await _v14_asyncio.sleep(0.05)
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("gap_audit_error", asset=sym,
                                   error=str(e)[:160])
        return result

    async def loop(self) -> None:
        """حلقة المدقق الدورية — supervised، لا تنهار."""
        self._running = True
        await _v14_asyncio.sleep(30.0)   # اترك الفتح الأول يكتمل
        while True:
            try:
                if globals().get("CLIENT") is None or \
                        not globals().get("CONNECTION_ALIVE"):
                    await _v14_asyncio.sleep(5.0)
                    continue
                res = await self.audit_once()
                if res["with_holes"]:
                    try:
                        logmsg(f"[v14-gap] audit: {res['audited']} opened assets, "
                               f"{res['with_holes']} had holes, "
                               f"{res['refills']} refilled (original method)")
                    except Exception:
                        pass
                await _v14_asyncio.sleep(self.audit_interval)
            except _v14_asyncio.CancelledError:
                self._running = False
                raise
            except Exception as e:
                V14_METRICS.inc("v14.gap.audit_errors")
                V14_JOURNAL.record("gap_audit_loop_error", error=str(e)[:200])
                await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)


# المدقق العام
V14_GAP_AUDITOR = V14GapLossAuditor()


async def v14_gap_guard_loop() -> None:
    """حلقة حارس الثغرات: تعمل كل 60 ثانية مسحة سريعة لكل عملة مفتوحة
    لضمان أن الآلية الأصلية مرّت عليها (بلا تعديل طريقة)."""
    await _v14_asyncio.sleep(20.0)
    while True:
        try:
            client = globals().get("CLIENT")
            if client is None or not globals().get("CONNECTION_ALIVE") or \
                    globals().get("IS_SUBSECOND"):
                await _v14_asyncio.sleep(10.0)
                continue
            # لكل عملة مفتوحة لم تُسد ثغراتها بعد (علامة التجمد الأصلية
            # داخل fill_gap_once تمنع اللمس المتكرر — استدعاؤها آمن)
            for sym in V14_OPENED.opened():
                rec = V14_OPENED.snapshot().get(sym, {})
                if not rec.get("last_gap_fill_at"):
                    ok = await v14_gap_fill_for_asset(sym, reason="guard")
                    if ok:
                        break   # واحدة في الدورة — البوابة تفرز البقية
                await _v14_asyncio.sleep(0.1)
            await _v14_asyncio.sleep(60.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception as e:
            V14_JOURNAL.record("gap_guard_error", error=str(e)[:200])
            await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)


# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء C — الوحدات 7 و 8 و 9 + نقاط الربط:
#   7) V14 SUPERVISOR — دون انهيار الخوادم (مشرف كل حلقة + خطافات استثناء
#      + حصاد المهام + حارس ذاكرة/قرص + تفريغ حمل + نبضة حياة)
#   8) V14 RESILIENCE — إعادة تشغيل البث بعد العودة (نمط pyquotex) + مراقب
#      جلسة + خطافات التركيب على المسارات الرسمية (بلا تعديل المسارات)
#   9) V14 API — الواجهة العامة للتطبيق + بناء حلقات الخلفية المشرفة
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 7 — V14 SUPERVISOR (دون انهيار الخوادم)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم: «تخص في تقويت السرفر وطريقة العمل دون انهيار الخوادم».
#
# الفكرة الجوهرية — نفس عقد pyquotex/ws/client.py::run_forever مطبق على كل
# حلقة خلفية في الخادم:
#   while True:
#       try: await connect_once(); attempt = 0      # النجاح يصفّر العداد
#       except: backoff_sleep(attempt); attempt += 1
#
# أي حلقة تموت (استثناء غير متوقع) يُعاد تشغيلها بـ backoff مهزوز — الخادم
# لا ينهار من انهيار حلقة واحدة. فوق ذلك:
#   - خطافات استثناء عامة (sys + threading + حلقة asyncio): كل شيء يُسجل.
#   - حصاد المهام الميتة الصامتة كل 30 ثانية.
#   - حارس ذاكرة (gc عند العتبات) وحارس قرص (تفريغ الحمل عند امتلاء).
#   - تفريغ حمل GRREN/AMBER/RED — RED يوقف الصيانة فقط؛ البث الحي وسد
#     الثغرات وفتح الشموع للمستخدم لا يتوقفان أبداً.
#   - نبضة حياة heartbeat JSON كل 10 ثوانٍ — إثبات حياة للخادم والتطبيق.
# ════════════════════════════════════════════════════════════════════════════

class V14LoopStatus:
    """حالة حلقة واحدة تحت المشرف."""
    __slots__ = ("name", "runs", "crashes", "last_alive_at", "last_error",
                 "last_error_at", "ever_started")

    def __init__(self, name: str) -> None:
        self.name = name
        self.runs = 0
        self.crashes = 0
        self.last_alive_at = 0.0
        self.last_error = ""
        self.last_error_at = 0.0
        self.ever_started = False


class V14Supervisor:
    """مشرف الحلقات — كل حلقة خلفية في v14 تعيش تحت إشرافه.

    الضمانات:
      - إعادة تشغيل تلقائية بـ backoff مهزوز (نمط pyquotex run_forever).
      - سقف معدل إعادة التشغيل: بعد 6 انهيارات/ساعة للحلقة الواحدة تُترك
        تنام 300 ثانية (حماية من دوران انهيار يشعل المعالج).
      - كل انهيار: عدّاد + سجل جلسة + رسالة ترمينال — لا صمت.
      - status() يعيد حالة كل الحلقات للنبضة والتقارير.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._statuses: _v14_Dict[str, V14LoopStatus] = {}
        self._restart_timestamps: _v14_Dict[str, _v14_List[float]] = {}
        self.started_at = time.time()

    def status_of(self, name: str) -> V14LoopStatus:
        with self._lock:
            st = self._statuses.get(name)
            if st is None:
                st = V14LoopStatus(name)
                self._statuses[name] = st
            return st

    def _restart_backoff(self, name: str) -> float:
        """سقف معدل الإعادة: 6/ساعة لكل حلقة → نوم طويل 300 ثانية."""
        now = time.monotonic()
        with self._lock:
            stamps = self._restart_timestamps.setdefault(name, [])
            while stamps and (now - stamps[0]) > 3600.0:
                stamps.pop(0)
            stamps.append(now)
            rate_ok = len(stamps) <= 6
        if rate_ok:
            return 0.0
        return 300.0

    async def supervise(self, name: str,
                        factory: Callable[[], _v14_Awaitable]) -> None:
        """يشغل الحلقة للأبد — يعيد تشغيلها عند كل موت بلا استسلام."""
        st = self.status_of(name)
        attempt = 0
        while True:
            try:
                st.ever_started = True
                st.runs += 1
                st.last_alive_at = time.time()
                V14_JOURNAL.record("loop_start", loop=name, run=st.runs)
                await factory()
                # الحلقة اللانهائية لا تعود عادة — عودتها تعامل كتوقف لطيف
                st.last_alive_at = time.time()
                V14_JOURNAL.record("loop_returned", loop=name)
                await _v14_asyncio.sleep(1.0)
                attempt = 0
            except _v14_asyncio.CancelledError:
                V14_JOURNAL.record("loop_cancelled", loop=name)
                raise
            except Exception as e:
                attempt += 1
                st.crashes += 1
                st.last_error = f"{type(e).__name__}: {e}"[:200]
                st.last_error_at = time.time()
                V14_METRICS.inc("v14.supervisor.loop_crashes")
                V14_METRICS.inc(f"v14.supervisor.crash.{name}")
                V14_JOURNAL.record("loop_crash", loop=name,
                                   run=st.runs, attempt=attempt,
                                   error=st.last_error)
                try:
                    logmsg(f"[v14-supervisor] loop '{name}' crashed "
                           f"(run {st.runs}, attempt {attempt}): "
                           f"{st.last_error} — restarting")
                except Exception:
                    pass
                # سقف معدل الإعادة ثم backoff مهزوز (نمط pyquotex)
                extra = self._restart_backoff(name)
                if extra:
                    try:
                        logmsg(f"[v14-supervisor] loop '{name}' restart-rate "
                               f"cap hit — cooling down {extra:.0f}s")
                    except Exception:
                        pass
                    await _v14_asyncio.sleep(extra)
                await v14_backoff_sleep(attempt, base=0.5, cap=30.0, jitter=0.15)

    def status(self) -> dict:
        with self._lock:
            out = {}
            for name, st in self._statuses.items():
                out[name] = {
                    "runs": st.runs,
                    "crashes": st.crashes,
                    "ever_started": st.ever_started,
                    "age_since_alive_s": round(time.time() - st.last_alive_at, 1)
                    if st.last_alive_at else None,
                    "last_error": st.last_error,
                }
            return out

    def alive_count(self) -> int:
        with self._lock:
            return sum(1 for st in self._statuses.values()
                       if st.ever_started and not st.last_error)


# المشرف العام
V14_SUPERVISOR = V14Supervisor()


async def v14_supervise(name: str,
                        factory: Callable[[], _v14_Awaitable]) -> None:
    """نقطة دخول موحدة: يشغّل أي حلقة تحت المشرف — تستخدم من __main__ ومن
    التطبيق بنفس الطريقة."""
    await V14_SUPERVISOR.supervise(name, factory)


def install_v14_exception_hooks() -> None:
    """خطافات استثناء عامة — كل خطأ غير ملتقط يُسجل ولا يُسقط الخادم.

    يغطي الثلاثة:
      - sys.excepthook: الاستثناءات في الخيط الرئيسي.
      - threading.excepthook: الاستثناءات في خيوط النظام (العدّاء الكاتب...).
      - loop.set_exception_handler: المهام الصامتة في حلقة asyncio.
    """
    def _hook(exc_type, exc_value, exc_tb) -> None:
        try:
            V14_METRICS.inc("v14.hooks.uncaught")
            V14_JOURNAL.record("uncaught",
                               kind="sys",
                               error=f"{exc_type.__name__}: {exc_value}")
            try:
                logmsg(f"[v14-hook] uncaught exception: "
                       f"{exc_type.__name__}: {exc_value}")
            except Exception:
                pass
        except Exception:
            pass

    try:
        old_hook = getattr(sys, "excepthook", None)
        sys.excepthook = _hook
    except Exception:
        pass

    try:
        import threading as _th
        _old_th = getattr(_th, "excepthook", None)

        def _thread_hook(args) -> None:
            try:
                V14_METRICS.inc("v14.hooks.uncaught")
                V14_JOURNAL.record(
                    "uncaught", kind="thread",
                    thread=getattr(args, "thread", None) and
                    args.thread.name or "?",
                    error=f"{getattr(args, 'exc_type', type(None)).__name__}: "
                          f"{getattr(args, 'exc_value', None)}")
                try:
                    logmsg(f"[v14-hook] uncaught in thread: {args}")
                except Exception:
                    pass
            except Exception:
                pass
        _th.excepthook = _thread_hook
    except Exception:
        pass

    # معالج استثناءات حلقة asyncio — يُثبَّت عند بدء الحلقات المشرفة
    def _loop_handler(loop, context) -> None:
        try:
            exc = context.get("exception")
            msg = context.get("message", "")
            V14_METRICS.inc("v14.hooks.loop_exceptions")
            V14_JOURNAL.record("loop_exception",
                               message=str(msg)[:160],
                               error=f"{type(exc).__name__}: {exc}" if exc else "")
        except Exception:
            pass

    try:
        loop = globals().get("ASYNC_LOOP")
        if loop is not None:
            loop.set_exception_handler(_loop_handler)
    except Exception:
        pass


class V14TaskHarvester:
    """حصاد المهام الميتة الصامتة — يستيقظ كل 30 ثانية ويمسح كل المهام
    المنتهية باستثناء لم تُقرأ نتيجتها (تلك التي كانت ستُخفى بصمت)."""

    def __init__(self) -> None:
        self._seen: _v14_Set[int] = set()
        self.harvested = 0

    async def loop(self) -> None:
        await _v14_asyncio.sleep(15.0)
        while True:
            try:
                await _v14_asyncio.sleep(30.0)
                pending_harvest = []
                for t in list(_v14_asyncio.all_tasks()):
                    try:
                        if t.done() and not t.cancelled():
                            exc = t.exception()
                            if exc is not None and \
                                    id(t) not in self._seen:
                                self._seen.add(id(t))
                                pending_harvest.append((t, exc))
                    except Exception:
                        continue
                if len(self._seen) > 4096:
                    self._seen.clear()
                for t, exc in pending_harvest:
                    self.harvested += 1
                    V14_METRICS.inc("v14.supervisor.harvested_exceptions")
                    V14_JOURNAL.record("harvested_task_exception",
                                       task=t.get_name(),
                                       error=f"{type(exc).__name__}: {exc}")
                    try:
                        logmsg(f"[v14-supervisor] harvested silent task "
                               f"exception: {type(exc).__name__}: {exc}")
                    except Exception:
                        pass
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=1.0, cap=10.0)


class V14MemoryGuard:
    """حارس ذاكرة — يأخذ RSS كل 30 ثانية ويستجيب بالعتبات:

      soft (افتراضي 512MB): gc.collect() + عدّاد.
      hard (افتراضي 768MB): gc.collect() كامل + تنظيف كاشات v14 المملوكة
                            فقط (لا يلمس شموع الأصول ولا أي بيانات رسمية
                            أبداً) + سجل + نبضة.

    RSS يقرأ من /proc/self/statm على لينكس ومن resource على غيره — بلا
    مكتبات خارجية.
    """

    def __init__(self, soft_mb: float = 512.0, hard_mb: float = 768.0) -> None:
        self.soft_mb = float(soft_mb)
        self.hard_mb = float(hard_mb)
        self.soft_events = 0
        self.hard_events = 0
        self.last_rss_mb = 0.0

    def rss_mb(self) -> float:
        try:
            # /proc/self/statm: الحقل الثاني = صفحات مقيمة (resident)
            with open("/proc/self/statm", "r") as f:
                parts = f.read().split()
            pages = int(parts[1])
            return pages * 4096.0 / (1024.0 * 1024.0)
        except Exception:
            try:
                import resource as _res
                ru = _res.getrusage(_res.RUSAGE_SELF).ru_maxrss
                return float(ru) / 1024.0   # KB→MB (لينكس)
            except Exception:
                return 0.0

    def _drop_owned_caches(self) -> None:
        """تنظيف الكاشات المملوكة لـ v14 فقط — صفر لمس للبيانات الرسمية."""
        try:
            try:
                V14_GATE._FETCH_CACHE_TTL_FLUSH = True  # noqa — لا شيء فعلي
            except Exception:
                pass
            # كاش debounce البوابة الأصلية يملكه v13 — لا نلمسه.
            # فقط المتتبعات الغنية والسجلات الفارغة:
            with V14_TICKS._lock:
                idle = [s for s, t in V14_TICKS.trackers.items()
                        if t.silence_seconds() > 600.0 and not t.ring]
                for s in idle:
                    V14_TICKS.trackers.pop(s, None)
            V14_GATE._prune_chains()
        except Exception:
            pass

    async def loop(self) -> None:
        await _v14_asyncio.sleep(20.0)
        while True:
            try:
                await _v14_asyncio.sleep(30.0)
                rss = self.rss_mb()
                self.last_rss_mb = rss
                V14_METRICS.gauge("v14.memory.rss_mb", round(rss, 1))
                if rss <= 0:
                    continue
                if rss >= self.hard_mb:
                    self.hard_events += 1
                    V14_METRICS.inc("v14.memory.hard_events")
                    collected = _v14_gc.collect(2)
                    self._drop_owned_caches()
                    V14_JOURNAL.record("memory_hard", rss_mb=round(rss, 1),
                                       collected=collected)
                    try:
                        logmsg(f"[v14-memory] HARD {rss:.0f}MB — "
                               f"gc({collected}) + owned-caches cleanup")
                    except Exception:
                        pass
                elif rss >= self.soft_mb:
                    self.soft_events += 1
                    V14_METRICS.inc("v14.memory.soft_events")
                    collected = _v14_gc.collect()
                    V14_JOURNAL.record("memory_soft", rss_mb=round(rss, 1),
                                       collected=collected)
                V14_METRICS.gauge("v14.memory.soft_events", self.soft_events)
                V14_METRICS.gauge("v14.memory.hard_events", self.hard_events)
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14DiskGuard:
    """حارس قرص — يفحص المساحة الحرة كل 10 دقائق على مجلدات HST وقاعدة
    الشموع. عند الانخفاض يفعّل تفريغ الحمل (يوقف الجلب الخلفي فقط —
    البث الحي وسد الثغرات للمفتوحات لا يتوقفان أبداً) ويسجل.

    العتبات: warn < 1GB ، shed < 500MB ، critical < 200MB.
    """

    def __init__(self) -> None:
        self.warn_free_mb = 1024.0
        self.shed_free_mb = 500.0
        self.critical_free_mb = 200.0
        self.last_free_mb = 0.0
        self.shed_active = False

    def _targets(self) -> _v14_List[str]:
        out = []
        try:
            out.append(globals().get("MT4_HISTORY_PATH") or ".")
        except Exception:
            out.append(".")
        return out

    def min_free_mb(self) -> float:
        vals = []
        for t in self._targets():
            try:
                usage = _v14_shutil.disk_usage(t)
                vals.append(usage.free / (1024.0 * 1024.0))
            except Exception:
                continue
        return min(vals) if vals else 0.0

    async def loop(self) -> None:
        await _v14_asyncio.sleep(30.0)
        while True:
            try:
                await _v14_asyncio.sleep(600.0)
                free = self.min_free_mb()
                self.last_free_mb = free
                V14_METRICS.gauge("v14.disk.free_mb", round(free, 1))
                if free <= 0:
                    continue
                if free <= self.critical_free_mb:
                    self.shed_active = True
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                    V14_JOURNAL.record("disk_critical", free_mb=round(free, 1))
                    try:
                        logmsg(f"[v14-disk] CRITICAL {free:.0f}MB free — "
                               f"background fetching paused (live streams "
                               f"and gap-fill continue)")
                    except Exception:
                        pass
                elif free <= self.shed_free_mb:
                    self.shed_active = True
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                    V14_JOURNAL.record("disk_shed", free_mb=round(free, 1))
                else:
                    if self.shed_active:
                        self.shed_active = False
                        V14_PAUSE_PRELOAD.set(False)
                        V14_JOURNAL.record("disk_recovered",
                                           free_mb=round(free, 1))
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14LoadShedder:
    """مفرّغ الحمل — يصنف الضغط GREEN/AMBER/RED من أربعة مؤشرات:

      - عمق بوابة الطلبات (تكدس = ضغط).
      - ذاكرة RSS.
      - معدل إعادة الاتصال الأخير.
      - مساحة القرص (من الحارس).

    RED: يوقف الصيانة فقط (يعلّم V14_PAUSE_PRELOAD و V14_SHED_PRESSURE).
    البث الحي، سد الثغرات للمفتوحات، وفتح الشموع للمستخدم لا يتوقفان أبداً.
    """

    def __init__(self) -> None:
        self.state = "GREEN"

    def evaluate(self) -> str:
        try:
            depth = V14_GATE.depth()
            rss = V14_MEMORY.last_rss_mb if "V14_MEMORY" in globals() else 0.0
            reconnect_hint = V14_RECONNECT_HINT.get()
            disk = V14_DISK.last_free_mb if "V14_DISK" in globals() else 0.0
            if depth >= 40 or reconnect_hint or \
                    (disk > 0 and disk <= V14_DISK.critical_free_mb):
                return "RED"
            if depth >= 15 or (rss and rss >= V14_MEMORY.soft_mb):
                return "AMBER"
            return "GREEN"
        except Exception:
            return "GREEN"

    async def loop(self) -> None:
        await _v14_asyncio.sleep(25.0)
        while True:
            try:
                await _v14_asyncio.sleep(15.0)
                new_state = self.evaluate()
                if new_state != self.state:
                    old = self.state
                    self.state = new_state
                    V14_METRICS.gauge("v14.pressure_state",
                                      {"GREEN": 0, "AMBER": 1, "RED": 2}
                                      .get(new_state, 0))
                    V14_JOURNAL.record("pressure", old=old, new=new_state)
                    try:
                        logmsg(f"[v14-shed] pressure {old} -> {new_state}")
                    except Exception:
                        pass
                if self.state == "RED":
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                elif self.state == "AMBER":
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(False)
                else:
                    # GREEN: أزل العلم فقط لو حارس القرص ليس هو الفاعل
                    if not V14_DISK.shed_active:
                        V14_PAUSE_PRELOAD.set(False)
                    V14_SHED_PRESSURE.set(False)
                V14_METRICS.gauge("v14.gate.depth", V14_GATE.depth())
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14Heartbeat:
    """نبضة الحياة — تكتب qx_server_heartbeat.json كل 10 ثوانٍ:

      وقت، pid، uptime، حالة الحلقات المشرفة، عمق البوابة، تيكات/ثانية،
      حالة الضغط، الذاكرة، القرص، سد الثغرات، النقاط، الجلسة.

    كتابة ذرية (tmp + rename) — القراءة آمنة دائماً من التطبيق أو المشغل.
    """

    def __init__(self, interval: float = 10.0) -> None:
        self.interval = float(interval)
        try:
            self.path = _v14_os.path.join(
                _v14_base_dir(), "qx_server_heartbeat.json")
        except Exception:
            self.path = "qx_server_heartbeat.json"
        self.writes = 0

    def payload(self) -> dict:
        try:
            mem = V14_MEMORY.rss_mb()
        except Exception:
            mem = 0.0
        try:
            disk = V14_DISK.last_free_mb
        except Exception:
            disk = 0.0
        try:
            endpoint_info = V14_ENDPOINTS.info()
        except Exception:
            endpoint_info = {}
        try:
            session = V14_SESSION.info()
        except Exception:
            session = {}
        try:
            shed = V14_LOAD_SHEDDER.state
        except Exception:
            shed = "GREEN"
        return {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": time.time(),
            "pid": _v14_os.getpid(),
            "uptime_s": round(time.time() - _V14_STARTED_AT, 1),
            "connection_alive": bool(globals().get("CONNECTION_ALIVE")),
            "active_host": globals().get("QX_HOST", ""),
            "streaming_assets": len(globals().get("ALL_STREAMING_ASSETS") or []),
            "opened_assets": len(V14_OPENED),
            "pressure": shed,
            "memory_rss_mb": round(mem, 1),
            "disk_free_mb": round(disk, 1),
            "gate": v14_gate_snapshot(),
            "ticks_rate_30s": round(V14_TICKS_RATE.rate(30.0), 2),
            "gap_fills": V14_METRICS.counter("v14.gap.fill_runs"),
            "gap_audits_holes": V14_METRICS.counter("v14.gap.holes_found"),
            "supervisor": V14_SUPERVISOR.status(),
            "endpoints": endpoint_info,
            "session": session,
            "journal": V14_JOURNAL.info(),
        }

    async def loop(self) -> None:
        await _v14_asyncio.sleep(10.0)
        while True:
            try:
                await _v14_asyncio.sleep(self.interval)
                data = self.payload()
                tmp = self.path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    _v14_json.dump(data, f, ensure_ascii=False, indent=1)
                _v14_os.replace(tmp, self.path)
                self.writes += 1
                V14_METRICS.gauge("v14.heartbeat.writes", self.writes)
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=1.0, cap=10.0)


# الكائنات العامة للحارس (تُنشأ هنا — تستعملها الحلقات ومفرّغ الحمل)
V14_MEMORY = V14MemoryGuard()
V14_DISK = V14DiskGuard()
V14_LOAD_SHEDDER = V14LoadShedder()
V14_HEARTBEAT = V14Heartbeat()


async def v14_harvester_loop() -> None:
    await V14TaskHarvester().loop()


async def v14_memory_guard_loop() -> None:
    await V14_MEMORY.loop()


async def v14_disk_guard_loop() -> None:
    await V14_DISK.loop()


async def v14_load_shedder_loop() -> None:
    await V14_LOAD_SHEDDER.loop()


async def v14_heartbeat_loop() -> None:
    await V14_HEARTBEAT.loop()


async def v14_metrics_loop() -> None:
    """لوحة المقاييس الدورية في الترمينال — كل 90 ثانية كتلة مرتبة."""
    await _v14_asyncio.sleep(45.0)
    while True:
        try:
            try:
                report = V14_METRICS.format_report(
                    f"V14 METRICS — host={globals().get('QX_HOST', '?')} "
                    f"assets={len(globals().get('ALL_STREAMING_ASSETS') or [])} "
                    f"opened={len(V14_OPENED)} pressure={V14_LOAD_SHEDDER.state}")
                logmsg(report)
            except Exception:
                pass
            await _v14_asyncio.sleep(90.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=2.0, cap=15.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 8 — V14 RESILIENCE (إعادة تشغيل البث بعد العودة + مراقب جلسة)
# ════════════════════════════════════════════════════════════════════════════
# منقول من pyquotex/ws/client.py:
#   _replay_subscriptions(): بعد كل إعادة اتصال ناجحة (open_count > 1)
#   انتظر حتى CONNECTED (حتى 40 × 0.05s) ثم أعد إصدار كل اشتراك متتبع.
#
# الخادم الأساسي auto_reconnect يعيد الاتصال نفسه — لكنه (بحسب توقيت انقطاع)
# يعيد تشغيل البث للأصول المتدفقة فقط، ويعيد الجلب الكامل فقط للانقطاع
# الطويل. v14 يضيف طبقة ضمان مستقلة: مراقب انتقال CONNECTION_ALIVE
# False→True يعيد تشغيل بث كل أصل متدفق له ماتت مهمته (بنفس نمط
# auto_reconnect حرفياً: إلغاء المهمة القديمة ثم run_coroutine_threadsafe
# لـ realtime_stream / subsecond_stream) — بلا أي مسار اتصال جديد.
# ════════════════════════════════════════════════════════════════════════════

class V14SessionStateMachine:
    """آلة حالات الجلسة — BOOT→CONNECTING→CONNECTED→DEGRADED→
    RECONNECTING→CONNECTED ... توثق كل انتقال بمدته في السجل والمقاييس.

    لا تتحكم في الاتصال — تراقب وتوثق فقط (المسار الرسمي أصحاب القرار).
    """

    BOOT = "BOOT"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"          # اتصال حي لكن بلا تيكات/صمت طويل
    RECONNECTING = "RECONNECTING"  # الكود الأساسي يعيد الاتصال الآن

    def __init__(self) -> None:
        self.state = self.BOOT
        self.entered_at = time.time()
        self.transitions = 0
        self.drops = 0
        self.longest_connected_s = 0.0
        self.last_connected_at = 0.0
        self.total_connected_s = 0.0
        self._lock = _v14_threading.Lock()

    def _enter(self, state: str, note: str = "") -> None:
        now = time.time()
        with self._lock:
            prev = self.state
            dur = now - self.entered_at
            self.state = state
            self.entered_at = now
            self.transitions += 1
            if prev == self.CONNECTED:
                self.total_connected_s += dur
                self.longest_connected_s = max(self.longest_connected_s, dur)
        if state == self.CONNECTED:
            self.last_connected_at = now
        if state == self.RECONNECTING:
            self.drops += 1
        V14_JOURNAL.record("session_state", old=prev, new=state,
                           prev_duration_s=round(dur, 1), note=note[:120])
        V14_METRICS.inc("v14.session.transitions")
        try:
            logmsg(f"[v14-session] {prev} -> {state} "
                   f"(prev lasted {dur:.0f}s)")
        except Exception:
            pass

    def observe(self) -> None:
        """قراءة الواقع الحالي وتحديث الحالة وفقها — بلا أي تدخل."""
        alive = bool(globals().get("CONNECTION_ALIVE"))
        client = globals().get("CLIENT")
        has_client = client is not None and getattr(client, "api", None) is not None
        with self._lock:
            state = self.state
        if alive and has_client:
            if state in (self.BOOT, self.RECONNECTING, self.DEGRADED):
                self._enter(self.CONNECTED)
        elif alive and not has_client:
            if state == self.CONNECTED:
                self._enter(self.DEGRADED, "alive but client lost")
        elif not alive:
            if state in (self.CONNECTED, self.DEGRADED):
                self._enter(self.RECONNECTING, "connection lost")

    def info(self) -> dict:
        with self._lock:
            cur_dur = time.time() - self.entered_at
            return {
                "state": self.state,
                "state_age_s": round(cur_dur, 1),
                "transitions": self.transitions,
                "drops": self.drops,
                "longest_connected_s": round(self.longest_connected_s, 1),
                "total_connected_s": round(self.total_connected_s, 1),
            }


V14_SESSION = V14SessionStateMachine()


class V14SubscriptionReplay:
    """إعادة تشغيل البث بعد العودة — نمط pyquotex _replay_subscriptions.

    يعمل مع مراقب الجلسة: عند انتقال RECONNECTING→CONNECTED بعد انقطاع
    يُعاد تشغيل بث كل أصل متدفق مهمته ماتة — بنفس نمط auto_reconnect
    (إلغاء + run_coroutine_threadsafe + إيقاع 0.05s). المهمة الحية
    لا تُلمس (لا ازدواجية بث).
    """

    def __init__(self) -> None:
        self.replays = 0
        self.restarted_assets = 0
        self._last_replay_at = 0.0

    async def replay_all(self) -> int:
        """يعيد تشغيل البث لكل أصل متدفق مهمته ماتة — يعيد عدد المعادين."""
        loop = _v14_asyncio.get_running_loop()
        # انتظار جاهزية الاتصال — نمط pyquotex (حتى 40 × 0.05s = 2s)
        for _ in range(40):
            client = globals().get("CLIENT")
            if client is not None and getattr(client, "api", None) is not None \
                    and globals().get("CONNECTION_ALIVE"):
                break
            await _v14_asyncio.sleep(0.05)
        client = globals().get("CLIENT")
        if client is None or getattr(client, "api", None) is None:
            return 0
        restarted = 0
        for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
            try:
                task = getattr(asset, "stream_task", None)
                alive = False
                try:
                    alive = task is not None and not task.done()
                except Exception:
                    alive = False
                if alive and getattr(asset, "streaming", False):
                    continue   # حي — لا تلمس (بلا ازدواجية)
                try:
                    if task is not None and not task.done():
                        task.cancel()
                except Exception:
                    pass
                asset.streaming = False
                asset.stream_task = asyncio.run_coroutine_threadsafe(
                    subsecond_stream(asset) if globals().get("IS_SUBSECOND")
                    else realtime_stream(asset), loop)
                restarted += 1
                await _v14_asyncio.sleep(0.05)  # نفس إيقاع auto_reconnect
            except Exception as e:
                V14_JOURNAL.record("replay_asset_fail",
                                   asset=getattr(asset, "api_symbol", "?"),
                                   error=str(e)[:160])
        if restarted:
            self.replays += 1
            self.restarted_assets += restarted
            self._last_replay_at = time.time()
            V14_METRICS.inc("v14.resilience.replays")
            V14_METRICS.inc("v14.resilience.restarted_assets", restarted)
            V14_JOURNAL.record("subscription_replay", restarted=restarted)
            try:
                logmsg(f"[v14-resilience] subscription replay: restarted "
                       f"{restarted} dead stream(s) after reconnect")
            except Exception:
                pass
        return restarted

    async def loop(self) -> None:
        """المراقب الدوري: يلاحظ انتقالات الجلسة ويشغل الإعادة عند العودة."""
        await _v14_asyncio.sleep(10.0)
        prev_state = None
        while True:
            try:
                await _v14_asyncio.sleep(2.0)
                V14_SESSION.observe()
                state = V14_SESSION.state
                if prev_state is not None and \
                        prev_state == V14SessionStateMachine.RECONNECTING and \
                        state == V14SessionStateMachine.CONNECTED:
                    # العودة من انقطاع — أعد الاشتراكات (نمط pyquotex)
                    await self.replay_all()
                    # أيضاً: سد ثغرات سريع لكل المفتوحات بعد الانقطاع
                    for sym in V14_OPENED.opened():
                        asyncio.ensure_future(
                            v14_gap_fill_for_asset(sym, reason="reconnect"))
                        await _v14_asyncio.sleep(0.05)
                prev_state = state
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("replay_watcher_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=1.0, cap=15.0)


V14_REPLAY = V14SubscriptionReplay()


async def v14_replay_watcher_loop() -> None:
    await V14_REPLAY.loop()


async def v14_session_watcher_loop() -> None:
    """مراقب الجلسة — يحدّث آلة الحالات كل ثانيتين."""
    await _v14_asyncio.sleep(5.0)
    while True:
        try:
            V14_SESSION.observe()
            info = V14_SESSION.info()
            V14_METRICS.gauge("v14.session.drops", info["drops"])
            await _v14_asyncio.sleep(2.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=1.0, cap=15.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 9 — V14 API + التركيب على المسارات الرسمية + بناء الحلقات المشرفة
# ════════════════════════════════════════════════════════════════════════════
# التركيب (hooking) قاعدة الذهبي فيه: كل غلاف يستدعي الأصل الكامل أولاً
# ثم يضيف سلوك v14 — المسارات الرسمية لم تُمَس حرفياً.
# ════════════════════════════════════════════════════════════════════════════

def _v14_wrap_cache_tick() -> None:
    """غلاف _cache_tick: يخزن بالطريقة الرسمية ثم يوقظ مضخة التيكات.
    «التكس لا ينام» — نقطة الالتقاط هذه هي الحدث الذي يوقظ المضخة فوراً."""
    global _cache_tick
    if bool(globals().get("_V14_CACHE_TICK_WRAPPED", False)):
        return
    orig = globals().get("_cache_tick")
    if orig is None:
        return

    def _wrapped(api_symbol, ts, price):
        try:
            orig(api_symbol, ts, price)       # الطريقة الرسمية كما هي
        except Exception:
            pass
        try:
            V14_TICKS.ingest_tick(api_symbol, ts, price)   # الإيقاظ الفوري
        except Exception:
            pass
    globals()["_cache_tick"] = _wrapped
    globals()["_V14_CACHE_TICK_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="_cache_tick")


def _v14_wrap_ensure_asset_loaded() -> None:
    """غلاف ensure_asset_loaded: ينادي الأصل كاملاً ثم يسجل الفتح ويجدول
    سد ثغرات فوري — «على كل عملة تم فتحها»."""
    global ensure_asset_loaded
    if bool(globals().get("_V14_ENSURE_WRAPPED", False)):
        return
    orig = globals().get("ensure_asset_loaded")
    if orig is None:
        return

    async def _wrapped(api_symbol):
        n = await orig(api_symbol)               # الأصل الكامل كما هو
        try:
            if n:
                v14_note_asset_opened(api_symbol, "ensure_asset_loaded")
        except Exception:
            pass
        return n

    globals()["ensure_asset_loaded"] = _wrapped
    globals()["_V14_ENSURE_WRAPPED"] = True
    # حدّث واجهة الخادم للفتح المبطن (التطبيق يقرأها من PAGINATION_API)
    try:
        pag = globals().get("PAGINATION_API")
        if isinstance(pag, dict):
            pag["ensure_asset_loaded"] = _wrapped
    except Exception:
        pass
    V14_JOURNAL.record("hook_installed", hook="ensure_asset_loaded")


def _v14_wrap_fetch_older_batch() -> None:
    """غلاف fetch_older_batch: الأصل كاملاً ثم تسجيل الفتح + سد فوري —
    التمرير للخلف كجزء من تغطية «كل عملة مفتوحة»."""
    global fetch_older_batch
    if bool(globals().get("_V14_OLDER_WRAPPED", False)):
        return
    orig = globals().get("fetch_older_batch")
    if orig is None:
        return

    async def _wrapped(api_symbol, *args, **kwargs):
        n = await orig(api_symbol, *args, **kwargs)   # الأصل الكامل
        try:
            v14_note_asset_opened(api_symbol, "fetch_older_batch")
        except Exception:
            pass
        return n

    globals()["fetch_older_batch"] = _wrapped
    globals()["_V14_OLDER_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="fetch_older_batch")


def _v14_wrap_preload_one_asset() -> None:
    """غلاف preload_one_asset: الأصل كاملاً ثم تسجيل الفتح — يغطي أيضاً
    عملة فتح الشارت الافتراضية (opener) عند جلبها الأولى."""
    global preload_one_asset
    if bool(globals().get("_V14_PRELOAD_WRAPPED", False)):
        return
    orig = globals().get("preload_one_asset")
    if orig is None:
        return

    async def _wrapped(api_symbol, *args, **kwargs):
        t0 = time.monotonic()
        n = await orig(api_symbol, *args, **kwargs)   # الأصل الكامل
        try:
            dt = time.monotonic() - t0
            V14_METRICS.observe("v14.preload.exec_s", dt)
            if n:
                v14_note_asset_opened(api_symbol, "preload_one_asset")
        except Exception:
            pass
        return n

    globals()["preload_one_asset"] = _wrapped
    globals()["_V14_PRELOAD_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="preload_one_asset")


def install_v14_hooks() -> None:
    """يستبق تثبيت كل الأغلفة مرتين — idempotent."""
    global _V14_HOOKS_INSTALLED
    if globals().get("_V14_HOOKS_INSTALLED"):
        return
    _v14_wrap_cache_tick()
    _v14_wrap_ensure_asset_loaded()
    _v14_wrap_fetch_older_batch()
    _v14_wrap_preload_one_asset()
    install_v14_exception_hooks()
    globals()["_V14_HOOKS_INSTALLED"] = True
    V14_JOURNAL.record("v14_hooks_installed")


# ─── واجهة v14 العامة للتطبيق والمشغل ───

V14_API = {
    "version": _V14_VERSION,
    # جلب بأولوية عبر بوابة التفرز (نفس الرد الخام الرسمي):
    "fetch": v14_fetch,
    "fetch_with_priority": v14_fetch,
    "gate_stats": v14_gate_snapshot,
    # سد الثغرات الأصلي لعملة محددة (بلا تغيير طريقة):
    "gap_fill_for_asset": v14_gap_fill_for_asset,
    "note_asset_opened": v14_note_asset_opened,
    "opened_registry": lambda: V14_OPENED.snapshot(),
    # التيكات: لا تنام — اشتراك + قراءة فورية:
    "ticks": V14_TICKS,
    "subscribe_ticks": V14_TICKS.subscribe,
    "unsubscribe_ticks": V14_TICKS.unsubscribe,
    "recent_ticks": V14_TICKS.recent_ticks,
    "ticks_snapshot": V14_TICKS.snapshot,
    # النقاط والجلسة والمقاييس:
    "endpoints": lambda: V14_ENDPOINTS.info(),
    "session": lambda: V14_SESSION.info(),
    "metrics": lambda: V14_METRICS.snapshot(),
    "metrics_report": V14_METRICS.format_report,
    "supervisor_status": lambda: V14_SUPERVISOR.status(),
    "journal_tail": V14_JOURNAL.tail,
    "journal_info": V14_JOURNAL.info,
    "heartbeat_path": lambda: V14_HEARTBEAT.path,
    "heartbeat_payload": V14_HEARTBEAT.payload,
    "pressure_state": lambda: V14_LOAD_SHEDDER.state,
    "pause_preload_flag": V14_PAUSE_PRELOAD,
    # السياسات (منقولة من pyquotex):
    "policy": V14_POLICY,
    "backoff_delay": v14_backoff_delay,
    "slots": V14_SLOTS,
}


def v14_build_background_loops() -> _v14_List[Tuple[str, Callable[[], _v14_Awaitable]]]:
    """يبني قائمة كل حلقات v14 الخلفية المشرفة — تستدعى مرة واحدة عند
    التشغيل (من __main__ في وضع الترمينال، ومن التطبيق بعد الدخول).

    كل عنصر (اسم، مُصنع coroutine) — المشرف يستدعي المصنع عند كل إعادة
    تشغيل فتكون الحلقة جديدة نظيفة كل مرة (نمط pyquotex run_forever).
    التركيب (hooks) يثبت هنا أيضاً قبل تشغيل أي شيء.
    """
    install_v14_hooks()

    async def _gate_worker():
        await V14_GATE.worker()

    async def _tick_pump():
        await V14_TICKS.pump_loop()

    async def _tick_sampler():
        await V14_TICKS.sampler_loop()

    async def _tick_silence():
        await V14_TICKS.silence_watchdog()

    async def _gap_guard():
        await v14_gap_guard_loop()

    async def _gap_audit():
        await V14_GAP_AUDITOR.loop()

    async def _endpoint_probe():
        await v14_endpoint_probe_loop()

    async def _replay_watcher():
        await v14_replay_watcher_loop()

    async def _session_watcher():
        await v14_session_watcher_loop()

    async def _harvester():
        await v14_harvester_loop()

    async def _memory_guard():
        await v14_memory_guard_loop()

    async def _disk_guard():
        await v14_disk_guard_loop()

    async def _load_shedder():
        await v14_load_shedder_loop()

    async def _heartbeat():
        await v14_heartbeat_loop()

    async def _metrics():
        await v14_metrics_loop()

    async def _selftest():
        await v14_selftest_loop()

    return [
        ("gate_worker", _gate_worker),           # تفرز الطلبات
        ("tick_pump", _tick_pump),               # التكس لا ينام
        ("tick_sampler", _tick_sampler),
        ("tick_silence", _tick_silence),
        ("gap_guard", _gap_guard),               # سد الثغرات لكل مفتوح
        ("gap_audit", _gap_audit),               # ولا يتم فقدان
        ("endpoint_probe", _endpoint_probe),     # تقوي نقاط الخوادم
        ("replay_watcher", _replay_watcher),     # دون انهيار
        ("session_watcher", _session_watcher),
        ("harvester", _harvester),
        ("memory_guard", _memory_guard),
        ("disk_guard", _disk_guard),
        ("load_shedder", _load_shedder),
        ("heartbeat", _heartbeat),
        ("metrics", _metrics),
        ("selftest", _selftest),                 # تشخيص ذاتي دوري
    ]


def v14_print_banner() -> None:
    """يطبع بانر طبقة التقوية — يُستدعى من __main__ بعد نجاح الدخول."""
    try:
        print()
        print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
        print(f"{Colors.BOLD}  V14 STRENGTHENING LAYER ACTIVE "
              f"(طبقة تقوية الخادم){Colors.RESET}")
        modules = [
            "تفرز الطلبات: بوابة أولوية (OPENING > GAP_FILL > SCROLL > PRELOAD)",
            "سد الثغرات الأصلي يُنفَّذ على كل عملة تم فتحها — ولا فقدان",
            "التكس لا ينام: مضخة مُيقَظة بالأحداث + كاشف فقدان التيكات",
            "تقوي نقاط الخوادم: مسابر RTT + قاطع دائرة + تقرير نطاقات",
            "دون انهيار: مشرف كل حلقة + خطافات استثناء + حارس ذاكرة/قرص",
            "إعادة تشغيل البث بعد كل عودة (نمط pyquotex subscription replay)",
            "نبضة حياة qx_server_heartbeat.json كل 10 ثوانٍ",
        ]
        for i, m in enumerate(modules, 1):
            print(f"  {Colors.DIM}{i}) {m}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    except Exception:
        pass


def v14_line_inventory() -> dict:
    """جرد أسطر الخادم — إثبات وصول الكود للعدد المطلوب (طلب المستخدم:
    «الكود يجب ان يصل الى 15الف سطر على الاقل» مع التطبيق)."""
    try:
        src_file = globals().get("__file__", "")
        total = 0
        if src_file and _v14_os.path.exists(src_file):
            with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
                total = sum(1 for _ in f)
        return {
            "server_lines": total,
            "v14_layer_marker": "# v14 الجزء C — الوحدات 7 و 8 و 9",
        }
    except Exception:
        return {"server_lines": 0, "v14_layer_marker": ""}


# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء D — الوحدة 10: التشخيص الذاتي (V14 SELF-DIAGNOSTICS)
# ════════════════════════════════════════════════════════════════════════════
# لماذا؟ «طريقة العمل دون انهيار الخوادم» تحتاج إثباتاً لا ادعاءً.
# هذه الوحدة تفحص نفسها عند الإقلاع وتعطي الأمر الجاهز للمشغل/التطبيق:
#   V14_API["selftest"]() → تقرير نجاح/فشل كل ضمانة من ضمانات v14:
#     1) بوابة الطلبات: الأولوية تُخدم قبل الخلفية، سلسلة العملة متسلسلة،
#        dedupe يعيد نفس الرد، مهلة الوفاة تفشل سريعاً لا تعليقاً.
#     2) دلو الرموز: المعدل محدود فعلاً.
#     3) متتبع التيكات: تصنيف NEW/DUP/STALE + كشف الفجوة (لا فقدان صامت).
#     4) قاطع الدائرة: CLOSED→OPEN→HALF_OPEN→CLOSED كلها تتحول صحيحة.
#     5) سجل الجلسة: يكتب ويقرأ (JSONL + دوران الحجم).
#     6) النبضة: payload مكتمل المفاتيح.
#     7) المشرف: يعيد تشغيل حلقة ماتة ويحصي الانهيار.
# كل الفحوصات تعمل على نُسخ معزولة (لا تلمس حالة الخادم الحية أبداً).
# ════════════════════════════════════════════════════════════════════════════

class V14SelfTest:
    """تشخيص ذاتي لطبقة v14 — كل فحص على نسخة معزولة بلا لمس حالة حية."""

    def __init__(self) -> None:
        self.results: _v14_List[Tuple[str, bool, str]] = []

    # ─────────────── أدوات مساعدة ───────────────
    def _record(self, name: str, ok: bool, note: str = "") -> None:
        self.results.append((name, bool(ok), note))

    # ─────────────── 1) بوابة الطلبات ───────────────
    async def _test_gate_priority(self) -> None:
        """الأولوية: طلب PRELOAD يُدخل أولاً ثم OPENING — OPENING يُخدم أولاً."""
        gate = V14RequestGate()
        served: _v14_List[str] = []

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            served.append(api_symbol)
            await _v14_asyncio.sleep(0.01)
            return [{"fake": api_symbol}]

        # نستبدل جلب العامل بنسخة الاختبار عبر التصحيح المحلي للنطاق
        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            fut_bg = gate.submit_nowait("BG_PRELOAD_TEST", 0, 60, 60,
                                        priority=int(RequestPriority.PRELOAD),
                                        label="selftest")
            fut_fg = gate.submit_nowait("FG_OPENING_TEST", 0, 60, 60,
                                        priority=int(RequestPriority.OPENING),
                                        label="selftest")
            worker = _v14_asyncio.create_task(gate.worker())
            await _v14_asyncio.wait_for(fut_fg, timeout=5.0)
            await _v14_asyncio.wait_for(fut_bg, timeout=5.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            ok = (served and served[0] == "FG_OPENING_TEST"
                  and len(served) == 2)
            self._record("gate.priority.order", ok,
                         f"served={served} (expected FG first)")
        except Exception as e:
            self._record("gate.priority.order", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_dedupe(self) -> None:
        """نفس الطلب المعلق مرتين → نفس الرد (لا طلب مكرر يختلط)."""
        gate = V14RequestGate()
        calls = []

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            calls.append(api_symbol)
            await _v14_asyncio.sleep(0.05)
            return [{"fake": api_symbol}]

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            worker = _v14_asyncio.create_task(gate.worker())
            fut1 = gate.submit_nowait("DEDUPE_TEST", 100, 60, 60,
                                      priority=int(RequestPriority.OPENING))
            fut2 = gate.submit_nowait("DEDUPE_TEST", 100, 60, 60,
                                      priority=int(RequestPriority.OPENING))
            ok_same = fut1 is fut2
            await _v14_asyncio.wait_for(
                _v14_asyncio.gather(fut1, fut2), timeout=5.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            self._record("gate.dedupe.same_future", ok_same and len(calls) == 1,
                         f"calls={len(calls)} (expected 1)")
        except Exception as e:
            self._record("gate.dedupe.same_future", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_expiry(self) -> None:
        """مهلة الوفاة: طلب بقي في الطابور بعد مهلته يفشل سريعاً (لا تعليق).

        الترتيب المتعمد: نرسل الطلب بمهلة 0.2 ثانية، لا نشغّل العامل إلا
        بعد انقضائها — فالعامل عند السحب يفحص المهلة ويرفض فوراً."""
        gate = V14RequestGate()

        async def fake_slow_fetch(api_symbol, end_time, seconds, period,
                                  foreground=False, timeout=None, retries=2):
            await _v14_asyncio.sleep(1.5)
            return []

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_slow_fetch
        try:
            fut = gate.submit_nowait("EXPIRE_TEST", 0, 60, 60,
                                     priority=int(RequestPriority.OPENING),
                                     wait_deadline=0.2)
            await _v14_asyncio.sleep(0.3)   # انقضت المهلة قبل بدء العامل
            worker = _v14_asyncio.create_task(gate.worker())
            failed_fast = False
            t0 = time.monotonic()
            try:
                await _v14_asyncio.wait_for(fut, timeout=2.0)
            except Exception:
                failed_fast = (time.monotonic() - t0) < 1.0
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            self._record("gate.deadline.fails_fast", failed_fast,
                         f"elapsed={time.monotonic() - t0:.2f}s")
        except Exception as e:
            self._record("gate.deadline.fails_fast", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_asset_chain(self) -> None:
        """سلسلة العملة: طلبان لنفس العملة لا يتداخلان — التسلسل مطلق."""
        gate = V14RequestGate()
        active = {"n": 0, "max": 0}

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            active["n"] += 1
            active["max"] = max(active["max"], active["n"])
            await _v14_asyncio.sleep(0.03)
            active["n"] -= 1
            return []

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            worker = _v14_asyncio.create_task(gate.worker())
            futs = [gate.submit_nowait(f"CHAIN_TEST_{i}", 0, 60, 60,
                                       priority=int(RequestPriority.PRELOAD))
                    for i in range(4)]
            await _v14_asyncio.wait_for(_v14_asyncio.gather(*futs), timeout=10.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            # عامل واحد → التزامن الفعلي لا يتجاوز 1 أبداً
            self._record("gate.asset_chain.never_parallel",
                         active["max"] == 1, f"max_concurrent={active['max']}")
        except Exception as e:
            self._record("gate.asset_chain.never_parallel", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    # ─────────────── 2) دلو الرموز ───────────────
    def _test_token_bucket(self) -> None:
        """دلو الرموز: المعدل محدود — 5 محاولات فورية على دلو rate=0.5
        ينجح منها فقط ما فيه رموز (سعة 1)."""
        bucket = V14TokenBucket(rate=0.5, capacity=1.0)
        got = sum(1 for _ in range(5) if bucket.try_acquire())
        self._record("bucket.limits_burst", got == 1, f"acquired={got}/5")

    # ─────────────── 3) متتبع التيكات ───────────────
    def _test_tracker(self) -> None:
        """تصنيف التيكات: NEW ثم DUP ثم STALE ثم قفزة كبيرة=فقدان محتمل.

        التتابع واقعي: تيكات متقاربة 2s تؤسس متوسط الفاصل، ثم تيك بعده
        100 ثانية (8× أضعاف المتوسط) = قفزة شاذة → GAP."""
        tr = V14TickTracker("SELFTEST")
        c1 = tr.ingest(1000, 1.0)                 # NEW
        c2 = tr.ingest(1000, 1.05)                # DUP (سعر أحدث بنفس الثانية)
        c3 = tr.ingest(999, 1.0)                  # STALE (أقدم)
        tr.ingest(1002, 1.1)                      # NEW (فاصل 2s)
        tr.ingest(1004, 1.15)                     # NEW (فاصل 2s)
        c6 = tr.ingest(1104, 1.2)                 # قفزة 100s → GAP
        ok = (c1 == TickClassification.NEW
              and c2 == TickClassification.DUPLICATE
              and c3 == TickClassification.STALE
              and c6 == TickClassification.GAP
              and tr.gap_events == 1)
        self._record("tracker.classification+gap", ok,
                     f"{c1}/{c2}/{c3}/{c6} gaps={tr.gap_events}")

    # ─────────────── 4) قاطع الدائرة ───────────────
    def _test_breaker(self) -> None:
        """الدورة الكاملة: CLOSED→OPEN (5 أخطاء)→HALF_OPEN (بعد استشفاء)→CLOSED."""
        br = V14CircuitBreaker("selftest", failure_threshold=3,
                               recovery_interval=0.05, half_open_successes=2)
        for _ in range(3):
            br.record_failure("sim")
        opened = br.state() == BreakerState.OPEN
        time.sleep(0.06)
        probe = br.allow_probe()                  # استشفاء
        half = br.state() == BreakerState.HALF_OPEN
        br.record_success()
        br.record_success()
        closed = br.state() == BreakerState.CLOSED
        self._record("breaker.full_cycle", opened and probe and half and closed,
                     f"open={opened} half={half} closed={closed}")

    # ─────────────── 5) سجل الجلسة ───────────────
    def _test_journal(self) -> None:
        """السجل يكتب ويقرأ — JSONL صالح."""
        tmp = _v14_os.path.join(_v14_os.path.dirname(V14_JOURNAL.path),
                                "qx_v14_selftest_journal.jsonl")
        j = V14SessionJournal(path=tmp, max_bytes=1024 * 1024)
        j.record("selftest_write", k=1, s="نص عربي")
        j.record("selftest_write2", k=2)
        tail = j.tail(2)
        ok = (len(tail) == 2 and tail[-1]["event"] == "selftest_write2"
              and tail[0]["s"] == "نص عربي")
        self._record("journal.write_read_utf8", ok, f"n={len(tail)}")

    # ─────────────── 6) النبضة ───────────────
    def _test_heartbeat(self) -> None:
        """payload النبضة يحتوي كل المفاتيح الحرجة."""
        try:
            hb = V14Heartbeat()
            data = hb.payload()
            required = {"time", "pid", "uptime_s", "connection_alive",
                        "gate", "supervisor", "session", "pressure",
                        "opened_assets", "memory_rss_mb"}
            missing = required - set(data.keys())
            self._record("heartbeat.payload_complete", not missing,
                         f"missing={missing or 'none'}")
        except Exception as e:
            self._record("heartbeat.payload_complete", False, f"error: {e}")

    # ─────────────── 7) المشرف ───────────────
    async def _test_supervisor_restart(self) -> None:
        """المشرف يعيد تشغيل حلقة ماتة ويحصي الانهيار.

        ملاحظة: supervise لا يعود أبداً بالتصميم (حماية دون انهيار) —
        الفحص يشغّله مهمة، يراقب عدّادات الحالة، ثم يلغيه."""
        runs = {"n": 0}

        async def dying_loop():
            runs["n"] += 1
            await _v14_asyncio.sleep(0.02)
            if runs["n"] <= 2:
                raise RuntimeError("simulated crash for selftest")
            # من هنا تكمل طبيعياً حتى الإلغاء — والمشرف يعيد تشغيلها

        sup = V14Supervisor()
        task = _v14_asyncio.create_task(
            sup.supervise("selftest_dying", dying_loop))
        # انتظر حتى 3 تشغيلات (2 انهيار + إعادة) أو مهلة 15 ثانية
        for _ in range(300):
            st = sup.status_of("selftest_dying")
            if st.runs >= 3:
                break
            await _v14_asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except _v14_asyncio.CancelledError:
            pass
        st = sup.status_of("selftest_dying")
        ok = st.runs >= 3 and st.crashes >= 2
        self._record("supervisor.restarts_dead_loop", ok,
                     f"runs={st.runs} crashes={st.crashes}")

    # ─────────────── 8) backoff ───────────────
    def _test_backoff(self) -> None:
        """backoff أُسّي مهزوز — ضمن حدود pyquotex."""
        d0 = v14_backoff_delay(0, base=1.0, cap=30.0, jitter=0.0)
        d3 = v14_backoff_delay(3, base=1.0, cap=30.0, jitter=0.0)
        d10 = v14_backoff_delay(10, base=1.0, cap=30.0, jitter=0.0)
        ok = (abs(d0 - 1.0) < 1e-9 and abs(d3 - 8.0) < 1e-9
              and d10 == 30.0)
        self._record("backoff.exponential+cap", ok,
                     f"d0={d0} d3={d3} d10={d10}")

    # ─────────────── التنفيذ الكامل ───────────────
    async def run_all(self) -> dict:
        self.results.clear()
        self._test_backoff()
        self._test_tracker()
        self._test_breaker()
        self._test_journal()
        self._test_heartbeat()
        self._test_token_bucket()
        await self._test_gate_priority()
        await self._test_gate_dedupe()
        await self._test_gate_expiry()
        await self._test_gate_asset_chain()
        await self._test_supervisor_restart()
        passed = sum(1 for _, ok, _ in self.results if ok)
        total = len(self.results)
        ok_all = passed == total
        V14_JOURNAL.record("selftest", passed=passed, total=total)
        V14_METRICS.inc("v14.selftest.runs")
        if not ok_all:
            V14_METRICS.inc("v14.selftest.failures")
        return {
            "ok": ok_all,
            "passed": passed,
            "total": total,
            "results": [
                {"name": name, "ok": ok, "note": note}
                for name, ok, note in self.results
            ],
        }


async def v14_selftest() -> dict:
    """التشخيص الذاتي الكامل — V14_API["selftest"]."""
    return await V14SelfTest().run_all()


# أضف التشخيص الذاتي للواجهة العامة
try:
    V14_API["selftest"] = v14_selftest
except Exception:
    pass


async def v14_selftest_loop() -> None:
    """تشخيص ذاتي دوري خفيف (كل 10 دقائق) — نفس الفحوصات، يحصي الفشل."""
    await _v14_asyncio.sleep(60.0)
    while True:
        try:
            await _v14_asyncio.sleep(600.0)
            try:
                res = await v14_selftest()
                if not res["ok"]:
                    V14_JOURNAL.record("selftest_periodic_fail",
                                       passed=res["passed"],
                                       total=res["total"])
                    try:
                        logmsg(f"[v14-selftest] periodic: {res['passed']}/"
                               f"{res['total']} passed — see journal")
                    except Exception:
                        pass
            except Exception as e:
                V14_JOURNAL.record("selftest_error", error=str(e)[:200])
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=2.0, cap=15.0)


if __name__ == "__main__":
    # ════════════════════════════════════════════════════════════════════
    # v13.0 — Preload Engine (بطلب المستخدم):
    #   - نفس تدفق v12: نطاق تلقائي + دخول (البريد وكلمة المرور فقط) + جدول
    #     العملات الكامل في الترمينال.
    #   - جديد: بعد الدخول مباشرة يجلب 300 شمعة لـ BRLUSD_otc (عملة فتح الشارت)
    #     مع حالتها ونسبة دفعها، ثم يجلب 300 شمعة لبقية الأصول المفتوحة واحدة
    #     تلو الأخرى، ويشغّل البث الحي لكل عملة حتى يكون أي شارت جاهزاً فوراً.
    #   - جديد: fetch_older_batch() تجلب دفعة 300 شمعة أقدم للتمرير للخلف —
    #     جاهزة على الخادم، وربطها بالتطبيق يُضاف لاحقاً (ليس الآن).
    #   - جديد: التيكات في الذاكرة فقط وتُحذف تلقائياً بعد 5 دقائق + تدوير
    #     السجل + ترميم candles.db — حتى لا يمتلئ القرص أبداً.
    #   - طريقة الدخول وطريقة جلب الشموع كما هي دون أي تغيير.
    # ════════════════════════════════════════════════════════════════════
    print()
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  QX SERVER v14.1 — Chart-Driven Loading + Strengthened Server (طبقة تقوية){Colors.RESET}")
    print(f"  {Colors.DIM}BRLUSD_otc: 300 شمعة فوراً بعد الدخول + الحالة ونسبة الدفع{Colors.RESET}")
    print(f"  {Colors.DIM}أي عملة أخرى: 300 شمعة تُجلب فقط عند فتح شارتها — واحدة تلو الأخرى{Colors.RESET}")
    print(f"  {Colors.DIM}التمرير للخلف: دفعة 300 شمعة أقدم في كل تمرير{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")

    # v12/v13: لا يوجد جدول حي — اطبع رسائل السجل مباشرة
    globals()['_STATUS_MESSAGES_QUEUE'] = None

    # ---- STAGE 1: النطاق تلقائياً حسب البلد (بدون أي سؤال) ----
    print()
    print(f"{Colors.BOLD}  Domain: detecting country automatically ...{Colors.RESET}")
    resolve_qx_host()
    globals()['QX_HOST'] = QX_HOST
    _geo_country = _GEO_CACHE.get("country") or "unknown"
    print(f"{Colors.GREEN}  Country: {_geo_country}  ->  Domain: {QX_HOST}{Colors.RESET}")

    # ---- STAGE 2: تسجيل الدخول — البريد وكلمة المرور فقط ----
    # نفس كود v10/v11/v12 حرفياً (حفظ الجلسة + connect_quotex + نفس المهلات).
    should_force = session_manager.should_force_fresh()
    saved_email = session_manager.get_saved_email()
    success = False
    if saved_email and not should_force:
        print(f"{Colors.GREEN}Found saved email: {saved_email}{Colors.RESET}")
        PASSWORD_INPUT = input(f"{Colors.CYAN} Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(saved_email, PASSWORD_INPUT, force_fresh=False, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=180)
    if not success:
        print()
        EMAIL_INPUT = input(f"{Colors.CYAN}Email: {Colors.RESET}").strip()
        PASSWORD_INPUT = input(f"{Colors.CYAN}Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(EMAIL_INPUT, PASSWORD_INPUT, force_fresh=True, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=300)
    if not success:
        print(f"\n{Colors.RED}[FAILED] Could not connect after all attempts.{Colors.RESET}")
        sys.exit(1)

    # ---- STAGE 3: المراقبة + القائمة + التحميل المسبق + البث الحي ----
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass
    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # جدول العملات الكامل (الدفع + مفتوح/مغلق) — كما في v12 تماماً:
    asyncio.run_coroutine_threadsafe(asset_payout_monitor(), ASYNC_LOOP)
    # v13: BRLUSD_otc فوراً (300 شمعة + بث حي) ثم بقية الأصول المفتوحة واحدة تلو الأخرى:
    asyncio.run_coroutine_threadsafe(preload_all_assets(), ASYNC_LOOP)
    # v13.1 (طلب المستخدم): آلية سد الثغرات تعمل الآن فعلاً — كانت معرّفة في
    # الكود بلا تشغيل (لذلك ظهرت فراغات في الشموع). نفس الآلية نفسها بلا أي تغيير:
    asyncio.run_coroutine_threadsafe(mt4_gap_filler(), ASYNC_LOOP)
    # v13: كاش التيكات في الذاكرة + حذف التيكات الأقدم من 5 دقائق:
    asyncio.run_coroutine_threadsafe(tick_cache_collector(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(tick_retention_loop(), ASYNC_LOOP)
    # v13: ترميم candles.db (أحدث 5000 شمعة لكل عملة) — القرص لا يمتلئ أبداً:
    asyncio.run_coroutine_threadsafe(candlestore_trim_loop(), ASYNC_LOOP)

    # ════════ v14.0: طبقة التقوية — كل الحلقات الجديدة تحت المشرف ════════
    # (دون انهيار الخوادم): تفرز الطلبات + سد الثغرات على كل مفتوح +
    # التكس لا ينام + تقوي النقاط + مشرف الحلقات + النبضة — والكود
    # الأساسي أعلاه كما هو حرفياً.
    try:
        for _v14_name, _v14_factory in v14_build_background_loops():
            asyncio.run_coroutine_threadsafe(
                v14_supervise(_v14_name, _v14_factory), ASYNC_LOOP)
        v14_print_banner()
    except Exception as _v14e:
        logmsg(f"[v14] layer issue (server continues unchanged): {_v14e}")

    print()
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  Connected! Chart opener ready + chart-driven loading ...{Colors.RESET}")
    print(f"  {Colors.DIM}1) BRLUSD_otc: 300 شمعة فوراً + الحالة ونسبة الدفع + بث حي{Colors.RESET}")
    print(f"  {Colors.DIM}2) أي عملة أخرى: تُجلب 300 شمعة فقط عند فتح شارتها (واحدة تلو الأخرى){Colors.RESET}")
    print(f"  {Colors.DIM}3) التمرير للخلف: دفعة 300 شمعة أقدم في كل تمرير{Colors.RESET}")
    print(f"  {Colors.DIM}4) الجدول الكامل (الدفع + مفتوح/مغلق) يُطبع ويُحدّث تلقائياً{Colors.RESET}")
    print(f"  {Colors.DIM}5) سد الثغرات يعمل: أي فجوة تُملأ بشموع مسطحة — لا فراغات{Colors.RESET}")
    print(f"  {Colors.DIM}6) التيكات في الذاكرة فقط وتُحذف بعد 5 دقائق — القرص لا يمتلئ{Colors.RESET}")
    print(f"  {Colors.DIM}للخروج: Ctrl+C{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")

    try:
        # الخيط الرئيسي يبقى حيّاً فقط — كل العمل في حلقات الخلفية
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print(f"{Colors.RED}Stopped{Colors.RESET}")
        writer_thread.running = False
