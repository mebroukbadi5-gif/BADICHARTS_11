# -*- coding: utf-8 -*-
"""build_live_app.py — PART 2: محرك الخادم داخل Backend + QML الدخول الحقيقي"""
import sys

SRC = "/home/z/my-project/gh_repo/BadiChartsStudio_live.py.part1"
DST = "/home/z/my-project/gh_repo/BadiChartsStudio_live.py"

src = open(SRC, encoding="utf-8").read()
edits = []


def rep(old, new, count=1, tag=""):
    global src
    found = src.count(old)
    if found != count:
        raise SystemExit(f"[FAIL] anchor not unique ({found}x, want {count}x): {tag or old[:80]}")
    src = src.replace(old, new)
    edits.append(tag or old[:60])


# ════════════════ 12) إشارة أحداث الخادم ════════════════
rep("""    paidCmd = Signal(str)                  # أمر تحكم بعيد صالح: تشغيل/إيقاف مؤشر مدفوع (طلب المستخدم)""",
    """    paidCmd = Signal(str)                  # أمر تحكم بعيد صالح: تشغيل/إيقاف مؤشر مدفوع (طلب المستخدم)
    qxEvent = Signal(str)                  # LIVE SERVER EDITION: أحداث خادم QX (الدخول/لوحة العملات/دفعات التمرير)""", tag="qxEvent signal")

# ════════════════ 13) Backend.__init__ — العملة الافتراضية + بلا شموع وهمية ════════════════
rep("""        self._market = "real"        # قسم الحساب الحقيقي/التجريبي حُذف — يبقى وسم السوق للعملات OTC فقط
        self._asset = cfg.get("asset", "EUR/USD")
        self._tf = cfg.get("tf", "1m")
        if not any(a["name"] == self._asset for a in ASSETS["real"] + ASSETS["otc"]):
            self._asset = "EUR/USD"
        board_names = [b["name"] for b in BOARD]
        saved_added = [n for n in (cfg.get("added") or []) if isinstance(n, str) and n in board_names]
        if not saved_added:
            saved_added = [n for n in ("EUR/USD", "BTC/USD") if n in board_names] or board_names[:2]
        self._added = list(dict.fromkeys(saved_added))""",
    """        self._market = "real"        # قسم الحساب الحقيقي/التجريبي حُذف — يبقى وسم السوق للعملات OTC فقط
        # LIVE SERVER EDITION (طلب المستخدم): العملة الافتراضية التي يفتح بها الشارت
        # هي BRLUSD_otc — يجلبها الكود مباشرة فور تسجيل الدخول (300 شمعة + الحالة + الدفع)
        self._asset = cfg.get("asset") or "BRL/USD OTC"
        self._tf = cfg.get("tf", "1m")
        if not isinstance(self._asset, str) or not self._asset.strip():
            self._asset = "BRL/USD OTC"
        # LIVE SERVER EDITION: شريط العملات يبدأ بعملة فتح الشارت — وعند وصول لوحة
        # العملات الحقيقية من الخادم تُصفّى القوائم عليها تلقائياً
        self._added = [n for n in (cfg.get("added") or []) if isinstance(n, str) and n.strip()]
        if not self._added:
            self._added = ["BRL/USD OTC"]""", tag="init asset default")

rep("""        self._live = True        # البث الحي يعمل مباشرة دائمًا — الشموع متحركة بلا زر (طلب المستخدم)
        self._tick = 0
        self._candles = generate_candles(self._asset, self._tf)""",
    """        self._live = True        # البث الحي يعمل مباشرة دائمًا — الشموع متحركة بلا زر (طلب المستخدم)
        self._tick = 0
        # LIVE SERVER EDITION (طلب المستخدم): الشموع الوهمية انزعت — الشموع الحقيقية
        # تصل من خادم QX بعد الدخول (BRLUSD_otc: 300 شمعة فوراً، ثم بقية العملات)
        self._candles = []
        self._qx_logged = False        # الدخول الحقيقي عبر خادم Quotex تم
        self._qx_login_busy = False    # محاولة دخول جارية الآن
        self._qx_board = []            # لوحة العملات الحقيقية [{name,symbol,payout,open,otc,flag}]
        self._qx_symbols = {}          # اسم العرض -> رمز الخادم (BRL/USD OTC -> BRLUSD_otc)
        self._qx_feed_key = ("", "")   # مفتاح الغذاء الحالي (العملة، الفريم)
        self._qx_last_sig = None       # بصمة آخر شمعة مُرسلة للشارت (t, c)
        self._qx_older_busy = False    # دفعة تمرير للخلف جارية
        self._qx_pre_log = 0.0         # خنق سجلات حالة التحميل المسبق""", tag="init feed")

