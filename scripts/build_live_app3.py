# -*- coding: utf-8 -*-
"""build_live_app.py — PART 3: switch/dec/boot + QML الدخول الحقيقي"""
SRC = "/home/z/my-project/gh_repo/BadiChartsStudio_live.py.part2"
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


# ════════════════ 15) switch — جلب حقيقي من الخادم ════════════════
rep("""    @Slot(str, str)
    def switch(self, asset, tf):
        self._asset = asset if any(a["name"] == asset for a in ASSETS["real"] + ASSETS["otc"]) else self._asset
        self._tf = tf if tf in dict(TFS) else self._tf
        self._market = "otc" if "OTC" in self._asset else "real"
        self._candles = generate_candles(self._asset, self._tf)
        self._tick = 0
        self._save_cfg()""",
    """    @Slot(str, str)
    def switch(self, asset, tf):
        # LIVE SERVER EDITION: التبديل يجلب الشموع الحقيقية من خادم Quotex.
        # العملة موجودة في لوحة الخادم عند توفرها — وإلا يُقبل الاسم كما هو
        # (لوحة العملات قد لا تكون وصلت بعد في ثوانٍ الدخول الأولى).
        if self._qx_symbols and asset not in self._qx_symbols:
            return
        self._asset = asset
        self._tf = tf if tf in dict(TFS) else self._tf
        self._market = "otc" if "OTC" in self._asset.upper() else "real"
        self._tick = 0
        self._qx_last_sig = None
        self._save_cfg()""", tag="switch real")

# ════════════════ 16) dec — دقة السعر الحقيقية ════════════════
rep("""    @Property(int, notify=candlesChanged)
    def dec(self):
        cfg = self._asset_cfg()
        return cfg["dec"]""",
    """    @Property(int, notify=candlesChanged)
    def dec(self):
        # LIVE SERVER EDITION: دقة السعر من آخر شمعة حقيقية (مطابقة لمنصة Quotex)
        try:
            p = float(self._candles[-1]["c"])
            if p >= 1000:
                return 2
            if p >= 100:
                return 3
            if p >= 10:
                return 4
            if p >= 1:
                return 5
            return 6
        except Exception:
            return 5""", tag="dec real")

# ════════════════ 17) boot_files_json — لوحة الإقلاع من الخادم ════════════════
rep("""                           "market": {"assets": [a["name"] for a in ASSETS["real"] + ASSETS["otc"]],
                                      "board": BOARD,""",
    """                           "market": {"assets": [b["name"] for b in self._qx_boot_board()],
                                      "board": self._qx_boot_board(),""", tag="boot board")

# ════════════════ 18) marketOpen — الحالة الحقيقية من الخادم ════════════════
rep("""    @Slot(str, result=bool)
    def marketOpen(self, name):
        \"\"\"حالة السوق لبطاقات العملات (طلب المستخدم): OTC والرقمية مفتوحة دائمًا —
        الفوركس مفتوح من الأحد 22:00 إلى الجمعة 22:00 بتوقيت UTC — نفس قاعدة الويب.\"\"\"
        n = str(name or "")
        if "OTC" in n:""",
    """    @Slot(str, result=bool)
    def marketOpen(self, name):
        \"\"\"حالة السوق من خادم QX الحقيقية عند توفرها — وإلا القاعدة المحلية الاحتياطية.\"\"\"
        n = str(name or "")
        try:
            for b in self._qx_board:
                if b.get("name") == n:
                    return bool(b.get("open"))
        except Exception:
            pass
        if "OTC" in n:""", tag="marketOpen real")

# ════════════════ 19) QML — صفحة الدخول: محو تسجيل الدخول الوهمي ════════════════
rep("""            property bool busy: false
            property bool ok: false
            property bool remember: true
            property string err: \"\"""",
    """            property bool busy: false
            property bool ok: false
            property bool remember: true
            property string err: ""
            property string qxStatus: \"\"       // LIVE SERVER EDITION: خط تقدم الاتصال بالخادم""", tag="login props")

rep("""                err = \"\"
                busy = true
                fakeAuth.restart()
            }
            Timer { id: fakeAuth; interval: 900; onTriggered: { loginPage.busy = false; loginPage.ok = true; win.loggedIn = true } }""",
    """                err = \"\"
                qxStatus = \"\"
                busy = true
                /* LIVE SERVER EDITION (طلب المستخدم): تسجيل الدخول الوهمي انزع —
                   الدخول حقيقي الآن عبر خادم Quotex الخاص بنا (qx_server_v13):
                   نفس connect_quotex، نفس الجلسة، ونفس طريقة جلب الشموع الأصلية */
                backend.qxLogin(userF.text.trim(), passF.text, remember)
            }""", tag="real login attempt")

rep("""            Component.onCompleted: enterAnim.restart()
            onVisibleChanged: if (visible) { t = 0; enterAnim.restart() }""",
    """            Component.onCompleted: {
                enterAnim.restart()
                /* LIVE SERVER EDITION: تعبئة البريد المحفوظ لدى الخادم (تذكّرني) */
                try { userF.text = backend.savedEmail } catch (e) {}
            }
            onVisibleChanged: if (visible) { t = 0; enterAnim.restart() }""", tag="prefill email")

