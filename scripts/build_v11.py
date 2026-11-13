#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني qx_server_v11.py من qx_server_v10.py:

- الكونسول يسأل فقط: البريد + كلمة المرور (نفس طريقة الدخول الأصلية حرفياً)
- بعد الدخول يجلب قائمة العملات الكاملة (دفع + مفتوح/مغلق) ويعرضها في واجهة FastAPI
- لا يوجد أي سؤال عن العملات/الفريمات/الأيام في الكونسول
- محرك جلب الشموع (1000 شمعة) يبقى في الملف كما هو دون أي تعديل، ولا يُشغَّل تلقائياً
"""
import py_compile
from pathlib import Path

SRC = Path('/home/z/my-project/download/qx_server_v10.py')
DST = Path('/home/z/my-project/download/qx_server_v11.py')

src = SRC.read_text(encoding='utf-8')

# ── 1) تحديث ملاحظة الرأس ─────────────────────────────────────────────────────
old_note = """# NOTE: Flask web dashboard REMOVED (v10.0) — replaced by console output +
# MT4 .hst files + qx_assets_payouts.json. No web server in this build."""
new_note = """# NOTE (v11.0): FastAPI web interface — the console asks ONLY for email +
# password (login method untouched), then serves a web UI with the FULL asset
# list (payout % + open/closed). No asset/timeframe/days console prompts.
# The candle engine (1000-candle fetch) stays in the file UNCHANGED but is
# not auto-started, because the program never asks for an asset (user spec)."""
assert old_note in src, 'header note not found'
src = src.replace(old_note, new_note)

# ── 2) إضافة استيراد FastAPI/uvicorn ─────────────────────────────────────────
old_imp = "from fake_useragent import UserAgent"
new_imp = """from fake_useragent import UserAgent

# v11.0: FastAPI + uvicorn — واجهة ويب لعرض قائمة العملات والدفع والحالة
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False"""
assert src.count(old_imp) == 1, 'import anchor not found'
src = src.replace(old_imp, new_imp)

# ── 3) ربط حفظ اللقطة بتحديث حالة الويب (منطق الجلب نفسه لا يتغير) ──────────
old_save = """        ASSETS_PAYOUT_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return True"""
new_save = """        ASSETS_PAYOUT_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        # v11.0: تحديث اللقطة في الذاكرة لواجهة الويب (نفس البيانات تماماً)
        try:
            _update_assets_state(entries)
        except Exception:
            pass
        return True"""
assert src.count(old_save) == 1, 'save anchor not found'
src = src.replace(old_save, new_save)

# ── 4) استبدال كتلة __main__ بالكامل (قسم FastAPI + التدفق الجديد) ──────────
marker = 'if __name__ == "__main__":'
idx = src.index(marker)
src_head = src[:idx]

