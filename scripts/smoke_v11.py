#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test: يستورد الوحدة ويشغل واجهة FastAPI على منفذ اختبار فقط."""
import os
import sys

os.chdir('/home/z/my-project/download')
sys.path.insert(0, '/home/z/my-project/download')

import qx_server_v11 as m  # noqa: E402
import uvicorn  # noqa: E402

print('FASTAPI_AVAILABLE =', m.FASTAPI_AVAILABLE)
print('WEB_APP =', type(m.WEB_APP).__name__)
uvicorn.run(m.WEB_APP, host='127.0.0.1', port=8123, log_level='error')
