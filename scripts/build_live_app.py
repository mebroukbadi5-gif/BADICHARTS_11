# -*- coding: utf-8 -*-
"""
build_live_app.py — يبني BadiChartsStudio_live.py من BadiChartsStudio.py

LIVE SERVER EDITION (طلب المستخدم):
  • ملف جديد بجانب التطبيق الأصلي — لا يُحذف ولا يُعدَّل أي شيء في الملف الأصلي.
  • انزع الشموع الوهمية + تسجيل الدخول الوهمي.
  • اربط التطبيق بخادم Quotex الخاص بنا (qx_server_v13.py) الموجود في نفس المستودع:
      - تسجيل دخول حقيقي (البريد + كلمة المرور) عبر نفس connect_quotex.
      - BRLUSD_otc: 300 شمعة فوراً بعد الدخول + الحالة ونسبة الدفع (عملة فتح الشارت).
      - بقية العملات تتحمل واحدة تلو الأخرى 300 شمعة (محرك preload_all_assets).
      - بث حي مستمر لكل العملات — أي شارت تفتحه تجده جاهزاً.
      - التمرير إلى الوراء يطلب دفعة 170 شمعة أقدم تُدمج دون أي تأثير على الشارت.
"""
import sys
import re

SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/gh_repo/BadiChartsStudio.py"
DST = sys.argv[2] if len(sys.argv) > 2 else "/home/z/my-project/gh_repo/BadiChartsStudio_live.py"

src = open(SRC, encoding="utf-8").read()
edits = []


def rep(old, new, count=1, tag=""):
    """استبدال مع تحقق صارم: يجب أن يظهر النص القديم بعدد مطابق تماماً."""
    global src
    found = src.count(old)
    if found != count:
        raise SystemExit(f"[FAIL] anchor not unique ({found}x, want {count}x): {tag or old[:80]}")
    src = src.replace(old, new)
    edits.append(tag or old[:60])


# ════════════════════════════ 1) الاستيرادات ════════════════════════════
rep("""import gzip
import lzma
import random
import threading""",
    """import gzip
import lzma
import random
import threading
import importlib
import asyncio""", tag="imports")

# ════════════════════════════ 2) التوثيق ════════════════════════════
rep("""  • Quotex real market & OTC assets (simulated live feed, pluggable)""",
    """  • LIVE SERVER EDITION — Quotex REAL market & OTC assets streamed by our own
    QX server (qx_server_v13.py beside the app): real login, real candles
    (BRLUSD_otc 300 on login + others one by one), live prices for every asset,
    scroll-back batches of 170 older candles — no fake candles, no fake login""", tag="docstring")

# ══════════════════════ 3) محمّل محرك الخادم ══════════════════════
rep("""from PySide6.QtWebEngineQuick import QtWebEngineQuick""",
    """from PySide6.QtWebEngineQuick import QtWebEngineQuick

# ═══════════════════ LIVE SERVER EDITION — QX ENGINE LOADER ═══════════════════
# التطبيق يشغّل خادم Quotex الخاص بنا (qx_server_v13.py) الموجود بجانبه مباشرة:
#   • نفس تسجيل الدخول (connect_quotex) ونفس جلب الشموع الأصلي دون أي تغيير.
#   • BRLUSD_otc: 300 شمعة فوراً بعد الدخول + الحالة ونسبة الدفع.
#   • بقية العملات واحدة تلو الأخرى (300 شمعة لكل عملة) + بث حي لكل عملة.
#   • دفعات التمرير للخلف (170 شمعة) عبر fetch_older_batch().
#   • التيكات في الذاكرة فقط وتُحذف بعد 5 دقائق (سياسة الخادم نفسها).
_QX_MOD = None


def _qx_module():
    \"\"\"تحميل محرك الخادم من بجانب التطبيق (يُحمَّل مرة واحدة).\"\"\"
    global _QX_MOD
    if _QX_MOD is not None:
        return _QX_MOD or None
    try:
        _app_dir = os.path.dirname(os.path.abspath(__file__))
        if _app_dir not in sys.path:
            sys.path.insert(0, _app_dir)
        _QX_MOD = importlib.import_module("qx_server_v13")
        try:
            _QX_MOD.DEBUG_LOGS = False
        except Exception:
            pass
    except Exception as _e:
        try:
            print("[QX] qx_server_v13.py load failed: " + str(_e))
        except Exception:
            pass
        _QX_MOD = False
    return _QX_MOD or None""", tag="qx loader")

# ═══════════════════ 4) JS — addPane: بلا شموع وهمية ═══════════════════
rep("""  chart.start();
  p.dataArr = generateCandles(cfg, p.tf, 620);
  chart.setData(p.dataArr);
  renderPaneHead(i);""",
    """  chart.start();
  /* LIVE SERVER EDITION (طلب المستخدم): الشموع الوهمية انزعت من التطبيق —
     الشارت يبدأ فارغاً وينتظر بيانات خادم Quotex الحقيقية
     (BRLUSD_otc: 300 شمعة فوراً بعد الدخول، ثم بقية العملات واحدة تلو الأخرى) */
  if (!window.__BADI_EMBEDDED) {
    p.dataArr = generateCandles(cfg, p.tf, 620);
    chart.setData(p.dataArr);
  }
  renderPaneHead(i);""", tag="addPane no fake")