NEW_TAIL = '''# ==============================================================================
# ===== v11.0: FastAPI WEB INTERFACE (واجهة الويب — قائمة العملات) =============
# ==============================================================================
# التدفق الجديد (طلب المستخدم):
#   1) عند التشغيل يسأل البرنامج فقط عن البريد وكلمة المرور (نفس طريقة الدخول
#      الأصلية دون أي تغيير).
#   2) بعد الدخول يجلب قائمة العملات الكاملة: نسبة الدفع + الحالة (مفتوح/مغلق).
#   3) يعرضها في واجهة ويب عربية عبر FastAPI مع تحديث تلقائي.
#   لا يوجد أي سؤال عن العملة أو الفريم أو عدد الأيام في الكونسول.
#   محرك جلب الشموع (1000 شمعة) يبقى في الملف كما هو، ولا يُشغَّل تلقائياً.
# ==============================================================================
WEB_HOST = "127.0.0.1"
WEB_PORT = 8000
_WEB_STARTED_AT = time.time()

# اللقطة المشتركة في الذاكرة التي تقرأ منها واجهة الويب.
# تُملأ تلقائياً من _save_assets_payout_file (نفس بيانات qx_assets_payouts.json).
ASSETS_PAYOUT_STATE = {
    "updated_at": None,
    "host": None,
    "count": 0,
    "open_count": 0,
    "closed_count": 0,
    "assets": [],
}
_STATE_LOCK = threading.Lock()

def _update_assets_state(entries):
    """يحدّث اللقطة في الذاكرة لواجهة الويب (نفس البيانات، بلا أي معالجة إضافية)."""
    try:
        with _STATE_LOCK:
            ASSETS_PAYOUT_STATE["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ASSETS_PAYOUT_STATE["host"] = QX_HOST
            ASSETS_PAYOUT_STATE["count"] = len(entries)
            ASSETS_PAYOUT_STATE["open_count"] = sum(1 for e in entries if e.get("open"))
            ASSETS_PAYOUT_STATE["closed_count"] = sum(1 for e in entries if e.get("open") is False)
            ASSETS_PAYOUT_STATE["assets"] = list(entries)
    except Exception as e:
        logmsg(f"[web] state update failed: {e}")

INDEX_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>قائمة العملات — Quotex</title>
<style>
:root{
  --bg:#0b1220; --card:#121b30; --card2:#0f1729; --line:#1e2a44;
  --txt:#e6edf7; --dim:#8fa0b8; --cyan:#22d3ee; --green:#4ade80;
  --red:#f87171; --amber:#fbbf24;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
  font-family:Tahoma,'Segoe UI',Arial,sans-serif;font-size:14px}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
header{display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  justify-content:space-between;background:linear-gradient(135deg,#101a30,#0c1424);
  border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-bottom:14px}
h1{font-size:19px;margin:0;color:#fff}
h1 small{display:block;font-weight:normal;color:var(--dim);font-size:12px;margin-top:4px}
.badges{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.badge{border-radius:999px;padding:6px 12px;font-size:12px;border:1px solid var(--line);
  background:var(--card2);color:var(--dim)}
.badge.on{color:var(--green);border-color:rgba(34,197,94,.4);background:rgba(34,197,94,.12)}
.badge.off{color:var(--red);border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.12)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.stat .v{font-size:22px;font-weight:bold}
.stat .l{color:var(--dim);font-size:12px;margin-top:3px}
.v.cyan{color:var(--cyan)} .v.green{color:var(--green)} .v.red{color:var(--red)}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}
.toolbar input[type=search]{flex:1;min-width:180px;background:var(--card2);color:var(--txt);
  border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:13px;outline:none}
.toolbar input[type=search]:focus{border-color:var(--cyan)}
.toolbar label.chk{display:flex;align-items:center;gap:6px;color:var(--dim);font-size:13px;
  background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:8px 12px;cursor:pointer}
button{background:var(--cyan);color:#06202a;border:none;border-radius:10px;padding:9px 16px;
  font-size:13px;font-weight:bold;cursor:pointer;font-family:inherit}
button:active{opacity:.8}
.hint{color:var(--dim);font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
  border-radius:12px;overflow:hidden}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th{position:sticky;top:0;background:#16213a;color:var(--dim);font-size:12px;font-weight:bold}
tbody tr:hover{background:rgba(34,211,238,.05)}
td.num{color:var(--dim);width:36px}
td.sym{font-family:Consolas,Menlo,monospace;direction:ltr;text-align:left;color:#7dd3fc;font-weight:bold}
td.nm{color:var(--dim);font-size:12px;max-width:220px;overflow:hidden;text-overflow:ellipsis}
.pay.hi{color:var(--green);font-weight:bold}
.pay.mid{color:var(--amber);font-weight:bold}
.pay.low,.pay.na{color:var(--dim)}
.pill{padding:3px 12px;border-radius:999px;font-size:12px;font-weight:bold;display:inline-block}
.pill.open{background:rgba(34,197,94,.15);color:var(--green);border:1px solid rgba(34,197,94,.35)}
.pill.closed{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.35)}
.pill.unknown{background:rgba(148,163,184,.15);color:#94a3b8;border:1px solid rgba(148,163,184,.3)}
td.empty{text-align:center;color:var(--dim);padding:34px;font-size:13px}
footer{color:var(--dim);font-size:11px;margin-top:14px;text-align:center}
@media(max-width:640px){ .stats{grid-template-columns:repeat(2,1fr)} td.nm{display:none} th:nth-child(3){display:none} }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>قائمة العملات — Quotex
        <small>نسبة الدفع والحالة (مفتوح / مغلق) — تحديث تلقائي</small>
      </h1>
    </div>
    <div class="badges">
      <span class="badge" id="conn">جارٍ التحقق…</span>
      <span class="badge">النطاق: <span id="host">—</span></span>
      <span class="badge">البلد: <span id="country">—</span></span>
      <span class="badge">الحساب: <span id="email">—</span></span>
    </div>
  </header>

  <div class="stats">
    <div class="stat"><div class="v cyan" id="stTotal">—</div><div class="l">إجمالي العملات</div></div>
    <div class="stat"><div class="v green" id="stOpen">—</div><div class="l">مفتوحة</div></div>
    <div class="stat"><div class="v red" id="stClosed">—</div><div class="l">مغلقة</div></div>
    <div class="stat"><div class="v" id="stUpd" style="font-size:14px;padding-top:6px">—</div><div class="l">آخر تحديث للبيانات</div></div>
  </div>

  <div class="toolbar">
    <input type="search" id="q" placeholder="بحث عن عملة… (مثال: EURUSD)">
    <label class="chk"><input type="checkbox" id="openOnly"> المفتوحة فقط</label>
    <button id="refresh">تحديث الآن</button>
    <span class="hint" id="cnt"></span>
  </div>

  <table>
    <thead>
      <tr>
        <th>#</th><th>العملة</th><th>الاسم</th><th>الدفع %</th>
        <th>تيربو %</th><th>1 دقيقة %</th><th>5 دقائق %</th><th>الحالة</th>
      </tr>
    </thead>
    <tbody id="tbody">
      <tr><td colspan="8" class="empty">في انتظار جلب قائمة العملات من الخادم…</td></tr>
    </tbody>
  </table>

  <footer>QX Server v11.0 — FastAPI • البيانات من الخادم مباشرة (نفس طريقة pyquotex الرسمية)</footer>
</div>

<script>
var state = { assets: [], openOnly: false, q: '' };
function $(id){ return document.getElementById(id); }
function esc(s){
  var d = document.createElement('div');
  d.textContent = String(s == null ? '' : s);
  return d.innerHTML;
}
function fmtP(v){
  return (typeof v === 'number') ? v + '%' : '—';
}
function payClass(v){
  if (typeof v !== 'number') return 'pay na';
  if (v >= 80) return 'pay hi';
  if (v >= 60) return 'pay mid';
  return 'pay low';
}
async function load(){
  try{
    var d = await (await fetch('/api/assets')).json();
    state.assets = d.assets || [];
    $('stUpd').textContent = d.updated_at || '—';
    $('stTotal').textContent = (typeof d.count === 'number') ? d.count : state.assets.length;
    $('stOpen').textContent = (typeof d.open_count === 'number') ? d.open_count : 0;
    $('stClosed').textContent = (typeof d.closed_count === 'number') ? d.closed_count : 0;
    render();
  }catch(e){}
  try{
    var s = await (await fetch('/api/status')).json();
    var b = $('conn');
    b.textContent = s.connected ? 'متصل' : 'انقطع الاتصال — إعادة المحاولة';
    b.className = 'badge ' + (s.connected ? 'on' : 'off');
    $('host').textContent = s.host || '—';
    $('country').textContent = s.country || '—';
    $('email').textContent = s.email || '—';
  }catch(e){}
}
function render(){
  var q = state.q.trim().toUpperCase();
  var list = state.assets.filter(function(a){
    if (state.openOnly && !a.open) return false;
    if (q){
      var hay = ((a.asset || '') + ' ' + (a.name || '')).toUpperCase();
      if (hay.indexOf(q) === -1) return false;
    }
    return true;
  });
  list = list.slice().sort(function(x, y){
    var ox = x.open ? 1 : 0, oy = y.open ? 1 : 0;
    if (ox !== oy) return oy - ox;
    var px = (typeof x.payout === 'number') ? x.payout : -1;
    var py = (typeof y.payout === 'number') ? y.payout : -1;
    return py - px;
  });
  var tb = $('tbody');
  if (!list.length){
    var msg = state.assets.length
      ? 'لا توجد نتائج مطابقة للبحث'
      : 'جارٍ جلب قائمة العملات من الخادم… (تظهر خلال ثوانٍ بعد تسجيل الدخول)';
    tb.innerHTML = '<tr><td colspan="8" class="empty">' + msg + '</td></tr>';
    $('cnt').textContent = '';
    return;
  }
  var rows = list.map(function(a, i){
    var st = a.open
      ? '<span class="pill open">مفتوح</span>'
      : (a.open === false ? '<span class="pill closed">مغلق</span>'
                          : '<span class="pill unknown">غير معروف</span>');
    return '<tr>'
      + '<td class="num">' + (i + 1) + '</td>'
      + '<td class="sym">' + esc(a.asset) + '</td>'
      + '<td class="nm">' + esc(a.name) + '</td>'
      + '<td class="' + payClass(a.payout) + '">' + fmtP(a.payout) + '</td>'
      + '<td class="' + payClass(a.turbo_payout) + '">' + fmtP(a.turbo_payout) + '</td>'
      + '<td>' + fmtP(a.profit_1m) + '</td>'
      + '<td>' + fmtP(a.profit_5m) + '</td>'
      + '<td>' + st + '</td>'
      + '</tr>';
  }).join('');
  tb.innerHTML = rows;
  $('cnt').textContent = 'عرض ' + list.length + ' من ' + state.assets.length;
}
$('q').addEventListener('input', function(e){ state.q = e.target.value; render(); });
$('openOnly').addEventListener('change', function(e){ state.openOnly = e.target.checked; render(); });
$('refresh').addEventListener('click', load);
load();
setInterval(load, 15000);
</script>
</body>
</html>"""

def _build_web_app():
    """يبني تطبيق FastAPI: صفحة الواجهة + واجهتان JSON (العملات + حالة الاتصال)."""
    app = FastAPI(title="Quotex Assets Monitor — BadiCharts",
                  docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/", response_class=HTMLResponse)
    async def web_index():
        return INDEX_HTML

    @app.get("/api/assets")
    async def web_api_assets():
        # نفس البيانات التي تُحفظ في qx_assets_payouts.json — من الذاكرة مباشرة،
        # وإن لم تُملأ بعد نقرأ ملف اللقطة المحفوظ (نفس محتوى الجدول المطبوع).
        with _STATE_LOCK:
            snap = {k: (list(v) if isinstance(v, list) else v)
                    for k, v in ASSETS_PAYOUT_STATE.items()}
        if not snap.get("assets"):
            try:
                data = json.loads(ASSETS_PAYOUT_FILE.read_text(encoding="utf-8"))
                snap["updated_at"] = data.get("updated_at") or snap["updated_at"]
                snap["host"] = data.get("host") or snap["host"]
                snap["count"] = data.get("count", 0)
                snap["open_count"] = data.get("open_count", 0)
                snap["closed_count"] = data.get("closed_count", 0)
                snap["assets"] = data.get("assets", [])
            except Exception:
                pass
        return {
            "ok": True,
            "assets": snap.get("assets", []),
            "updated_at": snap.get("updated_at"),
            "host": snap.get("host"),
            "count": snap.get("count", 0),
            "open_count": snap.get("open_count", 0),
            "closed_count": snap.get("closed_count", 0),
        }

    @app.get("/api/status")
    async def web_api_status():
        email_masked = ""
        try:
            if EMAIL:
                _n, _sep, _d = str(EMAIL).partition("@")
                email_masked = (_n[:2] + "***@" + _d) if _sep else str(EMAIL)
        except Exception:
            email_masked = ""
        return {
            "ok": True,
            "connected": bool(CONNECTION_ALIVE and CLIENT is not None),
            "host": QX_HOST,
            "country": _GEO_CACHE.get("country"),
            "email": email_masked,
            "uptime_seconds": int(time.time() - _WEB_STARTED_AT),
            "refresh_interval": PAYOUT_REFRESH_INTERVAL,
            "version": "11.0",
        }

    return app

WEB_APP = _build_web_app() if FASTAPI_AVAILABLE else None

def _pick_free_port(start_port: int, host: str, tries: int = 11) -> int:
    """يفحص المنفذ الأول المتاح بدءاً من start_port (لتجنب تعارض منفذ مشغول)."""
    import socket as _socket
    for _p in range(start_port, start_port + tries):
        try:
            with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as _sk:
                _sk.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
                _sk.bind((host, _p))
                return _p
        except OSError:
            continue
    return start_port


if __name__ == "__main__":
    # ════════════════════════════════════════════════════════════════════
    # v11.0 — التدفق الجديد: لا أسئلة عملات / فريمات / أيام إطلاقاً.
    #   STAGE 1: التعرف على النطاق تلقائياً (بنغلاديش -> market-qx.info)
    #   STAGE 2: البريد + كلمة المرور فقط (نفس طريقة الدخول الأصلية حرفياً)
    #   STAGE 3: بعد الدخول: جلب قائمة العملات الكاملة + الدفع + الحالة
    #   STAGE 4: عرضها في واجهة ويب FastAPI على http://127.0.0.1:8000
    # ════════════════════════════════════════════════════════════════════
    print()
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  QX SERVER v11.0 — FastAPI Asset Monitor{Colors.RESET}")
    print(f"  {Colors.DIM}الدخول ثم عرض قائمة العملات والدفع والحالة في المتصفح{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")

    if not FASTAPI_AVAILABLE or WEB_APP is None:
        print(f"{Colors.RED}  Missing packages: fastapi / uvicorn{Colors.RESET}")
        print(f"  {Colors.CYAN}pip install fastapi uvicorn{Colors.RESET}")
        sys.exit(1)

    # ---- STAGE 1: النطاق تلقائياً حسب البلد (بدون أي سؤال) ----
    print()
    print(f"{Colors.BOLD}  Domain: detecting country automatically ...{Colors.RESET}")
    resolve_qx_host()
    globals()['QX_HOST'] = QX_HOST
    _geo_country = _GEO_CACHE.get("country") or "unknown"
    print(f"{Colors.GREEN}  Country: {_geo_country}  ->  Domain: {QX_HOST}{Colors.RESET}")

    # ---- STAGE 2: تسجيل الدخول — البريد وكلمة المرور فقط ----
    # نفس كود v10 حرفياً (حفظ الجلسة + connect_quotex + نفس المهلات).
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
        print(f"\\n{Colors.RED}[FAILED] Could not connect after all attempts.{Colors.RESET}")
        sys.exit(1)

    # ---- STAGE 3: مراقبة الاتصال + جلب قائمة العملات (حلقات v10 دون تغيير) ----
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass
    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # جلب قائمة العملات الكاملة + نسبة الدفع + الحالة (مفتوح/مغلق) وتحديثها دورياً.
    # نفس asset_payout_monitor في v10: يطبع الجدول في الكونسول مرة واحدة،
    # يحفظ qx_assets_payouts.json، ويحدّث واجهة الويب تلقائياً.
    asyncio.run_coroutine_threadsafe(asset_payout_monitor(), ASYNC_LOOP)

    # ---- STAGE 4: تشغيل واجهة الويب (FastAPI + uvicorn) ----
    _bind_host = WEB_HOST
    _bind_port = _pick_free_port(WEB_PORT, _bind_host)
    _url = f"http://{_bind_host}:{_bind_port}"
    print()
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")
    print(f"{Colors.BOLD}  Connected! The assets web interface is running:{Colors.RESET}")
    print(f"  {Colors.CYAN}{_url}{Colors.RESET}")
    print(f"  {Colors.DIM}القائمة تظهر خلال ثوانٍ وحدّثتها الواجهة تلقائياً كل 15 ثانية{Colors.RESET}")
    print(f"  {Colors.DIM}اترك هذا الترمينال مفتوحاً — للخروج: Ctrl+C{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 64}{Colors.RESET}")
    try:
        # فتح المتصفح تلقائياً (يُتجاهل بصمت إن لم يتوفر)
        try:
            import webbrowser as _wb
            threading.Timer(1.5, lambda: _wb.open(_url)).start()
        except Exception:
            pass
        uvicorn.run(WEB_APP, host=_bind_host, port=_bind_port, log_level="warning")
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print(f"{Colors.RED}Stopped{Colors.RESET}")
        writer_thread.running = False
'''

DST.write_text(src_head + NEW_TAIL, encoding='utf-8')
py_compile.compile(str(DST), doraise=True)
print('OK: wrote', DST)