# ════════════════ 20) QML — خط تقدم الاتصال في بطاقة الدخول ════════════════
rep("""                        // رسالة الخطأ / النجاح
                        Label {
                            Layout.fillWidth: true; Layout.preferredHeight: 18
                            text: loginPage.ok ? backend.s.signinok : loginPage.err""",
    """                        // LIVE SERVER EDITION: خط تقدم الاتصال الحقيقي بالخادم
                        Label {
                            Layout.fillWidth: true; Layout.preferredHeight: 16
                            visible: loginPage.qxStatus !== ""
                            text: loginPage.qxStatus
                            horizontalAlignment: loginPage.ha
                            font.pixelSize: 11; color: backend.c.accent
                            elide: Text.ElideRight
                        }

                        // رسالة الخطأ / النجاح
                        Label {
                            Layout.fillWidth: true; Layout.preferredHeight: 18
                            text: loginPage.ok ? backend.s.signinok : loginPage.err""", tag="status label")

# ════════════════ 21) QML — جسر رسائل الصفحة: أمر التمرير للوراء ════════════════
rep("""        if (cmd === "tf") { backend.switch(backend.assetLabel, arg); return }""",
    """        if (cmd === "tf") { backend.switch(backend.assetLabel, arg); return }
        if (cmd === "older") { backend.fetchOlder(arg); return }   // LIVE SERVER EDITION: دفعة 170 شمعة أقدم""", tag="older cmd")

# ════════════════ 22) QML — استقبال أحداث الخادم ════════════════
rep("""        function onSigResult(js) {
            win.webCall("__badiApp.sigResult(" + js + ")")
        }""",
    """        function onSigResult(js) {
            win.webCall("__badiApp.sigResult(" + js + ")")
        }
        function onQxEvent(js) {
            /* LIVE SERVER EDITION: أحداث خادم Quotex — دخول حقيقي، لوحة العملات
               الحقيقية (الدفع + الحالة)، ودفعات التمرير للوراء (170 شمعة) */
            var e = null
            try { e = JSON.parse(js) } catch (err) { return }
            if (!e || !e.type) return
            if (e.type === "login") {
                if (e.state === "ok") {
                    loginPage.busy = false; loginPage.ok = true; loginPage.qxStatus = ""
                    win.loggedIn = true
                } else if (e.state === "err") {
                    loginPage.busy = false; loginPage.ok = false
                    loginPage.err = e.msg || "Login failed"; loginPage.qxStatus = ""
                } else {
                    loginPage.qxStatus = e.msg || ""
                }
                return
            }
            if (e.type === "board") {
                win.webCall("__badiApp.setBoard(" + JSON.stringify(e.board) + ")")
                return
            }
            if (e.type === "older") {
                win.webCall("__badiApp.prependCandles(" + JSON.stringify(e.candles) + ")",
                            function (res) {
                                /* مزامنة عدّاد الشموع حتى لا تُعاد تهيئة الشارت
                                   بعد دمج الدفعة — العرض يبقى ثابتاً تماماً */
                                var n = parseInt(res || "0", 10) || 0
                                if (n > 0) win.lastLen = backend.candlesCount
                            })
                return
            }
        }""", tag="onQxEvent")

# ════════════════ 23) الترجمات — الإنجليزية ════════════════
rep("""        "errEmpty": "Please enter your username and password.", "signing": "Signing in…", "signinok": "Signed in successfully",""",
    """        "errEmpty": "Please enter your username and password.", "signing": "Signing in…", "signinok": "Signed in successfully",
        "qxResolving": "Detecting your country & server domain…", "qxConnecting": "Connecting to the Quotex server", "qxAuth": "Signing in to your Quotex account…", "qxLoad": "Connected — loading BRLUSD_otc (300 candles)…", "qxFail": "Could not connect to Quotex — check your email/password", "qxEngine": "QX engine not found — keep qx_server_v13.py beside the app",""", tag="T en")

# ════════════════ 24) الترجمات — العربية ════════════════
rep("""        "errEmpty": "يرجى إدخال اسم المستخدم وكلمة المرور.", "signing": "جارٍ الدخول…", "signinok": "تم الدخول بنجاح",""",
    """        "errEmpty": "يرجى إدخال اسم المستخدم وكلمة المرور.", "signing": "جارٍ الدخول…", "signinok": "تم الدخول بنجاح",
        "qxResolving": "جارٍ التعرف على بلدك واختيار نطاق الخادم…", "qxConnecting": "جارٍ الاتصال بخادم كوتكس", "qxAuth": "جارٍ تسجيل الدخول إلى حساب كوتكس…", "qxLoad": "تم الاتصال — جارٍ تحميل BRLUSD_otc (300 شمعة)…", "qxFail": "تعذر الاتصال بكوتكس — تحقق من البريد وكلمة المرور", "qxEngine": "محرك الخادم غير موجود — أبقِ qx_server_v13.py بجانب التطبيق",""", tag="T ar")

open(DST, "w", encoding="utf-8").write(src)
print("PART 3 OK —", len(edits), "edits applied")
print("\n".join("  ✓ " + e for e in edits))