# ═══════════════════ 5) JS — setPaneAsset: بلا شموع وهمية ═══════════════════
rep("""  if (!(window.__BADI_EMBEDDED && i === primaryPane)) {
    p.dataArr = generateCandles(cfg, p.tf, 620);
    try { p.chart.setData(p.dataArr); } catch (e) {}
    p.tick = 0;
  }""",
    """  if (!window.__BADI_EMBEDDED) {
    p.dataArr = generateCandles(cfg, p.tf, 620);
    try { p.chart.setData(p.dataArr); } catch (e) {}
    p.tick = 0;
  }""", tag="setPaneAsset no fake")

# ═══════════════════ 6) JS — خطّاف التمرير للوراء في setupChart ═══════════════════
rep("""      const origUpdate = ch.update.bind(ch);
      ch.update = function (c) { wake(); return origUpdate(c); };
      wake();
    }
  } catch (e) {}""",
    """      const origUpdate = ch.update.bind(ch);
      ch.update = function (c) { wake(); return origUpdate(c); };
      wake();
      /* LIVE SERVER EDITION: عند التمرير إلى بداية الشارت يُطلب من خادم QX
         دفعة أقدم صغيرة (170 شمعة) تُدمج في الشارت دون أي تأثير على العرض —
         كلما زاد التمرير للخلف ظهرت شموع أخرى مثل المنصات الاحترافية */
      try {
        const origConstrain = ch.constrainRightOffset.bind(ch);
        ch.constrainRightOffset = function () {
          origConstrain();
          if (typeof window.__badiMaybeLoadOlder === "function") window.__badiMaybeLoadOlder(p);
        };
      } catch (e) {}
    }
  } catch (e) {}""", tag="setupChart older hook")

# ═══════════════════ 7) JS — بوابة طلب دفعة الشموع الأقدم ═══════════════════
rep("""window.__badiSend = send;""",
    """window.__badiSend = send;
/* ═══ LIVE SERVER EDITION: دفعة التمرير للخلف (170 شمعة) ═══
   عندما يقترب التمرير من بداية البيانات يُطلب من الخادم دفعة أقدم؛ وصولها
   يُدمج في الشارت مع تثبيت العرض الحالي تماماً (لا قفزة ولا إعادة ضبط). */
var OLDER = { loading: false, at: 0, asset: "", tf: "" };
window.__badiMaybeLoadOlder = function (p) {
  try {
    if (!window.__BADI_EMBEDDED || !p || !window.__badiPrimary || p !== window.__badiPrimary()) return;
    var dd = p.dataArr;
    if (!dd || dd.length < 30 || !p.chart) return;
    if (OLDER.loading) {
      if (Date.now() - OLDER.at > 8000) OLDER.loading = false; else return;
    }
    var ch = p.chart;
    if (typeof ch.rightOffset !== "number" || !ch.sim || !ch.sim.candles || !ch.sim.candles.length) return;
    var N = ch.sim.candles.length;
    var visible = (ch.chartRight - ch.chartLeft) / (ch.barSpacing || 8);
    var firstIdx = N - 1 + ch.rightOffset - visible;
    if (firstIdx > 4) return;
    var t0 = dd[0].time;
    if (t0 > 1e11) t0 = Math.floor(t0 / 1000);
    OLDER.loading = true; OLDER.at = Date.now();
    OLDER.asset = String(p.asset || ""); OLDER.tf = String(p.tf || "");
    send("older", JSON.stringify({ before: Math.floor(t0), asset: OLDER.asset, tf: OLDER.tf }));
  } catch (e) { OLDER.loading = false; }
};""", tag="older bridge")

# ═══════════════════ 8) JS — pushTick: ثبات العرض أثناء التمرير للخلف ═══════════════════
rep("""        if (!pr.dataArr.length) pr.dataArr = [k];
        else {
          var last = pr.dataArr[pr.dataArr.length - 1];
          if (k.time > last.time) {
            pr.dataArr.push(k);
            if (pr.dataArr.length > 1500) pr.dataArr = pr.dataArr.slice(-1200);
          } else pr.dataArr[pr.dataArr.length - 1] = k;
        }""",
    """        if (!pr.dataArr.length) pr.dataArr = [k];
        else {
          var last = pr.dataArr[pr.dataArr.length - 1];
          if (k.time > last.time) {
            pr.dataArr.push(k);
            /* أثناء التمرير للخلف: ولادة شمعة جديدة لا تُزيح العرض — يبقى ثابتاً
               مثل المنصات الاحترافية (وليس اتباع الشمعة الحية) */
            try { if (pr.chart && pr.chart.rightOffset < 0) pr.chart.rightOffset -= 1; } catch (e) {}
            if (pr.dataArr.length > 3000) {
              var excess = pr.dataArr.length - 2600;
              pr.dataArr.splice(0, excess);
              try { if (pr.chart && pr.chart.sim && pr.chart.sim.candles) pr.chart.sim.candles.splice(0, excess); } catch (e) {}
            }
          } else pr.dataArr[pr.dataArr.length - 1] = k;
        }""", tag="pushTick anchor")

