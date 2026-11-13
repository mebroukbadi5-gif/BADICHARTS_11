#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test مع بيانات محاكاة للتأكد من عرض الجدول كاملاً."""
import os, sys
os.chdir('/home/z/my-project/download')
sys.path.insert(0, '/home/z/my-project/download')
import qx_server_v11 as m
import uvicorn

m._update_assets_state([
    {"asset": "EURUSD_otc", "name": "EUR/USD (OTC)", "payout": 92, "turbo_payout": 88, "profit_1m": 90, "profit_5m": 85, "open": True},
    {"asset": "GBPUSD_otc", "name": "GBP/USD (OTC)", "payout": 75, "turbo_payout": 70, "profit_1m": 72, "profit_5m": 70, "open": True},
    {"asset": "USDJPY_otc", "name": "USD/JPY (OTC)", "payout": 55, "turbo_payout": None, "profit_1m": 50, "profit_5m": 48, "open": False},
    {"asset": "BTCUSD_otc", "name": "Bitcoin (OTC)", "payout": None, "turbo_payout": 60, "profit_1m": None, "profit_5m": None, "open": None},
    {"asset": "XAUUSD_otc", "name": "Gold (OTC)", "payout": 84, "turbo_payout": 80, "profit_1m": 82, "profit_5m": 79, "open": True},
])
m.ASSETS_PAYOUT_STATE["host"] = "quotex.com"
uvicorn.run(m.WEB_APP, host='127.0.0.1', port=8124, log_level='error')