rep("""        # تشغيل المؤقت فعليًا — بلا هذا السطر كان محرك الشموع الحية متوقفًا تمامًا
        # ولهذا لم تكن شموع جديدة تظهر في التطبيق (الشارت متجمد)
        self._timer.start()""",
    """        # تشغيل المؤقت فعليًا — بلا هذا السطر كان محرك الشموع الحية متوقفًا تمامًا
        # ولهذا لم تكن شموع جديدة تظهر في التطبيق (الشارت متجمد)
        self._timer.start()
        # ── LIVE SERVER EDITION: مضخة بيانات خادم QX ──
        # تسحب الأسعار الحية من محرك الخادم (يعمل داخل التطبيق) وتدفعها للشارت،
        # وتراقب لوحة العملات (الدفع + مفتوح/مغلق) وحالة التحميل المسبق.
        self._qxT = QTimer(self)
        self._qxT.setInterval(400)
        self._qxT.timeout.connect(self._qx_poll)
        self._qxT.start()""", tag="qx poll timer")

# ════════════════ 14) _on_tick — بلا محاكاة محلية ════════════════
rep("""    def _on_tick(self):
        # التغذية الحية تعمل فقط عند تفعيل اللايف، أما تسويات الإشارات والصفقات فتعمل دائمًا
        if self._live:
            cfg = self._asset_cfg()
            tf = max(5, self._tf_sec())
            # شمعة جديدة عند مرور حد الفريم بالتوقيت الحقيقي لا بعدد التكات من الإقلاع —
            # الانحراف عن حدود الدقيقة الحقيقية كان يجعل العدّ التنازلي يعلق على 00
            # بقية الدقيقة (يعمل في أول شمعة ثم يتوقف — ملاحظة المستخدم)
            now = int(time.time())
            boundary = now - (now % tf)
            cur = self._candles[-1]
            if cur["t"] < boundary:
                # الفريم انتهى فعلاً — أغلق الشمعة وافتح شمعة الحد الحقيقي،
                # واملأ أي فجوة لو تأخرت التكة (نوم/تعليق النظام) بحد أقصى 500 شمعة
                gap = min(int((boundary - cur["t"]) // tf), 500)
                for _ in range(gap):
                    self._candles.append(new_candle(self._candles[-1], tf, cfg["vol"]))
                if len(self._candles) > 1500:
                    self._candles = self._candles[-1200:]
            else:
                self._candles[-1] = step_candle(cur, cfg["vol"])
            # الترتيب مهم: احسب قيم المؤشرات أولًا ثم ادفع الشمعة —
            # الترتيب العكسي كان يرسم الشمعة الجديدة بدون قيمة المؤشر لشمعة كاملة
            self._compute_py()
            self.candlesChanged.emit()
        self._check_sig_results()""",
    """    def _on_tick(self):
        # LIVE SERVER EDITION (طلب المستخدم): الشموع الوهمية انزعت — التغذية الحية
        # تأتي الآن من خادم Quotex عبر _qx_poll() كل 400ms. يبقى هنا فقط تسوية
        # نتائج الإشارات (WIN/LOSS) لأنها تعمل دائماً بغض النظر عن التغذية.
        self._check_sig_results()

    # ═════════════════════════════════════════════════════════════════════
    #  LIVE SERVER EDITION — محرك خادم Quotex داخل التطبيق
    #  نفس الخادم الذي يعمل في الترمينال (qx_server_v13.py) لكن يُقاد من الواجهة:
    #  دخول حقيقي، BRLUSD_otc فوراً (300 شمعة)، بقية العملات واحدة تلو الأخرى،
    #  بث حي لكل العملات، ودفعات 170 شمعة عند التمرير للوراء.
    # ═════════════════════════════════════════════════════════════════════
    _QX_FEED_CAP = 3000          # حد الشموع في ذاكرة الواجهة (نفس سياسة الخادم)
    _QX_FEED_TRIM = 2600         # القص عند التجاوز (نفس سلوك الجسر في الصفحة)

    def _emit_qx(self, obj):
        \"\"\"بث حدث خادم QML (الدخول / لوحة العملات / دفعات التمرير).\"\"\"
        try:
            self.qxEvent.emit(json.dumps(obj, ensure_ascii=False))
        except Exception:
            pass

    @staticmethod
    def _api_from_display(name):
        \"\"\"اسم العرض (BRL/USD OTC) -> رمز الخادم (BRLUSD_otc).\"\"\"
        s = str(name or "").strip()
        otc = s.upper().endswith(" OTC")
        base = s[:-4].strip() if otc else s
        base = base.replace("/", "").upper()
        return base + ("_otc" if otc else "")

    @staticmethod
    def _display_from_api(sym):
        \"\"\"رمز الخادم (BRLUSD_otc) -> اسم العرض (BRL/USD OTC).\"\"\"
        s = str(sym or "").strip()
        if not s:
            return ""
        otc = s.lower().endswith("_otc")
        base = s[:-4] if otc else s
        b = base.upper()
        suffix = " OTC" if otc else ""
        quotes = ("USDT", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD",
                  "BRL", "PKR", "INR", "TRY", "MXN", "ARS", "COP", "EGP", "BDT", "NGN")
        for q in quotes:
            if b.endswith(q) and len(b) > len(q):
                head = b[:-len(q)]
                if head:
                    return head + "/" + q + suffix
        if len(b) == 6 and b.isalpha():
            return b[:3] + "/" + b[3:] + suffix
        return b + suffix

    @staticmethod
    def _fmt_engine_candles(candles):
        \"\"\"شموع الخادم {time,open,...} -> غذاء الصفحة {t,o,h,l,c,v}.\"\"\"
        out = []
        for c in candles or []:
            try:
                t = int(c.get("time", 0))
                o = float(c.get("open", 0)); h = float(c.get("high", 0))
                l = float(c.get("low", 0)); cl = float(c.get("close", 0))
                if t <= 0 or cl <= 0:
                    continue
                out.append({"t": t, "o": o, "h": h, "l": l, "c": cl,
                            "v": int(c.get("volume", 0) or 0)})
            except Exception:
                continue
        return out

    def _qx_engine_candles(self, api):
        \"\"\"نسخة شموع العملة من ذاكرة الخادم (جاهزة دائماً — البث الحي يعمل داخلها).\"\"\"
        qx = _qx_module()
        if not qx or not api:
            return []
        try:
            a = qx._get_or_create_asset(api)
            return self._fmt_engine_candles(list(a.candles or []))
        except Exception:
            return []

    def _qx_build_board(self, entries):
        \"\"\"لوحة العملات الحقيقية من لقطة instruments في الخادم.\"\"\"
        board, symbols = [], {}
        for e in entries or []:
            sym = str((e or {}).get("asset") or "").strip()
            if not sym:
                continue
            disp = self._display_from_api(sym)
            if not disp or disp in symbols:
                continue
            payout = e.get("payout")
            try:
                payout = int(round(float(payout))) if payout is not None else 0
            except Exception:
                payout = 0
            opn = e.get("open")
            board.append({"name": disp, "symbol": sym, "payout": payout,
                          "open": bool(opn) if opn is not None else True,
                          "otc": sym.lower().endswith("_otc"),
                          "flag": pair_flag_uri(disp)})
            symbols[disp] = sym
        return board, symbols

    @staticmethod
    def _board_sig(board):
        try:
            return json.dumps([[b["name"], b["payout"], b["open"]] for b in board])
        except Exception:
            return ""

    def _qx_boot_board(self):
        \"\"\"لوحة الإقلاع: عملة فتح الشارت قبل وصول اللوحة الحقيقية من الخادم.\"\"\"
        if self._qx_board:
            return self._qx_board
        return [{"name": "BRL/USD OTC", "symbol": "BRLUSD_otc", "payout": 0,
                 "open": True, "otc": True, "flag": pair_flag_uri("BRL/USD OTC")}]

    def _qx_load_feed(self, force=False):
        \"\"\"تحميل غذاء الشارت الحقيقي للعملة/الفريم الحاليين من الخادم.\"\"\"
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if not api:
            return
        qx = _qx_module()
        if not qx:
            return
        tf_sec = self._tf_sec()
        key = (self._asset, self._tf)
        if tf_sec == 60:
            # فريم الدقيقة: شموع الخادم في الذاكرة (جاهزة من التحميل المسبق + البث الحي)
            candles = self._qx_engine_candles(api)
            if candles and (force or not self._candles or self._qx_feed_key != key):
                self._candles = candles[-self._QX_FEED_CAP:]
                self._qx_feed_key = key
        elif tf_sec < 60:
            # فريمات الثواني: تُبنى من تيكات الخادم الحية (نافذة 5 دقائق — سياسة الخادم)
            ticks = []
            try:
                d = qx._TICK_CACHE.get(api)
                if d:
                    ticks = list(d)
            except Exception:
                ticks = []
            feed = self._ticks_to_candles(ticks, tf_sec)
            if feed and (force or not self._candles or self._qx_feed_key != key):
                self._candles = feed
                self._qx_feed_key = key
        else:
            # فريمات أعلى من الدقيقة: جلب مباشر 300 شمعة بنفس طريقة الخادم الأصلية
            if force or not self._candles or self._qx_feed_key != key:
                self._qx_fetch_tf_async(api, tf_sec, 300)
                self._qx_feed_key = key

    def _qx_fetch_tf_async(self, api, tf_sec, count):
        \"\"\"جلب شموع فريم أعلى داخل حلقة الخادم (نفس CLIENT.get_candles الأصلي).\"\"\"
        qx = _qx_module()
        if not qx or getattr(qx, "CLIENT", None) is None:
            return
        asset_name, tf_key = self._asset, self._tf

        def _worker():
            try:
                end = int(time.time())
                fut = asyncio.run_coroutine_threadsafe(
                    qx.CLIENT.get_candles(api, end, count * tf_sec, tf_sec), qx.ASYNC_LOOP)
                res = fut.result(timeout=45)
                candles = self._qx_fmt_raw(res, tf_sec)[-count:]
                if candles and asset_name == self._asset and tf_key == self._tf:
                    self._candles = candles
                    self._qx_feed_key = (asset_name, tf_key)
                    self.candlesChanged.emit()
                    self._log("ok", f"loaded {len(candles)} candles — {asset_name} {tf_key}")
            except Exception as e:
                self._log("err", f"fetch {asset_name} {tf_key}: {str(e)[:120]}")

        threading.Thread(target=_worker, daemon=True, name="qxFetchTf").start()

    @staticmethod
    def _qx_fmt_raw(res, tf_sec):
        \"\"\"تنسيق رد الخادم لفريم أعلى: محاذاة على حدود الفريم + إزالة التكرار.\"\"\"
        out, seen = [], set()
        for c in res or []:
            try:
                if not isinstance(c, dict):
                    continue
                ts = int(float(c.get("time", c.get("timestamp", 0))))
                if ts <= 0:
                    continue
                t = ts - ts % tf_sec
                o = float(c.get("open", 0)); h = float(c.get("high", c.get("max", 0)))
                l = float(c.get("low", c.get("min", 0))); cl = float(c.get("close", 0))
                if o <= 0 or cl <= 0:
                    continue
                if t in seen:
                    continue
                seen.add(t)
                out.append({"t": t, "o": o, "h": max(h, o, cl), "l": min(l, o, cl),
                            "c": cl, "v": 0})
            except Exception:
                continue
        out.sort(key=lambda x: x["t"])
        return out

    @staticmethod
    def _ticks_to_candles(ticks, tf_sec):
        \"\"\"بناء شموع فريمات الثواني من تيكات الخادم (الذاكرة فقط).\"\"\"
        buckets = {}
        for tk in ticks or []:
            try:
                ts, price = int(tk[0]), float(tk[1])
            except Exception:
                continue
            if price <= 0 or ts <= 0:
                continue
            b = ts - ts % tf_sec
            d = buckets.get(b)
            if d is None:
                buckets[b] = {"t": b, "o": price, "h": price, "l": price, "c": price, "v": 1}
            else:
                if price > d["h"]:
                    d["h"] = price
                if price < d["l"]:
                    d["l"] = price
                d["c"] = price
                d["v"] += 1
        return [buckets[k] for k in sorted(buckets)]

    def _qx_merge_tail_full(self, new_feed):
        \"\"\"دمج غذاء الخادم مع غذاء الواجهة من الذيل فقط — رأس البيانات يبقى ثابتاً
        حتى لا يُعاد ضبط الشارت أثناء التمرير للخلف. يعيد True إن تغيّر شيء.\"\"\"
        old = self._candles
        if not new_feed:
            return False
        if not old:
            self._candles = new_feed
            return True
        last_new = new_feed[-1]
        added = [c for c in new_feed if c["t"] > old[-1]["t"]]
        changed = False
        if added:
            self._candles = old + added
            changed = True
        if self._candles[-1]["t"] == last_new["t"]:
            if (abs(self._candles[-1]["c"] - last_new["c"]) > 1e-12
                    or abs(self._candles[-1]["h"] - last_new["h"]) > 1e-12
                    or abs(self._candles[-1]["l"] - last_new["l"]) > 1e-12):
                self._candles[-1] = last_new
                changed = True
        if len(self._candles) > self._QX_FEED_CAP:
            self._candles = self._candles[-self._QX_FEED_TRIM:]
        return changed

    def _qx_extend_tail(self, px, tf_sec):
        \"\"\"مدّtail الشمعة الحية للفريمات غير الدقيقة من السعر الحي للخادم.\"\"\"
        if px <= 0:
            return False
        now = int(time.time())
        bucket = now - now % tf_sec
        if not self._candles:
            self._candles = [{"t": bucket, "o": px, "h": px, "l": px, "c": px, "v": 1}]
            return True
        last = self._candles[-1]
        if last["t"] == bucket:
            if (abs(px - last["c"]) > 1e-12 or px > last["h"] or px < last["l"]):
                last["c"] = px
                if px > last["h"]:
                    last["h"] = px
                if px < last["l"]:
                    last["l"] = px
                return True
            return False
        if bucket > last["t"]:
            self._candles.append({"t": bucket, "o": last["c"],
                                  "h": max(last["c"], px), "l": min(last["c"], px),
                                  "c": px, "v": 0})
            if len(self._candles) > self._QX_FEED_CAP:
                self._candles = self._candles[-self._QX_FEED_TRIM:]
            return True
        return False

    def _qx_poll(self):
        \"\"\"مضخة الخادم: لوحة العملات + التغذية الحية + حالة التحميل المسبق.\"\"\"
        if not self._qx_logged:
            return
        qx = _qx_module()
        if qx is None or getattr(qx, "CLIENT", None) is None:
            return
        # 1) لوحة العملات الحقيقية (الاسم + الدفع + مفتوح/مغلق) — تُدفع عند أي تغيير
        try:
            entries = qx._instruments_snapshot()
            if entries:
                board, symbols = self._qx_build_board(entries)
                if board and (symbols != self._qx_symbols
                              or self._board_sig(board) != self._board_sig(self._qx_board)):
                    self._qx_board = board
                    self._qx_symbols = symbols
                    real = set(symbols.keys())
                    self._added = [n for n in self._added if n in real]
                    if not self._added:
                        opener = self._display_from_api(qx.PRELOAD_FIRST_SYMBOL)
                        self._added = [opener if opener in real else board[0]["name"]]
                    self._emit_qx({"type": "board", "board": board})
                    self.addedChanged.emit()
        except Exception:
            pass
        # 2) التغذية الحية للشارت الحالي (الخادم يبث أسعار كل العملة باستمرار)
        try:
            self._qx_live_step()
        except Exception:
            pass
        # 3) حالة التحميل المسبق → سجل التطبيق (مخنوقة كل 3 ثوانٍ)
        try:
            now = time.time()
            if now - self._qx_pre_log >= 3.0:
                self._qx_pre_log = now
                info = qx._PRELOADED_INFO
                if info:
                    opener = qx.PRELOAD_FIRST_SYMBOL
                    o = info.get(opener)
                    n_stream = len(qx.ALL_STREAMING_ASSETS)
                    msg = (f"QX preload: {len(info)} assets loaded, {n_stream} streaming live"
                           + (f" | opener {opener}: {o['candles']} candles" if o else ""))
                    self._log("info", msg)
        except Exception:
            pass

    def _qx_live_step(self):
        \"\"\"خطوة التغذية الحية: تحديث شموع العملة الحالية من الخادم ثم الدفع للشارت.\"\"\"
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if not api:
            return
        qx = _qx_module()
        tf_sec = self._tf_sec()
        key = (self._asset, self._tf)
        if tf_sec == 60:
            candles = self._qx_engine_candles(api)
            if candles:
                if not self._candles or self._qx_feed_key != key:
                    self._candles = candles[-self._QX_FEED_CAP:]
                    self._qx_feed_key = key
                else:
                    self._qx_merge_tail_full(candles)
        elif tf_sec < 60:
            ticks = []
            try:
                d = qx._TICK_CACHE.get(api)
                if d:
                    ticks = list(d)
            except Exception:
                ticks = []
            feed = self._ticks_to_candles(ticks, tf_sec)
            if feed:
                if not self._candles or self._qx_feed_key != key:
                    self._candles = feed
                    self._qx_feed_key = key
                else:
                    self._qx_merge_tail_full(feed)
        else:
            px = 0.0
            try:
                a = qx._get_or_create_asset(api)
                px = float(a.price or 0.0)
            except Exception:
                px = 0.0
            if px <= 0:
                m1 = self._qx_engine_candles(api)
                if m1:
                    px = m1[-1]["c"]
            self._qx_extend_tail(px, tf_sec)
        # دفع التغيير للشارت فقط عند تغير آخر شمعة فعلاً (أداء)
        if self._candles:
            last = self._candles[-1]
            sig = (last["t"], round(float(last["c"]), 10), len(self._candles))
            if sig != self._qx_last_sig:
                self._qx_last_sig = sig
                if self._py_mods:
                    self._compute_py()
                self.candlesChanged.emit()

    # ---------- الدخول الحقيقي عبر خادم Quotex (بديل تسجيل الدخول الوهمي) ----------
    @Property(str, constant=True)
    def savedEmail(self):
        \"\"\"البريد المحفوظ لدى الخادم (للتذكير عند الدخول التالي).\"\"\"
        qx = _qx_module()
        try:
            return str(qx.session_manager.get_saved_email() or "")
        except Exception:
            return ""

    @Slot(str, str, bool)
    def qxLogin(self, email, password, remember):
        \"\"\"تشغيل محرك الخادم وتسجيل الدخول الحقيقي — يعمل في خيط منفصل حتى لا
        تتجمد الواجهة، ويبلّغ كل خطوة عبر qxEvent.\"\"\"
        if self._qx_login_busy:
            return
        self._qx_login_busy = True
        threading.Thread(target=self._qx_login_worker,
                         args=(str(email or "").strip(), str(password or ""), bool(remember)),
                         daemon=True, name="qxLogin").start()

    def _qx_login_worker(self, email, password, remember):
        L = T[self._lang]
        try:
            qx = _qx_module()
            if qx is None:
                self._emit_qx({"type": "login", "state": "err", "msg": L.get("qxEngine", "QX engine not found")})
                return
            self._emit_qx({"type": "login", "state": "busy", "msg": L.get("qxResolving", "...")})
            qx.resolve_qx_host()
            host = getattr(qx, "QX_HOST", "quotex.com")
            self._emit_qx({"type": "login", "state": "busy",
                           "msg": L.get("qxConnecting", "...") + " — " + host})
            # نفس تسجيل الدخول الأصلي حرفياً: جلسة محفوظة أولاً ثم دخول جديد
            fut = asyncio.run_coroutine_threadsafe(
                qx.connect_quotex(email, password, force_fresh=False, max_attempts=3),
                qx.ASYNC_LOOP)
            ok = bool(fut.result(timeout=300))
            if not ok:
                self._emit_qx({"type": "login", "state": "err", "msg": L.get("qxFail", "Login failed")})
                return
            # حلقات الخادم الخلفية — نفس تدفق تشغيل الخادم في الترمينال حرفياً
            loop = qx.ASYNC_LOOP
            self._emit_qx({"type": "login", "state": "busy", "msg": L.get("qxLoad", "...")})
            asyncio.run_coroutine_threadsafe(qx.health_monitor(), loop)
            asyncio.run_coroutine_threadsafe(qx.auto_reconnect(), loop)
            asyncio.run_coroutine_threadsafe(qx.keepalive_loop(), loop)
            asyncio.run_coroutine_threadsafe(qx.stale_message_watchdog(), loop)
            asyncio.run_coroutine_threadsafe(qx.asset_payout_monitor(), loop)
            # BRLUSD_otc فوراً (300 شمعة + الحالة + الدفع) ثم بقية العملات واحدة تلو الأخرى
            asyncio.run_coroutine_threadsafe(qx.preload_all_assets(), loop)
            # تيكات في الذاكرة فقط + حذف الأقدم من 5 دقائق (حماية القرص)
            asyncio.run_coroutine_threadsafe(qx.tick_cache_collector(), loop)
            asyncio.run_coroutine_threadsafe(qx.tick_retention_loop(), loop)
            asyncio.run_coroutine_threadsafe(qx.candlestore_trim_loop(), loop)
            self._qx_logged = True
            self._qx_load_feed(force=True)
            self._log("ok", "QX server connected — " + host + " | opener: " + str(qx.PRELOAD_FIRST_SYMBOL))
            self._emit_qx({"type": "login", "state": "ok"})
        except Exception as e:
            self._emit_qx({"type": "login", "state": "err", "msg": str(e)[:160]})
        finally:
            self._qx_login_busy = False

    # ---------- دفعة التمرير للخلف (170 شمعة) ----------
    @Slot(str)
    def fetchOlder(self, arg):
        \"\"\"طلب دفعة شموع أقدم من الخادم عند التمرير إلى بداية الشارت.\"\"\"
        if not self._qx_logged or self._qx_older_busy:
            self._emit_qx({"type": "older", "candles": []})
            return
        self._qx_older_busy = True
        threading.Thread(target=self._qx_older_worker, args=(str(arg or "{}"),),
                         daemon=True, name="qxOlder").start()

    def _qx_older_worker(self, arg):
        batch = []
        try:
            try:
                req = json.loads(arg or "{}")
            except Exception:
                req = {}
            before = int(req.get("before") or 0)
            asset = str(req.get("asset") or self._asset)
            tf = str(req.get("tf") or self._tf)
            qx = _qx_module()
            api = self._qx_symbols.get(asset) or self._api_from_display(asset)
            tf_sec = dict(TFS).get(tf, 60)
            if qx and api and before > 0 and getattr(qx, "CLIENT", None) is not None and tf_sec >= 60:
                if tf_sec == 60:
                    # دفعة الخادم الرسمية: fetch_older_batch تجلب 170 شمعة أقدم وتدمجها
                    fut = asyncio.run_coroutine_threadsafe(
                        qx.fetch_older_batch(api, before, qx.PAGINATION_BATCH), qx.ASYNC_LOOP)
                    fut.result(timeout=60)
                    batch = [c for c in self._qx_engine_candles(api) if c["t"] < before][-qx.PAGINATION_BATCH:]
                else:
                    fut = asyncio.run_coroutine_threadsafe(
                        qx.CLIENT.get_candles(api, before, 170 * tf_sec, tf_sec), qx.ASYNC_LOOP)
                    res = fut.result(timeout=45)
                    batch = [c for c in self._qx_fmt_raw(res, tf_sec) if c["t"] < before][-170:]
                # مزامنة غذاء بايثون فوراً حتى لا يعيد المضخة إرسال إعادة ضبط للشارت
                if tf == self._tf and asset == self._asset and batch:
                    if tf_sec == 60:
                        self._candles = self._qx_engine_candles(api)
                        if len(self._candles) > self._QX_FEED_CAP:
                            self._candles = self._candles[-self._QX_FEED_TRIM:]
                    else:
                        self._candles = batch + self._candles
                        if len(self._candles) > self._QX_FEED_CAP:
                            self._candles = self._candles[-self._QX_FEED_TRIM:]
                    self._qx_last_sig = None
                if batch:
                    self._log("info", f"older batch: +{len(batch)} candles — {asset} {tf}")
                else:
                    self._log("info", f"older batch: no more history — {asset} {tf}")
            elif tf_sec < 60:
                self._log("info", "sub-second history builds from live ticks (5-min server window)")
        except Exception as e:
            self._log("err", "older batch: " + str(e)[:120])
        finally:
            self._qx_older_busy = False
        self._emit_qx({"type": "older", "candles": batch})""", tag="_on_tick + QX engine block")

open(DST + ".part2", "w", encoding="utf-8").write(src)
print("PART 2 OK —", len(edits), "edits applied")
print("\n".join("  ✓ " + e for e in edits))