# ═══════════════════ 9) JS — setBoard + prependCandles في __badiApp ═══════════════════
rep("""    pushTick: function (c) {""",
    """    setBoard: function (list) {
      /* LIVE SERVER EDITION: لوحة العملات الحقيقية من خادم QX
         (الاسم + نسبة الدفع + مفتوح/مغلق + علم الزوج) */
      try {
        var arr = (typeof list === "string") ? JSON.parse(list) : (list || []);
        if (!Array.isArray(arr) || !arr.length) return;
        BOARD = arr;
        window.__BADI_REAL_OPEN = {};
        for (var i = 0; i < arr.length; i++) window.__BADI_REAL_OPEN[arr[i].name] = !!arr[i].open;
        try { renderAssets(); } catch (e) {}
        try { renderAssetMenu(); } catch (e) {}
        try {
          if (typeof panes !== "undefined" && panes.forEach)
            panes.forEach(function (p, ix) { renderPaneHead(ix); });
        } catch (e) {}
      } catch (e) {}
    },
    prependCandles: function (arr) {
      /* LIVE SERVER EDITION: دمج دفعة الشموع الأقدم (تمرير للخلف) دون أي تأثير
         على الشارت — نفس الشموع تبقى في نفس مكانها بالضبط، فقط يزداد التاريخ
         على اليسار مثل المنصات الاحترافية. تعيد عدد الشموع المضافة. */
      try {
        OLDER.loading = false;
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr || !pr.chart) return 0;
        var add = normArr(arr || []);
        if (!add.length || !pr.dataArr.length) return 0;
        var firstT = pr.dataArr[0].time;
        var pre = [];
        for (var i = 0; i < add.length; i++) { if (add[i].time < firstT) pre.push(add[i]); }
        if (!pre.length) return 0;
        pre.sort(function (a, b) { return a.time - b.time; });
        pr.dataArr = pre.concat(pr.dataArr);
        var ch = pr.chart, sim = ch.sim;
        if (sim && sim.candles) {
          for (var j = pre.length - 1; j >= 0; j--) {
            var c = pre[j];
            var nc = { time: c.time, open: c.open, high: c.high, low: c.low, close: c.close, volume: c.volume || 0 };
            if (sim._norm) nc = sim._norm(nc);
            sim.candles.unshift(nc);
          }
        }
        /* ملاحظة: لا تعديل على rightOffset — مرساة العرض محسوبة من نهاية المصفوفة،
           فالإضافة في البداية تُبقي كل شمعة في مكانها تماماً */
        ch.computeTimeWeights(); ch.computeIndicators();
        try { ch.invalidateTimeMarks(); } catch (e) {}
        ch.autoScale(); ch.invalidate();
        try { runSignals(); } catch (e) {}
        return pre.length;
      } catch (e) {
        OLDER.loading = false;
        try { console.log("BADI::dbg prepend ERR " + e); } catch (e2) {}
        return 0;
      }
    },
    pushTick: function (c) {""", tag="setBoard+prepend")

# ═══════════════════ 10) JS — حالة السوق الحقيقية ═══════════════════
rep("""function badiMarketOpen(name) {
  var n = String(name || "");
  if (n.indexOf("OTC") >= 0) return true;            /* أزواج OTC مفتوحة دائمًا */""",
    """function badiMarketOpen(name) {
  var n = String(name || "");
  try { var RO = window.__BADI_REAL_OPEN; if (RO && RO[n] !== undefined) return !!RO[n]; } catch (e) {}
  if (n.indexOf("OTC") >= 0) return true;            /* أزواج OTC مفتوحة دائمًا */""", tag="real market open")

# ═══════════════════ 11) JS — إيقاف ماسح الشموع الوهمية ═══════════════════
rep("""function scanSignals() {
  if (!SIG_DEFS.length || typeof generateCandles !== "function") return;""",
    """function scanSignals() {
  if (!SIG_DEFS.length || typeof generateCandles !== "function") return;
  /* LIVE SERVER EDITION (طلب المستخدم): الماسح المتعدد كان يولّد شموعاً وهمية
     لكل عملة — انزع في وضع الخادم الحي. إشارات عملة الشارت الحقيقية تغطيها
     runSignals على بيانات الخادم الفعلية */
  if (window.__BADI_EMBEDDED) return;""", tag="no fake scanner")

open(DST + ".part1", "w", encoding="utf-8").write(src)
print("PART 1 OK —", len(edits), "edits applied")
print("\n".join("  ✓ " + e for e in edits))
