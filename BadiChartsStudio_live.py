# -*- coding: utf-8 -*-
# ==========================================================================
#  BadiCharts Studio — FULL SOURCE  (الكود كامل وظاهر وواضح)
#
#  منذ التحديث v2.9.0 أصبح الحجم غير مهم — BadiChartsStudio.py و
#  BadiChartsStudio_readable.py هما نفس الكود بالضبط (نسختان متطابقتان)،
#  مرتّب على ثلاثة أجزاء:
#
#    PART 1 — THE WEB PAGE (studio.html)
#             صفحة الاستوديو كاملة: HTML + CSS + JavaScript
#             (الشارت، محرر الأكواد، المؤشرات، أدوات الرسم، نافذة التسمية)
#
#    PART 2 — BADI-CHARTS-V2 v2.13.0 CHART LIBRARY (badi-chart.js)
#             مكتبة رسم الشموع (كود خارجي ثابت من صانع المكتبة —
#             تُترك مضغوطة فقط لأنها لا تحتاج تعديلاً وتوفّر ~130KB)
#
#    PART 3 — THE DESKTOP APP (Python + QML)
#             التطبيق نفسه: نافذة سطح المكتب، شاشة الدخول، محرك بايثون
#             للمؤشرات، إشارات تلجرام، الثيمات، وجسر الاتصال بالصفحة
#
#  التشغيل:  pip install PySide6   ثم   python BadiChartsStudio.py
#  (أو BadiChartsStudio_readable.py — نفس النتيجة تماماً)
#
#  أحدث الدفعات (v2.13.0):
#   • المكتبة المدمجة ترقّيت إلى BADI-CHARTS-V2 v2.13.0 (نفس الواجهة، بلا كسور)
#   • لوحة الإشارات بتبويبين: الإشارات (الجارية الآن) + السجل (المنتهية بنتيجتها)
#   • المؤشر المشفر (.badi) يعمل داخليًا فقط: لا يُفتح في المحرر، لا يُحفظ،
#     وبطاقته على الشارت بلا زر تعديل — وإشاراته تعمل كأي مؤشر
#   • حماية أقوى: ماسح أنماط ممنوعة (شبكة/تخزين/أجزاء التطبيق الداخلية) يرفض
#     أي كود مشفر يحاول المرور على ملفات التطبيق + فحص QuickJS معزول
#     بحدود ذاكرة ووقت — الكود الخطير يتوقف داخله ولا يلمس ملفات الجهاز أبدًا
#   • المفتاح 256-بت مدموج في الكود، ثابت للجميع، لا يُنسخ ولا يُحفظ ولا يُعرض
#   • معرّف مستخدم ثابت BADI-XXXX-XXXX-XXXX في الشريط السفلي (انقر لنسخه):
#     عشوائي لكل مستخدم، محفوظ بعمق في مواقع مخفية موقّعة HMAC ومربوطة بالجهاز —
#     لا يمكن تغييره ولا نقله إلى جهاز أو تطبيق آخر
#   • ترخيص المؤشر المشفر بالمعرّف: البائع يضع معرّف المشتري في حوار التشفير
#     فيُدمج داخل الملف المشفر — لا يعمل المؤشر إلا على الجهاز المطابق
#   • زر فتح مجلد التطبيق بجوار زر المحرر — يضع فيه المستخدم المؤشرات والأدوات
#   • الإعدادات: منتقي ألوان حرة (نقر المربّع يفتح نافذة الألوان) لكل ألوان الشارت
# ==========================================================================


# ═══════════════════════════════════════════════════════════════════════════
#  PART 1 — THE WEB PAGE (studio.html) — صفحة الاستوديو كاملة وكودها ظاهر
# ═══════════════════════════════════════════════════════════════════════════
STUDIO_HTML = r'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="color-scheme" content="dark"/>
<link rel="icon" href="data:,"/>
<title>Chart Studio — Chart + Indicator Editor & Drawing Tools</title>
<!-- ═══ BADI-CHARTS-V2 v2.13.0 chart library ═══ -->
<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.13.0/chart.js"></script>
<!-- ═══ Monaco code editor — lazy-loaded on first editor open (light startup) ═══ -->
<style>
:root{
  --bg:#0b0e14; --panel:#0e1015; --panel2:#0d1117; --panel3:#131722;
  --border:#1c2030; --border2:#2a2e39; --text:#cfd2da;
  --accent:#0ea5e9; --accent-h:#38bdf8; --accent-t:#7dd3fc;
  --acc-soft:rgba(14,165,233,.12); --acc-bd:rgba(14,165,233,.5);
  --t-bright:#e4e4e7; --t-mid:#a1a1aa; --t-dim:#71717a; --t-dim2:#52525b;
  --t-dim3:#3f3f46; --btn-bg:#1e222d; --ok-soft:rgba(16,185,129,.25);
  --violet:#a78bfa; --ok:#34d399; --err:#f87171;
  --sbar:#2e333c; --sbar-h:#454b56;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Tahoma,Arial,sans-serif;font-size:14px;overflow:hidden}
button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit}
select{font-family:inherit}
svg{vertical-align:middle;flex-shrink:0}
[hidden]{display:none!important}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Courier New",monospace}
.grow{flex:1}
.op70{opacity:.7}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
/* شريط تمرير رقيق وناعم مثل شريط المحرر — بدون حدود سميكة (طلب المستخدم) */
::-webkit-scrollbar-thumb{background:var(--sbar);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--sbar-h)}
::-webkit-scrollbar-corner{background:transparent}

#app{display:flex;flex-direction:column;height:100vh}

/* ═══ Top bar ═══ */
.topbar{position:relative;display:flex;height:48px;flex-shrink:0;align-items:center;gap:6px;background:var(--panel);border-bottom:1px solid var(--border);padding:0 12px}
.tfs{display:flex;overflow:hidden;border-radius:6px;border:1px solid var(--border2)}
.tf{padding:5px 9px;font-size:11px;font-weight:700;background:var(--panel3);color:#a1a1aa;transition:.15s}
.tf:hover{background:var(--btn-bg);color:var(--t-bright)}
.tf.on{background:var(--accent);color:#fff}
/* سهم إخفاء/إظهار قائمة الفريمات (طلب المستخدم): يطوي القائمة ويُبقي الفريم المضبوط ظاهرًا
   ليعرف المستخدم أن هذا مكان الفريمات */
.tf-arrow{display:grid;width:22px;height:22px;flex-shrink:0;place-items:center;border-radius:6px;border:1px solid var(--border2);background:var(--panel3);color:var(--t-dim);transition:.15s}
.tf-arrow:hover{color:var(--t-bright);background:var(--btn-bg)}
.tf-arrow svg{display:block;width:12px;height:12px;transition:transform .18s}
.tf-arrow.on svg{transform:rotate(180deg)}
.tf.tf-hidden{display:none}

/* ═══ Buttons ═══ */
.abtn{display:grid;height:28px;width:28px;place-items:center;border-radius:6px;background:var(--accent);color:#fff;transition:.15s}
.abtn:hover{background:var(--accent-h)}
.ibtn{display:grid;height:28px;width:28px;place-items:center;border-radius:6px;border:1px solid var(--border2);background:var(--panel3);color:#a1a1aa;transition:.15s}
.ibtn:hover{color:var(--t-bright);background:var(--btn-bg)}
.ibtn.wide{width:auto;display:inline-flex;align-items:center;gap:6px;padding:0 10px}
.ibtn.wide .btxt{font-size:11.5px;font-weight:700;letter-spacing:.02em}
.ibtn.on{border-color:var(--acc-bd);background:var(--acc-soft);color:var(--accent-h)}
.ibtn.ghost{border:none;background:transparent;color:#71717a}
.ibtn.ghost:hover{background:var(--btn-bg);color:var(--t-bright)}
.ibtn.danger:hover{background:rgba(239,68,68,.1);color:var(--err);border-color:transparent}
.pulse svg{animation:pulse 1.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}

/* ═══ Main area: chart + editor on the right ═══ */
#main{flex:1;min-height:0;display:flex;flex-direction:column}
#chartPane{display:flex;flex-direction:column;min-width:0;height:44vh;flex-shrink:0}
#resizeHandle{display:none}
@media(min-width:1024px){
  #main{flex-direction:row}
  #chartPane{height:auto;flex:1}
  #resizeHandle{display:block;width:4px;flex-shrink:0;cursor:col-resize;background:var(--border);transition:background .15s}
  #resizeHandle:hover{background:var(--acc-bd)}
  #editorPane{border-top:0}
}
#chartBar{display:flex;flex-direction:column;height:auto;flex-shrink:0;align-items:stretch;gap:0;background:var(--panel);border-bottom:1px solid var(--border);padding:0 0 4px}
#chartRow{display:flex;flex:1;min-height:0}
/* ═══ منطقة الشارت — شارت واحد فقط (تقسيم الشارت أُزيل بطلب المستخدم) ═══ */
#gridHost{position:relative;flex:1;min-width:0;min-height:0;display:grid;gap:5px;padding:5px;background:var(--bg)}
#gridHost[data-n="1"]{grid-template-columns:1fr;grid-template-rows:1fr}
.pane{position:relative;display:flex;flex-direction:column;min-width:0;min-height:0;border:0;border-radius:9px;overflow:hidden;background:var(--bg);cursor:pointer}
/* رأس اللوحة (شريط اسم العملة) أُزيل بالكامل — الشارت يملأ اللوحة الآن (طلب المستخدم) */
.pane-tf{font-size:9.5px;font-weight:800;color:var(--accent-t);background:var(--acc-soft);border-radius:6px;padding:1px 6px;flex-shrink:0;direction:ltr}
.pane-pay{font-size:9.5px;font-weight:800;color:var(--ok);flex-shrink:0}
.pane-cv{position:relative;flex:1;min-height:0}
.pane-cv canvas{position:absolute;inset:0;display:block;width:100%;height:100%}
/* المؤقت التنازلي بجانب الشمعة الحية — أصبح ميزة countdown الأصلية في مكتبة
   BADI-CHARTS v2.13.0: يُرسم داخل الشارت بإحداثياته نفسها، فيحافظ على مسافته عن
   الشمعة مهما كان الزوم، بلا عنصر HTML وبلا حلقة requestAnimationFrame خاصة */
#libLoading{position:absolute;inset:0;display:grid;place-items:center;background:var(--bg);z-index:5}
.loadbox{display:flex;flex-direction:column;align-items:center;gap:12px}
.spin{height:32px;width:32px;border-radius:9999px;border:2px solid var(--border2);border-top-color:var(--accent-h);animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loadtext{font-size:12px;color:var(--t-dim)}
.liberr{display:flex;flex-direction:column;align-items:center;gap:12px;color:var(--t-mid);font-size:13px;text-align:center;padding:0 24px}
.liberr .retry{width:auto;height:32px;padding:0 18px;border-radius:8px;font-size:13px}

/* ═══ شريط معلومات بسيط تحت الشارت — بدل شريط أدوات الرسم المحذوف ═══ */
.chip{border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;background:var(--acc-soft);color:var(--accent-t)}
#statusBar{display:flex;height:26px;flex-shrink:0;align-items:center;gap:7px;padding:0 12px;background:var(--panel);border-top:1px solid var(--border);font-size:10.5px;font-weight:600;color:var(--t-dim);user-select:none;white-space:nowrap;overflow:hidden}
#statusBar .grow{flex:1}
/* معرّف المستخدم الثابت BADI-XXXX-XXXX-XXXX — انقر لنسخه (طلب المستخدم) */
#stUid{cursor:pointer;font-weight:800;letter-spacing:.04em;color:#3B8BFF}
#stUid:hover{text-decoration:underline}
#stUid.copied{color:var(--ok,#22C55E);text-decoration:none}
.st-dot{width:7px;height:7px;border-radius:999px;background:var(--ok);box-shadow:0 0 6px rgba(34,197,94,.55);flex-shrink:0}
.st-dot.live{animation:stpulse 1.2s ease-in-out infinite}
@keyframes stpulse{0%,100%{opacity:1}50%{opacity:.35}}
.st-sep{color:var(--t-dim3)}
#stConn{color:var(--t-mid)}
#stClock,#stFps,#stTz{color:var(--t-mid)}

/* ═══ Signals — side panel on the RIGHT (history of fired signals, black cards) ═══ */
#sigPane{width:272px;flex-shrink:0;display:flex;flex-direction:column;background:var(--panel);border-right:1px solid var(--border)}
#sigHead{display:flex;height:30px;flex-shrink:0;align-items:center;gap:6px;padding:0 10px;font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--t-dim);border-bottom:1px solid var(--border);overflow:hidden}
/* زر الإخفاء داخل رأس البطاقة — بحد واضح بلون الزر حتى يكون ظاهرًا بوضوح */
#sigHead .ibtn{width:22px;height:22px;border-radius:6px;color:var(--accent-h);border-color:var(--acc-bd);background:var(--acc-soft)}
#sigHead .ibtn:hover{background:var(--acc-bd)}
/* زر فتح/غلق البطاقة ثابت لا يختفي + شارة العدد الحمراء الصغيرة 1 2 3 (طلب المستخدم) */
#sigShow{position:relative;flex-shrink:0}
#sigBadge{position:absolute;top:-4px;inset-inline-end:-4px;min-width:15px;height:15px;border-radius:8px;background:#FF4D5E;color:#fff;font-size:9px;font-weight:800;line-height:15px;text-align:center;padding:0 4px;direction:ltr;font-style:normal;box-shadow:0 1px 4px rgba(0,0,0,.45);pointer-events:none}
#sigHead .chip{height:15px;padding:0 6px;font-size:9px}
/* تبويبا لوحة الإشارات: الإشارات (الجارية الآن) + السجل (المنتهية بنتيجتها) — طلب المستخدم */
.sig-tab{display:inline-flex;height:20px;align-items:center;gap:4px;flex-shrink:1;min-width:0;max-width:122px;padding:0 8px;border-radius:999px;border:1px solid transparent;background:transparent;color:var(--t-dim);font-size:9.5px;font-weight:800;letter-spacing:.04em;cursor:pointer;transition:.15s;text-transform:uppercase;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.sig-tab b{font-size:9px;opacity:.65;font-weight:800}
.sig-tab:hover{color:var(--t-mid);background:var(--panel3)}
.sig-tab.on{color:var(--accent-h);background:var(--acc-soft);border-color:var(--acc-bd)}
#sigList{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;gap:8px;padding:9px}
/* بطاقة الإشارة — تصميم محسّن: سوداء دائمًا + شريط اتجاه على الحافة،
   الأخضر #22E08A / الأحمر #FF4D5E كلمسات فقط، حد وظل ملوّنان بلون الاتجاه */
.sigcard{--sc:#22E08A;--scbg:rgba(34,224,138,.26);position:relative;flex-shrink:0;border-radius:12px;padding:10px 12px 8px 14px;color:#F2F5F3;cursor:pointer;overflow:hidden;
  background:radial-gradient(120% 90% at 100% 0%,var(--scbg) 0%,transparent 55%),linear-gradient(180deg,#10161A 0%,#070A0C 100%);
  border:1px solid #2b3a35;box-shadow:0 10px 24px -14px rgba(0,0,0,.7);transition:transform .12s,border-color .15s;
  border-color:color-mix(in srgb,var(--sc) 35%,#1b2227);
  box-shadow:0 10px 24px -14px color-mix(in srgb,var(--sc) 70%,#000)}
.sigcard::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--sc);opacity:.85}
.sigcard:hover{border-color:color-mix(in srgb,var(--sc) 55%,#1b2227);transform:translateY(-1px)}
.sigcard.sell{--sc:#FF4D5E;--scbg:rgba(255,77,94,.26)}
.sigcard.pop{animation:sigpop .9s ease-out}
@keyframes sigpop{0%{box-shadow:0 0 0 0 var(--scbg)}100%{box-shadow:0 0 0 14px transparent}}
@media (prefers-reduced-motion:reduce){.sigcard.pop{animation:none}}
.sig-top{display:flex;direction:ltr;align-items:center;justify-content:space-between;gap:8px;margin:0 0 1px}
.sig-badge{display:inline-flex;align-items:center;gap:5px;background:var(--sc);color:#04100A;font-weight:800;font-size:10.5px;padding:3px 9px;border-radius:999px;letter-spacing:.4px}
.sigcard.sell .sig-badge{color:#1b0407}
.sig-badge svg{width:11px;height:11px}
.sig-res{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:999px;font-weight:800;font-size:10.5px;letter-spacing:.5px}
.sig-res svg{width:11px;height:11px}
.sig-res.win{background:rgba(34,224,138,.16);color:#22E08A}
.sig-res.loss{background:rgba(255,77,94,.16);color:#FF4D5E}
.sig-etime{font-size:10.5px;font-weight:700;color:var(--sc);direction:ltr;white-space:nowrap}
.sig-pair{display:flex;align-items:center;gap:7px;font-size:16.5px;font-weight:800;letter-spacing:.3px;margin:5px 0 6px;color:#F2F5F3;white-space:nowrap}
.sig-pair .aflag{width:23px;height:12px;border-radius:2px}
.sig-rows{border-top:1px solid #1E272D;padding-top:4px;display:flex;flex-direction:column;gap:1px}
.sig-row{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:3px 0;font-size:11px}
.sig-row span{color:#8D9993;flex-shrink:0;display:inline-flex;align-items:center;gap:5px}
.sig-row b{font-weight:600;color:#F2F5F3;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;direction:ltr;text-align:right}
.sig-row .sig-ind{color:#B79CFF;font-weight:700}
.sig-empty{font-size:10.5px;line-height:17px;color:var(--t-dim3);padding:4px 2px}
/* إخفاء/إظهار لوحة الإشارات — زر الإخفاء داخل رأس البطاقة
   وزر الإظهار في شريط أدوات الشارت (بجانب الحذف والملاءمة) حتى لا يغطي
   أي زر الشارت أو علم العملة، ولا يوجد أي إخفاء قسري حسب عرض النافذة */
#sigPane.off{display:none}

/* ═══ Editor pane ═══ */
#editorPane{display:flex;flex-direction:column;min-height:0;flex:1;background:var(--panel2);border-top:1px solid var(--border)}
@media(min-width:1024px){#editorPane{flex:0 0 auto}}
#tabsRow{display:flex;height:36px;flex-shrink:0;align-items:center;gap:4px;overflow-x:auto;background:var(--panel);border-bottom:1px solid var(--border);padding:0 8px}
.tab{display:flex;height:28px;flex-shrink:0;cursor:pointer;align-items:center;gap:6px;border-radius:6px;padding:0 8px;font-size:11px;background:var(--panel3);color:#71717a;transition:.15s;user-select:none;white-space:nowrap}
.tab:hover{color:var(--t-mid)}
.tab.on{background:var(--panel2);color:var(--text);box-shadow:inset 0 -2px 0 0 var(--accent)}
.dot{width:6px;height:6px;flex-shrink:0;border-radius:9999px;background:var(--t-dim3)}
.dot.on{background:var(--ok)}
.kind{display:flex;flex-shrink:0}
.t-ind{color:var(--accent-t)}
.t-tool{color:var(--violet)}
.t-badi{color:var(--ok)}
.tab.badi{background:color-mix(in srgb,var(--ok) 9%,var(--panel3))}
.tab-x{color:var(--t-dim2);opacity:0;transition:.15s;border-radius:4px;display:flex}
.tab:hover .tab-x{opacity:1}
.tab-x:hover{color:var(--err)}
.dirty{color:var(--accent-h);font-size:9px}
.tab-add{display:grid;height:24px;width:24px;flex-shrink:0;place-items:center;border-radius:6px;color:var(--t-dim)}
.tab-add:hover{background:var(--btn-bg);color:var(--t-bright)}
.tab-add.ed-close{margin-inline-start:auto}
.tab-add.ed-close:hover{background:rgba(239,68,68,.12);color:var(--err)}

.edbar{position:relative;display:flex;height:36px;flex-shrink:0;align-items:center;gap:6px;background:#10141d;padding:0 8px;border-bottom:1px solid var(--border)}
.edbar.empty{font-size:11px;color:var(--t-dim);padding:0 12px}
.rbtn{display:grid;height:28px;width:28px;place-items:center;border-radius:6px;background:rgba(16,185,129,.15);color:var(--ok);box-shadow:inset 0 0 0 1px rgba(16,185,129,.4);transition:.15s}
.rbtn:hover{background:var(--ok-soft)}
.kindchip{display:grid;height:24px;width:24px;flex-shrink:0;place-items:center;border-radius:6px}
.kindchip.ind{background:var(--acc-soft);color:var(--accent-h)}
.kindchip.tool{background:rgba(139,92,246,.15);color:var(--violet)}
.fname{font-size:11px;color:var(--t-dim)}
.ed-close-end{margin-inline-start:2px}
.ed-close-end:hover{background:rgba(239,68,68,.12);color:var(--err);border-color:transparent}

#codeHost{position:relative;flex:1;min-height:0}
#codeEmpty{display:none;flex:1;place-items:center}
#codeEmpty.show{display:grid}
.empty-new{display:flex;flex-direction:column;align-items:center;gap:8px;border:1px dashed var(--border2);border-radius:10px;padding:16px 24px;font-size:12px;color:#71717a;transition:.15s}
.empty-new:hover{border-color:var(--acc-bd);color:var(--accent-h)}
.code-ta{width:100%;height:100%;resize:none;background:var(--panel2);color:var(--text);border:0;outline:none;padding:12px;font:13px/20px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;tab-size:2}

/* ═══ Console — يُسحب من رأسه إلى الأعلى ليكبر ويُخفى بزر (طلب المستخدم) ═══ */
#consoleBox{display:flex;height:84px;flex-shrink:0;flex-direction:column;background:var(--bg);border-top:1px solid var(--border)}
#consoleBox.min{height:24px!important}
#consoleBox.min #consoleMsgs{display:none}
#consoleHead{display:flex;height:24px;flex-shrink:0;align-items:center;justify-content:space-between;padding:0 12px;font-size:10px;font-weight:700;color:var(--t-dim);cursor:ns-resize;user-select:none}
#consoleBox.min #consoleHead{color:var(--t-mid)}
.chead-btns{display:flex;align-items:center;gap:4px}
#cClear{color:var(--t-dim2);display:flex}
#cClear:hover{color:var(--t-bright)}
#cHide{color:var(--t-dim2);display:flex}
#cHide:hover{color:var(--t-bright)}
#consoleMsgs{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:0 12px 6px}
.cempty{font-size:10px;color:var(--t-dim3)}
.msg{display:flex;gap:8px;padding:1px 0;font:10.5px/16px ui-monospace,Menlo,Consolas,monospace}
.msg .t{flex-shrink:0;color:var(--t-dim3);direction:ltr}
.msg.err{color:var(--err)}
.msg.ok{color:var(--ok)}
.msg.info{color:var(--t-dim)}
.msg .x{word-break:break-all}

/* ═══ New file modal ═══ */
.modal{position:fixed;inset:0;z-index:100;display:grid;place-items:center;background:rgba(0,0,0,.6);backdrop-filter:blur(2px)}
.modal-card{width:460px;max-width:92vw;background:#11151f;border:1px solid var(--border2);border-radius:14px;padding:20px}
.modal-card h3{font-size:15px;color:var(--text);text-align:left}
.modal-desc{margin-top:8px;font-size:12px;line-height:20px;color:var(--t-mid);text-align:left}
.hl{color:var(--accent-h);margin:0 4px;font-size:11px}
.modal-opts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.opt{display:flex;flex-direction:column;align-items:center;gap:8px;border:1px solid var(--border2);border-radius:12px;background:var(--panel3);padding:16px;transition:.15s}
.opt:hover{border-color:var(--acc-bd);background:var(--acc-soft)}
.opt .oicon{color:var(--accent-h);transition:transform .15s}
.opt:hover .oicon{transform:scale(1.1)}
.opt b{font-size:13px;color:var(--accent-t)}
.opt small{font-size:10.5px;line-height:16px;color:var(--t-dim);text-align:center}
.opt:disabled{opacity:.4;cursor:not-allowed}
.nf-lang{display:flex;gap:10px;margin-top:14px}
.nf-lang button{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:10px;border-radius:10px;border:1px solid var(--border2);background:var(--panel3);color:var(--t-mid);transition:border-color .15s,background .15s,color .15s}
.nf-lang button b{font-size:12.5px;letter-spacing:.02em}
.nf-lang button small{font-size:10px;color:var(--t-dim)}
.nf-lang button:hover{border-color:var(--acc-bd);color:var(--text)}
.nf-lang button.on{border-color:var(--acc-bd);background:var(--acc-soft);color:var(--accent-t)}
.nf-lang button.on b{color:var(--accent-t)}
.nf-name{width:100%;margin-top:12px;padding:10px 13px;border-radius:10px;border:1px solid var(--border2);background:var(--panel3);color:var(--t-bright);font-size:13.5px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;outline:none;transition:border-color .15s,box-shadow .15s}
.nf-name:focus{border-color:var(--acc-bd);box-shadow:0 0 0 3px var(--acc-soft)}
.nf-name::placeholder{color:var(--t-dim2)}
/* ── New-file wizard (3 steps) ── */
.modal-card.wz{width:540px;max-width:94vw;padding:18px 20px 16px}
.wz-head{display:flex;align-items:center;gap:12px}
.wz-head h3{flex:1;font-size:16px}
.wz-dots{display:flex;gap:6px;align-items:center}
.wz-dots i{width:8px;height:8px;border-radius:50%;background:var(--border2);transition:.15s}
.wz-dots i.on{background:var(--accent-h);box-shadow:0 0 0 3px var(--acc-soft)}
.wz-x{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;color:var(--t-mid);background:transparent;border:none;cursor:pointer}
.wz-x:hover{background:var(--panel3);color:var(--text)}
.wz-bar{height:3px;border-radius:2px;background:var(--panel3);margin:10px 0 14px;overflow:hidden}
.wz-bar span{display:block;height:100%;width:33.3%;border-radius:2px;background:linear-gradient(90deg,var(--accent),var(--accent-h));transition:width .2s}
.wz-q{font-size:13px;color:var(--t-mid);margin-bottom:10px;text-align:left}
.wz-q b{color:var(--accent-t)}
.wz-note{font-size:11px;line-height:17px;color:var(--t-dim);margin-top:10px;text-align:left}
.modal-opts .opt{padding:20px 14px}
.modal-opts .opt.on{border-color:var(--acc-bd);background:var(--acc-soft)}
.modal-opts .opt.on b{color:var(--accent-t)}
.wz-foot{display:flex;align-items:center;gap:10px;margin-top:16px}
.wz-btn{padding:9px 24px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;transition:.15s;border:1px solid transparent}
.wz-btn.primary{background:linear-gradient(90deg,var(--accent),var(--accent-h));color:#fff}
.wz-btn.primary:hover{filter:brightness(1.12)}
.wz-btn.primary:disabled{opacity:.45;cursor:not-allowed;filter:none}
.wz-btn.ghost{background:var(--panel3);border-color:var(--border2);color:var(--t-mid)}
.wz-btn.ghost:hover{color:var(--text);border-color:var(--acc-bd)}

/* ═══ Currency strip (chart bar): chips row + a CONTINUOUS scrollbar UNDER the names ═══ */
#chartBar{position:relative}
.cbar-top{display:flex;height:38px;flex-shrink:0;align-items:center;gap:4px;padding:4px 8px 2px}
.achips{display:flex;min-width:120px;flex:1;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none}
.achips::-webkit-scrollbar{display:none}
.cbtn{display:grid;width:22px;height:22px;flex-shrink:0;place-items:center;border-radius:6px;border:1px solid var(--border2);background:var(--panel3);color:var(--t-dim);transition:.15s}
.cbtn:hover{color:var(--t-bright);background:var(--btn-bg)}
.cbtn:disabled{opacity:.35;cursor:default;background:var(--panel3);color:var(--t-dim)}
/* شريط التمرير المصغر: بعرض الشريط كاملاً تحت أسماء العملات — ممتد حتى أيقونة الحذف */
.achip{display:inline-flex;height:26px;flex-shrink:0;align-items:center;gap:6px;border-radius:7px;border:1px solid var(--border2);background:var(--panel3);padding:0 4px 0 7px;cursor:pointer;transition:.15s}
.achip:hover{border-color:var(--acc-bd)}
.achip.on{border-color:var(--acc-bd);background:var(--acc-soft)}
.achip b{font-size:11px;letter-spacing:.02em;color:var(--t-bright);white-space:nowrap}
.achip.on b{color:var(--accent-t)}
.apay{font-style:normal;font-size:10px;font-weight:800;color:var(--ok);white-space:nowrap}
/* شارة حالة السوق: مفتوح/مغلوق بجانب نسبة الدفع (طلب المستخدم) — أخضر/أحمر حسب الحالة */
.amstate{font-style:normal;font-size:9px;font-weight:800;line-height:1;padding:3px 6px;border-radius:6px;flex-shrink:0;white-space:nowrap}
.amstate.open{color:var(--ok);background:rgba(52,211,153,.14)}
.amstate.closed{color:var(--err);background:rgba(248,113,113,.14)}
.amdot{display:inline-block;width:6px;height:6px;border-radius:50%;flex-shrink:0}
.amdot.open{background:var(--ok)}
.amdot.closed{background:var(--err)}
/* علامة × الصغيرة داخل بطاقة العملة — إزالة العملة من الشريط مباشرة من البطاقة نفسها (طلب المستخدم) */
.achip .adel{display:grid;width:15px;height:15px;place-items:center;border-radius:4px;color:var(--t-dim2);flex-shrink:0;transition:.15s}
.achip .adel:hover{color:var(--err);background:rgba(248,113,113,.16)}
.achip .adel svg{display:block;width:8px;height:8px}
.aflag{display:block;width:21px;height:11px;border-radius:2px}
.aempty{font-size:10.5px;color:var(--t-dim2);white-space:nowrap}

@media(max-width:640px){.tfs,.tf-arrow{display:none}}

/* ═══ Currency list popup (+ button): search + add/remove ═══ */
#assetMenu{position:absolute;top:60px;left:4px;z-index:70;display:flex;flex-direction:column;width:264px;max-height:330px;border-radius:12px;background:var(--panel3);border:1px solid var(--border2);box-shadow:0 16px 34px -14px rgba(0,0,0,.65);overflow:hidden}
.am-search{display:flex;align-items:center;gap:7px;padding:8px 10px;border-bottom:1px solid var(--border);color:var(--t-dim)}
.am-search input{flex:1;min-width:0;border:0;background:transparent;color:var(--t-bright);font:600 12px/1 inherit;outline:none;font-family:inherit}
.am-search input::placeholder{color:var(--t-dim2)}
#amList{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:5px}
.am-row{display:flex;width:100%;align-items:center;gap:8px;border:0;background:transparent;border-radius:8px;padding:6px 8px;cursor:pointer;color:var(--t-bright);text-align:left}
.am-row:hover{background:var(--btn-bg)}
.am-row .aflag{width:25px;height:13px;flex-shrink:0}
.am-row b{flex:1;min-width:0;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.am-row .apay{font-style:normal;font-size:10px;font-weight:800;color:var(--ok);flex-shrink:0}
.am-tog{display:grid;width:20px;height:20px;flex-shrink:0;place-items:center;border-radius:6px;border:1px solid var(--border2);color:var(--t-dim)}
.am-tog.on{background:var(--accent);border-color:var(--accent);color:#fff}
</style>
</head>
<body>
<div id="app">

  <!-- ═══ Top bar — timeframes · library · screenshot ‖ telegram · editor · folder · logout
       زر الوضع الليلي/النهاري في الترويسة العليا للتطبيق فقط (طلب المستخدم)
       والشموع الحية تعمل مباشرة دائمًا — لا زر لتشغيل/إيقاف البث ═══ -->
  <header class="topbar">
    <div class="tfs" id="tfGroup"></div>
          <button id="tfArrow" class="tf-arrow" title="Hide/show the timeframes"></button>
    <button id="shotBtn" class="ibtn" title="Screenshot the chart" aria-label="Take a chart screenshot"></button>
    <span class="grow"></span>
    <button id="webTg" class="ibtn wide" title="Telegram bot — signals, results and history" aria-label="Open the Telegram bot page"></button>
    <!-- زر المؤشرات بجوار زر المحرر مباشرة (طلب المستخدم) -->
    <button id="indBtn" class="ibtn wide" title="Indicators library" aria-label="Open the indicators library"></button>
    <button id="edToggle" class="ibtn wide" title="Open or close the editor" aria-label="Open or close the editor"></button>
    <button id="dirBtn" class="ibtn wide" title="Open the app folder — drop your indicators and tools here" aria-label="Open the app folder"></button>
    <button id="webLogout" class="ibtn danger" title="Log out" aria-label="Log out"></button>
  </header>

  <div id="main">
    <!-- ═══ Chart pane ═══ -->
    <section id="chartPane">
      <div id="chartBar">
        <div class="cbar-top">
          <!-- طلب المستخدم: زر واحد ثابت لفتح وغلق بطاقة الإشارات لا يختفي أبدًا + شارة حمراء بعدد الإشارات -->
          <button id="sigShow" class="ibtn" title="Open or close the signals panel" aria-label="Open or close the signals panel"><i id="sigBadge" hidden></i></button>
          <!-- زر فتح قائمة العملات: بجانب السهمين وبحجم زر فتح بطاقة الإشارات (طلب المستخدم) -->
          <button id="assetAdd" class="ibtn" title="Add or remove currencies" aria-label="Open the currency list"></button>
          <button id="assetPrev" class="cbtn" title="Scroll the currencies back" aria-label="Scroll back"></button>
          <button id="assetNext" class="cbtn" title="Scroll the currencies forward" aria-label="Scroll forward"></button>
          <div id="assetChips" class="achips"></div>
          <button id="fitBtn" class="ibtn ghost" title="Fit view to all data" aria-label="Fit view"></button>
        </div>
        <div id="assetMenu" hidden>
          <div class="am-search"><span id="amSearchIco"></span><input id="amSearch" type="text" placeholder="Search a currency…" autocomplete="off" spellcheck="false"></div>
          <div id="amList" class="custom-scroll"></div>
        </div>
      </div>
      <div id="chartRow">
        <!-- ═══ لوحة الإشارات في الجهة اليسرى (طلب المستخدم): تبويبان — الإشارات الحالية + السجل ═══ -->
        <aside id="sigPane">
          <div id="sigHead">
            <button id="sigTabSig" class="sig-tab on" type="button"></button>
            <button id="sigTabHist" class="sig-tab" type="button"></button>
            <span class="grow"></span>
            <button id="sigSound" class="ibtn ghost" title="Mute or unmute the signal sounds" aria-label="Toggle signal sounds"></button>
            <button id="sigClear" class="ibtn ghost" title="Clear the signals list" aria-label="Clear signals"></button>
            <button id="sigHide" class="ibtn" title="Hide the signals panel" aria-label="Hide the signals panel"></button>
          </div>
          <div id="sigList" class="custom-scroll"></div>
        </aside>
        <!-- ═══ Multi-chart grid — each pane works on its own (asset + timeframe) ═══ -->
        <div id="gridHost" data-n="1">
          <div id="libLoading">
            <div class="loadbox">
              <div class="spin"></div>
              <p class="loadtext">Loading the chart library…</p>
            </div>
          </div>
        </div>
      </div>
      <!-- ═══ شريط معلومات بسيط تحت الشارت: متصل · المنطقة الزمنية · الوقت · FPS (بدون اسم العملة — طلب المستخدم) ═══ -->
      <div id="statusBar">
        <span id="stBrand" class="mono">BADI STUDIO v2.13.1</span>
        <span class="st-sep">·</span>
        <span id="stDot" class="st-dot"></span><span id="stConn">Connected</span>
        <span class="grow"></span>
        <span id="stTz" class="mono" dir="ltr">UTC—</span>
        <span class="st-sep">·</span>
        <span id="stClock" class="mono">—</span>
        <span class="st-sep">·</span><span id="stFps" class="mono">— FPS</span>
        <span class="st-sep">·</span><span id="stUid" class="mono" dir="ltr">BADI-····-····-····</span>
      </div>
    </section>

    <!-- Editor resize handle -->
    <div id="resizeHandle" title="Drag to resize the editor — double-click to reset"></div>

    <!-- ═══ Editor pane — right side ═══ -->
    <section id="editorPane">
      <div id="tabsRow"></div>

      <div id="edBarFull" class="edbar" hidden>
        <button id="runBtn" class="abtn" title="Run and apply to the chart (Ctrl+Enter)" aria-label="Run"></button>
        <button id="edNewBtn" class="abtn" title="Create a new file — you choose the name and the language" aria-label="New file"></button>
        <button id="saveBtn" class="ibtn" title="Save in browser (Ctrl+S)" aria-label="Save"></button>
        <!-- BADI: تشفير المؤشر الحالي إلى ملف .badi + استيراد مؤشر مشفر — المفتاح يبقى داخل التطبيق -->
        <button id="badiEnc" class="ibtn" title="Encrypt the indicator — export a .badi file" aria-label="Export the encrypted indicator"></button>
        <button id="badiImp" class="ibtn" title="Import an encrypted indicator (.badi)" aria-label="Import an encrypted indicator"></button>
        <span id="kindChip" class="kindchip ind"></span>
        <span class="grow"></span>
        <span id="edFileName" dir="ltr" class="mono fname"></span>
        <button id="delBtn" class="ibtn danger" title="Delete file" aria-label="Delete file"></button>
        <button id="edCloseBtn" class="ibtn ed-close-end" title="Close the editor" aria-label="Close the editor"></button>
      </div>
      <div id="edBarEmpty" class="edbar empty">No file selected — pick a file above or create a new one.
        <button id="badiImpEmpty" class="ibtn" title="Import an encrypted indicator (.badi)" aria-label="Import an encrypted indicator"></button></div>

      <div id="codeEmpty"><button id="emptyNew" class="empty-new"></button></div>
      <div id="codeHost" dir="ltr"></div>

      <div id="consoleBox">
        <div id="consoleHead" title="Drag up to enlarge the console — double-click or the arrow button to hide and show">
          <span>Console</span>
          <span class="chead-btns">
            <button id="cClear" title="Clear console" aria-label="Clear console"></button>
            <button id="cHide" title="Hide or show the console — drag the header up to enlarge it" aria-label="Hide or show the console"></button>
          </span>
        </div>
        <div id="consoleMsgs" class="custom-scroll"></div>
      </div>
    </section>
  </div>
</div>

<!-- ═══ New file wizard: 1 type → 2 language → 3 name ═══ -->
<div id="newModal" class="modal" hidden>
  <div class="modal-card wz" role="dialog" aria-modal="true" aria-label="Create new file">
    <div class="wz-head">
      <h3 id="wzTitle">Create New File</h3>
      <span class="wz-dots" id="wzDots"><i class="on"></i><i></i><i></i></span>
      <button id="wzClose" class="wz-x" title="Close" aria-label="Close"></button>
    </div>
    <div class="wz-bar"><span id="wzBar"></span></div>
    <div class="wz-pane" id="wzPane1">
      <p class="wz-q">What do you want to create?</p>
      <div class="modal-opts">
        <button id="optIndicator" class="opt"></button>
        <button id="optTool" class="opt"></button>
      </div>
    </div>
    <div class="wz-pane" id="wzPane2" hidden>
      <p class="wz-q">Choose the language</p>
      <div class="nf-lang" id="nfLang">
        <button id="nfLangJs" type="button"><b>JavaScript</b><small>.js — runs inside the chart</small></button>
        <button id="nfLangPy" type="button"><b>Python</b><small>.py — desktop engine</small></button>
      </div>
      <p class="wz-note" id="wzLangNote" hidden>Drawing tools run in JavaScript only.</p>
    </div>
    <div class="wz-pane" id="wzPane3" hidden>
      <p class="wz-q">Name your <b id="wzKindLabel">indicator</b></p>
      <input id="nfName" class="nf-name" dir="auto" placeholder="My Indicator" maxlength="40" spellcheck="false" autocomplete="off">
      <p class="wz-note">The file opens in the editor right away — indicators run after ▶ Run, drawing tools activate immediately.</p>
    </div>
    <div class="wz-foot">
      <button id="wzBack" class="wz-btn ghost" type="button" hidden>Back</button>
      <span class="grow"></span>
      <button id="wzNext" class="wz-btn primary" type="button" disabled>Continue</button>
    </div>
  </div>
</div>

<noscript>This application requires JavaScript to be enabled in the browser.</noscript>
<script>
"use strict";
/* ═══════════════════════════════════════════════════════════════
   Chart Studio — single self-contained HTML file
   chart + indicator editor and drawing tools on top of BADI-CHARTS-V2 v2.13.0
   No indicator runs automatically — everything waits for the user to press ▶.
   ═══════════════════════════════════════════════════════════════ */

/* ───────────── Helpers ───────────── */
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
/* رسائل إلى تطبيق سطح المكتب (بوابة الجسر — متاحة في وضع التضمين فقط) */
function badiSend(cmd, arg) {
  const f = window.__badiSend;
  if (!f) return;
  try { f(cmd, arg); } catch (e) {}
}

/* ───────────── Inline SVG icons (no external icon library) ───────────── */
const ICONS = {
  "mouse-pointer": '<path d="M4.037 4.688a.495.495 0 0 1 .651-.651l16 6.5a.5.5 0 0 1-.063.947l-6.124 1.58a2 2 0 0 0-1.438 1.435l-1.579 6.126a.5.5 0 0 1-.947.063z"/>',
  "lock":      '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  "dl":        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="3" y2="15"/>',
  "slash": '<path d="M5 19 19 5"/>',
  "columns": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 3v18"/>',
  "minus": '<path d="M5 12h14"/>',
  "vline": '<path d="M12 3v18"/>',
  "band": '<path d="M4 7h16"/><path d="M4 17h16"/><path d="M4 12h16" stroke-opacity=".45"/>',
  "square": '<rect x="4" y="4" width="16" height="16" rx="2"/>',
  "arrow-up-right": '<path d="M7 17 17 7"/><path d="M8 7h9v9"/>',
  "percent": '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
  "brush": '<path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08"/><path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z"/>',
  "hexagon": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
  "type": '<polyline points="4 7 4 4 20 4 20 7"/><line x1="9" x2="15" y1="20" y2="20"/><line x1="12" x2="12" y1="4" y2="20"/>',
  "move-up-right": '<path d="M13 5h6v6"/><path d="M19 5 5 19"/>',
  "eraser": '<path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/>',
  "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
  "stop": '<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
  "rotate": '<path d="M21 12a9 9 0 1 1-2.64-6.36L21 8"/><path d="M21 3v5h-5"/>',
  "save": '<path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/>',
  "trash": '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
  "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
  "maximize": '<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" x2="14" y1="3" y2="10"/><line x1="3" x2="10" y1="21" y2="14"/>',
  "radio": '<path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/><path d="M19.1 4.9C23 8.8 23 15.2 19.1 19.1"/>',
  "panel-right": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M15 3v18"/>',
  "file-plus": '<path d="M15 2H5a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7z"/><path d="M14 2v5h5"/><path d="M12 11v6"/><path d="M9 14h6"/>',
  "pen": '<path d="m12 19 7-7 3 3-7 7-3-3z"/><path d="m18 13-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="m2 2 7.586 7.586"/><circle cx="11" cy="11" r="2"/>',
  "candle": '<path d="M9 5v4"/><rect x="7" y="9" width="4" height="6" rx="1"/><path d="M9 15v2"/><path d="M17 3v2"/><rect x="15" y="5" width="4" height="8" rx="1"/><path d="M17 13v3"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
  "check": '<path d="M20 6 9 17l-5-5"/>',
  "chevron-down": '<path d="m6 9 6 6 6-6"/>',
  "chevron-up": '<path d="m18 15-6-6-6 6"/>',
  "chevron-left": '<path d="m15 18-6-6 6-6"/>',
  "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  "arrowsUpDown": '<path d="m3 16 4 4 4-4"/><path d="M7 20V8"/><path d="m21 8-4-4-4 4"/><path d="M17 4v12"/>',
  "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
  "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
  "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
  "chevron-right": '<path d="m9 18 6-6-6-6"/>',
  "gear": '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  "up": '<path d="M7 17 17 7M8 7h9v9"/>',
  "down": '<path d="M7 7l10 10M17 8v9H8"/>',
  "volume": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>',
  "volumex": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="22" x2="16" y1="9" y2="15"/><line x1="16" x2="22" y1="9" y2="15"/>',
  "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
  "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
  "folder": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
};
function icon(name, size, cls) {
  return '<svg class="' + (cls || "") + '" width="' + (size || 14) + '" height="' + (size || 14) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICONS[name] || "") + "</svg>";
}

/* ───────────── Built-in drawing tools: name + icon ───────────── */
const TOOL_NAMES = {
  cursor: "Cross cursor",
  trend: "Trend line",
  channel: "Parallel channel",
  hline: "Horizontal line",
  vline: "Vertical line",
  band: "Range / zone",
  rect: "Rectangle",
  arrow: "Arrow",
  fib: "Fibonacci retracement",
  brush: "Free brush",
  poly: "Polygon",
  text: "Text",
  ray: "Ray",
  eraser: "Eraser (delete a drawing)"
};
const TOOL_ICONS = {
  cursor: "mouse-pointer", trend: "slash", channel: "columns", hline: "minus",
  vline: "vline", band: "band", rect: "square", arrow: "arrow-up-right",
  fib: "percent", brush: "brush", poly: "hexagon", text: "type",
  ray: "move-up-right", eraser: "eraser"
};

/* ───────────── Candle data (seeded simulation + live feed) ───────────── */
const SYMBOLS = {
  BTCUSDT: { label: "BTC/USDT", base: 67240, vol: 0.011, decimals: 2 },
  ETHUSDT: { label: "ETH/USDT", base: 3268, vol: 0.013, decimals: 2 },
  SOLUSDT: { label: "SOL/USDT", base: 147.6, vol: 0.018, decimals: 2 },
  XAUUSD: { label: "XAU/USD", base: 2382, vol: 0.006, decimals: 2 }
};
const TIMEFRAMES = {
  "5s": 5 * 1000,
  "10s": 10 * 1000,
  "15s": 15 * 1000,
  "30s": 30 * 1000,
  "1m": 60 * 1000,
  "2m": 2 * 60000,
  "3m": 3 * 60000,
  "5m": 5 * 60000,
  "10m": 10 * 60000,
  "15m": 15 * 60000,
  "30m": 30 * 60000,
  "1H": 60 * 60000,
  "4H": 4 * 60 * 60000,
  "1D": 24 * 60 * 60000
};
function tfMs(k) { return TIMEFRAMES[k] || TIMEFRAMES["1m"]; }
const SYMBOL_KEYS = Object.keys(SYMBOLS);
const TF_KEYS = Object.keys(TIMEFRAMES);

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function hashStr(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function round(v, d) { const f = Math.pow(10, d); return Math.round(v * f) / f; }

function generateCandles(cfg, tfKey, count) {
  count = count || 620;
  tfKey = tfKey || "1m";
  const tfMs0 = tfMs(tfKey);
  const rnd = mulberry32(hashStr(cfg.label + ":" + tfKey));
  const tfSec = tfMs0 / 1000;
  const now = Math.floor(Date.now() / 1000);
  const endTime = Math.floor(now / tfSec) * tfSec;
  const candles = [];
  let price = cfg.base * (0.82 + rnd() * 0.36);
  let drift = 0, vola = cfg.vol, regimeLeft = 0;
  for (let k = 0; k < count; k++) {
    if (regimeLeft <= 0) {
      regimeLeft = 18 + Math.floor(rnd() * 60);
      const dir = rnd() < 0.42 ? 0 : rnd() < 0.5 ? 1 : -1;
      drift = dir * cfg.vol * (0.05 + rnd() * 0.22);
      vola = cfg.vol * (0.55 + rnd() * 1.15);
    }
    regimeLeft--;
    const open = price;
    const shock = (rnd() + rnd() + rnd() - 1.5) * 1.15;
    const close = Math.max(cfg.base * 0.05, open * (1 + drift + shock * vola));
    const wickUp = Math.abs(shock) * vola * (0.25 + rnd() * 0.9) * open;
    const wickDn = Math.abs(shock) * vola * (0.25 + rnd() * 0.9) * open;
    const high = Math.max(open, close) + wickUp * 0.6;
    const low = Math.min(open, close) - wickDn * 0.6;
    const bodyPct = Math.abs(close - open) / open;
    const volume = Math.round((0.6 + rnd() * 0.8 + bodyPct / Math.max(vola, 1e-9) * 0.35) * 9000);
    candles.push({
      time: endTime - (count - 1 - k) * tfSec,
      open: round(open, cfg.decimals),
      high: round(high, cfg.decimals),
      low: round(low, cfg.decimals),
      close: round(close, cfg.decimals),
      volume: volume
    });
    price = close;
  }
  return candles;
}
function stepCandle(c, vol) {
  const drift = (Math.random() - 0.5) * 2 * vol * 0.14 * c.close;
  const close = Math.max(1e-6, c.close + drift);
  return {
    time: c.time, open: c.open,
    close: close,
    high: Math.max(c.high, close),
    low: Math.min(c.low, close),
    volume: c.volume + Math.round(Math.random() * c.volume * 0.012 + 1)
  };
}
function newCandleFrom(prev, tfMs, vol) {
  const open = prev.close;
  const first = open * (1 + (Math.random() - 0.5) * 2 * vol * 0.1);
  return {
    time: prev.time + tfMs / 1000,
    open: open,
    high: Math.max(open, first),
    low: Math.min(open, first),
    close: first,
    volume: Math.round(50 + Math.random() * 300)
  };
}

/* ───────────── Code templates + ready examples (all disabled by default) ───────────── */
const INDICATOR_TEMPLATE = `// ═══════════════════════════════════════════════════════════
//  Chart Studio — Custom indicator
//  The code returns the indicator definition object via return { ... }
//
//  calculate(candles, s)  ← computation (runs on every data update)
//      candles : array of candles [{time, open, high, low, close, volume}]
//      s       : settings (from settings below, edited via the ⚙ icon on the chart)
//      returns : a number array, or an object like {mid, upper, lower} or {fast, slow}
//
//  render(ctx, values, h, s)  ← drawing (optional — without it every series is
//      drawn automatically as a line using the definition color / palette)
//      ctx    : Canvas 2D context
//      values : the calculate output
//      h      : coordinate helpers:
//          h.indexToX(i)   candle index → pixel X
//          h.priceToY(p)   price → pixel Y        (overlay type)
//          h.paneToY(v)    value → pixel Y        (pane type)
//          h.firstIdx / h.lastIdx / h.candles / h.THEME / h.barSpacing
//
//  Ready-made math helpers:
//      Indicators.sma(v, p)   Indicators.ema(v, p)
//      Indicators.bollinger(v, p, m)   Indicators.rsi(v, p)
//      Indicators.macd(v, f, sl, sg)   Indicators.volumeProfile(candles, bins)
//
//  Print messages: log('text') ← shows in the editor console
// ═══════════════════════════════════════════════════════════

return {
  label: 'My Custom Indicator',
  type: 'overlay',           // 'overlay' over the candles  |  'pane' in a bottom pane
  color: '#38bdf8',
  settings: { period: 20 },  // keys period/mult/fast/slow/signal/bins/color appear in the settings card

  calculate(candles, s) {
    const closes = candles.map(c => c.close);
    return Indicators.sma(closes, s.period);
  },

  // for the 'pane' type you can set the range (optional):
  // getRange(values, s) { return { min: 0, max: 100 }; },

  render(ctx, values, h, s) {
    if (!values) return;
    ctx.strokeStyle = s.color || this.color;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    let started = false;
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      const v = values[i];
      if (v == null) { started = false; continue; }
      const x = h.indexToX(i);
      const y = this.type === 'pane' ? h.paneToY(v) : h.priceToY(v);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
};
`;

const TOOL_TEMPLATE = `// ═══════════════════════════════════════════════════════════
//  Chart Studio — Custom drawing tool
//  The code returns the tool definition object via return { ... }
//
//  onStart(ctx)           when the drag starts
//      ctx = { x, y, idx, price }   ← pixel coordinates + (candle index, price)
//      return the drawing object where you store your data.
//
//  onUpdate(d, ctx)       while dragging — modify the drawing object d
//
//  onDraw(ctx, d, h)      drawing on every frame
//      h = { indexToX(i), priceToY(p), xToIndex(x), yToPrice(y),
//            chartLeft, chartRight, chartTop, chartBottom,
//            priceTop, priceBottom, barSpacing, THEME }
//
//  onHitTest(d, x, y, h)  return true if the click (x,y) is over the drawing
//                         (used for selection / deletion / properties panel)
//
//  Tip: store coordinates as (index, price) {i1, p1, i2, p2}
//         so your drawings stay glued to the candles when zooming/panning.
// ═══════════════════════════════════════════════════════════

return {
  label: 'My Custom Tool',
  icon: '✦',                 // the symbol shown in the tools bar
  defaultStyle: { color: '#38bdf8', lineWidth: 2 },

  onStart(ctx) {
    return { i1: ctx.idx, p1: ctx.price, i2: ctx.idx, p2: ctx.price };
  },

  onUpdate(d, ctx) {
    d.i2 = ctx.idx;
    d.p2 = ctx.price;
  },

  onDraw(ctx, d, h) {
    const x1 = h.indexToX(d.i1), y1 = h.priceToY(d.p1);
    const x2 = h.indexToX(d.i2), y2 = h.priceToY(d.p2);
    ctx.strokeStyle = d.color;
    ctx.lineWidth = d.lineWidth || 2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    // handles at both ends
    ctx.fillStyle = d.color;
    for (const p of [[x1, y1], [x2, y2]]) {
      ctx.beginPath();
      ctx.arc(p[0], p[1], 3.5, 0, Math.PI * 2);
      ctx.fill();
    }
  },

  onHitTest(d, x, y, h) {
    const x1 = h.indexToX(d.i1), y1 = h.priceToY(d.p1);
    const x2 = h.indexToX(d.i2), y2 = h.priceToY(d.p2);
    const len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const t = Math.max(0, Math.min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (len * len)));
    const px = x1 + t * (x2 - x1), py = y1 + t * (y2 - y1);
    return Math.hypot(x - px, y - py) <= 6;
  }
};
`;

const EXAMPLE_EMA_CROSS = `// Example 1 — EMA cross drawn over the candles
// Edit fast/slow from the ⚙ icon next to the indicator name on the chart
return {
  label: 'EMA Cross (example)',
  type: 'overlay',
  color: '#26a69a',
  settings: { fast: 9, slow: 21 },

  calculate(candles, s) {
    const closes = candles.map(c => c.close);
    return {
      fast: Indicators.ema(closes, s.fast),
      slow: Indicators.ema(closes, s.slow)
    };
  },

  render(ctx, v, h, s) {
    if (!v) return;
    const line = (arr, color, width) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.beginPath();
      let started = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        const val = arr[i];
        if (val == null) { started = false; continue; }
        const x = h.indexToX(i), y = h.priceToY(val);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    };
    line(v.slow, '#ef5350', 1.4);
    line(v.fast, '#26a69a', 1.6);
  }
};
`;

const EXAMPLE_RSI = `// Example 2 — RSI indicator in a bottom pane with 30/70 overbought/oversold zones
return {
  label: 'RSI (example)',
  type: 'pane',
  color: '#b39ddb',
  settings: { period: 14 },

  calculate(candles, s) {
    return Indicators.rsi(candles.map(c => c.close), s.period);
  },

  getRange() { return { min: 0, max: 100 }; },

  render(ctx, v, h, s) {
    if (!v) return;
    const y70 = h.paneToY(70), y30 = h.paneToY(30);
    // transparent 30-70 zone
    ctx.fillStyle = 'rgba(179,157,219,0.07)';
    ctx.fillRect(h.chartLeft, y70, h.chartRight - h.chartLeft, y30 - y70);
    // overbought/oversold levels
    ctx.setLineDash([3, 3]);
    for (const pair of [[y70, '#ef5350'], [y30, '#26a69a']]) {
      ctx.strokeStyle = pair[1];
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(h.chartLeft, pair[0]);
      ctx.lineTo(h.chartRight, pair[0]);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    // indicator line
    ctx.strokeStyle = s.color || this.color;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    let started = false;
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      const val = v[i];
      if (val == null) { started = false; continue; }
      const x = h.indexToX(i), y = h.paneToY(val);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
};
`;

const EXAMPLE_SIGNAL_ARROW = `// Example 3 — "Signal Arrow" tool: click anywhere on the chart to place an arrow
return {
  label: 'Signal Arrow (example)',
  icon: '⬆',
  defaultStyle: { color: '#38bdf8', lineWidth: 2 },

  onStart(ctx) {
    return { i1: ctx.idx, p1: ctx.price };
  },

  onDraw(ctx, d, h) {
    const x = h.indexToX(d.i1);
    const y = h.priceToY(d.p1);
    ctx.strokeStyle = d.color;
    ctx.fillStyle = d.color;
    ctx.lineWidth = d.lineWidth || 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(x, y + 16);
    ctx.lineTo(x, y - 13);
    ctx.moveTo(x - 7, y - 5);
    ctx.lineTo(x, y - 15);
    ctx.lineTo(x + 7, y - 5);
    ctx.stroke();
  },

  onHitTest(d, x, y, h) {
    const dx = x - h.indexToX(d.i1);
    const dy = y - h.priceToY(d.p1);
    return dx * dx + dy * dy < 22 * 22;
  }
};
`;

/* ───────────── Local storage + random names ───────────── */
const STORAGE_KEY = "badi-studio-v2";
const NAME_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; // no ambiguous O/0 or I/1

function randomSuffix(n) {
  n = n || 6;
  let s = "";
  const buf = new Uint32Array(n);
  if (window.crypto && crypto.getRandomValues) crypto.getRandomValues(buf);
  else for (let i = 0; i < n; i++) buf[i] = Math.floor(Math.random() * 0xffffffff);
  for (let i = 0; i < n; i++) s += NAME_CHARS[buf[i] % NAME_CHARS.length];
  return s;
}
/** Clean a user-typed file name (no illegal/path chars), spaces allowed */
function cleanName(s, fallback) {
  let t = String(s || "").trim().replace(/[\\/:*?"<>|]/g, "").replace(/\s+/g, " ").slice(0, 40).trim();
  return t || fallback;
}
/** Append " 2", " 3" … when the name already exists */
function uniqueFileName(base) {
  const taken = {};
  files.forEach((f) => { taken[f.fileName] = 1; });
  if (!taken[base]) return base;
  const m = base.match(/(\.[a-z]+)$/i);
  const ext = m ? m[1] : "";
  const stem = m ? base.slice(0, base.length - ext.length) : base;
  let n = 2;
  while (taken[stem + " " + n + ext]) n++;
  return stem + " " + n + ext;
}
/** Display name for chart legend/alerts — file name without the extension */
function fileLabel(s) { return String(s || "").replace(/\.(js|py)$/i, ""); }

/** Build a new file — the user chooses the name and the language (js / py) */
function makeFile(kind, userName) {
  const sfx = randomSuffix(6);
  const isPy = kind === "py";
  const fallback = isPy ? "Python Indicator" : (kind === "tool" ? "My Tool" : "My Indicator");
  const code = isPy
    ? ((window.__BADI_BOOT_FILES && window.__BADI_BOOT_FILES.pyTemplate) || "# Python indicator\n")
    : (kind === "tool" ? TOOL_TEMPLATE : INDICATOR_TEMPLATE);
  return {
    id: (isPy ? "py_" : kind === "tool" ? "tool_" : "ind_") + sfx.toLowerCase(),
    fileName: uniqueFileName(cleanName(userName, fallback) + (isPy ? ".py" : ".js")),
    kind: isPy ? "py" : kind,
    code: code,
    enabled: false,
    createdAt: Date.now()
  };
}
function loadFiles() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (!data || !Array.isArray(data.files)) return null;
    return data.files.filter((f) => f && typeof f.id === "string" && typeof f.code === "string" && (f.kind === "indicator" || f.kind === "tool"));
  } catch (e) { return null; }
}
function saveFiles(list) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ files: list })); } catch (e) { /* storage full or blocked */ }
}
function seedExamples() {
  const s1 = randomSuffix(6), s2 = randomSuffix(6), s3 = randomSuffix(6);
  return [
    { id: "ind_" + s1.toLowerCase(), fileName: "EMA Cross.js", kind: "indicator", code: EXAMPLE_EMA_CROSS, enabled: false, createdAt: Date.now() },
    { id: "ind_" + s2.toLowerCase(), fileName: "RSI Zones.js", kind: "indicator", code: EXAMPLE_RSI, enabled: false, createdAt: Date.now() - 1000 },
    { id: "tool_" + s3.toLowerCase(), fileName: "Signal Arrow.js", kind: "tool", code: EXAMPLE_SIGNAL_ARROW, enabled: false, createdAt: Date.now() - 2000 }
  ];
}

/** Run user code in a closed scope and return the definition object (must end with return {...}) */
function compileScript(code, logFn) {
  try {
    const fn = new Function("Indicators", "THEME", "log", '"use strict";\n' + code);
    const def = fn(window.Indicators, window.THEME, logFn);
    if (!def || typeof def !== "object") {
      return { def: null, error: "The code must return the definition object via return { ... }" };
    }
    return { def: def, error: null };
  } catch (e) {
    return { def: null, error: e instanceof Error ? e.message : String(e) };
  }
}

/* ───────────── State ───────────── */
let files = [];
let activeId = null;
const dirtyIds = new Set();   // files not saved yet (● dot)
const editedIds = new Set();  // code edited after the last successful run (↻ re-run)
let editorOpen = false;
let editorW = 430;
let tool = "cursor";
let symbol = "BTCUSDT";       // web-mode default asset key
let live = true;               /* الشموع الحية متحركة مباشرة دائمًا — بلا زر تشغيل/إيقاف (طلب المستخدم) */
let msgs = [];
let msgSeq = 0;
const errCounts = new Map();
let saveTimer = 0;

/* ── Multi-chart state: كل شارت يعمل بنفسه باسم عملته وفريمه ── */
let panes = [];               // {el, head, cv, chart, dataArr, asset, tf, tick}
/* حالة الواجهة العامة: شريط الحالة السفلي + العد التنازلي بجانب الشمعة الحية —
   تُدار من لوحة إعدادات سطح المكتب وتُحفظ في localStorage (طلب المستخدم) */
window.__BADI_UI__ = (function () {
  var sb = true, cd = true;
  try { sb = localStorage.getItem("badiStatusBar") !== "0"; } catch (e) {}
  try { cd = localStorage.getItem("badiCd") !== "0"; } catch (e) {}
  return { sb: sb, cd: cd };
})();
try { var _badiSb = document.getElementById("statusBar"); if (_badiSb) _badiSb.style.display = window.__BADI_UI__.sb ? "" : "none"; } catch (e) {}

let activePane = 0;           // the selected pane (light border + editor target)
let primaryPane = 0;          // the pane fed by the desktop engine (asset === CUR_ASSET)
let CUR_ASSET = "";           // active currency label (embedded: synced from Python)
const activeFile = () => files.find((f) => f.id === activeId) || null;
const aPane = () => panes[activePane] || null;
const aChart = () => (panes[activePane] ? panes[activePane].chart : null);
const pChart = () => (panes[primaryPane] ? panes[primaryPane].chart : null);
function paneIdxByAsset(name) { return panes.findIndex((p) => p.asset === name); }
/** Symbol simulation config for any board name (known labels reuse SYMBOLS) */
function assetCfg(name) {
  for (const k of SYMBOL_KEYS) if (SYMBOLS[k].label === name) return SYMBOLS[k];
  const h = hashStr(name);
  if (name.indexOf("BTC") >= 0) return { label: name, base: 67000 + (h % 400), vol: 0.011, decimals: 2 };
  if (name.indexOf("ETH") >= 0) return { label: name, base: 3260 + (h % 60), vol: 0.013, decimals: 2 };
  if (name.indexOf("XAU") >= 0) return { label: name, base: 2380 + (h % 20), vol: 0.006, decimals: 2 };
  return { label: name, base: 0.6 + (h % 1800) / 1000, vol: 0.0011, decimals: name.indexOf("JPY") >= 0 ? 3 : 5 };
}

/* ── LIVE SERVER EDITION: دقة السعر الحقيقية لكل عملة ──
   مكتبة الشارت تُنسّق الأسعار عبر priceScale (10^عدد الأرقام العشرية):
   100 = رقمين عشريين فقط — وهذا ما جعل أسعار العملات الرخيصة مثل
   BRLUSD_otc (~0.83) تبدو مسطّحة خاطئة على المحور وفي بطاقة OHLC.
   نستنتج الأرقام من شموع الخادم الحقيقية نفسها (أكثر عدد كسور في
   آخر 60 شمعة) مع احتياطات ذكية حسب نوع العملة. */
function inferDecimalsFromCandles(arr) {
  if (!Array.isArray(arr) || !arr.length) return 0;
  let best = 0;
  const from = Math.max(0, arr.length - 60);
  for (let i = arr.length - 1; i >= from; i--) {
    const c = arr[i]; if (!c) continue;
    const vals = [c.close, c.high, c.low, c.open];
    for (const v of vals) {
      if (typeof v !== "number" || !Number.isFinite(v)) continue;
      const s = String(v);
      const dot = s.indexOf(".");
      if (dot < 0) continue;
      const frac = s.length - dot - 1;
      if (frac > best) best = frac;
    }
    if (best >= 8) break;
  }
  return Math.min(best, 8);
}
function badiDecimals(name, dataArr) {
  const n = Number(inferDecimalsFromCandles(dataArr || []));
  if (n > 0) return n;
  const s = String(name || "");
  if (s.indexOf("BTC") >= 0 || s.indexOf("ETH") >= 0 || s.indexOf("XAU") >= 0) return 2;
  if (s.indexOf("JPY") >= 0) return 3;
  return 5;
}
function badiPriceScale(name, dataArr) { return Math.pow(10, badiDecimals(name, dataArr)); }

/* ───────────── Console ───────────── */
function log(kind, text) {
  msgSeq++;
  msgs.push({ id: msgSeq, at: Date.now(), kind: kind, text: text });
  if (msgs.length > 81) msgs = msgs.slice(-81);
  renderConsole();
}
function renderConsole() {
  const box = $("consoleMsgs");
  box.innerHTML = msgs.length === 0
    ? '<p class="cempty">Run messages, errors and log() output appear here…</p>'
    : msgs.map((m) => '<div class="msg ' + m.kind + '"><span class="t">' + new Date(m.at).toLocaleTimeString("en-GB") + '</span><span class="x">' + esc(m.text) + "</span></div>").join("");
  box.scrollTop = box.scrollHeight;
}

/* ───────────── Render: file tabs ───────────── */
function renderTabs() {
  const box = $("tabsRow");
  const ar = window.__BADI_LANG__ === "ar";
  let h = files.map((f) => {
    const on = f.id === activeId;
    const isBadi = f.kind === "badi";
    const kIcon = isBadi ? "lock" : (f.kind === "indicator" ? "candle" : "pen");
    const kCls = isBadi ? "t-badi" : (f.kind === "indicator" ? "t-ind" : "t-tool");
    const dotTitle = isBadi ? (ar ? "مؤشر مشفر (BADI)" : "Encrypted indicator (BADI)")
                            : (f.enabled ? "Applied to the chart" : "Stopped");
    const t = isBadi ? (ar ? esc(f.fileName) + " — مؤشر مشفر: انقر لفك التشفير وفتحه" : esc(f.fileName) + " — encrypted indicator: click to decrypt and open") : esc(f.fileName);
    return '<div class="tab' + (on ? " on" : "") + (isBadi ? " badi" : "") + '" data-id="' + f.id + '" title="' + t + '">'
      + (isBadi ? "" : '<span class="dot' + (f.enabled ? " on" : "") + '" title="' + dotTitle + '"></span>')
      + '<span class="kind ' + kCls + '">' + icon(kIcon, 11) + "</span>"
      + '<span dir="ltr" class="mono">' + esc(f.fileName) + "</span>"
      + (dirtyIds.has(f.id) ? '<span class="dirty" title="Unsaved">●</span>' : "")
      + '<button class="tab-x" data-x="' + f.id + '" title="Delete file" aria-label="Delete ' + esc(f.fileName) + '">' + icon("x", 11) + "</button>"
      + "</div>";
  }).join("");
  h += '<button class="tab-add" id="tabAdd" title="New file" aria-label="New file">' + icon("plus", 13) + "</button>";
  h += '<button class="tab-add ed-close" data-edclose="1" title="Close editor" aria-label="Close editor">' + icon("x", 13) + "</button>";
  box.innerHTML = h;
}

/* ───────────── Render: run button states ─────────────
   ▶ stopped (sky) / ■ running on the chart (green) / ↻ edited after run */
function renderRunBtn() {
  const f = activeFile();
  if (!f) return;
  const btn = $("runBtn");
  const edited = editedIds.has(f.id);
  if (!f.enabled) {
    btn.className = "abtn";
    btn.innerHTML = icon("play", 13);
    btn.title = "Run and apply to the chart (Ctrl+Enter)";
    btn.setAttribute("aria-label", "Run");
  } else if (edited) {
    btn.className = "rbtn";
    btn.innerHTML = icon("rotate", 13);
    btn.title = "Code changed since the last run — click to re-run with the new code (Ctrl+Enter)";
    btn.setAttribute("aria-label", "Re-run");
  } else {
    btn.className = "rbtn";
    btn.innerHTML = icon("stop", 10);
    btn.title = "Running on the chart now — click to stop";
    btn.setAttribute("aria-label", "Stop");
  }
}

/* ───────────── Render: editor toolbar ───────────── */
function renderEdBar() {
  const f = activeFile();
  $("edBarFull").hidden = !f;
  $("edBarEmpty").hidden = !!f;
  if (!f) return;
  renderRunBtn();
  $("saveBtn").innerHTML = icon("save", 13);
  const kc = $("kindChip");
  kc.className = "kindchip " + (f.kind === "indicator" ? "ind" : "tool");
  kc.innerHTML = icon(f.kind === "indicator" ? "candle" : "pen", 13);
  kc.title = f.kind === "indicator" ? "Indicator" : "Drawing tool";
  $("edFileName").textContent = f.fileName;
}

/* ───────────── Render: code area ───────────── */
function renderCodeArea() {
  const f = activeFile();
  $("codeEmpty").classList.toggle("show", !f);
  $("codeHost").hidden = !f;
  if (!f) return;
  editorSetCode(f.code, f.id);
}

/* ───────────── Render: timeframe, editor toggle ───────────── */
let tfCollapsed = false;
function applyTfCollapse() {
  /* سهم الفريمات (طلب المستخدم): عند الطي تُخفى كل الأزرار ويبقى الفريم المضبوط
     وحده ظاهرًا ليعرف المستخدم أن هذا مكان الفريمات */
  const tg = $("tfGroup");
  if (!tg) return;
  const act = aPane() ? aPane().tf : "";
  tg.querySelectorAll(".tf").forEach((b) => b.classList.toggle("tf-hidden", tfCollapsed && b.dataset.tf !== act));
  const ar = $("tfArrow");
  if (ar) ar.classList.toggle("on", tfCollapsed);
}
function renderTf() {
  document.querySelectorAll(".tf").forEach((b) => b.classList.toggle("on", b.dataset.tf === (aPane() ? aPane().tf : "")));
  applyTfCollapse();
}
function renderEdToggle() {
  $("edToggle").className = "ibtn wide" + (editorOpen ? " on" : "");
  $("edToggle").title = editorOpen ? "Close editor" : "Open editor";
  $("editorPane").hidden = !editorOpen;
  $("resizeHandle").hidden = !editorOpen || window.innerWidth < 1024;
  if (editorOpen) ensureMonaco();
}
function applyEdW() {
  if (window.innerWidth >= 1024) $("editorPane").style.width = editorW + "px";
  else $("editorPane").style.width = "";
}
function renderAll() {
  renderTabs(); renderEdBar(); renderCodeArea(); renderTf(); renderConsole();
}
/* ═══════════ File operations: run / stop / delete / create ═══════════ */

/** Wrap user hooks with error capture (same error shown at most twice) */
function guardDef(f, def) {
  const out = Object.assign({}, def, { id: f.id, label: fileLabel(f.fileName) || def.label });
  const hooks = ["calculate", "render", "getRange", "onStart", "onUpdate", "onDraw", "onHitTest"];
  for (const h of hooks) {
    const fn = def[h];
    if (typeof fn !== "function") continue;
    out[h] = function (...args) {
      try {
        return fn.apply(def, args);
      } catch (e) {
        const n = (errCounts.get(f.id + h) || 0) + 1;
        errCounts.set(f.id + h, n);
        if (n <= 2) log("err", f.fileName + " · " + h + "(): " + (e instanceof Error ? e.message : String(e)));
        else if (n === 3) log("info", "Stopped showing errors for " + f.fileName + " · " + h + "() (issue persists)");
        throw e;
      }
    };
  }
  return out;
}

/** Default line renderer — used when an indicator defines calculate() but no render().
 *  Draws every series as a line: arrays directly, objects key-by-key with a palette.
 *  `this` is the indicator definition (color/type available). */
function defaultLineRender(ctx, v, h, s) {
  if (!v) return;
  const PAL = ["#38bdf8", "#a78bfa", "#34d399", "#f87171", "#facc15", "#f472b6", "#60a5fa"];
  const c0 = (s && s.color) || this.color || "#38bdf8";
  const one = (arr, color) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    let started = false;
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      const val = arr[i];
      if (val == null || (typeof val === "number" && !isFinite(val))) { started = false; continue; }
      const x = h.indexToX(i);
      const y = this.type === "pane" ? h.paneToY(val) : h.priceToY(val);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  };
  if (Array.isArray(v)) { one(v, c0); return; }
  let ci = 0;
  for (const key in v) {
    if (!Object.prototype.hasOwnProperty.call(v, key)) continue;
    if (!Array.isArray(v[key])) continue;
    one(v[key], ci === 0 ? c0 : PAL[ci % PAL.length]);
    ci++;
  }
}

/** Compile the file and apply it to the ACTIVE pane's chart (editor → open chart) */
function applyFile(f, activate) {
  const ch = aChart();
  if (!ch) return false;
  const r = compileScript(f.code, function (...args) {
    log("info", f.fileName + ": " + args.map(String).join(" "));
  });
  if (r.error || !r.def) {
    log("err", f.fileName + ": " + r.error);
    return false;
  }
  /* إذا لم يكتب المستخدم render() نرسم الخطوط تلقائيًا — المؤشر يعمل دائمًا
     (calculate فقط يكفي: ترسم كل سلسلة كخط بلون افتراضي أو لون التعريف) */
  if (typeof r.def.render !== "function" && typeof r.def.calculate === "function")
    r.def.render = defaultLineRender;
  const g = guardDef(f, r.def);
  /* طلب المستخدم: الصورة المصغرة يجب أن تُظهر المؤشر مرسومًا — نعلّم لحظة أول رسم ناجح
     ليُلتقط الالتقاط بعد أن يكون المؤشر على الشارت فعلاً لا قبله */
  if (f.kind === "indicator" && typeof g.render === "function") {
    const drawnRender = g.render;
    g.render = function (ctx, v, h, s) {
      if (v) f.__drawnOnce = true;
      return drawnRender.call(this, ctx, v, h, s);
    };
  }
  if (f.kind === "indicator") {
    ch.addIndicator(g, { onEdit: function () { openFile(f.id); } });
  } else {
    ch.addDrawingTool(g);
    if (activate) ch.setTool(f.id);
  }
  return true;
}

function setEnabled(id, v) {
  const f = files.find((x) => x.id === id);
  if (f) { f.enabled = v; scheduleSave(); renderTabs(); renderRunBtn(); }
}

/** ▶ Run: compile + apply + set state */
function runFile(id, activate) {
  if (activate === undefined) activate = true;
  const f = files.find((x) => x.id === id);
  if (!f) return;
  const ok = applyFile(f, activate);
  if (!ok) return;
  log("ok", f.kind === "indicator"
    ? "▶ Applied indicator " + f.fileName + " to the chart"
    : "▶ Registered tool " + f.fileName + (activate ? " — click the chart to draw" : ""));
  f.enabled = true;
  /* طلب المستخدم: لا تُلتقط أي لقطة عند التشغيل إطلاقًا — الصورة تُلتقط عند الحفظ فقط */
  editedIds.delete(id); /* the new code is now the displayed one */
  scheduleSave(); renderTabs(); renderRunBtn();
}

/* ═══ الصورة المصغرة: تُلتقط عند الحفظ فقط (طلب المستخدم) ═══
   لا أي لقطة قبل الحفظ — لا عند التشغيل ولا عند الحفظ التلقائي أثناء الكتابة.
   إن كان المؤشر يعمل على الشارت ننتظر أول رسم فعلي له (حتى ~10 ثوانٍ) لتصبح
   الصورة نظيفة له وحده، وإن لم يكن يعمل تُلتقط فورًا بعد استقرار الحفظ */
var __thumbSent = {}, __thumbTries = {};
function scheduleThumbCapture(fileName, kind, f) {
  try {
    if (!window.__BADI_EMBEDDED) return;
    if (!fileName || kind === "tool") return;   /* الأدوات لا تحتاج صورة */
    const key = String(fileName).toLowerCase();
    if (__thumbSent[key]) return;
    __thumbSent[key] = true;
    const started = Date.now();
    const poll = setInterval(function () {
      try {
        /* يعمل على الشارت: انتظار أول رسم فعلي — لا يعمل: لقطة فورية بلا انتظار */
        if (f && f.enabled && !(f.__drawnOnce) && Date.now() - started < 10000) return;
        clearInterval(poll);
        /* مهلة صغيرة حتى يكتمل الإطار على الشارت */
        setTimeout(function () { badiSend("badi-thumb", String(fileName)); }, 400);
      } catch (e) { try { clearInterval(poll); } catch (e2) {} }
    }, 250);
  } catch (e) {}
}

/** ⏻ Run/stop toggle */
function toggleFile(id) {
  const f = files.find((x) => x.id === id);
  const ch = aChart();
  if (!f || !ch) return;
  if (!f.enabled) {
    const ok = applyFile(f, f.kind === "tool");
    if (!ok) return;
    log("ok", "⏻ Started " + f.fileName);
    setEnabled(id, true);
  } else {
    if (f.kind === "indicator") {
      ch.removeIndicator(f.id);
    } else {
      ch._instanceTools = (ch._instanceTools || []).filter((t) => t.id !== f.id);
      if (ch._customTools) delete ch._customTools[f.id];
      if (ch.activeTool === f.id) ch.setTool("cursor");
    }
    log("info", "⏻ Stopped " + f.fileName);
    setEnabled(id, false);
  }
}

function deleteFile(id) {
  const f = files.find((x) => x.id === id);
  if (!f) return;
  if (!window.confirm("Permanently delete file " + f.fileName + "?")) return;
  const ch = aChart();
  if (ch && f.enabled) {
    if (f.kind === "indicator") ch.removeIndicator(f.id);
    else {
      ch._instanceTools = (ch._instanceTools || []).filter((t) => t.id !== f.id);
      if (ch._customTools) delete ch._customTools[f.id];
      if (ch.activeTool === f.id) ch.setTool("cursor");
    }
  }
  files = files.filter((x) => x.id !== id);
  if (activeId === id) activeId = files.length ? files[0].id : null;
  dirtyIds.delete(id); editedIds.delete(id);
  curCodeId = null;
  scheduleSave(); renderTabs(); renderEdBar(); renderCodeArea();
  log("info", "🗑 Deleted file " + f.fileName);
}

/** Create file with the name the user typed — indicator waits for ▶, tool activates immediately */
function createFile(kind, name) {
  const f = makeFile(kind, name);
  let enabled = false;
  const ch = aChart();
  if (ch && kind === "tool") {
    const r = compileScript(f.code);
    if (r.def && !r.error) {
      const g = guardDef(f, r.def);
      ch.addDrawingTool(g);
      ch.setTool(f.id);
      enabled = true;
    }
  }
  f.enabled = enabled;
  files.push(f);
  closeNewModal();
  scheduleSave();
  openFile(f.id);   /* يفتح المحرر على الملف الجديد فورًا بعد إنهاء الخطوات */
  if (kind === "tool") {
    log("ok", enabled
      ? "✦ Tool " + f.fileName + " created and activated — click the chart to draw"
      : "✦ Tool " + f.fileName + " created — press ▶ Run after editing");
  } else {
    log("info", "✦ " + f.fileName + " created — edit the code then press ▶ Run to apply it");
  }
}

function openFile(id) {
  const f = files.find((x) => x.id === id);   /* findFile هنا غير متاحة — BRIDGE_POST داخل IIFE */
  if (f && f.kind === "badi") { requestBadiOpen(f); return; }   /* .badi: فك التشفير بدل فتحه في المحرر */
  activeId = id;
  const wasOpen = editorOpen;
  editorOpen = true;
  curCodeId = null;
  renderTabs(); renderEdBar(); renderCodeArea();
  if (!wasOpen) { renderEdToggle(); applyEdW(); window.dispatchEvent(new Event("resize")); }
  if (monacoReady && ed) ed.focus();
}

/* ═════ BADI: فتح مؤشر مشفر من قائمة BadiCharts — يُفك داخل التطبيق بمفتاحه ═════ */
function requestBadiOpen(f) {
  if (!window.__BADI_EMBEDDED) { log("err", "BADI works inside the desktop app only"); return; }
  const base = String(f.fileName || "").replace(/\.badi$/i, "");
  const twin = files.find((x) => x.kind !== "badi" && String(x.fileName || "").toLowerCase() === (base + ".js").toLowerCase());
  if (twin) { openFile(twin.id); return; }   /* يوجد ملف أصلي بنفس الاسم — افتح المصدر مباشرة */
  badiSend("badi-open", f.fileName);
}

/* ═══════════ Save ═══════════ */
function scheduleSave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(function () { saveFiles(files); }, 700);
}
function saveNow() {
  saveFiles(files);
  dirtyIds.clear();
  renderTabs();
  /* لقطة المؤشر عند الحفظ الصريح (طلب المستخدم): حفظ = لقطة، عدم الحفظ = لا لقطة */
  try {
    const sf = activeFile();
    if (sf && sf.kind !== "tool" && sf.fileName) {
      delete __thumbSent[String(sf.fileName).toLowerCase()];
      scheduleThumbCapture(sf.fileName, sf.kind, sf);
    }
  } catch (e) {}
  log("ok", "💾 All files saved in your browser");
}

/* ═══════════ Code editing ═══════════ */
function onChangeCode(v) {
  const f = activeFile();
  if (!f) return;
  f.code = v;
  dirtyIds.add(f.id);
  editedIds.add(f.id);
  scheduleSave();
  renderTabs(); renderRunBtn();
}

/* ───────────── Monaco editor (plain-text fallback) ───────────── */
let ed = null, monacoReady = false, fbTa = null, curCodeId = null, suppressModel = false, monacoTimer = 0, monacoLoading = false;
const MONACO_VS = "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs";
const MONACO_LOADER = MONACO_VS + "/loader.js";

/* Monaco loads lazily — only when the editor is opened for the first time */
function monacoWait(on) {
  const host = $("codeHost");
  if (!host) return;
  if (host.style.position !== "relative") host.style.position = "relative";
  let d = document.getElementById("monacoWait");
  if (on && !d) {
    d = document.createElement("div");
    d.id = "monacoWait";
    d.style.cssText = "position:absolute;inset:0;display:grid;place-items:center;align-content:center;gap:10px;color:var(--accent-t);font-size:12px;z-index:5;pointer-events:none";
    d.innerHTML = '<div class="spin"></div><div>Loading editor&hellip;</div>';
    host.appendChild(d);
  } else if (!on && d) d.remove();
}
function ensureMonaco() {
  if (monacoReady || fbTa || monacoLoading || !editorOpen) return;
  monacoLoading = true;
  monacoWait(true);
  const s = document.createElement("script");
  s.src = MONACO_LOADER;
  s.onload = function () { initMonaco(); };
  s.onerror = function () { monacoLoading = false; monacoWait(false); fallbackTextarea(); };
  document.head.appendChild(s);
}

function initMonaco() {
  if (typeof window.require === "function") {
    try {
      window.require.config({ paths: { vs: MONACO_VS } });
    } catch (e) { fallbackTextarea(); return; }
    monacoTimer = setTimeout(fallbackTextarea, 8000);
    window.require(["vs/editor/editor.main"], function () {
      clearTimeout(monacoTimer);
      bootMonaco();
    }, function () {
      clearTimeout(monacoTimer);
      fallbackTextarea();
    });
  } else {
    fallbackTextarea();
  }
}
function bootMonaco() {
  monacoWait(false);
  if (monacoReady) return;
  if (typeof monaco === "undefined") { fallbackTextarea(); return; }
  try { if (window.__badiDefineMonThemes) window.__badiDefineMonThemes(); } catch (e) {}
  monaco.editor.defineTheme("badi-dark", {
    base: "vs-dark", inherit: true,
    rules: [
      { token: "comment", foreground: "6a737d", fontStyle: "italic" },
      { token: "keyword", foreground: "7dd3fc" },
      { token: "number", foreground: "79c0ff" },
      { token: "string", foreground: "a5d6a7" },
      { token: "type.identifier", foreground: "d2a8ff" },
      { token: "delimiter", foreground: "cfd2da" }
    ],
    colors: {
      "editor.background": "#0d1117",
      "editor.foreground": "#e6edf3",
      "editorLineNumber.foreground": "#3d4451",
      "editorLineNumber.activeForeground": "#38bdf8",
      "editor.selectionBackground": "#264f78aa",
      "editor.lineHighlightBackground": "#161b22",
      "editorCursor.foreground": "#38bdf8",
      "editorIndentGuide.background1": "#1c2030",
      "editorGutter.background": "#0d1117"
    }
  });
  ed = monaco.editor.create($("codeHost"), {
    value: "",
    language: "javascript",
    theme: window.__BADI_MONACO_THEME__ || "badi-dark",
    fontSize: 13,
    lineHeight: 20,
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    wordWrap: "on",
    renderLineHighlight: "all",
    smoothScrolling: true,
    cursorBlinking: "smooth",
    padding: { top: 10, bottom: 10 },
    scrollbar: { verticalScrollbarSize: 9, horizontalScrollbarSize: 9 },
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    overviewRulerBorder: false,
    bracketPairColorization: { enabled: true }
  });
  ed.onDidChangeModelContent(function () {
    if (!suppressModel) onChangeCode(ed.getValue());
  });
  monacoReady = true;
  curCodeId = null;
  const f = activeFile();
  if (f) editorSetCode(f.code, f.id);
}
function fallbackTextarea() {
  monacoWait(false);
  if (monacoReady || fbTa) return;
  fbTa = document.createElement("textarea");
  fbTa.className = "code-ta";
  fbTa.dir = "ltr";
  fbTa.spellcheck = false;
  fbTa.addEventListener("input", function () { onChangeCode(fbTa.value); });
  fbTa.addEventListener("keydown", function (e) {
    if (e.key === "Tab") {
      e.preventDefault();
      fbTa.setRangeText("  ", fbTa.selectionStart, fbTa.selectionEnd, "end");
      onChangeCode(fbTa.value);
    }
  });
  $("codeHost").appendChild(fbTa);
  curCodeId = null;
  const f = activeFile();
  if (f) editorSetCode(f.code, f.id);
}
function editorSetCode(code, id) {
  if (curCodeId === id) return;
  curCodeId = id;
  if (monacoReady && ed) {
    suppressModel = true;
    ed.setValue(code);
    suppressModel = false;
    ed.setScrollTop(0);
  } else if (fbTa) {
    fbTa.value = code;
  }
}

/* ═══════════ Multi-chart engine: كل لوحة شارت مستقلة تمامًا ═══════════ */
/** Wire one BadiCharts instance: perf throttle, settings card, delete-sync, shortcuts */
function setupChart(ch, p) {
  try {
    if (window.__BADI_EMBEDDED) {
      ch._renderThrottleMs = 33;
      let idleT = 0;
      const wake = function () {
        ch._renderThrottleMs = 33;
        clearTimeout(idleT);
        idleT = setTimeout(function () { ch._renderThrottleMs = 150; }, 600);
      };
      ["mousedown", "mousemove", "wheel", "touchstart", "touchmove", "keydown"].forEach(function (ev) {
        window.addEventListener(ev, wake, { passive: true });
      });
      const origUpdate = ch.update.bind(ch);
      ch.update = function (c) { wake(); return origUpdate(c); };
      wake();
      /* LIVE SERVER EDITION: عند التمرير إلى بداية الشارت يُطلب من خادم QX
         دفعة أقدم صغيرة (300 شمعة) تُدمج في الشارت دون أي تأثير على العرض —
         كلما زاد التمرير للخلف ظهرت شموع أخرى مثل المنصات الاحترافية */
      try {
        const origConstrain = ch.constrainRightOffset.bind(ch);
        ch.constrainRightOffset = function () {
          origConstrain();
          if (typeof window.__badiMaybeLoadOlder === "function") window.__badiMaybeLoadOlder(p);
        };
      } catch (e) {}
    }
  } catch (e) {}

  /* Settings card ⚙ supports any key in settings (not only the built-in ones) */
  ch._openSettingsCard = function (id, state) {
    const st = state || {};
    const s = st.settings || {};
    const fields = [];
    for (const key of Object.keys(s)) {
      const v = s[key];
      if (typeof v === "number") fields.push({ key: key, label: key, type: "number", value: v });
      else if (typeof v === "string" && v.indexOf("#") === 0) fields.push({ key: key, label: key, type: "color", value: v });
      else fields.push({ key: key, label: key, type: "text", value: String(v) });
    }
    this.settingsCard = {
      id: id,
      x: this.chartLeft + 60,
      y: this.chartTop + 60,
      w: 240,
      h: 36 + fields.length * 30 + 40,
      fields: fields,
      title: (st.def && st.def.label) || id,
      draft: Object.assign({}, s)
    };
  };

  /* Delete sync: removing the indicator from the legend card updates the file state */
  const proto = Object.getPrototypeOf(ch);
  const origRemove = proto.removeIndicator.bind(ch);
  ch.removeIndicator = function (id) {
    const r = origRemove(id);
    onRemoved(id);
    return r;
  };

  /* Do not leak chart shortcuts (R / + / - / Delete) while typing in the editor */
  ch.onKeyDown = function (e) {
    const t = e.target;
    const typing = !!t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
    if (!typing && !e.ctrlKey && !e.metaKey && !e.altKey) proto.onKeyDown.call(this, e);
    else if (e.key === "Escape") { this.activeTool = "cursor"; this.currentDrawing = null; }
  };

  ch.onToolChange(function (tid) {
    tool = tid;
  });
}

function paneHeadHTML(p) {
  const it = BOARD.filter((x) => x.name === p.asset)[0] || {};
  return (it.flag ? '<img class="aflag" src="' + it.flag + '" alt="">' : "")
    + "<b>" + esc(p.asset) + "</b>"
    + '<span class="pane-tf">' + esc(p.tf) + "</span>"
    + (it.payout ? '<span class="pane-pay">' + Number(it.payout) + "%</span>" : "");
}
function renderPaneHead(i) { const p = panes[i]; if (p && p.head) p.head.innerHTML = paneHeadHTML(p); }
function renderPaneActive() { panes.forEach((p, i) => p.el.classList.toggle("on", i === activePane)); }

function addPane() {
  const i = panes.length;
  const used = panes.map((p) => p.asset);
  const pool = addedNames().filter((n) => used.indexOf(n) < 0);
  const name = pool.length ? pool[i % pool.length] : (addedNames()[0] || (BOARD[0] && BOARD[0].name) || "BTC/USDT");
  const el = document.createElement("div");
  el.className = "pane";
  el.dataset.pane = i;
  el.title = "Open this chart — click to select it";
  /* شريط اسم العملة فوق الشارت أُزيل نهائيًا — المعلومة نفسها موجودة في سطر OHLC تحته (طلب المستخدم) */
  el.innerHTML = '<div class="pane-cv"><canvas></canvas></div>';
  $("gridHost").appendChild(el);
  const cv = el.querySelector("canvas");
  const cfg = assetCfg(name);
  const bootDec = Number(((window.__BADI_BOOT_FILES || {}).market || {}).dec);
  const dec0 = (Number.isFinite(bootDec) && bootDec > 0 && bootDec <= 8)
    ? bootDec : badiDecimals(name, null);
  const chart = new window.BadiCharts(cv, {
    symbol: { label: cfg.label, priceScale: Math.pow(10, dec0), decimals: dec0 },
    timeframe: { label: "1m", ms: tfMs("1m") },
    theme: window.__BADI_CHART_THEME__ || { drawing: "#38bdf8", drawingActive: "#7dd3fc" },
    /* العدّ التنازلي الأصلي للمكتبة بجانب الشمعة الحية (طلب المستخدم): رقمان فقط
       بلا إطار أو خلفية، بإزاحة ثابتة (14px) عن حافة الشمعة مهما كان الزوم */
    countdown: { enabled: !!(window.__BADI_UI__ && window.__BADI_UI__.cd), format: "ss", fontSize: 13, offsetX: 14, offsetY: 0, color: "#22E08A" }
  });
  const p = { el: el, head: el.querySelector(".pane-head"), cv: cv, chart: chart, asset: name, tf: "1m", dataArr: [], tick: 0 };
  setupChart(chart, p);
  chart.start();
  /* LIVE SERVER EDITION (طلب المستخدم): الشموع الوهمية انزعت من التطبيق —
     الشارت يبدأ فارغاً وينتظر بيانات خادم Quotex الحقيقية
     (BRLUSD_otc: 300 شمعة فوراً بعد الدخول، ثم بقية العملات واحدة تلو الأخرى) */
  if (!window.__BADI_EMBEDDED) {
    p.dataArr = generateCandles(cfg, p.tf, 620);
    chart.setData(p.dataArr);
  }
  renderPaneHead(i);
  panes.push(p);
  return p;
}

/** Select a pane — it gets the light border and becomes the editor's target */
function setPaneActive(i) {
  if (!panes[i]) return;
  activePane = i;
  renderPaneActive();
  const ch = aChart();
  if (ch) {
    try { ch.setTool(tool); } catch (e) {}
  }
  window.__BADI_CHART = ch;
  renderTf();
  const p = panes[i];
  if (window.__BADI_EMBEDDED && p.asset !== CUR_ASSET) pickAsset(p.asset);
}

/** Give a pane another asset + timeframe (the engine-fed pane waits for Python data) */
function setPaneAsset(i, name, tfKey) {
  const p = panes[i];
  if (!p) return;
  p.asset = name;
  if (tfKey) p.tf = tfKey;
  const cfg = assetCfg(name);
  try {
    /* دقة السعر باسم العملة (احتياط) — وتُصحّح تلقائياً من أرقام الخادم
       الحقيقية فور وصول الشموع عبر setMarket (m.dec من بايثون) */
    const decN = badiDecimals(name, null);
    p.chart.setSymbol({ label: cfg.label, priceScale: Math.pow(10, decN), decimals: decN });
    p.chart.setTimeframe({ label: p.tf, ms: tfMs(p.tf) });
  } catch (e) {}
  if (!window.__BADI_EMBEDDED) {
    p.dataArr = generateCandles(cfg, p.tf, 620);
    try { p.chart.setData(p.dataArr); } catch (e) {}
    p.tick = 0;
  }
  renderPaneHead(i);
  renderTf();
}

function initPanes() {
  const startName = CUR_ASSET || (addedNames()[0] || (BOARD[0] && BOARD[0].name) || "BTC/USDT");
  /* شارت واحد فقط — تقسيم الشارت أُزيل بالكامل بطلب المستخدم */
  while (panes.length < 1) addPane();
  while (panes.length > 1) {
    const p = panes.pop();
    try { if (p.chart && p.chart.rafId) cancelAnimationFrame(p.chart.rafId); } catch (e) {}
    p.el.remove();
  }
  $("gridHost").dataset.n = "1";
  setPaneAsset(0, startName);
  primaryPane = 0;
  activePane = 0;
  renderPaneActive();
  libReady = true;
  $("libLoading").hidden = true;
  window.__BADI_CHART = aChart();
  /* Restore only files the user enabled themselves previously */
  for (const f of files) { if (f.enabled) applyFile(f, false); }
}
let libReady = false;

/* ── Hooks used by the desktop bridge (BRIDGE_POST) ── */
window.__badiPaneState = function () { return { active: activePane, primary: primaryPane, n: panes.length }; };
/* يعيد لوحة المحرك نفسها (وليس نسخة) — حتى يُكتب dataArr في اللوحة فعلاً عند setCandles */
window.__badiPrimary = function () {
  return panes[primaryPane] || panes[0] || null;
};
window.__badiPCH = pChart;
window.__badiShotCanvas = function () { const p = aPane() || panes[0]; return p ? p.cv : null; };
/* setMarket من محرك بايثون: يميّز اللوحة المغذاية من المحرك ويحدّث اسمها وفريمها والشرائح */
window.__badiSetMarket = function (m) {
  try {
    CUR_ASSET = String(m.label || CUR_ASSET);
    let i = paneIdxByAsset(CUR_ASSET);
    if (i < 0) i = 0;
    primaryPane = i;
    const p = panes[i];
    if (p) {
      p.tf = String(m.tf || p.tf);
      try {
        /* دقة السعر الحقيقية من أرقام خادم Quotex (backend.dec) —
           priceScale = 10^decimals حتى تظهر الأسعار الرخيصة (BRLUSD_otc…)
           بكل أرقامها على المحور وبطاقة OHLC لا مثل 0.83 المسطّحة */
        let dec = Number(m.dec);
        if (!(dec > 0 && dec <= 8)) dec = badiDecimals(CUR_ASSET, p.dataArr);
        p.chart.setSymbol({ label: CUR_ASSET, priceScale: Math.pow(10, dec), decimals: dec });
        p.chart.setTimeframe({ label: p.tf, ms: Number(m.tfMs || tfMs(p.tf)) });
      } catch (e) {}
      renderPaneHead(i);
      document.querySelectorAll(".tf").forEach((b) => b.classList.toggle("on", b.dataset.tf === p.tf));
    }
    renderPaneActive();
    renderAssets();
  } catch (e) {}
};
/* حُذف قسم التداول والرصيد (طلب المستخدم) — لم يبقَ إلا سجل الإشارات */

function onRemoved(id) {
  const f = files.find((x) => x.id === id && x.kind === "indicator");
  if (f) { f.enabled = false; scheduleSave(); renderTabs(); renderRunBtn(); }
}

/** Local simulation feed for the non-engine panes + countdowns refresh */
function liveTick() {
  if (live) {
    const nowSec = Math.floor(Date.now() / 1000);
    for (let i = 0; i < panes.length; i++) {
      if (window.__BADI_EMBEDDED && i === primaryPane) continue;   // Python drives that pane
      const p = panes[i];
      const cfg = assetCfg(p.asset);
      p.tick++;
      const last = p.dataArr[p.dataArr.length - 1];
      if (!last) continue;
      /* شمعة جديدة فقط عند مرور حد الفريم بالتوقيت الحقيقي — كانت تُنشأ بعدد
         تكات من الإقلاع فتنحرف أوقات الشموع عن حدود الدقيقة ويعلق العدّ على 00 */
      const tf = Math.max(5, Math.floor(tfMs(p.tf) / 1000));
      const lastT = Math.floor(last.time > 1e11 ? last.time / 1000 : last.time);
      const boundary = nowSec - (nowSec % tf);
      if (lastT < boundary) {
        /* املأ الفجوة لو تأخرت التكة (نوم/تعليق) — بحد أقصى 500 شمعة */
        const gap = Math.min(Math.floor((boundary - lastT) / tf), 500);
        for (let k = 0; k < gap; k++) {
          const nc = newCandleFrom(p.dataArr[p.dataArr.length - 1], tfMs(p.tf), cfg.vol);
          p.dataArr.push(nc);
          p.chart.update(nc);
        }
      } else {
        const sc = stepCandle(last, cfg.vol);
        p.dataArr[p.dataArr.length - 1] = sc;
        p.chart.update(sc);
      }
      syncCdColor(p);
    }
  }
  sigLocalResolve();
  sigExpireSweep();
}

/* ═══ انتهاء بطاقة الإشارة مع انتهاء شمعة الفريم (طلب المستخدم) ═══
   البطاقة الجارية تختفي من قائمة الإشارات بمجرد انقضاء مدتها —
   والنتيجة (WIN/LOSS) تُسجَّل في تبويب السجل عند وصولها من المحرك. */
function sigExpireSweep() {
  let changed = false;
  const now = Date.now();
  for (const g of SIGS) {
    if (!g.result && !g.expired && g.durSec > 0 && now - g.at >= g.durSec * 1000) { g.expired = true; changed = true; }
  }
  if (changed) renderSignals();
}

/* ═══ المؤقت التنازلي بجانب الشمعة الحية (طلب المستخدم) ═══
   نستخدم ميزة countdown الأصلية في المكتبة (v2.13.0): تُرسم داخل الشارت بإحداثياته
   نفسه — رقمان فقط بلا إطار أو خلفية، بإزاحة ثابتة (14px) عن حافة الشمعة الحية
   مهما كان الزوم. نعيد تعريف drawCountdown على نموذج المكتبة نفسه بثلاثة إصلاحات:
   1) المكتبة تمرّر طابع requestAnimationFrame (performance.now) إلى drawCountdown
      بينما أوقات الشموع بالثواني الحقيقية — فكان العدّ ينقطع ويعود في ثوانٍ خاطئة.
      نحسب الوقت من Date.now() فيبقى العدّ محاذيًا لحدود الشمعة بالتوقيت الحقيقي.
   2) المكتبة تخفي الرقم كليًا إذا لم يكن هناك مكان بين الشمعة ومحور السعر (زوم
      مع الشمعة ملاصقة للمحور) — فكان يبدو وكأنه توقف. البديل: نرسمه فوق الشمعة
      نفسها (وسطًا أعلى ذيلها) بمسافة واضحة — لا تصادم مع أي شمعة ولا مع المحور.
   3) لون الرقم = لون اتجاه الشمعة الحية (أخضر/أحمر) — يتحدث مع كل تكة (syncCdColor). */
(function () {
  try {
    if (window.BadiCharts && BadiCharts.prototype) {
      BadiCharts.prototype.drawCountdown = function () {
        try {
          const cd = this._countdown;
          if (!cd || !cd.enabled) return;
          const candles = this.sim.candles, N = candles.length;
          if (N === 0) return;
          const last = candles[N - 1];
          if (!last || !last.time) return;
          const tfMs = this.timeframe.ms || 6e4;
          const closeSec = last.time + Math.round(tfMs / 1e3);
          /* وقت الحائط الحقيقي لا طابع الرسم — محاذاة كاملة لحدود الفريم */
          const nowSec = Math.floor(Date.now() / 1000);
          let rem = closeSec - nowSec;
          if (rem < 0) rem = 0;
          const value = Math.min(99, Math.max(0, rem % 60));   /* رقمان فقط دائمًا */
          const text = (value < 10 ? "0" : "") + value;
          const y = this.priceToY(last.close) + (cd.offsetY || 0);
          if (!isFinite(y) || y < this.priceTop - 6 || y > this.priceBottom + 6) return;
          const ctx = this.ctx;
          ctx.save();
          ctx.font = (cd.fontSize || 11) + "px -apple-system, Segoe UI, Roboto, sans-serif";
          ctx.fillStyle = cd.color || this.theme.textDim;
          ctx.textAlign = "left";
          ctx.textBaseline = "middle";
          const tw = ctx.measureText(text).width;
          const off = (cd.offsetX != null) ? cd.offsetX : 6;
          const slotEdge = this.indexToX(N - 1) + this.barSpacing / 2;
          /* إزاحة مرنة: تبقى الرقم بجانب الشمعة في العرض الافتراضي (المساحة حتى
             محور السعر ضيقة عند الزوم الصغير) — وتنتقل فوق الشمعة فقط عند الانحشار */
          const avail = (this.chartRight - 4) - slotEdge;
          let x = slotEdge + off;
          if (!isFinite(x)) { ctx.restore(); return; }
          if (x + tw > this.chartRight - 4) {
            if (avail >= tw + 8) {
              /* يكفي المكان لإزاحة أصغر — اضغطها بدل ترك الشمعة */
              x = slotEdge + Math.max(6, avail - tw - 2);
            }
            if (x + tw > this.chartRight - 4) {
              /* لا مكان إطلاقًا يمين الشمعة → فوق الشمعة وسطًا أعلى ذيلها */
              const yTop = this.priceToY(last.high) - (cd.fontSize || 11);
              if (isFinite(yTop) && yTop - (cd.fontSize || 11) / 2 > this.priceTop + 2) {
                ctx.textAlign = "center";
                ctx.fillText(text, Math.round(this.indexToX(N - 1)), Math.round(yTop));
              }
              ctx.restore();
              return;
            }
          }
          if (x < this.chartLeft + 4) { ctx.restore(); return; }
          ctx.fillText(text, Math.floor(x), Math.floor(y));
          ctx.restore();
        } catch (e) {}
      };
    }
  } catch (e) {}
})();
/* مزامنة لون العدّ التنازلي مع اتجاه الشمعة الأخيرة (يتحدث مع كل تكة/تغيير ثيم) */
function syncCdColor(p) {
  try {
    const ch = p.chart;
    if (!ch || !ch._countdown || typeof ch.setCountdown !== "function") return;
    const arr = (ch.sim && ch.sim.candles && ch.sim.candles.length) ? ch.sim.candles : (p.dataArr || []);
    const last = arr[arr.length - 1];
    if (!last) return;
    const th = window.__BADI_CHART_THEME__ || {};
    const col = last.close >= last.open ? (th.bull || "#22E08A") : (th.bear || "#FF4D5E");
    if (ch._countdown.color !== col) ch.setCountdown({ color: col });
  } catch (e) {}
}

function showLibError(msg) {
  const box = $("libLoading");
  box.hidden = false;
  box.innerHTML = '<div class="liberr"><p>' + esc(msg) + '</p><button class="abtn retry" onclick="location.reload()">Retry</button></div>';
}

/* ═══════════ Init & events ═══════════ */
function buildStatic() {
  $("tfGroup").innerHTML = TF_KEYS.map((k) => '<button class="tf" data-tf="' + k + '">' + k + "</button>").join("");
  /* سهم إخفاء/إظهار قائمة الفريمات (طلب المستخدم) — الحالة تُحفظ بين الجلسات */
  const tfAr = $("tfArrow");
  if (tfAr) {
    tfAr.innerHTML = icon("chevron-up", 12);
    tfAr.title = window.__BADI_LANG__ === "ar" ? "إخفاء/إظهار قائمة الفريمات" : "Hide/show the timeframes";
    tfAr.addEventListener("click", function () {
      tfCollapsed = !tfCollapsed;
      try { localStorage.setItem("badiTfCollapsed", tfCollapsed ? "1" : "0"); } catch (e) {}
      applyTfCollapse();
    });
  }
  try { tfCollapsed = localStorage.getItem("badiTfCollapsed") === "1"; } catch (e) { tfCollapsed = false; }
  applyTfCollapse();
  $("edNewBtn").innerHTML = icon("plus", 16);
  $("edCloseBtn").innerHTML = icon("x", 14);
  $("indBtn").innerHTML = icon("arrowsUpDown", 15) + '<span class="btxt">Indicators</span>';
  $("edToggle").innerHTML = icon("code", 15) + '<span class="btxt">Editor</span>';
  /* زر فتح مجلد التطبيق — بجوار زر المحرر (طلب المستخدم) */
  const dbIco = $("dirBtn");
  if (dbIco) dbIco.innerHTML = icon("folder", 15) + '<span class="btxt">Folder</span>';
  /* أيقونات BADI: تشفير المؤشر (قفل) + استيراد مؤشر مشفر (تنزيل) */
  const beIco = $("badiEnc"), biIco = $("badiImp"), bieIco = $("badiImpEmpty");
  if (beIco) beIco.innerHTML = icon("lock", 13);
  if (biIco) biIco.innerHTML = icon("dl", 13);
  if (bieIco) bieIco.innerHTML = icon("dl", 13);
  $("shotBtn").innerHTML = icon("camera", 15);
  $("webTg").innerHTML = icon("send", 14) + '<span class="btxt">Bot Telegram</span>';
  $("webLogout").innerHTML = icon("logout", 15);
  /* أزرار الإخفاء داخل رأس البطاقة + زر الإظهار في شريط أدوات الشارت */
  $("sigHide").innerHTML = icon("chevron-left", 14);
  /* الجرس + شارة العدد — الشارة تُعاد مع الأيقونة لأن innerHTML يمسح الأبناء (طلب المستخدم) */
  $("sigShow").innerHTML = icon("bell", 14) + '<i id="sigBadge" hidden></i>';
  updateSigBadge();
  $("assetAdd").innerHTML = icon("plus", 13);
  $("assetPrev").innerHTML = icon("chevron-left", 13);
  $("assetNext").innerHTML = icon("chevron-right", 13);
  $("amSearchIco").innerHTML = icon("search", 14);
  $("fitBtn").innerHTML = icon("maximize", 14);
  $("sigSound").innerHTML = icon(soundOn ? "volume" : "volumex", 14);
  $("sigClear").innerHTML = icon("trash", 12);
  $("cClear").innerHTML = icon("x", 12);
  $("cHide").innerHTML = icon("chevron-down", 12);
  $("delBtn").innerHTML = icon("trash", 13);
  $("saveBtn").innerHTML = icon("save", 13);
  $("emptyNew").innerHTML = icon("file-plus", 22) + "<span>Create a new file (indicator or drawing tool)</span>";
  $("wzClose").innerHTML = icon("x", 14);
  $("optIndicator").innerHTML = '<span class="oicon">' + icon("candle", 30) + '</span><b>Indicator</b><small id="optIndSub">Calculations drawn over the candles or in a bottom pane — waits for ▶ Run</small>';
  $("optTool").innerHTML = '<span class="oicon">' + icon("pen", 30) + '</span><b>Drawing Tool</b><small>Interactive drag-on-chart tool — activated immediately on creation</small>';
}

function loadState() {
  let f = loadFiles();
  if (!f) f = seedExamples();
  files = f;
  activeId = f.length ? f[0].id : null;
}

let wzStep = 1, wzKind = null, wzLang = "js";
const WZ_TITLES = { 1: "Create New File", 2: "Choose Language", 3: "Name It" };
function setNfLang(l) {
  wzLang = l;
  $("nfLangJs").classList.toggle("on", l === "js");
  $("nfLangPy").classList.toggle("on", l === "py");
}
function wzShow(step) {
  wzStep = step;
  $("wzPane1").hidden = step !== 1;
  $("wzPane2").hidden = step !== 2;
  $("wzPane3").hidden = step !== 3;
  $("wzTitle").textContent = WZ_TITLES[step];
  $("wzBar").style.width = (step * 33.3) + "%";
  const dots = $("wzDots").children;
  for (let i = 0; i < dots.length; i++) dots[i].className = i < step ? "on" : "";
  $("wzBack").hidden = step === 1;
  const nx = $("wzNext");
  nx.textContent = step === 3 ? "Create" : "Continue";
  nx.disabled = step === 1 && !wzKind;
  if (step === 2) {
    const toolNoPy = wzKind === "tool";
    $("nfLangPy").disabled = toolNoPy || !window.__BADI_EMBEDDED;
    $("wzLangNote").hidden = !toolNoPy;
    if (toolNoPy) setNfLang("js");       /* tools are JavaScript-only */
  }
  if (step === 3) {
    $("wzKindLabel").textContent = wzKind === "tool" ? "drawing tool" : "indicator";
    $("nfName").placeholder = wzLang === "py" ? "Python Indicator" : (wzKind === "tool" ? "My Tool" : "My Indicator");
    try { $("nfName").focus(); $("nfName").select(); } catch (e) {}
  }
}
function wzNext() {
  if (wzStep === 1) { if (wzKind) wzShow(2); return; }
  if (wzStep === 2) { wzShow(3); return; }
  createFile(wzKind === "tool" ? "tool" : (wzLang === "py" ? "py" : "indicator"), $("nfName").value);
}
function openNewModal() {
  wzKind = null;
  setNfLang("js");
  badiSend("rescan", "1");   /* فحص مجلد BadiCharts قبل إنشاء ملف جديد */
  $("optIndicator").classList.remove("on");
  $("optTool").classList.remove("on");
  $("nfName").value = "";
  $("newModal").hidden = false;
  wzShow(1);
}
function closeNewModal() { $("newModal").hidden = true; }
function closeEditor() {
  editorOpen = false;
  renderEdToggle(); applyEdW();
  window.dispatchEvent(new Event("resize"));
}

/* ═════ Currency strip: chips = flag + name + payout + market dot + a SMALL × ON the card
   to remove that currency from the strip (the × back on the card itself — user request) ═════ */
var BOARD = [];
var ADDED = null;          /* embedded mode: the desktop app is the source of truth */
const ASSETS_KEY = "badiAssetsV1";
function buildBoard() {
  const mk = (window.__BADI_BOOT_FILES || {}).market;
  if (mk && Array.isArray(mk.board) && mk.board.length) return mk.board;
  return SYMBOL_KEYS.map((k) => ({ name: SYMBOLS[k].label, payout: 87, flag: "", key: k }));
}
function boardNames() { return BOARD.map((x) => x.name); }
function addedNames() {
  const valid = (list) => boardNames().filter((n) => list.indexOf(n) >= 0);
  if (window.__BADI_EMBEDDED) {
    if (ADDED === null) {
      const mk = (window.__BADI_BOOT_FILES || {}).market;
      let def = (mk && Array.isArray(mk.added) && mk.added.length) ? valid(mk.added) : [];
      if (!def.length) {
        def = valid(["EUR/USD", "BTC/USD"]);
        if (!def.length) def = boardNames().slice(0, 2);
      }
      ADDED = def;
    }
    return ADDED.slice();
  }
  try {
    const r = JSON.parse(localStorage.getItem(ASSETS_KEY) || "null");
    if (Array.isArray(r)) return valid(r.filter((n) => typeof n === "string"));
  } catch (e) { /* corrupted storage */ }
  let def = valid(["EUR/USD", "BTC/USD"]);
  if (!def.length) def = boardNames().slice(0, 2);
  try { localStorage.setItem(ASSETS_KEY, JSON.stringify(def)); } catch (e) {}
  return def;
}
function assetsSave(list) {
  if (!list.length) return;                    /* there must always be ONE currency on the bar */
  if (window.__BADI_EMBEDDED) {
    ADDED = boardNames().filter((n) => list.indexOf(n) >= 0);
    /* the desktop app is the source of truth — report and it echoes the new list back */
    badiSend("assets", JSON.stringify(ADDED));
  }
  try { localStorage.setItem(ASSETS_KEY, JSON.stringify(list)); } catch (e) {}
}
function curAssetLabel() { return CUR_ASSET; }
/** Add/remove a currency from the bar (menu row click) — never remove the last one */
function toggleAsset(name) {
  const cur = addedNames();
  if (cur.indexOf(name) >= 0) {
    if (cur.length <= 1) { log("info", "At least one currency must stay on the bar"); return; }
    assetsSave(cur.filter((n) => n !== name));
  } else {
    assetsSave(cur.concat([name]));
  }
  renderAssets();
  renderAssetMenu();
}
function renderAssets() {
  const box = $("assetChips");
  if (!box) return;
  const cur = curAssetLabel();
  /* بطاقة العملة تنتهي بعلامة × الصغيرة: النقر عليها يزيل العملة من الشريط فورًا —
     والنقر على باقي البطاقة يفتح شارتها (طلب المستخدم: إعادة × إلى البطاقة نفسها) */
  box.innerHTML = addedNames().map((n) => {
    const it = BOARD.filter((x) => x.name === n)[0];
    if (!it) return "";
    const ar = window.__BADI_LANG__ === "ar";
    const open = (typeof badiMarketOpen === "function") ? badiMarketOpen(it.name) : true;
    const stT = ar ? (open ? "السوق مفتوح" : "السوق مغلوق") : (open ? "Market open" : "Market closed");
    const delT = ar ? "إزالة " + it.name + " من الشريط" : "Remove " + it.name + " from the strip";
    return '<span class="achip' + (it.name === cur ? " on" : "") + '" data-asset="' + esc(it.name) +
      '" title="' + esc(it.name) + ' — open this chart">'
      + (it.flag ? '<img class="aflag" src="' + it.flag + '" alt="">': "")
      + "<b>" + esc(it.name) + "</b>"
      + '<i class="apay">' + Number(it.payout || 0) + "%</i>"
      + '<i class="amdot ' + (open ? "open" : "closed") + '" title="' + stT + '"></i>'
      + '<i class="adel" data-del="' + esc(it.name) + '" title="' + esc(delT) + '">'
      + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></i></span>';
  }).join("") || '<span class="aempty">No currencies — add them from the + menu</span>';
}
window.__badiRenderAssets = renderAssets;   /* the desktop bridge refreshes it on setMarket */
/** Open a currency's chart: select (or reuse) a pane, then switch the feed to it */
function openAssetChart(name) {
  const it = BOARD.filter((x) => x.name === name)[0];
  if (!it) return;
  let i = paneIdxByAsset(name);
  if (i < 0) { i = activePane; setPaneAsset(i, name); }
  CUR_ASSET = name;
  setPaneActive(i);
  if (window.__BADI_EMBEDDED) {
    badiSend("asset", it.name);             /* the bridge forwards it to Python */
    renderAssets();
  } else {
    symbol = it.key || symbol;
    renderAssets();
  }
}
const pickAsset = openAssetChart;           /* bridge compat alias */
/* currency list popup (+ button): search box + add/remove rows */
function renderAssetMenu() {
  const box = $("amList");
  if (!box) return;
  const q = (($("amSearch") && $("amSearch").value) || "").trim().toLowerCase();
  const rows = BOARD.filter((it) => !q || it.name.toLowerCase().indexOf(q) >= 0);
  const ar = window.__BADI_LANG__ === "ar";
  box.innerHTML = rows.map((it) => {
    const on = addedNames().indexOf(it.name) >= 0;
    const open = (typeof badiMarketOpen === "function") ? badiMarketOpen(it.name) : true;
    return '<button class="am-row" data-am="' + esc(it.name) + '" title="' +
      ((window.__BADI_LANG__ === "ar") ? "افتح شارت هذه العملة وأضفها إلى الشريط" : "Open this chart and add it to the strip") + '">'
      + (it.flag ? '<img class="aflag" src="' + it.flag + '" alt="">' : "")
      + "<b>" + esc(it.name) + "</b>"
      + '<i class="apay">' + Number(it.payout || 0) + "%</i>"
      + '<i class="amstate ' + (open ? "open" : "closed") + '">' + (ar ? (open ? "مفتوح" : "مغلوق") : (open ? "Open" : "Closed")) + "</i>"
      + '<span class="am-tog' + (on ? " on" : "") + '">' + icon(on ? "check" : "plus", 11) + "</span></button>";
  }).join("") || '<p class="aempty" style="padding:8px">No currency matches the search</p>';
}
function assetMenuOpen() { $("assetMenu").hidden = false; renderAssetMenu(); try { $("amSearch").focus(); } catch (e) {} }
function assetMenuClose() { $("assetMenu").hidden = true; }
/* ═════ Sounds — signal chimes + win/loss tones (WebAudio, mute button in the panel) ═════ */
let actx = null, amaster = null, soundOn = true;
try { soundOn = localStorage.getItem("badiSound") !== "0"; } catch (e) {}
function audioCtx() {
  if (!actx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    try {
      actx = new AC();
      amaster = actx.createGain(); amaster.gain.value = 0.8;
      const comp = actx.createDynamicsCompressor();
      amaster.connect(comp); comp.connect(actx.destination);
    } catch (e) { return null; }
  }
  if (actx.state === "suspended") { try { actx.resume(); } catch (e) {} }
  return actx;
}
function note(freq, at, dur, o) {
  o = o || {};
  const c = audioCtx(); if (!c) return;
  const t = c.currentTime + at;
  const g = c.createGain(), f = c.createBiquadFilter();
  f.type = "lowpass"; f.frequency.value = o.lp || 7000;
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(o.vol || 0.2, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  g.connect(f); f.connect(amaster);
  [[1, 1]].concat(o.over || [[2, .25], [3, .08]]).forEach((pr) => {
    const osc = c.createOscillator(), og = c.createGain();
    osc.type = o.type || "sine"; osc.frequency.value = freq * pr[0]; og.gain.value = pr[1];
    osc.connect(og); og.connect(g);
    osc.start(t); osc.stop(t + dur + 0.05);
  });
}
/* طلب المستخدم (بعد ما زال يسمع تعارضًا): صوت واحد فقط في كل لحظة + فاصل واضح بين أي صوتين.
   أي صوت جديد (إشارة أخرى/نتيجة/خسارة) ينتظر انتهاء الصوت السابق كليًا ثم فاصل 350 مللي ثانية قبل أن يبدأ،
   والجدولة على ساعة AudioContext نفسها بدقة العينات — يستحيل تقاطع صوتين حتى لو وصلا في نفس المللي ثانية،
   والترتيب دائمًا: إشارة ← نتيجتها ← الإشارة التالية (طابور صارم بلا تجاوز) */
let sndBusyUntil = 0;
const SND_GAP = 0.35;                       /* الفاصل الإلزامي بين نهاية أي صوت وبداية الذي يليه */
function sndSlot(dur) {
  const c = audioCtx(); if (!c) return -1;
  const now = c.currentTime;
  const at = sndBusyUntil ? Math.max(0, sndBusyUntil + SND_GAP - now) : 0;
  if (at > 6) return -1;                    /* الطابور أطول من 6 ثوانٍ — أهمِل النغمة الجديدة بدل التكديس */
  sndBusyUntil = now + at + dur;
  return at;
}
/* فك قفل الصوت من أول لمسة للمستخدم (سياسة المتصفحات) — مثل ملف المستخدم التجريبي */
document.addEventListener("pointerdown", function () { try { audioCtx(); } catch (e) {} }, { once: true });
/* New signal: BUY = rising two-note chime, SELL = falling two-note chime */
function playSignal(type) {
  if (!soundOn) return;
  /* طلب المستخدم: كل إشارة صوتها يُسمع — لا حذف للصوت الثاني، الطابور يفصل الأصوات بفاصل واضح بدل التعارض */
  const at = sndSlot(0.9);
  if (at < 0) return;
  if (type === "buy") { note(659.25, at, .35); note(987.77, at + .11, .6); }
  else { note(987.77, at, .35); note(659.25, at + .11, .6); }
}
/* Result: WIN = bright rising arpeggio, LOSS = low soft falling tone */
function playResult(r) {
  if (!soundOn) return;
  /* الحزمة تشمل ذيل النغمات (osc.stop بعد نهاية المغلف بـ 50 مللي) حتى لا يبدأ الصوت التالي فوق الذيل */
  const at = sndSlot(r === "win" ? 1.3 : 1.1);
  if (at < 0) return;
  if (r === "win") {
    [523.25, 659.25, 783.99].forEach((f, i) => note(f, at + i * .09, .35, { vol: .17 }));
    note(1046.5, at + .27, .9, { vol: .2 });
  } else {
    note(196.00, at, .45, { type: "triangle", vol: .26, lp: 900, over: [[2, .12]] });
    note(146.83, at + .17, .75, { type: "triangle", vol: .26, lp: 800, over: [[2, .1]] });
  }
}
function renderSigSound() {
  const b = $("sigSound");
  if (!b) return;
  b.innerHTML = icon(soundOn ? "volume" : "volumex", 14);
  b.title = soundOn ? "Mute the signal sounds" : "Unmute the signal sounds";
}
function toggleSound() {
  soundOn = !soundOn;
  try { localStorage.setItem("badiSound", soundOn ? "1" : "0"); } catch (e) {}
  renderSigSound();
  if (soundOn) playSignal("buy");
}

/* ═════ Signals history — fed by the desktop bridge from the user's indicators ═════
   بطاقة الديمو: سوداء دائمًا + شارة BUY/SELL + علم الزوج + المدة والمؤشر والتوقيت،
 ونتيجة WIN/LOSS تصل من المحرك بعد انتهاء مدة الفريم. النقر عليها يفتح شارت عملتها */
var SIGS = [];
/* تبويب لوحة الإشارات النشط: "sig" = الإشارات الجارية الآن ، "hist" = سجل المنتهية (طلب المستخدم) */
var SIG_TAB = "sig";
function setSigTab(tab) {
  SIG_TAB = (tab === "hist") ? "hist" : "sig";
  const a = $("sigTabSig"), b = $("sigTabHist");
  if (a) a.classList.toggle("on", SIG_TAB === "sig");
  if (b) b.classList.toggle("on", SIG_TAB === "hist");
  renderSignals();
}
/* تسميات التبويبين بعدد كل قسم — عربية/إنجليزية حسب لغة التطبيق */
function updateSigTabs() {
  const ar = window.__BADI_LANG__ === "ar";
  let pend = 0, done = 0;
  for (const g of SIGS) { if (!g.result && !g.expired) pend++; else if (g.result) done++; }
  const a = $("sigTabSig"), b = $("sigTabHist");
  if (a) a.innerHTML = (ar ? "الإشارات" : "Signals") + " <b>" + pend + "</b>";
  if (b) b.innerHTML = (ar ? "السجل" : "History") + " <b>" + done + "</b>";
}
/* بطاقة الإشارة قابلة للتصميم من المؤشر نفسه (طلب المستخدم):
   signal({…, card: "HTML حر"}) أو card:{html, bg, accent, color} — البطاقة غير ثابتة */
function normSigCard(c) {
  try {
    if (!c) return null;
    if (typeof c === "string") c = { html: c };
    if (typeof c !== "object") return null;
    const html = String(c.html || "");
    if (!html.trim()) return null;
    const clean = (v) => String(v || "").replace(/"/g, "'").slice(0, 120);
    return { html: html.slice(0, 6000), bg: clean(c.bg), accent: clean(c.accent), color: clean(c.color) };
  } catch (e) { return null; }
}
window.__badiPushSignal = function (s) {
  try {
    SIGS.unshift({ asset: String(s.asset || ""), tf: String(s.tf || ""),
                   dir: s.dir === "down" ? "down" : "up", price: Number(s.price || 0),
                   indicator: String(s.indicator || ""), at: Date.now(),
                   durSec: Number(s.durSec || 0), result: null,
                   card: normSigCard(s.card) });
    if (SIGS.length > 60) SIGS.length = 60;
    renderSignals();
    playSignal(s.dir === "down" ? "sell" : "buy");
  } catch (e) {}
};
/* نتيجة الإشارة (WIN/LOSS) تصل من محرك سطح المكتب بعد انتهاء المدة */
window.__badiSigResult = function (r) {
  try {
    for (let i = 0; i < SIGS.length; i++) {
      const g = SIGS[i];
      if (!g.result && g.asset === String(r.asset || "") && g.tf === String(r.tf || "") && g.dir === (r.dir === "down" ? "down" : "up")) {
        g.result = r.result === "win" ? "win" : "loss";
        break;
      }
    }
    renderSignals();
    playResult(r.result === "win" ? "win" : "loss");
  } catch (e) {}
};
/* fallback (browser mode only): resolve locally from the pane price after the duration */
function sigLocalResolve() {
  if (window.__BADI_EMBEDDED) return;
  let changed = false;
  for (const g of SIGS) {
    if (g.result || !g.durSec || Date.now() - g.at < g.durSec * 1000) continue;
    const i = paneIdxByAsset(g.asset);
    const p = i >= 0 ? panes[i] : null;
    const px = p && p.dataArr.length ? p.dataArr[p.dataArr.length - 1].close : g.price;
    g.result = ((g.dir === "up" && px > g.price) || (g.dir === "down" && px < g.price)) ? "win" : "loss";
    changed = true;
    playResult(g.result);
  }
  if (changed) renderSignals();
}
function sigCard(g) {
  const buy = g.dir === "up";
  const it = BOARD.filter((x) => x.name === g.asset)[0] || {};
  const t = new Date(g.at);
  const pad = (n) => String(n).padStart(2, "0");
  const etime = pad(t.getHours()) + ":" + pad(t.getMinutes()) + ":" + pad(t.getSeconds());
  /* بطاقة مصممة من المؤشر نفسه (طلب المستخدم): card: '<b>…</b>' أو {html, bg, accent, color} */
  if (g.card && String(g.card.html || "").trim()) {
    let st = "";
    if (g.card.bg) st += "background:" + g.card.bg + ";";
    if (g.card.accent) st += "--sc:" + g.card.accent + ";";
    if (g.card.color) st += "color:" + g.card.color + ";";
    return '<article class="sigcard custom ' + (buy ? "buy" : "sell") + '" data-asset="' + esc(g.asset) + '"'
      + (st ? ' style="' + st + '"' : "") + ' title="' + esc(g.asset) + " — open its chart\">"
      + String(g.card.html) + "</article>";
  }
  const arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">' + (buy ? ICONS.up : ICONS.down) + "</svg>";
  const res = g.result
    ? '<span class="sig-res ' + g.result + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">' + (g.result === "win" ? '<path d="M5 12.5l4.5 4.5L19 7"/>' : '<path d="M6 6l12 12M18 6L6 18"/>') + "</svg>" + (g.result === "win" ? "WIN" : "LOSS") + "</span>"
    : '<span class="sig-etime">' + etime + "</span>";
  return '<article class="sigcard ' + (buy ? "buy" : "sell") + '" data-asset="' + esc(g.asset) +
      '" title="' + esc(g.asset) + " — open its chart\">"
    + '<div class="sig-top">' + res + '<span class="sig-badge">' + arrow + (buy ? "BUY" : "SELL") + "</span></div>"
    + '<h3 class="sig-pair">' + (it.flag ? '<img class="aflag" src="' + it.flag + '" alt="">' : "") + esc(g.asset || "—") + "</h3>"
    + '<div class="sig-rows">'
    + '<div class="sig-row"><span>' + (window.__BADI_LANG__ === "ar" ? "المدة" : "Duration") + "</span><b>" + esc(g.tf || "—") + "</b></div>"
    + '<div class="sig-row"><span>' + (window.__BADI_LANG__ === "ar" ? "المؤشر" : "Indicator") + '</span><b class="sig-ind">' + esc(g.indicator || "—") + "</b></div>"
    + '<div class="sig-row"><span>' + (window.__BADI_LANG__ === "ar" ? "الدخول" : "Entry") + "</span><b>" + etime + " · " + (isFinite(g.price) ? g.price : "—") + "</b></div>"
    + "</div></article>";
}
/* شارة العدد الحمراء على زر فتح/غلق البطاقة — رقم صغير 1 2 3 حسب عدد الإشارات الجارية (طلب المستخدم) */
function updateSigBadge() {
  const bd = $("sigBadge");
  if (!bd) return;
  const n = SIGS.filter((g) => !g.result && !g.expired).length;
  bd.textContent = n > 99 ? "99+" : String(n);
  bd.hidden = n === 0;
}
function renderSignals() {
  const box = $("sigList");
  if (!box) return;
  updateSigTabs();
  updateSigBadge();
  const pend = SIGS.filter((g) => !g.result && !g.expired);
  const done = SIGS.filter((g) => !!g.result);
  const list = SIG_TAB === "sig" ? pend : done;
  /* حُذف شريط "N signals" من رأس اللوحة — كان نصه يفور خارج إطاره عند تكبر العدد
     (ملاحظة المستخدم) — والعدد يظهر داخل تبويبي الإشارات/السجل نفسهما */
  const ar = window.__BADI_LANG__ === "ar";
  const emptyMsg = SIG_TAB === "sig"
    ? (ar ? "الإشارات الجارية من مؤشراتك تظهر هنا — شراء/بيع وعلم الزوج والمدة والمؤشر وتوقيت الدخول. النتيجة (WIN/LOSS) تظهر عند انتهاء المدة وتنتقل للسجل."
          : "Current signals from your indicators appear here — BUY/SELL, the currency flag, duration, indicator and entry time. The result (WIN/LOSS) appears when the duration ends, then the signal moves to History.")
    : (ar ? "سجل الإشارات المنتهية مع نتيجتها — WIN إذا كان الإغلاق أفضل من الدخول و LOSS خلاف ذلك. انقر أي بطاقة لفتح شارت عملتها."
          : "Finished signals land here with their result — WIN when the closing price beat the entry, LOSS otherwise. Click any card to open its chart.");
  box.innerHTML = list.length === 0
    ? '<p class="sig-empty">' + emptyMsg + "</p>"
    : list.map(sigCard).join("");
}

/* ═════ قسم التداول حُذف بالكامل (طلب المستخدم) — أُبقي على سجل الإشارات فقط ═════ */

function bindEvents() {
  /* timeframe buttons apply to the ACTIVE pane (its own timeframe) */
  $("tfGroup").addEventListener("click", function (e) {
    const b = e.target.closest(".tf");
    const p = aPane();
    if (!b || !p || b.dataset.tf === p.tf) return;
    setPaneAsset(activePane, p.asset, b.dataset.tf);
    renderTf();
  });
  $("edNewBtn").addEventListener("click", openNewModal);
  $("edCloseBtn").addEventListener("click", closeEditor);
  /* BADI: التصدير المشفر والاستيراد — التنفيذ الفعلي على جانب سطح المكتب (المفتاح داخل التطبيق) */
  function encSend(cmd) {
    if (window.__badiSend) window.__badiSend(cmd, "1");
    else log("info", "BADI works inside the desktop app only");
  }
  $("badiEnc").addEventListener("click", function () {
    const f = activeFile();
    if (!f || f.kind === "py") { log("err", "BADI: JavaScript indicators only — a Python file cannot be encrypted"); return; }
    if (!f.code || !f.code.trim()) { log("err", "BADI: there is no code to encrypt"); return; }
    saveNow();
    encSend("badi-export");
  });
  $("badiImp").addEventListener("click", function () { encSend("badi-import"); });
  $("badiImpEmpty").addEventListener("click", function () { encSend("badi-import"); });
  $("assetChips").addEventListener("click", function (e) {
    /* علامة × داخل البطاقة = إزالة العملة من الشريط فقط ولا تفتح الشارت (طلب المستخدم) */
    const d = e.target.closest("[data-del]");
    if (d) { toggleAsset(d.dataset.del); return; }
    const c = e.target.closest("[data-asset]");
    if (c) openAssetChart(c.dataset.asset);
  });
  /* currency list popup: + opener, search box, add/remove rows, click-outside closes */
  $("assetAdd").addEventListener("click", function (e) {
    e.stopPropagation();
    if ($("assetMenu").hidden) assetMenuOpen(); else assetMenuClose();
  });
  $("assetMenu").addEventListener("click", function (e) { e.stopPropagation(); });
  $("amSearch").addEventListener("input", renderAssetMenu);
  $("amList").addEventListener("click", function (e) {
    const r = e.target.closest("[data-am]");
    if (!r) return;
    /* v13.2 (طلب المستخدم): النقر على عملة في بطاقة العملات يفتح شارتها فوراً
       وتُضاف إلى شريط العملات إذا لم تكن مضافة — وليس إضافة إلى الشريط فقط */
    const nm = r.dataset.am;
    if (addedNames().indexOf(nm) < 0) assetsSave(addedNames().concat([nm]));
    openAssetChart(nm);
    assetMenuClose();
  });
  document.addEventListener("click", function (e) {
    if (!$("assetMenu").hidden && !e.target.closest("#assetMenu") && !e.target.closest("#assetAdd")) assetMenuClose();
  });
  /* currency strip scrolling: two arrows + a small draggable scrollbar */
  $("assetPrev").addEventListener("click", function () {
    $("assetChips").scrollBy({ left: -220, behavior: "smooth" });
  });
  $("assetNext").addEventListener("click", function () {
    $("assetChips").scrollBy({ left: 220, behavior: "smooth" });
  });
  /* عجلة الفأرة تمرر شريط العملات أفقيًا — بديل شريط التمرير المصغر المُزال (طلب المستخدم) */
  $("assetChips").addEventListener("wheel", function (ev) {
    if (Math.abs(ev.deltaY) > Math.abs(ev.deltaX)) { this.scrollLeft += ev.deltaY; ev.preventDefault(); }
  }, { passive: false });
  /* multi-chart: click a pane selects it (light border) — signals cards open their chart */
  $("gridHost").addEventListener("click", function (e) {
    const pn = e.target.closest(".pane");
    if (pn) setPaneActive(Number(pn.dataset.pane));
  });
  $("sigList").addEventListener("click", function (e) {
    const card = e.target.closest("[data-asset]");
    if (card) openAssetChart(card.dataset.asset);
  });
  $("edToggle").addEventListener("click", function () {
    editorOpen = !editorOpen;
    if (editorOpen) badiSend("rescan", "1");   /* فحص مجلد BadiCharts عند فتح المحرر */
    renderEdToggle(); applyEdW();
    window.dispatchEvent(new Event("resize"));
  });
  /* زر فتح مجلد التطبيق (BadiCharts) — يضع فيه المستخدم المؤشرات والأدوات مباشرة */
  $("dirBtn").addEventListener("click", function () { badiSend("opendir"); });
  $("fitBtn").addEventListener("click", function () { const ch = aChart(); if (ch) ch.resetView(); });

  /* Run button: ▶ run / ■ stop / ↻ re-run with the new code */
  $("runBtn").addEventListener("click", function () {
    const f = activeFile();
    if (!f) return;
    if (!f.enabled || editedIds.has(f.id)) runFile(f.id);
    else toggleFile(f.id);
  });
  $("saveBtn").addEventListener("click", saveNow);
  $("delBtn").addEventListener("click", function () { if (activeId) deleteFile(activeId); });
  $("cClear").addEventListener("click", function () { msgs = []; renderConsole(); });
  /* ═══ الكونسول: سحب الرأس إلى الأعلى لتكبيره + إخفاء/إظهار بزر — الحجم والحالة محفوظان (طلب المستخدم) ═══ */
  let conH = 84, conMin = false;
  try {
    conH = Math.max(30, parseInt(localStorage.getItem("badiConH") || "84", 10) || 84);
    conMin = localStorage.getItem("badiConMin") === "1";
  } catch (e) {}
  function applyConH(persist) {
    const cb = $("consoleBox");
    if (!cb) return;
    conH = Math.max(30, Math.min(conH, Math.max(140, Math.round(window.innerHeight * 0.6))));
    cb.style.height = conMin ? "24px" : conH + "px";
    cb.classList.toggle("min", conMin);
    const h = $("cHide");
    if (h) {
      h.innerHTML = icon(conMin ? "chevron-up" : "chevron-down", 12);
      h.title = conMin ? "Show the console" : "Hide the console";
    }
    if (persist) {
      try { localStorage.setItem("badiConH", String(conH)); localStorage.setItem("badiConMin", conMin ? "1" : "0"); } catch (e) {}
    }
  }
  function toggleConMin() { conMin = !conMin; applyConH(true); }
  $("cHide").addEventListener("click", toggleConMin);
  (function () {
    const head = $("consoleHead");
    let drag = null;
    head.addEventListener("mousedown", function (e) {
      if (e.target.closest("button")) return;
      drag = { y: e.clientY, h: conH, wasMin: conMin };
      e.preventDefault();
    });
    window.addEventListener("mousemove", function (e) {
      if (!drag) return;
      const dy = drag.y - e.clientY;                /* سحب إلى الأعلى = أكبر */
      if (drag.wasMin) {
        if (dy > 16) { conMin = false; applyConH(); drag.wasMin = false; drag.h = conH; drag.y = e.clientY; }
        return;
      }
      const nh = Math.max(30, drag.h + dy);
      if (nh !== conH) { conH = nh; applyConH(); }
    });
    window.addEventListener("mouseup", function (e) {
      if (!drag) return;
      const moved = Math.abs(e.clientY - drag.y), wasMin = drag.wasMin;
      drag = null;
      if (wasMin && moved < 5) conMin = false;      /* نقرة على الرأس المخفي تكفي لإظهاره */
      applyConH(true);
    });
    head.addEventListener("dblclick", function (e) {
      if (e.target.closest("button")) return;
      toggleConMin();
    });
  })();
  applyConH(false);
  $("sigSound").addEventListener("click", toggleSound);
  /* تبويبا الإشارات/السجل — طلب المستخدم */
  $("sigTabSig").addEventListener("click", function () { setSigTab("sig"); });
  $("sigTabHist").addEventListener("click", function () { setSigTab("hist"); });
  $("sigClear").addEventListener("click", function () { SIGS = []; renderSignals(); });
  $("emptyNew").addEventListener("click", openNewModal);
  $("optIndicator").addEventListener("click", function () {
    wzKind = "indicator";
    this.classList.add("on"); $("optTool").classList.remove("on");
    wzShow(2);
  });
  $("optTool").addEventListener("click", function () {
    wzKind = "tool";
    this.classList.add("on"); $("optIndicator").classList.remove("on");
    wzShow(2);
  });
  $("nfLangJs").addEventListener("click", function () { setNfLang("js"); });
  $("nfLangPy").addEventListener("click", function () { if (!this.disabled) setNfLang("py"); });
  $("wzBack").addEventListener("click", function () { if (wzStep > 1) wzShow(wzStep - 1); });
  $("wzNext").addEventListener("click", wzNext);
  $("wzClose").addEventListener("click", closeNewModal);
  $("nfName").addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); wzNext(); }
  });
  if (!window.__BADI_EMBEDDED) $("nfLangPy").style.display = "none";   /* pure web: no Python engine */
  $("newModal").addEventListener("click", function (e) { if (e.target === $("newModal")) closeNewModal(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNewModal();
  });

  /* File tabs (event delegation) */
  $("tabsRow").addEventListener("click", function (e) {
    const xb = e.target.closest("[data-x]");
    if (xb) { deleteFile(xb.dataset.x); return; }
    if (e.target.closest("#tabAdd")) { openNewModal(); return; }
    if (e.target.closest("[data-edclose]")) { closeEditor(); return; }
    const tb = e.target.closest(".tab");
    if (tb) openFile(tb.dataset.id);
  });


  /* side panel show/hide (signals) — الدالة كانت مفقودة فصارت اللوحة ثابتة لا تُخفى (إصلاح طلب المستخدم)
     وتحديثًا لطلب المستخدم: زر الجرس واحد ثابت لفتح وغلق البطاقة — لم يعد يُخفى عند فتح اللوحة */
  function setSigHidden(off) {
    const p = $("sigPane");
    if (p) p.classList.toggle("off", !!off);
    try { localStorage.setItem("badiSigHidden", off ? "1" : "0"); } catch (e) {}
    /* عرض الشارت تغيّر — أعِد تخطيط الكانفس (المكتبة تسمع لـ window.resize فقط) */
    try { window.dispatchEvent(new Event("resize")); } catch (e) {}
  }
  window.setSigHidden = setSigHidden;   /* متاحة لجسر سطح المكتب (__badiApp.setSigHidden) */
  $("sigHide").addEventListener("click", function () { setSigHidden(true); });
  /* الجرس نفسه يفتح ويغلق البطاقة — يبقى ظاهرًا في الحالتين ولا يختفي عند ظهور الإشارات (طلب المستخدم) */
  $("sigShow").addEventListener("click", function () {
    const p = $("sigPane");
    setSigHidden(!p.classList.contains("off"));
  });
  /* لا تُفتح لوحة الإشارات تلقائيًا عند الإقلاع أبدًا — يفتحها المستخدم من زر الجرس (طلب المستخدم) */
  setSigHidden(true);

  /* Shortcuts: Ctrl+S save / Ctrl+Enter run */
  window.addEventListener("keydown", function (e) {
    if (!(e.ctrlKey || e.metaKey)) return;
    const k = e.key.toLowerCase();
    if (k === "s") {
      e.preventDefault(); e.stopPropagation(); saveNow();
    } else if (k === "enter") {
      e.preventDefault(); e.stopPropagation();
      if (activeId) runFile(activeId);
    }
  }, true);

  /* Editor resize handle (editor on the right — dragging left widens it) */
  const H = $("resizeHandle");
  let drag = null, lastDisp = 0;
  H.addEventListener("pointerdown", function (e) {
    drag = { x: e.clientX, w: editorW };
    H.setPointerCapture(e.pointerId);
  });
  H.addEventListener("pointermove", function (e) {
    if (!drag || window.innerWidth < 1024) return;
    const dx = e.clientX - drag.x;
    editorW = clampW(drag.w - dx);
    applyEdW();
    const now = performance.now();
    if (now - lastDisp > 90) { lastDisp = now; window.dispatchEvent(new Event("resize")); }
  });
  H.addEventListener("pointerup", function (e) {
    if (!drag) return;
    drag = null;
    try { H.releasePointerCapture(e.pointerId); } catch (err) {}
    window.dispatchEvent(new Event("resize"));
  });
  H.addEventListener("dblclick", function () {
    editorW = 430; applyEdW(); window.dispatchEvent(new Event("resize"));
  });

  window.addEventListener("resize", applyEdW);
  document.addEventListener("visibilitychange", function () { if (document.hidden) saveFiles(files); });
  window.addEventListener("beforeunload", function () { saveFiles(files); });
}
function clampW(v) {
  const max = Math.floor(window.innerWidth * 0.62);
  return Math.max(300, Math.min(max, v));
}

/* ───────────── شريط المعلومات البسيط: متصل · المنطقة الزمنية · الوقت · FPS — بدون اسم العملة (طلب المستخدم) ───────────── */
function startStatusBar() {
  const dot = $("stDot"), conn = $("stConn"), tzEl = $("stTz"),
        clockEl = $("stClock"), fpsEl = $("stFps");
  /* عدّاد إطارات حقيقي من حلقة الرسم */
  let frames = 0, t0 = performance.now();
  (function loop(t) {
    frames++;
    if (t - t0 >= 1000) {
      fpsEl.textContent = Math.max(1, Math.round(frames * 1000 / Math.max(1, t - t0))) + " FPS";
      frames = 0; t0 = t;
    }
    requestAnimationFrame(loop);
  })(performance.now());
  /* المنطقة الزمنية المحلية مثل UTC+1 UTC+3 UTC+5:30 */
  const offMin = -new Date().getTimezoneOffset();
  const ab = Math.abs(offMin), hh = Math.floor(ab / 60), mm = ab % 60;
  tzEl.textContent = "UTC" + (offMin < 0 ? "-" : "+") + hh + (mm ? ":" + String(mm).padStart(2, "0") : "");
  /* الحالة والساعة — تحديث نصف ثانية (النص يتبع لغة التطبيق) */
  const ar = function () { return window.__BADI_LANG__ === "ar"; };
  /* معرّف المستخدم الثابت — انقر لنسخه (طلب المستخدم) */
  const uidEl = $("stUid");
  if (uidEl) {
    uidEl.title = ar() ? "معرّف المستخدم — انقر للنسخ" : "USER ID — click to copy";
    uidEl.addEventListener("click", function () {
      const u = window.__BADI_UID__ || "";
      if (!u) return;
      try { badiSend("copyuid", u); } catch (e) {}
      uidEl.classList.add("copied");
      uidEl.textContent = ar() ? "تم النسخ" : "Copied";
      setTimeout(function () {
        uidEl.classList.remove("copied");
        uidEl.textContent = window.__BADI_UID__ || u;
      }, 1100);
    });
  }
  function tick() {
    conn.textContent = live ? (ar() ? "مباشر" : "Live") : (ar() ? "متصل" : "Connected");
    dot.classList.toggle("live", !!live);
    clockEl.textContent = new Date().toLocaleTimeString("en-GB", { hour12: false });
  }
  tick();
  setInterval(tick, 500);
}

function boot() {
  buildStatic();
  BOARD = buildBoard();
  CUR_ASSET = String(((window.__BADI_BOOT_FILES || {}).market || {}).asset || (BOARD[0] && BOARD[0].name) || "");
  renderAssets();
  renderSignals();
  renderSigSound();
  loadState();
  badiSend("rescan", "1");   /* فحص مجلد BadiCharts عند الإقلاع */
  renderAll();
  renderEdToggle();
  applyEdW();
  bindEvents();
  startStatusBar();
  if (window.BadiCharts) {
    try { initPanes(); }
    catch (e) { showLibError("Error initializing the chart: " + ((e && e.message) || e)); }
  } else {
    showLibError("Failed to load the chart library — check your internet connection and try again.");
  }
  setInterval(liveTick, 1000);
}
document.addEventListener("DOMContentLoaded", boot);
</script>
</body>
</html>
'''


# ═══════════════════════════════════════════════════════════════════════════
#  PART 2 — BADI-CHARTS-V2 v2.13.0 CHART LIBRARY (badi-chart.js)
#  مكتبة الشارت (خارجية ثابتة — نسخة v2.13.0 مصغّرة: حُذفت التعليقات والمسافات
#  فقط دون أي تغيير في السلوك، ومضغوطة لتوفير الحجم)
# ═══════════════════════════════════════════════════════════════════════════
BADI_LIB_B64 = """
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
Z7Ww9ndnZ48ettv4K33USQ/38Ff3MD58FOOvR4PuT6ece3awd0C/fkoPfhp0a1+MyzFGrFxoiekX9MUPkf8ZVfBGJ/iTAGe15Yvp
jA4699d4FE1nk4tpURc+GBu1rbrYTPRAEgukjVoAYy48V8ka5WUgIFGPzQVmEJ3kt+Dn0SQuBAwv5+xsDQCCQBIMH0rDXvk8uVdJ
vX6pjHUAJ6eWtBoTR2a8zvPextJJhNLuOwAUahBJbROpoTZxtrGBoC+hgVj14C7AqsdaG0Su390+NX2No3xRmF+NiQ+7co9hoKz5
VtO/exn5qf67rxmfrnVettCb326Styjb4C3uZXRXbV7nOcPhY7NozTFqX7zV0iekuqT5goa12ml0NGWtlsuo4uYZnojbumSQHv9h
e6RPvQX/OKFk+eJqXcS9ze6VZK/c1i3VF4nfZewme/KPMme7q+GamsZ/BaZp8zW2aIu7G5+ZztNLLiLWGDcbkRvnayI3uqeXhoZQ
qm3tzUA6gx2IyXKmx2XXub3tCvosG2EMryQ6SqRti1V4ffRHrYOIzC3eBllKyC2TwD3I86dvZklLR326F90rRXM8jQiRRhhe24ZW
eFXa1EpWXnbLJze6Ldb1S0XU6Y0vdcpXDf/mbrqF342YyI+c/r9ThM/v4jLtvEWQ4r+qdtWECpzsTS+47U67+vZ6ZT/CWt4r1qwb
zHKl31H9GPtLz9mDOqe1pYBxnx3IG9ls/E6+QXYgHFdb2SxCxwujIv70uH3c6TU7fceQcHYE6a1Or7ML/1bYD57+WawGYfQ1Irsd
P8o48O0o+ZH2gYDujzURdN7ULdde69zRAKQy3LFnveJjplFqRJ37a1pE9Vq2SaOeUTqdmtRoJTKeG/6xp4j33wJYS6S4khc38BKk
yiOHvOW/3wV9qfeQ2i3eJWyRY6la6RL/vk9+XEVk5e8duzMMu8C2dalFG8O22gr+ZmUaD62xPZ631ovHtB9CRweHuDOUX41DfbAn
MFJWllj3J+YbVERHuwlsMJ4Vqo/3NY+LLhO6YUJHNb4w/pfJ5OJJwebTdZDaxC8KqmkW+eotslsq9CIfxNO0VilhNhEMP1QIed61
lbV9qwX0jNrLbPfnQLOC53x1YXQuRlrIQfanf849BSg41mDygqtOF+eR46Si4Tqi2O3+21nlBxu+ARj81T4C+Is5EfSjkPFS+C4S
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
7sL0+y+JcCOgQvYBAA==
"""


# ═══════════════════════════════════════════════════════════════════════════
#  PART 3 — THE DESKTOP APP (Python + QML) — التطبيق كاملاً كود واضح
#  (سطر واحد فقط مُعدَّل هنا: الصفحة تُقرأ من STUDIO_HTML الموجود أعلاه
#   بدل فك الضغط — انظر دالة build_embedded_html أسفل)
# ═══════════════════════════════════════════════════════════════════════════
"""
BadiCharts Studio — desktop indicator studio (Python + PySide6/QML)
Splash + login (same BadiCharts logo & flow) → studio:
  • the chart & editor are the embedded HTML app (BADI-CHARTS-V2 v2.13.0 chart
    + Monaco editor) rendered inside the window with QtWebEngine
  • program indicators & tools in JavaScript or Python (Python runs in the
    desktop engine and its values are pushed into the chart)
  • advanced ready-made indicators library
  • LIVE SERVER EDITION — Quotex REAL market & OTC assets streamed by our own
    QX server (qx_server_v13.py beside the app): real login, real candles
    (BRLUSD_otc 300 on login + others one by one), live prices for every asset,
    scroll-back batches of 300 older candles — no fake candles, no fake login
  • Telegram alerts from your indicators, with chart screenshots
  • black dark theme ↔ light theme — the chart & editor follow the app colors live
  • English ↔ العربية
Run:  pip install PySide6 && python BadiChartsStudio.py
"""
import os
import re
import sys
import json
import time
import base64
import hashlib
import hmac
import gzip
import lzma
import random
import threading
import importlib
import asyncio
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from math import ceil

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QUrl, QFileSystemWatcher, QMimeData
from PySide6.QtGui import QGuiApplication, QDesktopServices
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick

# ═══════════════════ LIVE SERVER EDITION — QX ENGINE LOADER ═══════════════════
# المحرك مدمج داخل هذا الملف (كود واحد — v14.8): لا يحتاج أي ملف ثانٍ بجانبه.
#   • نفس تسجيل الدخول (connect_quotex) ونفس جلب الشموع الأصلي دون أي تغيير.
#   • BRLUSD_otc: 300 شمعة فوراً بعد الدخول + الحالة ونسبة الدفع.
#   • بقية العملات واحدة تلو الأخرى (300 شمعة لكل عملة) + بث حي لكل عملة.
#   • دفعات التمرير للخلف (300 شمعة) عبر fetch_older_batch().
#   • v14.1 (مثل تريدنغ فيو): التمرير للخلف يُطلب عند اقتراب بداية البيانات من
#     الربع الأيسر من الشاشة (لا انتظار آخر 5 شموع)، مع ذاكرة «لا يوجد أقدم»
#     لكل عملة+فريم، ودمج الدفعة موسوماً بالعملة والفريم فلا يختلط، وإعادة
#     طلب تلقائية ما دمت متعمقاً في التاريخ.
#   • التيكات في الذاكرة فقط وتُحذف بعد 5 دقائق (سياسة الخادم نفسها).
# ═════════════ v14.8: كود واحد — المحرك مدمج داخل هذا الملف ═════════════
# طلب المستخدم حرفياً: «يجب ان يكون كود واحد وليس يحمل كود ثاني».
# كل كود محرك Quotex موجود أدناه في النص الخام _QX_ENGINE_SOURCE ويُنفَّذ
# في مساحة أسماء وحدّة عند الإقلاع — التطبيق لا يحمّل أي ملف ثانٍ ولا
# يحتاج qx_server_v14.py أو qx_server_v13.py بجانبه أبداً.
_QX_MOD = None


def _qx_module():
    """المحرك المدمج (كود واحد): يُنفَّذ مرة واحدة في مساحة أسماء معزولة
    ويعيد وحدة تحمل كل رموز المحرك (CLIENT, ASYNC_LOOP, MT4_WRITER,
    get_historical_candles, _fill_missing_slots, ...) دون أي ملف خارجي."""
    global _QX_MOD
    if _QX_MOD is not None:
        return _QX_MOD or None
    try:
        import types as _types
        _mod = _types.ModuleType("qx_embedded_engine")
        _mod.__file__ = os.path.abspath(__file__)
        _mod.__name__ = "qx_embedded_engine"
        exec(compile(_QX_ENGINE_SOURCE, "qx_embedded_engine", "exec"), _mod.__dict__)
        sys.modules["qx_embedded_engine"] = _mod
        try:
            _mod.DEBUG_LOGS = False
        except Exception:
            pass
        _QX_MOD = _mod
    except Exception as _e:
        try:
            print("[QX] embedded engine init failed: " + str(_e))
        except Exception:
            pass
        _QX_MOD = False
    return _QX_MOD or None


# ═══════════════════════ _QX_ENGINE_SOURCE ═══════════════════════
# المحرك الكامل (qx_server_v14 + إصلاحات تقرير الفحص v14.8) كنص خام —
# لا يحتوي ''' أبداً فالمحدد آمن. هذا هو «الكود الثاني» القديم أصبح جزءاً
# من هذا الملف الواحد.

_QX_ENGINE_SOURCE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import io
import ssl
import json

# ==============================================================================
# ENCODING FIX: Force UTF-8 on stdout / stderr / stdin to prevent
# UnicodeEncodeError / UnicodeDecodeError when the script prints or logs
# non-ASCII characters (Arabic, accents, emoji, etc.) on Windows consoles
# whose default code page is cp1252 / cp1256.
# ==============================================================================
# Fix console encoding on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set default encoding to UTF-8
try:
    io.TextIOWrapper(open.__self__, encoding='utf-8')
except Exception:
    pass
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
# FIX FOR NUITKA / FROZEN ENVIRONMENT
# ==============================================================================
# 1) fake_useragent: force local-only mode so it doesn't try to fetch a remote
#    user-agent list (which would crash when running as a frozen EXE / Nuitka
#    build with no network access or no writable cache dir).
os.environ['HTTPX_FAKE_USERAGENT_LOCAL_ONLY'] = 'True'
os.environ['FAKE_USERAGENT_FALLBACK'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# 2) SSL certificates: pin certifi's CA bundle path into the env vars that
#    requests / websocket-client / ssl module all read. This avoids
#    "SSL: CERTIFICATE_VERIFY_FAILED" errors in frozen builds where the
#    default cert store is missing or points to a temp dir.
_cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = _cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = _cert_path
os.environ['REQUESTS_CA_BUNDLE'] = _cert_path

# 3) Working directory: chdir to the folder that contains the EXE (frozen) or
#    the .py file (script mode) so app_data.db, mt4_config.json, etc. are
#    created next to the binary — NOT inside a temp _MEIPASS / build dir.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.chdir(BASE_DIR)
except Exception:
    pass

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
# SECTION 1.6: STARTUP INTERFACE (Welcome + License Verification)
# ==============================================================================
# هذا القسم مستقل تماماً: يعرض شعار QXMT4 + قائمة ترخيص + تحقق عبر Supabase.
# ينتهي عمله بمجرد تأكيد الترخيص، ثم يُسلّم التحكم إلى بقية البرنامج.
# كل الأسماء داخل فضاء `qx_startup.*` — لا توجد تعارضات مع بقية الكود.
# ==============================================================================
import hashlib as _qx_hashlib
import socket as _qx_socket
import platform as _qx_platform
from dataclasses import dataclass as _qx_dataclass
from datetime import datetime as _qx_datetime, timezone as _qx_timezone

try:
    from pyfiglet import figlet_format as _qx_figlet_format, FontNotFound as _qx_FontNotFound
except ImportError:  # pragma: no cover
    _qx_figlet_format = None
    _qx_FontNotFound = Exception

try:
    import requests as _qx_requests
except ImportError:  # pragma: no cover
    _qx_requests = None


def _qx_supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # enable ANSI on Windows 10+
    return True


class _QxStyle:
    """أكواد ANSI. تصبح سلاسل فارغة عند تعطيل الألوان."""

    _NAMES = {
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "DIM": "\033[2m",
        "CYAN": "\033[96m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "MAGENTA": "\033[95m",
        "RED": "\033[91m",
        "WHITE": "\033[97m",
        "BLUE": "\033[94m",
        "GRAY": "\033[90m",
    }

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        for name, code in self._NAMES.items():
            setattr(self, name, code if enabled else "")

    def rgb(self, r: int, g: int, b: int) -> str:
        return f"\033[38;2;{r};{g};{b}m" if self.enabled else ""


def _qx_term_size() -> tuple:
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def _qx_clear() -> None:
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def _qx_configure_stdout() -> None:
    if (sys.stdout.encoding or "").lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _qx_best_rule_char() -> str:
    """Heavy box-drawing line if the terminal can encode it, else ASCII."""
    encoding = (sys.stdout.encoding or "ascii")
    for char in ("\u2501", "\u2550", "\u2015"):  # heavy, double, horizontal bar
        try:
            char.encode(encoding)
            return char
        except (UnicodeEncodeError, LookupError):
            continue
    return "-"


_QX_GRADIENT = (
    (138, 43, 226),
    (106, 60, 235),
    (75, 80, 245),
    (40, 120, 250),
    (0, 170, 255),
    (0, 230, 255),
)


@_qx_dataclass
class QxStartupConfig:
    app_name: str = "QXMT4"
    # حساب المطور الفعلي (يظهر في قسم DEVELOPER → Username)
    username: str = "@qxzero1"
    # رابط القناة الرسمي للمطور (يظهر في قسم DEVELOPER → Channel)
    channel: str = "https://t.me/qxchart"
    # بوت التراخيص (يظهر فقط في "Get your license from …" — بلونين مختلفين)
    license_bot: str = "@QXChartLicenseBot"
    license_bot_url: str = "https://t.me/QXChartLicenseBot"
    font: str = "slant"
    animate: bool = True
    line_delay: float = 0.06
    width: int = 52
    rule_char: str = ""  # empty -> auto-detect (heavy line, or "-" fallback)
    supabase_url: str = "https://scuebmuivzqckasssyfu.supabase.co"
    supabase_anon_key: str = "sb_publishable_wBPTnTcj6baFgyYxaP41rw_a5KPd8-C"
    license_table: str = "licenses"
    # license_store_path has been removed: license data now lives in the
    # SQLite database (app_data.db, 'licenses' table). See _QxLicenseStore.

    def __post_init__(self):
        if not self.rule_char:
            self.rule_char = _qx_best_rule_char()


# ---- Banner rendering ----

def _qx_figlet(text: str, font: str) -> list:
    if _qx_figlet_format is None:
        return [text]
    try:
        art = _qx_figlet_format(text, font=font)
    except _qx_FontNotFound:
        art = _qx_figlet_format(text)
    return [line for line in art.splitlines() if line.strip()]


def _qx_print_gradient(lines, st: '_QxStyle', indent: str = "  ",
                       delay: float = 0.0) -> None:
    for i, line in enumerate(lines):
        r, g, b = _QX_GRADIENT[i % len(_QX_GRADIENT)]
        sys.stdout.write(f"{indent}{st.rgb(r, g, b)}{st.BOLD}{line}{st.RESET}\n")
        sys.stdout.flush()
        if delay:
            time.sleep(delay)


def _qx_show_welcome(cfg: 'QxStartupConfig', st: '_QxStyle') -> None:
    """ترحيب صغير في المنتصف، يُكتب حرفاً حرفاً."""
    _qx_clear()
    cols, rows = _qx_term_size()
    text = f"Welcome, {cfg.app_name} Trader"

    top_pad = max(0, rows // 2 - 1)
    print("\n" * top_pad, end="")

    left_pad = " " * max(0, (cols - len(text)) // 2)
    r, g, b = _QX_GRADIENT[2]
    color = st.rgb(r, g, b)

    sys.stdout.write(left_pad)
    sys.stdout.flush()
    for ch in text:
        sys.stdout.write(f"{color}{st.BOLD}{ch}{st.RESET}")
        sys.stdout.flush()
        if cfg.animate:
            time.sleep(0.04)
    print()

    if cfg.animate:
        time.sleep(0.7)
    _qx_clear()


def _qx_show_logo(cfg: 'QxStartupConfig', st: '_QxStyle') -> None:
    print()
    _qx_print_gradient(_qx_figlet(cfg.app_name, cfg.font), st,
                       delay=cfg.line_delay if cfg.animate else 0.0)
    print()


# ---- Menu ----

def _qx_rule(cfg: 'QxStartupConfig', st: '_QxStyle') -> None:
    print(f"  {st.GRAY}{cfg.rule_char * cfg.width}{st.RESET}")


def _qx_show_menu(cfg: 'QxStartupConfig', st: '_QxStyle') -> None:
    _qx_rule(cfg, st)
    # العناوين الرئيسية (DEVELOPER, ACTIVATION) باللون السماوي + Bold (مثل الشعار)
    print(f"  {st.CYAN}{st.BOLD}DEVELOPER{st.RESET}")
    # التسميات الثابتة (Username, Channel) باللون الأبيض الباهت
    # القيم (المحتوى الفعلي) باللون السماوي + Bold
    print(f"  {st.WHITE}Username{st.RESET} : {st.CYAN}{st.BOLD}{cfg.username}{st.RESET}")
    print(f"  {st.WHITE}Channel {st.RESET} : {st.CYAN}{st.BOLD}{cfg.channel}{st.RESET}")
    print(f"  {st.DIM}Contact via Telegram for support and updates{st.RESET}")
    _qx_rule(cfg, st)
    print()

    print(f"  {st.CYAN}{st.BOLD}ACTIVATION{st.RESET}")
    access_points = (
        "Fetches all timeframes from 5 seconds up to 1 day",
        "Auto-reconnects when internet drops, never loses the stream",
        "User can fetch as many candles as needed",
        "Default: 1000 candles per asset in just 4 seconds",
        "Supports two timeframe ranges simultaneously",
        "Includes 41 OTC assets out of the box",
    )
    for item in access_points:
        print(f"  {st.GREEN}*{st.RESET} {st.WHITE}{item}{st.RESET}")
    print()

    _qx_rule(cfg, st)
    # [L]/[Q] بلون سماوي زاهي + Bold (مثل الشعار)
    print(f"  {st.CYAN}{st.BOLD}[L]{st.RESET} {st.WHITE}Enter license key{st.RESET}")
    print(f"  {st.CYAN}{st.BOLD}[Q]{st.RESET} {st.WHITE}Quit{st.RESET}")
    _qx_rule(cfg, st)
    # "Get your license from @QXChartLicenseBot" — بلونين مختلفين:
    #   النص التمهيدي باللون الرمادي (DIM)
    #   اسم البوت باللون السماوي الزاهي + Bold (مثل لون الشعار)
    print(f"  {st.DIM}Get your license from {st.RESET}{st.CYAN}{st.BOLD}{cfg.license_bot}{st.RESET}")
    print()


def _qx_render_home(cfg: 'QxStartupConfig', st: '_QxStyle') -> None:
    """إعادة رسم الشعار + القائمة (بعد كل تغيير شاشة)."""
    _qx_clear()
    _qx_show_logo(cfg, st)
    _qx_show_menu(cfg, st)


# ---- License: local cache ----
# NOTE: The original JSON-file-based _QxLocalStore has been replaced by a
# SQLite-backed _QxLicenseStore defined later in this file (after the
# DB_PATH and _init_db() definitions). All license data now lives in the
# 'licenses' table of app_data.db — no JSON files are read or written.
#
# A tiny backward-compat stub is provided here so any external code that
# still calls _QxLocalStore(...) keeps working; it transparently delegates
# to _QxLicenseStore.

class _QxLocalStore:
    """[Deprecated] Backward-compat shim that delegates to _QxLicenseStore.
    Kept so legacy call sites don't break. No JSON file is touched."""

    def __init__(self, file_path: str = None):
        # file_path is accepted for backward-compat but ignored; all data
        # now lives in the SQLite database (DB_PATH / app_data.db).
        self._impl = _QxLicenseStore()

    def get(self, key: str):
        return self._impl.get(key)

    def set(self, key: str, value) -> bool:
        return self._impl.set(key, value)

    def delete(self, key: str) -> bool:
        return self._impl.delete(key)


def _qx_get_hardware_id() -> str:
    try:
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
        # Safe encoding for username
        if isinstance(user, bytes):
            user = user.decode('utf-8', errors='ignore')
        else:
            user = str(user).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        user = "unknown"

    try:
        hostname = _qx_socket.gethostname()
        if isinstance(hostname, bytes):
            hostname = hostname.decode('utf-8', errors='ignore')
    except Exception:
        hostname = "unknown"

    raw = f"{user}-{_qx_platform.system().lower()}-{hostname}"
    return _qx_hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---- License: Supabase REST client ----

@_qx_dataclass
class _QxSupabaseConfig:
    url: str
    anon_key: str
    table: str = "licenses"
    usage_table: str = "usage_logs"
    timeout: float = 10.0


class _QxSupabaseLicenseClient:
    def __init__(self, cfg: '_QxSupabaseConfig'):
        self.cfg = cfg
        self._headers = {
            "apikey": cfg.anon_key,
            "Authorization": f"Bearer {cfg.anon_key}",
            "Content-Type": "application/json",
        }

    def _rest_url(self, table: str) -> str:
        return f"{self.cfg.url.rstrip('/')}/rest/v1/{table}"

    def fetch_license(self, license_key: str) -> Optional[dict]:
        params = {
            "select": "id,license_key,username,is_active,expires_at,hardware_id",
            "license_key": f"eq.{license_key}",
        }
        resp = _qx_requests.get(
            self._rest_url(self.cfg.table),
            headers=self._headers,
            params=params,
            timeout=self.cfg.timeout,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None

    def bind_hardware(self, license_key: str, hardware_id: str) -> None:
        resp = _qx_requests.patch(
            self._rest_url(self.cfg.table),
            headers=self._headers,
            params={"license_key": f"eq.{license_key}"},
            json={"hardware_id": hardware_id, "last_seen": _qx_now_iso()},
            timeout=self.cfg.timeout,
        )
        resp.raise_for_status()

    def touch_last_seen(self, license_key: str) -> None:
        resp = _qx_requests.patch(
            self._rest_url(self.cfg.table),
            headers=self._headers,
            params={"license_key": f"eq.{license_key}"},
            json={"last_seen": _qx_now_iso()},
            timeout=self.cfg.timeout,
        )
        resp.raise_for_status()

    def log_usage(self, license_id, action_type: str = "login") -> None:
        try:
            _qx_requests.post(
                self._rest_url(self.cfg.usage_table),
                headers=self._headers,
                json={"license_id": license_id, "action_type": action_type},
                timeout=self.cfg.timeout,
            )
        except _qx_requests.RequestException:
            pass  # تسجيل الاستخدام اختياري، لا تُعطّل العملية أبداً


def _qx_now_iso() -> str:
    return _qx_datetime.now(_qx_timezone.utc).isoformat()


def _qx_parse_datetime(value: str) -> Optional[_qx_datetime]:
    try:
        return _qx_datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


# ---- License: verification flow ----

@_qx_dataclass
class QxLicenseResult:
    ok: bool
    username: Optional[str] = None
    expires_at: Optional[_qx_datetime] = None
    message: str = ""


def _qx_verify_with_supabase(client: '_QxSupabaseLicenseClient', license_key: str) -> 'QxLicenseResult':
    hw_id = _qx_get_hardware_id()

    try:
        license_row = client.fetch_license(license_key)
    except _qx_requests.RequestException as e:
        return QxLicenseResult(False, message=f"Could not reach the license server: {e}")

    if not license_row:
        return QxLicenseResult(False, message="Invalid or non-existent license key.")

    if not license_row.get("is_active"):
        return QxLicenseResult(False, message="This license has been deactivated by the administrator.")

    expires_raw = license_row.get("expires_at")
    expires_at = _qx_parse_datetime(expires_raw) if expires_raw else None
    if expires_at and expires_at < _qx_datetime.now(_qx_timezone.utc):
        return QxLicenseResult(False, message=f"This license expired on {expires_at:%Y-%m-%d}.")

    bound_hw = license_row.get("hardware_id")
    if bound_hw:
        if bound_hw != hw_id:
            return QxLicenseResult(False, message="This license key is bound to another device and cannot be shared.")
    else:
        try:
            client.bind_hardware(license_key, hw_id)
        except _qx_requests.RequestException as e:
            return QxLicenseResult(False, message=f"Could not bind license to this device: {e}")

    try:
        client.log_usage(license_row.get("id"))
        client.touch_last_seen(license_key)
    except _qx_requests.RequestException:
        pass

    return QxLicenseResult(
        True,
        username=license_row.get("username"),
        expires_at=expires_at,
        message="License verified.",
    )


def _qx_verify_license_local(key: str) -> bool:
    """بديل محلي فقط يُستخدم عند عدم وجود إعدادات Supabase."""
    valid_keys = {
        "QXMT4-XXXX-XXXX-XXXX",
        "QXMT4-DEMO-0000-0000",
    }
    return key.strip().upper() in valid_keys


def _qx_try_license_key(cfg: 'QxStartupConfig', st: '_QxStyle', key: str) -> Optional['QxLicenseResult']:
    """التحقق من مفتاح ترخيص أدخله المستخدم."""
    if cfg.supabase_url and cfg.supabase_anon_key:
        if _qx_requests is None:
            print(f"  {st.RED}[X] 'requests' is not installed (pip install requests).{st.RESET}")
            return None
        store = _QxLicenseStore()  # SQLite-backed (no JSON)
        client = _QxSupabaseLicenseClient(_QxSupabaseConfig(
            url=cfg.supabase_url,
            anon_key=cfg.supabase_anon_key,
            table=cfg.license_table,
        ))
        result = _qx_verify_with_supabase(client, key)
        if result.ok:
            store.set("license", {
                "license_key": key,
                "hardware_id": _qx_get_hardware_id(),
                "saved_at": _qx_now_iso(),
            })
            print(f"\n  {st.GREEN}{st.BOLD}[OK] Welcome {result.username or ''}. License activated.{st.RESET}")
            return result
        print(f"\n  {st.RED}{st.BOLD}[X] {result.message}{st.RESET}")
        return None

    if _qx_verify_license_local(key):
        print(f"\n  {st.GREEN}{st.BOLD}[OK] License activated.{st.RESET}")
        return QxLicenseResult(True, message="License activated.")
    print(f"\n  {st.RED}{st.BOLD}[X] Invalid license key.{st.RESET}")
    print(f"  {st.DIM}Contact {cfg.username} to get a license.{st.RESET}")
    return None


def _qx_try_saved_license(cfg: 'QxStartupConfig', st: '_QxStyle') -> Optional['QxLicenseResult']:
    """فحص صامت لترخيص محفوظ سابقاً عبر Supabase، إن وُجد."""
    if not (cfg.supabase_url and cfg.supabase_anon_key and _qx_requests):
        return None
    store = _QxLicenseStore()  # SQLite-backed (no JSON)
    saved = store.get("license")
    if not saved or saved.get("hardware_id") != _qx_get_hardware_id():
        return None
    client = _QxSupabaseLicenseClient(_QxSupabaseConfig(
        url=cfg.supabase_url,
        anon_key=cfg.supabase_anon_key,
        table=cfg.license_table,
    ))
    result = _qx_verify_with_supabase(client, saved["license_key"])
    return result if result.ok else None


# ---- Main startup loop ----

def qx_run_startup(cfg: Optional['QxStartupConfig'] = None, skip_welcome: bool = False) -> Optional['QxLicenseResult']:
    """يعرض الترحيب + شاشة الترخيص. يُرجع QxLicenseResult عند النجاح،
    أو None إذا خرج المستخدم قبل إدخال ترخيص صالح."""
    _qx_configure_stdout()
    cfg = cfg or QxStartupConfig()
    st = _QxStyle(_qx_supports_color())

    if not skip_welcome:
        _qx_show_welcome(cfg, st)
    _qx_render_home(cfg, st)

    # حاول ترخيصاً محفوظاً سابقاً بشكل صامت قبل أي سؤال.
    try:
        saved_result = _qx_try_saved_license(cfg, st)
    except Exception as _e:
        # Any error reading the saved license (UnicodeDecodeError, OSError,
        # JSON parse error, network error, ...) must not block the menu.
        try:
            print(f"  \033[93m[warn] saved-license check failed: {_e}\033[0m")
        except Exception:
            pass
        saved_result = None
    if saved_result:
        print(f"\n  {st.GREEN}{st.BOLD}[OK] Welcome back{', ' + saved_result.username if saved_result.username else ''}. License valid.{st.RESET}")
        time.sleep(1.0)
        return saved_result

    prompt = f"  {st.YELLOW}> License key (or [Q] to quit): {st.RESET}"

    while True:
        try:
            raw_choice = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        choice = raw_choice.lower()

        if choice in ("q", "quit", "exit"):
            return None

        if choice == "l":
            print()
            try:
                key = input(f"  {st.CYAN}License key: {st.RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return None
            if not key:
                print(f"\n  {st.RED}[X] No key entered.{st.RESET}")
                input(f"\n  {st.DIM}Press Enter to continue...{st.RESET}")
                _qx_render_home(cfg, st)
                continue
            raw_choice = key

        result = _qx_try_license_key(cfg, st, raw_choice)
        if result:
            time.sleep(1.0)
            return result

        input(f"\n  {st.DIM}Press Enter to continue...{st.RESET}")
        _qx_render_home(cfg, st)



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

# ----------------------------------------------------------------------
# SECTION 2B: DATABASE STORAGE
# Replaces saved_email.txt, session.json, session_state.json with a single
# SQLite database file (app_data.db). SQLite is built into Python, so there
# are no extra dependencies. All credentials, session cookies/tokens and
# login state now live in two tables:
#   - sessions  (email -> JSON blob with cookies/token/user_agent)
#   - app_state (single-row table: email, password, host, last_login, ...)
# On every startup, the sessions table is wiped so the app performs a fresh
# login (no stale cookies/token) — see SessionManager.delete_session_file().
# ----------------------------------------------------------------------
import sqlite3 as _sqlite3

DB_PATH = Path(resource_path("app_data.db"))
_db_lock = threading.Lock()

def _db_conn() -> "_sqlite3.Connection":
    conn = _sqlite3.connect(str(DB_PATH), timeout=15, check_same_thread=False)
    conn.row_factory = _sqlite3.Row
    return conn

def _init_db() -> None:
    try:
        DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    except Exception:
        pass
    with _db_lock:
        conn = _db_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    email TEXT PRIMARY KEY,
                    data  TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_state (
                    id                  INTEGER PRIMARY KEY CHECK (id = 1),
                    email               TEXT,
                    password            TEXT,
                    host                TEXT,
                    last_login          REAL,
                    last_success        INTEGER,
                    failed_auth_count   INTEGER
                )
            """)
            # ---- New: licenses table (replaces license_store.json) ----
            conn.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    key         TEXT PRIMARY KEY,
                    value_json  TEXT NOT NULL,
                    updated_at  INTEGER
                )
            """)
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

    # ---- One-time migration: import any existing license_store.json ----
    # so legacy users don't lose their saved license. After migration the
    # JSON file is renamed to .bak so it's no longer read on next start.
    try:
        _migrate_legacy_license_json()
    except Exception:
        pass

_init_db()

# ==============================================================================
# LICENSE STORE: SQLite-backed replacement for the old JSON _QxLocalStore.
# All license data now lives in the 'licenses' table of app_data.db.
# No JSON files are read or written by this code path.
# ==============================================================================

class _QxLicenseStore:
    """Persisted key-value store backed by the SQLite database.
    Replaces the legacy JSON file-based _QxLocalStore. Uses the
    'licenses' table created by _init_db()."""

    def __init__(self, db_path: 'Optional[Path]' = None):
        # DB_PATH is a module-level constant defined above; we resolve it
        # lazily so this class is safe to instantiate at any time.
        self._db_path = db_path if db_path is not None else DB_PATH

    def _conn(self):
        conn = _sqlite3.connect(str(self._db_path), timeout=15, check_same_thread=False)
        conn.row_factory = _sqlite3.Row
        return conn

    def get(self, key: str = 'license'):
        # Read a saved value. Returns a dict or None.
        with _db_lock:
            conn = self._conn()
            try:
                row = conn.execute(
                    "SELECT value_json FROM licenses WHERE key=?", (key,)
                ).fetchone()
                if row:
                    try:
                        return json.loads(row["value_json"])
                    except (json.JSONDecodeError, TypeError, ValueError):
                        return None
                return None
            except Exception:
                return None
            finally:
                conn.close()

    def set(self, key: str, value) -> bool:
        # Save a value. Returns True on success.
        try:
            value_json = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return False
        with _db_lock:
            conn = self._conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO licenses (key, value_json, updated_at) VALUES (?, ?, ?)",
                    (key, value_json, int(time.time()))
                )
                conn.commit()
                return True
            except Exception:
                return False
            finally:
                conn.close()

    def delete(self, key: str = 'license') -> bool:
        with _db_lock:
            conn = self._conn()
            try:
                conn.execute("DELETE FROM licenses WHERE key=?", (key,))
                conn.commit()
                return True
            except Exception:
                return False
            finally:
                conn.close()


def _migrate_legacy_license_json() -> None:
    """One-time migration: if a legacy license_store.json file exists in
    the current working directory, import its 'license' entry into the
    SQLite 'licenses' table, then rename the JSON file to .bak so it is
    no longer used on subsequent startups."""
    legacy_paths = [
        Path("license_store.json"),
        Path("app_data.db"),  # legacy collision case
    ]
    store = _QxLicenseStore()
    for p in legacy_paths:
        try:
            if not p.exists() or not p.is_file():
                continue
            # Skip if the file is actually the SQLite database
            if p.resolve() == DB_PATH.resolve():
                continue
            # Read defensively with errors='replace' so a binary file
            # (e.g. a SQLite file accidentally pointed at) does not raise.
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                try:
                    data = json.load(f)
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Not a JSON file - rename to .bak so we don't keep
                    # trying to read it on every startup.
                    p.rename(p.with_suffix(p.suffix + '.bak'))
                    continue
            if not isinstance(data, dict):
                p.rename(p.with_suffix(p.suffix + '.bak'))
                continue
            lic = data.get('license')
            if isinstance(lic, dict):
                # Only migrate if not already in SQLite
                if not store.get('license'):
                    store.set('license', lic)
            # Rename the JSON file to .bak so it's not used again
            p.rename(p.with_suffix(p.suffix + '.bak'))
        except Exception:
            pass


def load_session(email: str, user_agent: str = None) -> dict:
    if user_agent is None:
        try: user_agent = UserAgent().random
        except Exception: user_agent = USER_AGENT
    default_data = {"cookies": None, "token": None, "user_agent": user_agent}
    with _db_lock:
        conn = _db_conn()
        try:
            row = conn.execute("SELECT data FROM sessions WHERE email=?", (email,)).fetchone()
            if row:
                try:
                    data = json.loads(row["data"])
                    if not data.get("user_agent"):
                        data["user_agent"] = user_agent
                    return data
                except json.JSONDecodeError:
                    pass
            conn.execute(
                "INSERT OR REPLACE INTO sessions (email, data) VALUES (?, ?)",
                (email, json.dumps(default_data, indent=2))
            )
            conn.commit()
            return default_data
        except Exception:
            return default_data
        finally:
            conn.close()

def update_session(email: str, d: dict) -> dict:
    with _db_lock:
        conn = _db_conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (email, data) VALUES (?, ?)",
                (email, json.dumps(d, indent=2))
            )
            conn.commit()
            return d
        except Exception:
            return d
        finally:
            conn.close()

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
        # Use raw bytes so BeautifulSoup can detect the real encoding;
        # never rely on requests' .text which may raise UnicodeDecodeError.
        try:
            raw = self.response.content if self.response is not None else b""
            return BeautifulSoup(raw, "html.parser", from_encoding="utf-8")
        except Exception:
            return BeautifulSoup(b"", "html.parser")

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
            # Defensive: a malformed binary frame must never crash the WS thread.
            if isinstance(msg, (bytes, bytearray, memoryview)):
                msg_str = bytes(msg).decode("utf-8", errors="ignore")
            else:
                msg_str = str(msg)

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

                    asyncio.run_coroutine_threadsafe(
                        self.api.event_registry.set_event(f'candles_ready_{asset}', message),
                        loop
                    )

                    index = message.get("index")
                    if index is not None:
                        asyncio.run_coroutine_threadsafe(
                            self.api.event_registry.set_event(f'candles_ready_{asset}_{index}', message),
                            loop
                        )

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
        try:
            CONNECTION_ALIVE = False
        except Exception:
            pass

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
        try:
            CONNECTION_ALIVE = False
        except Exception:
            pass

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

    async def get_all_assets(self):
        return {}

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
    try:
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
    try:
        tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        # Safe encoding - ignore problematic characters
        error_msg = str(exc).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        print(f"  \033[91m[{ts}] FATAL in {context}: {error_msg}\033[0m")
        _log_to_file(f"[{ts}] FATAL in {context}: {error_msg}\n{tb_text}")
    except Exception as e:
        # Fallback if even the error handler fails
        try:
            print(f"  \033[91m[{ts}] FATAL in {context}: Encoding error occurred\033[0m")
            _log_to_file(f"[{ts}] FATAL in {context}: Encoding error - {e}")
        except:
            pass

def _thread_excepthook(args):
    log_exception(f"thread '{args.thread.name}'", args.exc_value)
threading.excepthook = _thread_excepthook

def _main_excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt): sys.__excepthook__(exc_type, exc_value, exc_tb); return
    # Transient encoding errors should NOT kill the whole process.
    if issubclass(exc_type, UnicodeError):
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            safe = str(exc_value).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            print(f"  \033[93m[{ts}] SWALLOWED UnicodeError at top level: {safe}\033[0m")
            _log_to_file(f"[{ts}] SWALLOWED UnicodeError at top level: {safe}")
        except Exception:
            pass
        return
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
                _digits_config_cache = json.loads(DIGITS_CONFIG_FILE.read_text(encoding='utf-8', errors='replace'))
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
        config = json.loads(MT4_CONFIG_FILE.read_text(encoding='utf-8', errors='replace')) if MT4_CONFIG_FILE.exists() else {}
        config["mt4_history_path"] = path
        config["saved_at"] = int(time.time())
        MT4_CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
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
            saved_path = json.loads(MT4_CONFIG_FILE.read_text(encoding='utf-8', errors='replace')).get("mt4_history_path", "")
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

# Credentials, session state and login state now live in app_data.db
# (see SECTION 2B). The three constants below are kept only as legacy
# references for any external code that still imports them; they are no
# longer used for storage.
SESSION_FILE = Path("session.json")
SESSION_STATE_FILE = Path("session_state.json")
EMAIL_FILE = Path("saved_email.txt")

class SessionManager:
    def __init__(self): self.state = self._load_state()
    def _load_state(self) -> dict:
        try:
            with _db_lock:
                conn = _db_conn()
                try:
                    row = conn.execute("SELECT * FROM app_state WHERE id=1").fetchone()
                    if row:
                        return {
                            "last_login": row["last_login"] or 0,
                            "last_success": bool(row["last_success"]),
                            "failed_auth_count": row["failed_auth_count"] or 0,
                            "email": row["email"] or "",
                            "password": row["password"] or "",
                            "host": row["host"] or "qxbroker.com",
                        }
                finally:
                    conn.close()
        except Exception:
            pass
        return {"last_login": 0, "last_success": False, "failed_auth_count": 0, "email": "", "password": "", "host": "qxbroker.com"}
    def _save_state(self):
        try:
            with _db_lock:
                conn = _db_conn()
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO app_state
                        (id, email, password, host, last_login, last_success, failed_auth_count)
                        VALUES (1, ?, ?, ?, ?, ?, ?)
                    """, (
                        1,
                        self.state.get("email", ""),
                        self.state.get("password", ""),
                        self.state.get("host", "qxbroker.com"),
                        self.state.get("last_login", 0),
                        1 if self.state.get("last_success", False) else 0,
                        self.state.get("failed_auth_count", 0),
                    ))
                    conn.commit()
                finally:
                    conn.close()
        except Exception:
            pass
    def should_force_fresh(self) -> bool:
        if not self.state.get("last_success", False): return True
        if self.state.get("failed_auth_count", 0) >= 2: return True
        if time.time() - self.state.get("last_login", 0) > 7 * 24 * 3600: return True
        return False
    def record_success(self, email: str, password: str = "", host: str = None):
        # Save credentials (email + password) and login state in app_data.db.
        # password defaults to whatever was already stored, so callers that
        # don't pass it explicitly won't wipe the saved value.
        update_dict = {
            "last_login": time.time(),
            "last_success": True,
            "failed_auth_count": 0,
            "email": email,
            "password": password or self.state.get("password", ""),
        }
        if host: update_dict["host"] = host
        self.state.update(update_dict)
        self._save_state()
    def record_failure(self, error: str):
        self.state["last_login"] = time.time()
        self.state["last_success"] = False
        self.state["failed_auth_count"] = self.state.get("failed_auth_count", 0) + 1
        self._save_state()
    def get_saved_email(self) -> str:
        email = self.state.get("email", "")
        return email if email else ""
    def get_saved_password(self) -> str:
        return self.state.get("password", "")
    def get_saved_host(self) -> str:
        return self.state.get("host", "qxbroker.com")
    @staticmethod
    def delete_session_file():
        # Clear the sessions table so the next login performs a fresh
        # authentication (no stale cookies/token). The credentials row in
        # app_state is intentionally preserved so the user doesn't have to
        # retype email/password.
        try:
            with _db_lock:
                conn = _db_conn()
                try:
                    conn.execute("DELETE FROM sessions")
                    conn.commit()
                    return True
                finally:
                    conn.close()
        except Exception:
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
SUBSECOND_MAX_CANDLES = 200  # keep last 200 subsecond candles in memory (rolling)
SUBSECOND_HISTORY_CANDLES = 500  # fetch up to 500 historical subsecond candles at startup (was 1000, reduced for speed)
# Semaphore to limit concurrent subsecond history fetches (3 at a time, not 41)
# Created lazily on first use to avoid event loop binding issues at import time
_SUBSECOND_FETCH_SEMAPHORE = None
# ===== FIX 4: 1000 ( ) =====
# 500 1000 (4s).
# : workers=5 + chunk=200 ( ) .
INITIAL_CANDLES = 1000
MIN_CANDLES_THRESHOLD = 100
HISTORY_DAYS = 0.75
FETCH_DURATION_SECONDS = int(86400 * HISTORY_DAYS)
STREAM_POLL_INTERVAL = 0.15
# ===== FIX 4: WRITE_INTERVAL = 0.5s 3.0s ( 500ms) =====
WRITE_INTERVAL = 0.5
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

# ===== FIX K: Quotex =====
# Domain list. Labels are intentionally NEUTRAL (no country/region labels) so
# no user feels singled out. Just the domain name as the broker publishes it.
DOMAINS = [
    ("qxbroker.com",    "qxbroker.com"),
    ("market-qx.info",  "market-qx.info"),
]
# — session_state
QX_HOST = "qxbroker.com"

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
                CONNECTION_ALIVE = False
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
            CONNECTION_ALIVE = False
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
                        if asset.write(): dirty_count += 1
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
                # FIX K: persist email + password + host in app_data.db so the
                # next launch can auto-login without re-prompting the user.
                session_manager.record_success(email, password=password, host=QX_HOST)
                return True
            else:
                error_msg = str(reason) if reason else "Unknown error"
                session_manager.record_failure(error_msg)
        except Exception as e:
            error_msg = str(e)[:200]
            session_manager.record_failure(error_msg)
            if attempt < max_attempts: await asyncio.sleep(5 * attempt)
    CONNECTION_ALIVE = False
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
                if LAST_CONNECTION_DROP_TIME == 0:
                    LAST_CONNECTION_DROP_TIME = time.time()
                    logmsg(f"[stale_watchdog] drop time recorded at {LAST_CONNECTION_DROP_TIME:.0f}")
                CONNECTION_ALIVE = False
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
            logmsg(f"[health_monitor] marking connection DEAD: {dead_reason}")
            CONNECTION_ALIVE = False
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
            # Prefer the in-memory PASSWORD global (always set after the first
            # successful connect_quotex call). If that's not available yet, fall
            # back to the password persisted in app_data.db so auto-reconnect can
            # still work after a fresh process start.
            password_for_reconnect = PASSWORD or session_manager.get_saved_password()
            # ===== FIX: try RECONNECTING =====
            # : `if not (email and PASSWORD): continue`
            # => try RECONNECTING = True =>
            # => !
            if not (email and password_for_reconnect):
                # RECONNECTING
                RECONNECTING = False
                continue
            delay = 0 if consecutive_failures == 0 else min(RECONNECT_BASE_DELAY * (2 ** (consecutive_failures - 1)), RECONNECT_MAX_DELAY)
            if delay > 0:
                logmsg(f"[reconnect] connection lost, retrying in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                logmsg("[reconnect] connection lost, reconnecting immediately...")
            # FIX K:
            _saved_host = session_manager.get_saved_host()
            if _saved_host and QX_HOST != _saved_host:
                QX_HOST = _saved_host
                logmsg(f"[reconnect] using saved host: {QX_HOST}")
            success = await connect_quotex(email, password_for_reconnect, force_fresh=True, max_attempts=1)
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
                    res_chunk = await asyncio.wait_for(
                        CLIENT.get_candles(api_name, chunk_end, chunk_seconds, fetch_period),
                        timeout=20,
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
                    bridge_1s = await asyncio.wait_for(
                        CLIENT.get_candles(
                            asset.api_symbol,
                            bridge_end_time,
                            bridge_1s_offset,
                            1  # period=1 (1s candles — مدعوم دائماً من الخادم)
                        ),
                        timeout=BRIDGE_FETCH_TIMEOUT,
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

async def fetch_subsecond_history(asset: Asset, idx=1, total=1):
    """Fetch historical subsecond candles by fetching 1s candles and aggregating.

    Strategy (per Quotex server limitations):
    1. Use `get_candles` (single request, NOT parallel get_historical_candles)
       with period=1 — server returns ~500 1s candles per request
    2. Make multiple staggered requests going backwards in time
    3. Stop when server returns 3 empty chunks in a row (hit history limit)
    4. Aggregate 1s candles locally into 5s/10s/15s/30s

    Uses a semaphore (3 concurrent) to avoid overwhelming server.
    """
    if CLIENT is None or not hasattr(CLIENT, 'get_candles'):
        logmsg(f"[subfetch:{asset.symbol}] CLIENT not ready")
        return []
    api_name = asset.api_symbol
    display_name = asset.symbol
    # Target: SUBSECOND_HISTORY_CANDLES aggregated candles
    # = SUBSECOND_HISTORY_CANDLES * SUBSECOND_SECONDS 1s candles
    # هامش 1.5x (بدل 2x) لتقليل وقت الجلب → تقليل الفجوة الزمنية بين التاريخي والبث
    target_1s_count = int(SUBSECOND_HISTORY_CANDLES * SUBSECOND_SECONDS * 1.5)
    chunk_seconds = 500  # ~500 1s candles per request (server limit)
    all_candles_1s = []
    current_end = time.time()
    # زيادة max_chunks من 20 → 40
    max_chunks = 40
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
                # Small delay between chunks to avoid server rate limiting
                await asyncio.sleep(0.03)
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
    logmsg(f"[subfetch:{display_name}] got {len(unique_1s)} 1s candles from {chunks_done} chunks, aggregating to {SUBSECOND_LABEL}")
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
    # Aggregate 1s candles into target subsecond timeframe
    aggregated = _aggregate_sub_minute(formatted_1s, SUBSECOND_SECONDS)
    # Limit to SUBSECOND_HISTORY_CANDLES
    result = aggregated[-SUBSECOND_HISTORY_CANDLES:]
    logmsg(f"[subfetch:{display_name}] DONE: {len(unique_1s)} 1s -> {len(result)} {SUBSECOND_LABEL} candles")
    return result

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
                        asset.candles.append({'time': aligned_time, 'open': price, 'high': price, 'low': price, 'close': price, 'volume': 1})
                    if len(asset.candles) > INITIAL_CANDLES: asset.candles = asset.candles[-INITIAL_CANDLES:]
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
        if len(state['candles']) > 1000:
            state['candles'] = state['candles'][-1000:]
        state['last_price'] = tick['price']
        now = time.time()
        if now - state['last_write'] > 0.2:
            self.write_to_file(asset, period, state['candles'])
            state['last_write'] = now

    def write_to_file(self, asset: str, period: int, candles: list):
        """ HST {asset}{period}.hst ( AUDJPY-OTC1.hst).
 
 Args:
 asset: derived_symbol ( "AUDJPY-OTC")
 period: MT4 timeframe (PERIOD=1 for M1)
 """
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
            candles = await client.get_candles(api_symbol, time.time(), offset_seconds, PERIOD_SECONDS)
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
        try:
            is_filled, _last_at = self.candle_store.is_gap_filled(derived_symbol)
            if is_filled:
                return    # frozen - keep candles exactly as they were
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
            candles = await client.get_candles(api_symbol, time.time(), int(small_days * 86400), PERIOD_SECONDS)
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
        GAP_FILL_ACTIVE = True  # FIX L10:
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
            # —
            GAP_FILL_SUMMARY = (
                f"GAP FILL c{cycle}: {i}/{total} done | {filled_count} filled | "
                f"{skipped_count} skipped | {failed_count} failed | {time.time()-t0:.1f}s"
            )
        else:
            # ( connection loss)
            elapsed = time.time() - t0
            fail_str = f" | Failed: {', '.join(failed_assets[:5])}" if failed_assets else ""
            GAP_FILL_SUMMARY = (
                f"GAP FILL c{cycle}: COMPLETE in {elapsed:.1f}s | {filled_count}/{total} filled | "
                f"{skipped_count} skipped{fail_str} | next in {GAP_FILL_REFRESH_INTERVAL}s"
            )
            GAP_FILL_ACTIVE = False
            # (5 )
            await asyncio.sleep(GAP_FILL_REFRESH_INTERVAL)
            # ( / )
            total = len(ALL_STREAMING_ASSETS)
            continue
        # connection loss —
        GAP_FILL_ACTIVE = False
        await asyncio.sleep(GAP_FILL_REFRESH_INTERVAL)
        total = len(ALL_STREAMING_ASSETS)

def print_dashboard():
    _tf_label = "Unknown"
    for tf_tuple in TIMEFRAMES:
        mt4_p, secs, label = tf_tuple[0], tf_tuple[1], tf_tuple[2]
        if mt4_p == PERIOD and secs == PERIOD_SECONDS:
            _tf_label = label
            break
    # تبسيط العنوان: سطر واحد فاصل بدل 3 خطوط زرقاء كثيفة
    print(f"  {Colors.DIM}{'─'*68}{Colors.RESET}")
    print(f"  {Colors.BOLD}QXChartMT4 Pro - v8.0  {Colors.DIM}|  @qxzero1  |  2026{Colors.RESET}")
    print(f"  {Colors.DIM}{'─'*68}{Colors.RESET}")
    print(f"  {Colors.CYAN}Timeframe  {Colors.RESET}: {_tf_label} ({PERIOD_SECONDS}s)")
    print(f"  {Colors.CYAN}History    {Colors.RESET}: {HISTORY_DAYS:.2f} day = {INITIAL_CANDLES} candles")
    # FIX L11: TZ offset display
    _tz_sec = _get_tz_offset()
    _tz_sign = '+' if _tz_sec >= 0 else '-'
    _tz_h, _tz_m = divmod(abs(_tz_sec) // 60, 60)
    _tz_src = "manual" if LOCAL_TZ_OFFSET_SECONDS is not None else "system"
    print(f"  {Colors.CYAN}TZ offset  {Colors.RESET}: UTC{_tz_sign}{_tz_h:02d}:{_tz_m:02d} (source={_tz_src})")
    print(f"  {Colors.CYAN}Gap fill   {Colors.RESET}: {GAP_FILL_CANDLES} candles / {GAP_FILL_REFRESH_INTERVAL}s")
    print(f"  {Colors.GREEN}Contact    {Colors.RESET}: https://t.me/qxchart")
    print(f"  {Colors.DIM}{'─'*68}{Colors.RESET}\n")

if __name__ == "__main__":
    # ════════════════════════════════════════════════════════════════════
    # STAGE 1: STARTUP — شعار QXMT4 + التحقق من الترخيص
    # ════════════════════════════════════════════════════════════════════
    # Top-level safety net: any UnicodeError that escapes qx_run_startup
    # (or any later stage) gets logged once and we exit cleanly instead
    # of leaving an unhandled-exception traceback that sys.excepthook
    # would also turn into a process exit.
    try:
        license_result = qx_run_startup()
    except UnicodeError as _ue:
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            safe = str(_ue).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            print(f"  \033[93m[{ts}] Top-level UnicodeError caught: {safe}\033[0m")
            print(f"  \033[93mContinuing as if no saved license. Please enter a license key manually.\033[0m")
            _log_to_file(f"[{ts}] Top-level UnicodeError caught in __main__: {safe}")
        except Exception:
            pass
        license_result = None
    if license_result is None:
        # المستخدم خرج قبل إدخال ترخيص صالح
        sys.exit(0)
    # نقطة التكامل: الترخيص مُفعّل، نُكمل إلى قوائم الفريمات/التاريخ/الدومين
    # ════════════════════════════════════════════════════════════════════

    # ════════════════════════════════════════════════════════════════════
    # STAGE 2: Select Timeframe — 3 أعمدة × 5 صفوف (بدون خطوط زرقاء كثيرة)
    # ════════════════════════════════════════════════════════════════════
    # ترتيب الفريمات حسب الطلب:
    # العمود الأول (1-5): M1, M2, M3, M5, M10
    # العمود الثاني (6-10): M15, M30, H1, H4, D1
    # العمود الثالث (11-14): S5, S10, S15, S30
    _TF_DISPLAY_ORDER = [
        # (idx, mt4_period, seconds, short_label, full_label)
        (1,  1,    60,    "M1",  "1 minute"),
        (2,  2,    120,   "M2",  "2 minutes"),
        (3,  3,    180,   "M3",  "3 minutes"),
        (4,  5,    300,   "M5",  "5 minutes"),
        (5,  10,   600,   "M10", "10 minutes"),
        (6,  15,   900,   "M15", "15 minutes"),
        (7,  30,   1800,  "M30", "30 minutes"),
        (8,  60,   3600,  "H1",  "1 hour"),
        (9,  240,  14400, "H4",  "4 hours"),
        (10, 1440, 86400, "D1",  "1 day"),
        (11, 1,    5,     "S5",  "5 seconds"),
        (12, 1,    10,    "S10", "10 seconds"),
        (13, 1,    15,    "S15", "15 seconds"),
        (14, 1,    30,    "S30", "30 seconds"),
    ]
    # خريطة (idx → is_subsecond)
    _TF_SUBSEC = {11: True, 12: True, 13: True, 14: True}

    print()
    print(f"{Colors.BOLD}  Select Timeframe{Colors.RESET}")
    print(f"  {Colors.DIM}{'═' * 55}{Colors.RESET}")
    # عرض القائمة في 3 أعمدة × 5 صفوف
    # صف 0: idx 1,6,11 | صف 1: 2,7,12 | صف 2: 3,8,13 | صف 3: 4,9,14 | صف 4: 5,10,—
    _ROWS = [
        (1, 6, 11),   # M1   M15   S5
        (2, 7, 12),   # M2   M30   S10
        (3, 8, 13),   # M3   H1    S15
        (4, 9, 14),   # M5   H4    S30
        (5, 10, None),# M10  D1    —
    ]
    _tf_lookup = {row[0]: row for row in _TF_DISPLAY_ORDER}
    # ثوابت المحاذاة: كل عمود 17 حرف ظاهر، فجوة 2 حرف بين الأعمدة
    # → كل صف = 2 (indent) + 17*3 + 2*2 = 57 حرف (مطابق لخط ═ 55 + 2 indent)
    # الصيغة: "XX - XXXXX - XXX" = 2 + 3 + 5 + 3 + 4 = 17 حرف ظاهر لكل خلية
    _TF_COL_WIDTH = 17
    _TF_GAP = "  "  # فجوة صغيرة بين الأعمدة (قرّب الأعمدة من بعضها)
    for row in _ROWS:
        cells = []
        for idx in row:
            if idx is None:
                # ملء بمسافات بنفس عرض العمود (يحافظ على تساوي طول الصف)
                cells.append(" " * _TF_COL_WIDTH)
                continue
            entry = _tf_lookup[idx]
            sec = entry[2]      # seconds (int)
            label = entry[3]    # short_label (M1, S30, ...)
            # التنسيق: idx(يمين 2) + " - " + sec(يسار 5) + " - " + label(يسار 4) = 17 حرف
            # Cyan = لون الشعار (بدل Yellow)
            cells.append(f"{Colors.CYAN}{idx:>2}{Colors.RESET} - {sec:<5} - {label:<4}")
        print(f"  {cells[0]}{_TF_GAP}{cells[1]}{_TF_GAP}{cells[2]}")
    print(f"  {Colors.DIM}{'═' * 55}{Colors.RESET}")
    while True:
        try:
            tf_choice = input(f"{Colors.CYAN}  Choose 1-14 (default=1 for M1): {Colors.RESET}").strip()
            if not tf_choice:
                _chosen_idx = 1
            else:
                _chosen_idx = int(tf_choice)
                if not (1 <= _chosen_idx <= 14):
                    print(f"{Colors.RED}  Invalid choice (1-14).{Colors.RESET}")
                    continue
            break
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.RED}  Invalid input.{Colors.RESET}")
        except EOFError:
            _chosen_idx = 1
            break
    _tf_entry = _tf_lookup[_chosen_idx]
    PERIOD, PERIOD_SECONDS = _tf_entry[1], _tf_entry[2]
    _tf_short = _tf_entry[2]
    _tf_full = _tf_entry[3]
    _is_subsecond = _TF_SUBSEC.get(_chosen_idx, False)
    globals()['PERIOD'] = PERIOD
    globals()['PERIOD_SECONDS'] = PERIOD_SECONDS
    if PERIOD_SECONDS < 60:
        globals()['IS_SUBSECOND'] = True
        globals()['SUBSECOND_SECONDS'] = PERIOD_SECONDS
        _subsec_label = f"{PERIOD_SECONDS}S"
        globals()['SUBSECOND_LABEL'] = _subsec_label
        print(f"{Colors.GREEN}  Using timeframe: {_tf_short} - {_tf_full}{Colors.RESET}")
        print(f"{Colors.DIM}  Sub-minute: fetches period=1 history + aggregates locally{Colors.RESET}\n")
    else:
        globals()['IS_SUBSECOND'] = False
        globals()['SUBSECOND_SECONDS'] = 0
        globals()['SUBSECOND_LABEL'] = ""
        print(f"{Colors.GREEN}  Using timeframe: {_tf_short} - {_tf_full}{Colors.RESET}\n")

    # ════════════════════════════════════════════════════════════════════
    # STAGE 3: Select History Size
    # للفريمات الفرعية (subsecond) نستخدم قيمة ثابتة ولا نسأل المستخدم
    # لأن النظام يجلب period=1 ويُجمّع محلياً — عدد الأيام غير ذي معنى هنا
    # ════════════════════════════════════════════════════════════════════
    if PERIOD_SECONDS < 60:
        # الفريمات الفرعية (5S/10S/15S/30S): قيمة ثابتة بدون سؤال
        INITIAL_CANDLES = SUBSECOND_HISTORY_CANDLES
        HISTORY_DAYS = (INITIAL_CANDLES * PERIOD_SECONDS) / 86400.0 * 1.15
        FETCH_DURATION_SECONDS = int(86400 * HISTORY_DAYS)
        globals()['INITIAL_CANDLES'] = INITIAL_CANDLES
        globals()['HISTORY_DAYS'] = HISTORY_DAYS
        globals()['FETCH_DURATION_SECONDS'] = FETCH_DURATION_SECONDS
        # رسالة قصيرة بدل قائمة كاملة
        print(f"{Colors.DIM}  Sub-second timeframe: auto history ({INITIAL_CANDLES} candles, {HISTORY_DAYS:.2f} days){Colors.RESET}\n")
    else:
        # الفريمات 60s+: نسأل المستخدم عن عدد الأيام
        _default_days = (1000 * PERIOD_SECONDS) / 86400.0 * 1.15  # +15% margin
        print(f"{Colors.BOLD}  Select History Size{Colors.RESET}")
        print(f"  {Colors.DIM}Default: 1000 candles ({_default_days:.2f} days). Or enter days manually.{Colors.RESET}")
        while True:
            try:
                days_input = input(f"{Colors.CYAN}  Days (default={_default_days:.2f}): {Colors.RESET}").strip()
                if not days_input:
                    INITIAL_CANDLES = 1000
                    HISTORY_DAYS = _default_days
                else:
                    days_val = float(days_input)
                    if days_val <= 0:
                        print(f"{Colors.RED}  Must be positive.{Colors.RESET}")
                        continue
                    HISTORY_DAYS = days_val * 1.15
                    INITIAL_CANDLES = max(int((days_val * 86400) / PERIOD_SECONDS), 100)
                FETCH_DURATION_SECONDS = int(86400 * HISTORY_DAYS)
                globals()['INITIAL_CANDLES'] = INITIAL_CANDLES
                globals()['HISTORY_DAYS'] = HISTORY_DAYS
                globals()['FETCH_DURATION_SECONDS'] = FETCH_DURATION_SECONDS
                break
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}  Invalid input.{Colors.RESET}")
            except EOFError:
                INITIAL_CANDLES = 1000
                HISTORY_DAYS = _default_days
                FETCH_DURATION_SECONDS = int(86400 * HISTORY_DAYS)
                globals()['INITIAL_CANDLES'] = INITIAL_CANDLES
                globals()['HISTORY_DAYS'] = HISTORY_DAYS
                globals()['FETCH_DURATION_SECONDS'] = FETCH_DURATION_SECONDS
                break
        print(f"{Colors.GREEN}  Using history: {HISTORY_DAYS:.2f} days = {INITIAL_CANDLES} candles{Colors.RESET}\n")

    # (تم حذف كتلة Dashboard بناءً على طلب المستخدم — الترحيب + القوائم كافية)

    # ════════════════════════════════════════════════════════════════════
    # STAGE 4: Select Domain — عنوان + قائمة مختصرة + سطر إدخال
    # ════════════════════════════════════════════════════════════════════
    saved_host = session_manager.get_saved_host()
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
    print(f"{Colors.GREEN}  Using domain: {QX_HOST}{Colors.RESET}\n")

    # ════════════════════════════════════════════════════════════════════
    # STAGE 5: تسجيل دخول Quotex
    # ════════════════════════════════════════════════════════════════════
    # Wipe the sessions table on every launch so the app always starts from a
    # clean state — no stale cookies/token from a previous run. The saved
    # credentials (email + password) live in app_state, which is intentionally
    # preserved so the user does not have to retype them.
    session_manager.delete_session_file()
    session_manager.delete_browser_dir()
    should_force = session_manager.should_force_fresh()
    saved_email = session_manager.get_saved_email()
    saved_password = session_manager.get_saved_password()
    success = False
    # Case 1: both email and password are saved AND the previous login was
    # healthy (not too old, not too many failed attempts) → auto-login with
    # force_fresh=True (the sessions table is already empty).
    if saved_email and saved_password and not should_force:
        print(f"{Colors.GREEN}Found saved credentials: {saved_email}{Colors.RESET}")
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(saved_email, saved_password, force_fresh=True, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=180)
    # Case 2: saved email only (no password on file) → ask for the password.
    if not success and saved_email and not should_force:
        print(f"{Colors.GREEN}Found saved email: {saved_email}{Colors.RESET}")
        PASSWORD_INPUT = input(f"{Colors.CYAN} Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(saved_email, PASSWORD_INPUT, force_fresh=True, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=180)
    # Case 3: no usable saved credentials → prompt for both email and password.
    if not success:
        print()
        EMAIL_INPUT = input(f"{Colors.CYAN}Email: {Colors.RESET}").strip()
        PASSWORD_INPUT = input(f"{Colors.CYAN}Password: {Colors.RESET}").strip()
        fut = asyncio.run_coroutine_threadsafe(connect_quotex(EMAIL_INPUT, PASSWORD_INPUT, force_fresh=True, max_attempts=3), ASYNC_LOOP)
        success = fut.result(timeout=300)
    if not success:
        print(f"\n{Colors.RED}[FAILED] Could not connect after all attempts.{Colors.RESET}")
        sys.exit(1)
        
    # (FIX D) "Connected successfully!" —
    if WINAPI_AVAILABLE:
        time.sleep(1)
        find_mt4_window()

    # (FIX D) HST —
    try:
        os.makedirs(MT4_HISTORY_PATH, exist_ok=True)
    except Exception:
        pass

    total_assets = len(ASSET_LIST)
    # ===== FIX 8: 1 — =====
    print(f"\n{Colors.CYAN}{'═'*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  SECTION 1: CANDLE FETCHING ({total_assets} assets, {INITIAL_CANDLES} candles each){Colors.RESET}")
    print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}\n")

    all_assets = []
    total_loaded = 0
    consecutive_disconnects = 0
    for idx, symbol in enumerate(ASSET_LIST, 1):
        # ===== FIX 3: =====
        # auto_reconnect .
        # ASYNC_LOOP run_coroutine_threadsafe
        # main async.
        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            logmsg(f"[fetch_loop] connection dead before asset {idx}/{total_assets}; waiting for reconnect...")
            async def _wait_reconnect(timeout=30.0):
                try:
                    await wait_until(
                        lambda: CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None,
                        timeout=timeout,
                        poll_interval=0.5,
                    )
                    return True
                except asyncio.TimeoutError:
                    return False
            reconnected = asyncio.run_coroutine_threadsafe(_wait_reconnect(30.0), ASYNC_LOOP).result(timeout=35)
            if reconnected:
                consecutive_disconnects = 0
            else:
                consecutive_disconnects += 1
                logmsg(f"[fetch_loop] reconnect failed within 30s (streak={consecutive_disconnects})")
                if consecutive_disconnects >= MAX_RECONNECTS_DURING_FETCH:
                    logmsg(f"[fetch_loop] giving up after {consecutive_disconnects} failed reconnects")
                    break
                continue
        asset = Asset(symbol)
        display = pretty_asset_name(symbol)
        all_assets.append(asset)
        ALL_STREAMING_ASSETS.append(asset)
        start_time = time.time()
        # Use 1.0s delay between assets for sub-minute (server sensitive to period=1)
        # 0.1s for 60s+ timeframes (normal speed)
        _asset_delay = 1.0 if PERIOD_SECONDS < 60 else FETCH_ASSET_DELAY
        # Start realtime_stream FIRST (before historical fetch)
        # This way the stream collects live ticks DURING the fetch, closing the gap
        # between historical last candle and live first candle
        asset.stream_task = asyncio.run_coroutine_threadsafe(realtime_stream(asset), ASYNC_LOOP)
        # Small delay to let stream subscribe before fetch
        time.sleep(0.1)
        # Now fetch historical candles (stream is collecting live ticks in parallel)
        fut = asyncio.run_coroutine_threadsafe(fetch_candles_with_retry(asset, max_retries=MAX_FETCH_RETRIES, idx=idx, total=total_assets), ASYNC_LOOP)
        try:
            candles_count, attempts = fut.result(timeout=180)
            elapsed = time.time() - start_time
            if candles_count >= MIN_CANDLES_THRESHOLD:
                total_loaded += candles_count
                consecutive_disconnects = 0
                attempts_str = "" if attempts == 1 else f" ({attempts} attempts)"
                print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.GREEN}{candles_count} candles in {elapsed:.1f}s{attempts_str}{Colors.RESET} Streaming")
            else:
                print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.RED}Only {candles_count} candles{Colors.RESET} Streaming")
        except Exception as e:
            print(f"\r{Colors.CLEAR_LINE}  {Colors.CYAN}{display:<25}{Colors.RESET} {Colors.RED}Error: {str(e)[:30]}{Colors.RESET}")
            if "Connection" in str(e) or "closed" in str(e).lower():
                consecutive_disconnects += 1
                if consecutive_disconnects >= MAX_RECONNECTS_DURING_FETCH:
                    logmsg(f"[fetch_loop] too many disconnects ({consecutive_disconnects}); aborting fetch")
                    break
        # Merge: any live ticks collected during fetch are already in asset.candles
        # fetch_candles_with_retry overwrites asset.candles with historical only.
        # To preserve live ticks, merge them back after fetch.
        # (handled inside realtime_stream which appends to asset.candles)
        # ===== FIX 7: cooldown — =====
        # . keepalive_loop .
        if FETCH_COOLDOWN_EVERY > 0 and idx > 0 and idx % FETCH_COOLDOWN_EVERY == 0 and idx < total_assets:
            logmsg(f"[fetch_loop] cooldown {FETCH_COOLDOWN_DURATION}s after {idx}/{total_assets} assets")
            time.sleep(FETCH_COOLDOWN_DURATION)
        else:
            # Use 1.0s for sub-minute (server sensitive to period=1), 0.1s for 60s+
            time.sleep(_asset_delay)

    # NOTE: gap filler runs automatically on its interval (every GAP_FILL_REFRESH_INTERVAL).
    # First cycle waits 60s, then runs periodically. Not forced at startup.
    # Gap fill respects the user's chosen timeframe via dynamic _align_time/_fill_missing_slots.

    asyncio.run_coroutine_threadsafe(health_monitor(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(auto_reconnect(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(keepalive_loop(), ASYNC_LOOP)
    asyncio.run_coroutine_threadsafe(stale_message_watchdog(), ASYNC_LOOP)
    # start the automatic gap filler loop (runs every GAP_FILL_REFRESH_INTERVAL)
    asyncio.run_coroutine_threadsafe(mt4_gap_filler(), ASYNC_LOOP)
    
    # ===== FIX 8: dashboard — 3 =====
    # 1: ( )
    # 2: ( status line )
    # 3: ( mt4_gap_filler)
    print(f"\n{Colors.GREEN}{'═'*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  All assets loaded and streaming!{Colors.RESET}")
    print(f"  Total: {total_loaded} candles for {len(all_assets)} assets")
    print(f"  History window: {HISTORY_DAYS} day (optimized, fast fetch)")
    print(f"  Writer Thread: ACTIVE (every {WRITE_INTERVAL}s)")
    print(f"  Refresh: BATCHED (every {REFRESH_INTERVAL}s)")
    print(f"  Stream Poll: {STREAM_POLL_INTERVAL}s")
    print(f"  Health Monitor: ACTIVE (Lenient: ignores websocket flickers)")
    print(f"  Keepalive Ping: ACTIVE (every {KEEPALIVE_PING_INTERVAL}s, multi-type)")
    print(f"  Stale Watchdog: ACTIVE (recycles if silent > {STALE_MESSAGE_TIMEOUT}s)")
    print(f"  Auto-Reconnect: instant detect + exponential backoff (never gives up)")
    print(f"  Internal Watchdog: ACTIVE (recycles stale connections > 90s)")
    print(f"  Fetch: {FETCH_MAX_WORKERS} workers, {FETCH_CHUNK_SIZE}c/batch, {FETCH_BATCH_DELAY}s delay, {FETCH_ASSET_DELAY}s between assets")
    print(f"  Retry: {MAX_FETCH_RETRIES} attempts, backoff {RETRY_BACKOFF_BASE}-{RETRY_BACKOFF_MAX}s")
    print(f"{Colors.GREEN}{'═'*60}{Colors.RESET}\n")

    # ===== FIX E/F/G: — =====
    # FIX E: ( 6)
    # FIX F: ( print() )
    # FIX G: ( / ) +
    # FIX H: (columns/rows) —

    import shutil as _shutil
    def _get_term_size():
        try:
            s = _shutil.get_terminal_size((80, 24))
            return s.columns, s.lines
        except Exception:
            return 80, 24

    def _fmt_price(p):
        if p <= 0: return "—"
        if p >= 1000: return f"{p:.3f}"
        if p >= 100:  return f"{p:.3f}"
        if p >= 1:    return f"{p:.5f}"
        return f"{p:.5f}"

    def _draw_live_table(first_draw=False):
        cols, rows = _get_term_size()
        # ===== FIX H: — =====
        # : 25 chars (name=12 + price=10 + )
        # : 50 chars (name=25 + price=15 + status=8 + )
        cols = max(25, cols)
        if cols >= 55:
            name_w, price_w = 25, 15
            show_status = True
        elif cols >= 40:
            name_w, price_w = 20, 12
            show_status = True
        elif cols >= 30:
            name_w, price_w = 15, 10
            show_status = False
        else:
            name_w, price_w = 12, 8
            show_status = False
        bar_w = max(20, min(70, cols - 2))
        # ( )
        header_lines = 3
        data_lines = len(all_assets) + 1  # +1
        gap_lines = 0
        if GAP_FILL_SUMMARY:
            gap_lines = 3  # ===, summary, ===
        # status messages lines (queued log messages)
        msg_lines_count = min(len(_STATUS_MESSAGES_QUEUE), 3)
        msg_lines = msg_lines_count + (1 if msg_lines_count > 0 else 0)  # +1 for separator
        total_lines = header_lines + data_lines + gap_lines + msg_lines
        if not first_draw:
            sys.stdout.write(f"\033[{total_lines}A")
        # ===== =====
        sys.stdout.write(f"\033[2K{Colors.CYAN}{'═'*bar_w}{Colors.RESET}\n")
        sys.stdout.write(f"\033[2K{Colors.BOLD}  LIVE PRICES{Colors.RESET}\n")
        sys.stdout.write(f"\033[2K{Colors.CYAN}{'═'*bar_w}{Colors.RESET}\n")
        # ===== =====
        for asset in all_assets:
            display = pretty_asset_name(asset.api_symbol)
            # name_w
            if len(display) > name_w:
                display = display[:name_w-1] + "~"
            # FIX G:
            name_visible = f"{display:<{name_w}}"
            name_colored = f"{Colors.BLUE}{name_visible}{Colors.RESET}"
            # FIX G: ( / )
            price_str = _fmt_price(asset.price)
            if asset.previous_price > 0 and asset.price > 0:
                if asset.price > asset.previous_price:
                    price_colored = f"{Colors.GREEN}{price_str:<{price_w}}{Colors.RESET}"
                elif asset.price < asset.previous_price:
                    price_colored = f"{Colors.RED}{price_str:<{price_w}}{Colors.RESET}"
                else:
                    price_colored = f"{price_str:<{price_w}}"
            else:
                price_colored = f"{price_str:<{price_w}}"

            if show_status:
                if asset.updates > 0:
                    status_str = f"{Colors.GREEN}LIVE{Colors.RESET}"
                else:
                    status_str = f"{Colors.RED}WAIT{Colors.RESET}"
                sys.stdout.write(f"\033[2K  {name_colored} {price_colored} {status_str}\n")
            else:
                sys.stdout.write(f"\033[2K  {name_colored} {price_colored}\n")

        if CONNECTION_ALIVE:
            conn_status = f"{Colors.GREEN}CONNECTED{Colors.RESET}"
        else:
            conn_status = f"{Colors.RED}RECONNECTING...{Colors.RESET}"
        if show_status:
            sys.stdout.write(f"\033[2K  {Colors.BLUE}{'Connection':<{name_w}}{Colors.RESET} {'':<{price_w}} {conn_status}\n")
        else:
            sys.stdout.write(f"\033[2K  {Colors.BLUE}{'Connection':<{name_w}}{Colors.RESET} {conn_status}\n")
        # ===== FIX F: ( ) =====
        if GAP_FILL_SUMMARY:
            summary = GAP_FILL_SUMMARY
            # bar_w-4
            max_len = bar_w - 4
            if len(summary) > max_len:
                summary = summary[:max_len-3] + "..."
            # :
            if "ABORTED" in GAP_FILL_SUMMARY or "Failed:" in GAP_FILL_SUMMARY and "0 failed" not in GAP_FILL_SUMMARY:
                summary_colored = f"{Colors.RED}{summary}{Colors.RESET}"
            elif "COMPLETE" in GAP_FILL_SUMMARY:
                summary_colored = f"{Colors.GREEN}{summary}{Colors.RESET}"
            elif GAP_FILL_ACTIVE:
                summary_colored = f"{Colors.CYAN}{summary}{Colors.RESET}"
            else:
                summary_colored = summary
            sys.stdout.write(f"\033[2K{Colors.CYAN}{'═'*bar_w}{Colors.RESET}\n")
            sys.stdout.write(f"\033[2K  {summary_colored}\n")
            sys.stdout.write(f"\033[2K{Colors.CYAN}{'═'*bar_w}{Colors.RESET}\n")
        # Display queued log messages (last 3)
        if _STATUS_MESSAGES_QUEUE:
            sys.stdout.write(f"\033[2K{Colors.DIM}{'─'*bar_w}{Colors.RESET}\n")
            for msg in _STATUS_MESSAGES_QUEUE[-3:]:
                # truncate to bar_w-4
                if len(msg) > bar_w - 4:
                    msg = msg[:bar_w-7] + "..."
                sys.stdout.write(f"\033[2K  {Colors.DIM}{msg}{Colors.RESET}\n")
        sys.stdout.flush()

    # Initial draw
    _draw_live_table(first_draw=True)
    print()
    print(f"{Colors.CYAN}Live streaming active. Press Enter for menu, Ctrl+C to stop.{Colors.RESET}")
    print()

    # Interactive menu state
    stop_requested = False
    reinit_requested = False
    _enter_pressed = threading.Event()

    def _stdin_listener():
        while not stop_requested and not reinit_requested:
            try:
                line = sys.stdin.readline()
                if line == '' or line is None:
                    time.sleep(0.5)
                    continue
                _enter_pressed.set()
                while _enter_pressed.is_set() and not stop_requested and not reinit_requested:
                    time.sleep(0.1)
            except (KeyboardInterrupt, EOFError):
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)

    _stdin_thread = threading.Thread(target=_stdin_listener, daemon=True, name="StdinListener")
    _stdin_thread.start()

    def _show_interactive_menu():
        print()
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        print(f"{Colors.BOLD}  MENU{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        print(f"  {Colors.CYAN}1{Colors.RESET} - Change Timeframe (current: {_current_period_label()})")
        print(f"  {Colors.CYAN}2{Colors.RESET} - Change History days (current: {HISTORY_DAYS:.2f}d = {INITIAL_CANDLES} candles)")
        print(f"  {Colors.CYAN}3{Colors.RESET} - Change both timeframe and history days")
        print(f"  {Colors.CYAN}4{Colors.RESET} - Resume streaming (continue)")
        print(f"  {Colors.CYAN}5{Colors.RESET} - Exit program")
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        while True:
            try:
                c = input(f"{Colors.CYAN}Choose 1-5: {Colors.RESET}").strip()
                if c in ('1', '2', '3', '4', '5'):
                    return int(c)
                print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}Invalid input.{Colors.RESET}")
            except EOFError:
                return 4

    def _choose_timeframe():
        # نفس تنسيق القائمة الأولية: 3 أعمدة × 5 صفوف
        # The cell layout must match Stage 2 exactly: "XX - SSSSS - LLLL" (17 chars).
        # The current item is highlighted in GREEN instead of an inline asterisk,
        # so column widths stay perfectly aligned with the initial menu.
        print()
        print(f"{Colors.BOLD}  Select Timeframe{Colors.RESET}")
        print(f"  {Colors.DIM}{'═' * 55}{Colors.RESET}")
        _ROWS_LOCAL = [
            (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14), (5, 10, None),
        ]
        _TF_COL_WIDTH = 17
        _TF_GAP = "  "
        for row in _ROWS_LOCAL:
            cells = []
            for idx in row:
                if idx is None:
                    cells.append(" " * _TF_COL_WIDTH)
                    continue
                tf_tuple = TIMEFRAMES[idx - 1]
                mt4_p = tf_tuple[0]
                secs = tf_tuple[1]
                full_label = tf_tuple[2]            # e.g. "M1  - 1 minute"
                short_label = full_label.split()[0]   # e.g. "M1"
                is_current = (mt4_p == PERIOD and secs == PERIOD_SECONDS)
                cell_color = Colors.GREEN if is_current else Colors.CYAN
                # Identical layout to Stage 2: "XX - SSSSS - LLLL" = 17 visible chars
                cells.append(f"{cell_color}{idx:>2}{Colors.RESET} - {secs:<5} - {short_label:<4}")
            print(f"  {cells[0]}{_TF_GAP}{cells[1]}{_TF_GAP}{cells[2]}")
        print(f"  {Colors.DIM}{'═' * 55}{Colors.RESET}")
        print(f"  {Colors.DIM}(green = current){Colors.RESET}")
        while True:
            try:
                tf_choice = input(f"{Colors.CYAN}  Choose 1-14 (default=1 for M1): {Colors.RESET}").strip()
                if not tf_choice:
                    return TIMEFRAMES[0]
                tf_idx = int(tf_choice) - 1
                if 0 <= tf_idx < len(TIMEFRAMES):
                    return TIMEFRAMES[tf_idx]
                print(f"{Colors.RED}  Invalid choice (1-14).{Colors.RESET}")
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}  Invalid input.{Colors.RESET}")
            except EOFError:
                return TIMEFRAMES[0]

    def _choose_history_days():
        # للفريمات الفرعية: لا نسأل، نُرجع قيمة ثابتة (نفس سلوك Initial Setup)
        if PERIOD_SECONDS < 60:
            _auto_days = (SUBSECOND_HISTORY_CANDLES * PERIOD_SECONDS) / 86400.0 * 1.15
            print(f"{Colors.DIM}  Sub-second timeframe: auto history ({SUBSECOND_HISTORY_CANDLES} candles){Colors.RESET}")
            return _auto_days, SUBSECOND_HISTORY_CANDLES
        # للفريمات 60s+: نسأل المستخدم
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        print(f"{Colors.BOLD}  Select History Size:{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        _default_days_local = (1000 * PERIOD_SECONDS) / 86400.0 * 1.15  # +15% margin
        print(f"  {Colors.CYAN}Enter number of days (e.g., 1, 2, 3, 4...)")
        print(f"   Or press Enter for default 1000 candles ({_default_days_local:.2f} days){Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*70}{Colors.RESET}")
        while True:
            try:
                days_input = input(f"{Colors.CYAN}Days: {Colors.RESET}").strip()
                if not days_input:
                    return _default_days_local, 1000
                days_val = float(days_input)
                if days_val <= 0:
                    print(f"{Colors.RED}Must be positive.{Colors.RESET}")
                    continue
                # Apply 15% margin to user-specified days too
                days_with_margin = days_val * 1.15
                candles = max(int((days_val * 86400) / PERIOD_SECONDS), 100)
                return days_with_margin, candles
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}Invalid input.{Colors.RESET}")
            except EOFError:
                return _default_days_local, 1000

    # status update loop with interactive menu support
    while not stop_requested:
        try:
            while True:
                if _enter_pressed.is_set() or stop_requested or reinit_requested:
                    break
                _draw_live_table(first_draw=False)
                time.sleep(STATUS_REFRESH_INTERVAL)
            if stop_requested:
                break
            if reinit_requested:
                break
            action = _show_interactive_menu()
            _enter_pressed.clear()
            if action == 4:
                _draw_live_table(first_draw=True)
                continue
            elif action == 5:
                stop_requested = True
                break
            elif action in (1, 2, 3):
                new_period = PERIOD
                new_period_seconds = PERIOD_SECONDS
                if action in (1, 3):
                    _new_tf = _choose_timeframe()
                    new_period = _new_tf[0]
                    new_period_seconds = _new_tf[1]
                new_days = HISTORY_DAYS
                new_candles = INITIAL_CANDLES
                # للفريمات الفرعية: _choose_history_days يُرجع قيمة ثابتة تلقائياً
                # للفريمات 60s+: يسأل المستخدم
                if action in (2, 3):
                    new_days, new_candles = _choose_history_days()
                # Update globals BEFORE the live re-fetch — refetch_all_candles()
                # reads IS_SUBSECOND / SUBSECOND_SECONDS to decide which stream
                # function (subsecond_stream vs realtime_stream) to restart.
                globals()['PERIOD'] = new_period
                globals()['PERIOD_SECONDS'] = new_period_seconds
                if new_period_seconds < 60:
                    globals()['IS_SUBSECOND'] = True
                    globals()['SUBSECOND_SECONDS'] = new_period_seconds
                    globals()['SUBSECOND_LABEL'] = f"{new_period_seconds}S"
                else:
                    globals()['IS_SUBSECOND'] = False
                    globals()['SUBSECOND_SECONDS'] = 0
                    globals()['SUBSECOND_LABEL'] = ""
                globals()['HISTORY_DAYS'] = new_days
                globals()['INITIAL_CANDLES'] = new_candles
                globals()['FETCH_DURATION_SECONDS'] = int(86400 * new_days) if new_days > 0 else 0
                print(f"\n{Colors.GREEN}Switching to {_current_period_label()}, {new_days:.2f} days = {new_candles} candles...{Colors.RESET}")
                # ===== LIVE SWITCH (no restart) =====
                # Instead of os.execv() (which kills the process and forces the
                # user to re-enter license / timeframe / domain / login), we
                # stop the existing streams, clear the candles for every asset,
                # re-fetch with the new timeframe and restart the streams —
                # all in-place. The status loop simply continues afterwards.
                if not (CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None):
                    print(f"{Colors.YELLOW}  Connection is currently down — waiting for auto-reconnect to apply the new timeframe.{Colors.RESET}")
                    # The auto_reconnect loop will pick up the new globals on
                    # its next iteration and re-fetch with the new timeframe.
                else:
                    try:
                        print(f"{Colors.DIM}  Re-fetching all assets live (no restart)...{Colors.RESET}")
                        refetch_fut = asyncio.run_coroutine_threadsafe(refetch_all_candles(), ASYNC_LOOP)
                        refetch_fut.result(timeout=900)  # up to 15 minutes for 41 assets
                    except Exception as e:
                        print(f"{Colors.RED}  Live re-fetch error: {e}{Colors.RESET}")
                _enter_pressed.clear()
                _draw_live_table(first_draw=True)
                continue
        except KeyboardInterrupt:
            stop_requested = True
            break
        except Exception as e:
            log_exception("main status loop", e)
            try:
                print(f"\n{Colors.CYAN}[main loop] recovered from error: {e}{Colors.RESET}", flush=True)
            except Exception:
                pass
            time.sleep(1)

    # If reinit was requested: نُعيد تشغيل البرنامج بشكل نظيف
    # ملاحظة: هذا إعادة بناء كاملة (full re-init) لكنها أسرع من إغلاق الترمنال
    # لأن البرنامج يبدأ مباشرة من نقطة الترخيص المحفوظ (لا يسأل المستخدم ثانية)
    if reinit_requested:
        print(f"\n{Colors.CYAN}Applying new timeframe settings...{Colors.RESET}")
        print(f"{Colors.DIM}  (Saved license will auto-apply on restart){Colors.RESET}")
        sys.stdout.flush()
        time.sleep(1.0)
        # إعادة تنفيذ البرنامج بشكل نظيف — saved_license سيُفعّل تلقائياً
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # graceful shutdown
    cols, rows = _get_term_size()
    gap_lines = 3 if GAP_FILL_SUMMARY else 0
    total_lines_now = 3 + len(all_assets) + 1 + gap_lines
    sys.stdout.write(f"\033[{total_lines_now}B\n")
    sys.stdout.flush()
    print(f"{Colors.RED}Stopped{Colors.RESET}")
    print(f"{Colors.CYAN}Total updates: {sum(a.updates for a in all_assets):,}{Colors.RESET}")
    print(f"{Colors.CYAN}Total candles stored: {sum(len(a.candles) for a in all_assets):,}{Colors.RESET}")
    print()
    writer_thread.running = False


# ═══════════════════════════════════════════════════════════════════════════
# ═══ طبقة ربط التطبيق (APP GLUE) — v15.0 «الأصل هو الخادم»                  ═══
# ═══════════════════════════════════════════════════════════════════════════
# هذا القسم يُضاف **فوق** كود الخادم الأصلي (الملصق حرفياً) دون تعديل أي سطر
# فيه. كل ما يلي ليس منطقاً جديداً ولا منطقاً معدّلاً — إنه مجرد جسور تمرّر
# طلبات التطبيق إلى آلة الخادم الأصلية نفسها كما هي حرفياً:
#   fetch_candles_with_retry / realtime_stream / MT4_WRITER.fill_gap_once /
#   _fill_missing_slots / _align_time / CLIENT.get_candles /
#   CLIENT._fetch_historical_batch / WriterThread / mt4_gap_filler ...
# (كود الخادم الأصلي أعلاه لم يُمَس بايت واحد — وهذا القسم يبدأ بعده مباشرة)
# ═══════════════════════════════════════════════════════════════════════════

# ─── استيرادات الطبقة فقط (المحرك الأصلي لم يُمَس) ───
from collections import deque as _qx_deque

# ═══ 1) النطاقات + البلد (نفس كتلة v10 الرسمية حرفياً) ═══
DEFAULT_DOMAIN_GLOBAL = "quotex.com"
DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
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

# ═══ 2) قائمة العملات الكاملة + الدفع + الحالة (نفس كتلة v10 حرفياً) ═══
PAYOUT_REFRESH_INTERVAL = 60
try:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")
except Exception:
    ASSETS_PAYOUT_FILE = Path("qx_assets_payouts.json")

def _instruments_snapshot():
    """يبني قائمة الأصول الكاملة (الاسم + نسبة الدفع + الحالة) من instruments."""
    if CLIENT is None or CLIENT.api is None:
        return []
    insts = getattr(CLIENT.api, "instruments", None) or []
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
        data = await CLIENT.api.event_registry.wait_event("instruments_ready", timeout=5.0)
    if isinstance(data, list) and data:
        CLIENT.api.instruments = data
    return list(getattr(CLIENT.api, "instruments", None) or [])

def _print_payout_table(entries):
    """طباعة الجدول الكامل: العملة / نسبة الدفع / الحالة (مفتوح أو مغلق)."""
    open_entries = [e for e in entries if e.get("open")]
    closed_entries = [e for e in entries if e.get("open") is False]
    print(f"\n{Colors.CYAN}{'═' * 72}{Colors.RESET}")
    print(f"{Colors.BOLD}  FULL ASSET LIST — PAYOUT % — OPEN/CLOSED{Colors.RESET}")
    print(f"  Total: {len(entries)}  |  {Colors.GREEN}OPEN: {len(open_entries)}{Colors.RESET}"
          f"  |  {Colors.RED}CLOSED: {len(closed_entries)}{Colors.RESET}"
          f"  |  Domain: {QX_HOST}")
    print(f"{Colors.CYAN}{'─' * 72}{Colors.RESET}")
    print(f"  {'ASSET':<16}{'PAYOUT':>7}  {'TURBO':>6}  {'1M':>5}  {'5M':>5}  STATUS")
    print(f"{Colors.DIM}{'─' * 72}{Colors.RESET}")
    for e in entries:
        name = (e.get("asset") or "?")[:16]
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
        print(f"  {name:<16}{payout_str:>7}  {turbo_str:>6}  {p1_str:>5}  {p5_str:>5}  {status}")
    print(f"{Colors.CYAN}{'═' * 72}{Colors.RESET}")

async def asset_payout_monitor():
    """يجلب قائمة العملات الكاملة + نسبة الدفع + حالة الزوج (مفتوح/مغلق) مباشرة
    بعد تسجيل الدخول، يطبع الجدول مرة واحدة، يحفظ لقطة JSON، ثم يحدّث بهدوء
    كل PAYOUT_REFRESH_INTERVAL ثانية."""
    await asyncio.sleep(2.0)
    first = True
    last_signature = None
    while True:
        try:
            if CLIENT is None or CLIENT.api is None or not CONNECTION_ALIVE:
                await asyncio.sleep(5.0)
                continue
            entries = []
            try:
                await fetch_instruments_now(timeout=12.0)
                entries = _instruments_snapshot()
            except Exception as e:
                logmsg(f"[payout] refresh failed: {e}")
            if entries:
                _save_assets_payout_file(entries)
                signature = tuple(sorted(
                    (e.get("asset"), str(e.get("payout")), str(e.get("open")))
                    for e in entries))
                if first:
                    try:
                        _print_payout_table(entries)
                    except Exception:
                        pass
                    first = False
                elif signature != last_signature:
                    open_n = sum(1 for e in entries if e.get("open"))
                    closed_n = sum(1 for e in entries if e.get("open") is False)
                    logmsg(f"[payout] updated: {len(entries)} assets "
                           f"({open_n} open / {closed_n} closed) — snapshot saved")
                last_signature = signature
        except Exception as e:
            log_exception("asset_payout_monitor", e)
        await asyncio.sleep(PAYOUT_REFRESH_INTERVAL)

# ═══ 3) مرصد instruments فوق on_message الأصلي ═══
# الأصل يعمل كاملاً أولاً حرفياً (_qx_orig_on_message(self, wss, msg)) ثم نطبّق
# **على مرحلتين** (نفس كتلة v14 المُجرّبة حرفياً — سبب ظهور قائمة العملات فارغة
# في v15.0 كان أن المرصد هنا كان يعالج الصيغة المضمّنة فقط):
#   الرد الرسمي على 42["instruments/get"] يصل كما يلي (سلوك المكتبة الرسمية):
#     المرحلة 1: 451-["instruments/list",{...,"_placeholder":true,"num":0}]
#                (رسالة تحكم تحمل placeholder فقط — بلا بيانات)
#     المرحلة 2: إطار منفصل يحتوي JSON القائمة الفعلية
# v15.1: المساران معاً — كما في v14 حرفياً.
_qx_orig_on_message = WebsocketClient.on_message

def _qx_on_message_with_instruments(self, wss, msg):
    _qx_orig_on_message(self, wss, msg)      # الأصل حرفياً — كل شيء كما هو
    try:
        msg_str = msg.decode("utf-8", errors="ignore") if isinstance(msg, bytes) else str(msg)

        if "instruments/list" in msg_str and "_placeholder" in msg_str:
            # المرحلة 1: نتذكر أننا ننتظر الإطار التالي الذي يحمل البيانات الفعلية
            try:
                self.api._temp_status = msg_str
            except Exception:
                pass
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
            if getattr(self.api, "_temp_status", "") and "instruments/list" in self.api._temp_status:
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
    except Exception as _e:
        logger.debug(f"instruments/list observer error: {_e}")

WebsocketClient.on_message = _qx_on_message_with_instruments

# ═══ 4) إعدادات التطبيق على المحرك (نفس آلية قائمة الأصل نفسها) ═══
# القيم الافتراضية حسب طلب المستخدم: دفعة 700 شمعة (حتى 1000 من الإعدادات)
# وتاريخ 0.80 يوم لكل عملة.
PRELOAD_CANDLES = 700
PAGINATION_BATCH = 700
QX_HISTORY_DAYS = 0.80
ASSET_MAX_CANDLES = 45000
PRELOAD_FIRST_SYMBOL = ASSET_LIST[0] if ASSET_LIST else "BRLUSD_otc"
_PRELOADED_INFO = {}
V14_DEEP_REPAIRED = {}
_QX_WINDOW_BUSY = False
# v15.1 (طلب المستخدم): دائرة تحميل عند تحميل الشموع — حالة التحميل المسبق
# المتسلسل (92 عملة واحدة تلو الأخرى) تُحدَّث هنا وترفعها المضخة للواجهة
# حتى تختفي الدائرة عند انتهاء جلب الشموع.
_QX_PRELOAD_STATUS = {"active": False, "idx": 0, "total": 0, "loaded": 0,
                      "finished_at": 0.0}

def apply_history_days(days_val):
    """تطبيق عدد أيام التاريخ بنفس آلية قائمة الأصل حرفياً (STAGE 3 وقائمة
    «Change History days» في الكود الأصلي): هامش +15% على المدى، INITIAL_CANDLES
    من الأيام، وFETCH_DURATION_SECONDS من المدى مع الهامش — نفس الثلاثي الأصلي."""
    global HISTORY_DAYS, INITIAL_CANDLES, FETCH_DURATION_SECONDS, QX_HISTORY_DAYS
    try:
        d = float(days_val)
    except Exception:
        d = 0.80
    d = max(0.05, d)
    days_with_margin = d * 1.15
    try:
        INITIAL_CANDLES = max(int((d * 86400) / max(1, PERIOD_SECONDS)), 100)
    except Exception:
        INITIAL_CANDLES = 1000
    HISTORY_DAYS = days_with_margin
    FETCH_DURATION_SECONDS = int(86400 * days_with_margin)
    QX_HISTORY_DAYS = d
    return QX_HISTORY_DAYS

# ═══ 5) سجل الأصول: نفس Asset الأصلي حرفياً (بلا أي حقن) ═══
def _get_or_create_asset(api):
    """يجلب أصل العملة من سجل البث أو ينشئه بـ Asset الأصلي نفسه."""
    sym = str(api or "").strip()
    if not sym:
        return None
    for a in ALL_STREAMING_ASSETS:
        try:
            if a.api_symbol == sym:
                return a
        except Exception:
            continue
    a = Asset(sym)
    ALL_STREAMING_ASSETS.append(a)
    return a

def _apply_candles_to_asset(asset, unique):
    """كتابة الخط الكامل في ذاكرة الأصل (Asset الأصلي) + السعر الحي."""
    try:
        asset.candles = list(unique or [])
        if asset.candles:
            asset.price = asset.candles[-1]["close"]
        asset.mark_dirty()
    except Exception:
        pass

async def ensure_asset_loaded(api):
    """عملة فُتح شارتها — v15.3: أسلوب الأصل الأصلي حرفياً (طلب المستخدم:
    «لماذا غيرت طريقة جلب الشموع قلت يجب ان تستخدم مثل هنا في هذا الكود يجلب
    يسد الثغرات ولا ينام الكود» و«من المفترض لجلب 1000 شمعة 4 ثواني»):
    1) البث الحي أولاً (realtime_stream الأصلية كما هي)
    2) seed_history الأصلية كما هي — طلب **واحد** get_candles بمدى الأيام
       كاملاً (اللقطة المحفوظة إن كانت طازجة تُعرض فوراً بلا أي طلب) —
       هي نفسها التي تجلب 1000+ شمعة في ~4 ثوانٍ في الأصل
    3) إذا فشل الجلب: الاحتياط الأصلي fetch_candles_with_retry بمحاولة واحدة
    تعيد عدد الشموع في الذاكرة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None:
        return 0
    try:
        st = getattr(asset, "stream_task", None)
        if st is not None and hasattr(st, "done") and not st.done():
            pass
        else:
            asset.streaming = False
            asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
    except Exception:
        try:
            asset.streaming = False
            asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
        except Exception:
            pass
    if len(asset.candles) >= MIN_CANDLES_THRESHOLD:
        return len(asset.candles)
    try:
        days = max(0.5, float(QX_HISTORY_DAYS))
    except Exception:
        days = 0.80
    ok = False
    try:
        ok = bool(await MT4_WRITER.seed_history(CLIENT, asset, PERIOD, days))
    except Exception as e:
        logmsg(f"[seed:{api}] seed_history failed: {e}")
    # لقطة محفوظة قديمة: آخر شمعة أقدم مما تصلح له آلة السد الأصلية نفسها
    # (GAP_FILL_CANDLES شمعة فقط) — نتجاهلها ونجلب تاريخاً حقيقياً كاملاً
    # بدل عرض خط قديم مثقوب
    try:
        if ok and asset.candles:
            last_t = int(asset.candles[-1].get("time", 0) or 0)
            stale_after = max(1800, int(GAP_FILL_CANDLES * PERIOD_SECONDS * 3))
            if last_t and (time.time() - last_t) > stale_after:
                ok = False
    except Exception:
        pass
    if not ok or len(asset.candles) < MIN_CANDLES_THRESHOLD:
        try:
            await fetch_candles_with_retry(asset, max_retries=1, idx=1, total=1)
        except Exception as e:
            logmsg(f"[seed:{api}] fetch fallback failed: {e}")
    return len(asset.candles)

# ═══ 6) جسور الجلب — نفس دوال الأصل حرفياً ═══
def _format_raw_candles(raw):
    """تنسيق رد الخادم الرسمي: تحليل _parse_raw_candles الأصلي + محاذاة
    _align_time الأصلية + إزالة تكرار وترتيب — نفس حلقة التنسيق في
    fetch_candles_once الأصلية."""
    if not raw:
        return []
    parsed = _parse_raw_candles(raw)          # الأصل حرفياً
    formatted = []
    for c in parsed:
        try:
            aligned = _align_time(int(c["time"]))
            formatted.append({"time": aligned, "open": c["open"], "high": c["high"],
                              "low": c["low"], "close": c["close"],
                              "volume": int(c.get("volume", 0) or 0)})
        except Exception:
            continue
    seen, unique = set(), []
    for c in formatted:
        if c["time"] not in seen:
            seen.add(c["time"])
            unique.append(c)
    unique.sort(key=lambda x: x["time"])
    return unique

async def qx_fetch_window_raw(api, end_ts, seconds, tf_sec, foreground=False, timeout=45.0):
    """بوابة الجلب الأمامية الواحدة — نداء CLIENT.get_candles الأصلي نفسه
    (المُجرّب والآمن). foreground يمنع اختلاط طلب العرض الحالي مع التحميل المسبق."""
    global _QX_WINDOW_BUSY
    if CLIENT is None or CLIENT.api is None:
        return []
    if foreground:
        for _ in range(int(max(1.0, float(timeout) * 10))):
            if not _QX_WINDOW_BUSY:
                break
            await asyncio.sleep(0.1)
    _QX_WINDOW_BUSY = True
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, int(end_ts), int(max(60, seconds)), int(tf_sec)),
            timeout=float(timeout))
        return list(res or [])
    except Exception:
        return []
    finally:
        _QX_WINDOW_BUSY = False

async def fetch_older_batch(api, before_ts, batch=300):
    """دفعة أقدم للتمرير للخلف — نداء CLIENT.get_candles الأصلي بمرساة before_ts،
    والدمج في ذاكرة الأصل بلا تقليص (setdefault: القديم الناقص فقط يُضاف)."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    psec = max(1, int(PERIOD_SECONDS))
    batch = max(50, int(batch or 300))
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, int(before_ts), batch * psec, psec), timeout=45.0)
    except Exception:
        return 0
    if not res:
        return 0
    candles = [c for c in res
               if isinstance(c, dict) and int(c.get("time", 0) or 0) < int(before_ts)]
    if not candles:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None:
        return 0
    merged_map = {c["time"]: c for c in asset.candles}
    for c in candles:
        merged_map.setdefault(c["time"], c)
    merged = sorted(merged_map.values(), key=lambda x: x["time"])
    asset.candles = merged[-int(ASSET_MAX_CANDLES):]
    if asset.candles:
        asset.price = asset.candles[-1]["close"]
    asset.mark_dirty()
    return len(candles)

async def qx_get_historical_batches(asset, amount_of_seconds, period, timeout=30,
                                    max_workers=5, batch_callback=None):
    """نفس طريقة الأصل get_historical_candles بكل تفاصيلها (نفس
    CLIENT._fetch_historical_batch الأصلية، نفس chunk=period×FETCH_CHUNK_SIZE،
    نفس عدد العمال max_workers، نفس الرجوع للخلف ونفس قاعدة 3 فشل، نفس
    FETCH_BATCH_DELAY) — الفرق الوحيد: كل دفعة تُسلَّم فور وصولها عبر
    batch_callback(batch, worker_id) ليرفعها التطبيق إلى الشارت حية."""
    if CLIENT is None or CLIENT.api is None:
        return []
    max_workers = max_workers or 1
    chunk_seconds = period * FETCH_CHUNK_SIZE
    all_candles = {}
    current_time = int(time.time())
    target_start_time = current_time - amount_of_seconds
    block_size = max(1, amount_of_seconds // max_workers)
    semaphore = asyncio.Semaphore(max_workers)

    async def worker(start_t, end_t, worker_id):
        worker_candles = {}
        async with semaphore:
            oldest_t = start_t
            consecutive_failures_in_worker = 0
            while oldest_t > end_t:
                if not CLIENT or not getattr(getattr(CLIENT, "api", None), "state", None) \
                        or not getattr(CLIENT.api.state, "check_accepted_connection", False):
                    break
                index = next(_request_counter)
                batch_data = await CLIENT._fetch_historical_batch(
                    asset, oldest_t, chunk_seconds, period, index, timeout)
                if not batch_data:
                    oldest_t -= chunk_seconds
                    consecutive_failures_in_worker += 1
                    if consecutive_failures_in_worker >= 3:
                        break
                    await asyncio.sleep(FETCH_BATCH_DELAY * 2)
                    continue
                consecutive_failures_in_worker = 0
                new_batch = CLIENT._parse_historical_candles(batch_data)
                if not new_batch:
                    oldest_t -= chunk_seconds
                    continue
                batch_times = []
                for c in new_batch:
                    ts = c["time"]
                    if ts >= end_t and ts <= start_t:
                        worker_candles[ts] = c
                        batch_times.append(ts)
                if not batch_times:
                    oldest_t -= chunk_seconds
                    continue
                batch_times.sort()
                new_oldest = batch_times[0]
                if batch_callback:
                    try:
                        batch_callback([worker_candles[t] for t in batch_times], worker_id)
                    except Exception:
                        pass
                oldest_t = new_oldest if new_oldest < oldest_t else oldest_t - chunk_seconds
                await asyncio.sleep(FETCH_BATCH_DELAY)
        return list(worker_candles.values())

    try:
        await CLIENT.start_candles_stream(asset, period)
    except Exception:
        pass
    tasks = []
    for i in range(max_workers):
        s = current_time - (i * block_size)
        e = max(target_start_time, s - block_size)
        tasks.append(worker(s, e, i))
    results = await asyncio.gather(*tasks)
    for batch in results:
        for c in batch:
            all_candles[c["time"]] = c
    return sorted(all_candles.values(), key=lambda x: x["time"])

async def v14_deep_gap_seal(api, reason=""):
    """السد العميق: مرساة عند أقدم شمعة اصطناعية (volume==0) — نداء الجلب
    الأصلي CLIENT.get_candles يعيد شموعاً حقيقية تُستبدل بالشرطات المسطحة داخل
    نافذة محدودة (حتى 200 شمعة) دون لمس الشمعة الحية ولا تقليص الذاكرة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    asset = _get_or_create_asset(api)
    if asset is None or len(asset.candles) < 2:
        return 0
    psec = max(1, int(PERIOD_SECONDS))
    cur_start = _align_time(int(time.time()))
    art = [c for c in asset.candles
           if int(c.get("volume", 1) or 0) == 0 and c["time"] < cur_start]
    if not art:
        return 0
    oldest = min(c["time"] for c in art)
    span = max(1, (cur_start - oldest) // psec)
    window = min(200, span + 10)
    try:
        res = await asyncio.wait_for(
            CLIENT.get_candles(api, cur_start + psec, window * psec, psec),
            timeout=30.0)
    except Exception:
        return 0
    if not res:
        return 0
    real = {}
    for c in res:
        if isinstance(c, dict) and int(c.get("time", 0) or 0) > 0:
            real[int(c["time"])] = c
    if not real:
        return 0
    merged = []
    for c in asset.candles:
        if c["time"] >= cur_start:
            merged.append(c)                      # الشمعة الحية لا تُلمس
            continue
        r = real.get(c["time"])
        if r is not None and int(c.get("volume", 1) or 0) == 0:
            merged.append(dict(r))
        else:
            merged.append(c)
    have = {c["time"] for c in merged}
    for t, r in real.items():
        if t not in have and t < cur_start:
            merged.append(dict(r))
    merged.sort(key=lambda x: x["time"])
    asset.candles = merged[-int(ASSET_MAX_CANDLES):]
    if asset.candles:
        asset.price = asset.candles[-1]["close"]
    asset.mark_dirty()
    V14_DEEP_REPAIRED[api] = time.time()
    return len(real)

# ═══ 7) التيكات في الذاكرة (فريمات الثواني S5..S30) — الأصل لم يُمَس ═══
_TICK_CACHE = {}
_TICK_QUEUE_MAX = 4096
_TICK_MAX_AGE = 300.0      # 5 دقائق — ذاكرة فقط

async def tick_cache_collector():
    """يلتقط كل تيك يصل (realtime_candles الأصلية — يتحدث عند كل تيك) في ذاكرة
    كل عملة بث حي، بلا أي كتابة على القرص. يبني منه التطبيق فريمات الثواني."""
    while True:
        try:
            if CLIENT is not None and getattr(CLIENT, "api", None) is not None:
                rc = getattr(CLIENT.api, "realtime_candles", {}) or {}
                for sym, tick in list(rc.items()):
                    if not isinstance(tick, (list, tuple)) or len(tick) < 3:
                        continue
                    try:
                        ts, price = int(tick[1]), float(tick[2])
                    except Exception:
                        continue
                    if price <= 0 or ts <= 0:
                        continue
                    q = _TICK_CACHE.get(sym)
                    if q is None:
                        q = _qx_deque(maxlen=_TICK_QUEUE_MAX)
                        _TICK_CACHE[sym] = q
                    if q and q[-1][0] == ts and q[-1][1] == price:
                        continue
                    q.append((ts, price))
        except Exception:
            pass
        await asyncio.sleep(0.05)

async def tick_retention_loop():
    """حذف التيكات الأقدم من 5 دقائق (ذاكرة فقط)."""
    while True:
        try:
            now = time.time()
            for sym, q in list(_TICK_CACHE.items()):
                while q and (now - q[0][0]) > _TICK_MAX_AGE:
                    q.popleft()
                if not q:
                    _TICK_CACHE.pop(sym, None)
        except Exception:
            pass
        await asyncio.sleep(30.0)

async def candlestore_trim_loop():
    """تشذيب candles.db بهدوء: الاحتفاظ بأحدث 5000 شمعة لكل رمز معروف
    + نقطة تحقق WAL كل ساعات — حماية القرص دون أي مساس بالجلب."""
    while True:
        try:
            store = MT4_WRITER.candle_store
            conn = store._get_write_conn()
            try:
                syms = set()
                try:
                    syms.update(str(k) for k in MT4_WRITER._gap_filled.keys())
                except Exception:
                    pass
                for a in list(ALL_STREAMING_ASSETS):
                    try:
                        syms.add(str(a.symbol))
                    except Exception:
                        pass
                for sym in syms:
                    try:
                        conn.execute(
                            "DELETE FROM candles WHERE symbol=? AND time <= "
                            "(SELECT time FROM candles WHERE symbol=? "
                            "ORDER BY time DESC LIMIT 1 OFFSET 5000)",
                            (sym, sym))
                    except Exception:
                        pass
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(6 * 3600.0)

# ═══ 8) علامات تجمّد السد — نفس مخازن الأصل حرفياً ═══
def clear_gap_flag_any(variants):
    """رفع علامة التجمّد عن رمز بأي صيغة تخزين ممكنة (الذاكرة + candles.db)."""
    syms = [str(v or "").strip() for v in (variants or []) if str(v or "").strip()]
    for sym in syms:
        try:
            MT4_WRITER._gap_filled[sym] = False
        except Exception:
            pass
        try:
            MT4_WRITER._gap_filled_at.pop(sym, None)
        except Exception:
            pass
        try:
            MT4_WRITER.candle_store.set_gap_filled(sym, False)
        except Exception:
            pass

def reset_gap_flags():
    """تصفير علامات التجمّد في الذاكرة (نفس مخازن MT4_WRITER الأصلية)."""
    try:
        for sym in list(MT4_WRITER._gap_filled.keys()):
            MT4_WRITER._gap_filled[sym] = False
    except Exception:
        pass
    try:
        MT4_WRITER._gap_filled_at.clear()
    except Exception:
        pass

# ═══ 9) التحميل المسبق المتسلسل — «ضع كل العملات واحدة تلو الأخرى» ═══
async def preload_all_assets():
    """التحميل المسبق المتسلسل لكل العملات المفتوحة **واحدة تلو الأخرى** —
    نفس تدفق الكتلة الرئيسية للأصل حرفياً لكل عملة:
      realtime_stream أولاً (يجمع التيك أثناء الجلب) ← fetch_candles_with_retry
      الأصلية (تاريخ FETCH_DURATION_SECONDS + الجسر + سد الفجوات + HST) ←
      فاصل بين عملة وأخرى.
    فاتحة الشارت أولاً (BRLUSD_otc) ثم بقية العملات المفتوحة من instruments
    بالترتيب. كل عملة تُسجَّل في _PRELOADED_INFO لحالة التحميل في الواجهة."""
    if CLIENT is None or CLIENT.api is None:
        return 0
    # اطلب قائمة instruments مرة واحدة (الطريقة الرسمية) وانتظر وصولها باختصار
    try:
        await fetch_instruments_now(timeout=12.0)
    except Exception:
        pass
    try:
        await wait_until(lambda: bool(_instruments_snapshot()),
                         timeout=15.0, poll_interval=0.5)
    except asyncio.TimeoutError:
        pass
    symbols, seen = [], set()
    opener = PRELOAD_FIRST_SYMBOL
    if opener:
        symbols.append(opener)
        seen.add(opener)
    entries = _instruments_snapshot()
    for e in entries:
        sym = str((e or {}).get("asset") or "").strip()
        if not sym or sym in seen:
            continue
        if e.get("open") is False:
            continue        # المغلقة الآن لا بث حي لها — تُحمّل عند فتح شارتها
        symbols.append(sym)
        seen.add(sym)
    if len(symbols) <= 1:
        # fallback: قائمة الأصل الافتراضية ASSET_LIST كما هي
        for sym in list(ASSET_LIST):
            if sym not in seen:
                symbols.append(sym)
                seen.add(sym)
    total = len(symbols)
    logmsg(f"[preload] sequential preload: {total} assets, ONE after another "
           f"(history window {FETCH_DURATION_SECONDS}s each)")
    # v15.1: بدء التحميل المسبق — الدائرة تظهر في الواجهة من هذه اللحظة
    try:
        _QX_PRELOAD_STATUS["active"] = True
        _QX_PRELOAD_STATUS["idx"] = 0
        _QX_PRELOAD_STATUS["total"] = int(total)
        _QX_PRELOAD_STATUS["loaded"] = 0
        _QX_PRELOAD_STATUS["finished_at"] = 0.0
    except Exception:
        pass
    loaded = 0
    streak = 0
    for idx, sym in enumerate(symbols, 1):
        if not CONNECTION_ALIVE or CLIENT is None or CLIENT.api is None:
            logmsg(f"[preload] connection lost at {idx}/{total}; waiting reconnect…")
            try:
                await wait_until(
                    lambda: CONNECTION_ALIVE and CLIENT is not None and CLIENT.api is not None,
                    timeout=30.0, poll_interval=0.5)
            except asyncio.TimeoutError:
                streak += 1
                if streak >= MAX_RECONNECTS_DURING_FETCH:
                    logmsg("[preload] giving up after repeated disconnects")
                    break
                continue
        streak = 0
        asset = _get_or_create_asset(sym)
        if asset is None:
            continue
        try:
            st = getattr(asset, "stream_task", None)
            if st is None or (hasattr(st, "done") and st.done()):
                asset.streaming = False
                asset.stream_task = asyncio.ensure_future(realtime_stream(asset))
        except Exception:
            pass
        if len(asset.candles) < MIN_CANDLES_THRESHOLD:
            try:
                n, _att = await fetch_candles_with_retry(
                    asset, max_retries=MAX_FETCH_RETRIES, idx=idx, total=total)
                if n >= MIN_CANDLES_THRESHOLD:
                    loaded += 1
            except Exception as e:
                logmsg(f"[preload] {sym}: {str(e)[:80]}")
        else:
            loaded += 1
        _PRELOADED_INFO[sym] = {"candles": len(asset.candles), "at": time.time()}
        # v15.1: تحديث حالة الدائرة بعد كل عملة (واحدة تلو الأخرى)
        try:
            _QX_PRELOAD_STATUS["idx"] = int(idx)
            _QX_PRELOAD_STATUS["loaded"] = int(loaded)
        except Exception:
            pass
        if idx % 10 == 0:
            logmsg(f"[preload] progress: {idx}/{total} assets ({loaded} loaded)")
        # فاصل بين عملة وأخرى — نفس الأصل: واحدة تلو الأخرى بلا تسرّع
        await asyncio.sleep(1.0 if PERIOD_SECONDS < 60 else FETCH_ASSET_DELAY)
    # v15.1: انتهاء التحميل المسبق — الدائرة تختفي من الواجهة
    try:
        _QX_PRELOAD_STATUS["active"] = False
        _QX_PRELOAD_STATUS["idx"] = int(total)
        _QX_PRELOAD_STATUS["loaded"] = int(loaded)
        _QX_PRELOAD_STATUS["finished_at"] = time.time()
    except Exception:
        pass
    logmsg(f"[preload] done: {loaded}/{total} assets loaded sequentially")
    return loaded

def v14_print_banner():
    try:
        print("[QX] engine = الخادم الأصلي مدمجاً حرفياً + طبقة ربط التطبيق "
              "(منطق الخادم لم يُغيَّر)")
    except Exception:
        pass

def v14_build_background_loops():
    """كل حلقات الأصل الخلفية تعمل أصلاً (health_monitor/auto_reconnect/
    keepalive_loop/stale_message_watchdog/asset_payout_monitor/preload/
    mt4_gap_filler/tick_cache_collector/...) — لا حلقات إضافية هنا."""
    return []

def v14_supervise(name, factory):
    """مشرف مباشر: يُمرّر كوروتين الحلقة كما هو (احتياط — لا يُستدعى حالياً)."""
    async def _sup():
        try:
            coro = factory()
            if coro is not None:
                await coro
        except Exception as e:
            try:
                logmsg(f"[supervise:{name}] {e}")
            except Exception:
                pass
    return _sup()


# ═══════════════════════════════════════════════════════════════════════════
# ═══ v15.2: إصلاح حفظ البريد («تذكّرني») — في طبقة الربط، الأصل لم يُمَس ═══
# ═══════════════════════════════════════════════════════════════════════════
# سبب «ميزة حفض الايميل لماذا لا تعمل» (طلب المستخدم): كود الأصل في
# SessionManager._save_state يمرر **7 قيم** لعبارة INSERT بها **6 علامات ؟**
# فقط (VALUES (1, ?, ?, ?, ?, ?, ?) — العمود id مكتوب قيمةً حرفية والكود
# يمرر 1 أيضاً) فترفع sqlite الخطأ «Incorrect number of bindings supplied.
# The current statement uses 6, and there are 7 supplied» وexcept الصامت
# يبتلعه — النتيجة: البريد/كلمة السر/الحالة لا تُكتب في app_data.db أبداً،
# ولا يظهر البريد في واجهة تسجيل الدخول عند الإقلاع التالي.
# الإصلاح: نفس الكود الأصلي حرفياً بعدد الروابط الصحيح فقط (6 قيم بعد id
# الحرفي) — لا أي تغيير في منطق آخر، وكود الأصل أعلاه لم يُمَس بايت واحد.
def _v152_session_save_state(self):
    try:
        with _db_lock:
            conn = _db_conn()
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO app_state
                    (id, email, password, host, last_login, last_success, failed_auth_count)
                    VALUES (1, ?, ?, ?, ?, ?, ?)
                """, (
                    self.state.get("email", ""),
                    self.state.get("password", ""),
                    self.state.get("host", "qxbroker.com"),
                    self.state.get("last_login", 0),
                    1 if self.state.get("last_success", False) else 0,
                    self.state.get("failed_auth_count", 0),
                ))
                conn.commit()
            finally:
                conn.close()
    except Exception:
        pass


try:
    SessionManager._save_state = _v152_session_save_state
except Exception:
    pass

'''


# ---------------------------------------------------------------- الألوان
DARK = dict(bg="#000000", side="#000000", card="#0A0A0A", border="#1F1F23",
            fg="#FFFFFF", sub="#8A9099", hover="#151518",
            accent="#3B8BFF", g1="#14B8F5", g2="#3B6CF5", good="#22C55E", bad="#EF4444")
LIGHT = dict(bg="#FFFFFF", side="#FFFFFF", card="#F5F7FB", border="#E1E6F0",
             fg="#000000", sub="#5B6B80", hover="#EAEFF8",
             accent="#2563EB", g1="#0EA5E9", g2="#2F5BF0", good="#16A34A", bad="#DC2626")

# --------------------------------------------------------------- الترجمات
T = {
    "en": {
        "login": "Sign in", "user": "Username", "pass": "Password", "signin": "Log in",
        "welcome": "Welcome back", "studio": "Studio", "ind": "Indicators", "sig": "Signals",
        "hist": "History", "sett": "Settings", "logout": "Log out", "start": "Start",
        "stop": "Stop", "running": "Running", "stopped": "Stopped", "theme": "Theme",
        "lang": "Language", "dark": "Dark", "light": "Light", "market": "Market",
        "real": "Real", "otc": "OTC", "asset": "Asset", "live": "Live", "fit": "Fit view",
        "clear": "Clear drawings", "shot": "Screenshot", "tools": "Tools", "cursor": "Cursor",
        "trend": "Trend line", "hline": "Horizontal line", "vline": "Vertical line",
        "rect": "Rectangle", "fib": "Fibonacci", "brush": "Brush", "eraser": "Eraser",
        "mytools": "My tools", "editor": "Editor", "console": "Console", "run": "Run",
        "save": "Save", "del": "Delete", "newfile": "New file", "kind": "Kind",
        "kindjs": "JS Indicator", "kindpy": "Python Indicator", "kindtool": "JS Tool",
        "token": "Bot token", "chats": "Chats / channels", "tmpl": "Message template",
        "tghint": "There is no chat-id field here on purpose — the indicator author writes the chat id(s) inside the indicator code (signal() returns chats). Signals and their results are sent to that chat automatically.",
        "attach": "Attach chart screenshot", "test": "Send test", "saved": "Saved",
        "upcoming": "Upcoming signals", "none": "No signals yet", "time": "Time",
        "dir": "Direction", "up": "Up", "down": "Down", "price": "Price",
        "indicator": "Indicator", "status": "Status", "sent": "Sent", "fail": "Failed",
        "latest": "Latest signals", "add": "Add to chart",
        "libDesc": "Advanced ready-made indicators — click Add, edit the code, then Run.",
        "codejs": "JS Indicator", "codepy": "Python Indicator", "codetool": "JS Drawing Tool",
        "welcomeTitle": "Program indicators & tools in Python or JavaScript",
        "feed": "Market feed", "feednote": "Live feed is simulated for Real & OTC assets — plug a real Quotex connector in AssetFeed.",
        "delconfirm": "Delete this file permanently?", "savedall": "All files saved",
        "files": "Files", "userbox": "User", "guest": "Guest", "shotdone": "Screenshot saved",
        "nosig": "No signals yet", "sigvars": "Variables:",
        "paste": "Paste", "copy": "Copy", "cut": "Cut", "selall": "Select all",
        "err": "Error", "mustreturn": "The code must return { ... }",
        "compileok": "compiled and applied", "applied": "applied",
        "stoppedfile": "stopped", "toolactive": "activated — click the chart to draw",
        "toolregistered": "registered — pick it from My tools",
        "f1": "Program indicators & tools in Python or JavaScript",
        "f2": "Advanced ready-made indicators library",
        "f3": "Telegram alerts from your indicators",
        "f4": "Signals with chart screenshots",
        "f5": "Quotex real market & OTC assets",
        "f6": "Left toolbar, dark & light themes",
        "shotbtn": "Screenshot", "chartshot": "Chart screenshot", "logclear": "Clear",
        "telegram": "Telegram", "chart": "Chart",
        "demo": "Demo", "acct": "Account",
        "tgbot": "Telegram bot", "backchart": "Back to chart",
        "currs": "Currencies", "currsHint": "Tap a currency to add or remove it — the bar below the chart shows added currencies only",
        "mktOpen": "Open", "mktClosed": "Closed",
        "otherSett": "Other settings", "darkMode": "Dark mode", "langLbl": "Language", "sndLbl": "Signal sounds",
        "sbLbl": "Status bar", "cdLbl": "Candle countdown",
        "histDays": "History candles — days", "histSave": "Save",
        "histDaysHint": "When you open a currency the engine fetches this many days in ONE request (0.5 – 30, default 2); the server delivers it in batches and every batch rises to the chart immediately — the chart stays free (zoom/pan) and no candles are lost. Type the number and press Save.",
        "histSaved": "History days saved — opening a currency now loads the new range",
        "batchCandles": "Batch candles — direct batch", "batchSave": "Save",
        "batchCandlesHint": "The direct batch fetched for a currency when you open it, and the size of every batch pushed to the chart (default 700, adjustable up to 1000). Type the number and press Save.",
        "batchSaved": "Batch candles saved — next batches use the new size",
        "badiSect": "Encrypted indicators (BADI)", "keyFp": "Key fingerprint:",
        "notifT": "Notifications", "notifEmpty": "No notifications yet",
        "notifHint": "Notifications from your paid indicators appear here — the developer sends them from his own server (updates, subscription reminders). No files can ever pass through this channel.",
        "notifClear": "Clear all",
        "notifUnreadX": "%1 unread notification(s)", "notifAllRead": "All notifications read",
        "paidSrvLbl": "Paid control server (optional) — the app polls it and accepts whitelist commands only:",
        "paidIdLbl": "Paid indicator ID on that server:",
        "badiEnc": "Encrypt the indicator — export a .badi file", "badiImp": "Import an encrypted indicator (.badi)",
        "badiSaved": "Encrypted indicator saved", "badiEmpty": "There is no code to encrypt",
        "badiJsOnly": "Only JavaScript indicators can be encrypted", "badiOk": "Loaded — runs internally, its code stays hidden",
        "badiFail": "BADI import failed", "badiHint": "The 256-bit key is fused into the app — it is never written to any file, never shown and cannot be copied. The encrypted indicator runs inside the chart directly: its code never opens in the editor and is never saved anywhere. The .badi file sits next to the real indicator file — like MetaTrader.",
        "licTitle": "Encrypt indicator — buyer license", "licHint": "Paste the buyer's USER ID so the indicator runs on his device only. Multiple buyers: separate IDs with commas. Leave empty to allow everyone.",
        "licOk": "Encrypt", "licCancel": "Cancel", "yourUid": "Your USER ID:",
        "uidCopied": "USER ID copied to clipboard", "folderOpen": "App folder opened",
        "badiFolder": "Indicators folder", "badiFolderHint": "Created indicators and tools are saved here as real files — you can also drop your own files into these folders and the app loads them automatically.",
        "chartLook": "Chart appearance", "lookHint": "Type any color freely (hex like #22E08A or rgba) — not limited to presets. Changes apply instantly and are saved.",
        "cBg": "Chart background", "cBull": "Bullish candle", "cBear": "Bearish candle",
        "cGrid": "Grid", "cAxis": "Axis text", "cCross": "Crosshair", "cDraw": "Drawings",
        "resetLook": "Restore defaults", "pickColor": "Pick a color freely",
        "myinds": "My indicators", "myindsHint": "Auto-detected from the BadiCharts folder — drop any indicator or tool file there and it appears here instantly.",
        "myindThumbNone": "Screenshot on save", "kindbadi": "Encrypted (.badi)",
        "backChart": "Back to chart",
        "shareOk": "Indicator file copied — paste it in Telegram or anywhere", "shareFail": "Share failed",
        "rescan": "Rescan",
        "badge": "Charting Engine", "h1": "Read the market,", "h2": "trade with confidence.",
        "lead": "Code your own indicators, get signals with chart snapshots, and trade smarter — all in one studio.",
        "cardSub": "Enter your Quotex platform account credentials — not a Badi Studio account", "remember": "Remember me",
        "errEmpty": "Please enter your username and password.", "signing": "Signing in…", "signinok": "Signed in successfully",
        "qxResolving": "Detecting your country & server domain…", "qxConnecting": "Connecting to the Quotex server", "qxAuth": "Signing in to your Quotex account…", "qxLoad": "Connected — loading BRLUSD_otc (300 candles)…", "qxFail": "Could not connect to Quotex — check your email/password", "qxEngine": "QX engine error — restart the app",
        "tgsave1": "Saved bot token", "tgonly": "One bot only — saving a new token replaces the previous one.",
        "tgdel": "Delete the saved token", "tgcleared": "Saved token deleted",
    },
    "ar": {
        "login": "تسجيل الدخول", "user": "اسم المستخدم", "pass": "كلمة المرور",
        "signin": "دخول", "welcome": "مرحباً بعودتك", "studio": "الاستوديو",
        "ind": "المؤشرات", "sig": "الإشارات", "hist": "السجل", "sett": "الإعدادات",
        "logout": "خروج", "start": "تشغيل", "stop": "إيقاف", "running": "يعمل",
        "stopped": "متوقف", "theme": "المظهر", "lang": "اللغة", "dark": "داكن",
        "light": "فاتح", "market": "السوق", "real": "حقيقي", "otc": "OTC",
        "asset": "الأصل", "live": "مباشر", "fit": "ملاءمة العرض",
        "clear": "مسح الرسومات", "shot": "لقطة شاشة", "tools": "الأدوات",
        "cursor": "تحديد", "trend": "خط اتجاه", "hline": "خط أفقي", "vline": "خط عمودي",
        "rect": "مستطيل", "fib": "فيبوناتشي", "brush": "فرشاة", "eraser": "ممحاة",
        "mytools": "أدواتي", "editor": "المحرر", "console": "الكونسول", "run": "تشغيل",
        "save": "حفظ", "del": "حذف", "newfile": "ملف جديد", "kind": "النوع",
        "kindjs": "مؤشر JS", "kindpy": "مؤشر Python", "kindtool": "أداة JS",
        "token": "توكن البوت", "chats": "الدردشات / القنوات", "tmpl": "قالب الرسالة",
        "tghint": "لا حقل لمعرّف المحادثة هنا عمدًا — يضع مبرمج المؤشر معرّف الدردشة داخل كود المؤشر نفسه (يرجع signal() القيمة chats)، وتُرسل الإشارات ونتائجها تلقائيًا إلى تلك المحادثة.",
        "attach": "إرفاق لقطة الشارت", "test": "إرسال تجريبي", "saved": "تم الحفظ",
        "upcoming": "الإشارات القادمة", "none": "لا إشارات بعد", "time": "الوقت",
        "dir": "الاتجاه", "up": "صعود", "down": "هبوط", "price": "السعر",
        "indicator": "المؤشر", "status": "الحالة", "sent": "أُرسلت", "fail": "فشلت",
        "latest": "أحدث الإشارات", "add": "أضف للشارت",
        "libDesc": "مؤشرات جاهزة متطورة — اضغط أضف، عدّل الكود، ثم شغّل.",
        "codejs": "مؤشر JS", "codepy": "مؤشر Python", "codetool": "أداة JS",
        "welcomeTitle": "برمجة المؤشرات والأدوات بلغة بايثون أو جافا سكريبت",
        "feed": "التغذية السوقية", "feednote": "التغذية محاكاة لأصول Real و OTC — اربط موصل كوتكس الحقيقي في AssetFeed.",
        "delconfirm": "حذف هذا الملف نهائياً؟", "savedall": "حُفظت كل الملفات",
        "files": "الملفات", "userbox": "المستخدم", "guest": "زائر",
        "shotdone": "حُفظت لقطة الشاشة", "nosig": "لا إشارات بعد", "sigvars": "المتغيرات:",
        "paste": "لصق", "copy": "نسخ", "cut": "قص", "selall": "تحديد الكل",
        "err": "خطأ", "mustreturn": "الكود يجب أن يُعيد { ... }",
        "compileok": "ترجمة وتطبيق", "applied": "طُبّق",
        "stoppedfile": "أُوقف", "toolactive": "مفعّلة — انقر على الشارت للرسم",
        "toolregistered": "سُجّلت — اخترها من أدواتي",
        "f1": "برمجة المؤشرات والأدوات بلغة بايثون أو جافا سكريبت",
        "f2": "مكتبة مؤشرات جاهزة متطورة",
        "f3": "تنبيهات تلجرام من مؤشراتك",
        "f4": "إشارات مع لقطات شاشة للشارت",
        "f5": "سوق كوتكس الحقيقي وأصول OTC",
        "f6": "شريط أدوات يساراً ومظهر داكن وفاتح",
        "shotbtn": "لقطة", "chartshot": "لقطة الشارت", "logclear": "مسح",
        "telegram": "تلجرام", "chart": "الشارت",
        "demo": "تجريبي", "acct": "الحساب",
        "tgbot": "بوت تلجرام", "backchart": "عودة إلى الشارت",
        "currs": "العملات", "currsHint": "اضغط على العملة لإضافتها أو إزالتها — الشريط تحت الشارت يعرض العملات المضافة فقط",
        "mktOpen": "مفتوح", "mktClosed": "مغلوق",
        "otherSett": "إعدادات أخرى", "darkMode": "الوضع الليلي", "langLbl": "اللغة", "sndLbl": "أصوات الإشارات",
        "sbLbl": "شريط الحالة", "cdLbl": "العد التنازلي على الشارت",
        "histDays": "شموع التاريخ — عدد الأيام", "histSave": "حفظ",
        "histDaysHint": "عند فتح العملة يجلب المحرك هذا العدد من الأيام بطلب واحد (0.5 – 30، الافتراضي يومان)، والخادم يرفعه على دفعات وكل دفعة تُرفع إلى الشارت فوراً — الشارت يبقى حراً (زوم/تحريك) ولا تُفقد أي شمعة. اكتب الرقم واضغط حفظ.",
        "histSaved": "تم حفظ عدد الأيام — فتح العملة يجلب المدى الجديد",
        "batchCandles": "شموع الدفعة المباشرة", "batchSave": "حفظ",
        "batchCandlesHint": "الدفعة المباشرة التي تُجلب للعملة عند فتح شارتها، وحجم كل دفعة تُرفع إلى الشارت (الافتراضي 700 شمعة، وقابل للتعديل حتى 1000). اكتب الرقم واضغط حفظ.",
        "batchSaved": "تم حفظ عدد شموع الدفعة — الدفعات القادمة بالحجم الجديد",
        "badiSect": "المؤشرات المشفرة (BADI)", "keyFp": "بصمة المفتاح:",
        "notifT": "الإشعارات", "notifEmpty": "لا توجد إشعارات بعد",
        "notifHint": "تظهر هنا إشعارات المؤشرات المدفوعة — المبرمج يرسلها من خادمه (تحديثات، تذكير بالاشتراك). لا يمكن لأي ملف أن يمر عبر هذه القناة إطلاقًا.",
        "notifClear": "مسح الكل",
        "notifUnreadX": "%1 إشعار غير مقروء", "notifAllRead": "كل الإشعارات مقروءة",
        "paidSrvLbl": "خادم التحكم المدفوع (اختياري) — التطبيق يسأله دوريًا ويقبل الأوامر البيضاء فقط:",
        "paidIdLbl": "معرف المؤشر المدفوع عند ذلك الخادم:",
        "badiEnc": "تشفير المؤشر وتصديره إلى ملف .badi", "badiImp": "استيراد مؤشر مشفر (.badi)",
        "badiSaved": "تم حفظ المؤشر المشفر", "badiEmpty": "لا يوجد كود لتشفيره",
        "badiJsOnly": "التشفير لمؤشرات JavaScript فقط — ملفات Python غير مدعومة", "badiOk": "تم التحميل — يعمل داخليًا وكودــه مخفي",
        "badiFail": "فشل استيراد BADI", "badiHint": "المفتاح 256-بت مدموج داخل التطبيق — لا يُكتب أبدًا في أي ملف، ولا يُعرض، ولا يمكن نسخه. المؤشر المشفر يعمل داخل الشارت مباشرة: كودــه لا يُفتح في المحرر ولا يُحفظ في أي مكان. الملف المشفر .badi يُحفظ بجوار ملف المؤشر الأصلي — مثل ميتاتريدر.",
        "licTitle": "تشفير المؤشر — ترخيص المشتري", "licHint": "الصق معرّف المشتري (USER ID) ليعمل المؤشر على جهازه هو فقط. لعدة مشترين: افصل المعرفات بفاصلة. اتركه فارغًا ليعمل مع الجميع.",
        "licOk": "تشفير", "licCancel": "إلغاء", "yourUid": "معرّفك (USER ID):",
        "uidCopied": "تم نسخ معرّف المستخدم", "folderOpen": "تم فتح مجلد التطبيق",
        "badiFolder": "مجلد المؤشرات", "badiFolderHint": "المؤشرات والأدوات التي تنشئها تُحفظ هنا كملفات حقيقية — ويمكنك أن تضع ملفاتك مباشرة في هذه المجلدات وسيتعرف عليها التطبيق تلقائيًا.",
        "chartLook": "مظهر الشارت", "lookHint": "اكتب أي لون بحرية (hex مثل #22E08A أو rgba) — ليست الألوان محدودة بقوائم. التغيير يُطبق فورًا ويُحفظ.",
        "cBg": "خلفية الشارت", "cBull": "الشمعة الصاعدة", "cBear": "الشمعة الهابطة",
        "cGrid": "الشبكة", "cAxis": "نص المحاور", "cCross": "مؤشر التقاطع", "cDraw": "أدوات الرسم",
        "resetLook": "استعادة الافتراضي", "pickColor": "اختر أي لون بحرية",
        "myinds": "مؤشراتي", "myindsHint": "تُكتشف تلقائيًا من مجلد BadiCharts — ضع أي ملف مؤشر أو أداة في المجلد وسيظهر هنا فورًا.",
        "myindThumbNone": "اللقطة عند الحفظ", "kindbadi": "مؤشر مشفر (.badi)",
        "backChart": "الرجوع إلى الشارت",
        "shareOk": "نُسخ ملف المؤشر إلى الحافظة — الصقه في تلجرام أو أي مكان", "shareFail": "فشلت المشاركة",
        "rescan": "إعادة فحص",
        "badge": "محرك الشارتات", "h1": "اقرأ السوق بذكاء،", "h2": "وتداول بثقة.",
        "lead": "برمج مؤشراتك، واستلم إشارات مع لقطات الشارت، وتداول بذكاء — كل ذلك في استوديو واحد.",
        "cardSub": "أدخل بيانات حساب منصة كوتكس (Quotex) — وليس حساب بادي استوديو", "remember": "تذكّرني",
        "errEmpty": "يرجى إدخال اسم المستخدم وكلمة المرور.", "signing": "جارٍ الدخول…", "signinok": "تم الدخول بنجاح",
        "qxResolving": "جارٍ التعرف على بلدك واختيار نطاق الخادم…", "qxConnecting": "جارٍ الاتصال بخادم كوتكس", "qxAuth": "جارٍ تسجيل الدخول إلى حساب كوتكس…", "qxLoad": "تم الاتصال — جارٍ تحميل BRLUSD_otc (300 شمعة)…", "qxFail": "تعذر الاتصال بكوتكس — تحقق من البريد وكلمة المرور", "qxEngine": "خطأ في محرك الخادم — أعد تشغيل التطبيق",
        "tgsave1": "توكن البوت المحفوظ", "tgonly": "بوت واحد فقط — عند حفظ توكن جديد يستبدل التوكن السابق.",
        "tgdel": "حذف التوكن المحفوظ", "tgcleared": "تم حذف التوكن المحفوظ",
    },
}

# ---------------------------------------------------------------- الأيقونات
ICONS = {
    "zap":    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "clock":  '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "send":   '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
    "link":   '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "list":   '<line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/>',
    "radio":  '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
    "trend":  '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "sett":   '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
    "login":  '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/>',
    "sun":    '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "moon":   '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "globe":  '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "user":   '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "lock":   '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "play":   '<polygon points="6 3 20 12 6 21 6 3"/>',
    "stop":   '<rect width="14" height="14" x="5" y="5" rx="2"/>',
    "copy":   '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "ok":     '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "no":     '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "check":  '<path d="M20 6 9 17l-5-5"/>',
    "up":     '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "down":   '<path d="m7 7 10 10"/><path d="M17 7v10H7"/>',
    "power":  '<path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.77.04"/>',
    "mouse":  '<path d="M4.037 4.688a.495.495 0 0 1 .651-.651l16 6.5a.5.5 0 0 1-.063.947l-6.124 1.58a2 2 0 0 0-1.438 1.435l-1.579 6.126a.5.5 0 0 1-.947.063z"/>',
    "slash":  '<path d="M5 19 19 5"/>',
    "minus":  '<path d="M5 12h14"/>',
    "vline":  '<path d="M12 3v18"/>',
    "square": '<rect x="4" y="4" width="16" height="16" rx="2"/>',
    "percent":'<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "brush":  '<path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08"/><path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z"/>',
    "eraser": '<path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/>',
    "trash":  '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
    "maximize":'<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" x2="14" y1="3" y2="10"/><line x1="3" x2="10" y1="21" y2="14"/>',
    "x":      '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "plus":   '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "save":   '<path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/>',
    "rotate": '<path d="M21 12a9 9 0 1 1-2.64-6.36L21 8"/><path d="M21 3v5h-5"/>',
    "panel":  '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>',
    "code":   '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "candle": '<path d="M9 5v4"/><rect x="7" y="9" width="4" height="6" rx="1"/><path d="M9 15v2"/><path d="M17 3v2"/><rect x="15" y="5" width="4" height="8" rx="1"/><path d="M17 13v3"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
    "chevl":  '<path d="m15 18-6-6 6-6"/>',
    "chevr":  '<path d="m9 18 6-6-6-6"/>',
    "chevd":  '<path d="m6 9 6 6 6-6"/>',
    "file":   '<path d="M15 2H5a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7z"/><path d="M14 2v5h5"/>',
    "bell":   '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "eye":    '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "eyeoff": '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>',
    "idcard": '<path d="M16 10h2"/><path d="M16 14h2"/><path d="M6.17 15a3 3 0 0 1 5.66 0"/><circle cx="9" cy="11" r="2"/><rect x="2" y="5" width="20" height="14" rx="2"/>',
    "loader": '<path d="M21 12a9 9 0 1 1-6.219-8.56"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
}

# ---------------------------------------------------------------- الشعار (BadiCharts — طبقات SVG)
LOGO_PAL = {
    True:  dict(ink="#FFFFFF", tag="#A8B8CA", g1="#43D9FF", g2="#4C8DFF"),
    False: dict(ink="#000000", tag="#5B6B80", g1="#12C4F0", g2="#3B6CF5"),
}
ICON_SVG = ('<g transform="translate(14 26)"><g fill="none" stroke="{g1}" stroke-width="5" stroke-linecap="round">'
            '<path d="M10 14V46"/><path d="M10 21H2"/><path d="M10 39H18"/>'
            '<rect x="24" y="12" width="16" height="32" rx="3" fill="{g1}" stroke="none"/>'
            '<path d="M32 12V0"/><path d="M32 44V54"/><path d="M54 22V54"/><path d="M54 29H46"/><path d="M54 47H62"/></g></g>')
LETTERS = [
    ("B", "ink", "M108.612 49.214Q108.612 53.262 105.783 55.631Q102.954 58.0 97.894 58.0H82.852V25.708H97.388Q102.31 25.708 105.093 27.962Q107.876 30.216 107.876 34.08Q107.876 36.932 106.381 38.818Q104.886 40.704 102.402 41.44Q105.208 42.038 106.91 44.223Q108.612 46.408 108.612 49.214ZM90.718 38.772H95.87Q97.802 38.772 98.837 37.921Q99.872 37.07 99.872 35.414Q99.872 33.758 98.837 32.884Q97.802 32.01 95.87 32.01H90.718ZM100.654 48.156Q100.654 46.454 99.527 45.488Q98.4 44.522 96.422 44.522H90.718V51.652H96.514Q98.492 51.652 99.573 50.755Q100.654 49.858 100.654 48.156Z"),
    ("a1", "ink", "M122.418 31.964Q125.132 31.964 127.179 33.068Q129.226 34.172 130.33 35.966V32.332H138.196V58.0H130.33V54.366Q129.18 56.16 127.133 57.264Q125.086 58.368 122.372 58.368Q119.244 58.368 116.668 56.735Q114.092 55.102 112.597 52.089Q111.102 49.076 111.102 45.12Q111.102 41.164 112.597 38.174Q114.092 35.184 116.668 33.574Q119.244 31.964 122.418 31.964ZM124.718 38.818Q122.372 38.818 120.739 40.497Q119.106 42.176 119.106 45.12Q119.106 48.064 120.739 49.789Q122.372 51.514 124.718 51.514Q127.064 51.514 128.697 49.812Q130.33 48.11 130.33 45.166Q130.33 42.222 128.697 40.52Q127.064 38.818 124.718 38.818Z"),
    ("d", "ink", "M153.152 31.964Q155.682 31.964 157.775 33.022Q159.868 34.08 161.064 35.874V23.96H168.93V58.0H161.064V54.32Q159.96 56.16 157.913 57.264Q155.866 58.368 153.152 58.368Q149.978 58.368 147.402 56.735Q144.826 55.102 143.331 52.089Q141.836 49.076 141.836 45.12Q141.836 41.164 143.331 38.174Q144.826 35.184 147.402 33.574Q149.978 31.964 153.152 31.964ZM155.452 38.818Q153.106 38.818 151.473 40.497Q149.84 42.176 149.84 45.12Q149.84 48.064 151.473 49.789Q153.106 51.514 155.452 51.514Q157.798 51.514 159.431 49.812Q161.064 48.11 161.064 45.166Q161.064 42.222 159.431 40.52Q157.798 38.818 155.452 38.818Z"),
    ("i", "ink", "M173.398 25.432Q173.398 23.592 174.709 22.373Q176.02 21.154 178.09 21.154Q180.114 21.154 181.425 22.373Q182.736 23.592 182.736 25.432Q182.736 27.226 181.425 28.445Q180.114 29.664 178.09 29.664Q176.02 29.664 174.709 28.445Q173.398 27.226 173.398 25.432ZM182.0 32.332V58.0H174.134V32.332Z"),
    ("C", "grad", "M202.108 25.34Q207.858 25.34 211.952 28.376Q216.046 31.412 217.426 36.656H208.778Q207.812 34.632 206.041 33.574Q204.27 32.516 202.016 32.516Q198.382 32.516 196.128 35.046Q193.874 37.576 193.874 41.808Q193.874 46.04 196.128 48.57Q198.382 51.1 202.016 51.1Q204.27 51.1 206.041 50.042Q207.812 48.984 208.778 46.96H217.426Q216.046 52.204 211.952 55.217Q207.858 58.23 202.108 58.23Q197.416 58.23 193.713 56.137Q190.01 54.044 187.94 50.318Q185.87 46.592 185.87 41.808Q185.87 37.024 187.94 33.275Q190.01 29.526 193.713 27.433Q197.416 25.34 202.108 25.34Z"),
    ("h", "grad", "M247.286 43.004V58.0H239.466V44.062Q239.466 41.486 238.132 40.06Q236.798 38.634 234.544 38.634Q232.29 38.634 230.956 40.06Q229.622 41.486 229.622 44.062V58.0H221.756V23.96H229.622V35.782Q230.818 34.08 232.888 33.068Q234.958 32.056 237.534 32.056Q241.95 32.056 244.618 34.977Q247.286 37.898 247.286 43.004Z"),
    ("a2", "grad", "M262.012 31.964Q264.726 31.964 266.773 33.068Q268.82 34.172 269.924 35.966V32.332H277.79V58.0H269.924V54.366Q268.774 56.16 266.727 57.264Q264.68 58.368 261.966 58.368Q258.838 58.368 256.262 56.735Q253.686 55.102 252.191 52.089Q250.696 49.076 250.696 45.12Q250.696 41.164 252.191 38.174Q253.686 35.184 256.262 33.574Q258.838 31.964 262.012 31.964ZM264.312 38.818Q261.966 38.818 260.333 40.497Q258.7 42.176 258.7 45.12Q258.7 48.064 260.333 49.789Q261.966 51.514 264.312 51.514Q266.658 51.514 268.291 49.812Q269.924 48.11 269.924 45.166Q269.924 42.222 268.291 40.52Q266.658 38.818 264.312 38.818Z"),
    ("r", "grad", "M298.91 32.056V40.382H296.748Q293.804 40.382 292.332 41.647Q290.86 42.912 290.86 46.086V58.0H282.994V32.332H290.86V36.61Q292.24 34.494 294.31 33.275Q296.38 32.056 298.91 32.056Z"),
    ("t", "grad", "M316.488 51.33V58.0H312.486Q308.208 58.0 305.816 55.907Q303.424 53.814 303.424 49.076V38.864H300.296V32.332H303.424V26.076H311.29V32.332H316.442V38.864H311.29V49.168Q311.29 50.318 311.842 50.824Q312.394 51.33 313.682 51.33Z"),
    ("s", "grad", "M318.978 49.582H326.752Q326.89 50.916 327.994 51.744Q329.098 52.572 330.708 52.572Q332.18 52.572 332.985 51.997Q333.79 51.422 333.79 50.502Q333.79 49.398 332.64 48.869Q331.49 48.34 328.914 47.696Q326.154 47.052 324.314 46.339Q322.474 45.626 321.14 44.085Q319.806 42.544 319.806 39.922Q319.806 37.714 321.025 35.897Q322.244 34.08 324.613 33.022Q326.982 31.964 330.248 31.964Q335.078 31.964 337.861 34.356Q340.644 36.748 341.058 40.704H333.79Q333.606 39.37 332.617 38.588Q331.628 37.806 330.018 37.806Q328.638 37.806 327.902 38.335Q327.166 38.864 327.166 39.784Q327.166 40.888 328.339 41.44Q329.512 41.992 331.996 42.544Q334.848 43.28 336.642 43.993Q338.436 44.706 339.793 46.293Q341.15 47.88 341.196 50.548Q341.196 52.802 339.931 54.573Q338.666 56.344 336.297 57.356Q333.928 58.368 330.8 58.368Q327.442 58.368 324.82 57.218Q322.198 56.068 320.68 54.067Q319.162 52.066 318.978 49.582Z"),
]
TAGLINE = (
           "M86.508 73.904Q87.7845 73.904 88.77924999999999 74.53075Q89.774 75.1575 90.2225 76.3075H88.647Q88.3365 75.675 87.78450000000001 75.36449999999999Q87.2325 75.054 86.508 75.054Q85.7145 75.054 85.0935 75.4105Q84.4725 75.767 84.12174999999999 76.434Q83.771 77.101 83.771 77.9865Q83.771 78.872 84.12174999999999 79.539Q84.4725 80.206 85.0935 80.56825Q85.7145 80.9305 86.508 80.9305Q87.2325 80.9305 87.78450000000001 80.62Q88.3365 80.3095 88.647 79.677H90.2225Q89.774 80.827 88.77924999999999 81.44800000000001Q87.7845 82.069 86.508 82.069Q85.381 82.069 84.4495 81.54575Q83.518 81.0225 82.97175 80.091Q82.4255 79.1595 82.4255 77.9865Q82.4255 76.8135 82.97175 75.882Q83.518 74.9505 84.45525 74.42725Q85.3925 73.904 86.508 73.904ZM101.7345 74.0075V82.0H100.42349999999999V78.504H96.663V82.0H95.35199999999999V74.0075H96.663V77.4345H100.42349999999999V74.0075Z" +
           "M111.87799999999999 80.367H108.5315L107.95649999999999 82.0H106.588L109.45149999999998 73.996H110.96949999999998L113.83299999999998 82.0H112.45299999999999ZM111.50999999999999 79.2975 110.21049999999998 75.583 108.89949999999999 79.2975ZM122.82649999999998 82.0 120.98649999999999 78.803H119.98599999999999V82.0H118.67499999999998V74.0075H121.43499999999999Q122.35499999999999 74.0075 122.99324999999999 74.3295Q123.63149999999999 74.6515 123.94774999999998 75.19200000000001Q124.26399999999998 75.7325 124.26399999999998 76.3995Q124.26399999999998 77.1815 123.80974999999998 77.81975Q123.35549999999999 78.458 122.41249999999998 78.688L124.39049999999999 82.0ZM119.98599999999999 77.7565H121.43499999999999Q122.17099999999999 77.7565 122.54475 77.3885Q122.91849999999998 77.0205 122.91849999999998 76.3995Q122.91849999999998 75.7785 122.55049999999999 75.42775Q122.18249999999999 75.077 121.43499999999999 75.077H119.98599999999999Z" +
           "M134.7065 74.0075V75.077H132.579V82.0H131.268V75.077H129.129V74.0075ZM140.94 74.0075V82.0H139.62900000000002V74.0075Z" +
           "M152.8315 82.0H151.5205L147.576 76.0315V82.0H146.26500000000001V73.996H147.576L151.5205 79.953V73.996H152.8315ZM163.941 76.3075Q163.6305 75.7095 163.07850000000002 75.40475Q162.5265 75.1 161.80200000000002 75.1Q161.0085 75.1 160.3875 75.4565Q159.7665 75.813 159.41575 76.4685Q159.065 77.124 159.065 77.9865Q159.065 78.849 159.41575 79.51025Q159.7665 80.1715 160.3875 80.52799999999999Q161.0085 80.8845 161.80200000000002 80.8845Q162.8715 80.8845 163.5385 80.2865Q164.2055 79.6885 164.35500000000002 78.665H161.3535V77.6185H165.758V78.642Q165.63150000000002 79.5735 165.09675000000001 80.3555Q164.562 81.1375 163.70525 81.60325Q162.8485 82.069 161.80200000000002 82.069Q160.675 82.069 159.7435 81.54575Q158.812 81.0225 158.26575000000003 80.091Q157.7195 79.1595 157.7195 77.9865Q157.7195 76.8135 158.26575000000003 75.882Q158.812 74.9505 159.74925000000002 74.42725Q160.68650000000002 73.904 161.80200000000002 73.904Q163.07850000000002 73.904 164.07325000000003 74.53075Q165.068 75.1575 165.5165 76.3075Z" +
           "M178.547 75.0655V77.4115H181.30700000000002V78.481H178.547V80.9305H181.65200000000002V82.0H177.23600000000002V73.996H181.65200000000002V75.0655ZM193.4285 82.0H192.1175L188.173 76.0315V82.0H186.86200000000002V73.996H188.173L192.1175 79.953V73.996H193.4285Z" +
           "M204.538 76.3075Q204.22750000000002 75.7095 203.6755 75.40475Q203.1235 75.1 202.39900000000003 75.1Q201.6055 75.1 200.98450000000003 75.4565Q200.36350000000002 75.813 200.01275 76.4685Q199.662 77.124 199.662 77.9865Q199.662 78.849 200.01275 79.51025Q200.36350000000002 80.1715 200.98450000000003 80.52799999999999Q201.6055 80.8845 202.39900000000003 80.8845Q203.4685 80.8845 204.1355 80.2865Q204.8025 79.6885 204.95200000000003 78.665H201.95050000000003V77.6185H206.35500000000002V78.642Q206.22850000000003 79.5735 205.69375000000002 80.3555Q205.15900000000002 81.1375 204.30225000000002 81.60325Q203.4455 82.069 202.39900000000003 82.069Q201.27200000000002 82.069 200.34050000000002 81.54575Q199.40900000000002 81.0225 198.86275 80.091Q198.31650000000002 79.1595 198.31650000000002 77.9865Q198.31650000000002 76.8135 198.86275 75.882Q199.40900000000002 74.9505 200.34625000000003 74.42725Q201.28350000000003 73.904 202.39900000000003 73.904Q203.67550000000003 73.904 204.67025 74.53075Q205.66500000000002 75.1575 206.11350000000002 76.3075ZM212.554 74.0075V82.0H211.24300000000002V74.0075Z" +
           "M224.4455 82.0H223.1345L219.19 76.0315V82.0H217.87900000000002V73.996H219.19L223.1345 79.953V73.996H224.4455ZM231.0815 75.0655V77.4115H233.84150000000002V78.481H231.0815V80.9305H234.18650000000002V82.0H229.77050000000003V73.996H234.18650000000002V75.0655Z")

LOGO_LAYERS = ([{"n": "icon", "kind": "icon", "delay": 150}] +
               [{"n": l[0], "kind": "rise", "delay": 1000 + 70 * i} for i, l in enumerate(LETTERS)] +
               [{"n": "tag", "kind": "fade", "delay": 2300}])


def logo_uri(name, dark):
    p = LOGO_PAL[bool(dark)]
    if name == "icon":
        body = ICON_SVG.format(**p)
    elif name == "tag":
        body = f'<path fill="{p["tag"]}" fill-opacity="1" d="{TAGLINE}"/>'
    else:
        _, kind, d = next(l for l in LETTERS if l[0] == name)
        fill = p["ink"] if kind == "ink" else "url(#g)"
        body = f'<path fill="{fill}" d="{d}"/>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="2 12 354 80"><defs>'
           '<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="184.4" y1="0" x2="342.7" y2="0">'
           f'<stop offset="0" stop-color="{p["g1"]}"/><stop offset="1" stop-color="{p["g2"]}"/>'
           f'</linearGradient></defs>{body}</svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def logo_uri_full(dark):
    """شعار التطبيق الكامل (الأيقونة + الحروف + السطر النصي) بـ SVG واحد — لصفحة الويب المدمجة."""
    p = LOGO_PAL[bool(dark)]
    bodies = [ICON_SVG.format(**p)]
    for _l0, kind, d in LETTERS:
        fill = p["ink"] if kind == "ink" else "url(#g)"
        bodies.append(f'<path fill="{fill}" d="{d}"/>')
    bodies.append(f'<path fill="{p["tag"]}" fill-opacity="1" d="{TAGLINE}"/>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="2 12 354 80"><defs>'
           '<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="184.4" y1="0" x2="342.7" y2="0">'
           f'<stop offset="0" stop-color="{p["g1"]}"/><stop offset="1" stop-color="{p["g2"]}"/>'
           f'</linearGradient></defs>{"".join(bodies)}</svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def icon_uri(name, color):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
           f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
           f'stroke-linejoin="round">{ICONS[name]}</svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def make_app_icon():
    """أيقونة النافذة وشريط المهام: علامة BadiCharts من SVG بعدة مقاسات
    (تُتجاهل بهدوء إن لم يتوفر QtSvg)."""
    try:
        from PySide6.QtCore import QByteArray, Qt
        from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
        from PySide6.QtSvg import QSvgRenderer
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="8 16 76 76">'
               + ICON_SVG.format(**LOGO_PAL[True]) + '</svg>')
        r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        icon = QIcon()
        for s in (16, 24, 32, 48, 64, 128, 256):
            img = QImage(s, s, QImage.Format_ARGB32)
            img.fill(Qt.transparent)
            pt = QPainter(img)
            r.render(pt)
            pt.end()
            icon.addPixmap(QPixmap.fromImage(img))
        return icon
    except Exception:
        return QIcon()

# ---------------------------------------------------------------- السوق: كوتكس حقيقي + OTC
ASSETS = {
    "real": [
        {"name": "EUR/USD", "base": 1.0865, "vol": 0.0009, "dec": 5},
        {"name": "GBP/USD", "base": 1.2712, "vol": 0.0011, "dec": 5},
        {"name": "USD/JPY", "base": 151.42, "vol": 0.0010, "dec": 3},
        {"name": "EUR/JPY", "base": 164.28, "vol": 0.0011, "dec": 3},
        {"name": "GBP/JPY", "base": 192.44, "vol": 0.0013, "dec": 3},
        {"name": "AUD/CAD", "base": 0.8942, "vol": 0.0010, "dec": 5},
        {"name": "USD/CHF", "base": 0.9052, "vol": 0.0009, "dec": 5},
        {"name": "EUR/GBP", "base": 0.8546, "vol": 0.0008, "dec": 5},
        {"name": "BTC/USD", "base": 67240.0, "vol": 0.011, "dec": 2},
        {"name": "ETH/USD", "base": 3268.0, "vol": 0.013, "dec": 2},
        {"name": "XAU/USD", "base": 2382.4, "vol": 0.006, "dec": 2},
    ],
    "otc": [
        {"name": "EUR/USD OTC", "base": 1.0862, "vol": 0.0012, "dec": 5},
        {"name": "GBP/USD OTC", "base": 1.2709, "vol": 0.0014, "dec": 5},
        {"name": "USD/JPY OTC", "base": 151.38, "vol": 0.0012, "dec": 3},
        {"name": "GBP/JPY OTC", "base": 192.40, "vol": 0.0015, "dec": 3},
        {"name": "AUD/CAD OTC", "base": 0.8938, "vol": 0.0013, "dec": 5},
        {"name": "EUR/GBP OTC", "base": 0.8544, "vol": 0.0011, "dec": 5},
        {"name": "NZD/USD OTC", "base": 0.5992, "vol": 0.0014, "dec": 5},
        {"name": "USD/PKR OTC", "base": 278.42, "vol": 0.0016, "dec": 3},
        {"name": "USD/BRL OTC", "base": 5.1240, "vol": 0.0018, "dec": 4},
        {"name": "USD/INR OTC", "base": 83.42, "vol": 0.0013, "dec": 3},
        {"name": "USD/TRY OTC", "base": 32.28, "vol": 0.0020, "dec": 3},
        {"name": "BTC/USD OTC", "base": 67210.0, "vol": 0.013, "dec": 2},
    ],
}
# الفريمات الكاملة (طلب المستخدم): 10 ثوانٍ و30 ثانية و2 و3 و10 و30 دقيقة و4 ساعات ويوم —
# مع الإبقاء على الفريمات القديمة (5 ثوانٍ و15 ثانية و1 و5 و15 دقيقة وساعة)
TFS = [("5s", 5), ("10s", 10), ("15s", 15), ("30s", 30), ("1m", 60), ("2m", 120), ("3m", 180),
       ("5m", 300), ("10m", 600), ("15m", 900), ("30m", 1800), ("1H", 3600), ("4H", 14400), ("1D", 86400)]

# ---------------------------------------------- أعلام ونِسَب الدفع لشريط العملات
def _flag_uri(body):
    """علم مصغّر SVG (يُرسم في كل الأنظمة بلا اعتماد على خطوط الإيموجي)."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14">' + body
           + '<rect x="0.4" y="0.4" width="19.2" height="13.2" rx="2" fill="none"'
             ' stroke="rgba(128,128,128,.35)" stroke-width="0.8"/></svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


FLAGS = {
    "USD": '<rect width="20" height="14" fill="#b22234"/><path d="M0 2.6h20M0 5.8h20M0 9h20M0 12.2h20" stroke="#fff" stroke-width="1.2"/><rect width="9.5" height="7.6" fill="#3c3b6e"/>',
    "EUR": '<rect width="20" height="14" fill="#2b4bd7"/><circle cx="10" cy="7" r="3.1" fill="none" stroke="#f8d33e" stroke-width="1.2" stroke-dasharray="1.15 1.32"/>',
    "GBP": '<rect width="20" height="14" fill="#012169"/><path d="M0 0l20 14M20 0L0 14" stroke="#fff" stroke-width="2.6"/><path d="M0 0l20 14M20 0L0 14" stroke="#c8102e" stroke-width="1.1"/><path d="M10 0v14M0 7h20" stroke="#fff" stroke-width="4.2"/><path d="M10 0v14M0 7h20" stroke="#c8102e" stroke-width="2.2"/>',
    "JPY": '<rect width="20" height="14" fill="#f4f4f4"/><circle cx="10" cy="7" r="3.4" fill="#bc002d"/>',
    "AUD": '<rect width="20" height="14" fill="#012169"/><path d="M0 0l8 5.6M8 0L0 5.6" stroke="#fff" stroke-width="1.3"/><path d="M4 0v5.6M0 2.8h8" stroke="#fff" stroke-width="1.9"/><path d="M4 0v5.6M0 2.8h8" stroke="#c8102e" stroke-width="0.9"/><circle cx="14.5" cy="4.5" r="1" fill="#fff"/><circle cx="16" cy="8.5" r="1" fill="#fff"/><circle cx="13" cy="10.5" r="0.9" fill="#fff"/>',
    "CAD": '<rect width="20" height="14" fill="#f4f4f4"/><rect width="5" height="14" fill="#d80621"/><rect x="15" width="5" height="14" fill="#d80621"/><path d="M10 3l2.4 4.2-2.4 4-2.4-4z" fill="#d80621"/>',
    "CHF": '<rect width="20" height="14" fill="#da291c"/><path d="M10 3.6v6.8M6.6 7h6.8" stroke="#fff" stroke-width="2.1"/>',
    "NZD": '<rect width="20" height="14" fill="#012169"/><path d="M0 0l8 5.6M8 0L0 5.6" stroke="#fff" stroke-width="1.2"/><path d="M4 0v5.6M0 2.8h8" stroke="#fff" stroke-width="1.7"/><path d="M4 0v5.6M0 2.8h8" stroke="#c8102e" stroke-width="0.8"/><circle cx="14.5" cy="5" r="1" fill="#c8102e"/><circle cx="16" cy="9.5" r="1" fill="#c8102e"/>',
    "PKR": '<rect width="20" height="14" fill="#01411c"/><rect width="5" height="14" fill="#f4f4f4"/><circle cx="12" cy="7" r="3" fill="#f4f4f4"/><circle cx="13.2" cy="6.2" r="2.6" fill="#01411c"/>',
    "BRL": '<rect width="20" height="14" fill="#009c3b"/><path d="M10 2.2l7 4.8-7 4.8-7-4.8z" fill="#f8d33e"/><circle cx="10" cy="7" r="2.1" fill="#002776"/>',
    "INR": '<rect width="20" height="14" fill="#f93"/><rect y="4.67" width="20" height="4.66" fill="#f4f4f4"/><rect y="9.33" width="20" height="4.67" fill="#128807"/><circle cx="10" cy="7" r="1.5" fill="none" stroke="#008" stroke-width="0.7"/>',
    "TRY": '<rect width="20" height="14" fill="#e30a17"/><circle cx="8" cy="7" r="3.1" fill="#f4f4f4"/><circle cx="8.9" cy="7" r="2.5" fill="#e30a17"/><path d="M13.2 7l2.2-0.7-1.4 1.9 0.1-2.3 1.3 1.9z" fill="#f4f4f4"/>',
    "BTC": '<rect width="20" height="14" fill="#f7931a"/><text x="10" y="10.6" font-size="9.5" font-weight="bold" text-anchor="middle" fill="#fff" font-family="Arial,sans-serif">\u20bf</text>',
    "ETH": '<rect width="20" height="14" fill="#454a75"/><path d="M10 1.8l4.2 5.4L10 9.8 5.8 7.2z" fill="#f4f4f4" fill-opacity="0.92"/><path d="M10 10.9l4.2-2.7L10 12.4l-4.2-4.2z" fill="#f4f4f4" fill-opacity="0.6"/>',
    "XAU": '<rect width="20" height="14" fill="#3d3325"/><path d="M3.4 10l1.5-2.8h2.9l1.5 2.8z" fill="#e8b923"/><path d="M10.7 10l1.5-2.8h2.9l1.5 2.8z" fill="#f6cf3f"/>',
}


def _flag_code_clean(s):
    """تنظيف اسم العملة من لاحقة OTC وأي قوسين: «BRL (OTC)» → «BRL»."""
    s = str(s or "").strip()
    s = s.split("(")[0]                    # اسقط كل ما بعد القوسين
    s = re.sub(r"\bOTC\b", "", s, flags=re.I)
    return s.strip()


def asset_flag(name):
    """علم العملة الأولى في الزوج كـ data-URI (BTC/ETH/XAU لها أيقونة خاصة).
    v14.1: تنظيف لاحقة (OTC) — الأسماء الحقيقية من الخادم مثل «USD/BRL (OTC)»
    كانت تفشل في البحث عن العلم بسبب القوسين فيظهر علم واحد فقط."""
    base = _flag_code_clean(str(name).split("/")[0])
    return _flag_uri(FLAGS[base]) if base in FLAGS else ""


_RIM_GRAY = ('<rect x="0.4" y="0.4" width="19.2" height="13.2" rx="2" fill="none"'
             ' stroke="rgba(128,128,128,.35)" stroke-width="0.8"/>')
_RIM_WHITE = ('<rect x="0.4" y="0.4" width="19.2" height="13.2" rx="2" fill="none"'
              ' stroke="rgba(255,255,255,.9)" stroke-width="1.4"/>')


def _flag_cell(code, rim):
    """خلية علم واحدة داخل SVG مدموج — والعملة غير المعروفة تُرسم كشارة
    رمز محايدة (لا يظهر أبداً زوج بعلم واحد ناقص — طلب المستخدم:
    «العملة فيها عملتين يجب أن تضع علمين وليس علم واحد»)."""
    body = FLAGS.get(code)
    if body is None:
        body = ('<rect width="20" height="14" rx="2" fill="#4b5563"/>'
                f'<text x="10" y="9.6" font-size="6.2" font-weight="bold" '
                f'text-anchor="middle" fill="#e5e7eb" '
                f'font-family="Arial,sans-serif">{code[:4] or "?"}</text>')
    return f'<g transform="scale(0.7)">{body}{rim}</g>'


def pair_flag_uri(name):
    """علمان جنب بعض في SVG واحد مدموجين بشكل نظيف (العملة الأولى + عملة الاقتباس).
    v14.1: يعمل مع كل صيغ الأسماء — «USD/BRL (OTC)» و«USD/BRL OTC» و«USD/BRL» —
    وإن نقص علم أحد الطرفين تُرسم شارة رمزه بدل أن يسقط الزوج لعلم واحد."""
    parts = str(name).split("/")
    base = _flag_code_clean(parts[0])
    quote = _flag_code_clean(parts[1]) if len(parts) > 1 else ""
    if not quote:
        return asset_flag(name)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 27 14">'
           f'<g transform="translate(0,2.1)">{_flag_cell(base, _RIM_GRAY)}</g>'
           f'<g transform="translate(13,2.1)">{_flag_cell(quote, _RIM_WHITE)}</g></svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


# ═════════════════════════════════════════════════════════════════════════════
# v13.2 (طلب المستخدم): أعلام باقي العملات — كل العملات في جدول الخادم لها علم
# (كانت بعض العملات بلا علم). أضيف أعلام العملات الناقصة + شارات للعملات
# الرقمية والسلع والمؤشرات (بلا علم دولة).
# ═════════════════════════════════════════════════════════════════════════════
FLAGS["BDT"] = '<rect width="20" height="14" fill="#006a4e"/><circle cx="9" cy="7" r="3.2" fill="#f42a41"/>'
FLAGS["EGP"] = '<rect width="20" height="14" fill="#ce1126"/><rect y="4.67" width="20" height="4.66" fill="#fff"/><rect y="9.33" width="20" height="4.67" fill="#000"/><path d="M10 6.2l1 1.6-1 1.6-1-1.6z" fill="#c09300"/>'
FLAGS["NGN"] = '<rect width="20" height="14" fill="#fff"/><rect width="6.7" height="14" fill="#008751"/><rect x="13.3" width="6.7" height="14" fill="#008751"/>'
FLAGS["IDR"] = '<rect width="20" height="14" fill="#fff"/><rect width="20" height="7" fill="#ce1126"/>'
FLAGS["ARS"] = '<rect width="20" height="14" fill="#74acdf"/><rect y="4.67" width="20" height="4.66" fill="#fff"/><circle cx="10" cy="7" r="1.5" fill="#f6b40e"/>'
FLAGS["COP"] = '<rect width="20" height="7" fill="#fcd116"/><rect y="7" width="20" height="3.5" fill="#003893"/><rect y="10.5" width="20" height="3.5" fill="#ce1126"/>'
FLAGS["DZD"] = '<rect width="10" height="14" fill="#006233"/><rect x="10" width="10" height="14" fill="#fff"/><circle cx="10" cy="7" r="2.9" fill="none" stroke="#d21034" stroke-width="1.1"/><circle cx="11" cy="7" r="2.3" fill="#fff"/><circle cx="10.4" cy="7" r="2.1" fill="#d21034"/>'
FLAGS["MXN"] = '<rect width="20" height="14" fill="#006847"/><rect x="6.7" width="6.6" height="14" fill="#fff"/><rect x="13.3" width="6.7" height="14" fill="#ce1126"/><circle cx="10" cy="7" r="1.6" fill="#8c6f2f"/>'
FLAGS["PHP"] = '<rect width="20" height="7" fill="#0038a8"/><rect y="7" width="20" height="7" fill="#ce1126"/><path d="M0 0l8.5 7L0 14z" fill="#fff"/><circle cx="3" cy="7" r="1.7" fill="#fcd116"/>'
FLAGS["ZAR"] = '<rect width="20" height="14" fill="#e03c31"/><rect width="20" height="7" fill="#001489"/><path d="M0 0l11 7L0 14z" fill="#007749"/><path d="M0 2.2l8 4.8-8 4.8z" fill="#fff"/><path d="M0 3.8l5.6 3.2L0 10.2z" fill="#ffb81c"/><path d="M0 0l11 7L0 14" stroke="#000" stroke-width="0.7" fill="none"/>'
FLAGS["XAG"] = '<rect width="20" height="14" fill="#4b5563"/><path d="M3.4 10l1.5-2.8h2.9l1.5 2.8z" fill="#e5e7eb"/><path d="M10.7 10l1.5-2.8h2.9l1.5 2.8z" fill="#f3f4f6"/>'
FLAGS["HKD"] = '<rect width="20" height="14" fill="#de2910"/><circle cx="10" cy="7" r="3" fill="#fff"/><circle cx="10" cy="7" r="1.1" fill="#de2910"/>'


def _badge_uri(body, label, fg="#FFFFFF", dy=10.4, fs=8.6):
    """شارة أصل SVG — للعملات الرقمية والسلع والمؤشرات (بلا علم دولة)."""
    txt = (f'<text x="10" y="{dy}" font-size="{fs}" font-weight="bold" '
           f'text-anchor="middle" fill="{fg}" font-family="Arial,sans-serif">{label}</text>')
    return _flag_uri(body + txt)


# شارات العملات الرقمية والسلع والمؤشرات — بمفتاح رمز الخادم نفسه (طلب المستخدم:
# قائمة العملات التي يجلبها السكريبت كلها لها علم/شارة)
SINGLE_BADGES = {
    "AXSUSD_otc": _badge_uri('<rect width="20" height="14" fill="#0050d8"/>', "AXS"),
    "USCrude_otc": _flag_uri('<rect width="20" height="14" fill="#1f2a33"/><path d="M10 2.4c2.7 3.5 4 5.6 4 7.3a4 4 0 0 1-8 0c0-1.7 1.3-3.8 4-7.3z" fill="#e8b923"/>'),
    "UKBrent_otc": _flag_uri('<rect width="20" height="14" fill="#0b3d2c"/><path d="M10 2.4c2.7 3.5 4 5.6 4 7.3a4 4 0 0 1-8 0c0-1.7 1.3-3.8 4-7.3z" fill="#f6cf3f"/>'),
    "ETCUSD_otc": _badge_uri('<rect width="20" height="14" fill="#328332"/>', "ETC"),
    "ATOUSD_otc": _flag_uri('<rect width="20" height="14" fill="#2e2d50"/><circle cx="10" cy="7" r="2" fill="none" stroke="#fff" stroke-width="0.9"/><ellipse cx="10" cy="7" rx="4.4" ry="1.7" fill="none" stroke="#fff" stroke-width="0.8" transform="rotate(24 10 7)"/><ellipse cx="10" cy="7" rx="4.4" ry="1.7" fill="none" stroke="#fff" stroke-width="0.8" transform="rotate(-24 10 7)"/>'),
    "AVAUSD_otc": _badge_uri('<rect width="20" height="14" fill="#e84142"/>', "AVAX"),
    "BCHUSD_otc": _badge_uri('<rect width="20" height="14" fill="#8dc351"/>', "\u20bf", fs=9.6),
    "BNBUSD_otc": _badge_uri('<rect width="20" height="14" fill="#f3ba2f"/>', "BNB"),
    "BTCUSD_otc": _badge_uri('<rect width="20" height="14" fill="#f7931a"/>', "\u20bf", fs=9.6),
    "ETHUSD_otc": _flag_uri('<rect width="20" height="14" fill="#454a75"/><path d="M10 1.8l4.2 5.4L10 9.8 5.8 7.2z" fill="#f4f4f4" fill-opacity="0.92"/><path d="M10 10.9l4.2-2.7L10 12.4l-4.2-4.2z" fill="#f4f4f4" fill-opacity="0.6"/>'),
    "DASUSD_otc": _badge_uri('<rect width="20" height="14" fill="#008ce7"/>', "DASH"),
    "DOTUSD_otc": _flag_uri('<rect width="20" height="14" fill="#e6007a"/><circle cx="10" cy="4" r="1.7" fill="#fff"/><circle cx="6.2" cy="10" r="1.7" fill="#fff"/><circle cx="13.8" cy="10" r="1.7" fill="#fff"/>'),
    "LINUSD_otc": _flag_uri('<rect width="20" height="14" fill="#2a5ada"/><path d="M10 2.4l3 1.7v3.5l-3 1.7-3-1.7V4.1z" fill="#fff"/><path d="M10 7.4l3 1.7v3.5l-3 1.7-3-1.7V9.1z" fill="#fff" fill-opacity="0.75"/>'),
    "LTCUSD_otc": _badge_uri('<rect width="20" height="14" fill="#345d9d"/>', "\u0141", fs=9.8),
    "SOLUSD_otc": _flag_uri('<rect width="20" height="14" fill="#141414"/><path d="M5 4.6h9.2l-1.9 1.9H3.1z" fill="#14f195"/><path d="M5 7.1h9.2L12.3 9H3.1z" fill="#9945ff"/><path d="M5 9.6h9.2l-1.9 1.9H3.1z" fill="#14f195"/>'),
    "TONUSD_otc": _badge_uri('<rect width="20" height="14" fill="#0098ea"/>', "TON"),
    "TRUUSD_otc": _badge_uri('<rect width="20" height="14" fill="#1f2a5b"/>', "TRUMP", fs=7.2),
    "XRPUSD_otc": _badge_uri('<rect width="20" height="14" fill="#23292f"/>', "XRP"),
    "ZECUSD_otc": _badge_uri('<rect width="20" height="14" fill="#f4b728"/>', "Z"),
    "XAGUSD_otc": _badge_uri('<rect width="20" height="14" fill="#4b5563"/>', "Ag"),
    "XAUUSD_otc": _badge_uri('<rect width="20" height="14" fill="#3d3325"/>', "Au", fg="#f6cf3f"),
    "XAGUSD": _badge_uri('<rect width="20" height="14" fill="#4b5563"/>', "Ag"),
    "XAUUSD": _badge_uri('<rect width="20" height="14" fill="#3d3325"/>', "Au", fg="#f6cf3f"),
    "F40EUR": _flag_uri('<rect width="6.7" height="14" fill="#0055a4"/><rect x="6.7" width="6.6" height="14" fill="#fff"/><rect x="13.3" width="6.7" height="14" fill="#ef4135"/>'),
    "STXEUR": _flag_uri('<rect width="20" height="14" fill="#2b4bd7"/><circle cx="10" cy="7" r="3.1" fill="none" stroke="#f8d33e" stroke-width="1.2" stroke-dasharray="1.15 1.32"/><text x="10" y="9.2" font-size="6.4" font-weight="bold" text-anchor="middle" fill="#f8d33e" font-family="Arial,sans-serif">50</text>'),
    "AXJAUD": _flag_uri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14"><rect width="20" height="14" fill="#012169"/><path d="M0 0l8 5.6M8 0L0 5.6" stroke="#fff" stroke-width="1.3"/><path d="M4 0v5.6M0 2.8h8" stroke="#fff" stroke-width="1.9"/><path d="M4 0v5.6M0 2.8h8" stroke="#c8102e" stroke-width="0.9"/><circle cx="14.5" cy="4.5" r="1" fill="#fff"/><circle cx="16" cy="8.5" r="1" fill="#fff"/><circle cx="13" cy="10.5" r="0.9" fill="#fff"/></svg>'),
    "CHIA50": _flag_uri('<rect width="20" height="14" fill="#de2910"/><path d="M4.4 2.6l0.9 2.6h2.7l-2.2 1.7 0.9 2.6-2.3-1.6-2.3 1.6 0.9-2.6L0.8 5.2h2.7z" fill="#ffde00" transform="scale(0.85) translate(0.6,0.4)"/><circle cx="12.6" cy="3.4" r="0.8" fill="#ffde00"/><circle cx="14.6" cy="6" r="0.8" fill="#ffde00"/><circle cx="14.6" cy="9" r="0.8" fill="#ffde00"/><circle cx="12.6" cy="11.4" r="0.8" fill="#ffde00"/>'),
    "FTSGBP": _flag_uri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14"><rect width="20" height="14" fill="#012169"/><path d="M0 0l20 14M20 0L0 14" stroke="#fff" stroke-width="2.6"/><path d="M0 0l20 14M20 0L0 14" stroke="#c8102e" stroke-width="1.1"/><path d="M10 0v14M0 7h20" stroke="#fff" stroke-width="4.2"/><path d="M10 0v14M0 7h20" stroke="#c8102e" stroke-width="2.2"/></svg>'),
    "JPXJPY": _flag_uri('<rect width="20" height="14" fill="#f4f4f4"/><circle cx="10" cy="7" r="3.4" fill="#bc002d"/>'),
    "HSIHKD": _flag_uri('<rect width="20" height="14" fill="#de2910"/><circle cx="10" cy="7" r="3" fill="#fff"/><circle cx="10" cy="7" r="1.1" fill="#de2910"/>'),
    "IBXEUR": _flag_uri('<rect width="20" height="3.5" fill="#aa151b"/><rect y="3.5" width="20" height="7" fill="#f1bf00"/><rect y="10.5" width="20" height="3.5" fill="#aa151b"/>'),
}

# ═════════════════════════════════════════════════════════════════════════════
# v13.2 (طلب المستخدم): قائمة كل العملات التي يجلبها السكريبت (جدول الترمينال
# نفسه) مع الاسم الحقيقي كما يعرضه Quotex — الواجهة تعرض هذه الأسماء الحقيقية
# وليس الأسماء النظامية المولّدة (BRLUSD_otc تُعرض «USD/BRL (OTC)» مثلاً).
# ═════════════════════════════════════════════════════════════════════════════
QX_ASSET_NAMES = {
    "AXSUSD_otc": "Axie Infinity (OTC)",
    "BRLUSD_otc": "USD/BRL (OTC)",
    "EURNZD_otc": "EUR/NZD (OTC)",
    "USCrude_otc": "USCrude (OTC)",
    "USDBDT_otc": "USD/BDT (OTC)",
    "USDEGP_otc": "USD/EGP (OTC)",
    "USDNGN_otc": "USD/NGN (OTC)",
    "CADCHF_otc": "CAD/CHF (OTC)",
    "UKBrent_otc": "UKBrent (OTC)",
    "USDJPY": "USD/JPY",
    "USDIDR_otc": "USD/IDR (OTC)",
    "NZDUSD_otc": "NZD/USD (OTC)",
    "EURJPY": "EUR/JPY",
    "AUDJPY": "AUD/JPY",
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "CADJPY": "CAD/JPY",
    "EURCAD": "EUR/CAD",
    "AUDUSD": "AUD/USD",
    "EURGBP": "EUR/GBP",
    "CHFJPY": "CHF/JPY",
    "GBPJPY": "GBP/JPY",
    "ETCUSD_otc": "Ethereum Classic (OTC)",
    "AUDCAD": "AUD/CAD",
    "EURAUD": "EUR/AUD",
    "USDCAD": "USD/CAD",
    "EURCHF": "EUR/CHF",
    "F40EUR": "CAC 40",
    "GBPAUD": "GBP/AUD",
    "GBPCAD": "GBP/CAD",
    "GBPCHF": "GBP/CHF",
    "STXEUR": "EURO STOXX 50",
    "USDCHF": "USD/CHF",
    "AXJAUD": "S&P/ASX 200",
    "CHIA50": "FTSE China A50 Index",
    "FTSGBP": "FTSE 100",
    "JPXJPY": "Nikkei 225",
    "ATOUSD_otc": "Cosmos (OTC)",
    "AUDCAD_otc": "AUD/CAD (OTC)",
    "AUDCHF_otc": "AUD/CHF (OTC)",
    "AUDJPY_otc": "AUD/JPY (OTC)",
    "AUDUSD_otc": "AUD/USD (OTC)",
    "AVAUSD_otc": "Avalanche (OTC)",
    "BCHUSD_otc": "Bitcoin Cash (OTC)",
    "BNBUSD_otc": "Binance Coin (OTC)",
    "BTCUSD_otc": "Bitcoin (OTC)",
    "CADJPY_otc": "CAD/JPY (OTC)",
    "CHFJPY_otc": "CHF/JPY (OTC)",
    "DASUSD_otc": "Dash (OTC)",
    "DOTUSD_otc": "Polkadot (OTC)",
    "ETHUSD_otc": "Ethereum (OTC)",
    "EURAUD_otc": "EUR/AUD (OTC)",
    "EURCAD_otc": "EUR/CAD (OTC)",
    "EURCHF_otc": "EUR/CHF (OTC)",
    "EURGBP_otc": "EUR/GBP (OTC)",
    "EURJPY_otc": "EUR/JPY (OTC)",
    "EURUSD_otc": "EUR/USD (OTC)",
    "GBPAUD_otc": "GBP/AUD (OTC)",
    "GBPCAD_otc": "GBP/CAD (OTC)",
    "GBPCHF_otc": "GBP/CHF (OTC)",
    "GBPJPY_otc": "GBP/JPY (OTC)",
    "GBPNZD_otc": "GBP/NZD (OTC)",
    "GBPUSD_otc": "GBP/USD (OTC)",
    "LINUSD_otc": "Chainlink (OTC)",
    "LTCUSD_otc": "Litecoin (OTC)",
    "NZDCAD_otc": "NZD/CAD (OTC)",
    "NZDCHF_otc": "NZD/CHF (OTC)",
    "NZDJPY_otc": "NZD/JPY (OTC)",
    "SOLUSD_otc": "Solana (OTC)",
    "TONUSD_otc": "Toncoin (OTC)",
    "TRUUSD_otc": "Trump (OTC)",
    "USDARS_otc": "USD/ARS (OTC)",
    "USDCAD_otc": "USD/CAD (OTC)",
    "USDCHF_otc": "USD/CHF (OTC)",
    "USDCOP_otc": "USD/COP (OTC)",
    "USDDZD_otc": "USD/DZD (OTC)",
    "USDINR_otc": "USD/INR (OTC)",
    "USDJPY_otc": "USD/JPY (OTC)",
    "USDMXN_otc": "USD/MXN (OTC)",
    "USDPHP_otc": "USD/PHP (OTC)",
    "USDPKR_otc": "USD/PKR (OTC)",
    "USDZAR_otc": "USD/ZAR (OTC)",
    "XAGUSD_otc": "Silver (OTC)",
    "XAUUSD_otc": "Gold (OTC)",
    "XRPUSD_otc": "Ripple (OTC)",
    "ZECUSD_otc": "Zcash (OTC)",
    "AUDNZD_otc": "AUD/NZD (OTC)",
    "AUDCHF": "AUD/CHF",
    "HSIHKD": "Hong Kong 50",
    "IBXEUR": "IBEX 35",
    "XAGUSD": "Silver",
    "XAUUSD": "Gold",
}
# الاسم الحقيقي ← رمز الخادم (للتحويل العكسي السريع في الواجهة)
QX_NAME_TO_SYMBOL = {v: k for k, v in QX_ASSET_NAMES.items()}
# عملة فتح الشارت الافتراضية (طلب المستخدم): BRLUSD_otc باسمها الحقيقي
QX_OPENER_SYMBOL = "BRLUSD_otc"
QX_OPENER_NAME = QX_ASSET_NAMES[QX_OPENER_SYMBOL]


def qx_asset_display(sym, server_name=""):
    """الاسم الحقيقي للواجهة + العلم الكامل لأي عملة (طلب المستخدم):
    1) اسم الخادم الحقيقي من instruments أولاً.
    2) وإلا الاسم الحقيقي من جدول QX_ASSET_NAMES (جدول الخادم نفسه).
    3) العلم: شارة خاصة للرقمية/السلعة/المؤشر، وعلمان مدموجان للأزواج."""
    sym = str(sym or "").strip()
    name = str(server_name or "").strip() or QX_ASSET_NAMES.get(sym, "")
    if not name:
        name = sym                      # آخر احتياط: رمز الخادم نفسه بلا تخمين
    flag = SINGLE_BADGES.get(sym)
    if flag is None:
        flag = pair_flag_uri(name) if "/" in name else asset_flag(name)
    return name, flag


ASSET_PAYOUT = {
    "EUR/USD": 92, "GBP/USD": 90, "USD/JPY": 89, "EUR/JPY": 87, "GBP/JPY": 85,
    "AUD/CAD": 86, "USD/CHF": 88, "EUR/GBP": 87, "BTC/USD": 90, "ETH/USD": 89,
    "XAU/USD": 86, "EUR/USD OTC": 93, "GBP/USD OTC": 91, "USD/JPY OTC": 90,
    "GBP/JPY OTC": 87, "AUD/CAD OTC": 88, "EUR/GBP OTC": 89, "NZD/USD OTC": 90,
    "USD/PKR OTC": 87, "USD/BRL OTC": 86, "USD/INR OTC": 87, "USD/TRY OTC": 85,
    "BTC/USD OTC": 91,
}

# قائمة العملات المتاحة للشريط: تُعرض على الشريط المُضاف منها فقط (لا الكل) — بعلمي الزوج مدموجين
BOARD = [{"name": a["name"], "payout": ASSET_PAYOUT.get(a["name"], 85),
          "flag": pair_flag_uri(a["name"])} for a in ASSETS["real"] + ASSETS["otc"]]

# ---------------------------------------------------------------- بيانات الشموع (محاكاة بذريّة)
def _mulberry32(seed):
    a = seed & 0xFFFFFFFF

    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
        t = (t ^ (t + ((t ^ (t >> 7)) * (t | 61) & 0xFFFFFFFF))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0
    return rnd


def _hash(s):
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def generate_candles(asset, tf_key, count=620):
    cfg = next((a for a in ASSETS["real"] + ASSETS["otc"] if a["name"] == asset), ASSETS["real"][0])
    tf_sec = dict(TFS).get(tf_key, 60)
    rnd = _mulberry32(_hash(asset + ":" + tf_key))
    now = int(datetime.now().timestamp())
    end_t = now - now % tf_sec
    out = []
    price = cfg["base"] * (0.85 + rnd() * 0.3)
    drift = vola = 0.0
    regime = 0
    for k in range(count):
        if regime <= 0:
            regime = 18 + int(rnd() * 60)
            d = rnd() < 0.42
            drift = (0.0 if d else (1 if rnd() < 0.5 else -1)) * cfg["vol"] * (0.05 + rnd() * 0.22)
            vola = cfg["vol"] * (0.55 + rnd() * 1.15)
        regime -= 1
        o = price
        shock = (rnd() + rnd() + rnd() - 1.5) * 1.15
        c = max(cfg["base"] * 0.05, o * (1 + drift + shock * vola))
        wu = abs(shock) * vola * (0.25 + rnd() * 0.9) * o
        wd = abs(shock) * vola * (0.25 + rnd() * 0.9) * o
        h = max(o, c) + wu * 0.6
        l = min(o, c) - wd * 0.6
        f = 10 ** cfg["dec"]
        out.append({"t": end_t - (count - 1 - k) * tf_sec,
                    "o": round(o * f) / f, "h": round(h * f) / f,
                    "l": round(l * f) / f, "c": round(c * f) / f,
                    "v": round(600 + rnd() * 1400)})
        price = c
    return out


def step_candle(c, vol):
    d = (random.random() - 0.5) * 2 * vol * 0.14 * c["c"]
    c = dict(c)
    c["c"] = c["c"] + d
    c["h"] = max(c["h"], c["c"])
    c["l"] = min(c["l"], c["c"])
    c["v"] += random.randint(1, 25)
    return c


def new_candle(prev, tf_sec, vol):
    o = prev["c"]
    first = o * (1 + (random.random() - 0.5) * 2 * vol * 0.1)
    return {"t": prev["t"] + tf_sec, "o": o, "h": max(o, first), "l": min(o, first),
            "c": first, "v": random.randint(50, 350)}
# ---------------------------------------------------------------- قوالب الأكواد
JS_IND_TEMPLATE = """// BadiCharts Studio — JS indicator
// The code must end with: return { ... }
//   calculate(candles, s)  -> values (array or {Name: [...]})
//   render(ctx, values, h, s) is optional — a default line renderer is used
//     h: h.indexToX(i)  h.priceToY(p)  h.paneToY(v)  h.firstIdx  h.lastIdx
//   candles keys: time, open, high, low, close, volume
//   Helpers: Indicators.sma(v,p) ema(v,p) rsi(v,p) macd(v,f,sl,sg)
//            bollinger(v,p,m) stoch(candles,p,sm) atr(candles,p)
//   Market API (طلب المستخدم: معلومات الزوج + نسبة الدفع + مفتوح/مغلق):
//     Indicators.market.info(['EUR/USD'])  → {name, payout, open, otc}  (بدون اسم = عملة الشارت الحالية)
//     Indicators.market.assets()           → كل العملات [{name, payout, open, otc}]
//     Indicators.market.added()            → العملات المضافة إلى الشريط
//     Indicators.market.current()          → عملة الشارت النشط
//   إشارات تلغرام: signal() يرجع {dir:'up'|'down', price, chats:'@channel أو -100...'}
//     chats = معرف محادثة تلغرام لهذا المؤشر — يُرسل إليها مع النتيجة تلقائيًا
//   نطاق العملات (إرسال إشارات لأكثر من عملة): أضف إلى settings:
//     scope: 'added' (المضافة للشريط) | 'high' (أعلى نسبة دفع ≥ settings.minPayout) | 'all' (كل العملات)
//   Print to the console:  log('text')

return {
  label: 'My Indicator',
  type: 'overlay',            // 'overlay' over candles | 'pane' bottom window
  settings: { period: 20 },

  calculate(candles, s) {
    const closes = candles.map(c => c.close);
    return { Mid: Indicators.sma(closes, s.period) };
  },

  // optional custom drawing:
  // render(ctx, values, h, s) { ... },

  // optional Telegram alert — return {dir:'up'|'down', price, chats:'@mychannel'} or null:
  //   chats = معرف محادثة تلغرام لهذا المؤشر (بدل إعدادات التطبيق)
  //   scope/minPayout في settings تتحكم في نطاق العملات (المضافة / أعلى دفع / الكل)
  signal(candles, values, s) { return null; }
};
"""

PY_IND_TEMPLATE = '''# BadiCharts Studio — Python indicator
# Required: LABEL, TYPE ('overlay' | 'pane'), SETTINGS dict
#           def calculate(candles, s) -> {'Name': [values...]} or [values...]
# Optional: def get_range(values) -> (min, max)      # for pane type
#           def signal(candles, values) -> {'dir':'up'|'down','price':x,'chats':'@channel'} or None
#             chats = Telegram chat id for this indicator's signals (optional)
# Helpers injected: sma(), ema(), rsi()
# candles = [{"t","o","h","l","c","v"}, ...]

LABEL = "My PY Indicator"
TYPE = "overlay"
SETTINGS = {"period": 20}


def calculate(candles, s):
    closes = [c["c"] for c in candles]
    return {"EMA": ema(closes, s["period"])}


def signal(candles, values):
    return None
'''

JS_TOOL_TEMPLATE = """// BadiCharts Studio — JS drawing tool
// The code must end with: return { ... }
//   onStart(ctx)            -> drawing object   ctx = {x, y, idx, price}
//   onUpdate(d, ctx)        modify d while dragging
//   onDraw(ctx, d, h)       draw every frame    h.indexToX(i) h.priceToY(p)
//   onHitTest(d, x, y, h)   -> true if click hits the drawing (eraser)
// Tip: store coordinates as (index, price) so drawings stick to candles.

return {
  label: 'My Tool',
  icon: '*',

  onStart(ctx) {
    return { i1: ctx.idx, p1: ctx.price, i2: ctx.idx, p2: ctx.price };
  },

  onUpdate(d, ctx) {
    d.i2 = ctx.idx;
    d.p2 = ctx.price;
  },

  onDraw(ctx, d, h) {
    const x1 = h.indexToX(d.i1), y1 = h.priceToY(d.p1);
    const x2 = h.indexToX(d.i2), y2 = h.priceToY(d.p2);
    ctx.strokeStyle = '#14B8F5';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  },

  onHitTest(d, x, y, h) {
    const x1 = h.indexToX(d.i1), y1 = h.priceToY(d.p1);
    const x2 = h.indexToX(d.i2), y2 = h.priceToY(d.p2);
    const len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const t = Math.max(0, Math.min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (len * len)));
    return Math.hypot(x - (x1 + t * (x2 - x1)), y - (y1 + t * (y2 - y1))) <= 6;
  }
};
"""

# ---------------------------------------------------------------- مكتبة مؤشرات جاهزة
LIB = [
    {"key": "ema", "name": "EMA Cross", "desc": "Fast/slow EMA crossover with alerts",
     "code": """return {
  label: 'EMA Cross',
  type: 'overlay',
  settings: { fast: 9, slow: 21 },

  calculate(candles, s) {
    const cl = candles.map(c => c.close);
    return { fast: Indicators.ema(cl, s.fast), slow: Indicators.ema(cl, s.slow) };
  },

  render(ctx, v, h, s) {
    if (!v) return;
    const line = (arr, color, w) => {
      ctx.strokeStyle = color; ctx.lineWidth = w; ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        const x = h.indexToX(i), y = h.priceToY(arr[i]);
        if (arr[i] == null) { st = false; continue; }
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
    };
    line(v.slow, '#EF4444', 1.4);
    line(v.fast, '#14B8F5', 1.8);
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 2) return null;
    const f1 = v.fast[n - 2], f0 = v.fast[n - 1];
    const s1 = v.slow[n - 2], s0 = v.slow[n - 1];
    if ([f1, f0, s1, s0].some(x => x == null)) return null;
    if (f1 <= s1 && f0 > s0) return { dir: 'up', price: candles[n - 1].close };
    if (f1 >= s1 && f0 < s0) return { dir: 'down', price: candles[n - 1].close };
    return null;
  }
};"""},
    {"key": "rsi", "name": "RSI + Zones", "desc": "RSI pane with 30/70 zones and alerts",
     "code": """return {
  label: 'RSI',
  type: 'pane',
  settings: { period: 14 },

  calculate(candles, s) {
    return Indicators.rsi(candles.map(c => c.close), s.period);
  },

  getRange() { return { min: 0, max: 100 }; },

  render(ctx, v, h, s) {
    if (!v) return;
    const y70 = h.paneToY(70), y30 = h.paneToY(30);
    ctx.fillStyle = 'rgba(139,92,246,0.08)';
    ctx.fillRect(h.chartLeft, y70, h.chartRight - h.chartLeft, y30 - y70);
    ctx.setLineDash([3, 3]);
    for (const p of [[y70, '#EF4444'], [y30, '#22C55E']]) {
      ctx.strokeStyle = p[1]; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(h.chartLeft, p[0]); ctx.lineTo(h.chartRight, p[0]); ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.strokeStyle = '#3B6CF5'; ctx.lineWidth = 1.6; ctx.beginPath();
    let st = false;
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      if (v[i] == null) { st = false; continue; }
      const x = h.indexToX(i), y = h.paneToY(v[i]);
      if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
    }
    ctx.stroke();
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 2 || v[n - 1] == null || v[n - 2] == null) return null;
    if (v[n - 2] <= 30 && v[n - 1] > 30) return { dir: 'up', price: candles[n - 1].close };
    if (v[n - 2] >= 70 && v[n - 1] < 70) return { dir: 'down', price: candles[n - 1].close };
    return null;
  }
};"""},
    {"key": "macd", "name": "MACD", "desc": "MACD 12/26/9 with histogram",
     "code": """return {
  label: 'MACD',
  type: 'pane',
  settings: { fast: 12, slow: 26, signal: 9 },

  calculate(candles, s) {
    const cl = candles.map(c => c.close);
    return Indicators.macd(cl, s.fast, s.slow, s.signal);
  },

  render(ctx, v, h) {
    if (!v || !v.macd) return;
    const bw = Math.max(2, (h.barSpacing || 6) * 0.55);
    ctx.fillStyle = 'rgba(20,184,245,0.35)';
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      const hv = v.hist ? v.hist[i] : null;
      if (hv == null) continue;
      const y0 = h.paneToY(0), y1 = h.paneToY(hv);
      ctx.fillRect(h.indexToX(i) - bw / 2, Math.min(y0, y1), bw, Math.abs(y1 - y0) || 1);
    }
    for (const [arr, col, w] of [[v.macd, '#14B8F5', 1.7], [v.signal, '#EF4444', 1.3]]) {
      ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        if (arr[i] == null) { st = false; continue; }
        const x = h.indexToX(i), y = h.paneToY(arr[i]);
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 2) return null;
    const m1 = v.macd[n - 2], m0 = v.macd[n - 1], g1 = v.signal[n - 2], g0 = v.signal[n - 1];
    if ([m1, m0, g1, g0].some(x => x == null)) return null;
    if (m1 <= g1 && m0 > g0) return { dir: 'up', price: candles[n - 1].close };
    if (m1 >= g1 && m0 < g0) return { dir: 'down', price: candles[n - 1].close };
    return null;
  }
};"""},
    {"key": "bb", "name": "Bollinger Bands", "desc": "20/2 bands with squeeze alerts",
     "code": """return {
  label: 'Bollinger Bands',
  type: 'overlay',
  settings: { period: 20, mult: 2.0 },

  calculate(candles, s) {
    const cl = candles.map(c => c.close);
    return Indicators.bollinger(cl, s.period, s.mult);
  },

  render(ctx, v, h, s) {
    if (!v) return;
    ctx.setLineDash([4, 3]);
    const band = (arr, color) => {
      ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        if (arr[i] == null) { st = false; continue; }
        const x = h.indexToX(i), y = h.priceToY(arr[i]);
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
    };
    band(v.upper, '#8A9099');
    band(v.lower, '#8A9099');
    ctx.setLineDash([]);
    band(v.mid, '#3B6CF5');
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 3) return null;
    const c2 = candles[n - 2].close, c0 = candles[n - 1].close;
    if (c2 < v.upper[n - 2] && c0 >= v.upper[n - 1]) return { dir: 'down', price: c0 };
    if (c2 > v.lower[n - 2] && c0 <= v.lower[n - 1]) return { dir: 'up', price: c0 };
    return null;
  }
};"""},
    {"key": "stoch", "name": "Stochastic", "desc": "%K/%D oscillator with OB/OS alerts",
     "code": """return {
  label: 'Stochastic',
  type: 'pane',
  settings: { period: 14, smooth: 3 },

  calculate(candles, s) {
    return Indicators.stoch(candles, s.period, s.smooth);
  },

  getRange() { return { min: 0, max: 100 }; },

  render(ctx, v, h) {
    if (!v) return;
    const y80 = h.paneToY(80), y20 = h.paneToY(20);
    ctx.setLineDash([3, 3]);
    for (const p of [[y80, '#EF4444'], [y20, '#22C55E']]) {
      ctx.strokeStyle = p[1]; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(h.chartLeft, p[0]); ctx.lineTo(h.chartRight, p[0]); ctx.stroke();
    }
    ctx.setLineDash([]);
    for (const [arr, col, w] of [[v.k, '#14B8F5', 1.7], [v.d, '#EF4444', 1.2]]) {
      ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        if (arr[i] == null) { st = false; continue; }
        const x = h.indexToX(i), y = h.paneToY(arr[i]);
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 2) return null;
    const k1 = v.k[n - 2], k0 = v.k[n - 1], d1 = v.d[n - 2], d0 = v.d[n - 1];
    if ([k1, k0, d1, d0].some(x => x == null)) return null;
    if (k1 <= d1 && k0 > d0 && k0 < 45) return { dir: 'up', price: candles[n - 1].close };
    if (k1 >= d1 && k0 < d0 && k0 > 55) return { dir: 'down', price: candles[n - 1].close };
    return null;
  }
};"""},
    {"key": "supertrend", "name": "Supertrend", "desc": "ATR trailing trend with flip alerts",
     "code": """return {
  label: 'Supertrend',
  type: 'overlay',
  settings: { period: 10, mult: 3.0 },

  calculate(candles, s) {
    const atr = Indicators.atr(candles, s.period);
    const up = [], dn = [], dir = [];
    let trend = 1, prev = null;
    for (let i = 0; i < candles.length; i++) {
      const a = atr[i];
      if (a == null) { up.push(null); dn.push(null); dir.push(null); continue; }
      const mid = (candles[i].high + candles[i].low) / 2;
      let u = mid + s.mult * a, d = mid - s.mult * a;
      if (prev != null) {
        u = (u < prev.u || candles[i - 1].close > prev.u) ? u : prev.u;
        d = (d > prev.d || candles[i - 1].close < prev.d) ? d : prev.d;
        trend = candles[i].close > prev.u ? 1 : (candles[i].close < prev.d ? -1 : prev.t);
      }
      prev = { u: u, d: d, t: trend };
      up.push(trend === 1 ? d : null);
      dn.push(trend === -1 ? u : null);
      dir.push(trend);
    }
    return { up: up, dn: dn, dir: dir };
  },

  render(ctx, v, h) {
    if (!v) return;
    const seg = (useUp, color) => {
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        const arr = useUp ? v.up : v.dn;
        if (arr[i] == null) { st = false; continue; }
        const x = h.indexToX(i), y = h.priceToY(arr[i]);
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
    };
    seg(true, '#22C55E');
    seg(false, '#EF4444');
  },

  signal(candles, v) {
    const n = candles.length;
    if (!v || n < 2 || v.dir[n - 1] == null || v.dir[n - 2] == null) return null;
    if (v.dir[n - 2] < 0 && v.dir[n - 1] > 0) return { dir: 'up', price: candles[n - 1].close };
    if (v.dir[n - 2] > 0 && v.dir[n - 1] < 0) return { dir: 'down', price: candles[n - 1].close };
    return null;
  }
};"""},
]

SEEDS = [
    {"kind": "js", "code": JS_IND_TEMPLATE},
    {"kind": "py", "code": PY_IND_TEMPLATE},
    {"kind": "jstool", "code": JS_TOOL_TEMPLATE},
]

# ---------------------------------------------------------------- مساعدات بايثون للمؤشرات
def _sma(v, p):
    out, s = [None] * len(v), 0.0
    for i, x in enumerate(v):
        s += x
        if i >= p:
            s -= v[i - p]
        if i >= p - 1:
            out[i] = s / p
    return out


def _ema(v, p):
    out, k = [None] * len(v), 2.0 / (p + 1)
    prev = None
    for i, x in enumerate(v):
        prev = x if prev is None else x * k + prev * (1 - k)
        out[i] = prev if i >= p - 1 else None
    return out


def _rsi(v, p):
    out = [None] * len(v)
    if len(v) <= p:
        return out
    g, l = 0.0, 0.0
    for i in range(1, p + 1):
        d = v[i] - v[i - 1]
        g += max(d, 0)
        l += max(-d, 0)
    ag, al = g / p, l / p
    out[p] = 100.0 - 100.0 / (1 + ag / al) if al else 100.0
    for i in range(p + 1, len(v)):
        d = v[i] - v[i - 1]
        ag = (ag * (p - 1) + max(d, 0)) / p
        al = (al * (p - 1) + max(-d, 0)) / p
        out[i] = 100.0 - 100.0 / (1 + ag / al) if al else 100.0
    return out


PY_HELPERS = {"sma": _sma, "ema": _ema, "rsi": _rsi, "math": __import__("math")}

CFG_DIR = os.path.dirname(os.path.abspath(__file__))
CFG_FILE = os.path.join(CFG_DIR, "config.json")
FILES_FILE = os.path.join(CFG_DIR, "files.json")
SHOTS_DIR = os.path.join(CFG_DIR, "signals")
NAME_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

# ───── مظهر الشارت: الألوان القابلة للتغيير الحر من زر الإعدادات (طلبات المستخدم) ─────
# مفاتيح مكتبة BADI-CHARTS-V2 — أي لون hex/rgba يُقبل بلا قوائم محدودة
CHART_THEME_DEFAULTS = {
    "bg":       "#0e1015",   # خلفية الشارت
    "bull":     "#26a69a",   # الشمعة الصاعدة
    "bear":     "#ef5350",   # الشمعة الهابطة
    "bullVol":  "rgba(38,166,154,0.50)",   # حجم الشمعة الصاعدة
    "bearVol":  "rgba(239,83,80,0.50)",   # حجم الشمعة الهابطة
    "grid":     "#1c2030",   # الشبكة
    "axisText": "#787b86",   # ألوان محاور السعر/الوقت
    "crosshair":"#787b86",   # مؤشر التقاطع
    "drawing":  "#38bdf8"    # أدوات الرسم
}
TG_TMPL_DEFAULT = ("🎯 {dir} | {asset} ({tf})\n⏱ Duration: {tf}\n"
                   "📊 Indicator: {indicator}\n🕐 Entry: {time}\n💰 Price: {price}")


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def random_suffix(n=6):
    return "".join(random.choice(NAME_CHARS) for _ in range(n))


def _tg_send(token, chats, text, png=None):
    """إرسال إلى تلجرام: نص لكل المحادثات + صورة اختيارية (multipart)."""
    ok_count = 0
    errs = []
    chats = [c.strip() for c in chats.replace(";", ",").split(",") if c.strip()]
    if not token.strip():
        raise ValueError("empty bot token")
    if not chats:
        raise ValueError("no chat ids")
    for ch in chats:
        try:
            if png:
                boundary = "----BadiCharts" + random_suffix(12)
                body = b""
                for k, v in [("chat_id", ch)]:
                    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
                body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"signal.png\"\r\n"
                         "Content-Type: image/png\r\n\r\n").encode() + png + b"\r\n"
                body += (f"--{boundary}--\r\n").encode()
                req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token.strip()}/sendPhoto", data=body,
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
                urllib.request.urlopen(req, timeout=20).read()
            else:
                payload = urllib.parse.urlencode({"chat_id": ch, "text": text}).encode()
                urllib.request.urlopen(f"https://api.telegram.org/bot{token.strip()}/sendMessage",
                                       payload, timeout=20).read()
            ok_count += 1
        except Exception as e:
            errs.append(str(e)[:80])
    if ok_count == 0:
        raise RuntimeError(errs[0] if errs else "send failed")
    return ok_count, errs
# ---------------------------------------------------------------- الباك إند
# ═══════════════════════════════════════════════════════════════════════════
#  BADI — BADI SECURE INDICATOR FORMAT (المؤشرات المشفرة)
#  صيغة الملف .badi:  MAGIC "BADI" (4) + VERSION (1) + NONCE (12) + AES-256-GCM(ciphertext+tag)
#  • المفتاح الرئيسي 256-بت مدموج داخل هذا الملف (BADI_MASTER_KEY_HEX) — ثابت
#    للجميع، لا يُكتب في أي ملف، ولا يُنسخ إلى الحافظة، ولا يُعرض، ولا يُرسل —
#    لا توجد أي وصلة تُخرجه من التطبيق؛ البصمة المعروضة SHA-256 مقطوعة لا تكشفه.
#  • التشفير AES-GCM مع AAD = MAGIC+VERSION حتى لا يُنقل أي جزء من الملف دون كشفه.
#  • المؤشر يُفك داخل الذاكرة فقط، يُفحص (ماسح أنماط ممنوعة + QuickJS معزولة
#    بلا ملفات ولا شبكة) ثم يُشغَّل داخليًا على الشارت: لا يُفتح في المحرر،
#    لا يُحفظ، ولا يظهر كوده للمستخدم إطلاقًا — المؤشرات المدفوعة آمنة.
#  • الملف المشفر .badi يُكتب بجوار ملف المؤشر الأصلي — مثل ميتاتريدر.
# ═══════════════════════════════════════════════════════════════════════════
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_AESGCM = True
except Exception:
    AESGCM = None
    _HAS_AESGCM = False
try:
    import quickjs as _quickjs
    _HAS_QJS = True
except Exception:
    _quickjs = None
    _HAS_QJS = False

BADI_MAGIC = b"BADI"
BADI_VERSION = b"\x01"
BADI_MSGS = {
    "en": {
        "noaes": "Encryption library missing — run: pip install cryptography",
        "notbadi": "Not a BADI file",
        "badver": "Unsupported BADI version",
        "short": "Corrupted file — data is incomplete",
        "key": "Decryption failed — the file is corrupted or the app key does not match",
        "text": "Corrupted file — the decrypted content is not text",
        "noc": "The code does not define calculate(candles, settings)",
        "run": "The code crashed in the sandbox",
        "blocked": "Indicator code tried to access app files, services or internals — rejected",
        "license": "This indicator is licensed to another USER ID — it will not run on this device. Your ID: ",
        "uidbad": "Invalid USER ID — the correct format is BADI-XXXX-XXXX-XXXX",
        "paidend": "Subscription of this paid indicator ended — renew from its developer",
        "paidoff": "This paid indicator is currently disabled by its developer",
        "paidbad": "Invalid paid server/ID — server must be an http(s) URL and ID letters/digits only",
    },
    "ar": {
        "noaes": "مكتبة التشفير غير موجودة — ثبّتها بالأمر: pip install cryptography",
        "notbadi": "هذا الملف ليس بصيغة BADI",
        "badver": "إصدار ملف BADI غير مدعوم",
        "short": "الملف تالف — البيانات غير مكتملة",
        "key": "فك التشفير فشل — الملف تالف أو مفتاح التطبيق غير مطابق",
        "text": "الملف تالف — المحتوى المفكوك ليس نصًا",
        "noc": "الكود لا يعرّف calculate(candles, settings)",
        "run": "الكود توقف داخل بيئة الاختبار المعزولة",
        "blocked": "كود المؤشر يحاول الوصول إلى ملفات أو خدمات أو أجزاء داخلية من التطبيق — مرفوض",
        "license": "هذا المؤشر مرخّص لمعرّف مستخدم آخر — لن يعمل على هذا الجهاز. معرّفك: ",
        "uidbad": "معرّف مستخدم غير صالح — الصيغة الصحيحة BADI-XXXX-XXXX-XXXX",
        "paidend": "انتهى اشتراك هذا المؤشر المدفوع — يجب التجديد من مبرمجه",
        "paidoff": "هذا المؤشر المدفوع موقوف حاليًا من مبرمجه",
        "paidbad": "خادم/معرف المدفوع غير صالح — الخادم يجب أن يكون رابط http(s) والمعرف حروفًا وأرقامًا فقط",
    },
}


# ───── حماية BADI: أنماط ممنوعة في كود المؤشرات المشفرة (طلب المستخدم) ─────
# الملفات التي ينشئها التطبيق والمفاتيح وأجزاء المحرك الداخلية لا يمكن للمؤشر
# المشفر أن يمرّ عليها: الشبكة والتخزين وجسر سطح المكتب وأسماء الأجزاء الداخلية
# كلها ممنوعة — وأي كود يلمسها يُرفض قبل تشغيله (ويُفحص أيضًا داخل QuickJS).
BADI_BANNED_RE = re.compile(
    r"(localstorage|sessionstorage|indexeddb|xmlhttprequest|websocket|eventsource"
    r"|sendbeacon|fetch\s*\(|import\s*\(|importscripts|document\.cookie|caches\b"
    r"|showopenfilepicker|showdirectorypicker|requestfilesystem|getdirectoryhandle"
    r"|getfilehandle|__badiapp|__badisend|badisend|__badipch|__badi_chart|__badipane"
    r"|__badiprimary|__badipushsignal|__badisigresult|__badisetmarket|__badithemekit"
    r"|__badishotcanvas|__badi_boot|__badi_embedded|__badi_app_theme|__badi_chart_theme"
    r"|__badi_chart_user|__badi_monaco|pywebview|webchannel|qtwebchannel"
    r"|new\s+worker|require\s*\("
    r"|eval\s*\(|new\s+function\s*\(|function\s*\(\s*[\"']"
    r"|settimeout\s*\(\s*[\"']|setinterval\s*\(\s*[\"'])",
    re.I)


class BADIError(Exception):
    """خطأ BADI — الرسالة مفتاح من BADI_MSGS يُترجم حسب لغة التطبيق."""
    pass


class BADI:
    """تشفير/فك تشفير مؤشرات JavaScript بصيغة .badi — المفتاح داخل التطبيق فقط.

    المفتاح 256-بت مدموج داخل هذا الملف (طلب المستخدم: يبقى داخل التطبيق
    ولا يُكتب أبدًا داخل ملف المؤشر). لاستخدام مفتاحك الخاص استبدل قيمة
    BADI_MASTER_KEY_HEX بـ 64 حرفًا سداسيًا عشوائيًا."""

    BADI_MASTER_KEY_HEX = "AAC20E18936337C73D4D358E0A65BE9A2CFF59A96EA2709ACE23F468A082379F"

    @classmethod
    def master_key(cls):
        """مفتاح 256-بت مدموج داخل التطبيق — 32 بايت (64 حرفًا hex)."""
        return bytes.fromhex(cls.BADI_MASTER_KEY_HEX)

    @classmethod
    def fingerprint(cls):
        """بصمة قصيرة للمفتاح للعرض في الإعدادات (لا تكشف المفتاح نفسه)."""
        return hashlib.sha256(cls.master_key()).hexdigest()[:12].upper()

    @classmethod
    def encrypt(cls, source: str) -> bytes:
        if not _HAS_AESGCM:
            raise BADIError("noaes")
        nonce = os.urandom(12)
        aes = AESGCM(cls.master_key())
        enc = aes.encrypt(nonce, source.encode("utf-8"), BADI_MAGIC + BADI_VERSION)
        return BADI_MAGIC + BADI_VERSION + nonce + enc

    @classmethod
    def decrypt(cls, blob: bytes) -> str:
        if not _HAS_AESGCM:
            raise BADIError("noaes")
        if len(blob) < 4 or blob[:4] != BADI_MAGIC:
            raise BADIError("notbadi")
        if len(blob) < 5:
            raise BADIError("short")
        if blob[4:5] != BADI_VERSION:
            raise BADIError("badver")
        if len(blob) < 5 + 12 + 16:
            raise BADIError("short")
        try:
            aes = AESGCM(cls.master_key())
            plain = aes.decrypt(blob[5:17], blob[17:], BADI_MAGIC + BADI_VERSION)
        except Exception:
            raise BADIError("key")
        try:
            return plain.decode("utf-8")
        except Exception:
            raise BADIError("text")


# ═══════════ معرّف المستخدم الثابت — BADI-XXXX-XXXX-XXXX (طلب المستخدم) ═══════════
# لكل مستخدم يُثبّت التطبيق معرّف عشوائي ثابت لا يتغير أبدًا:
#  • يُولَّد مرة واحدة ويُحفظ بعمق في مواقع مخفية (مجلد التطبيق + بيانات المستخدم على
#    النظام) موقّعًا بـ HMAC-SHA256 ومربوطًا ببصمة هذا الجهاز — لا يمكن تغييره ولا
#    نقله إلى جهاز أو تطبيق آخر: أي نسخ لملف التخزين إلى جهاز آخر يُرفض (البصمة لا
#    تطابق) ويُولَّد معرّف جديد تلقائيًا. أي عبث في المحتوى يكسر التوقيع.
#  • البائع يدمج معرّف المشتري داخل المؤشر المشفر (.badi) — والمؤشر لا يعمل إلا على
#    الجهاز الذي يطابق معرّفه المدمج (فحص داخل التطبيق عند فك التشفير).
BADI_UID_RE = re.compile(r"^BADI-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}$")
BADI_UID_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"   # بلا 0/O/1/I لتجنب اللبس
# سر التوقيع مشتق من مفتاح التطبيق الرئيسي — لا يُكتب في أي ملف ولا يُعرض
BADI_UID_SECRET = hashlib.sha256(
    BADI.master_key() + b"badi-user-id-signature-v1").digest()

_USER_ID_CACHE = None
_USER_ID_LOCK = threading.Lock()


def _machine_fp():
    """بصمة الجهاز من معرّفات النظام المستقرة (لا تتغير بين الجلسات):
    machine-id على لينكس، MachineGuid على ويندوز، IOPlatformUUID على ماك،
    ثم عنوان MAC إن كان حقيقيًا (وليس العشوائي المؤقت) واسم الجهاز —
    لربط معرّف المستخدم بهذا الجهاز فقط: نسخ ملف التخزين لجهاز آخر لا يُقبل."""
    parts = []
    # 1) معرّف الجهاز على لينكس (مستقر عبر إعادة التشغيل)
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            with open(p, "r", encoding="utf-8") as fh:
                mid = fh.read().strip()
            if mid:
                parts.append(mid[:64])
                break
        except Exception:
            pass
    # 2) MachineGuid على ويندوز (سجل النظام)
    try:
        import winreg as _wr
        with _wr.OpenKey(_wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            parts.append(str(_wr.QueryValueEx(k, "MachineGuid")[0]))
    except Exception:
        pass
    # 3) IOPlatformUUID على ماك
    try:
        import subprocess as _sp
        out = _sp.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                      capture_output=True, text=True, timeout=3).stdout
        for ln in out.splitlines():
            if "IOPlatformUUID" in ln and '"' in ln:
                parts.append(ln.rsplit('"', 2)[-2])
                break
    except Exception:
        pass
    # 4) عنوان MAC فقط إن كان حقيقيًا — عند فشل القراءة يولّد uuid رقمًا عشوائيًا
    #    مؤقتًا (بت multicast = 1) فلا يصلح لبصمة مستقرة ويُستبعد
    try:
        import uuid as _uuid
        node = _uuid.getnode()
        if node and ((node >> 40) & 1) == 0:
            parts.append(str(node))
    except Exception:
        pass
    # 5) اسم الجهاز (مكمّل، ليس كافيًا وحده)
    try:
        import platform as _plat
        parts.append((_plat.node() or "")[:64])
    except Exception:
        pass
    if not parts:
        parts.append("unknown-device")
    return hashlib.sha256(
        "|".join(parts).encode("utf-8", "ignore")).hexdigest()[:32]


def _uid_stores():
    """مواقع التخزين العميقة لمعرّف المستخدم (نسخ احتياطية متعددة — قاعدة داخلية)."""
    out = []
    try:
        out.append(os.path.join(CFG_DIR, ".badi-sys", "id.dat"))
        out.append(os.path.join(CFG_DIR, ".badi-sys", ".c", "s.bin"))
        try:
            from PySide6.QtCore import QStandardPaths
            ad = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation)
            if ad:
                out.append(os.path.join(ad, "BadiCharts", ".sys", "id.dat"))
        except Exception:
            pass
    except Exception:
        pass
    return out


def _uid_sign(uid, fp, ts):
    msg = ("v1|%s|%s|%d" % (uid, fp, ts)).encode("utf-8")
    return hmac.new(BADI_UID_SECRET, msg, hashlib.sha256).hexdigest()


def _uid_record_ok(rec, fp):
    """يتحقق من صحة سجل التخزين: توقيع HMAC + مطابقة بصمة الجهاز — يرجع (ts, uid) أو None."""
    try:
        if not isinstance(rec, dict):
            return None
        uid = str(rec.get("id") or "").strip().upper()
        if not BADI_UID_RE.match(uid):
            return None
        if str(rec.get("fp") or "") != fp:
            return None
        ts = int(rec.get("ts") or 0)
        if ts <= 0 or _uid_sign(uid, fp, ts) != str(rec.get("sig") or ""):
            return None
        return (ts, uid)
    except Exception:
        return None


def _gen_user_id():
    """معرّف عشوائي مثل BADI-7K9X-4M2P-8Q6R — من os.urandom (حتمي آمن)."""
    raw = os.urandom(12)
    grp = ["".join(BADI_UID_ALPHABET[b % 32] for b in raw[i:i + 4]) for i in (0, 4, 8)]
    return "BADI-" + "-".join(grp)


def _write_uid_everywhere(uid, fp):
    """كتابة السجل الموقّع في كل مواقع التخزين العميقة (نسخ احتياطية)."""
    ts = int(time.time())
    rec = {"id": uid, "fp": fp, "ts": ts, "sig": _uid_sign(uid, fp, ts)}
    body = json.dumps(rec, ensure_ascii=False)
    for p in _uid_stores():
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            try:
                os.chmod(p, 0o666)      # فك القراءة-فقط قبل إعادة الكتابة
            except Exception:
                pass
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(body)
            try:
                os.chmod(p, 0o444)      # قراءة فقط — يمنع العبث السهل
            except Exception:
                pass
        except Exception:
            pass


def _get_user_id():
    """معرّف المستخدم الثابت — يُقرأ من أقدم نسخة صالحة أو يُولَّد مرة واحدة ويُحفظ بعمق."""
    global _USER_ID_CACHE
    with _USER_ID_LOCK:
        if _USER_ID_CACHE:
            return _USER_ID_CACHE
        fp = _machine_fp()
        best = None
        for p in _uid_stores():
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    rec = json.loads(fh.read().strip() or "{}")
            except Exception:
                continue
            ok = _uid_record_ok(rec, fp)
            if ok and (best is None or ok[0] < best[0]):
                best = ok
        uid = best[1] if best else _gen_user_id()
        _USER_ID_CACHE = uid
        _write_uid_everywhere(uid, fp)
        return uid


def _badi_payload(plain):
    """تفكيك الحمولة المفكوكة: مغلف جديد {t:badi-ind,...} أو كود خام (توافق مع الملفات القديمة).
    يرجع (code, license_ids, paid_manifest, name) — بيان المؤشر المدفوع (المعرف + خادم المبرمج)
    مدفون داخل المغلف المشفر نفسه: لا يمكن لأي سكريبت قراءته قبل الفك ولا زوّره (طلب المستخدم)."""
    s = str(plain or "")
    if s.lstrip().startswith("{"):
        try:
            d = json.loads(s)
            if isinstance(d, dict) and d.get("t") == "badi-ind" and "code" in d:
                lic = d.get("license") or []
                if not isinstance(lic, list):
                    lic = []
                lic = [str(x).strip().upper() for x in lic if str(x).strip()]
                paid = _norm_paid_manifest(d.get("paid")) if d.get("paid") else None
                return str(d.get("code") or ""), lic, paid, str(d.get("name") or "")
        except Exception:
            pass
    return s, [], None, ""


def _badi_license_denied(license_ids):
    """True إذا كان المؤشر مرخّصًا لمعرّفات لا تشمل معرّف هذا الجهاز (طلب المستخدم):
    قائمة فارغة = يعمل مع الجميع — وإلا يجب تطابق معرّف واحد على الأقل."""
    ids = [str(x or "").strip().upper() for x in (license_ids or []) if str(x or "").strip()]
    if not ids:
        return False
    return _get_user_id().upper() not in ids


# ═══════════ المؤشرات المدفوعة — قاعدة محمية + تحكم المبرمج عبر خادمه (طلب المستخدم) ═══════════
# المبدأ الأمني (لا يمكن لأي سكريبت تجاوزه):
#   • بيان المؤشر المدفوع (معرفه + خادم مبرمجه) مدفون داخل المغلف المشفر AES-GCM نفسه —
#     لا يُقرأ إلا عند فك التشفير داخل التطبيق، فلا يمكن لأي كود زوّره أو تغييره.
#   • قاعدة البيانات الصغيرة موقّعة HMAC-SHA256 بمفتاح مشتق من مفتاح التطبيق + بصمة
#     الجهاز، وبنسخ مخفية متعددة — الحذف أو التعديل لا يمدد الاشتراك أبدًا:
#     (الفشل مغلق) المفقود = مؤشر متوقف حتى يعيد خادم المبرمج الحقيقة.
#   • منع تراجع ساعة الجهاز: يُحفظ آخر تاريخ رأاه النظام — الأيام لا تزيد أبدًا.
#   • قناة التحكم من الخادم: استطلاع GET صغير واستجابة JSON فقط ≤16KB — أوامر بيضاء
#     (duration/enable/disable/status/notify) وفقط: لا ملفات ولا base64 ولا تنفيذ أي كود.
_PAID_VER = 1
_PAID_LOCK = threading.RLock()   # RLock: نفس الخيط يستدعي دوالاً داخلية تأخذ القفل
_PAID_RECS = None


def _paid_secret():
    """سر توقيع القاعدة المحمية — مشتق داخل التطبيق من مفتاحه + بصمة الجهاز، لا يُكتب في أي ملف."""
    return hashlib.sha256(
        BADI.master_key() + b"badi-paid-store-v1" + _machine_fp().encode()).digest()


def _paid_stores():
    """مواقع القاعدة المحمية (نسخ مخفية متعددة — قاعدة داخلية مثل معرّف المستخدم)."""
    out = [os.path.join(CFG_DIR, ".badi-sys", "paid.dat"),
           os.path.join(CFG_DIR, ".badi-sys", ".c", "p.bin")]
    try:
        from PySide6.QtCore import QStandardPaths
        ad = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if ad:
            out.append(os.path.join(ad, "BadiCharts", ".sys", "paid.dat"))
    except Exception:
        pass
    try:
        out.append(os.path.join(BADI_DIR, ".sys", "paid.dat"))
    except Exception:
        pass
    return out


def _paid_sign(body):
    return hmac.new(_paid_secret(), body.encode("utf-8"), hashlib.sha256).hexdigest()


def _paid_load():
    """قراءة القاعدة: تُعتمد السجلات من النسخ السليمة التوقيع فقط — أي عبث يكسر التوقيع فيُهمَل."""
    global _PAID_RECS
    with _PAID_LOCK:
        if _PAID_RECS is not None:
            return _PAID_RECS
        recs = {}
        for p in _paid_stores():
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    d = json.loads(fh.read().strip() or "{}")
                if not isinstance(d, dict) or int(d.get("v") or 0) != _PAID_VER:
                    continue
                body = json.dumps(d.get("recs") or {}, sort_keys=True, ensure_ascii=False)
                if hmac.compare_digest(str(d.get("sig") or ""), _paid_sign(body)):
                    for k, v in (d.get("recs") or {}).items():
                        if isinstance(v, dict) and str(v.get("id") or "") == str(k):
                            old = recs.get(k)
                            if old is None or int(v.get("upd") or 0) >= int(old.get("upd") or 0):
                                recs[k] = v
            except Exception:
                continue
        _PAID_RECS = recs
        return _PAID_RECS


def _paid_save():
    """كتابة القاعدة في كل النسخ المخفية مع التوقيع + وضع القراءة فقط (منع العبث السهل)."""
    with _PAID_LOCK:
        body = json.dumps(_PAID_RECS or {}, sort_keys=True, ensure_ascii=False)
        doc = {"v": _PAID_VER, "recs": _PAID_RECS or {}, "sig": _paid_sign(body)}
        txt = json.dumps(doc, ensure_ascii=False)
        for p in _paid_stores():
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                try:
                    os.chmod(p, 0o666)
                except Exception:
                    pass
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(txt)
                try:
                    os.chmod(p, 0o444)
                except Exception:
                    pass
            except Exception:
                pass


def _today_iso():
    return datetime.now().strftime("%Y-%m-%d")


def _paid_days_left(rec, today):
    """الأيام المتبقية من الاشتراك — مع منع تراجع التاريخ (آخر تاريخ رأاه النظام)."""
    try:
        exp = str(rec.get("expiry") or "")
        if not exp:
            return None
        seen = str(rec.get("last_seen") or "")
        use = today if str(today) >= seen else seen
        ed = datetime.strptime(exp, "%Y-%m-%d").date()
        td = datetime.strptime(use, "%Y-%m-%d").date()
        return (ed - td).days
    except Exception:
        return None


def _norm_paid_manifest(m):
    """تحقق صارم من بيان المؤشر المدفوع: معرف آمن + خادم http(s) فقط — بلا أي شيء آخر."""
    try:
        if not isinstance(m, dict):
            return None
        sid = str(m.get("id") or "").strip()
        srv = str(m.get("server") or "").strip()
        if not re.match(r"^[A-Za-z0-9_.\-]{1,64}$", sid):
            return None
        u = urllib.parse.urlparse(srv)
        if u.scheme not in ("https", "http") or not u.netloc or len(srv) > 200:
            return None
        if any(c in srv for c in "\"'" + "<>"):
            return None
        return {"id": sid, "server": srv}
    except Exception:
        return None


def paid_register(manifest, name):
    """تسجيل/تحديث سجل المؤشر المدفوع في القاعدة المحمية — يُستدعى فقط عند فك التشفير
    داخل التطبيق (لا يمكن لأي سكريبت استدعاؤه أو زوّر بياناته)."""
    with _PAID_LOCK:
        recs = _paid_load()
        rid = str(manifest.get("id") or "")
        rec = recs.get(rid) or {}
        nm = str(name or rec.get("name") or "").strip()
        if nm and not re.search(r"\.(js|py)$", nm, re.I):
            nm += ".js"
        rec.update({"id": rid, "name": nm or rid,
                    "server": str(manifest.get("server") or ""),
                    "upd": int(time.time())})
        rec.setdefault("expiry", "")
        rec.setdefault("status", "")
        rec.setdefault("enabled", True)
        rec.setdefault("warned", 99)
        if str(rec.get("last_seen") or "") < _today_iso():
            rec["last_seen"] = _today_iso()
        recs[rid] = rec
        _paid_save()


def paid_records():
    """نسخة من سجلات القاعدة المحمية — للقراءة فقط."""
    with _PAID_LOCK:
        return dict(_paid_load())


def paid_days_left(rec, today):
    return _paid_days_left(rec, today)


def paid_save_rec(rec):
    """حفظ تعديل سجل (من مراقبة الاشتراك المحلية) — مع تحديث آخر تاريخ رأاه النظام."""
    with _PAID_LOCK:
        recs = _paid_load()
        rec["upd"] = int(time.time())
        if str(rec.get("last_seen") or "") < _today_iso():
            rec["last_seen"] = _today_iso()
        recs[str(rec.get("id") or "")] = rec
        _paid_save()


def paid_open_denied(rid, lang):
    """بوابة الفتح للمدفوع: انتهى الاشتراك أو أوقفه المبرمج؟ الفشل مغلق — لا فتح."""
    rec = paid_records().get(str(rid or ""))
    if not rec:
        return None
    if rec.get("enabled") is False:
        return BADI_MSGS[lang].get("paidoff", "locked by developer")
    left = _paid_days_left(rec, _today_iso())
    if left is not None and left < 0:
        return BADI_MSGS[lang].get("paidend", "subscription ended")
    return None


def paid_apply_commands(rid, rec, cmds):
    """تنفيذ الأوامر البيضاء فقط (طلب المستخدم: مدة/تشغيل/إيقاف/نجاح/إشعار — وفقط).
    يرجع (toggles, notes) — أي أمر آخر يُتجاهل صامتًا ولا يُنفذ أي كود من الخادم."""
    toggles, notes = [], []
    for c in cmds[:20]:
        try:
            if not isinstance(c, dict):
                continue
            cmd = str(c.get("cmd") or "").strip().lower()
            if cmd == "duration":
                days = c.get("days")
                until = c.get("until")
                if days is not None:
                    n = max(1, min(3650, int(days)))
                    try:
                        base = datetime.strptime(str(rec.get("expiry") or _today_iso()), "%Y-%m-%d").date()
                        today = datetime.strptime(_today_iso(), "%Y-%m-%d").date()
                        rec["expiry"] = (max(base, today) + timedelta(days=n)).strftime("%Y-%m-%d")
                    except Exception:
                        rec["expiry"] = (datetime.strptime(_today_iso(), "%Y-%m-%d") + timedelta(days=n)).strftime("%Y-%m-%d")
                elif until:
                    rec["expiry"] = datetime.strptime(str(until), "%Y-%m-%d").strftime("%Y-%m-%d")
                rec["warned"] = 99
                rec["upd"] = int(time.time())
            elif cmd in ("enable", "disable"):
                want = (cmd == "enable")
                if rec.get("enabled") != want:      # أمر التشغيل/الإيقاف فقط عند تغيّر فعلي
                    rec["enabled"] = want
                    toggles.append((str(rec.get("name") or rid), want))
                rec["upd"] = int(time.time())
            elif cmd == "status":
                st = str(c.get("state") or "").strip().lower()
                if st in ("active", "expired"):
                    rec["status"] = st
                    if st == "expired" and not rec.get("expiry"):
                        rec["enabled"] = False
                        toggles.append((str(rec.get("name") or rid), False))
                    rec["upd"] = int(time.time())
            elif cmd == "notify":
                notes.append(str(c.get("text") or ""))
        except Exception:
            continue
    if toggles or notes:
        with _PAID_LOCK:
            recs = _paid_load()
            rec["upd"] = int(time.time())
            recs[str(rec.get("id") or "")] = rec
            _paid_save()
    return toggles, notes


def _downloads_dir():
    """مجلد التنزيلات على الجهاز (يُستعمل عند الحاجة للتصدير اليدوي)."""
    try:
        from PySide6.QtCore import QStandardPaths
        p = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        if p and os.path.isdir(p):
            return p
    except Exception:
        pass
    p = os.path.join(os.path.expanduser("~"), "Downloads")
    return p if os.path.isdir(p) else os.path.expanduser("~")


# ═══════════ مجلد BadiCharts على القرص (طلب المستخدم) ═══════════
# التطبيق يحفظ كل مؤشر/أداة ينشئها المستخدم كملف حقيقي في:
#   <مجلد التطبيق>/BadiCharts/Indicators/   → المؤشرات (.js و .py)
#   <مجلد التطبيق>/BadiCharts/Tools/        → أدوات الرسم (.js)
# وأي ملف .badi مشفر يُكتب بجوار ملف المؤشر الأصلي (مثل .mq5/.ex5 في ميتاتريدر).
# المستخدم يمكنه أيضًا أن يضع ملفات المؤشرات/الأدوات مباشرة في المجلد —
# التطبيق يفحص المجلدين عند الإقلاع وعند فتح المحرر ويستوردها تلقائيًا.
def _desktop_dir():
    """مجلد سطح المكتب الحقيقي على أي نظام (طلب المستخدم: التطبيق ينشئ مجلده على سطح المكتب)."""
    try:
        from PySide6.QtCore import QStandardPaths
        p = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        if p and os.path.isdir(p) and os.access(p, os.W_OK):
            return p
    except Exception:
        pass
    home = os.path.expanduser("~")
    for cand in ("Desktop", "سطح المكتب", "OneDrive/Desktop", "OneDrive/سطح المكتب"):
        p = os.path.join(home, cand)
        if os.path.isdir(p) and os.access(p, os.W_OK):
            return p
    return CFG_DIR   # تعذر الوصول لسطح المكتب — بجانب التطبيق (احتياط)


def _migrate_badi_tree(src, dst):
    """ترحيل محتوى Indicators/Tools/Thumbs من الموقع القديم إلى الجديد (مرة واحدة)."""
    try:
        if not os.path.isdir(src) or (os.path.isdir(dst) and any(os.scandir(dst))):
            return
        import shutil as _sh
        for sub in ("Indicators", "Tools", "Thumbs"):
            s, d = os.path.join(src, sub), os.path.join(dst, sub)
            if not os.path.isdir(s):
                continue
            os.makedirs(d, exist_ok=True)
            for it in os.listdir(s):
                sp, dp = os.path.join(s, it), os.path.join(d, it)
                try:
                    if os.path.isfile(dp):
                        continue
                    try:
                        os.replace(sp, dp)
                    except Exception:
                        _sh.copy2(sp, dp)
                        os.remove(sp)
                except Exception:
                    pass
    except Exception:
        pass


# مجلد التطبيق على سطح المكتب أولًا — وإن فشل الإنشاء يبقى بجانب التطبيق (طلب المستخدم)
_BADI_DIR_DESK = os.path.join(_desktop_dir(), "BadiCharts")
_BADI_DIR_LOCAL = os.path.join(CFG_DIR, "BadiCharts")
try:
    os.makedirs(_BADI_DIR_DESK, exist_ok=True)
    BADI_DIR = _BADI_DIR_DESK
except Exception:
    BADI_DIR = _BADI_DIR_LOCAL
_migrate_badi_tree(_BADI_DIR_LOCAL, BADI_DIR)
BADI_IND_DIR = os.path.join(BADI_DIR, "Indicators")
BADI_TOOL_DIR = os.path.join(BADI_DIR, "Tools")
# صور المصغرة: صورة واحدة فقط لكل مؤشر — تُلتقط تلقائيًا عند أول تشغيل (طلب المستخدم)
BADI_THUMB_DIR = os.path.join(BADI_DIR, "Thumbs")


# ═══════════ ملف الدليل: شرح البرمجة والرسم على الشارت (طلب المستخدم) ═══════════
# يُكتب مرة واحدة في BadiCharts/Indicators عند الإقلاع — مؤشر حقيقي يعمل،
# والشرح الكامل داخل تعليقاته: بنية المؤشر، الحساب والدوال الجاهزة، API السوق
# (نسبة الدفع + مفتوح/مغلق)، الإشارات وتلجرام والنطاق، الرسم الحر على الشارت،
# وأدوات الرسم التفاعلية. إذا حذفه المستخدم يُعاد عند الإقلاع التالي.
# طلب المستخدم: أسماء ملفات البرمجة بالإنجليزية — وليس بالعربية
GUIDE_FILE_NAME = "BadiCharts_Programming_Guide.js"
# النسخ القديمة ذات الاسم العربي تُحذف عند الإقلاع (ترحيل)
LEGACY_GUIDE_FILES = ("دليل البرمجة والرسم على الشارت.js",)

GUIDE_JS = """/* ═══════════════════════════════════════════════════════════════════════════
   BadiCharts Programming Guide — دليل البرمجة والرسم على الشارت (الشرح الكامل)
   ═══════════════════════════════════════════════════════════════════════════

   هذا الملف مؤشر حقيقي يعمل على الشارت — والشرح الكامل في التعليقات أدناه.
   شغّله بزر ▶ وسترى: نطاق بولينجر مرسوم + تعبئة شفافة + دائرة + نص حر.

   ── 1) بنية أي مؤشر ────────────────────────────────────────────────────────
   الكود ينتهي دائمًا بـ return { ... } ويحوي:

     label    : اسم المؤشر كما يظهر على الشارت
     type     : 'overlay' فوق الشموع   |   'pane' نافذة أسفل الشارت
     color    : لون المؤشر الافتراضي
     settings : الإعدادات — أي مفتاح يظهر تلقائيًا في بطاقة الإعدادات ⚙
                (period / mult / fast / slow / signal / bins / color)

   ── 2) calculate(candles, s) — الحساب ──────────────────────────────────────
     candles : مصفوفة الشموع [{time, open, high, low, close, volume}, ...]
     s       : الإعدادات أعلاه
     يعيد    : مصفوفة أرقام  أو  كائن {الاسم: [قيم...], ...}

     دوال جاهزة:
       Indicators.sma(v, p)          المتوسط المتحرك البسيط
       Indicators.ema(v, p)          المتوسط المتحرك الأسي
       Indicators.bollinger(v, p, m) → {mid, upper, lower}
       Indicators.rsi(v, p)          مؤشر القوة النسبية
       Indicators.macd(v, f, sl, sg) الماكد
       Indicators.stoch(candles, p, sm) الاستوكاستك
       Indicators.atr(candles, p)    متوسط المدى الحقيقي

   ── 3) معلومات الزوج: نسبة الدفع + السوق مفتوح أم مغلق (API السوق) ────────
     Indicators.market.info()             ← الزوج الحالي: {name, payout, open, otc}
     Indicators.market.info('EUR/USD')    ← زوج محدد بالاسم
     Indicators.market.assets()           ← كل العملات [{name, payout, open, otc}]
     Indicators.market.added()            ← العملات المضافة إلى شريط العملات فقط
     Indicators.market.current()          ← عملة الشارت النشط الآن
     الحالة: OTC والعملات الرقمية مفتوحة دائمًا — والفوركس من الأحد 22:00 إلى الجمعة 22:00 UTC

   ── 4) الإشارات + بوت تلجرام ───────────────────────────────────────────────
     signal(candles, values, s) تُفحص كل ثانية، وعندما تعيد:

       {dir: 'up' | 'down', price: السعر, chats: '@قناتك أو -100...'}   ← إشارة
       null                                                             ← لا شيء

       chats = معرف محادثة/قناة تلجرام لهذا المؤشر — الإشارة ونتيجتها (WIN/LOSS)
               تُرسلان تلقائيًا إلى تلك المحادثة مع لقطة الشارت.
     لإرسال إشارات لأكثر من عملة أضف مفاتيح في settings:
       scope:     'added' → العملات المضافة للشريط فقط
                  'high'  → العملات ذات نسبة الدفع الأعلى (ليس شرطًا تكون مضافة)
                  'all'   → كل العملات
       minPayout: 85            ← الحد الأدنى مع scope: 'high'

     🎨 تصميم بطاقة الإشارة بنفسك — البطاقة غير ثابتة (طلب المستخدم):
       أضف card إلى الإشارة، وقيمتها HTML حر أو كائن:
         signal({dir:'up', card:'<div style="padding:6px 10px"><b>MY SIGNAL</b></div>'})
         signal({dir:'down', card:{html:'…', bg:'#101820', accent:'#FF4D5E', color:'#ffffff'}})
           html   : محتوى البطاقة كاملًا — أي HTML وستايل تريده (حرية تامة)
           bg     : خلفية البطاقة          accent : لون الشريط الجانبي للبطاقة
           color  : لون النص الافتراضي
       بدون card تظهر البطاقة الافتراضية. ملاحظات:
       • توقيت الإشارة يظهر في الزاوية اليسرى للبطاقة.
       • البطاقة تختفي تلقائيًا بعد انتهاء شمعة الفريم، والنتيجة (WIN/LOSS)
         تُسجَّل في تبويب السجل.
       • المؤقت التنازلي بجانب الشمعة الحية (رقمان فقط بلا إطار) تلقائي —
         يعرض الثواني المتبقية لإغلاق الشمعة الحالية.

   ── 5) الرسم الحر — الشارت يقبل رسم أي شيء (Canvas 2D كامل) ───────────────
     render(ctx, values, h, s) اختيارية — بدونها تُرسم النتائج خطوطًا تلقائيًا.
       ctx    : سياق Canvas 2D — خطوط، مستطيلات، دوائر، نصوص، تدرجات، ظلال...
       values : ناتج calculate
       h      : أدوات الإحداثيات:
                  h.indexToX(i)     فهرس الشمعة → بكسل X
                  h.priceToY(p)     السعر → بكسل Y        (نوع overlay)
                  h.paneToY(v)      قيمة → بكسل Y         (نوع pane)
                  h.firstIdx / h.lastIdx / h.candles / h.THEME / h.barSpacing
                  h.chartLeft / h.chartRight / h.priceTop / h.priceBottom
                  h.drawGradientArea(...)  تعبئة متدرجة جاهزة

   ── 6) أدوات الرسم التفاعلية — اسحب وارسم على الشارت مباشرة ───────────────
     أداة رسم تُبرمج بأربع دوال (راجع مثال Signal Arrow في المحرر):

       onStart(ctx)         بدء السحب  → يعيد كائن الرسم {i1, p1, ...}
       onUpdate(d, ctx)     أثناء السحب → عدّل بيانات الرسم d
       onDraw(ctx, d, h)    الرسم في كل إطار
       onHitTest(d, x, y, h) هل النقطة فوق الرسم؟ (للتحديد/الحذف/الخصائص)

     نصيحة: خزّن الإحداثيات كـ (فهرس شمعة + سعر) — تبقى الرسوم ملتصقة
            بالشموع عند التكبير والتحريك.

   ── 7) إضافات ──────────────────────────────────────────────────────────────
     getRange(values, s) → {min, max}   تحديد نطاق النافذة السفلية (pane)
     log('نص')                          طباعة في كونسول المحرر
     النتيجة تُحسب تلقائيًا: عند انتهاء مدة الفريم تُقارن الدخول بالخروج (WIN/LOSS)

   ── 8) المؤشرات المدفوعة — تحكم المبرمج في مؤشره عبر خادمه (جديد) ───────────
   عند تشفير المؤشر (نافذة الترخيص) توجد حقلا المدفوع:
     Paid control server : https://خادمك/badi/api   (https فقط — اختياري)
     Paid indicator ID   : PRO_SIGNAL_1             (حروف وأرقام و _ . - فقط)
   الحقولا يُدمان داخل المغلف المشفر نفسه — لا يمكن لأي سكريبت تغييرهما.

   ثم تتحكم في المؤشر من خادمك — التطبيق يسأل خادمك عند الإقلاع وكل 15 دقيقة:
     GET {server}?ind=ID&dev=USER-ID&left=الأيام المتبقية&st=الحالة&v=1
     (left = الأيام المتبقية محليًا — تتابعها من خادمك وتقرر بنفسك)
   ويقبل تطبيقك من خادمك استجابة JSON فقط (أقل من 16KB):
     {"ok":1,"cmds":[
       {"cmd":"duration","days":30},             ← تحديد/تمديد الاشتراك 30 يومًا
       {"cmd":"duration","until":"2026-12-31"},  ← أو حتى تاريخ محدد
       {"cmd":"enable"},                         ← تشغيل المؤشر
       {"cmd":"disable"},                        ← إيقاف المؤشر
       {"cmd":"status","state":"active"},        ← active أو expired (ساري/انتهى)
       {"cmd":"notify","text":"تم تحديث المؤشر — فلترة أدق وإصلاحات"} ← إشعار للمستخدم
     ]}
   هذه الأوامر كلها — وفقط: أي أمر آخر يُتجاهل، ولا يُنفَّذ أي كود قادم من الخادم،
   ولا يمكن رفع أو سحب أي ملف عبر هذه القناة إطلاقًا — أي استجابة تحوي base64
   أو ملفًا أو بيانات كبيرة تُرفض ويُحظر خادمك 10 دقائق.

   قاعدة بيانات صغيرة محمية داخل التطبيق لكل مؤشر مدفوع (لا يمكن حذفها أو عبثها):
     • تحفظ لكل مؤشر: معرفه، خادمه، تاريخ انتهاء الاشتراك، الحالة، الأيام المتبقية،
       وآخر تاريخ رأاه النظام.
     • موقّعة HMAC-SHA256 بمفتاح مشتق من مفتاح التطبيق + بصمة هذا الجهاز، وبنسخ
       مخفية متعددة — حذفها أو تعديلها لا يمدد الاشتراك: (الفشل مغلق) المؤشر
       يتوقف حتى يجيب خادمك بالحقيقة ويعيد الحالة.
     • مراقبة الأيام تعمل حتى لو حذف المستخدم سجلّات التطبيق: الأيام تُحسب
       من آخر تاريخ رأاه النظام — رجّع المستخدم ساعة جهازه فلن يكسب يومًا واحدًا.
     • التذكير تلقائي: قبل الانتهاء بـ 7 و3 ويوم واحد يظهر إشعار «ينتهي اشتراك
       مؤشر كذا بعد N يوم — يجب التجديد»، وعند الانتهاء: «انتهى الشهر/الاشتراك —
       يجب التجديد» وينطفئ المؤشر حتى تفعّله أنت من خادمك.
     • إشعاراتك (notify) تظهر في بطاقة الإشعارات الصغيرة بجانب زر الإعدادات —
       نص فقط حتى 300 حرف، بلا HTML ولا روابط ملفات.

   الحماية المدمجة (لا يمكن لأي سكريبت تجاوزها):
     • مفتاح فك تشفير المؤشرات مدموج داخل التطبيق — لا يُكتب في ملف، لا يصل إلى
       صفحة الويب، ولا يمكن نسخه؛ لا يظهر إلا بصمته في الإعدادات.
     • بيان المدفوع (المعرف + الخادم) داخل التشفير — كود المؤشر نفسه لا يراه ولا يغيره.
     • كود المؤشر ممنوع منه الشبكة والتخزين والجسور نهائيًا (فحص مزدوج قبل التشغيل
       وداخل QuickJS) — ولا يرى الترخيص ولا القاعدة المحمية ولا خادم التحكم شيء منه.
     • الأوامر تُفحص بقائمة بيضاء صارمة داخل التطبيق — تنفيذ الكود من الخادم مستحيل.
   ═══════════════════════════════════════════════════════════════════════════ */

return {
  label: 'BADI Guide',
  type: 'overlay',
  color: '#22E08A',
  settings: { period: 20, mult: 2 },

  calculate(candles, s) {
    const closes = candles.map(c => c.close);
    return Indicators.bollinger(closes, s.period, s.mult);   // {mid, upper, lower}
  },

  render(ctx, v, h, s) {
    if (!v) return;

    // (أ) تعبئة شفافة بين الحدين — الأشكال المملوءة ممكنة أيضًا
    ctx.fillStyle = 'rgba(34, 224, 138, 0.08)';
    ctx.beginPath();
    let started = false;
    for (let i = h.firstIdx; i <= h.lastIdx; i++) {
      if (v.upper[i] == null) continue;
      const x = h.indexToX(i), y = h.priceToY(v.upper[i]);
      if (!started) { ctx.moveTo(x, y); started = true; } else ctx.lineTo(x, y);
    }
    for (let i = h.lastIdx; i >= h.firstIdx; i--) {
      if (v.lower[i] == null) continue;
      ctx.lineTo(h.indexToX(i), h.priceToY(v.lower[i]));
    }
    ctx.closePath();
    ctx.fill();

    // (ب) خطوط بعرض ولون ونمط مخصص
    const line = (arr, color, width, dash) => {
      ctx.strokeStyle = color; ctx.lineWidth = width;
      ctx.setLineDash(dash || []);
      ctx.beginPath();
      let st = false;
      for (let i = h.firstIdx; i <= h.lastIdx; i++) {
        const val = arr[i];
        if (val == null) { st = false; continue; }
        const x = h.indexToX(i), y = h.priceToY(val);
        if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    };
    line(v.upper, '#FF4D5E', 1.4);          // الحد الأعلى — أحمر
    line(v.lower, '#22E08A', 1.4);          // الحد الأدنى — أخضر
    line(v.mid, '#38bdf8', 1.6, [5, 4]);    // الوسط — أزرق متقطع

    // (ج) دائرة على آخر شمعة + نص حر — رسم أي شيء فوق الشارت
    const last = h.lastIdx, mid = v.mid[last];
    if (mid != null) {
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.arc(h.indexToX(last), h.priceToY(mid), 3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = '#8b93a7';
    ctx.font = '11px sans-serif';
    ctx.fillText('هذا نص حر — يمكنك رسم أي شيء على الشارت (Canvas 2D كامل)',
                 h.chartLeft + 10, h.priceTop + 16);
  },

  signal(candles, v, s) {
    // مثال شكل إشارة — محايد افتراضيًا (يعيد null حتى لا يزعجك أثناء التجربة):
    // const info = Indicators.market.info();            // {name, payout, open, otc}
    // if (!info.open) return null;                      // السوق مغلق؟ لا إشارات
    // return { dir: 'up', price: candles[candles.length - 1].close,
    //          chats: '@mychannel' };                   // معرف تلجرام لهذا المؤشر
    return null;
  }
};"""


def _seed_guide_file():
    """كتابة ملف دليل البرمجة والرسم في مجلد Indicators (مرة واحدة) — الاسم بالإنجليزية (طلب المستخدم)."""
    try:
        # ترحيل: حذف النسخ القديمة ذات الاسم العربي إن وُجدت
        for old in LEGACY_GUIDE_FILES:
            op = os.path.join(BADI_IND_DIR, old)
            if os.path.exists(op):
                try:
                    os.remove(op)
                except Exception:
                    pass
        p = os.path.join(BADI_IND_DIR, GUIDE_FILE_NAME)
        cur = ""
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    cur = fh.read()
            except Exception:
                cur = ""
        # يُعاد كتابة الدليل عند تغيّر محتواه — ليصل قسم المؤشرات المدفوعة الجديد لكل المستخدمين
        if cur.strip() != GUIDE_JS.strip():
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(GUIDE_JS + "\n")
    except Exception:
        pass


def _ensure_badi_dirs():
    for d in (BADI_DIR, BADI_IND_DIR, BADI_TOOL_DIR, BADI_THUMB_DIR):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass
    _seed_guide_file()


def _safe_file_name(name):
    """اسم ملف آمن — يمنع المسارات المطلقة/النسبية ويحافظ على الامتداد."""
    n = os.path.basename(str(name or "").strip())
    n = n.replace("\\", "_").replace("/", "_")
    return n[:120] if n else ""


def _disk_dir_for(kind):
    """مجلد الملف حسب نوعه: المؤشرات (js/py) في Indicators والأدوات في Tools."""
    return BADI_TOOL_DIR if str(kind) in ("jstool", "tool") else BADI_IND_DIR


def _disk_path_for(f):
    """المسار الحقيقي لملف على القرص حسب نوعه واسمه."""
    return os.path.join(_disk_dir_for(f.get("kind")), _safe_file_name(f.get("fileName")))


def _read_text_file(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except Exception:
            return None


def _write_text_file(path, text):
    """كتابة آمنة: ملف مؤقت ثم استبدال — حتى لا يفسد ملف المؤشر عند انقطاع مفاجئ."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


# بيئة مساعدين مبسطة لفحص كود المؤشر داخل QuickJS (نفس واجهة window.Indicators في الشارت)
_QJS_STUBS = r'''
var Indicators = {
  sma: function (arr, p) { var out = [], s = 0, i; p = p || 1;
    for (i = 0; i < arr.length; i++) { s += arr[i]; if (i >= p) s -= arr[i - p]; out.push(i >= p - 1 ? s / p : null); } return out; },
  ema: function (arr, p) { var k = 2 / ((p || 1) + 1), out = [], e = null, i;
    for (i = 0; i < arr.length; i++) { e = (e === null) ? arr[i] : arr[i] * k + e * (1 - k); out.push(e); } return out; },
  rsi: function (candles, p) { var out = [null], g = 0, l = 0, i; p = p || 14;
    for (i = 1; i < candles.length; i++) { var d = candles[i].close - candles[i - 1].close;
      g = (g * (p - 1) + Math.max(d, 0)) / p; l = (l * (p - 1) + Math.max(-d, 0)) / p;
      out.push(l === 0 ? 100 : 100 - 100 / (1 + g / l)); } return out; },
  atr: function (candles, p) { var tr = [], i;
    for (i = 0; i < candles.length; i++) tr.push(i === 0 ? candles[i].high - candles[i].low
      : Math.max(candles[i].high - candles[i].low, Math.abs(candles[i].high - candles[i - 1].close), Math.abs(candles[i].low - candles[i - 1].close)));
    return Indicators.ema(tr, p || 14); },
  /* API السوق داخل بيئة الفحص المعزولة — نفس واجهة الشارت (معلومات الزوج + الدفع + الحالة) */
  market: {
    info: function (name) { return { name: String(name || "EUR/USD"), payout: 85, open: true, otc: false }; },
    assets: function () { return [{ name: "EUR/USD", payout: 92, open: true, otc: false }]; },
    added: function () { return ["EUR/USD"]; },
    current: function () { return "EUR/USD"; }
  },
  stoch: function (candles, p, sm) {
    var p2 = p || 14, s2 = sm || 3, raw = [], i, j, k = [], d = [];
    for (i = 0; i < candles.length; i++) {
      if (i < p2 - 1) { raw.push(null); continue; }
      var hh = -1e18, ll = 1e18;
      for (j = i - p2 + 1; j <= i; j++) { hh = Math.max(hh, candles[j].high); ll = Math.min(ll, candles[j].low); }
      raw.push(hh === ll ? 50 : (candles[i].close - ll) / (hh - ll) * 100);
    }
    for (i = 0; i < raw.length; i++) {
      if (raw[i] == null) { k.push(null); continue; }
      var seg = [], w;
      for (w = i; w >= 0 && w > i - s2; w--) { if (raw[w] == null) break; seg.push(raw[w]); }
      k.push(seg.length === s2 ? seg.reduce(function (a, b) { return a + b; }, 0) / s2 : null);
    }
    for (i = 0; i < k.length; i++) {
      if (k[i] == null) { d.push(null); continue; }
      var seg2 = [], w2;
      for (w2 = i; w2 >= 0 && w2 > i - s2; w2--) { if (k[w2] == null) break; seg2.push(k[w2]); }
      d.push(seg2.length === s2 ? seg2.reduce(function (a, b) { return a + b; }, 0) / s2 : null);
    }
    return { k: k, d: d }; }
};
'''


class Backend(QObject):
    langChanged = Signal()
    darkChanged = Signal()
    filesChanged = Signal()
    candlesChanged = Signal()
    histChainChanged = Signal()            # v14.5: سلسلة التاريخ تعمل الآن (لا إعادة ضبط للشارت أثناءها)
    histChanged = Signal()
    consoleMsg = Signal(str, str)          # kind, text
    pyValues = Signal(str, str, str)       # id, seriesJson, rangeJson
    testResult = Signal(bool, str)
    shotSaved = Signal(bool, str)          # ok, path
    liveChanged = Signal()
    addedChanged = Signal()                # قائمة العملات المضافة تغيّرت (لوحة الإعدادات)
    sigResult = Signal(str)                # نتيجة إشارة (WIN/LOSS) بعد انتهاء المدة
    myIndsChanged = Signal()               # قائمة مؤشراتي في صفحة المؤشرات تغيّرت (طلب المستخدم)
    notifChanged = Signal()                # بطاقة الإشعارات تغيّرت (طلب المستخدم)
    paidCmd = Signal(str)                  # أمر تحكم بعيد صالح: تشغيل/إيقاف مؤشر مدفوع (طلب المستخدم)
    qxEvent = Signal(str)                  # LIVE SERVER EDITION: أحداث خادم QX (الدخول/لوحة العملات/دفعات التمرير)
    savedEmailChanged = Signal()           # v15.2: تغيّر البريد المحفوظ («تذكّرني»)

    def __init__(self):
        super().__init__()
        cfg = _read_json(CFG_FILE, {})
        self._lang = cfg.get("lang", "en")
        self._dark = bool(cfg.get("dark", True))
        # v14.3 (طلب المستخدم): عدد أيام شموع التاريخ المجلوبة عند فتح العملة —
        # الافتراضي يومان، يقبل 0.5 حتى 30 يوم. يُضبط من بطاقة الإعدادات وحفظ.
        try:
            _hd = float(str(cfg.get("hist_days", 0.80)).replace(",", "."))
        except Exception:
            _hd = 0.80
        self._hist_days = max(0.5, min(30.0, _hd))
        # v14.7 (طلب المستخدم حرفياً): «اريد ان تجلب 700 شمعة بدل 300 شمعة
        # كدفعة مباشرة للعملة ويمكن تعديلها في الاعدادات الى 1000 شمعة في
        # الدفعة» — حجم الدفعة المباشرة عند فتح العملة وحجم كل دفعة تُرفع
        # إلى الشارت. الافتراضي 700، يقبل التعديل حتى 1000، يُحفظ بالضغط على حفظ.
        try:
            _bc = int(float(str(cfg.get("batch_candles", 700)).replace(",", ".")))
        except Exception:
            _bc = 700
        self._batch_candles = max(100, min(1000, _bc))
        self._market = "real"        # قسم الحساب الحقيقي/التجريبي حُذف — يبقى وسم السوق للعملات OTC فقط
        # LIVE SERVER EDITION (طلب المستخدم): العملة الافتراضية ثابتة دائماً —
        # الشارت يفتح على BRLUSD_otc (باسمها الحقيقي USD/BRL (OTC) كما في الخادم —
        # v13.2) مهما كانت الإعدادات القديمة المحفوظة
        self._asset = QX_OPENER_NAME
        self._tf = cfg.get("tf", "1m")
        if not isinstance(self._tf, str) or self._tf not in dict(TFS):
            self._tf = "1m"
        # LIVE SERVER EDITION: شريط العملات يبدأ نظيفاً بعملة فتح الشارت فقط —
        # قوائم العملات القديمة المحفوظة من نسخة الشموع الوهمية (AUD/CAD،
        # EUR/GBP…) لا تعود إلى الشريط أبداً؛ وأي عملة أخرى يدخلها المستخدم
        # بنفسه من قائمة + (العملات الحقيقية من الخادم) — طلب المستخدم
        # «العملات الوهمية التي في التطبيق انزعها».
        self._added = [QX_OPENER_NAME]
        # v13.2: خريطة الاسم الحقيقي → رمز الخادم تُبذر بعملة فتح الشارت
        # حتى يعمل الجلب فور الدخول قبل وصول اللوحة الكاملة
        self._qx_symbols = {QX_OPENER_NAME: QX_OPENER_SYMBOL}
        self._live = True        # البث الحي يعمل مباشرة دائمًا — الشموع متحركة بلا زر (طلب المستخدم)
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
        self._qx_resync_pending = False  # v14.3: مزامنة كاملة بعد إصلاح سد الثغرات
        self._qx_pre_log = 0.0         # خنق سجلات حالة التحميل المسبق
        # v15.2 (طلب المستخدم): دائرة تحميل الشموع — حالة صريحة تبدأ عند بداية
        # جلب شموع العملة المفتوحة وتنتهي عند وصولها (أو مهلة أمان 60 ثانية)
        self._qx_loading = False       # جلب شموع العملة الحالية جارٍ الآن
        self._qx_loading_at = 0.0      # لحظة بدء الجلب
        self._qx_tf_retry = 0.0        # خنق إعادة محاولة جلب فريم أعلى
        self._qx_ensure_at = {}        # v13.1: آخر جلب فوري لكل عملة (خنق 15 ثانية)
        self._qx_ensure_fail = {}      # v13.1: عدّاد فشل الجلب الفوري (خنق تصاعدي)
        # v13.2 (طلب المستخدم): طابور جلب متسلسل — فتح عدة عملات بسرعة يجلبها
        # واحدة تلو الأخرى مع فاصل بين عملة وأخرى، بلا تسرّع ولا طلبات متوازية
        self._qx_loadq = []            # طابور العملات المطلوب جلبها
        self._qx_load_pending = set()  # العملات المنتظرة في الطابور (منع التكرار)
        self._qx_load_lock = threading.Lock()
        self._qx_load_busy = False     # عامل الطابور يعمل الآن
        self._qx_sealed = set()        # v15.3: العملات التي سُدّت ثغراتها — آلة الأصل مرة واحدة لكل فتح
        # v14.5 (طلب المستخدم): طلب واحد بمدى الأيام كاملاً — الخادم يجيبه على
        # دفعات وكل دفعة (300 شمعة) تُرفع إلى الشارت فور وصولها بعد المعالجة.
        # لا طلب 300 شمعة جديدة في كل مرة (كان يعيد نفس الدفعة الأولى).
        self._qx_chain_gen = {}        # مولّد لكل مفتاح (عملة، فريم) — يُجهض السلسلة القديمة عند بدء أحدث
        self._qx_chain_running = {}    # المفتاح -> مولّد السلسلة الجارية (لحالة histChainActive)
        self._qx_chain_done = set()    # عملات/فريمات بلغت هدف الأيام أو نفد تاريخها
        self._qx_chain_lock = threading.Lock()
        self._qx_chain_active = False  # سلسلة التاريخ تعمل للعملة/الفريم المعروضين الآن
        self._files = self._load_files()
        _ensure_badi_dirs()
        self.syncDiskFiles(emit=False)     # استيراد أي ملفات وضعها المستخدم في مجلد BadiCharts
        # ── مراقبة مجلدي BadiCharts: أي ملف يوضعه المستخدم يُكتشف فورًا ويظهر في
        #    صفحة المؤشرات مباشرة دون إعادة تشغيل (طلب المستخدم) ──
        self._watcher = QFileSystemWatcher(self)
        self._watcher.addPath(BADI_IND_DIR)
        self._watcher.addPath(BADI_TOOL_DIR)
        self._watcher.directoryChanged.connect(self._on_dir_changed)
        self._hist = _read_json(os.path.join(CFG_DIR, "signals.json"), [])
        self._sigpend = []       # إشارات بانتظار نتيجتها (WIN/LOSS بعد مدة الفريم)
        # ── مظهر الشارت القابل للتخصيص من الإعدادات (خلفية/ألوان الشموع...) ──
        self._chart_theme = dict(CHART_THEME_DEFAULTS)
        saved_ct = cfg.get("chart_theme") or {}
        if isinstance(saved_ct, dict):
            for k, v in saved_ct.items():
                if k in self._chart_theme and isinstance(v, str) and re.match(r"^#[0-9a-fA-F]{3,8}$|^rgba?\(.*\)$", v.strip()):
                    self._chart_theme[k] = v.strip()
        self._py_mods = {}       # id -> module dict
        self._py_err = {}        # id -> count
        self._py_names = {}      # id -> fileName
        self._pending = None     # إشارة بانتظار لقطة الشاشة
        os.makedirs(SHOTS_DIR, exist_ok=True)

        # ── المؤشرات المدفوعة: بطاقة الإشعارات (بلا إشعارات جاهزة — المبرمج يرسلها من خادمه)
        #    + قناة تحكم المبرمج عبر خادمه بأوامر بيضاء فقط (طلب المستخدم) ──
        self._notifs = []            # إشعارات البطاقة: نص فقط — لا ملفات إطلاقًا عبر هذه القناة
        self._paid_block = {}        # خادم تجاوز الحدود → حظر مؤقت 10 دقائق (تشديد الحماية)
        self._paidT = QTimer(self)
        self._paidT.setInterval(15 * 60 * 1000)
        self._paidT.timeout.connect(self._paid_poll)
        self._paidT.start()
        QTimer.singleShot(6000, self._paid_poll)
        self._paidW = QTimer(self)
        self._paidW.setInterval(60 * 60 * 1000)
        self._paidW.timeout.connect(self._paid_watch)
        self._paidW.start()
        QTimer.singleShot(7000, self._paid_watch)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)
        # تشغيل المؤقت فعليًا — بلا هذا السطر كان محرك الشموع الحية متوقفًا تمامًا
        # ولهذا لم تكن شموع جديدة تظهر في التطبيق (الشارت متجمد)
        self._timer.start()
        # ── LIVE SERVER EDITION: مضخة بيانات خادم QX ──
        # تسحب الأسعار الحية من محرك الخادم (يعمل داخل التطبيق) وتدفعها للشارت،
        # وتراقب لوحة العملات (الدفع + مفتوح/مغلق) وحالة التحميل المسبق.
        self._qxT = QTimer(self)
        # v15 (طلب المستخدم حرفياً): التحديث ليس كل 400/500 ميلي ثانية بل كل
        # تيك يصل — المؤقّت فاتح فقط (40ms) و_qx_poll تخرج فوراً بلا تيك جديد
        self._qxT.setInterval(40)
        self._qxT.timeout.connect(self._qx_poll)
        self._qxT.start()

    # ---------- خصائص الواجهة ----------
    def _get_lang(self):
        return self._lang

    def _set_lang(self, v):
        if v in T and v != self._lang:
            self._lang = v
            self.langChanged.emit()
            self._save_cfg()

    lang = Property(str, _get_lang, _set_lang, notify=langChanged)
    s = Property("QVariantMap", lambda self: T[self._lang], notify=langChanged)
    rtl = Property(bool, lambda self: self._lang == "ar", notify=langChanged)

    def _get_dark(self):
        return self._dark

    def _set_dark(self, v):
        if v != self._dark:
            self._dark = bool(v)
            self.darkChanged.emit()
            self._save_cfg()

    dark = Property(bool, _get_dark, _set_dark, notify=darkChanged)
    c = Property("QVariantMap", lambda self: DARK if self._dark else LIGHT, notify=darkChanged)

    # ---------- الحساب والرصيد والصفقات حُذفت بالكامل (طلب المستخدم) ----------

    @Property(list, constant=True)
    def board(self):
        """كل العملات المتاحة (اسم + نسبة الدفع + علم الزوج مدموجاً) للوحة الإعدادات."""
        return BOARD

    @Slot(str, result=bool)
    def marketOpen(self, name):
        """حالة السوق من خادم QX الحقيقية عند توفرها — وإلا القاعدة المحلية الاحتياطية."""
        n = str(name or "")
        try:
            for b in self._qx_board:
                if b.get("name") == n:
                    return bool(b.get("open"))
        except Exception:
            pass
        if "OTC" in n:
            return True
        if "BTC" in n or "ETH" in n:
            return True
        now = datetime.now(timezone.utc)
        js_day = (now.weekday() + 1) % 7        # الأحد=0 … السبت=6 (مطابق لـ getUTCDay في الويب)
        hour = now.hour + now.minute / 60.0
        return not (js_day == 6 or (js_day == 5 and hour >= 22) or (js_day == 0 and hour < 22))

    @Property(list, notify=addedChanged)
    def added(self):
        """العملات المعروضة على شريط العملات (المضافة فقط)."""
        return self._added

    def _valid_board_names(self):
        """أسماء العملات الصالحة للشريط: لوحة الخادم الحقيقية عند توفرها —
        والقائمة الوهمية القديمة احتياطاً قبل وصول اللوحة فقط (طلب المستخدم:
        العملات الوهمية انزعها — يُقبل على الشريط الحقيقي من خادم Quotex)."""
        real = [b.get("name") for b in self._qx_board
                if isinstance(b, dict) and b.get("name")]
        if real:
            return real
        return [b["name"] for b in BOARD]

    @Slot(str)
    def toggleAdded(self, name):
        """إضافة/إزالة عملة من الشريط — مع إبقاء عملة واحدة على الأقل دائمًا."""
        if not isinstance(name, str) or name not in self._valid_board_names():
            return
        if name in self._added:
            if len(self._added) <= 1:      # يجب أن تبقى عملة واحدة على الأقل في الشريط
                return
            self._added = [n for n in self._added if n != name]
        else:
            self._added = self._added + [name]
        self._save_cfg()
        self.addedChanged.emit()

    @Slot(str)
    def setAddedJson(self, js):
        """الصفحة أبلغت عن قائمة جديدة (حذف من الشريط عبر × أو قائمة +)."""
        try:
            arr = json.loads(js)
        except Exception:
            return
        if not isinstance(arr, list):
            return
        board_names = self._valid_board_names()   # العملات الحقيقية من الخادم فقط
        clean = list(dict.fromkeys(n for n in arr if isinstance(n, str) and n in board_names))
        if not clean:                       # لا يُحذف كل شيء — عملة واحدة على الأقل
            return
        if clean == self._added:
            return
        self._added = clean
        self._save_cfg()
        self.addedChanged.emit()

    @Property(list, constant=True)
    def logoLayers(self):
        return LOGO_LAYERS

    @Property(list, constant=True)
    def libs(self):
        return LIB

    @Property(list, constant=True)
    def tfs(self):
        return [k for k, _ in TFS]

    @Property(str, notify=candlesChanged)
    def candlesJson(self):
        return json.dumps(self._candles, separators=(",", ":"))

    @Property(str, notify=candlesChanged)
    def lastTickJson(self):
        """آخر شمعة فقط — تُدفع كل ثانية بدون إعادة تسلسل المصفوفة كاملة (أداء)."""
        return json.dumps(self._candles[-1], separators=(",", ":")) if self._candles else "{}"

    @Property(str, notify=candlesChanged)
    def tailJson(self):
        """آخر 3 شموع — تُدفع كل دفعة: الشمعة الحية + الإغلاق النهائي للشمعة
        المغلقة قبلهما، حتى لا تبقى شمعة مغلقة خاطئة في الشارت ثم "تقفز" فجأة
        إلى قيمتها الصحيحة عند أول مزامنة كاملة (أُصلحت بطلب المستخدم)."""
        return json.dumps(self._candles[-3:], separators=(",", ":")) if self._candles else "[]"

    @Slot(int, result=str)
    def tailJsonN(self, n):
        """v13.1: آخر n شمعة فقط — دفعة ذيل خفيفة تُدفع للشارت عند تراكم أكثر
        من شمعة بين نبضتين، بدل إعادة إرسال المصفوفة كاملة (بلا قفزات ولا
        إعادة ضبط للعرض — طلب المستخدم). تُدمج عبر pushTail نفسها."""
        try:
            n = max(1, int(n))
            return json.dumps(self._candles[-n:], separators=(",", ":"))
        except Exception:
            return "[]"

    @Property(int, notify=candlesChanged)
    def candlesCount(self):
        return len(self._candles)

    @Property(bool, notify=candlesChanged)
    def chartLoading(self):
        """v13.2/v15.2 (طلب المستخدم): دائرة تحميل في الشارت — True فقط أثناء
        جلب شموع العملة المفتوحة فعلاً (حالة صريحة تبدأ عند بداية الجلب
        وتنتهي عند وصول الشموع أو مهلة 60 ثانية) — بدل شارت أسود فارغ."""
        return bool(self._qx_logged and getattr(self, "_qx_loading", False)
                    and not self._candles)

    @Property(str, notify=filesChanged)
    def filesJson(self):
        return json.dumps(self._files, ensure_ascii=False)

    @Property(str, notify=histChanged)
    def histJson(self):
        return json.dumps(self._hist[-200:], ensure_ascii=False)

    @Property(bool, notify=liveChanged)
    def live(self):
        return self._live

    @Property(str, notify=candlesChanged)
    def assetLabel(self):
        return self._asset

    @Property(str, notify=candlesChanged)
    def tfLabel(self):
        return self._tf

    @Property(int, notify=candlesChanged)
    def dec(self):
        return self._price_decimals()

    def _price_decimals(self):
        """دقة السعر المطابقة لمنصة Quotex: أولاً أرقام الخادم الرسمية
        (mt4_digits — BRLUSD_otc مثلاً لها أرقامها الخاصة)، وإلا تقدير من
        آخر سعر حقيقي. تُستعمل للسعر على المحور وبطاقة OHLC
        (priceScale = 10^decimals في مكتبة الشارت)."""
        try:
            qx = _qx_module()
            if qx is not None:
                api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
                if api:
                    d = int(qx._get_or_create_asset(api).digits())
                    if 0 < d <= 10:
                        return d
        except Exception:
            pass
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
            return 5

    @Property(int, notify=candlesChanged)
    def tfSec(self):
        return self._tf_sec()

    # ---------- أدوات داخلية ----------
    def _asset_cfg(self, asset=None):
        name = str(asset or self._asset or "")
        for a in ASSETS["real"] + ASSETS["otc"]:
            if a["name"] == name:
                return a
        return ASSETS["real"][0]

    def _tf_sec(self):
        return dict(TFS).get(self._tf, 60)

    def _save_cfg(self):
        _write_json(CFG_FILE, {"lang": self._lang, "dark": self._dark,
                               "asset": self._asset, "tf": self._tf,
                               "added": self._added,
                               "chart_theme": self._chart_theme,
                               "hist_days": self._hist_days,
                               "batch_candles": self._batch_candles})

    def _load_files(self):
        data = _read_json(FILES_FILE, None)
        if isinstance(data, dict) and isinstance(data.get("files"), list):
            data = data["files"]
        out = []
        base_names = {"js": "My Indicator", "py": "Python Indicator", "jstool": "My Tool"}
        for s in SEEDS:
            sfx = random_suffix(6)
            ext = "py" if s["kind"] == "py" else "js"
            out.append({"id": s["kind"] + "_" + sfx.lower(),
                        "fileName": f"{base_names[s['kind']]}.{ext}", "kind": s["kind"],
                        "code": s["code"], "enabled": False})
        if isinstance(data, list) and data:
            # ترحيل اسم الدليل للإنجليزية (طلب المستخدم): تجاهل المدخل القديم ذا الاسم العربي
            # حتى لا تعيد المزامنة كتابته إلى القرص بعد حذفه
            out = [f for f in data if isinstance(f, dict)
                   and str(f.get("fileName") or "") not in LEGACY_GUIDE_FILES]
        return out

    def _log(self, kind, text):
        self.consoleMsg.emit(kind, text)

    # ---------- مجلد BadiCharts: حفظ المؤشرات على القرص ومزامنتها ----------
    # كل مؤشر/أداة يُنشأ في التطبيق يُكتب كملف حقيقي داخل BadiCharts/Indicators
    # أو BadiCharts/Tools — وأي ملف يوضعه المستخدم هناك يُستورد تلقائيًا.
    @staticmethod
    def _norm_kind(k):
        k = str(k or "").lower()
        if k in ("js", "indicator"):
            return "indicator"
        if k in ("jstool", "tool"):
            return "tool"
        if k == "py":
            return "py"
        if k == "badi":
            return "badi"
        return "indicator"

    @staticmethod
    def _new_file_id(kind):
        pfx = {"indicator": "ind", "tool": "tool", "py": "py", "badi": "badi"}.get(kind, "ind")
        return pfx + "_" + random_suffix(6).lower()

    def _disk_scan(self):
        """فحص مجلدي BadiCharts: ملفات المؤشرات/الأدوات + ملفات .badi المشفرة."""
        _ensure_badi_dirs()
        items = []
        for d, exts in ((BADI_IND_DIR, ("js", "py")), (BADI_TOOL_DIR, ("js",))):
            try:
                names = sorted(os.listdir(d))
            except Exception:
                continue
            for n in names:
                p = os.path.join(d, n)
                if not os.path.isfile(p) or n.endswith(".tmp"):
                    continue
                ext = n.rsplit(".", 1)[-1].lower() if "." in n else ""
                if ext in exts:
                    code = _read_text_file(p)
                    if code is None:
                        continue
                    kind = "py" if ext == "py" else ("tool" if d == BADI_TOOL_DIR else "indicator")
                    items.append({"fileName": n, "kind": kind, "code": code, "path": p})
                elif ext == "badi":
                    items.append({"fileName": n, "kind": "badi", "code": "", "path": p})
        return items

    def _write_entry_to_disk(self, f):
        """كتابة كود ملف المستخدم إلى مساره الحقيقي في BadiCharts — تُرجع المسار أو None."""
        kind = self._norm_kind(f.get("kind"))
        name = _safe_file_name(f.get("fileName"))
        if not name or kind == "badi" or not str(f.get("code") or "").strip():
            return None
        path = os.path.join(_disk_dir_for(kind), name)
        return path if _write_text_file(path, f.get("code", "")) else None

    def _delete_entry_from_disk(self, f):
        """حذف ملف المستخدم من القرص (مصدره أو ملفه المشفر)."""
        kind = self._norm_kind(f.get("kind"))
        name = _safe_file_name(f.get("fileName"))
        if not name:
            return
        p = f.get("path") if kind == "badi" else os.path.join(_disk_dir_for(kind), name)
        for cand in (p, os.path.join(BADI_IND_DIR, name), os.path.join(BADI_TOOL_DIR, name)):
            try:
                if cand and os.path.isfile(cand):
                    os.remove(cand)
                    break
            except Exception:
                pass

    def syncDiskFiles(self, emit=True):
        """مزامنة قائمة الملفات مع مجلد BadiCharts:
        يستورد الملفات الموضوعة يدويًا، يحدّث الكود المتغير، يعتمد الملفات القديمة،
        يوفر ملفات .badi بجوار ملفاتها الأصلية، ويحذف ما حُذف من المجلد."""
        _ensure_badi_dirs()
        disk = self._disk_scan()
        changed = False
        # فهرس القرص: (اسم منقح، نوع) → عنصر
        disk_map = {}
        for it in disk:
            disk_map[(it["fileName"].lower(), it["kind"])] = it
        # 1) اعتماد/تحديث ملفات المستخدم الموجودة في القائمة
        for f in self._files:
            kind = self._norm_kind(f.get("kind"))
            if kind == "badi":
                continue
            name = _safe_file_name(f.get("fileName"))
            if not name:
                continue
            it = disk_map.get((name.lower(), kind))
            if it is not None:
                if f.get("code") != it["code"]:      # القرص هو المرجع (تعديل خارجي)
                    f["code"] = it["code"]
                    changed = True
            elif str(f.get("code") or "").strip():
                self._write_entry_to_disk(f)          # اعتماد: ملف قديم ليس على القرص بعد
        # 2) استيراد الملفات الجديدة من المجلد (ملفات وضعها المستخدم يدويًا)
        have = set()
        for f in self._files:
            have.add((_safe_file_name(f.get("fileName")).lower(), self._norm_kind(f.get("kind"))))
        for (nl, kind), it in disk_map.items():
            if (nl, kind) in have:
                continue
            self._files.append({"id": self._new_file_id(kind), "fileName": it["fileName"],
                                "kind": kind, "code": it.get("code", ""), "enabled": False,
                                "createdAt": int(time.time() * 1000), "path": it.get("path", "")})
            changed = True
        # 3) حذف ما لم يعد موجودًا على القرص (حذف يدوي من المجلد)
        keep = []
        for f in self._files:
            kind = self._norm_kind(f.get("kind"))
            name = _safe_file_name(f.get("fileName"))
            if kind == "badi":
                p = f.get("path") or ""
                if p and not os.path.isfile(p) and not os.path.isfile(os.path.join(BADI_IND_DIR, name)):
                    changed = True
                    continue
            else:
                if name and not any(os.path.isfile(os.path.join(d, name))
                                    for d in (BADI_IND_DIR, BADI_TOOL_DIR)):
                    changed = True
                    continue
            keep.append(f)
        self._files = keep
        # 4) ترتيب: ملف .badi يظهر مباشرة بجوار ملفه الأصلي (مثل ميتاتريدر) — بدون تغيير ترتيب البقية
        twins = {}
        rest = []
        for f in self._files:
            if self._norm_kind(f.get("kind")) == "badi":
                base = _safe_file_name(f.get("fileName")).rsplit(".", 1)[0].lower()
                twins.setdefault(base, []).append(f)
            else:
                rest.append(f)
        ordered = []
        for f in rest:
            ordered.append(f)
            base = _safe_file_name(f.get("fileName")).rsplit(".", 1)[0].lower()
            if base in twins:
                ordered.extend(twins.pop(base))
        for v in twins.values():
            ordered.extend(v)
        if ordered != self._files:
            self._files = ordered
            changed = True
        if changed:
            _write_json(FILES_FILE, self._files)
            if emit:
                self.filesChanged.emit()
            self.myIndsChanged.emit()          # حدّث "مؤشراتي" في صفحة المؤشرات
        return changed

    # ---------- الملفات ----------
    @Slot(str)
    def saveFiles(self, files_json):
        try:
            data = json.loads(files_json)
            if isinstance(data, dict) and isinstance(data.get("files"), list):
                data = data["files"]          # تقرير الصفحة يأتي مغلّفاً {v, files}
            if not isinstance(data, list):
                return
            old = {f.get("id"): f for f in self._files if isinstance(f, dict)}
            new = []
            for f in data:
                if not isinstance(f, dict) or not isinstance(f.get("id"), str):
                    continue
                f = dict(f)
                f["kind"] = self._norm_kind(f.get("kind"))
                f["fileName"] = _safe_file_name(f.get("fileName"))
                new.append(f)
            # حذف من القرص: ملفات اختفت من القائمة أو غيّرت اسمها
            new_ids = {f["id"] for f in new}
            for fid, of in old.items():
                if fid in new_ids:
                    nf = next((x for x in new if x["id"] == fid), None)
                    if nf and _safe_file_name(nf.get("fileName")) != _safe_file_name(of.get("fileName")):
                        self._delete_entry_from_disk(of)   # إعادة تسمية → احذف الاسم القديم
                else:
                    self._delete_entry_from_disk(of)       # حذف من المحرر → حذف من القرص
            # كتابة كل ملف إلى مساره الحقيقي (فقط عند تغيّر الكود — لتجنب الكتابة الزائدة)
            for f in new:
                p = _disk_path_for(f) if self._norm_kind(f.get("kind")) != "badi" else None
                if p:
                    old_code = _read_text_file(p)
                    if old_code != f.get("code", ""):
                        self._write_entry_to_disk(f)
            self._files = new
            _write_json(FILES_FILE, self._files)
            self.myIndsChanged.emit()          # حدّث "مؤشراتي" في صفحة المؤشرات
        except Exception as e:
            self._log("err", f"save: {e}")

    @Slot()
    def rescanFiles(self):
        """فحص مجلد BadiCharts واستيراد أي ملفات جديدة وضعها المستخدم يدويًا."""
        if self.syncDiskFiles():
            self._log("info", "BadiCharts folder synced — indicators/tools reloaded")
        self.myIndsChanged.emit()

    @Slot()
    def seedTestInd(self):
        """مؤشر تجريبي في مجلد BadiCharts/Indicators للفحص الآلي (اختبار الصورة المصغرة)."""
        try:
            os.makedirs(BADI_IND_DIR, exist_ok=True)
            p = os.path.join(BADI_IND_DIR, "Test RSI.js")
            if not os.path.exists(p):
                code = (
                    "return { label: 'Test RSI', type: 'pane', color: '#b39ddb', settings: { period: 14 },\n"
                    "  calculate(candles, s) { return Indicators.rsi(candles.map(c => c.close), s.period); },\n"
                    "  getRange() { return { min: 0, max: 100 }; } };\n"
                )
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(code)
            # ملف مشفر تجريبي بجوار أصله — لاختبار التشغيل الداخلي للمشفر في الفحص الآلي
            enc_p = os.path.join(BADI_IND_DIR, "Test Enc.badi")
            if not os.path.exists(enc_p):
                enc_code = (
                    "return { label: 'Test Enc', type: 'overlay', color: '#38bdf8', settings: { period: 10 },\n"
                    "  calculate(candles, s) { return { EMA: Indicators.ema(candles.map(c => c.close), s.period) } } };\n"
                )
                r = json.loads(self.badiExport(enc_code, "Test Enc.js", "indicator", ""))
                if not r.get("ok"):
                    self._log("err", "seedTestInd: encrypt — " + str(r.get("error", "")))
            if self.syncDiskFiles():
                self.myIndsChanged.emit()
        except Exception as e:
            self._log("err", "seedTestInd: " + str(e))

    def _on_dir_changed(self, _path):
        """المستخدم وضع/حذف ملفًا في مجلد BadiCharts — اكتشاف فوري (طلب المستخدم).
        تأخير بسيط حتى يكتمل النسخ، ثم إعادة فحص وتحديث صفحة المؤشرات."""
        try:
            self._watcher.addPath(BADI_IND_DIR)
            self._watcher.addPath(BADI_TOOL_DIR)
        except Exception:
            pass
        QTimer.singleShot(450, self._rescan_after_change)

    def _rescan_after_change(self):
        changed = self.syncDiskFiles()
        if changed:
            self._log("info", "BadiCharts folder synced — indicators/tools reloaded")
        self.myIndsChanged.emit()

    # ---------- مؤشراتي في صفحة المؤشرات + الصور المصغرة (طلب المستخدم) ----------
    def _thumb_index(self):
        """فهرس الصور المصغرة: اسم المؤشر بدون امتداد (صغير) → مسار الصورة."""
        idx = {}
        try:
            for n in os.listdir(BADI_THUMB_DIR):
                base, ext = os.path.splitext(n)
                if ext.lower() in (".jpg", ".jpeg", ".png"):
                    idx[base.lower()] = os.path.join(BADI_THUMB_DIR, n)
        except Exception:
            pass
        return idx

    @Property(str, notify=myIndsChanged)
    def myIndsJson(self):
        """كل مؤشراتك وأدواتك (المشفرة .badi أيضًا) — تظهر في صفحة المؤشرات."""
        items = []
        thumbs = self._thumb_index()
        for f in self._files:
            kind = self._norm_kind(f.get("kind"))
            name = _safe_file_name(f.get("fileName"))
            if not name:
                continue
            base = name.rsplit(".", 1)[0].lower()
            items.append({"fileName": name, "kind": kind, "enc": kind == "badi",
                          "thumb": thumbs.get(base, "")})
        return json.dumps(items, ensure_ascii=False)

    @Slot(str, str)
    def saveIndThumb(self, file_name, data_url):
        """لقطة المؤشر: تُحفظ عند الحفظ أو التشغيل الصريح وتُحدَّث كل مرة (طلب المستخدم).
        لا تُلتقط إطلاقًا إن لم يُحفظ/يُشغَّل المؤشر من المستخدم."""
        try:
            base = _safe_file_name(file_name).rsplit(".", 1)[0]
            if not base or not isinstance(data_url, str):
                return
            if ";base64," not in data_url or "," not in data_url:
                return
            raw = base64.b64decode(data_url.split(",", 1)[1], validate=False)
            if len(raw) < 512 or len(raw) > 2_000_000:   # لقطة عالية الدقة مضغوطة — السقف أُرفع مع الدقة
                return
            os.makedirs(BADI_THUMB_DIR, exist_ok=True)
            path = os.path.join(BADI_THUMB_DIR, base + ".jpg")
            tmp = path + ".tmp"
            with open(tmp, "wb") as fh:
                fh.write(raw)
            os.replace(tmp, path)
            self.myIndsChanged.emit()
        except Exception:
            pass

    @Slot(str)
    def delMy(self, file_name):
        """حذف مؤشر من بطاقات مؤشراتي (أيقونة سلة بجانب الاسم — طلب المستخدم):
        يحذف الملف من القرص مع ملف .badi الشقيق وصورة المصغرة ثم يزامن القائمة."""
        try:
            name = _safe_file_name(str(file_name))
            if not name:
                return
            base = name.rsplit(".", 1)[0].lower()
            removed = False
            for d in (BADI_IND_DIR, BADI_TOOL_DIR, BADI_DIR):
                try:
                    if not os.path.isdir(d):
                        continue
                    for n in os.listdir(d):
                        low = n.lower()
                        if low == name.lower() or (os.path.splitext(n)[0].lower() == base and low.endswith(".badi")):
                            try:
                                os.remove(os.path.join(d, n))
                                removed = True
                            except Exception:
                                pass
                except Exception:
                    pass
            try:
                if os.path.isdir(BADI_THUMB_DIR):
                    for n in os.listdir(BADI_THUMB_DIR):
                        if os.path.splitext(n)[0].lower() == base:
                            try:
                                os.remove(os.path.join(BADI_THUMB_DIR, n))
                            except Exception:
                                pass
            except Exception:
                pass
            if removed:
                # شطب المدخل من القائمة قبل المزامنة حتى لا يعيد syncDiskFiles كتابته على القرص
                try:
                    self._files = [f for f in self._files
                                   if not (_safe_file_name(f.get("fileName")).lower() == name.lower()
                                           or (_safe_file_name(f.get("fileName")).rsplit(".", 1)[0].lower() == base
                                               and self._norm_kind(f.get("kind")) == "badi"))]
                except Exception:
                    pass
                self.syncDiskFiles()
                self.myIndsChanged.emit()
                self.filesChanged.emit()
                self._log("info", "🗑 Deleted indicator: " + name)
        except Exception:
            pass

    @Slot(str, result=str)
    def shareIndicator(self, file_name):
        """زر الإرسال (طلب المستخدم): لا تشفير — ينسخ ملف المؤشر الأصلي نفسه إلى
        حافظة النظام كملف (يلصقه في أي مكان: تلجرام/مجلد) ثم يفتح تلجرام مباشرة."""
        try:
            name = _safe_file_name(file_name)
            ent = next((f for f in self._files
                        if _safe_file_name(f.get("fileName")).lower() == name.lower()), None)
            kind = self._norm_kind((ent or {}).get("kind"))
            path = ""
            if kind == "badi":
                p = (ent or {}).get("path") or ""
                if p and os.path.isfile(p):
                    path = p
            if not path:
                for d in (BADI_IND_DIR, BADI_TOOL_DIR):
                    cand = os.path.join(d, name)
                    if os.path.isfile(cand):
                        path = cand
                        break
            if not path and ent is not None and kind != "badi" and str(ent.get("code") or "").strip():
                if self._write_entry_to_disk(ent):
                    path = os.path.join(_disk_dir_for(kind), name)
            if not path or not os.path.isfile(path):
                return json.dumps({"ok": False, "error": BADI_MSGS[self._lang]["short"]})
            mime = QMimeData()
            mime.setUrls([QUrl.fromLocalFile(path)])
            mime.setText(path)
            QGuiApplication.clipboard().setMimeData(mime)
            # فتح تلجرام مباشرة بعد النسخ (طلب المستخدم) — تطبيق تلجرام إن وُجد وإلا الويب
            try:
                if not QDesktopServices.openUrl(QUrl("tg://")):
                    QDesktopServices.openUrl(QUrl("https://web.telegram.org/a/"))
            except Exception:
                pass
            return json.dumps({"ok": True, "path": path})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)[:120]})

    @Slot(result=str)
    def badiDirPath(self):
        """مسار مجلد BadiCharts للعرض في الإعدادات."""
        return BADI_DIR

    @Slot(str, result=str)
    def makeFile(self, kind):
        sfx = random_suffix(6)
        ext = "py" if kind == "py" else "js"
        code = {"js": JS_IND_TEMPLATE, "py": PY_IND_TEMPLATE, "jstool": JS_TOOL_TEMPLATE}[kind]
        base = {"js": "My Indicator", "py": "Python Indicator", "jstool": "My Tool"}[kind]
        norm = self._norm_kind(kind)
        # اسم فريد داخل نفس النوع — حتى لا يتصادم ملفان بنفس الاسم على القرص
        taken = {(str(f.get("fileName") or "").lower(), self._norm_kind(f.get("kind")))
                 for f in self._files}
        fname, n = f"{base}.{ext}", 2
        while (fname.lower(), norm) in taken:
            fname = f"{base} ({n}).{ext}"
            n += 1
        f = {"id": kind + "_" + sfx.lower(), "fileName": fname,
             "kind": norm, "code": code, "enabled": False}
        self._write_entry_to_disk(f)          # يُحفظ فورًا في مجلد BadiCharts
        self._files.append(f)
        self.filesChanged.emit()
        self.myIndsChanged.emit()
        _write_json(FILES_FILE, self._files)
        return json.dumps(f)

    @Slot(str, result=str)
    def addFromLib(self, key):
        """إضافة مؤشر جاهز: ملف جديد باسم المكتبة + تشغيل فوري."""
        item = next((l for l in LIB if l["key"] == key), None)
        if not item:
            return "{}"
        sfx = random_suffix(6)
        f = {"id": "js_" + sfx.lower(), "fileName": f"{item['name']}.js",
             "kind": "indicator", "code": item["code"], "enabled": False}
        self._write_entry_to_disk(f)          # يُحفظ فورًا في مجلد BadiCharts
        self._files.append(f)
        self.filesChanged.emit()
        self.myIndsChanged.emit()
        _write_json(FILES_FILE, self._files)
        return json.dumps(f)

    @Slot()
    def saveAll(self):
        _write_json(FILES_FILE, self._files)
        self._log("ok", T[self._lang]["savedall"])

    # ---------- الرمز/الفريم/البث ----------
    @Slot(str, str)
    def switch(self, asset, tf):
        # LIVE SERVER EDITION: التبديل يجلب الشموع الحقيقية من خادم Quotex.
        # العملة موجودة في لوحة الخادم عند توفرها — وإلا يُقبل الاسم كما هو
        # (لوحة العملات قد لا تكون وصلت بعد في ثوانٍ الدخول الأولى).
        # v15.3 (طلب المستخدم): بلا رفض صامت لأي اسم — الاسم يُحوَّل لرمز
        # الخادم داخل _qx_load_feed نفسه (اللوحة أو الاسم النظامي)
        changed = (asset != self._asset or tf != self._tf)
        self._asset = asset
        self._tf = tf if tf in dict(TFS) else self._tf
        self._market = "otc" if "OTC" in self._asset.upper() else "real"
        self._tick = 0
        self._qx_last_sig = None
        # v15.3 (طلب المستخدم: «عملة BRLUSD_otc لماذا لم تضف فيها دائرة تحميل»):
        # كل فتح لعملة يبدأ جلب شموعها فوراً — حتى إعادة فتح العملة المفتوحة
        # نفسها والشارت فارغ (كانت نقرة صامتة بلا دائرة تحميل ولا جلب —
        # والتطبيق يفتح أصلاً على BRLUSD_otc فكانت كل نقراتها صامتة).
        if changed or not self._candles:
            # إفراغ الشموع فوراً حتى لا تبقى شموع العملة السابقة معروضة تحت
            # اسم العملة الجديدة أثناء تحميل بياناتها من الخادم — الشارت
            # يبدأ فارغاً وينتظر بيانات الخادم الحقيقية فقط (لا شموع وهمية).
            self._candles = []
            self._qx_feed_key = ("", "")
            # v15.2 (طلب المستخدم): «عندما نفتح العملة من قائمة العملات» —
            # دائرة تحميل تظهر عند بداية جلب الشموع وتبقى حتى ينتهي الجلب
            # فيظهر الشارت. لا تحميل خلفي — الجلب عند الفتح فقط.
            self._qx_loading_arm()
            self._qx_load_feed(force=True)
            # الجلب اكتمل فوراً (شموع العملة في ذاكرة المحرك أو تيكات جاهزة) —
            # الدائرة تُطفأ في نفس اللحظة
            if self._qx_feed_key == (self._asset, self._tf) and self._candles:
                self._qx_loading_clear()
        self._save_cfg()
        # إعادة حساب كل مؤشرات بايثون المفعّلة على الشموع الجديدة فورًا
        # (بدل انتظار أول تيك — وإلا اختفى الخط لأن القيم القديمة خارج نطاق السعر الجديد)
        # الترتيب مهم: القيم أولًا ثم الدفع — تصل قيم المؤشرات مع الشموع في نفس اللحظة
        if self._py_mods:
            self._compute_py()
        self.candlesChanged.emit()

    @Slot(str, result=str)
    def assetsFor(self, market):
        return json.dumps([a["name"] for a in ASSETS[market]])

    @Slot(bool)
    def setLive(self, on):
        # البث الحي دائم الآن (طلب المستخدم) — لا يمكن إيقافه من الصفحة
        if not self._live:
            self._live = True
            self.liveChanged.emit()
            self._log("info", "Live feed started — " + self._asset + " " + self._tf)

    def _on_tick(self):
        # LIVE SERVER EDITION (طلب المستخدم): الشموع الوهمية انزعت — التغذية الحية
        # تأتي الآن من خادم Quotex عبر _qx_poll() كل 400ms. يبقى هنا فقط تسوية
        # نتائج الإشارات (WIN/LOSS) لأنها تعمل دائماً بغض النظر عن التغذية.
        self._check_sig_results()

    # ═════════════════════════════════════════════════════════════════════
    #  LIVE SERVER EDITION — محرك خادم Quotex داخل التطبيق
    #  نفس الخادم الذي يعمل في الترمينال (qx_server_v13.py) لكن يُقاد من الواجهة:
    #  دخول حقيقي، BRLUSD_otc فوراً (300 شمعة)، بقية العملات واحدة تلو الأخرى،
    #  بث حي لكل عملة فُتح شارتها، ودفعات 300 شمعة عند التمرير للوراء.
    # ═════════════════════════════════════════════════════════════════════
    _QX_FEED_CAP = 45000         # حد الشموع في ذاكرة الواجهة (v14.6: يسمع حتى 30 يوم من فريم الدقيقة نفسه — 43200 شمعة)
    _QX_FEED_TRIM = 44000        # القص عند التجاوز (نفس سلوك الجسر في الصفحة)

    def _emit_qx(self, obj):
        """بث حدث خادم QML (الدخول / لوحة العملات / دفعات التمرير)."""
        try:
            self.qxEvent.emit(json.dumps(obj, ensure_ascii=False))
        except Exception:
            pass

    @staticmethod
    def _api_from_display(name):
        """اسم العرض الحقيقي → رمز الخادم.
        v13.2: الجدول الثابت للأسماء الحقيقية أولاً (USD/BRL (OTC) → BRLUSD_otc)
        ثم التحويل النظامي القديم كاحتياط أخير فقط."""
        s = str(name or "").strip()
        # v13.2: lookup بالاسم الحقيقي من جدول الخادم نفسه — الأدق والأسرع
        code = QX_NAME_TO_SYMBOL.get(s)
        if code:
            return code
        otc = s.upper().endswith(" OTC")
        base = s[:-4].strip() if otc else s
        base = base.replace("/", "").upper()
        return base + ("_otc" if otc else "")

    @staticmethod
    def _display_from_api(sym):
        """رمز الخادم (BRLUSD_otc) -> اسم العرض (BRL/USD OTC)."""
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
        """شموع الخادم {time,open,...} -> غذاء الصفحة {t,o,h,l,c,v}."""
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
        """نسخة شموع العملة من ذاكرة الخادم (جاهزة دائماً — البث الحي يعمل داخلها)."""
        qx = _qx_module()
        if not qx or not api:
            return []
        try:
            a = qx._get_or_create_asset(api)
            return self._fmt_engine_candles(list(a.candles or []))
        except Exception:
            return []

    def _qx_build_board(self, entries):
        """لوحة العملات الحقيقية من لقطة instruments في الخادم.
        v13.2 (طلب المستخدم): الاسم المعروض هو الاسم الحقيقي من الخادم
        (USD/BRL (OTC)، Axie Infinity (OTC)، CAC 40…) وليس الاسم النظامي
        المولّد، وكل العملة لها علم/شارة من جدول الخادم نفسه."""
        board, symbols = [], {}
        for e in entries or []:
            sym = str((e or {}).get("asset") or "").strip()
            if not sym:
                continue
            disp, flg = qx_asset_display(sym, (e or {}).get("name") or "")
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
                          "flag": flg})
            symbols[disp] = sym
        return board, symbols

    @staticmethod
    def _board_sig(board):
        try:
            return json.dumps([[b["name"], b["payout"], b["open"]] for b in board])
        except Exception:
            return ""

    def _qx_boot_board(self):
        """لوحة الإقلاع: عملة فتح الشارت قبل وصول اللوحة الحقيقية من الخادم —
        v13.2: بالاسم الحقيقي نفسه الذي يعرضه الخادم (بلا وميض عند وصول اللوحة)
        ومع علمها من جدول العملات."""
        if self._qx_board:
            return self._qx_board
        _nm, _fl = qx_asset_display(QX_OPENER_SYMBOL)
        return [{"name": _nm, "symbol": QX_OPENER_SYMBOL, "payout": 0,
                 "open": True, "otc": True, "flag": _fl}]

    def _qx_ensure_asset(self, api):
        """v13.2 (طلب المستخدم): عملة فُتح شارتها تُجلب فوراً — دفعة مباشرة
        (v14.7: 700 شمعة افتراضياً بدل 300، قابلة للتعديل من الإعدادات حتى 1000)
        والعملات التي لم يُفتح شارتها لا تجلب أبداً.
        v13.2 (طلب المستخدم): إذا فتح المستخدم عدة عملات بسرعة يجلب
        **واحدة تلو الأخرى** — طابور متسلسل بفاصل بين عملة وأخرى، بلا تسرّع."""
        qx = _qx_module()
        if not qx or getattr(qx, "CLIENT", None) is None or not self._qx_logged or not api:
            return
        now = time.time()
        # v15.3 (سبب «انضر الى هذا تاخر 1 دقيقة ولم يرسم الشموع»): الخنق القديم
        # كان يحجب الجلب 15 ثانية لأول محاولة وكل فشل يضاعف المهلة حتى 60 ثانية
        # — فكان النقر على العملة صامتاً بلا جلب ولا دائرة تحميل دقيقة كاملة.
        # الآن: النقر يبدأ الجلب فوراً دائماً؛ مسافة 10 ثوانٍ فقط لإعادة
        # المحاولة التلقائية بعد فشل، ومنع التكرار عبر طابور الجلب نفسه.
        fails = self._qx_ensure_fail.get(api, 0)
        if fails and now - self._qx_ensure_at.get(api, 0.0) < 10.0:
            return
        self._qx_ensure_at[api] = now
        with self._qx_load_lock:
            if api in self._qx_load_pending:
                return                      # في الطابور بالفعل — لا تكرار
            self._qx_load_pending.add(api)
            self._qx_loadq.append(api)
        self._log("info", f"chart opened with no candles — loading {api} now (queued)")
        self._qx_start_load_worker()

    def _qx_start_load_worker(self):
        """تشغيل عامل الطابور المتسلسل (خيط واحد فقط يعالج الطلبات واحداً تلو الآخر)."""
        if self._qx_load_busy:
            return
        self._qx_load_busy = True
        threading.Thread(target=self._qx_load_worker, daemon=True,
                         name="qxLoadQueue").start()

    def _qx_load_worker(self):
        """عامل طابور الجلب: يجلب عملاً واحداً في كل مرة مع فاصل ثابت بين
        عملة وأخرى (طلب المستخدم: واحدة تلو الأخرى وليس بسرعة)."""
        qx = _qx_module()
        while True:
            api = None
            with self._qx_load_lock:
                if self._qx_loadq:
                    api = self._qx_loadq.pop(0)
                else:
                    self._qx_load_busy = False
                    return
            if not qx:
                continue
            try:
                fut = asyncio.run_coroutine_threadsafe(
                    qx.ensure_asset_loaded(api), qx.ASYNC_LOOP)
                n = fut.result(timeout=120)
                if n:
                    self._log("ok", f"{api}: {n} candles seeded (history/load) + live stream ON")
                    self._qx_ensure_fail[api] = 0
                    self._qx_last_sig = None   # المضخة تدفع الغذاء الجديد فوراً
                    # v15.3 (طلب المستخدم: «نحن عندما نضغط على العملة هو يبدا
                    # بجلب الشموع تضهر دائرة تحميل لاكتمال التحميل») — الشموع
                    # تُدفع إلى الشارت فور اكتمال الجلب والدائرة تُطفأ فيظهر
                    # الشارت، ثم آلة سد الثغرات الأصلية للعملة المفتوحة فقط في
                    # الخلفية (بلا أي جلب خلفي لعملة لم تُفتح — طلب المستخدم).
                    self._qx_push_feed_now(api)
                    if (api, "1m") not in getattr(self, "_qx_sealed", set()):
                        self._qx_sealed.add((api, "1m"))
                        threading.Thread(target=self._qx_seal_gaps, args=(api,),
                                         daemon=True, name="qxSeal").start()
                else:
                    self._qx_ensure_fail[api] = self._qx_ensure_fail.get(api, 0) + 1
            except Exception as e:
                self._qx_ensure_fail[api] = self._qx_ensure_fail.get(api, 0) + 1
                self._log("err", f"ensure {api}: {str(e)[:100]}")
            finally:
                with self._qx_load_lock:
                    self._qx_load_pending.discard(api)
            # v13.2: فاصل بين عملة وأخرى — الجلب واحداً تلو الآخر بلا تسرّع
            time.sleep(1.0)

    # ---------- v14.3: دفعات التاريخ عند فتح العملة (دفعة مباشرة) ----------
    def _hist_days_cfg(self):
        """عدد أيام شموع التاريخ المضبوط من الإعدادات (0.5 حتى 30، الافتراضي 0.80 — طلب المستخدم).

        v14.8 (سبب موت سلسلة جلب التاريخ من أساسها): كانت الدالة تحمل الاسم
        نفسه `_hist_days` الذي يحمله متغير الإعدادات، فكان المتغير يحجب
        الدالة وكل نداء `self._hist_days()` يفشل بخطأ «float غير قابل
        للاستدعاء» وتسقط سلسلة الجلب صامتة داخل try/except. الدالة الآن
        `_hist_days_cfg` والمتغير يبقى `_hist_days` — لا تعارض بعد الآن."""
        try:
            return max(0.5, min(30.0, float(self._hist_days)))
        except Exception:
            return 2.0

    @Property(str, constant=True)
    def histDaysStr(self):
        return str(self._hist_days)

    # ───── v14.7 (طلب المستخدم حرفياً): عدد شموع الدفعة المباشرة ─────
    @Property(str, constant=True)
    def batchCandlesStr(self):
        return str(self._batch_candles)

    @Slot(str)
    def setBatchCandles(self, v):
        """v14.7 (طلب المستخدم حرفياً): «اريد ان تجلب 700 شمعة بدل 300 شمعة
        كدفعة مباشرة للعملة ويمكن تعديلها في الاعدادات الى 1000 شمعة في
        الدفعة» — يكتب الرقم في بطاقة الإعدادات ويضغط حفظ: الدفعة المباشرة
        عند فتح العملة وكل دفعة تُرفع إلى الشارت تصبح بهذا الحجم
        (100 حتى 1000، الافتراضي 700). يُحفظ ويُطبَّق فوراً على المحرك."""
        try:
            n = int(round(float(str(v or "").replace(",", ".").strip())))
        except Exception:
            self._log("err", "Batch candles: invalid number")
            return
        if not (100 <= n <= 1000):
            self._log("err", "Batch candles: allowed range 100 – 1000")
            return
        self._batch_candles = n
        self._save_cfg()
        qx = _qx_module()
        if qx:
            try:
                qx.PRELOAD_CANDLES = n      # الدفعة المباشرة عند فتح العملة
            except Exception:
                pass
            try:
                qx.PAGINATION_BATCH = n     # حجم كل دفعة تُرفع إلى الشارت
            except Exception:
                pass
        self._log("ok", T[self._lang].get("batchSaved", "Batch candles saved"))
        # v15.3: أعد جلب العملة الحالية بأسلوب الأصل (طلب واحد) بالمدى الجديد
        self._qx_force_reload_current()

    @Property(bool, notify=histChainChanged)
    def histChainActive(self):
        """v14.5 (طلب المستخدم حرفياً: «الشارت لا نريده ان يتاثر اطلاقا يجب ان
        يبقا حر ولا يتاثر ولا نريد فقدان الشموع»): صفحة الويب تعرف من هذه
        الخاصية أن دفعات التاريخ تجري الآن — فلا تعيد ضبط الشارت أبداً أثناءها
        (لا syncFull) — الزوم والموضع يبقيان حرين والشموع لا تُفقد."""
        return bool(self._qx_chain_active)

    @Slot(str)
    def setHistDays(self, v):
        """v14.3 (طلب المستخدم): يكتب الرقم في بطاقة الإعدادات ويضغط حفظ —
        يقبل 0.5 يوم حتى 30 يوم، والافتراضي يومان. فتح العملة بعد الحفظ يجلب
        المدى الجديد بالدفعات المتسلسلة."""
        try:
            d = float(str(v or "").replace(",", ".").strip())
        except Exception:
            self._log("err", "History days: invalid number")
            return
        if not (0.5 <= d <= 30.0):
            self._log("err", "History days: allowed range 0.5 – 30")
            return
        self._hist_days = d
        self._save_cfg()
        qx = _qx_module()
        if qx:
            try:
                qx.QX_HISTORY_DAYS = d
                qx.apply_history_days(d)   # آلية قائمة الأصل نفسها (هامش +15% + INITIAL_CANDLES + FETCH_DURATION)
            except Exception:
                pass
        self._log("ok", T[self._lang].get("histSaved", "History days saved"))
        # v15.3: أعِد جلب العملة الحالية بأسلوب الأصل (طلب واحد) بالمدى الجديد
        self._qx_force_reload_current()

    def _qx_force_reload_current(self):
        """v15.3: إعادة جلب عملة الفتح الحالية من جذورها (بعد تغيير أيام
        التاريخ أو حجم الدفعة في الإعدادات) — نفس مسار فتح العملة حرفياً:
        دائرة التحميل تظهر، طلب واحد seed_history بالمدى الجديد، ثم الدفع
        والإخفاء فيظهر الشارت."""
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if not api:
            return
        qx = _qx_module()
        if qx:
            try:
                a = qx._get_or_create_asset(api)
                a.candles = []
                a.mark_dirty()
            except Exception:
                pass
            try:
                with self._qx_chain_lock:
                    self._qx_chain_done.discard((api, self._tf))
                    if self._tf != "1m":
                        self._qx_chain_done.discard((api, "1m"))
            except Exception:
                pass
            try:
                self._qx_ensure_fail[api] = 0   # تغيير إعدادات = محاولة جديدة فوراً
            except Exception:
                pass
        self._candles = []
        self._qx_feed_key = ("", "")
        self._qx_last_sig = None
        self._qx_loading_arm()
        self._qx_load_feed(force=True)

    def _qx_start_history_chain(self, api, tf_label="1m"):
        """v14.5 (طلب المستخدم حرفياً): «المحرك خليه يجلب شمعة تلك العملة حتا ل
        2 يوم وليس كل مرة يطلب 300 شمعة بل يرفع الى الشارت 300 شمعة كل دفعة اما
        طريقة الجلب يجلب 2 يوم ... اي دفعة جلبها يرفعها الى الشارت».

        تعمل عند فتح العملة وفقط: طلب **واحد** بمدى الأيام كاملاً عبر نفس
        طريقة الجلب الأصلية (CLIENT.get_candles → history/load)، والخادم يرفع
        الرد على دفعات — كل دفعة تُعالج وتُرفع إلى الشارت فوراً (300 شمعة لكل
        دفعة) دون انتظار انتهاء الجلب كله. لا طلب 300 شمعة جديدة بمرساة متحركة
        — كان يعيد نفس الدفعة الأولى. طريقة الرجوع للخلف (التمرير) أُلغيت."""
        qx = _qx_module()
        if not qx or not api or not self._qx_logged:
            return
        tf_sec = dict(TFS).get(tf_label, 60)
        if tf_sec < 60:
            return   # فريمات الثواني تُبنى من التيك الحي (سياسة الخادم) — لا تاريخ مطلب
        key = (api, tf_label)
        with self._qx_chain_lock:
            if key in self._qx_chain_done:
                return
            gen = int(self._qx_chain_gen.get(key, 0)) + 1
            self._qx_chain_gen[key] = gen     # يُجهض أي سلسلة قديمة لنفس المفتاح
            self._qx_chain_running[key] = gen
        threading.Thread(target=self._qx_chain_worker, args=(api, tf_label, gen),
                         daemon=True, name="qxHistChain").start()

    def _qx_chain_set_active(self, active):
        if bool(active) != bool(self._qx_chain_active):
            self._qx_chain_active = bool(active)
            try:
                self.histChainChanged.emit()
            except Exception:
                pass

    def _qx_chain_push_message(self, api, tf_label, tf_sec, raw,
                               horizon, pushed_t, viewing):
        """معالجة دفعة وصلت من الخادم: تنسيق + دمج في ذاكرة المحرك نفسها +
        رفع 300 شمعة لكل دفعة إلى الشارت فوراً (prepend بلا إعادة ضبط).
        تعيد عدد الشموع المرفوعة فعلاً."""
        qx = _qx_module()
        if not qx or not raw:
            return 0
        if tf_sec == 60:
            eng_all = qx._format_raw_candles(raw)               # تنسيق الخادم الرسمي
            app_all = self._fmt_engine_candles(list(eng_all))
        else:
            app_all = self._qx_fmt_raw(raw, tf_sec)
            eng_all = []
        new_c = [c for c in app_all
                 if (horizon <= 0 or c["t"] < horizon) and c["t"] not in pushed_t]
        if not new_c:
            return 0
        new_c.sort(key=lambda x: x["t"])
        cap = int(getattr(qx, "PAGINATION_BATCH", 700))
        n_pushed = 0
        i = 0
        while i < len(new_c):
            chunk = new_c[i:i + cap]
            i += len(chunk)
            for c in chunk:
                pushed_t.add(c["t"])
            # دمج الدفعة في ذاكرة المحرك نفسها (نفس دمج fetch_older_batch الأصلية)
            if tf_sec == 60 and eng_all:
                try:
                    # v14.6: حماية الشمعة الحية — نفس حماية fill_gap_once الأصلية
                    # في الكود المرجعي (t >= current_period_start → لا تُلمس):
                    # دفعة التاريخ لا تعيد الشمعة الحية المتشكلة من البث إلى الخلف
                    # (كان هذا يُظهر الشموع وكأنها تقفز أثناء وصول الدفعات)
                    cur_start = qx._align_time(int(time.time()))
                    t_lo, t_hi = chunk[0]["t"], chunk[-1]["t"]
                    eng_chunk = [c for c in eng_all
                                 if t_lo <= c["time"] <= t_hi and c["time"] < cur_start]
                    asset = qx._get_or_create_asset(api)
                    merged = list(eng_chunk) + list(asset.candles or [])
                    seen, unique = set(), []
                    for c in merged:
                        if c["time"] not in seen:
                            seen.add(c["time"])
                            unique.append(c)
                    unique.sort(key=lambda x: x["time"])
                    unique = unique[-int(getattr(qx, "ASSET_MAX_CANDLES", 45000)):]
                    qx._apply_candles_to_asset(asset, unique)
                except Exception:
                    pass
            n_pushed += len(chunk)
            if not viewing():
                continue   # العملة/الفريم تغيّرا — يُكمل دمج المحرك دون رفع للصفحة
            # مزامنة غذاء بايثون — الصفحة تدمج الدفعة عبر prependCandles
            # (بلا إعادة ضبط ولا قفزة: الزوم والموضع يبقيان كما هما)
            self._candles = chunk + self._candles
            seen_t = set()
            merged_app = []
            for c in self._candles:
                if c["t"] not in seen_t:
                    seen_t.add(c["t"])
                    merged_app.append(c)
            merged_app.sort(key=lambda x: x["t"])
            self._candles = merged_app[-self._QX_FEED_CAP:]
            _tail = self._candles[-3:]
            self._qx_last_sig = ((len(self._candles),) + tuple(
                (c["t"], round(float(c["o"]), 10), round(float(c["h"]), 10),
                 round(float(c["l"]), 10), round(float(c["c"]), 10)) for c in _tail)) if _tail else None
            self._emit_qx({"type": "older", "candles": chunk,
                           "asset": self._asset, "tf": tf_label})
            self.candlesChanged.emit()
            time.sleep(0.12)
        return n_pushed

    @staticmethod
    def _qx_gap_holes(candles, period_seconds):
        """عدد الثغرات الحقيقية في خط الشموع: فترات زمنية بلا أي شمعة (حتى
        الشموع المسطحة المملوءة تُحسب شموعاً). تُستخدم للتحقق أن آلة السد
        فعلت شيئاً فعلاً قبل/بعد كل محاولة."""
        try:
            if not candles or len(candles) < 2 or period_seconds <= 0:
                return 0
            ts = sorted({int(c["time"]) for c in candles})
            holes = 0
            for i in range(1, len(ts)):
                g = (ts[i] - ts[i - 1]) // period_seconds
                if g > 1:
                    holes += int(g) - 1
            return holes
        except Exception:
            return 0

    def _qx_seal_gaps(self, api):
        """سد ثغرات العملة — الآلة الأصلية حرفياً من qx_server_v10.py
        (MT4_WRITER.fill_gap_once كما هي، نفس نداء mt4_gap_filler الأصلي).

        لماذا لم تكن تعمل مع كل العملات؟ علامة التجمّد المحفوظة
        (gap_state.filled=1 في candles.db) كانت تجعل الآلة تعود فوراً بلا سد
        لأي عملة جمّدتها جلسة سابقة — فتبقى مثقوبة. هنا تُرفع العلامة عن هذه
        العملة وحدها **بكل أشكال الرمز الممكنة** (v14.6: الرمز كان مخزّناً
        بصيغة مختلفة عن الصيغتين المطلوبتين فلا تُرفع العلامة ولا يحدث سد —
        سبب «بعضها لا تسد ثغرات»)، ثم تُنفَّذ الخوارزمية الأصلية نفسها كما هي
        (سد أقل من ثانية: جلب آخر 10 شموع حقيقية واستبدال الناقص منها) مع
        إعادة محاولة تحققية حتى 3 مرات حتى تصبح الخط بلا ثغرات فعلية. وبعد
        السد يُعاد الخطر الكامل للذاكرة حتى لا يقص السد التاريخ المجلوب
        (v10 كان يحتفظ بآخر 1000 شمعة فقط — v14 يحتفظ بكل دفعات التاريخ)."""
        qx = _qx_module()
        if not qx or getattr(qx, "CLIENT", None) is None:
            return
        try:
            asset = qx._get_or_create_asset(api)
        except Exception:
            return
        period_seconds = int(getattr(qx, "PERIOD_SECONDS", 60) or 60)

        # كل أشكال الرمز الممكنة (v14.6): صيغ الـ db قد تختلف عن رمز الذاكرة
        variants = set()
        for s in (api, getattr(asset, "symbol", ""), getattr(asset, "api_symbol", "")):
            s = str(s or "").strip()
            if not s:
                continue
            for v in (s, s.upper(), s.lower(),
                      s.replace("_", "-"), s.replace("-", "_"),
                      s.upper().replace("_", "-"), s.upper().replace("-", "_"),
                      s.lower().replace("_", "-"), s.lower().replace("-", "_")):
                variants.add(v)

        def _clear_freeze():
            try:
                qx.clear_gap_flag_any(list(variants))
            except Exception:
                pass
            for sym in {str(getattr(asset, "symbol", "") or api)}:
                try:
                    qx.MT4_WRITER._gap_filled[sym] = False
                except Exception:
                    pass
                try:
                    qx.MT4_WRITER._gap_filled_at.pop(sym, None)
                except Exception:
                    pass

        full_before = list(asset.candles or [])
        holes_before = self._qx_gap_holes(full_before, period_seconds)
        # v14.6: حتى 3 محاولات تحققية — الأصلية نفسها بلا أي تغيير، فقط نتحقق
        # بعد كل محاولة أن الثغرات انخفضت فعلاً (إذا فشل جلب الرد مرة واحدة
        # بسبب ضغط البث لا تبقى العملة مثقوبة للأبد)
        for _attempt in range(3):
            _clear_freeze()
            try:
                fut = asyncio.run_coroutine_threadsafe(
                    qx.MT4_WRITER.fill_gap_once(qx.CLIENT, asset,
                                                int(getattr(qx, "PERIOD", 1))),
                    qx.ASYNC_LOOP)
                fut.result(timeout=30)
            except Exception:
                break
            holes_after = self._qx_gap_holes(list(asset.candles or []), period_seconds)
            if holes_after == 0 or holes_after >= holes_before:
                # سُدّت كل الثغرات، أو المحاولة لم تحسّن شيئاً (لا تكرر بلا فائدة)
                break
            holes_before = holes_after
        # إعادة الخط الكامل: شموع الآلة المُصلحة تحل محل المطابق زمنياً فقط —
        # لا فقدان لأي شمعة من دفعات التاريخ (طلب المستخدم: لا نريد فقدان الشموع)
        # v14.7 (سبب «بعد سد الثغرات ايضا لماذا لم تسد ثغرتها»): الآلة الأصلية
        # تُرجع آخر 1000 شمعة فقط (INITIAL_CANDLES في الكود المرجعي) فتبقى
        # الثغرات الأعمق من نافذة الآلة كما هي. هنا تُعاد شموع الآلة فوق الخط
        # الكامل ثم **نفس** دالة التعبئة الأصلية _fill_missing_slots (حرفياً
        # من الكود المرجعي، نفس سقف max_gap=1440) تُطبَّق على الخط كاملاً —
        # كل ثغرة ≤ يوم كامل تُسدّ بكل الأمداد لا آخر 1000 شمعة فقط.
        try:
            repaired = list(asset.candles or [])
            if full_before and repaired:
                rep_map = {c["time"]: c for c in repaired}
                full_t = {c["time"] for c in full_before}
                restored = [rep_map.get(c["time"], c) for c in full_before]
                restored += [c for c in repaired if c["time"] not in full_t]
                seen, unique = set(), []
                for c in sorted(restored, key=lambda x: x["time"]):
                    if c["time"] not in seen:
                        seen.add(c["time"])
                        unique.append(c)
                unique = qx._fill_missing_slots(list(unique), period_seconds,
                                                max_gap=1440)
                unique = unique[-int(getattr(qx, "ASSET_MAX_CANDLES", 45000)):]
                qx._apply_candles_to_asset(asset, unique)
        except Exception:
            pass
        # v14.9 (لقطة «مهذه المشاكل»): السد العميق في نهاية سلسلة التاريخ —
        # نفس نداء الجلب الرسمي لكن مرساته عند أقدم شمعة اصطناعية، فيستبدل
        # الشرطات المسطحة القديمة بشموع حقيقية قبل مزامنة الشارت (طبقة
        # إضافية بلا أي تغيير في الآلة الأصلية ولا في طريقة الجلب).
        try:
            _ds_fut = asyncio.run_coroutine_threadsafe(
                qx.v14_deep_gap_seal(api, reason="chain"), qx.ASYNC_LOOP)
            _ds_fut.result(timeout=60)
        except Exception:
            pass

    def _qx_chain_worker(self, api, tf_label, gen):
        key = (api, tf_label)
        days = 2.0
        total_pushed = 0
        viewing_ok = False
        try:
            qx = _qx_module()
            if not qx or getattr(qx, "CLIENT", None) is None:
                return
            days = self._hist_days_cfg()
            target = max(60, int(days * 86400))
            tf_sec = dict(TFS).get(tf_label, 60)

            def _viewing():
                """هل الشارت الحالي يعرض نفس العملة والفريم؟ (مطابقة على مستوى رمز الخادم)"""
                try:
                    cur_api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
                    return cur_api == api and self._tf == tf_label
                except Exception:
                    return False

            def _stale():
                """سلسلة أحدث بدأت لنفس المفتاح (تغيير الأيام مثلاً) — هذه تُجهض."""
                try:
                    with self._qx_chain_lock:
                        return self._qx_chain_gen.get(key) != gen
                except Exception:
                    return False
            try:
                qx.QX_HISTORY_DAYS = days
                qx.apply_history_days(days)   # آلية قائمة الأصل نفسها
            except Exception:
                pass
            if _stale():
                return
            viewing_ok = _viewing()
            # حماية الزوم: الصفحة لا تعيد ضبط الشارت أثناء السلسلة (طلب المستخدم:
            # الشارت لا نريده ان يتاثر اطلاقا يجب ان يبقا حر ولا يتاثر)
            if viewing_ok:
                self._qx_chain_set_active(True)
            # أفق التاريخ الجديد: كل ما هو أقدم من أول شمعة على الشارت الآن
            horizon = 0
            try:
                if viewing_ok and self._candles:
                    horizon = int(self._candles[0]["t"])
            except Exception:
                horizon = 0
            pushed_t = set()
            # ═══ v14.6 (طلب المستخدم حرفياً: «انضر الى هذا الكود لا توجد فيه
            #     تلك المشاكل»): طريقة الجلب نفسها من الكود المرجعي حرفياً —
            #     CLIENT.get_historical_candles (5 عمال × مرساة متحركة × دفعة
            #     ~200 شمعة كل 0.1 ثانية) وهي نفسها التي تجلب 1000 شمعة في ثوانٍ
            #     ومئات آلاف الشموع. طلب واحد بمدى الأيام كاملاً ولا طلب 300
            #     شمعة بمرساة ثابتة تعيد نفس الدفعة الأولى. ═══
            import queue as _bq
            batch_q = _bq.Queue()

            def _on_batch(batch, worker_id):
                """مرصد الدفعات (يعمل داخل حلقة الخادم — لا يبطئه أبداً):
                يسلم كل دفعة فور وصولها إلى عاملي السلسلة عبر طابور خفيف."""
                try:
                    if batch:
                        batch_q.put(list(batch))
                except Exception:
                    pass

            fut = asyncio.run_coroutine_threadsafe(
                qx.qx_get_historical_batches(
                    api, amount_of_seconds=target, period=tf_sec,
                    max_workers=5, batch_callback=_on_batch),
                qx.ASYNC_LOOP)
            # ═══ كل دفعة تصل تُعالج وتُرفع إلى الشارت فوراً — لا انتظار انتهاء
            #     الجلب كله (طلب المستخدم: اي دفعة جلبها يرفعها الى الشارت) ═══
            while True:
                if _stale():
                    try:
                        fut.cancel()
                    except Exception:
                        pass
                    return
                try:
                    batch = batch_q.get(timeout=0.2)
                except Exception:
                    if fut.done():
                        break
                    continue
                n = self._qx_chain_push_message(
                    api, tf_label, tf_sec, batch, horizon, pushed_t, _viewing)
                if n > 0:
                    total_pushed += n
            try:
                res = fut.result(timeout=180)
            except Exception:
                res = None
            if _stale():
                return
            # ═══ صافي الأمان: أي دفعة أفلتت من الرفع الحي تُرفع من النتيجة
            #     الكاملة (pushed_t يمنع التكرار — كل شمعة تُرفع مرة واحدة فقط) ═══
            if res:
                n = self._qx_chain_push_message(
                    api, tf_label, tf_sec, res, horizon, pushed_t, _viewing)
                if n > 0:
                    total_pushed += n
            # ═══ الدمج النهائي لذاكرة الخادم (نفس دلالات الكود المرجعي:
            #     _fill_missing_slots يسد فجوات حتى يوم كامل) دون لمس الشمعة الحية ═══
            if tf_sec == 60:
                self._qx_chain_final_merge(qx, api)
            # ═══ سد الثغرات — الآلة الأصلية حرفياً من v10، لكل عملة تُفتح دون استثناء ═══
            if tf_sec == 60:
                self._qx_seal_gaps(api)
            with self._qx_chain_lock:
                self._qx_chain_done.add(key)
            if total_pushed:
                self._log("ok", f"history: +{total_pushed} candles ({days} days) — "
                                f"{self._asset if _viewing() else api} {tf_label}")
            # v14.6: إصلاحات سد الثغرات ودمج الدفعات تصل إلى الشارت في مكانها عبر
            # patchCandles (بلا setData وبلا إعادة ضبط) — الزوم والموضع يبقيان حرين.
            # غذاء الواجهة يُنسّق أولاً من ذاكرة الخادم نفسها حتى تصل إصلاحات
            # السد الداخلية إلى الصفحة وليس إصلاحات الذيل فقط.
            if _viewing():
                if tf_sec == 60:
                    try:
                        eng = self._qx_engine_candles(api)
                        if eng:
                            # v15: استيعاب بلا تقليص — نافذة البث الأصلية (INITIAL_CANDLES)
                            # لا تُقصّ شموع دفعات التاريخ من الشارت أبداً
                            self._qx_absorb_engine_no_shrink(eng)
                            self._qx_last_sig = None   # المضخة تدفع الغذاء المُصلَح فوراً
                    except Exception:
                        pass
                self._qx_resync_pending = True
        except Exception as e:
            self._log("err", f"history chain {tf_label}: " + str(e)[:120])
        finally:
            try:
                with self._qx_chain_lock:
                    # القديمة تُزيل علامتها فقط — لا تلغي سلسلة أحدث لنفس المفتاح
                    if self._qx_chain_running.get(key) == gen:
                        self._qx_chain_running.pop(key, None)
                    cur_api = (self._qx_symbols.get(self._asset)
                               or self._api_from_display(self._asset))
                    still_active = (cur_api, self._tf) in self._qx_chain_running
                self._qx_chain_set_active(still_active)
            except Exception:
                self._qx_chain_set_active(False)

    def _qx_chain_final_merge(self, qx, api):
        """v14.6: دمج نهائي واحد لذاكرة الخادم بعد اكتمال دفعات التاريخ.
        نفس دلالات الكود المرجعي: شموع حقيقية + _fill_missing_slots (سقف يوم
        كامل كما في fill_gap_once الأصلية) — لكن الشمعة الحية المتشكلة من البث
        لا تُلمس أبداً (نفس حماية fill_gap_once الأصلية: t >= current_period_start)."""
        try:
            asset = qx._get_or_create_asset(api)
        except Exception:
            return
        try:
            merged = list(asset.candles or [])
            if not merged:
                return
            seen, unique = set(), []
            for c in sorted(merged, key=lambda x: x["time"]):
                if c["time"] not in seen:
                    seen.add(c["time"])
                    unique.append(c)
            cur_start = qx._align_time(int(time.time()))
            # حماية الشمعة الحية: إن كان البث الحي يشكّل شمعة الآن تبقى نسخته هي
            # المرجع — الدفعات لا تعيدها للخلف (هذا سبب «الشموع تقفز» سابقاً)
            live_map = {c["time"]: c for c in (asset.candles or [])
                        if c["time"] >= cur_start}
            if live_map:
                unique = [live_map.get(c["time"], c) if c["time"] >= cur_start else c
                          for c in unique]
            unique = unique[-int(getattr(qx, "ASSET_MAX_CANDLES", 45000)):]
            qx._apply_candles_to_asset(asset, unique)
        except Exception:
            pass

    def _qx_tail_repaired(self, engine):
        """v14.3: كشف إصلاحات آلة سد الثغرات داخل منطقة الذيل (آخر 40 شمعة).

        الآلة الأصلية (fill_gap_once كما هي من v10) تستبدل الشموع المغلقة
        الناقصة داخل ذاكرة الخادم — الدمج الذيلي فقط لا يوصل هذه الإصلاحات
        إلى الشارت (كانت تبقى الفجوة ظاهرة رغم عمل الآلة). هنا يُكتشف الإصلاح
        فيُحدَّث غذاء الشارت كاملاً مرة واحدة."""
        try:
            if not self._candles or not engine:
                return False
            win = {c["t"]: c for c in self._candles[-40:]}
            for c in engine[-40:]:
                o = win.get(c["t"])
                if o is None:
                    continue
                if (round(o["o"], 10) != round(c["o"], 10)
                        or round(o["h"], 10) != round(c["h"], 10)
                        or round(o["l"], 10) != round(c["l"], 10)
                        or round(o["c"], 10) != round(c["c"], 10)):
                    return True
        except Exception:
            return False
        return False

    def _qx_load_feed(self, force=False):
        """تحميل غذاء الشارت الحقيقي للعملة/الفريم الحاليين من الخادم."""
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
                # v15.3: seed_history الأصلية تجلب مدى الأيام كاملاً بطلب واحد
                # (1000+ شمعة في ~4 ثوانٍ كما في الأصل) — لا سلسلة دفعات بعد
                # الآن: كانت تعيد جلب نفس المدى فوق الجلب الأول فتتأخر الشموع
                # دقيقة كاملة قبل الرسم («تاخر 1 دقيقة ولم يرسم الشموع»)
            elif not candles:
                # v13.1: لا شموع بعد (لم يصل دور التحميل المسبق) — جلب فوري أمامي
                self._qx_ensure_asset(api)
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
            elif not feed:
                # v13.1: لا تيكات بعد (البث لم يبدأ لهذه العملة) — جلب فوري أمامي
                # يشغّل البث الحي نفسه فيتدفق التيك مباشرة
                self._qx_ensure_asset(api)
        else:
            # فريمات أعلى من الدقيقة: جلب مباشر بحجم الدفعة المضبوط (v14.7:
            # 700 افتراضياً بدل 300 — طلب المستخدم) بنفس طريقة الخادم الأصلية.
            # ملاحظة: feed_key يُضبط داخل العامل عند وصول الشموع فعلاً — حتى لا يبدأ
            # مدّ الذيل (_qx_extend_tail) قبل جلب البيانات ويصنع شموعاً مسطحة وهمية.
            if force or not self._candles or self._qx_feed_key != key:
                self._qx_fetch_tf_async(api, tf_sec,
                                        int(getattr(qx, "PAGINATION_BATCH", 700)))

    def _qx_fetch_tf_async(self, api, tf_sec, count):
        """جلب شموع فريم أعلى داخل حلقة الخادم — نفس CLIENT.get_candles الأصلي
        لكن عبر بوابة الجلب الواحدة (v13.1): طلب واحد في كل لحظة + أولوية أمامية
        (طلب المستخدم المعروض يتقدم على التحميل المسبق ولا يختلط معه)."""
        qx = _qx_module()
        if not qx or getattr(qx, "CLIENT", None) is None:
            return
        asset_name, tf_key = self._asset, self._tf

        def _worker():
            try:
                end = int(time.time())
                fut = asyncio.run_coroutine_threadsafe(
                    qx.qx_fetch_window_raw(api, end, count * tf_sec, tf_sec,
                                           foreground=True, timeout=45.0), qx.ASYNC_LOOP)
                res = fut.result(timeout=60)
                candles = self._qx_fmt_raw(res, tf_sec)[-count:]
                if candles and asset_name == self._asset and tf_key == self._tf:
                    self._candles = candles
                    self._qx_feed_key = (asset_name, tf_key)
                    self.candlesChanged.emit()
                    self._log("ok", f"loaded {len(candles)} candles — {asset_name} {tf_key}")
                    # v15.3: طلب واحد بمدى الدفعة كاملاً (count × الفريم) — نفس
                    # طريقة الأصل؛ لا سلسلة دفعات تعيد جلب نفس المدى مرة ثانية
            except Exception as e:
                self._log("err", f"fetch {asset_name} {tf_key}: {str(e)[:120]}")

        threading.Thread(target=_worker, daemon=True, name="qxFetchTf").start()

    @staticmethod
    def _qx_fmt_raw(res, tf_sec):
        """تنسيق رد الخادم لفريم أعلى: محاذاة على حدود الفريم + إزالة التكرار."""
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
        """بناء شموع فريمات الثواني من تيكات الخادم (الذاكرة فقط)."""
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

    def _qx_absorb_engine_no_shrink(self, engine, cap=None):
        """v14.7 — استيعاب شموع المحرك في غذاء الواجهة **بلا تقليص أبداً**.

        الآلة الأصلية fill_gap_once (حرفياً من الكود المرجعي) تعيد ذاكرة
        العملة مقصوصة إلى آخر 1000 شمعة — لو نُسخ المحرك مباشرة فوق الغذاء
        لُفقدت شموع دفعات التاريخ من الشارت («لماذا تختفي شموعها»). هنا:
        شموع المحرك تحل محل المطابق زمنياً (إصلاحات السد تصل)، شموع الغذاء
        الأقدم تبقى كما هي، وشموع المحرك الأحدث تُضاف — لا شمعة تُحذف."""
        if not engine:
            return False
        cap = int(cap or self._QX_FEED_CAP)
        if not self._candles:
            self._candles = list(engine)[-cap:]
            return True
        eng_map = {}
        for c in engine:
            eng_map[c["t"]] = c
        tail_t = self._candles[-1]["t"]
        merged = [eng_map.get(c["t"], c) for c in self._candles]
        merged += [c for c in engine if c["t"] > tail_t]
        seen, unique = set(), []
        for c in sorted(merged, key=lambda x: x["t"]):
            if c["t"] not in seen:
                seen.add(c["t"])
                unique.append(c)
        before = len(self._candles)
        self._candles = unique[-cap:]
        return len(self._candles) != before or any(
            c["t"] in eng_map for c in self._candles[-3:])

    def _qx_merge_tail_full(self, new_feed, tf_sec=None):
        """دمج غذاء الخادم مع غذاء الواجهة من الذيل فقط — رأس البيانات يبقى ثابتاً
        حتى لا يُعاد ضبط الشارت أثناء التمرير للخلف. يعيد True إن تغيّر شيء.

        v13.1 (طلب المستخدم): سد الثغرات داخل غذاء الواجهة نفسه — أي فجوة
        زمنية بين آخر شمعة موجودة وأول شمعة جديدة تُملأ بشموع مسطحة
        (فتح/إغلاق = إغلاق الشمعة السابقة) بسقف أمان كبير (720 فريم) —
        الفارغ في الشموع لن يحدث أبداً."""
        old = self._candles
        if not new_feed:
            return False
        if not old:
            self._candles = new_feed
            return True
        added = [c for c in new_feed if c["t"] > old[-1]["t"]]
        changed = False
        if added:
            # v13.1: سد الثغرات الزمنية بين الذيل القديم والجديد (شموع مسطحة)
            if tf_sec and tf_sec > 0:
                filled = []
                last_t = old[-1]["t"]
                last_c = old[-1]["c"]
                for c in added:
                    gap = int((c["t"] - last_t) // tf_sec) if c["t"] > last_t else 0
                    if gap > 1 and gap <= 720:
                        slot = last_t + tf_sec
                        while slot < c["t"]:
                            filled.append({"t": slot, "o": last_c, "h": last_c,
                                           "l": last_c, "c": last_c, "v": 0})
                            slot += tf_sec
                    filled.append(c)
                    last_t = c["t"]
                    last_c = c["c"]
                added = filled
            self._candles = old + added
            changed = True
        # تحديث الشموع المطابقة زمنياً (آخر 3 شموع): إغلاق الشمعة السابقة النهائي
        # + السعر الحي للشمعة الأخيرة — دون لمس رأس البيانات إطلاقاً
        upd = {c["t"]: c for c in new_feed}
        for i in range(max(0, len(self._candles) - 3), len(self._candles)):
            c = self._candles[i]
            nc = upd.get(c["t"])
            if nc is None:
                continue
            if (abs(nc["c"] - c["c"]) > 1e-12 or abs(nc["h"] - c["h"]) > 1e-12
                    or abs(nc["l"] - c["l"]) > 1e-12 or abs(nc["o"] - c["o"]) > 1e-12):
                self._candles[i] = nc
                changed = True
        if len(self._candles) > self._QX_FEED_CAP:
            self._candles = self._candles[-self._QX_FEED_TRIM:]
        return changed

    def _qx_extend_tail(self, px, tf_sec):
        """مدّ الذيل الحي للفريمات غير الدقيقة من السعر الحي للخادم."""
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
            # v13.1 (طلب المستخدم): سد الثغرات في مدّ الذيل — إذا قفز الزمن أكثر
            # من فريم واحد (سبت النظام مثلاً) تُملأ الفواصل الزمنية الوسيطة
            # بشموع مسطحة (إغلاق الشمعة السابقة) — لا فراغات في الفريمات العليا
            _gap = int((bucket - last["t"]) // tf_sec) if tf_sec > 0 else 1
            if 1 < _gap <= 720:
                _slot = last["t"] + tf_sec
                while _slot < bucket:
                    self._candles.append({"t": _slot, "o": last["c"], "h": last["c"],
                                          "l": last["c"], "c": last["c"], "v": 0})
                    _slot += tf_sec
            self._candles.append({"t": bucket, "o": last["c"],
                                  "h": max(last["c"], px), "l": min(last["c"], px),
                                  "c": px, "v": 0})
            if len(self._candles) > self._QX_FEED_CAP:
                self._candles = self._candles[-self._QX_FEED_TRIM:]
            return True
        return False

    def _qx_poll(self):
        """مضخة الخادم: لوحة العملات + التغذية الحية + حالة التحميل المسبق."""
        if not self._qx_logged:
            return
        qx = _qx_module()
        if qx is None or getattr(qx, "CLIENT", None) is None:
            return
        # ═══ v15 (طلب المستخدم حرفياً): التحديث عند وصول كل تيك ═══
        # realtime_stream الأصلية تحدّث last_update_time عند كل تيك يصل —
        # لا تيك جديد → خروج فوري بلا أي عمل. اللوحة والحالة كل ثانيتين.
        try:
            _api_now = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        except Exception:
            _api_now = None
        _stamp = None
        try:
            _a = qx._get_or_create_asset(_api_now) if _api_now else None
            if _a is not None:
                _stamp = (float(getattr(_a, "last_update_time", 0) or 0),
                          float(getattr(_a, "price", 0) or 0),
                          len(getattr(_a, "candles", []) or []))
        except Exception:
            _stamp = None
        _now = time.time()
        _tick_new = (_stamp is not None and _stamp != getattr(self, "_qx_tick_stamp", None))
        if _tick_new:
            self._qx_tick_stamp = _stamp
        _board_due = (_now - getattr(self, "_qx_board_at", 0.0)) >= 2.0
        # v15.2: أثناء جلب شموع العملة المفتوحة (دائرة التحميل) المضخة تعمل
        # دائماً حتى تختفي الدائرة فور وصول الشموع — بلا أي نبضات إضافية
        # في غير ذلك (التحميل المسبق الخلفي أُلغي — طلب المستخدم).
        _load_due = bool(getattr(self, "_qx_loading", False))
        if (not _tick_new and not _board_due and not _load_due
                and not getattr(self, "_qx_resync_pending", False)):
            return
        if _board_due:
            self._qx_board_at = _now
        # 1) لوحة العملات الحقيقية (الاسم + الدفع + مفتوح/مغلق) — تُدفع عند أي تغيير
        try:
            entries = qx._instruments_snapshot()
            if entries:
                board, symbols = self._qx_build_board(entries)
                if board and (symbols != self._qx_symbols
                              or self._board_sig(board) != self._board_sig(self._qx_board)):
                    old_symbols = self._qx_symbols
                    self._qx_board = board
                    self._qx_symbols = symbols
                    real = set(symbols.keys())
                    # v13.2: الأسماء الحقيقية — إذا كان الاسم المعروض الحالي/المضاف
                    # قديماً (قبل وصول اللوحة) انقله إلى الاسم الحقيقي لنفس الرمز
                    rev = {sy: nm for nm, sy in symbols.items()}
                    if self._asset not in real:
                        _cur_sym = old_symbols.get(self._asset) or QX_OPENER_SYMBOL
                        self._asset = rev.get(_cur_sym, self._asset)
                    old_to_new = {old_nm: rev.get(old_sy, old_nm)
                                  for old_nm, old_sy in old_symbols.items()}
                    self._added = [old_to_new.get(n, n) for n in self._added]
                    self._added = [n for n in self._added if n in real]
                    if not self._added:
                        opener = None
                        for b in board:
                            if b["symbol"] == qx.PRELOAD_FIRST_SYMBOL:
                                opener = b["name"]
                                break
                        if not opener:
                            opener, _fl_unused = qx_asset_display(qx.PRELOAD_FIRST_SYMBOL)
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
        # 4) v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة — تُطفأ
        #    فور وصول شموع العملة الحالية (الشارت يظهر بعد انتهاء الجلب)، مع
        #    مهلة أمان 60 ثانية حتى لا تبقى الدائرة عالقة أبداً.
        try:
            if getattr(self, "_qx_loading", False):
                _ready = (self._qx_feed_key == (self._asset, self._tf)
                          and bool(self._candles))
                if _ready or (_now - getattr(self, "_qx_loading_at", 0.0)) > 60.0:
                    if not _ready:
                        self._log("info", "candles loading timeout — spinner hidden")
                    self._qx_loading_clear()
        except Exception:
            pass

    def _qx_push_feed_now(self, api):
        """v15.3 (طلب المستخدم: «حتا ينتهي يضهر الشارت»): بعد اكتمال جلب شموع
        العملة تُدفع إلى الشارت فوراً وتُطفأ دائرة التحميل فيظهر الشارت —
        بلا انتظار نبضة المضخة. إذا كان المستخدم قد فتح عملة أخرى أثناء
        الجلب تبقى الدائرة لعملتها الجديدة (لا دائرة ولا دفع لعملة خلفية)."""
        try:
            cur_api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
            if cur_api != api:
                return
            candles = self._qx_engine_candles(api)
            if candles:
                self._candles = candles[-self._QX_FEED_CAP:]
                self._qx_feed_key = (self._asset, self._tf)
                if self._py_mods:
                    self._compute_py()
                self.candlesChanged.emit()
            self._qx_loading_clear()
        except Exception:
            pass

    def _qx_loading_arm(self):
        """v15.2 (طلب المستخدم): بدء دائرة تحميل الشموع — تظهر في اللحظة التي
        يبدأ فيها جلب شموع العملة المفتوحة وتُطفأ عند وصولها."""
        self._qx_loading = True
        self._qx_loading_at = time.time()
        self._emit_qx({"type": "chartload", "active": True, "asset": self._asset})

    def _qx_loading_clear(self):
        """v15.2: انتهاء جلب شموع العملة الحالية — إخفاء الدائرة فيظهر الشارت."""
        if not getattr(self, "_qx_loading", False):
            return
        self._qx_loading = False
        self._emit_qx({"type": "chartload", "active": False, "asset": self._asset})

    def _qx_live_step(self):
        """خطوة التغذية الحية: تحديث شموع العملة الحالية من الخادم ثم الدفع للشارت."""
        api = self._qx_symbols.get(self._asset) or self._api_from_display(self._asset)
        if not api:
            return
        qx = _qx_module()
        tf_sec = self._tf_sec()
        key = (self._asset, self._tf)
        if tf_sec == 60:
            candles = self._qx_engine_candles(api)
            if candles:
                # v14.9 (لقطة «مهذه المشاكل»): السد العميق استبدل شرطات قديمة
                # بشموع حقيقية في ذاكرة المحرك — تحديث كامل واحد للغذاء يُظهرها
                # فوراً (نفس مسار مزامنة السلسلة: بلا setData وبلا إعادة ضبط —
                # الزوم والموضع يبقيان حرين)
                try:
                    _ds_t = int((getattr(qx, "V14_DEEP_REPAIRED", {}) or {}).get(api, 0) or 0)
                    if _ds_t > int(getattr(self, "_qx_deep_seen", 0) or 0):
                        self._qx_deep_seen = _ds_t
                        self._qx_absorb_engine_no_shrink(candles)
                        self._qx_last_sig = None
                        self._qx_resync_pending = True
                except Exception:
                    pass
                if not self._candles or self._qx_feed_key != key:
                    self._candles = candles[-self._QX_FEED_CAP:]
                    self._qx_feed_key = key
                elif self._qx_tail_repaired(candles):
                    # v14.3: آلة سد الثغرات أصلحت شموعاً مغلقة في ذاكرة الخادم —
                    # الدمج الذيلي لا يوصل إصلاحات المنصف، تحديث كامل واحد يُظهرها
                    # (هنا تُغلق فجوة «بين شمعة الحية والشموع التي قبلها»)
                    # v14.7: الاستيعاب بلا تقليص — المحرك قد يعود مقصوصاً إلى
                    # آخر 1000 شمعة من الآلة الأصلية، والنسخ المباشر كان يُفقد
                    # شموع دفعات التاريخ من الشارت («لماذا تختفي شموعها»)
                    self._qx_absorb_engine_no_shrink(candles)
                    self._qx_resync_pending = True
                else:
                    self._qx_merge_tail_full(candles, tf_sec)
            elif self._qx_feed_key != key:
                # بيانات العملة لم تُحمّل بعد (التحميل المسبق يتدرج عملة تلو
                # أخرى) — الشارت يبقى فارغاً بدل إظهار شموع العملة السابقة
                self._candles = []
                self._qx_feed_key = key
            else:
                # v13.1: لا شموع في الخادم لهذه العملة — جلب فوري أمامي
                self._qx_ensure_asset(api)
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
                    self._qx_merge_tail_full(feed, tf_sec)
            elif self._qx_feed_key != key:
                self._candles = []
                self._qx_feed_key = key
            else:
                # v13.1: لا تيكات — جلب فوري أمامي يشغّل البث الحي أيضاً
                self._qx_ensure_asset(api)
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
            # مدّ الذيل الحي فقط بعد وصول الشموع المجلوبة فعلاً (feed_key == key) —
            # قبلها لا شموع مسطحة وهمية؛ وإذا فشل الجلب يعاد المحاولة كل 10 ثوانٍ
            if self._qx_feed_key == key:
                self._qx_extend_tail(px, tf_sec)
            elif not self._candles:
                now = time.time()
                if now - self._qx_tf_retry >= 10.0:
                    self._qx_tf_retry = now
                    self._qx_load_feed(force=True)
        # دفع التغيير للشارت فقط عند تغير آخر 3 شموع فعلاً (أداء) — الشمعة
        # الحية + الإغلاق النهائي لشمعتين مغلقتين (بدل بقائهما خاطئتين ثم
        # "قفزة" عند أول مزامنة كاملة — طلب المستخدم: إصلاح الشموع التي تقفز)
        if self._candles:
            tail = self._candles[-3:]
            sig = (len(self._candles),) + tuple(
                (c["t"], round(float(c["o"]), 10), round(float(c["h"]), 10),
                 round(float(c["l"]), 10), round(float(c["c"]), 10)) for c in tail)
            if sig != self._qx_last_sig:
                self._qx_last_sig = sig
                if self._py_mods:
                    self._compute_py()
                self.candlesChanged.emit()
        # v14.3: إصلاح سد الثغرات وصل — مزامنة كاملة واحدة تُظهر الشموع المُصلَحة
        if getattr(self, "_qx_resync_pending", False):
            self._qx_resync_pending = False
            self._emit_qx({"type": "resync"})

    # ---------- الدخول الحقيقي عبر خادم Quotex (بديل تسجيل الدخول الوهمي) ----------
    @Property(str, notify=savedEmailChanged)
    def savedEmail(self):
        """البريد المحفوظ («تذكّرني») — يظهر معبأ في واجهة تسجيل الدخول عند
        الإقلاع التالي. v15.2: الكتابة في app_data.db كانت تفشل صامتة في الأصل
        (عدد روابط خاطئ في _save_state — أُصلح في طبقة الربط داخل المحرك)."""
        qx = _qx_module()
        try:
            return str(qx.session_manager.get_saved_email() or "")
        except Exception:
            return ""

    @Slot(str, str, bool)
    def qxLogin(self, email, password, remember):
        """تشغيل محرك الخادم وتسجيل الدخول الحقيقي — يعمل في خيط منفصل حتى لا
        تتجمد الواجهة، ويبلّغ كل خطوة عبر qxEvent."""
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
            # v15.2 (طلب المستخدم): «لا نريده ان يحمل العملات في الخلفية
            # نريده ان يقوم بتحميل بطريقة عندما نفتح العملة من قائمة العملات» —
            # التحميل المسبق المتسلسل لكل العملات أُلغي تماماً. الشموع تُجلب
            # فقط عند فتح العملة: switch → _qx_load_feed → ensure_asset_loaded
            # وfetch_tf_async وسلسلة تاريخ العملة المفتوحة — نفس آلة الجلب
            # الفوري القائمة دون أي تحميل خلفي لأي عملة لم تُفتح.
            # v13.1 (طلب المستخدم): آلية سد الثغرات تعمل الآن مع التطبيق أيضاً —
            # نفس mt4_gap_filler الخادم بلا أي تغيير (كانت معرّفة بلا تشغيل)
            asyncio.run_coroutine_threadsafe(qx.mt4_gap_filler(), loop)
            # تيكات في الذاكرة فقط + حذف الأقدم من 5 دقائق (حماية القرص)
            asyncio.run_coroutine_threadsafe(qx.tick_cache_collector(), loop)
            asyncio.run_coroutine_threadsafe(qx.tick_retention_loop(), loop)
            asyncio.run_coroutine_threadsafe(qx.candlestore_trim_loop(), loop)
            # v14.0: طبقة تقوية الخادم — كل الحلقات الجديدة تحت المشرف
            # (دون انهيار الخوادم). الحلقات الأصلية أعلاه كما هي حرفياً،
            # وv14 يضيف فوقها فقط: بوابة تفرز الطلبات + سد الثغرات على كل
            # عملة مفتوحة + التكس لا ينام + تقوي النقاط + النبضة.
            if hasattr(qx, "v14_build_background_loops"):
                try:
                    for _v14_name, _v14_factory in qx.v14_build_background_loops():
                        asyncio.run_coroutine_threadsafe(
                            qx.v14_supervise(_v14_name, _v14_factory), loop)
                    if hasattr(qx, "v14_print_banner"):
                        qx.v14_print_banner()
                except Exception as _v14e:
                    try:
                        print("[QX] v14 strengthening layer issue "
                              "(server continues unchanged): " + str(_v14e))
                    except Exception:
                        pass
            self._qx_logged = True
            # v15.2 (طلب المستخدم): «ميزة حفض الايميل» — مع «تذكّرني» يبقى
            # البريد محفوظاً فيظهر معبأ في واجهة تسجيل الدخول عند الإقلاع
            # التالي؛ بلا تحديد لا يُحفظ شيء.
            try:
                _sm = qx.session_manager
                if not bool(remember):
                    _sm.state["email"] = ""
                    _sm.state["password"] = ""
                    _sm._save_state()
                self.savedEmailChanged.emit()
            except Exception:
                pass
            # v15.3: إعدادات الأيام وحجم الدفعة تُطبَّق على المحرك **قبل**
            # بدء الجلب — طلب seed_history الواحد يقرأ الأيام لحظة التنفيذ
            try:
                qx.QX_HISTORY_DAYS = self._hist_days_cfg()
                qx.apply_history_days(self._hist_days_cfg())   # آلية قائمة الأصل نفسها
            except Exception:
                pass
            try:
                qx.PRELOAD_CANDLES = int(self._batch_candles)
                qx.PAGINATION_BATCH = int(self._batch_candles)
            except Exception:
                pass
            # v15.2 (طلب المستخدم): دائرة تحميل الشموع لعملة فتح الشارت —
            # تظهر عند بداية الجلب وتختفي عند وصول الشموع فيظهر الشارت
            self._qx_loading_arm()
            self._qx_load_feed(force=True)
            if self._qx_feed_key == (self._asset, self._tf) and self._candles:
                self._qx_loading_clear()
            # v15.3: تصفير علامات تجمّد السد القديمة — آلة الأصل fill_gap_once
            # تعمل بعد اكتمال الجلب عبر السد الخلفي لعملة فُتحت فقط
            try:
                qx.reset_gap_flags()
            except Exception:
                pass
            # v15.3: لا سلسلة دفعات عند الدخول — _qx_load_feed أعلاه يجلب شموع
            # عملة الفتح بطلب واحد عبر seed_history الأصلية (مدى الأيام كاملاً
            # في ~4 ثوانٍ) ثم يرفعها إلى الشارت فوراً ويُطفئ دائرة التحميل
            self._log("ok", "QX server connected — " + host + " | opener: " + str(qx.PRELOAD_FIRST_SYMBOL))
            self._emit_qx({"type": "login", "state": "ok"})
        except Exception as e:
            self._emit_qx({"type": "login", "state": "err", "msg": str(e)[:160]})
        finally:
            self._qx_login_busy = False

    # ---------- دفعة التمرير للخلف (300 شمعة) ----------
    @Slot(str)
    def fetchOlder(self, arg):
        """طلب دفعة شموع أقدم من الخادم عند التمرير إلى بداية الشارت.

        v14.2: عندما يكون الطلب السابق لا يزال جارياً (_qx_older_busy) لا
        نرد برسالة فارغة — الرد الفارغ كان يصل إلى prependCandles فيضع
        OLDER.exhausted = المرساة الحالية، فيُحجب كل طلب لاحق لنفس النقطة
        («الرجوع للخلف لا يجلب شموعاً» بعد أول سحبين سريعين). الطلب الجاري
        سيصل بنتيجته ويُدمج، والعتبة الزمنية في __badiMaybeLoadOlder (8s)
        تمنع التكرار المفرط أثناءه."""
        if not self._qx_logged or self._qx_older_busy:
            return
        self._qx_older_busy = True
        threading.Thread(target=self._qx_older_worker, args=(str(arg or "{}"),),
                         daemon=True, name="qxOlder").start()

    def _qx_older_worker(self, arg):
        batch = []
        b_asset, b_tf = "", ""
        transient_error = False   # v14.2: خطأ عابر ≠ نهاية التاريخ
        try:
            try:
                req = json.loads(arg or "{}")
            except Exception:
                req = {}
            before = int(req.get("before") or 0)
            asset = str(req.get("asset") or self._asset)
            tf = str(req.get("tf") or self._tf)
            b_asset, b_tf = asset, tf
            qx = _qx_module()
            api = self._qx_symbols.get(asset) or self._api_from_display(asset)
            tf_sec = dict(TFS).get(tf, 60)
            if qx and api and before > 0 and getattr(qx, "CLIENT", None) is not None and tf_sec >= 60:
                if tf_sec == 60:
                    # دفعة الخادم الرسمية: fetch_older_batch تجلب 300 شمعة أقدم وتدمجها
                    # (v13.2: 300 وليس 170 — طلب المستخدم؛ وأولوية أمامية عبر بوابة الجلب)
                    fut = asyncio.run_coroutine_threadsafe(
                        qx.fetch_older_batch(api, before, qx.PAGINATION_BATCH), qx.ASYNC_LOOP)
                    fut.result(timeout=120)
                    batch = [c for c in self._qx_engine_candles(api) if c["t"] < before][-qx.PAGINATION_BATCH:]
                else:
                    # v13.2: نفس CLIENT.get_candles الأصلي لكن عبر البوابة الأمامية —
                    # دفعة 300 شمعة وليس 170 (طلب المستخدم)
                    _nb = int(getattr(qx, "PAGINATION_BATCH", 300))
                    fut = asyncio.run_coroutine_threadsafe(
                        qx.qx_fetch_window_raw(api, before, _nb * tf_sec, tf_sec,
                                               foreground=True, timeout=45.0), qx.ASYNC_LOOP)
                    res = fut.result(timeout=60)
                    batch = [c for c in self._qx_fmt_raw(res, tf_sec) if c["t"] < before][-_nb:]
                # مزامنة غذاء بايثون فوراً حتى لا يعيد المضخة إرسال إعادة ضبط للشارت
                if tf == self._tf and asset == self._asset and batch:
                    if tf_sec == 60:
                        self._qx_absorb_engine_no_shrink(self._qx_engine_candles(api))
                    else:
                        self._candles = batch + self._candles
                        if len(self._candles) > self._QX_FEED_CAP:
                            self._candles = self._candles[-self._QX_FEED_TRIM:]
                    # v13.1 (طلب المستخدم: بلا قفزات): لا إعادة ضبط بعد الدفعة —
                    # تحديث بصمة الذيل (آخر 3 شموع) فقط؛ الدفعة تُدمج في الصفحة
                    # بلا أي قفزة والمضخة تُبقي الشمعة الحية عبر pushTail العادي
                    _tail = self._candles[-3:]
                    self._qx_last_sig = ((len(self._candles),) + tuple(
                        (c["t"], round(float(c["o"]), 10), round(float(c["h"]), 10),
                         round(float(c["l"]), 10), round(float(c["c"]), 10)) for c in _tail)) if _tail else None
                if batch:
                    self._log("info", f"older batch: +{len(batch)} candles — {asset} {tf}")
                else:
                    self._log("info", f"older batch: no more history — {asset} {tf}")
            elif tf_sec < 60:
                self._log("info", "sub-second history builds from live ticks (5-min server window)")
        except Exception as e:
            transient_error = True
            self._log("err", "older batch: " + str(e)[:120])
        finally:
            self._qx_older_busy = False
        # v14.2: عند خطأ عابر (انقطاع، مهلة…) لا نرسل رداً فارغاً — الرد
        # الفارغ كان يضع OLDER.exhausted في الصفحة فيُحجب إعادة الطلب لنفس
        # المرساة للأبد. الذاكرة في الصفحة تُفرغ تلقائياً بعد 8 ثوانٍ فلا
        # يمنع المستخدم من المحاولة مجدداً. أما الرد الفارغ الحقيقي
        # (لا شموع أقدم أصلاً) فيصل كما هو — نهاية التاريخ فلا تكرار.
        if transient_error:
            return
        # v14.1: الدفعة موسومة بالعملة والفريم — الصفحة ترفض أي دفعة لا تطابق
        # الشارت الحالي (حماية من اختلاط الدفعات عند تبديل العملة أثناء الجلب)
        self._emit_qx({"type": "older", "candles": batch, "asset": b_asset, "tf": b_tf})

    # ---------- مؤشرات بايثون ----------
    _SAFE_BUILTINS = {"abs": abs, "min": min, "max": max, "len": len, "range": range,
                      "float": float, "int": int, "round": round, "sum": sum, "enumerate": enumerate,
                      "zip": zip, "list": list, "dict": dict, "sorted": sorted, "pow": pow,
                      "True": True, "False": False, "None": None}

    def _compile_py(self, f):
        mod = {}
        try:
            gl = dict(self._SAFE_BUILTINS)
            gl.update(PY_HELPERS)
            exec(f["code"], gl)          # noqa: S102 — بيئة محلية مقيّدة
            for req in ("LABEL", "TYPE", "SETTINGS", "calculate"):
                if req not in gl:
                    raise ValueError(f"missing {req}")
            mod = {k: gl[k] for k in ("LABEL", "TYPE", "SETTINGS", "calculate")
                   if k in gl}
            mod["signal"] = gl.get("signal")
            mod["get_range"] = gl.get("get_range")
            self._py_err[f["id"]] = 0
            return mod, None
        except Exception as e:
            return None, str(e)

    def _enabled_files(self, kind):
        return [f for f in self._files if f.get("enabled") and f.get("kind") == kind]

    def _compute_py(self):
        for mid, mod in list(self._py_mods.items()):
            try:
                res = mod["calculate"](self._candles, dict(mod["SETTINGS"]))
                if isinstance(res, (list, tuple)):
                    res = {"Value": list(res)}
                series = {}
                rng = None
                for k, arr in res.items():
                    series[k] = [None if (x is None or x != x) else round(float(x), 8) for x in arr]
                if mod.get("get_range") and str(mod.get("TYPE")) == "pane":
                    r = mod["get_range"](series)
                    rng = [float(r[0]), float(r[1])]
                self.pyValues.emit(mid, json.dumps(series), json.dumps(rng))
                if mod.get("signal"):
                    sig = mod["signal"](self._candles, {k: v for k, v in series.items()})
                    self._maybe_fire(mid, self._py_names.get(mid, str(mod.get("LABEL", mid))), sig)
            except Exception as e:
                n = self._py_err.get(mid, 0) + 1
                self._py_err[mid] = n
                name = self._py_names.get(mid, mid)
                if n <= 2:
                    self._log("err", f"{name}: {e}")
                elif n == 3:
                    self._log("info", f"{name}: errors hidden (persistent)")

    @Slot(str, str, str, result=str)
    def compilePyOne(self, fid, file_name, code):
        """ترجمة مؤشر بايثون واحد قادم من صفحة الويب المدمجة."""
        f = {"id": fid, "fileName": file_name, "kind": "py", "code": code, "enabled": True}
        mod, err = self._compile_py(f)
        if err:
            self._py_mods.pop(fid, None)
            return json.dumps({"ok": False, "error": str(err)})
        self._py_mods[fid] = mod
        self._py_names[fid] = file_name
        self._py_err[fid] = 0
        self._log("ok", f"{file_name} (Python) {T[self._lang]['compileok']}")
        return json.dumps({"ok": True, "label": str(mod["LABEL"]), "type": str(mod["TYPE"]),
                           "settings": mod["SETTINGS"]})

    @Slot(str, result=str)
    def libFile(self, key):
        """كود مؤشر جاهز كملف جديد يحمل اسم المكتبة — تُنشئه صفحة الويب المدمجة."""
        item = next((l for l in LIB if l["key"] == key), None)
        if not item:
            return "{}"
        sfx = random_suffix(6)
        return json.dumps({"id": "ind_" + sfx.lower(), "fileName": f"{item['name']}.js",
                           "kind": "indicator", "code": item["code"], "enabled": False})

    def boot_files_json(self):
        """ملفات المستخدم بصيغة صفحة الويب (تُحقن في HTML عند الإقلاع).
        ملفات .badi المشفرة تُدرج بجوار ملفاتها الأصلية — فك التشفير عند النقر فقط."""
        src = self._files
        if isinstance(src, dict) and isinstance(src.get("files"), list):
            src = src["files"]
        out = []
        for f in src:
            if not isinstance(f, dict):
                continue
            k = self._norm_kind(f.get("kind"))
            out.append({"id": f.get("id", ""), "fileName": f.get("fileName", ""),
                        "kind": k, "code": f.get("code", ""), "enabled": bool(f.get("enabled"))})
        return json.dumps({"files": out, "pyTemplate": PY_IND_TEMPLATE,
                           "badiDir": BADI_DIR,
                           "market": {"assets": [b["name"] for b in self._qx_boot_board()],
                                      "board": self._qx_boot_board(),
                                      "added": self._added,
                                      "tfs": [k for k, _ in TFS],
                                      "asset": self._asset, "tf": self._tf, "live": self._live,
                                      "dec": self._price_decimals()}})

    @Slot(str, result=str)
    def compilePy(self, files_json):
        """ترجمة كل ملفات بايثون المفعّلة — يستدعى بعد ▶ تشغيل ملف py."""
        try:
            data = json.loads(files_json)
        except Exception:
            data = []
        if isinstance(data, dict) and isinstance(data.get("files"), list):
            data = data["files"]
        norm = []
        for f in data if isinstance(data, list) else []:
            if isinstance(f, dict) and isinstance(f.get("id"), str):
                f = dict(f)
                f["kind"] = self._norm_kind(f.get("kind"))
                f["fileName"] = _safe_file_name(f.get("fileName"))
                norm.append(f)
        self._files = norm
        _write_json(FILES_FILE, self._files)
        out = {}
        for f in self._enabled_files("py"):
            mod, err = self._compile_py(f)
            if err:
                out[f["id"]] = {"ok": False, "error": err}
                self._log("err", f"{f['fileName']}: {err}")
            else:
                self._py_mods[f["id"]] = mod
                out[f["id"]] = {"ok": True, "label": str(mod["LABEL"]), "type": str(mod["TYPE"]),
                                "settings": mod["SETTINGS"]}
                self._log("ok", f"{f['fileName']} (Python) {T[self._lang]['compileok']}")
                self._compute_py()
        # إزالة وحدات الملفات الموقوفة
        for f in self._files:
            if not f.get("enabled") and f["id"] in self._py_mods:
                del self._py_mods[f["id"]]
        return json.dumps(out)

    # ---------- الإشارات ----------
    @Slot(str, str, str, float, str, str)
    def fireSignal(self, fid, label, dir_, price, asset="", chats=""):
        # asset: عملة الإشارة (من الماسح متعدد العملات أو الشارت) — chats: معرف المحادثة من المؤشر نفسه
        if not price and self._candles:
            price = self._candles[-1]["c"]
        self._maybe_fire(fid, label, {"dir": dir_, "price": float(price),
                                      "asset": str(asset or ""), "chats": str(chats or "")})

    def _maybe_fire(self, fid, label, sig):
        if not sig or not sig.get("dir"):
            return
        asset = str(sig.get("asset") or self._asset or "")
        cfg = self._asset_cfg(asset)
        on_chart = (asset == self._asset and bool(self._candles))
        # عملة الشارت: وقت الشمعة الحالية — العملات الأخرى: آخر شمعة مكتملة بالفريم الحالي
        now_bar = self._candles[-1]["t"] if on_chart else \
            (int(datetime.now().timestamp()) - int(datetime.now().timestamp()) % max(5, self._tf_sec()))
        key = fid + ":" + asset + ":" + self._tf
        last = self._fire_state.get(key)
        if last and last[0] == now_bar and last[1] == sig["dir"]:
            return
        self._fire_state[key] = (now_bar, sig["dir"])
        price = float(sig.get("price") or 0)
        if on_chart and not price:
            price = self._candles[-1]["c"]
        price_s = round(price, cfg["dec"])
        when = datetime.fromtimestamp(now_bar).strftime("%Y-%m-%d %H:%M:%S")
        chats = str(sig.get("chats") or "")
        self._send_signal(fid, label, sig["dir"], price_s, when, asset=asset, chats=chats)
        # النتيجة (WIN/LOSS) تُحسب بعد انتهاء مدة الفريم — تُرسل للبطاقة وللبوت بنفس الستايل
        expiry = (datetime.fromtimestamp(now_bar) + timedelta(seconds=self._tf_sec())).timestamp()
        self._sigpend.append({"asset": asset, "tf": self._tf, "dir": sig["dir"],
                              "entry": float(price), "expiry": expiry, "label": label,
                              "vol": cfg["vol"], "dec": cfg["dec"], "chats": chats})

    _fire_state = {}

    def _check_sig_results(self):
        """تسوية الإشارات المعلّقة: مقارنة السعر عند انتهاء المدة بسعر الدخول."""
        if not self._sigpend:
            return
        now = datetime.now().timestamp()
        still = []
        for sp in self._sigpend:
            if now < sp["expiry"]:
                still.append(sp)
                continue
            if self._candles and sp["asset"] == self._asset and self._live:
                exit_px = self._candles[-1]["c"]
            else:
                # محاكاة حتمية بحجم تقلب الأصل (بيانات تجريبية — تعمل حتى بدون لايف)
                f = ((_hash(sp["asset"] + sp["tf"] + str(int(sp["expiry"]))) % 2000) - 1000) / 1000.0
                exit_px = sp["entry"] * (1 + sp["vol"] * f * 3.0)
            exit_px = round(float(exit_px), sp["dec"])
            win = (sp["dir"] == "up" and exit_px > sp["entry"]) or (sp["dir"] == "down" and exit_px < sp["entry"])
            res = "win" if win else "loss"
            self.sigResult.emit(json.dumps({"asset": sp["asset"], "tf": sp["tf"], "dir": sp["dir"], "result": res}))
            self._log("ok" if win else "err",
                      ("✅ WIN" if win else "❌ LOSS") + f" — {sp['asset']} ({sp['tf']}) {sp['entry']} → {exit_px}")
            self._tg_result(sp, win, exit_px)
        self._sigpend = still

    def _tg_result(self, sp, win, exit_px):
        """رسالة نتيجة البوت — بنفس ستايل بطاقة الإشارة المصممة.
        معرف المحادثة يأتي من المؤشر نفسه (طلب المستخدم) — والاحتياط إعداد التطبيق."""
        try:
            cfg = _read_json(CFG_FILE, {})
            token = cfg.get("token", "")
            chats = str(sp.get("chats") or "") or cfg.get("chats", "")
            if not (token and chats):
                return
            dirl = "▲ BUY" if sp["dir"] == "up" else "▼ SELL"
            text = (("✅ WIN" if win else "❌ LOSS") + f" | {sp['asset']} ({sp['tf']})\n"
                    + f"{dirl} @ {sp['entry']} → {exit_px}\n📊 {sp['label']}")
            threading.Thread(target=lambda: self._tg_try(token, chats, text), daemon=True).start()
        except Exception:
            pass

    def _tg_try(self, token, chats, text):
        try:
            _tg_send(token, chats, text)
        except Exception as e:
            self._log("err", f"Telegram result: {str(e)[:90]}")

    @Slot()
    def refreshPy(self):
        self._compute_py()

    @Slot(str)
    def stopPy(self, fid):
        self._py_mods.pop(fid, None)

    @Slot(str)
    def chartShot(self, dataUrl):
        """الشارت أرسل لقطة (data:image/png;base64,....)."""
        try:
            b64 = dataUrl.split(",", 1)[1]
            png = base64.b64decode(b64)
            path = os.path.join(SHOTS_DIR, "shot_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png")
            with open(path, "wb") as fh:
                fh.write(png)
            self.shotSaved.emit(True, path)
            if self._pending:
                pend, self._pending = self._pending, None
                self._deliver(pend, png)
        except Exception as e:
            self._pending = None
            self._log("err", f"screenshot: {e}")
            if self._pending:
                pend, self._pending = self._pending, None
                self._deliver(pend, None)

    @Slot()
    def requestShot(self):
        """زر لقطة الشاشة (بدون إرسال)."""
        self._pending = None
        self.needShot.emit()

    needShot = Signal()

    def _send_signal(self, fid, label, dir_, price, when, asset=None, chats=""):
        cfg = _read_json(CFG_FILE, {})
        token = cfg.get("token", "")
        # معرف المحادثة يأتي من المؤشر نفسه (طلب المستخدم) — والاحتياط إعداد التطبيق القديم
        chats = str(chats or "").strip() or cfg.get("chats", "")
        asset = str(asset or self._asset or "")
        tmpl = TG_TMPL_DEFAULT
        dirl = "▲ BUY" if dir_ == "up" else "▼ SELL"
        try:
            text = tmpl.format(asset=asset, tf=self._tf, dir=dirl, price=price,
                               time=when, indicator=label)
        except Exception:
            text = f"{dirl} {asset} @ {price}"
        attach = bool(cfg.get("attach", True))
        entry = {"time": when, "asset": asset, "tf": self._tf, "indicator": label,
                 "dir": dir_, "price": price, "sent": None, "info": ""}
        rec = {"entry": entry, "token": token, "chats": chats, "text": text, "attach": attach}
        self._log("info", f"⚡ {label}: {dir_.upper()} {asset} @ {price}")
        if token and chats:
            self._pending = rec
            self.needShot.emit()
            # احتياط إذا لم تصدر لقطة خلال 4 ثوانٍ — أرسل نصاً فقط
            def _fallback():
                if self._pending is rec:
                    self._pending = None
                    self._deliver(rec, None)
            QTimer.singleShot(4000, _fallback)
        else:
            entry["sent"] = False
            # معرف المحادثة يُدمج في كود المؤشر من مبرمجه — لا حقل له في صفحة البوت
            entry["info"] = "no chat id — set chats in the indicator signal()" if token else "telegram not configured"
            self._hist.append(entry)
            self.histChanged.emit()
            _write_json(os.path.join(CFG_DIR, "signals.json"), self._hist[-500:])

    def _deliver(self, rec, png):
        entry = rec["entry"]
        try:
            n, errs = _tg_send(rec["token"], rec["chats"], rec["text"], png if rec["attach"] else None)
            entry["sent"] = True
            entry["info"] = f"{n} chat(s)" + ("; " + "; ".join(errs) if errs else "")
            self._log("ok", f"Telegram → {entry['info']} ({entry['asset']} {entry['dir']})")
        except Exception as e:
            entry["sent"] = False
            entry["info"] = str(e)[:120]
            self._log("err", f"Telegram: {entry['info']}")
        self._hist.append(entry)
        self.histChanged.emit()
        _write_json(os.path.join(CFG_DIR, "signals.json"), self._hist[-500:])

    @Slot(str, str, str)
    def sendTest(self, token, chats, text):
        def run():
            try:
                n, errs = _tg_send(token, chats, text)
                self.testResult.emit(True, f"{n} chat(s)" + ("; " + "; ".join(errs) if errs else ""))
            except Exception as e:
                self.testResult.emit(False, str(e)[:90])
        threading.Thread(target=run, daemon=True).start()

    @Slot(str, str, str)
    def saveTg(self, token, chats, tmpl_attach_json):
        try:
            d = json.loads(tmpl_attach_json)
            cfg = _read_json(CFG_FILE, {})
            cfg.update({"token": token, "chats": chats,
                        "tmpl": d.get("tmpl", ""), "attach": bool(d.get("attach", True))})
            _write_json(CFG_FILE, cfg)
            self._log("ok", "Telegram settings saved")
        except Exception as e:
            self._log("err", str(e))

    @Slot(result=str)
    def loadTg(self):
        cfg = _read_json(CFG_FILE, {})
        return json.dumps({"token": cfg.get("token", ""), "chats": cfg.get("chats", ""),
                           "tmpl": cfg.get("tmpl") or TG_TMPL_DEFAULT,
                           "attach": bool(cfg.get("attach", True))})

    # ---------- BADI: المؤشرات المشفرة (المفتاح داخل التطبيق فقط) ----------
    badiFpChanged = Signal()

    def _get_badi_fp(self):
        try:
            return BADI.fingerprint()
        except Exception:
            return "—"

    badiFp = Property(str, _get_badi_fp, notify=badiFpChanged)

    # ---------- مظهر الشارت: خلفية/ألوان الشموع بحرية من زر الإعدادات ----------
    chartThemeChanged = Signal()

    def _get_chart_theme_json(self):
        """التخصيصات فقط (المفاتيح التي تغيّر المستخدم عن الافتراضي) — تُدفع للويب بدلالة استبدال."""
        ov = {k: v for k, v in self._chart_theme.items() if CHART_THEME_DEFAULTS.get(k) != v}
        return json.dumps(ov, ensure_ascii=False)

    chartThemeJson = Property(str, _get_chart_theme_json, notify=chartThemeChanged)

    def _get_chart_theme_full_json(self):
        """كل قيم مظهر الشارت (الافتراضي + التخصيص) — للعرض في حقول الإعدادات."""
        return json.dumps(self._chart_theme, ensure_ascii=False)

    chartThemeFullJson = Property(str, _get_chart_theme_full_json, notify=chartThemeChanged)

    _COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
                           r"|^rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*(?:,\s*[\d.]+\s*)?\)$")

    @staticmethod
    def _hex_to_rgba(hex_color, alpha=0.5):
        """تحويل #RRGGBB إلى rgba(...) — لتوليد لون الحجم من لون الشمعة تلقائيًا."""
        h = hex_color.strip().lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) < 6:
            return None
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
        except ValueError:
            return None

    @Slot(str)
    def setChartTheme(self, js):
        """تطبيق ألوان الشارت المخصصة (أي لون hex/rgba بحرية — لا قوائم محدودة)."""
        try:
            d = json.loads(js)
        except Exception:
            return
        if not isinstance(d, dict):
            return
        applied = set()
        for k, v in d.items():
            if k in CHART_THEME_DEFAULTS and isinstance(v, str) and self._COLOR_RE.match(v.strip()):
                self._chart_theme[k] = v.strip()
                applied.add(k)
        # لون الحجم يتبع لون الشمعة تلقائيًا (إن لم يُحدَّد صراحة وقُبل لون الشمعة)
        for base, vol in (("bull", "bullVol"), ("bear", "bearVol")):
            if base in applied and vol not in d:
                derived = self._hex_to_rgba(self._chart_theme[base], 0.5)
                if derived:
                    self._chart_theme[vol] = derived
        self._save_cfg()
        self.chartThemeChanged.emit()

    @Slot()
    def resetChartTheme(self):
        """إعادة ألوان الشارت إلى الافتراضي."""
        self._chart_theme = dict(CHART_THEME_DEFAULTS)
        self._save_cfg()
        self.chartThemeChanged.emit()

    def _badi_sandbox_check(self, code):
        """فحص كود المؤشر المشفر قبل تحميله — فحص ثابت للأنماط الممنوعة (الملفات/
        الشبكة/أجزاء التطبيق الداخلية) ثم تشغيله داخل QuickJS المعزولة.
        يرجع رسالة خطأ أو None عند القبول."""
        # 1) فحص ثابت: الملفات التي ينشئها التطبيق والخدمات وأجزاء المحرك الداخلية
        #    لا يجوز للمؤشر المشفر أن يمرّ عليها — أي لمسة ترفض الملف كله (طلب المستخدم)
        try:
            if BADI_BANNED_RE.search(str(code or "")):
                return BADI_MSGS[self._lang]["blocked"]
        except Exception:
            pass
        # 2) فحص تشغيلي داخل QuickJS — لا نظام ملفات ولا شبكة هناك أصلًا
        if not _HAS_QJS:
            return None          # QuickJS غير متوفرة — يُحمَّل المؤشر ويظهر أي خطأ في كونسول المحرر
        try:
            ctx = _quickjs.Context()
            # عزل مشدد (طلب المستخدم): لا ملفات ولا شبكة أصلًا في QuickJS + حدود صارمة
            # للذاكرة والوقت — أي كود خطير يتوقف داخل البيئة المعزولة ولا يلمس الجهاز.
            try:
                ctx.set_memory_limit(64 * 1024 * 1024)     # 64MB
            except Exception:
                pass
            try:
                ctx.set_time_limit(6)                      # ثوانٍ — يوقف الحلقات اللانهائية
            except Exception:
                pass
            ctx.eval(_QJS_STUBS)
            harness = (
                "var __CODE = " + json.dumps(code) + ";\n"
                + "var __OUT = (function () {\n"
                + "  try {\n"
                + "    var __f = new Function('Indicators', 'THEME', 'log', '\"use strict\";\\n' + __CODE);\n"
                + "    var __d = __f(Indicators, {}, function () {});\n"
                + "    if (!__d || typeof __d !== 'object' || typeof __d.calculate !== 'function') return 'E:noc';\n"
                + "    var __c = [];\n"
                + "    for (var i = 0; i < 90; i++) {\n"
                + "      var t = 1700000000 + i * 60, o = 1 + i * 0.01, cl = 1.05 + i * 0.01;\n"
                + "      __c.push({ time: t, t: t, open: o, o: o, high: o + 0.05, h: o + 0.05,\n"
                + "                 low: o - 0.04, l: o - 0.04, close: cl, c: cl, volume: 1000, v: 1000 });\n"
                + "    }\n"
                + "    var __v = __d.calculate(__c, __d.settings || {});\n"
                + "    if (typeof __d.signal === 'function') __d.signal(__c, __v, __d.settings || {});\n"
                + "    return 'OK';\n"
                + "  } catch (e) { return 'E:' + (e && e.message ? e.message : String(e)); }\n"
                + "})();\n"
                + "__OUT"
            )
            out = str(ctx.eval(harness)).strip()
        except Exception:
            return None          # فشل بيئة QuickJS نفسها — لا نمنع الاستيراد بسببها
        if out == "OK":
            return None
        if out == "E:noc":
            return BADI_MSGS[self._lang]["noc"]
        msg = out[2:] if out.startswith("E:") else out
        low = msg.lower()
        # مساعد غير موجود في البيئة المعزولة فقط (الشارت يوفر window.Indicators كاملًا) → يُقبل
        if ("indicators" in low or "theme" in low or "not a function" in low
                or "undefined" in low):
            return None
        return BADI_MSGS[self._lang]["run"] + ": " + msg[:140]

    @Slot(str, str, str, str, str, str, result=str)
    def badiExport(self, code, file_name, kind="indicator", license_ids="", paid_server="", paid_id=""):
        """تشفير المؤشر وكتابة ملف .badi بجوار ملفه الأصلي في مجلد BadiCharts
        (مثل ميتاتريدر: .mq5/.ex5 جنبًا إلى جنب) — النتيجة JSON.
        يُكتب الملف الأصلي أولًا إن لم يكن على القرص، ثم الملف المشفر بجواره.
        license_ids: معرفات المستخدمين (USER ID) المسموح لهم — مفصولة بفواصل/مسافات؛
        فارغة = يعمل مع الجميع. لا يعمل الملف المشفر إلا على جهاز يطابق معرّفه (طلب المستخدم).
        المفتاح لا يُكتب في الملف — الترخيص عبر المغلف المشفر نفسه."""
        lang = self._lang
        try:
            _ensure_badi_dirs()
            kind = self._norm_kind(kind)
            if kind == "badi":
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["notbadi"]})
            ids = self._parse_license_ids(license_ids)
            if ids is None:
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["uidbad"]})
            fname = _safe_file_name(file_name) or "Indicator.js"
            base = fname.rsplit(".", 1)[0]
            src = {"fileName": fname, "kind": kind, "code": code or ""}
            src_path = self._write_entry_to_disk(src)   # حفظ المصدر أولًا (مثل حفظ .mq5 قبل الترجمة)
            # مغلف مشفر: الكود + قائمة المعرفات المرخصة — المفتاح خارج الملف تمامًا
            env = {"t": "badi-ind", "name": base, "license": ids,
                   "created": int(time.time()), "code": code or ""}
            # المؤشر المدفوع (طلب المستخدم): خادم المبرمج + معرف المؤشر عنده — يُدمان داخل
            # المغلف المشفر نفسه فلا يمكن لأي سكريبت تغييرهما، والتحكم لاحقًا من الخادم فقط
            if str(paid_server or "").strip() or str(paid_id or "").strip():
                pm = _norm_paid_manifest({"id": paid_id, "server": paid_server})
                if not pm:
                    return json.dumps({"ok": False, "error": BADI_MSGS[lang]["paidbad"]})
                env["paid"] = pm
            blob = BADI.encrypt(json.dumps(env, ensure_ascii=False))
            d = _disk_dir_for(kind)
            path = os.path.join(d, base + ".badi")
            with open(path, "wb") as fh:
                fh.write(blob)
            self.syncDiskFiles()        # يُدرج الملف المشفر في القائمة بجوار ملفه الأصلي فورًا
            return json.dumps({"ok": True, "path": path, "src": src_path or ""})
        except BADIError as e:
            return json.dumps({"ok": False, "error": BADI_MSGS[lang].get(str(e), str(e))})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)[:120]})

    @staticmethod
    def _parse_license_ids(raw):
        """قائمة معرفات المشترين من نص مفصول بفواصل/مسافات — None إذا كانت الصيغة خاطئة."""
        ids, seen = [], set()
        for tok in re.split(r"[,;\s]+", str(raw or "")):
            tok = tok.strip().upper()
            if not tok:
                continue
            if not BADI_UID_RE.match(tok):
                return None
            if tok not in seen:
                seen.add(tok)
                ids.append(tok)
        return ids

    @Slot(str, result=str)
    def badiOpenName(self, name):
        """فتح مؤشر مشفر من قائمة BadiCharts بالنقر عليه: فك التشفير داخل الذاكرة
        بمفتاح التطبيق + فحص QuickJS — النتيجة JSON (كود جاهز للإضافة للمحرر)."""
        lang = self._lang
        try:
            nm = _safe_file_name(name)
            ent = next((f for f in self._files
                        if self._norm_kind(f.get("kind")) == "badi"
                        and _safe_file_name(f.get("fileName")).lower() == nm.lower()), None)
            p = (ent or {}).get("path") or os.path.join(BADI_IND_DIR, nm)
            if not os.path.isfile(p):
                p = os.path.join(BADI_TOOL_DIR, nm)
            if not p or not os.path.isfile(p):
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["short"]})
            with open(p, "rb") as fh:
                blob = fh.read()
            plain = BADI.decrypt(blob)
            code, lic, pmanifest, pname = _badi_payload(plain)
            # بوابة الترخيص (طلب المستخدم): معرف المشتري المدمج يجب أن يطابق معرف هذا الجهاز
            if _badi_license_denied(lic):
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["license"] + _get_user_id()})
            # بوابة المؤشرات المدفوعة (طلب المستخدم): تسجيل السجل في القاعدة المحمية
            # + منع الفتح تمامًا عند انتهاء الاشتراك أو إيقاف المبرمج للمؤشر من خادمه
            if pmanifest:
                try:
                    paid_register(pmanifest, pname)
                    deny = paid_open_denied(str(pmanifest.get("id") or ""), lang)
                    if deny:
                        return json.dumps({"ok": False, "error": deny})
                except Exception:
                    pass
            warn = self._badi_sandbox_check(code)
            if warn:
                return json.dumps({"ok": False, "error": warn})
            base = re.sub(r"\.badi$", "", os.path.basename(p), flags=re.I).strip() or "indicator"
            fid = "badi" + format(int(time.time() * 1000) & 0xFFFFFFFFFFFF, "x")
            return json.dumps({"ok": True, "id": fid, "fileName": base + ".js", "code": code})
        except BADIError as e:
            return json.dumps({"ok": False, "error": BADI_MSGS[lang].get(str(e), str(e))})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)[:120]})

    @Slot(str, result=str)
    def badiImport(self, url):
        """استيراد ملف .badi: فك التشفير بمفتاح التطبيق داخل الذاكرة + فحص QuickJS — النتيجة JSON."""
        lang = self._lang
        try:
            p = url
            if p.startswith("file://"):
                try:
                    p = QUrl(p).toLocalFile()
                except Exception:
                    p = urllib.parse.unquote(urllib.parse.urlparse(p).path)
            if not p or not os.path.isfile(p):
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["short"]})
            with open(p, "rb") as fh:
                blob = fh.read()
            plain = BADI.decrypt(blob)
            code, lic, pmanifest, pname = _badi_payload(plain)
            # بوابة الترخيص (طلب المستخدم): معرف المشتري المدمج يجب أن يطابق معرف هذا الجهاز
            if _badi_license_denied(lic):
                return json.dumps({"ok": False, "error": BADI_MSGS[lang]["license"] + _get_user_id()})
            # بوابة المؤشرات المدفوعة (طلب المستخدم): تسجيل السجل في القاعدة المحمية
            # + منع الفتح تمامًا عند انتهاء الاشتراك أو إيقاف المبرمج للمؤشر من خادمه
            if pmanifest:
                try:
                    paid_register(pmanifest, pname)
                    deny = paid_open_denied(str(pmanifest.get("id") or ""), lang)
                    if deny:
                        return json.dumps({"ok": False, "error": deny})
                except Exception:
                    pass
            warn = self._badi_sandbox_check(code)
            if warn:
                return json.dumps({"ok": False, "error": warn})
            base = re.sub(r"\.badi$", "", os.path.basename(p), flags=re.I).strip() or "indicator"
            fid = "badi" + format(int(time.time() * 1000) & 0xFFFFFFFFFFFF, "x")
            return json.dumps({"ok": True, "id": fid, "fileName": base + ".js", "code": code})
        except BADIError as e:
            return json.dumps({"ok": False, "error": BADI_MSGS[lang].get(str(e), str(e))})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)[:120]})

    # ---------- لقطات الشاشة ----------
    # ملحوظة أمان: لا توجد أي وصلة تُخرج مفتاح BADI من التطبيق — لا نسخ ولا حفظ ولا إرسال.
    @Slot(str)
    def saveShot(self, dataUrl):
        self.chartShot(dataUrl)

    # ---------- الحافظة (احتياط للصق: يتيح للـ JS قراءة الحافظة عبر الجسر إن فشل navigator.clipboard) ----------
    @Slot(result=str)
    def clipboardText(self):
        return QGuiApplication.clipboard().text()

    @Slot(str)
    def copyText(self, text):
        """نسخ نص إلى حافظة الجهاز — لمعرّف المستخدم في الشريط السفلي (طلب المستخدم)."""
        try:
            QGuiApplication.clipboard().setText(str(text or ""))
        except Exception:
            pass

    # ---------- معرّف المستخدم الثابت BADI-XXXX-XXXX-XXXX (طلب المستخدم) ----------
    userId = Property(str, lambda self: _get_user_id(), constant=True)
    """معرّف هذا الجهاز الثابت — يُعرض في الشريط السفلي ويُستخدم لترخيص المؤشرات المشفرة."""

    # ---------- المؤشرات المدفوعة: بطاقة الإشعارات + قناة تحكم المبرمج (طلب المستخدم) ----------
    @Property(list, notify=notifChanged)
    def notifs(self):
        """قائمة إشعارات البطاقة الصغيرة — لا إشعارات جاهزة: المبرمج يرسلها من خادمه."""
        return self._notifs

    @Property(int, notify=notifChanged)
    def notifsUnread(self):
        """عدد غير المقروء — للشارة الحمراء على زر الإشعارات."""
        return sum(1 for n in self._notifs if not n.get("read"))

    @Slot()
    def notifsMarkAll(self):
        """فتح البطاقة يعلم الكل مقروءًا فتختفي الشارة الحمراء."""
        ch = False
        for n in self._notifs:
            if not n.get("read"):
                n["read"] = True
                ch = True
        if ch:
            self.notifChanged.emit()

    @Slot()
    def notifsClear(self):
        """مسح كل الإشعارات من البطاقة."""
        if self._notifs:
            self._notifs = []
            self.notifChanged.emit()

    def _notif_push(self, text, ind=""):
        """إشعار جديد: نص فقط ≤300 حرف — لا HTML ولا روابط ملفات (طلب المستخدم: تشديد الحماية)."""
        t = re.sub(r"[\x00-\x1f]", " ", str(text or "")).strip()[:300]
        if not t:
            return
        self._notifs.insert(0, {"t": t, "at": int(time.time()), "read": False,
                                "ind": str(ind or "")[:60]})
        if len(self._notifs) > 50:
            del self._notifs[50:]
        self.notifChanged.emit()

    def _paid_poll(self):
        """قناة تحكم المبرمج عبر خادمه (طلب المستخدم): استطلاع GET صغير لكل مؤشر مدفوع،
        استجابة JSON فقط ≤16KB وأوامر بيضاء فقط — لا رفع ولا سحب ملفات إطلاقًا،
        وأي استجابة تحوي ملفات/base64 → رفض كامل + حظر الخادم 10 دقائق."""
        try:
            recs = paid_records()
            today = _today_iso()
            now = time.time()
            for rid, rec in list(recs.items()):
                srv = str(rec.get("server") or "")
                if not srv or now < self._paid_block.get(rid, 0):
                    continue
                u = urllib.parse.urlparse(srv)
                if u.scheme not in ("https", "http") or not u.netloc:
                    continue
                try:
                    left = paid_days_left(rec, today)
                    q = urllib.parse.urlencode({
                        "ind": rid, "dev": _get_user_id(),
                        "left": "" if left is None else max(0, int(left)),
                        "st": str(rec.get("status") or ""), "v": "1"})
                    req = urllib.request.Request(
                        srv + ("&" if "?" in srv else "?") + q,
                        headers={"User-Agent": "BadiCharts-Paid/1"})
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        raw = resp.read(16385)
                    if len(raw) > 16384:
                        self._paid_block[rid] = time.time() + 600
                        continue
                    txt = raw.decode("utf-8", "ignore")
                    # حماية صارمة: أي أثر ملفات/base64 في الاستجابة → رفض + حظر الخادم
                    if re.search(r"base64|data:|file://|content-disposition|multipart", txt, re.I):
                        self._paid_block[rid] = time.time() + 600
                        continue
                    data = json.loads(txt)
                    if not isinstance(data, dict) or not isinstance(data.get("cmds"), list):
                        continue
                    if len(data["cmds"]) > 20:
                        self._paid_block[rid] = time.time() + 600
                        continue
                    self._paid_apply(rid, rec, data["cmds"])
                except Exception:
                    continue   # الخادم غير متاح — بلا إزعاج للمستخدم
        except Exception:
            pass

    def _paid_apply(self, rid, rec, cmds):
        """تنفيذ الأوامر البيضاء التي قررتها القاعدة: تشغيل/إيقاف عبر الجسر + إشعارات نصية."""
        try:
            toggles, notes = paid_apply_commands(rid, rec, cmds)
            for nm, on in toggles:
                if nm:
                    self.paidCmd.emit(json.dumps({"name": nm, "on": bool(on)}))
            for nt in notes:
                self._notif_push(nt, rec.get("name") or rid)
        except Exception:
            pass

    def _paid_watch(self):
        """مراقبة الاشتراك محليًا من القاعدة المحمية (طلب المستخدم): تذكير قبل الانتهاء
        بـ 7/3/1 يوم، وعند الانتهاء: إشعار + إيقاف المؤشر حتى يجدد المبرمج من خادمه."""
        try:
            today = _today_iso()
            for rid, rec in list(paid_records().items()):
                if not rec.get("expiry"):
                    continue
                left = paid_days_left(rec, today)
                if left is None:
                    continue
                name = str(rec.get("name") or rid)
                ar = self._lang == "ar"
                lv = -1 if left < 0 else (1 if left <= 1 else (3 if left <= 3 else (7 if left <= 7 else 30)))
                if lv < int(rec.get("warned", 99)):
                    rec["warned"] = lv
                    paid_save_rec(rec)
                    if lv == -1:
                        self._notif_push((ar and ("انتهى اشتراك مؤشر " + name + " — يجب التجديد لاستخدامه من جديد"))
                                         or ("Subscription of " + name + " ended — renew to use it again"), name)
                        if rec.get("enabled"):
                            rec["enabled"] = False
                            paid_save_rec(rec)
                            self.paidCmd.emit(json.dumps({"name": name, "on": False}))
                    else:
                        self._notif_push((ar and ("ينتهي اشتراك مؤشر " + name + " بعد " + str(max(0, left)) + " يوم — يجب التجديد"))
                                         or ("Subscription of " + name + " ends in " + str(max(0, left)) + " day(s) — renew"), name)
        except Exception:
            pass

    @Slot(result=str)
    def openBadiDir(self):
        """فتح مجلد BadiCharts على القرص (Indicators + Tools) — المستخدم يضع فيه
        المؤشرات والأدوات مباشرة فيتعرّف عليها التطبيق تلقائيًا (طلب المستخدم)."""
        try:
            _ensure_badi_dirs()
            QDesktopServices.openUrl(QUrl.fromLocalFile(BADI_DIR))
            return BADI_DIR
        except Exception:
            return ""

    # ---------- الأيقونات والشعار ----------
    @Slot(str, bool, result=str)
    def logo(self, name, dark):
        return logo_uri(name, dark)

    @Slot(str, str, result=str)
    def icon(self, name, color):
        return icon_uri(name, color)

    @Slot(bool, result=str)
    def mark(self, dark):
        """علامة BadiCharts (الشمعتان فقط) — لصفحة الدخول الجديدة."""
        p = LOGO_PAL[bool(dark)]
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="8 16 76 76">'
               + ICON_SVG.format(**p) + '</svg>')
        return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)
# ---------------------------------------------------------------- الواجهة (QML)
# ---------------------------------------------------------------- واجهة الويب المدمجة (HTML داخل التطبيق)
# الشارت هنا هو مكتبة BADI-CHARTS-V2 v2.13.0 نفسها والمحرر هو Monaco — كلاهما داخل صفحة HTML
# تُكتب بجانب التطبيق عند الإقلاع وتُستعرض داخل النافذة عبر QtWebEngine.


# يُحقن قبل سكربت الصفحة: أعلام التضمين + ملفات المستخدم + إخفاء أدوات السوق المكررة
BRIDGE_PRE = r"""<script>
/* BadiCharts Studio — desktop bridge (pre) */
window.__BADI_EMBEDDED = true;
window.__BADI_BOOT_FILES = __BOOT_JSON__;
window.__BADI_APP_THEME__ = __THEME_JSON__;
window.__badiThemeKit = (function () {
  function rgba(hex, a) {
    var h = String(hex || "").replace("#", "");
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var n = parseInt(h, 16) || 0;
    return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + a + ")";
  }
  /* ألوان صفحة الويب ← ألوان تطبيق سطح المكتب (تتبعها وتتغير معها مباشرة) */
  function applyVars(t) {
    if (!t || !t.c) return;
    var s = document.documentElement.style, c = t.c;
    s.setProperty("--bg", c.bg);
    s.setProperty("--panel", c.side);
    s.setProperty("--panel2", c.card);
    s.setProperty("--panel3", c.card);
    s.setProperty("--border", c.border);
    s.setProperty("--border2", c.border);
    s.setProperty("--text", c.fg);
    s.setProperty("--accent", c.accent);
    s.setProperty("--accent-h", c.g1);
    s.setProperty("--accent-t", c.g1);
    s.setProperty("--acc-soft", rgba(c.accent, 0.12));
    s.setProperty("--acc-bd", rgba(c.accent, 0.5));
    s.setProperty("--violet", c.g2);
    s.setProperty("--ok", c.good);
    s.setProperty("--err", c.bad);
    /* شريط التمرير يتكيف مع الثيم: شبه أسود على الداكن وشبه أبيض على الفاتح (طلب المستخدم) */
    s.setProperty("--sbar", t.dark ? "#2e333c" : "#ccd4df");
    s.setProperty("--sbar-h", t.dark ? "#454b56" : "#aeb9c8");
    if (t.dark) {
      s.setProperty("--t-bright", "#e4e4e7");
      s.setProperty("--t-mid", "#a1a1aa");
      s.setProperty("--t-dim", "#71717a");
      s.setProperty("--t-dim2", "#52525b");
      s.setProperty("--t-dim3", "#3f3f46");
      s.setProperty("--btn-bg", "#1e222d");
      s.setProperty("--ok-soft", "rgba(34,197,94,0.25)");
    } else {
      s.setProperty("--t-bright", "#18181b");
      s.setProperty("--t-mid", "#44536b");
      s.setProperty("--t-dim", "#5b6b80");
      s.setProperty("--t-dim2", "#6b7a90");
      s.setProperty("--t-dim3", "#a8b3c4");
      s.setProperty("--btn-bg", c.hover);
      s.setProperty("--ok-soft", "rgba(22,163,74,0.18)");
    }
    try { document.documentElement.style.colorScheme = t.dark ? "dark" : "light"; } catch (e) {}
    var m = document.querySelector('meta[name="color-scheme"]');
    if (m) m.setAttribute("content", t.dark ? "dark" : "light");
  }
  /* خريطة ثيم الشارت (BADI-CHARTS setTheme) من ألوان التطبيق */
  function chartTheme(t) {
    if (!t || !t.c) return null;
    var c = t.c, dark = !!t.dark;
    return {
      bg: c.bg, panelBg: c.card, toolbarBg: c.card, toolbarBorder: c.border,
      grid: c.border, gridStrong: c.border, axis: c.border,
      axisBg: c.card, axisBorder: c.border, axisText: c.sub,
      text: c.fg, textDim: c.sub, textBright: c.fg, textFade: c.sub,
      bull: c.good, bear: c.bad, bullVol: rgba(c.good, 0.5), bearVol: rgba(c.bad, 0.5),
      accent: c.accent, crosshair: c.sub, crosshairLabel: dark ? "#26262b" : "#e6ebf4",
      ma1: c.accent, ma2: c.g1, ma3: c.g2,
      bollingerMid: c.g1, bollingerBand: rgba(c.g2, 0.35),
      rsi: c.g2, rsiOver: c.bad, rsiUnder: c.good,
      macd: c.accent, macdSignal: c.g1, macdHistBull: rgba(c.good, 0.5), macdHistBear: rgba(c.bad, 0.5),
      drawing: c.accent, drawingActive: c.g1,
      buttonBg: c.card, buttonHover: c.hover, buttonText: c.fg,
      currentPriceBull: c.good, currentPriceBear: c.bad
    };
  }
  /* ثيم Monaco من ألوان التطبيق */
  function monTheme(t) {
    if (!t || !t.c) return null;
    var c = t.c, dark = !!t.dark;
    var bg = c.card, fg = dark ? "#e6e9ef" : "#1f2733";
    return {
      base: dark ? "vs-dark" : "vs", inherit: true,
      rules: [
        { token: "comment", foreground: dark ? "6b7280" : "8a94a6", fontStyle: "italic" },
        { token: "keyword", foreground: String(c.g1 || "#38bdf8").slice(1) },
        { token: "number", foreground: String(c.accent || "#3b8bff").slice(1) },
        { token: "string", foreground: dark ? "a5d6a7" : "0f7b3f" },
        { token: "type.identifier", foreground: String(c.g2 || "#3b6cf5").slice(1) },
        { token: "delimiter", foreground: fg.slice(1) }
      ],
      colors: {
        "editor.background": bg,
        "editor.foreground": fg,
        "editorLineNumber.foreground": dark ? "#3f4654" : "#a8b3c4",
        "editorLineNumber.activeForeground": String(c.g1 || "#38bdf8").slice(1),
        "editor.selectionBackground": String(c.accent || "#3b8bff") + (dark ? "55" : "30"),
        "editor.lineHighlightBackground": c.hover || (dark ? "#151518" : "#eaeff8"),
        "editorCursor.foreground": String(c.g1 || "#38bdf8").slice(1),
        "editorIndentGuide.background1": c.border,
        "editorGutter.background": bg
      }
    };
  }
  return { rgba: rgba, applyVars: applyVars, chartTheme: chartTheme, monTheme: monTheme };
})();
(function () { try {
  document.documentElement.classList.add("embedded");
  if (window.__badiThemeKit) window.__badiThemeKit.applyVars(window.__BADI_APP_THEME__);
} catch (e) {} })();
</script>
<style>#indBtn,#shotBtn{display:none!important}
html.embedded #indBtn{display:inline-flex!important;align-items:center}
html.embedded #shotBtn{display:grid!important}
html.embedded .modal-opts{grid-template-columns:repeat(2,1fr)}</style>"""

# يُحقن بعد سكربت الصفحة: جسر Python ↔ الصفحة
BRIDGE_POST = r"""<script>
/* ═══════════════ BadiCharts Studio — desktop bridge (post) ═══════════════
   يربط صفحة HTML (شارت BADI-CHARTS v2.13.0 + محرر Monaco) بمحرك Python:
   • الشموع تُدفع من Python (setCandles / pushTick) بدل المحاكاة المحلية
   • مؤشرات Python تُرسم عبر pyMeta / setPy
   • ملفات المستخدم تُزامَن مع التطبيق عبر BADI::files
   • إشارات المؤشرات (signal) تُرسل إلى Python عبر BADI::signal
   • لقطة الشارت تُرسل عبر BADI::shot عند الطلب
   • ثيم التطبيق (داكن/فاتح) يُطبَّع على الصفحة فوراً عبر setTheme
   ════════════════════════════════════════════════════════════════════════ */
(function () {
"use strict";
if (!window.__BADI_EMBEDDED) return;
var BOOT = window.__BADI_BOOT_FILES || {};
var SIG_DEFS = [];
var SIG_SEEN = {};
var PY = {};
var PY_STARTED = {};
/* BADI: المؤشرات المشفرة المحمّلة داخليًا — الكود لا يدخل قائمة الملفات ولا المحرر */
var HID_IND = {};

function send(cmd, obj) {
  try { console.log("BADI::" + cmd + " " + (typeof obj === "string" ? obj : JSON.stringify(obj))); } catch (e) {}
}
/* صفحة الاستوديو (سكربت الصفحة الرئيسي) تُبلّغ سطح المكتب عبر هذه البوابة:
   حذف عملة من الشريط (×) وتبديل العملة بالنقر على الشريحة */
window.__badiSend = send;
/* ═══ LIVE SERVER EDITION: دفعة التمرير للخلف (300 شمعة) ═══
   عندما يقترب التمرير من بداية البيانات يُطلب من الخادم دفعة أقدم؛ وصولها
   يُدمج في الشارت مع تثبيت العرض الحالي تماماً (لا قفزة ولا إعادة ضبط). */
var OLDER = { loading: false, at: 0, asset: "", tf: "", key: null, anchor: null, exhausted: null, consec: 0 };
/* ═══ v13.2 (طلب المستخدم): دائرة تحميل داخل الشارت ═══
   عندما تُفتح عملة لم تُجلب بعد تظهر دائرة تحميل وسط الشارت مع نص
   «جارٍ جلب الشموع من الخادم» — وتختفي فور وصول أول شموع — بدل شارت أسود فارغ */
var CHLOAD = { on: false, asset: "", el: null };
function chartLoadEl(pr) {
  try {
    if (!CHLOAD.el) {
      var st = document.createElement("style");
      st.textContent = ".badi-load{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;z-index:6;pointer-events:none;background:rgba(7,10,16,.72)}"
        + ".badi-load .bl-ring{width:46px;height:46px;border-radius:50%;border:3px solid rgba(128,140,170,.22);border-top-color:#3B8BFF;animation:badispin .9s linear infinite}"
        + ".badi-load .bl-txt{font:600 12px/1 system-ui,-apple-system,Segoe UI,sans-serif;letter-spacing:.3px;opacity:.7}"
        + ".badi-load .bl-sub{font:10px/1 system-ui,sans-serif;opacity:.45;margin-top:-6px}"
        + "@keyframes badispin{to{transform:rotate(360deg)}}";
      document.head.appendChild(st);
      CHLOAD.el = document.createElement("div");
      CHLOAD.el.className = "badi-load";
      CHLOAD.el.hidden = true;
    }
    var ar = window.__BADI_LANG__ === "ar";
    var _sub = CHLOAD.asset ? CHLOAD.asset : "";
    CHLOAD.el.innerHTML = '<div class="bl-ring"></div><div class="bl-txt">'
      + (ar ? "جارٍ جلب الشموع من الخادم…" : "Loading candles from server…")
      + '</div>' + (_sub ? '<div class="bl-sub">' + esc(_sub) + '</div>' : '');
    var host = pr && pr.el ? pr.el.querySelector(".pane-cv") : null;
    if (host && CHLOAD.el.parentNode !== host) host.appendChild(CHLOAD.el);
    return CHLOAD.el;
  } catch (e) { return null; }
}
/* ═══ v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة ═══
   شارة الزاوية أُزيلت («تلك دائرة تحميل لي ضفتها في جنب لماذا ضفتها هناك»).
   الدائرة الوسطى فقط: تظهر عند بداية جلب شموع العملة المفتوحة من قائمة
   العملات وتبقى حتى ينتهي الجلب فيظهر الشارت — غطاء تحميل كامل فوق الشارت. */
function renderChartLoading() {
  try {
    var pr = window.__badiPrimary ? window.__badiPrimary() : null;
    var el = chartLoadEl(pr);
    if (el) el.hidden = !CHLOAD.on;
  } catch (e) {}
}
window.__badiMaybeLoadOlder = function (p, auto) {
  /* v14.3 (طلب المستخدم): طريقة الرجوع الى الخلف لجلب الشموع التاريخية أُلغيت
     نهائياً — لم تنجح. البديل الرسمي: عند فتح العملة فقط يجلب الخادم دفعة
     300 شمعة ثم 300 اخرى (مثلما كان في السابق) حتى عدد الأيام المضبوط في
     الإعدادات، وكل دفعة تُرفع إلى الشارت فور وصولها عبر prependCandles.
     لذلك لا تُرسل طلبات older من التمرير ولا تُطبع أي رسائل في الترمينال. */
  return;
};
function reportFiles() {
  try {
    var full = JSON.stringify({ v: 1, files: files });
    var CH = 14000;
    if (full.length <= CH) { send("files", full); return; }
    var n = Math.ceil(full.length / CH);
    for (var i = 0; i < n; i++)
      console.log("BADI::files~" + (i + 1) + "/" + n + " " + full.substr(i * CH, CH));
  } catch (e) {}
}

/* ---- شموع بصيغة مزدوجة: {t,o,h,l,c,v} ↔ {time,open,high,low,close,volume} ---- */
function norm1(c) {
  if (!c) return c;
  if (c.time !== undefined && c.close !== undefined) {
    if (c.t === undefined) c.t = c.time;
    if (c.o === undefined) c.o = c.open;
    if (c.h === undefined) c.h = c.high;
    if (c.l === undefined) c.l = c.low;
    if (c.c === undefined) c.c = c.close;
    return c;
  }
  return { time: c.t, open: c.o, high: c.h, low: c.l, close: c.c, volume: c.v || 0,
           t: c.t, o: c.o, h: c.h, l: c.l, c: c.c };
}
function normArr(a) {
  var out = [];
  for (var i = 0; i < a.length; i++) out.push(norm1(Object.assign({}, a[i])));
  return out;
}
function forceRecalc() {
  try {
    var pr = window.__badiPrimary ? window.__badiPrimary() : null;
    if (pr && pr.dataArr && pr.dataArr.length && pr.chart) {
      pr.chart.update(Object.assign({}, pr.dataArr[pr.dataArr.length - 1]));   // نسخة — chart.update قد يعدّل الكائن
    }
  } catch (e) {}
}
function runSignals() {
  if (!SIG_DEFS.length) return;
  var pr = window.__badiPrimary ? window.__badiPrimary() : null;
  var dd = pr ? pr.dataArr : null;
  if (!dd || !dd.length) return;
  if (Object.keys(SIG_SEEN).length > 4000) SIG_SEEN = {};   /* تنظيف دوري لمفاتيح التكرار */
  for (var i = 0; i < SIG_DEFS.length; i++) {
    var s = SIG_DEFS[i];
    try {
      var v = s.def.calculate(dd, s.def.settings || {});
      var sig = s.def.signal(dd, v, s.def.settings || {});
      if (sig && sig.dir) {
        /* chats = معرف المحادثة يأتي من المؤشر نفسه (طلب المستخدم) */
        send("signal", { id: s.id, label: String(s.fileName || s.def.label || s.id),
                         dir: String(sig.dir), price: Number(sig.price || dd[dd.length - 1].close),
                         chats: String(sig.chats || "") });
        /* نفس الإشارة تظهر في قائمة الإشارات يسار الشارت (بدون تكرار لنفس الشمعة) */
        try {
          if (window.__badiPushSignal) {
            var ck = String(s.id) + "|" + String(sig.dir) + "|" + String(dd[dd.length - 1].time);
            if (!SIG_SEEN[ck]) {
              SIG_SEEN[ck] = 1;
              var tfBtn = document.querySelector(".tf.on");
              var tfL = tfBtn && tfBtn.dataset ? tfBtn.dataset.tf : String(pr.tf || "");
              window.__badiPushSignal({ asset: String(pr.asset || ""),
                                        tf: String(tfL),
                                        dir: String(sig.dir), price: Number(sig.price || 0),
                                        indicator: String(s.fileName || s.def.label || s.id),
                                        durSec: Math.round((window.tfMs ? window.tfMs(tfL) : 60000) / 1000),
                                        card: sig.card || null });
            }
          }
        } catch (e) {}
      }
    } catch (e) {}
  }
}
function findFile(id) {
  for (var i = 0; i < files.length; i++) if (files[i].id === id) return files[i];
  return null;
}

/* ═══ ماسح الإشارات متعدد العملات (طلب المستخدم) ═══
   المؤشر يحدد نطاق عملاته بإعداد scope في settings:
   • scope: "added" → إشارات العملات المضافة إلى الشريط فقط
   • scope: "high"  → العملات ذات نسبة الدفع الأعلى (settings.minPayout — ليست شرطًا تكون مضافة)
   • scope: "all"   → كل العملات إذا أراد المستخدم
   بدونه يعمل المؤشر على عملة الشارت فقط كما هو معتاد. الماسح يعمل كل ٣ ثوانٍ
   على بيانات محاكاة محلية لكل عملة، ويرسل الإشارة لبطاقتها وإشعارات تلغرام. */
function scanScopeAssets(scope, minPay) {
  if (scope === "added") return addedNames().slice();
  var bd = (typeof BOARD !== "undefined" && BOARD) ? BOARD : [];
  var all = bd.map(function (x) { return x.name; });
  if (scope === "high") {
    var mp = Number(minPay || 85);
    var hi = bd.filter(function (x) { return Number(x.payout || 0) >= mp; }).map(function (x) { return x.name; });
    return hi.length ? hi : all;
  }
  return all;
}
function scanSignals() {
  if (!SIG_DEFS.length || typeof generateCandles !== "function") return;
  /* LIVE SERVER EDITION (طلب المستخدم): الماسح المتعدد كان يولّد شموعاً وهمية
     لكل عملة — انزع في وضع الخادم الحي. إشارات عملة الشارت الحقيقية تغطيها
     runSignals على بيانات الخادم الفعلية */
  if (window.__BADI_EMBEDDED) return;
  var pr = window.__badiPrimary ? window.__badiPrimary() : null;
  var tf = pr ? pr.tf : "1m";
  for (var i = 0; i < SIG_DEFS.length; i++) {
    var s = SIG_DEFS[i];
    var scope = s.def && s.def.settings ? String(s.def.settings.scope || "") : "";
    if (scope !== "added" && scope !== "high" && scope !== "all") continue;
    var targets = scanScopeAssets(scope, s.def.settings.minPayout).slice(0, 40);
    for (var j = 0; j < targets.length; j++) {
      var nm = targets[j];
      if (pr && nm === pr.asset) continue;          /* عملة الشارت تغطيها runSignals */
      try {
        var cd = generateCandles(assetCfg(nm), tf, 300);
        if (!cd || cd.length < 30) continue;
        var v = s.def.calculate(cd, s.def.settings || {});
        var sig = s.def.signal(cd, v, s.def.settings || {});
        if (!sig || !sig.dir) continue;
        var ck = "SCAN|" + nm + "|" + String(sig.dir) + "|" + String(cd[cd.length - 1].t);
        if (SIG_SEEN[ck]) continue;
        SIG_SEEN[ck] = 1;
        var px = Number(sig.price || cd[cd.length - 1].c);
        if (window.__badiPushSignal) {
          window.__badiPushSignal({ asset: nm, tf: String(tf), dir: String(sig.dir), price: px,
                                    indicator: String(s.fileName || s.def.label || s.id),
                                    durSec: Math.round((window.tfMs ? window.tfMs(tf) : 60000) / 1000),
                                    card: sig.card || null });
        }
        send("signal", { id: s.id, label: String(s.fileName || s.def.label || s.id),
                         dir: String(sig.dir), price: px, asset: nm,
                         chats: String(sig.chats || "") });
      } catch (e) {}
    }
  }
}
setInterval(function () { try { scanSignals(); } catch (e) {} }, 3000);

/* ---- BADI: المؤشر المشفر يعمل داخليًا فقط — طلب المستخدم ----
   الكود يُفك في ذاكرة بايثون بمفتاح التطبيق ثم يُمرّر هنا مباشرة:
   • لا يُضاف لقائمة الملفات ولا يُفتح في المحرر ولا يُحفظ في أي مكان
   • بطاقة المؤشر على الشارت بلا زر تعديل (إخفاء/إعدادات/حذف فقط)
   • إشاراته (signal) تعمل مثل أي مؤشر آخر عبر SIG_DEFS
   • لا يمكنه الوصول لملفات التطبيق — فحص الخطر يجري في QuickJS قبل الوصول هنا */
function loadHiddenIndicator(o) {
  try {
    var id = String((o && o.id) || "");
    var name = String((o && o.fileName) || "encrypted.js");
    if (!id || !o || !o.code) return;
    var ch = aChart();
    if (!ch) { log("err", name + ": the chart is not ready yet — open a pane and retry"); return; }
    /* مرة واحدة لكل شارت: التقاط removeIndicator لتنظيف إشارات المؤشر المحذوف */
    if (!ch.__badiHidPatch) {
      ch.__badiHidPatch = true;
      ch.__badiOrigRem = ch.removeIndicator.bind(ch);     /* الأصل يُحفظ على الشارت نفسه */
      ch.removeIndicator = function (rid) {
        if (HID_IND[rid]) {
          SIG_DEFS = SIG_DEFS.filter(function (x) { return x.id !== rid; });
          delete HID_IND[rid];
        }
        return ch.__badiOrigRem(rid);
      };
    }
    var origRem = ch.__badiOrigRem;
    if (HID_IND[id]) {                    /* إعادة تحميل نفس المؤشر يستبدل النسخة القديمة */
      try { origRem(id); } catch (e) {}
      SIG_DEFS = SIG_DEFS.filter(function (x) { return x.id !== id; });
      delete HID_IND[id];
    }
    var r = compileScript(String(o.code), function () {});
    if (!r || r.error || !r.def) {
      log("err", name + ": " + ((r && r.error) || "invalid indicator code"));
      return;
    }
    if (typeof r.def.render !== "function" && typeof r.def.calculate === "function")
      r.def.render = defaultLineRender;
    var g = guardDef({ id: id, fileName: name }, r.def);
    ch.addIndicator(g, { icons: ["hide", "settings", "delete"] });   /* بلا زر التعديل — الكود لا يُفتح */
    HID_IND[id] = { fileName: name };
    if (typeof r.def.signal === "function")
      SIG_DEFS.push({ id: id, fileName: name, def: r.def });
    log("ok", "🔒 " + name + " — encrypted indicator loaded (runs internally, code stays hidden)");
  } catch (e) {}
}
function pyRun(f) {
  f.enabled = true; scheduleSave(); renderTabs(); renderRunBtn();
  log("info", f.fileName + " — compiling in the Python engine…");
  send("runpy", { id: f.id, fileName: f.fileName, code: f.code });
}
function pyStop(f) {
  f.enabled = false; scheduleSave(); renderTabs(); renderRunBtn();
  log("info", "⏻ Stopped " + f.fileName);
  send("stopy", { id: f.id });
}

/* ---- رقعات تُطبَّق قبل إقلاع الصفحة ---- */
var origLoadState = loadState;
loadState = function () {
  origLoadState();
  if (BOOT.files && BOOT.files.length) {
    files = BOOT.files.map(function (f) {
      return { id: f.id, fileName: f.fileName, kind: f.kind, code: f.code || "",
               enabled: !!f.enabled, createdAt: f.createdAt || Date.now() };
    });
    activeId = files.length ? files[0].id : null;
  }
};

var origApplyFile = applyFile;
applyFile = function (f, activate) {
  if (f && f.kind === "py") return false;
  var ok = origApplyFile(f, activate);
  try {
    SIG_DEFS = SIG_DEFS.filter(function (x) { return x.id !== f.id; });
    if (ok && f && f.kind === "indicator") {
      var r = compileScript(f.code, function () {});
      if (r.def && typeof r.def.signal === "function")
        SIG_DEFS.push({ id: f.id, fileName: f.fileName, def: r.def });
    }
  } catch (e) {}
  return ok;
};

var origRunFile = runFile;
runFile = function (id, activate) {
  var f = findFile(id);
  if (f && f.kind === "py") {
    if (!f.enabled || editedIds.has(f.id)) pyRun(f);
    return true;
  }
  return origRunFile(id, activate);
};

var origToggleFile = toggleFile;
toggleFile = function (id) {
  var f = findFile(id);
  if (f && f.kind === "py") {
    if (f.enabled) pyStop(f); else pyRun(f);
    return true;
  }
  return origToggleFile(id);
};

var origDeleteFile = deleteFile;
deleteFile = function (id) {
  var f = findFile(id);
  if (f && f.kind === "py") {
    if (!window.confirm("Permanently delete file " + f.fileName + "?")) return;
    if (f.enabled) send("stopy", { id: f.id });
    try { if (PY[id] && window.__badiPCH()) { window.__badiPCH().removeIndicator(id); delete PY[id]; } } catch (e) {}
    files = files.filter(function (x) { return x.id !== id; });
    if (activeId === id) activeId = files.length ? files[0].id : null;
    dirtyIds.delete(id); editedIds.delete(id); curCodeId = null;
    scheduleSave(); renderTabs(); renderEdBar(); renderCodeArea();
    log("info", "🗑 Deleted file " + f.fileName);
    return true;
  }
  return origDeleteFile(id);
};

var origEditorSetCode = editorSetCode;
editorSetCode = function (code, id) {
  origEditorSetCode(code, id);
  try {
    var f = activeFile();
    if (monacoReady && ed && f && window.monaco && ed.getModel())
      monaco.editor.setModelLanguage(ed.getModel(), f.kind === "py" ? "python" : "javascript");
  } catch (e) {}
};

var origScheduleSave = scheduleSave;
scheduleSave = function () { origScheduleSave(); reportFiles(); };

var origSaveNow = saveNow;
saveNow = function () { origSaveNow(); reportFiles(); };

var origRenderEdToggle = renderEdToggle;
renderEdToggle = function () { origRenderEdToggle(); send("editor", editorOpen ? "1" : "0"); };

/* loadData أُزيلت من الصفحة — بيانات اللوحات محلية للوحات غير المغذاية،
   واللوحة المغذاية (المطابقة لأصل المحرك) تستقبل شموعها عبر setCandles/pushTick */

var origBuildStatic = buildStatic;
buildStatic = function () {
  origBuildStatic();
  try {
    var mk = BOOT.market || null;
    if (mk && mk.tfs && mk.tfs.length) {
      document.getElementById("tfGroup").innerHTML = mk.tfs.map(function (t) {
        return '<button class="tf" data-tf="' + t + '">' + t + "</button>"; }).join("");
      document.querySelectorAll(".tf").forEach(function (b) {
        b.classList.toggle("on", b.dataset.tf === (mk.tf || "")); });
      /* إعادة تطبيق حالة طي الفريمات بعد إعادة بناء الأزرار (طلب المستخدم) */
      if (typeof applyTfCollapse === "function") applyTfCollapse();
      live = (mk.live === undefined) ? true : !!mk.live;
    }
    window.CUR_ASSET = String((mk && mk.asset) || "");
  } catch (e) {}
};
/* الشريط الثاني (صفحة الويب): الفريم مملوك لمحرك Python في وضع سطح المكتب،
   وأزرار بوت تلجرام/الخروج نُقلت إليه من الشريط العلوي للتطبيق.
   الوضع الليلي/النهاري في الترويسة العليا فقط — والبث الحي يعمل دائمًا بلا زر (طلب المستخدم) */
(function wireToolbar() {
  function click(id, fn) { var el = document.getElementById(id); if (el) el.addEventListener("click", fn); }
  click("indBtn", function () { send("page", "1"); });
  click("shotBtn", function () { send("shot", "1"); });
  var tg = document.getElementById("tfGroup");
  if (tg) tg.addEventListener("click", function (e) {
    var b = e.target.closest(".tf");
    /* الفريم يُدار من بايثون فقط للوحة المغذاية من المحرك — اللوحات الأخرى محلية */
    var st = window.__badiPaneState ? window.__badiPaneState() : { active: 0, primary: 0 };
    if (b && st.active === st.primary) send("tf", b.dataset.tf);
  });
  click("webTg", function () { send("page", "2"); });
  click("webLogout", function () { send("logout", "1"); });
})();

window.addEventListener("beforeunload", function () { reportFiles(); });

/* ---- توحيد بيئة المؤشرات (طبقة حماية لكل الأكواد) ----
   شموع الشارت الداخلية تصل بالمفاتيح الطويلة (close/high/low) فقط، وأكواد المستخدم
   والقوالب القديمة تستعمل المختصرة (c/h/l) — وTHEME في المكتبة v2.9.0 لا يحوي
   good/bad/g1/g2/sub كما لا يوفر barW. نلفّ compileScript بحيث:
   1) يصل calculate/signal شموع تحمل المجموعتين معًا
   2) يصل render بمساعد h مُوسَّع (THEME كامل + barW) */
function patchIndicatorEnv() {
  if (window.__IND_ENV_PATCHED__) return;
  window.__IND_ENV_PATCHED__ = 1;
  try {
    var origCompile = compileScript;
    compileScript = function (code, logFn) {
      var r = origCompile(code, logFn);
      if (r && r.def) {
        ["calculate", "signal"].forEach(function (k) {
          var fn = r.def[k];
          if (typeof fn !== "function") return;
          r.def[k] = function (candles) {
            var a = arguments;
            if (candles) for (var i = 0; i < candles.length; i++) {
              var c = candles[i]; if (!c) continue;
              if (c.c === undefined && c.close !== undefined) {
                c.t = c.time; c.o = c.open; c.h = c.high; c.l = c.low; c.c = c.close; c.v = c.volume;
              }
              if (c.close === undefined && c.c !== undefined) {
                c.time = c.t; c.open = c.o; c.high = c.h; c.low = c.l; c.close = c.c; c.volume = c.v;
              }
            }
            return fn.apply(this, a);
          };
        });
        var rf = r.def.render;
        if (typeof rf === "function") {
          r.def.render = function (ctx, v, h, s) {
            try {
              var T = h.THEME || {};
              var app = (window.__BADI_APP_THEME__ && window.__BADI_APP_THEME__.c) || {};
              var h2 = Object.create(h);
              h2.THEME = Object.assign({}, T, {
                good: app.good || T.bull || "#22C55E",
                bad: app.bad || T.bear || "#EF4444",
                g1: app.g1 || "#14B8F5",
                g2: app.g2 || "#3B6CF5",
                sub: app.sub || T.textDim || "#8A9099"
              });
              if (h2.barW === undefined) h2.barW = h.barSpacing || 6;
              return rf.call(this, ctx, v, h2, s);
            } catch (e) { return rf.call(this, ctx, v, h, s); }
          };
        }
      }
      return r;
    };
  } catch (e) {}
}

/* ---- مساعدات إضافية للمكتبة القديمة (stoch/atr) + API السوق للمؤشرات ---- */
function augmentIndicators() {
  try {
    window.Indicators = window.Indicators || {};
    /* ═══ API السوق للمؤشرات (طلب المستخدم) ═══
       المؤشر المبرمَج من المستخدم يستطيع الحصول على:
       • Indicators.market.info([الزوج])  → {name, payout, open, otc} — نسبة الدفع + السوق مفتوح أم مغلق
       • Indicators.market.assets()       → كل العملات مع نسبة الدفع وحالة السوق
       • Indicators.market.added()        → العملات المضافة إلى الشريط فقط
       • Indicators.market.current()      → عملة الشارت النشط الآن
       حالة السوق: OTC والعملات الرقمية مفتوحة دائمًا — والفوركس مفتوح من الأحد 22:00 إلى الجمعة 22:00 UTC */
    window.Indicators.market = {
      info: badiMarketInfo,
      current: function () { return String((aPane() && aPane().asset) || CUR_ASSET || ""); },
      added: function () { return addedNames().slice(); },
      assets: function () {
        var bd = (typeof BOARD !== "undefined" && BOARD) ? BOARD : [];
        return bd.map(function (x) {
          return { name: x.name, payout: Number(x.payout || 0), open: badiMarketOpen(x.name), otc: x.name.indexOf("OTC") >= 0 };
        });
      }
    };
    if (!window.Indicators.stoch) window.Indicators.stoch = function (candles, p, sm) {
      var raw = new Array(candles.length).fill(null), i, j;
      for (i = p - 1; i < candles.length; i++) {
        var hh = -1e18, ll = 1e18;
        for (j = i - p + 1; j <= i; j++) { hh = Math.max(hh, candles[j].high); ll = Math.min(ll, candles[j].low); }
        raw[i] = hh === ll ? 50 : (candles[i].close - ll) / (hh - ll) * 100;
      }
      var k = new Array(raw.length).fill(null), d = new Array(raw.length).fill(null);
      for (i = 0; i < raw.length; i++) {
        if (raw[i] == null) continue;
        var seg = [], w;
        for (w = i; w >= 0 && w > i - sm; w--) { if (raw[w] == null) break; seg.push(raw[w]); }
        if (seg.length === sm) k[i] = seg.reduce(function (a, b) { return a + b; }, 0) / sm;
      }
      for (i = 0; i < k.length; i++) {
        if (k[i] == null) continue;
        var seg2 = [], w2;
        for (w2 = i; w2 >= 0 && w2 > i - sm; w2--) { if (raw[w2] == null) break; seg2.push(raw[w2]); }
        if (seg2.length === sm) d[i] = seg2.reduce(function (a, b) { return a + b; }, 0) / sm;
      }
      return { k: k, d: d };
    };
    if (!window.Indicators.atr) window.Indicators.atr = function (candles, p) {
      var tr = candles.map(function (c, i) {
        if (i === 0) return c.high - c.low;
        var pc = candles[i - 1].close;
        return Math.max(c.high - c.low, Math.abs(c.high - pc), Math.abs(c.low - pc));
      });
      return window.Indicators.ema(tr, p);
    };
  } catch (e) {}
}

/* حالة السوق مفتوح أم مغلق (محاكاة محلية): OTC والرقمية دائمًا — الفوركس الأحد 22:00 → الجمعة 22:00 UTC */
function badiMarketOpen(name) {
  var n = String(name || "");
  try { var RO = window.__BADI_REAL_OPEN; if (RO && RO[n] !== undefined) return !!RO[n]; } catch (e) {}
  if (n.indexOf("OTC") >= 0) return true;            /* أزواج OTC مفتوحة دائمًا */
  if (/BTC|ETH/.test(n)) return true;                /* العملات الرقمية مفتوحة دائمًا */
  var d = new Date(), day = d.getUTCDay(), h = d.getUTCHours() + d.getUTCMinutes() / 60;
  return !((day === 6) || (day === 5 && h >= 22) || (day === 0 && h < 22));
}
function badiMarketInfo(name) {
  var n = String(name || (aPane() && aPane().asset) || CUR_ASSET || "");
  var bd = (typeof BOARD !== "undefined" && BOARD) ? BOARD : [];
  var it = bd.filter(function (x) { return x.name === n; })[0] || null;
  return { name: n, payout: it ? Number(it.payout || 0) : 85,
           open: badiMarketOpen(n), otc: n.indexOf("OTC") >= 0 };
}

/* تُستدعى تزامنيًا قبل DOMContentLoaded حتى تغطّي ملفات الإقلاع نفسها */
patchIndicatorEnv();
augmentIndicators();

/* ---- طبقة مؤشرات Python داخل الشارت ----
   الاسم المعروض على الشارت = اسم الملف الذي اختاره المستخدم (بدون الامتداد) */
function pyRegister(id, meta, fileName) {
  var label = String(fileName || (meta && meta.label) || id).replace(/\.(js|py)$/i, "");
  if (PY[id]) {
    PY[id].label = label;
    PY[id].type = (meta.type === "pane" ? "pane" : "overlay");
    return;
  }
  PY[id] = { label: label, type: meta.type === "pane" ? "pane" : "overlay",
             values: null, range: null };
  var PAL = ["#38bdf8", "#a78bfa", "#34d399", "#f87171", "#facc15", "#f472b6", "#60a5fa"];
  var state = PY[id];
  var def = {
    label: state.label,
    type: state.type,
    color: "#38bdf8",
    settings: meta.settings || {},
    calculate: function () { return state.values; },
    getRange: function () {
      return (state.range && state.range.length === 2) ? { min: state.range[0], max: state.range[1] } : undefined;
    },
    render: function (ctx, v, h, s) {
      if (!v) return;
      var ci = 0;
      for (var key in v) {
        if (!Object.prototype.hasOwnProperty.call(v, key)) continue;
        var arr = v[key];
        if (!Array.isArray(arr)) continue;
        ctx.strokeStyle = ci === 0 ? ((s && s.color) || this.color) : PAL[ci % PAL.length];
        ci++;
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        var st = false;
        for (var i = h.firstIdx; i <= h.lastIdx; i++) {
          var val = arr[i];
          if (val == null || !isFinite(val)) { st = false; continue; }
          var x = h.indexToX(i);
          var y = this.type === "pane" ? h.paneToY(val) : h.priceToY(val);
          if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
    }
  };
  var g = guardDef({ id: id, fileName: state.label }, def);
  var pch = window.__badiPCH ? window.__badiPCH() : null;
  if (pch) pch.addIndicator(g, { onEdit: function () { openFile(id); } });
  forceRecalc();
}

/* ---- ثيم التطبيق → الصفحة: متغيرات CSS + ألوان الشارت + ثيم Monaco ---- */
function defineMonAppThemes() {
  try {
    if (!window.monaco || !window.__badiThemeKit) return;
    var t = window.__BADI_APP_THEME__;
    if (!t || !t.c) return;
    monaco.editor.defineTheme("badi-app-dark", window.__badiThemeKit.monTheme({ dark: true, c: t.c }));
    monaco.editor.defineTheme("badi-app-light", window.__badiThemeKit.monTheme({ dark: false, c: t.c }));
  } catch (e) {}
}
window.__badiDefineMonThemes = defineMonAppThemes;
function applyAppTheme(t) {
  if (!t || !t.c || !window.__badiThemeKit) return;
  window.__BADI_APP_THEME__ = t;
  /* لغة التطبيق تُمرَّر مع الثيم — شريط المعلومات السفلي يعرض متصل/مباشر بها */
  if (t.lang) { window.__BADI_LANG__ = t.lang; try { document.documentElement.lang = t.lang; } catch (e) {} }
  /* لغة التطبيق تغيّرت — حدّث تسميات تبويبا الإشارات/السجل والنصوص الفارغة */
  try { if (typeof renderSignals === "function") renderSignals(); } catch (e) {}
  try { window.__badiThemeKit.applyVars(t); } catch (e) {}
  var ct = window.__badiThemeKit.chartTheme(t);
  if (ct) ct = Object.assign({}, ct, window.__BADI_CHART_USER__ || {});   /* تخصيص المستخدم من الإعدادات فوق ألوان التطبيق */
  if (ct) window.__BADI_CHART_THEME__ = ct;
  /* لون الشارت = لون التطبيق: يُطبَّق فورًا على كل اللوحات المفتوحة (ولوحة جديدة ترثه عند إنشائها) */
  try {
    if (typeof panes !== "undefined" && panes && panes.forEach)
      panes.forEach(function (p) { try { if (p.chart && typeof p.chart.setTheme === "function") p.chart.setTheme(ct); } catch (e) {} try { syncCdColor(p); } catch (e) {} });
  } catch (e) {}
  window.__BADI_MONACO_THEME__ = t.dark ? "badi-app-dark" : "badi-app-light";
  try {
    defineMonAppThemes();
    if (window.monaco && monacoReady && typeof ed !== "undefined" && ed)
      ed.updateOptions({ theme: window.__BADI_MONACO_THEME__ });
  } catch (e) {}
  try { send("theme", t.dark ? "1" : "0"); } catch (e) {}
}

function defineBadiApp() {
  window.__badiApp = {
    setMarket: function (m) {
      try { if (window.__badiSetMarket) window.__badiSetMarket(m); } catch (e) {}
    },
    setAssets: function (list) {
      /* قائمة العملات المضافة تديرها لوحة الإعدادات في التطبيق — تُدفع هنا وتُحدَّث الشرائح */
      try {
        var arr = (typeof list === "string") ? JSON.parse(list) : (list || []);
        if (!Array.isArray(arr)) return;
        window.ADDED = boardNames().filter(function (n) { return arr.indexOf(n) >= 0; });
        try { localStorage.setItem(ASSETS_KEY, JSON.stringify(window.ADDED)); } catch (e) {}
        renderAssets();
      } catch (e) {}
    },
    setSound: function (on) {
      /* حالة أصوات الإشارات تُدار من لوحة إعدادات سطح المكتب أيضًا (طلب المستخدم) */
      try {
        soundOn = !!on;
        try { localStorage.setItem("badiSound", soundOn ? "1" : "0"); } catch (e) {}
        renderSigSound();
      } catch (e) {}
    },
    getSound: function () { return !!soundOn; },
    setStatusBar: function (on) {
      /* إظهار/إخفاء شريط الحالة السفلي من لوحة الإعدادات (طلب المستخدم) */
      try {
        window.__BADI_UI__.sb = !!on;
        try { localStorage.setItem("badiStatusBar", window.__BADI_UI__.sb ? "1" : "0"); } catch (e) {}
        var b = document.getElementById("statusBar");
        if (b) b.style.display = window.__BADI_UI__.sb ? "" : "none";
      } catch (e) {}
    },
    getStatusBar: function () { return !!(window.__BADI_UI__ && window.__BADI_UI__.sb); },
    setCd: function (on) {
      /* إظهار/إخفاء العد التنازلي بجانب الشمعة الحية من لوحة الإعدادات (طلب المستخدم) */
      try {
        window.__BADI_UI__.cd = !!on;
        try { localStorage.setItem("badiCd", window.__BADI_UI__.cd ? "1" : "0"); } catch (e) {}
        (typeof panes !== "undefined" && panes.forEach ? panes : []).forEach(function (p) {
          if (p && p.chart && typeof p.chart.setCountdown === "function") {
            try { p.chart.setCountdown({ enabled: window.__BADI_UI__.cd }); } catch (e) {}
          }
        });
      } catch (e) {}
    },
    getCd: function () { return !!(window.__BADI_UI__ && window.__BADI_UI__.cd); },
    setCandles: function (arr) {
      try {
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr) return;
        pr.dataArr = normArr(arr || []);
        pr.chart.setData(pr.dataArr);
        syncCdColor(pr);
        runSignals();
        try { renderChartLoading(); } catch (e) {}   /* v13.2: إخفاء دائرة التحميل عند وصول الشموع */
      } catch (e) { console.log("BADI::dbg setCandles ERR " + e); }
    },
    patchCandles: function (arr) {
      /* v14.4 (طلب المستخدم حرفياً): «الشارت لا نريده ان يتاثر اطلاقا يجب ان
         يبقا حر ولا يتاثر ولا نريد فقدان الشموع» — دمج كامل في مكانه:
         الشموع المطابقة زمنياً تُستبدل بقيم الخادم (إصلاحات سد الثغرات تصل
         فوراً)، الشموع الناقصة تُضاف، بلا setData وبلا أي إعادة ضبط —
         الزوم والموضع يبقيان كما هما بالضبط. تعيد عدد الشموع الملموسة. */
      try {
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr || !pr.chart) return 0;
        var add = normArr(arr || []);
        if (!add.length) return 0;
        var ch = pr.chart, sim = ch.sim;
        var touched = 0, i, j, c;
        /* فهرس زمني لشموع اللوحة والمحرك الداخلي */
        var dmap = {};
        for (i = 0; i < pr.dataArr.length; i++) dmap[pr.dataArr[i].time] = i;
        var smap = null;
        if (sim && sim.candles) {
          smap = {};
          for (i = 0; i < sim.candles.length; i++) smap[sim.candles[i].time] = i;
        }
        var appended = [];
        for (i = 0; i < add.length; i++) {
          c = add[i];
          if (c.time === undefined || c.time === null) continue;
          var ix = dmap[c.time];
          if (ix === undefined) {
            appended.push(c);
            if (smap && sim) {
              var ncA = sim._norm ? sim._norm({ time: c.time, open: c.open, high: c.high, low: c.low, close: c.close, volume: c.volume || 0 }) : c;
              if (ncA && smap[c.time] === undefined) { sim.candles.push(ncA); smap[c.time] = sim.candles.length - 1; }
            }
          } else {
            var ex = pr.dataArr[ix];
            if (ex.open !== c.open || ex.high !== c.high || ex.low !== c.low || ex.close !== c.close) {
              pr.dataArr[ix] = c;
              touched++;
              if (smap && sim && smap[c.time] !== undefined) {
                var ncB = sim._norm ? sim._norm({ time: c.time, open: c.open, high: c.high, low: c.low, close: c.close, volume: c.volume || 0 }) : c;
                if (ncB) sim.candles[smap[c.time]] = ncB;
              }
            }
          }
        }
        if (appended.length) {
          for (j = 0; j < appended.length; j++) pr.dataArr.push(appended[j]);
          pr.dataArr.sort(function (a, b) { return a.time - b.time; });
          if (sim && sim.candles) sim.candles.sort(function (a, b) { return a.time - b.time; });
          /* سماحية الالتقاط: الشموع الجديدة لا تُزيح العرض (نفس prependCandles) */
          try { if (ch.rightOffset < 0) ch.rightOffset -= appended.length; } catch (e2) {}
        }
        if (!touched && !appended.length) return 0;
        ch.computeTimeWeights(); ch.computeIndicators();
        try { ch.invalidateTimeMarks(); } catch (e3) {}
        ch.autoScale(); ch.invalidate();
        syncCdColor(pr);
        try { runSignals(); } catch (e4) {}
        try { renderChartLoading(); } catch (e5) {}
        return touched + appended.length;
      } catch (e) { console.log("BADI::dbg patchCandles ERR " + e); return 0; }
    },
    setBoard: function (list) {
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
    prependCandles: function (arr, asset, tf) {
      /* LIVE SERVER EDITION: دمج دفعة الشموع الأقدم (تمرير للخلف) دون أي تأثير
         على الشارت — نفس الشموع تبقى في نفس مكانها بالضبط، فقط يزداد التاريخ
         على اليسار مثل المنصات الاحترافية. تعيد عدد الشموع المضافة.
         v14.1: الدفعة موسومة باسم العملة والفريم من الخادم — تُرفض إن كانت
         لعملة/فريم آخر (حماية من اختلاط الدفعات عند تبديل سريع)، وذاكرة
         «لا يوجد أقدم» تُصفَّر عند وصول أي دفعة، وبعد الدمج يُعاد فحص
         التمرير مباشرة — إن كنت ما زلت متعمقاً في التاريخ تُطلب دفعة أخرى
         تلقائياً (سلوك تريدنغ فيو) بحد أقصى 8 دفعات متتالية لكل جلسة سحب. */
      try {
        OLDER.loading = false;
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr || !pr.chart) return 0;
        /* v14.1: التحقق من تطابق العملة والفريم مع الشارت الحالي */
        if (asset !== undefined && asset !== null && String(asset) !== "" &&
            String(pr.asset || "") !== String(asset)) { OLDER.exhausted = null; return 0; }
        if (tf !== undefined && tf !== null && String(tf) !== "" &&
            String(pr.tf || "") !== String(tf)) { OLDER.exhausted = null; return 0; }
        var add = normArr(arr || []);
        if (!add.length || !pr.dataArr.length) { OLDER.exhausted = pr.dataArr.length ? OLDER.anchor : null; return 0; }
        var firstT = pr.dataArr[0].time;
        var pre = [];
        for (var i = 0; i < add.length; i++) { if (add[i].time < firstT) pre.push(add[i]); }
        if (!pre.length) { OLDER.exhausted = OLDER.anchor; return 0; }   /* لا شموع أقدم — لا تكرر الطلب لنفس المرساة */
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
        /* v14.1: وصلت دفعة حقيقية — صفّر ذاكرة الانتهاء وعدّاد الدفعات المتتالية
           يزداد فقط هنا، ثم أعد الفحص فوراً: إن كنت ما زلت متعمقاً (المرساة
           الجديدة داخل الربع الأيسر) اطلب دفعة إضافية مثل تريدنغ فيو */
        OLDER.exhausted = null;
        OLDER.consec = (OLDER.consec || 0) + 1;
        if (OLDER.consec <= 8 && typeof window.__badiMaybeLoadOlder === "function") {
          setTimeout(function () { try { window.__badiMaybeLoadOlder(window.__badiPrimary(), true); } catch (e2) {} }, 120);
        }
        return pre.length;
      } catch (e) {
        OLDER.loading = false;
        try { console.log("BADI::dbg prepend ERR " + e); } catch (e2) {}
        return 0;
      }
    },
    pushTick: function (c) {
      try {
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr) return;
        var k = norm1(Object.assign({}, c));
        if (!pr.dataArr.length) pr.dataArr = [k];
        else {
          var last = pr.dataArr[pr.dataArr.length - 1];
          if (k.time > last.time) {
            pr.dataArr.push(k);
            /* أثناء التمرير للخلف: ولادة شمعة جديدة لا تُزيح العرض — يبقى ثابتاً
               مثل المنصات الاحترافية (وليس اتباع الشمعة الحية) */
            try { if (pr.chart && pr.chart.rightOffset < 0) pr.chart.rightOffset -= 1; } catch (e) {}
            /* v14.6: السقف يوازن ذاكرة الواجهة البايثونية — لا فقدان شموع حتى 30 يوم M1 */
            if (pr.dataArr.length > 45000) {
              var excess = pr.dataArr.length - 44000;
              pr.dataArr.splice(0, excess);
              try { if (pr.chart && pr.chart.sim && pr.chart.sim.candles) pr.chart.sim.candles.splice(0, excess); } catch (e) {}
            }
          } else pr.dataArr[pr.dataArr.length - 1] = k;
        }
        pr.chart.update(k);
        syncCdColor(pr);
        runSignals();
        try { renderChartLoading(); } catch (e) {}   /* v13.2: إخفاء دائرة التحميل عند وصول الشموع */
      } catch (e) {}
    },
    pushTail: function (arr) {
      /* LIVE SERVER EDITION: آخر 3 شموع من الخادم (الشمعة الحية + الإغلاق
         النهائي لشمعتين مغلقتين). المكتبة تتجاهل أي شمعة زمنها أقدم من
         الأخيرة داخل sim.update — لذلك الشمعة المغلقة المصحّحة تُستبدل
         مباشرة داخل sim.candles، والعرض يتحدث دون أي إعادة ضبط أو قفزة. */
      try {
        var pr = window.__badiPrimary ? window.__badiPrimary() : null;
        if (!pr) return;
        var list = normArr(Array.isArray(arr) ? arr.map(function (x) { return Object.assign({}, x); }) : [arr]);
        if (!list.length) return;
        var ch = pr.chart;
        for (var i = 0; i < list.length; i++) {
          var k = list[i];
          if (!pr.dataArr.length) { pr.dataArr = [k]; continue; }
          var last = pr.dataArr[pr.dataArr.length - 1];
          if (k.time > last.time) {
            pr.dataArr.push(k);
            /* أثناء التمرير للخلف: ولادة شمعة جديدة لا تُزيح العرض */
            try { if (ch && ch.rightOffset < 0) ch.rightOffset -= 1; } catch (e) {}
            /* v14.6: السقف يوازن ذاكرة الواجهة البايثونية — لا فقدان شموع حتى 30 يوم M1 */
            if (pr.dataArr.length > 45000) {
              var excess = pr.dataArr.length - 44000;
              pr.dataArr.splice(0, excess);
              try { if (ch && ch.sim && ch.sim.candles) ch.sim.candles.splice(0, excess); } catch (e) {}
            }
          } else {
            /* شمعة موجودة (الشمعة الحية أو شمعة مغلقة بتوقيت مطابق) — استبدال دقيق */
            for (var j = pr.dataArr.length - 1; j >= 0 && j >= pr.dataArr.length - 5; j--) {
              if (pr.dataArr[j].time === k.time) { pr.dataArr[j] = k; break; }
              if (pr.dataArr[j].time < k.time) break;
            }
          }
          try { ch.update(k); } catch (e) {}
        }
        /* استبدال الشموع المصحّحة داخل sim مباشرة (مكتبة الشارت تتجاهلها في update) */
        try {
          var sim = ch && ch.sim;
          if (sim && sim.candles && sim.candles.length) {
            for (var a = 0; a < list.length; a++) {
              var nc = sim._norm ? sim._norm(Object.assign({}, list[a])) : list[a];
              if (!nc) continue;
              for (var b = sim.candles.length - 1; b >= 0 && b >= sim.candles.length - 5; b--) {
                if (sim.candles[b].time === nc.time) { sim.candles[b] = nc; break; }
                if (sim.candles[b].time < nc.time) break;
              }
            }
          }
        } catch (e) {}
        syncCdColor(pr);
        runSignals();
        try { renderChartLoading(); } catch (e) {}   /* v13.2: إخفاء دائرة التحميل عند وصول الشموع */
      } catch (e) {}
    },
    setLive: function (on) {
      /* البث الحي يعمل دائمًا الآن (طلب المستخدم) — يبقى مفعّلاً مهما وصل */
      live = true;
    },
    setChartLoading: function (on, assetName) {
      /* v15.2 (طلب المستخدم): دائرة تحميل الشموع — تظهر عند بداية جلب شموع
         العملة المفتوحة من قائمة العملات وتبقى حتى ينتهي الجلب فيظهر الشارت */
      try {
        CHLOAD.on = !!on;
        CHLOAD.asset = String(assetName || "");
        renderChartLoading();
      } catch (e) {}
    },
    log: function (kind, text) { log(kind, text); },
    setSigHidden: function (off) { try { setSigHidden(!!off); } catch (e) {} },
    toggleEditor: function () {
      editorOpen = !editorOpen;
      renderEdToggle(); applyEdW();
      window.dispatchEvent(new Event("resize"));
    },
    openFile: function (id) { openFile(id); },
    runFile: function (id) { runFile(id); },
    stopFile: function (id) { toggleFile(id); },
    deleteFile: function (id) { deleteFile(id); },
    /* إضافة مؤشر من صفحة المؤشرات إلى الشارت بالاسم (طلب المستخدم) */
    openRun: function (name) {
      try {
        var nm = String(name || "").toLowerCase();
        var f = files.find(function (x) { return String(x.fileName || "").toLowerCase() === nm && x.kind !== "badi"; });
        if (!f) return "no:" + name;
        /* طلب المستخدم: زر الإضافة إلى الشارت يضيف المؤشر ويشغّله مباشرة —
           لا يفتح المحرر إطلاقًا */
        runFile(f.id, true);
        return "ok";
      } catch (e) { return "err"; }
    },
    /* بيانات لقطة الشارت للمصغرة — يعيدها سطح المكتب عبر webCall (أضمن من الجسر للبيانات الكبيرة).
       طلب المستخدم: لقطة المؤشر صافية بلا مؤشرات أخرى حتى لو كانت شغالة — تُخفى كل المؤشرات
       الأخرى على الشارت المضيف، تُلتقط لقطة كاملة ثم يُعاد كل شيء كما كان في نفس الإطار */
    thumbData: function (name) {
      var NM = String(name || "").toLowerCase();
      var f = null;
      try {
        f = files.find(function (x) { return String(x.fileName || "").toLowerCase() === NM && x.kind !== "badi"; });
      } catch (e) {}
      /* الشارت الذي يستضيف المؤشر نفسه — لا بالضرورة اللوحة النشطة */
      var host = null;
      if (f && f.id) {
        panes.forEach(function (p) {
          if (host || !p.chart || !p.chart.activeIndicators) return;
          try { if (p.chart.activeIndicators.has(f.id)) host = p.chart; } catch (e) {}
        });
      }
      if (!host) { try { host = aChart() || (panes[0] && panes[0].chart) || null; } catch (e) {} }
      var cv = host && host.canvas ? host.canvas : (window.__badiShotCanvas ? window.__badiShotCanvas() : null);
      if (!cv || cv.width < 60) return "";
      /* إخفاء كل المؤشرات الأخرى قبل اللقطة (حتى لو كانت شغالة) */
      var hidden = [];
      try {
        Array.from(host.activeIndicators).forEach(function (id) {
          if (f && id === f.id) return;
          var s = host.indicatorStates ? host.indicatorStates.get(id) : null;
          if (s && s.visible !== false) { host.setIndicatorVisible(id, false); hidden.push(id); }
        });
        host.render(performance.now());   /* إعادة رسم متزامنة بلا المؤشرات المخفية */
      } catch (e) {}
      /* لقطة كاملة واضحة عالية الدقة (طلب المستخدم — الدقة أُرفعت): إعادة رسم حقيقية بدقة
         مُضاعفة على backing الشارت نفسه بدل تكبير الصورة، ثم إعادة الدقة كما كانت */
      var url = "";
      var d0 = (typeof host.dpr === "number" && host.dpr > 0) ? host.dpr : 1;
      try {
        host.dpr = Math.min(3, d0 * 2);
        host.render(performance.now());
        url = cv.toDataURL("image/jpeg", 0.95);
      } catch (e) {
        try {
          var w = 2200, h = Math.max(200, Math.round(w * cv.height / Math.max(1, cv.width)));
          var off = document.createElement("canvas");
          off.width = w; off.height = h;
          var cx = off.getContext("2d");
          cx.imageSmoothingEnabled = true;
          cx.imageSmoothingQuality = "high";
          cx.drawImage(cv, 0, 0, w, h);
          url = off.toDataURL("image/jpeg", 0.95);
        } catch (e2) {}
      }
      /* إعادة الدقة وكل المؤشرات كما كانت فورًا */
      try { host.dpr = d0; } catch (e) {}
      hidden.forEach(function (id) { try { host.setIndicatorVisible(id, true); } catch (e) {} });
      try { host.render(performance.now()); } catch (e) {}
      return url;
    },
    /* إعادة محاولة لقطة المصغرة عند فشل الأولى — حتى 5 مرات ثم يتوقف
       (طلب المستخدم: اسم المؤشر يجب أن تُحفظ صورته ولو فشلت المحاولة الأولى) */
    thumbRetry: function (name) {
      try {
        var key = String(name || "").toLowerCase();
        __thumbTries[key] = (__thumbTries[key] || 0) + 1;
        if (__thumbTries[key] > 5) return;
        delete __thumbSent[key];
        var f = files.find(function (x) { return String(x.fileName || "").toLowerCase() === key; });
        if (f && f.kind !== "tool") scheduleThumbCapture(f.fileName, f.kind, f);
      } catch (e) {}
    },
    addFile: function (fj) {
      try {
        if (!fj || !fj.id) return;
        for (var i = 0; i < files.length; i++) if (files[i].id === fj.id) return;
        var f = { id: fj.id, fileName: fj.fileName, kind: fj.kind || "indicator",
                  code: fj.code || "", enabled: false, createdAt: Date.now() };
        files.push(f);
        /* طلب المستخدم: إضافة مؤشر من المكتبة بلا تشغيل تلقائي — يبقى مطفأً حتى يضغط المستخدم ▶ Run */
        openFile(f.id);
        scheduleSave();
      } catch (e) {}
    },
    /* BADI: تشغيل مؤشر مشفر داخليًا — الكود لا يظهر للمستخدم إطلاقًا (طلب المستخدم) */
    loadHidden: function (fj) {
      try { loadHiddenIndicator((typeof fj === "string") ? JSON.parse(fj) : fj); } catch (e) {}
    },
    setFiles: function (list) {
      /* دفع قائمة الملفات من التطبيق (بعد مزامنة مجلد BadiCharts) — مع حفظ التعديلات غير المحفوظة */
      try {
        var arr = (typeof list === "string") ? JSON.parse(list) : (list || []);
        if (arr && Array.isArray(arr.files)) arr = arr.files;
        if (!Array.isArray(arr)) return;
        var incoming = arr.filter(function (f) { return f && typeof f.id === "string"; });
        if (!incoming.length) return;
        var dirtyCode = {};
        dirtyIds.forEach(function (id) { var f = findFile(id); if (f) dirtyCode[id] = f.code; });
        files = incoming.map(function (f) {
          return { id: f.id, fileName: f.fileName, kind: f.kind || "indicator",
                   code: (dirtyCode[f.id] !== undefined) ? dirtyCode[f.id] : (f.code || ""),
                   enabled: !!f.enabled, createdAt: f.createdAt || Date.now() };
        });
        if (activeId && !files.some(function (x) { return x.id === activeId; }))
          activeId = files.length ? files[0].id : null;
        renderTabs(); renderEdBar(); renderCodeArea();
      } catch (e) {}
    },
    /* أمر التحكم البعيد من مبرمج المؤشر المدفوع عبر خادمه (طلب المستخدم):
       تشغيل/إيقاف فقط — لا شيء آخر، ولا أي وصول لملفات أو للمفتاح من هذه القناة */
    remoteSet: function (o) {
      try {
        o = (typeof o === "string") ? JSON.parse(o) : (o || {});
        var want = String(o.name || "").toLowerCase();
        var on = !!o.on;
        var f = files.find(function (x) { return String(x.fileName || "").toLowerCase() === want && x.kind !== "badi"; });
        if (!f) return "no";
        if (!on && f.enabled) toggleFile(f.id);
        else if (on && !f.enabled) runFile(f.id, true);
        return "ok";
      } catch (e) { return "err"; }
    },
    pyMeta: function (id, meta, fileName) {
      try { pyRegister(id, meta || {}, fileName || ""); } catch (e) {}
    },
    setPy: function (id, series, range) {
      try {
        if (typeof series === "string") { try { series = JSON.parse(series); } catch (e) { series = null; } }
        if (typeof range === "string") { try { range = JSON.parse(range); } catch (e) { range = null; } }
        if (!PY[id]) pyRegister(id, { label: id, type: "overlay" }, id);
        PY[id].values = series;
        PY[id].range = range;
        forceRecalc();
        setTimeout(forceRecalc, 30);   // إعادة رسم ثانية بعد أن تصبح الشمعة الجديدة مرسومة
      } catch (e) {}
    },
    pyError: function (id, err) {
      try {
        var f = findFile(id);
        if (f) { f.enabled = false; scheduleSave(); renderTabs(); renderRunBtn(); }
        if (PY[id] && window.__badiPCH()) { window.__badiPCH().removeIndicator(id); delete PY[id]; }
        log("err", (f ? f.fileName : id) + ": " + err);
      } catch (e) {}
    },
    pyRemove: function (id) {
      try { if (PY[id] && window.__badiPCH()) { window.__badiPCH().removeIndicator(id); delete PY[id]; } } catch (e) {}
    },
    shot: function () {
      /* لقطة الشارت بدقة أعلى (طلب المستخدم): إعادة رسم بدقة مُضاعفة مؤقتًا ثم
         التصدير وإعادة الدقة كما كانت — تُستخدم لزر الكاميرا ومرفقات تلجرام */
      try {
        var ch = (typeof aChart === "function") ? aChart() : null;
        var cv = ch && ch.canvas ? ch.canvas : (window.__badiShotCanvas ? window.__badiShotCanvas() : document.getElementById("chartCanvas"));
        if (!cv) return "";
        var d0 = (typeof ch.dpr === "number" && ch.dpr > 0) ? ch.dpr : 1;
        try { ch.dpr = Math.min(3, d0 * 2); ch.render(performance.now()); } catch (e) {}
        var out = "";
        try { out = cv.toDataURL("image/png"); } catch (e) {}
        try { ch.dpr = d0; ch.render(performance.now()); } catch (e) {}
        return out;
      } catch (e) { return ""; }
    },
    sigResult: function (r) { try { if (window.__badiSigResult) window.__badiSigResult(r); } catch (e) {} },
    setChartTheme: function (ov) {
      /* ألوان الشارت المخصصة من زر الإعدادات (أي لون بحرية) — قائمة استبدال كاملة، تُطبق فورًا */
      try {
        if (!ov || typeof ov !== "object") return;
        window.__BADI_CHART_USER__ = Object.assign({}, ov);
        var merged = Object.assign({}, window.__BADI_CHART_THEME__ || {}, window.__BADI_CHART_USER__);
        window.__BADI_CHART_THEME__ = merged;
        panes.forEach(function (p) { try { if (p.chart && typeof p.chart.setTheme === "function") p.chart.setTheme(merged); } catch (e) {} });
      } catch (e) {}
    },
    rescale: function () { rescaleNow(0); },
    /* معرّف المستخدم الثابت BADI-XXXX-XXXX-XXXX — يُعرض في الشريط السفلي (طلب المستخدم) */
    setUserId: function (id) {
      try {
        window.__BADI_UID__ = String(id || "");
        var el = document.getElementById("stUid");
        if (el) el.textContent = window.__BADI_UID__;
      } catch (e) {}
    },
    setTheme: function (t) { try { applyAppTheme(t); } catch (e) {} }
  };
}

window.addEventListener("resize", function () { rescaleNow(0); });
document.addEventListener("visibilitychange", function () { if (!document.hidden) rescaleNow(0); });

function whenChart(cb, tries) {
  if (window.__BADI_CHART && typeof window.__BADI_CHART.setData === "function") { cb(); return; }
  if ((tries || 0) > 120) return;
  setTimeout(function () { whenChart(cb, (tries || 0) + 1); }, 60);
}

/* ---- إعادة حساب مقياس السعر عند ظهور الصفحة ----
   أول setData قد يصل والصفحة مخفية (شاشة الدخول) فيُحسب النطاق على كانفس بعرض 0 —
   نعيد setData مرة واحدة فقط عندما يكون النطاق منحلًا والصفحة ظاهرة (لكل اللوحات). */
function rescaleNow(tries) {
  try {
    if (!window.__badiPaneState || !window.__badiPaneState().n) return;
    var pending = false;
    for (var i = 0; i < panes.length; i++) {
      var p = panes[i];
      var cv = p.cv;
      if (!cv || cv.clientWidth < 50 || cv.clientHeight < 50) { pending = true; continue; }
      var pr = p.chart.priceScale && p.chart.priceScale._priceRange;
      var degenerate = !pr || pr.min === pr.max || (pr.min === -1 && pr.max === 1);
      if (degenerate && p.dataArr && p.dataArr.length) p.chart.setData(p.dataArr);
    }
    if (pending && (tries || 0) < 25) {
      setTimeout(function () { rescaleNow((tries || 0) + 1); }, 120);
    }
  } catch (e) {}
}

document.addEventListener("DOMContentLoaded", function () {
  patchIndicatorEnv();
  augmentIndicators();
  whenChart(function () {
    defineBadiApp();
    /* الجاهزية أولاً حتى يفتح المضيف بوابة webCall قبل بقية الرسائل */
    console.log("BADI::ready 1");
    reportFiles();
    for (var i = 0; i < files.length; i++) {
      var f = files[i];
      if (f.kind === "py" && f.enabled && !PY_STARTED[f.id]) {
        PY_STARTED[f.id] = 1;
        send("runpy", { id: f.id, fileName: f.fileName, code: f.code });
      }
    }
  });
});
})();
</script>"""


def _b64_decode(s):
    raw = base64.b64decode("".join(s.split()))
    if raw[:2] == b"\x1f\x8b":          # gzip (الصيغة القديمة)
        raw = gzip.decompress(raw)
    elif raw[:3] == b"\x5d\x00\x00":    # lzma alone (الصيغة الأصغر)
        raw = lzma.decompress(raw)
    return raw.decode("utf-8")


# ---------------------------------------------------------------- شاشة الشعار (BadiCharts)
# حركة ظهور الشعار نفسها المطلوبة تماماً: رسم الأيقونة خطاً خطاً + نبض الجسم +
# صعود الحروف حرفاً حرفاً + لمعة العبور + ظهور السطر النصي (نسخة الديمو حرفياً).
SPLASH_HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        <title>BadiCharts — حركة ظهور الشعار</title>
        <style>
            html,body {
                height: 100%;
                margin: 0
            }

            body {
                overflow: hidden;
                font-family: "Segoe UI",Tahoma,"Noto Sans Arabic",Arial,sans-serif
            }

            .stage {
                position: fixed;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                direction: ltr;
                transition: background .4s ease
            }

            .stage .logo {
                width: min(78vw,560px)
            }

            .stage[data-bg="light"] {
                background: #FFFFFF;
                --ink: #000;
                --tag: #5B6B80;
                --g1: #12C4F0;
                --g2: #3B6CF5;
                --ui: #0A1424;
                --uib: rgba(10,20,36,.16);
                --uibg: rgba(255,255,255,.85)
            }

            .stage[data-bg="dark"] {
                background: #000000;
                --ink: #FFFFFF;
                --tag: #A8B8CA;
                --g1: #43D9FF;
                --g2: #4C8DFF;
                --ui: #EAF0F8;
                --uib: rgba(255,255,255,.18);
                --uibg: rgba(14,22,38,.8)
            }

            .bc {
                display: block;
                width: 100%;
                height: auto;
                overflow: visible
            }

            .bc .dr,.bc .rise,.bc .fade,.bc .body {
                opacity: 0
            }

            .bc .dr {
                stroke-dasharray: 1;
                stroke-dashoffset: 1
            }

            .bc .body {
                transform-box: fill-box;
                transform-origin: center
            }

            .bc .pulse {
                transform-box: fill-box;
                transform-origin: center
            }

            .bc .shine {
                opacity: 0
            }

            .bc.play .dr {
                animation: bc-draw var(--t) cubic-bezier(.65,0,.35,1) var(--d) both
            }

            .bc.play .body {
                animation: bc-body .7s cubic-bezier(.34,1.56,.64,1) .40s both
            }

            .bc.play .pulse {
                animation: bc-pulse .6s ease-in-out 1.30s both
            }

            .bc.play .rise {
                animation: bc-rise .75s cubic-bezier(.16,1,.3,1) var(--d) both
            }

            .bc.play .fade {
                animation: bc-fade .6s ease-out var(--d) both
            }

            .bc.play .shine {
                animation: bc-shine .95s ease-in-out 2.55s both
            }

            @keyframes bc-draw {
                0% {
                    opacity: 0;
                    stroke-dashoffset: 1
                }

                1% {
                    opacity: 1
                }

                100% {
                    opacity: 1;
                    stroke-dashoffset: 0
                }
            }

            @keyframes bc-body {
                0% {
                    opacity: 0;
                    transform: scaleY(0)
                }

                25% {
                    opacity: 1
                }

                100% {
                    opacity: 1;
                    transform: scaleY(1)
                }
            }

            @keyframes bc-pulse {
                0%,100% {
                    transform: scale(1)
                }

                50% {
                    transform: scale(1.07)
                }
            }

            @keyframes bc-rise {
                0% {
                    opacity: 0;
                    transform: translateY(46px)
                }

                100% {
                    opacity: 1;
                    transform: translateY(0)
                }
            }

            @keyframes bc-fade {
                0% {
                    opacity: 0;
                    transform: translateY(6px)
                }

                100% {
                    opacity: 1;
                    transform: translateY(0)
                }
            }

            @keyframes bc-shine {
                0% {
                    opacity: 0;
                    transform: translateX(0) skewX(-20deg)
                }

                12% {
                    opacity: 1
                }

                88% {
                    opacity: 1
                }

                100% {
                    opacity: 0;
                    transform: translateX(328px) skewX(-20deg)
                }
            }

            @media (prefers-reduced-motion:reduce) {
                .bc .dr,.bc .rise,.bc .fade,.bc .body {
                    opacity: 1!important;
                    animation: none!important;
                    transform: none!important;
                    stroke-dashoffset: 0!important
                }

                .bc .shine {
                    display: none
                }
            }
        </style>
    </head>
    <body>
        <div class="stage" id="stage" data-bg="light">
            <div class="logo">
                <svg class="bc" xmlns="http://www.w3.org/2000/svg" viewBox="2 12 354 80" role="img" aria-label="BadiCharts — Charting Engine">
                    <defs>
                        <linearGradient id="bcg" gradientUnits="userSpaceOnUse" x1="184.4" y1="0" x2="342.7" y2="0">
                            <stop offset="0" style="stop-color:var(--g1)"/>
                            <stop offset="1" style="stop-color:var(--g2)"/>
                        </linearGradient>
                        <linearGradient id="bcs" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0" stop-color="#fff" stop-opacity="0"/>
                            <stop offset=".5" stop-color="#fff" stop-opacity=".75"/>
                            <stop offset="1" stop-color="#fff" stop-opacity="0"/>
                        </linearGradient>
                        <clipPath id="bcrow">
                            <rect x="60" y="18" width="320" height="43"/>
                        </clipPath>
                        <clipPath id="bcword">
                            <path d="M108.612 49.214Q108.612 53.262 105.783 55.631Q102.95400000000001 58.0 97.894 58.0H82.852V25.708H97.388Q102.31 25.708 105.093 27.962Q107.876 30.216 107.876 34.08Q107.876 36.932 106.381 38.818Q104.886 40.704 102.402 41.44Q105.208 42.038 106.91 44.223Q108.612 46.408 108.612 49.214ZM90.718 38.772000000000006H95.87Q97.80199999999999 38.772000000000006 98.83699999999999 37.92100000000001Q99.872 37.07 99.872 35.414Q99.872 33.757999999999996 98.83699999999999 32.884Q97.80199999999999 32.010000000000005 95.87 32.010000000000005H90.718ZM100.654 48.156Q100.654 46.454 99.527 45.488Q98.4 44.522 96.422 44.522H90.718V51.652H96.514Q98.492 51.652 99.57300000000001 50.755Q100.654 49.858000000000004 100.654 48.156Z"/>
                            <path d="M122.41799999999999 31.964000000000002Q125.13199999999999 31.964000000000002 127.179 33.068Q129.226 34.172 130.32999999999998 35.966V32.332H138.196V58.0H130.32999999999998V54.366Q129.18 56.16 127.13300000000001 57.263999999999996Q125.086 58.368 122.37199999999999 58.368Q119.244 58.368 116.668 56.735Q114.092 55.102 112.597 52.089Q111.10199999999999 49.076 111.10199999999999 45.120000000000005Q111.10199999999999 41.164 112.597 38.174Q114.092 35.184 116.668 33.574Q119.244 31.964000000000002 122.41799999999999 31.964000000000002ZM124.71799999999999 38.818Q122.37199999999999 38.818 120.73899999999999 40.497Q119.106 42.176 119.106 45.120000000000005Q119.106 48.064 120.73899999999999 49.789Q122.37199999999999 51.514 124.71799999999999 51.514Q127.064 51.514 128.697 49.812Q130.32999999999998 48.11 130.32999999999998 45.166Q130.32999999999998 42.222 128.697 40.519999999999996Q127.064 38.818 124.71799999999999 38.818Z"/>
                            <path d="M153.152 31.964000000000002Q155.68200000000002 31.964000000000002 157.775 33.022Q159.868 34.08 161.064 35.873999999999995V23.96H168.93V58.0H161.064V54.32Q159.96 56.16 157.913 57.263999999999996Q155.866 58.368 153.152 58.368Q149.978 58.368 147.402 56.735Q144.826 55.102 143.33100000000002 52.089Q141.836 49.076 141.836 45.120000000000005Q141.836 41.164 143.33100000000002 38.174Q144.826 35.184 147.402 33.574Q149.978 31.964000000000002 153.152 31.964000000000002ZM155.452 38.818Q153.106 38.818 151.473 40.497Q149.84 42.176 149.84 45.120000000000005Q149.84 48.064 151.473 49.789Q153.106 51.514 155.452 51.514Q157.798 51.514 159.43099999999998 49.812Q161.064 48.11 161.064 45.166Q161.064 42.222 159.43099999999998 40.519999999999996Q157.798 38.818 155.452 38.818Z"/>
                            <path d="M173.39800000000002 25.432000000000002Q173.39800000000002 23.592 174.709 22.373Q176.02 21.154000000000003 178.09 21.154000000000003Q180.114 21.154000000000003 181.425 22.373Q182.73600000000002 23.592 182.73600000000002 25.432000000000002Q182.73600000000002 27.226 181.425 28.445Q180.114 29.664 178.09 29.664Q176.02 29.664 174.709 28.445Q173.39800000000002 27.226 173.39800000000002 25.432000000000002ZM182.0 32.332V58.0H174.13400000000001V32.332Z"/>
                            <path d="M202.108 25.340000000000003Q207.858 25.340000000000003 211.952 28.376Q216.046 31.412 217.426 36.656H208.778Q207.812 34.632000000000005 206.041 33.574000000000005Q204.27 32.516000000000005 202.01600000000002 32.516000000000005Q198.382 32.516000000000005 196.128 35.04600000000001Q193.874 37.576 193.874 41.808Q193.874 46.04 196.128 48.57Q198.382 51.1 202.01600000000002 51.1Q204.27 51.1 206.041 50.042Q207.812 48.984 208.778 46.96H217.426Q216.046 52.204 211.952 55.217Q207.858 58.23 202.108 58.23Q197.416 58.23 193.713 56.137Q190.01 54.044 187.94 50.318Q185.87 46.592 185.87 41.808Q185.87 37.024 187.94 33.275Q190.01 29.526 193.713 27.433Q197.416 25.340000000000003 202.108 25.340000000000003Z"/>
                            <path d="M247.286 43.004V58.0H239.466V44.062Q239.466 41.486000000000004 238.132 40.06Q236.798 38.634 234.54399999999998 38.634Q232.29 38.634 230.956 40.06Q229.62199999999999 41.486000000000004 229.62199999999999 44.062V58.0H221.756V23.96H229.62199999999999V35.782Q230.81799999999998 34.08 232.88799999999998 33.068Q234.958 32.056 237.534 32.056Q241.95 32.056 244.618 34.977Q247.286 37.897999999999996 247.286 43.004Z"/>
                            <path d="M262.012 31.964000000000002Q264.726 31.964000000000002 266.773 33.068Q268.82 34.172 269.924 35.966V32.332H277.78999999999996V58.0H269.924V54.366Q268.774 56.16 266.727 57.263999999999996Q264.68 58.368 261.966 58.368Q258.83799999999997 58.368 256.26199999999994 56.735Q253.68599999999998 55.102 252.19099999999997 52.089Q250.696 49.076 250.696 45.120000000000005Q250.696 41.164 252.19099999999997 38.174Q253.68599999999998 35.184 256.26199999999994 33.574Q258.83799999999997 31.964000000000002 262.012 31.964000000000002ZM264.312 38.818Q261.966 38.818 260.33299999999997 40.497Q258.7 42.176 258.7 45.120000000000005Q258.7 48.064 260.33299999999997 49.789Q261.966 51.514 264.312 51.514Q266.658 51.514 268.291 49.812Q269.924 48.11 269.924 45.166Q269.924 42.222 268.291 40.519999999999996Q266.658 38.818 264.312 38.818Z"/>
                            <path d="M298.90999999999997 32.056V40.382000000000005H296.748Q293.804 40.382000000000005 292.332 41.647000000000006Q290.86 42.912 290.86 46.086V58.0H282.99399999999997V32.332H290.86V36.61Q292.24 34.494 294.31 33.275Q296.38 32.056 298.90999999999997 32.056Z"/>
                            <path d="M316.488 51.33V58.0H312.486Q308.20799999999997 58.0 305.816 55.907Q303.424 53.814 303.424 49.076V38.864000000000004H300.296V32.332H303.424V26.076H311.28999999999996V32.332H316.442V38.864000000000004H311.28999999999996V49.168Q311.29 50.318 311.842 50.824Q312.394 51.33 313.68199999999996 51.33Z"/>
                            <path d="M318.97799999999995 49.582H326.75199999999995Q326.89 50.916 327.99399999999997 51.744Q329.09799999999996 52.572 330.70799999999997 52.572Q332.17999999999995 52.572 332.98499999999996 51.997Q333.78999999999996 51.422 333.78999999999996 50.502Q333.78999999999996 49.397999999999996 332.64 48.869Q331.48999999999995 48.34 328.914 47.696Q326.154 47.052 324.31399999999996 46.339Q322.474 45.626 321.14 44.084999999999994Q319.806 42.544 319.806 39.922Q319.806 37.714 321.025 35.897Q322.24399999999997 34.08 324.61299999999994 33.022Q326.98199999999997 31.964000000000002 330.248 31.964000000000002Q335.078 31.964000000000002 337.861 34.356Q340.64399999999995 36.748000000000005 341.058 40.704H333.78999999999996Q333.606 39.370000000000005 332.61699999999996 38.588Q331.628 37.806 330.018 37.806Q328.638 37.806 327.902 38.335Q327.166 38.864000000000004 327.166 39.784Q327.166 40.888000000000005 328.33899999999994 41.440000000000005Q329.51199999999994 41.992000000000004 331.996 42.544Q334.84799999999996 43.28 336.64199999999994 43.993Q338.436 44.706 339.793 46.293000000000006Q341.15 47.88 341.19599999999997 50.548Q341.19599999999997 52.802 339.931 54.573Q338.666 56.344 336.297 57.356Q333.928 58.368 330.79999999999995 58.368Q327.44199999999995 58.368 324.81999999999994 57.218Q322.198 56.068 320.67999999999995 54.067Q319.162 52.066 318.97799999999995 49.582Z"/>
                        </clipPath>
                    </defs>
                    <g transform="translate(14 26)">
                        <g class="pulse" fill="none" stroke="var(--g1)" stroke-width="5" stroke-linecap="round">
                            <path class="dr" style="--d:.15s;--t:.45s" pathLength="1" d="M10 14 V46"/>
                            <path class="dr" style="--d:.50s;--t:.25s" pathLength="1" d="M10 21 H2"/>
                            <path class="dr" style="--d:.60s;--t:.25s" pathLength="1" d="M10 39 H18"/>
                            <rect class="body" x="24" y="12" width="16" height="32" rx="3" fill="var(--g1)" stroke="none"/>
                            <path class="dr" style="--d:.80s;--t:.30s" pathLength="1" d="M32 12 V0"/>
                            <path class="dr" style="--d:.80s;--t:.30s" pathLength="1" d="M32 44 V54"/>
                            <path class="dr" style="--d:.55s;--t:.45s" pathLength="1" d="M54 22 V54"/>
                            <path class="dr" style="--d:.90s;--t:.25s" pathLength="1" d="M54 29 H46"/>
                            <path class="dr" style="--d:1.00s;--t:.25s" pathLength="1" d="M54 47 H62"/>
                        </g>
                    </g>
                    <g clip-path="url(#bcrow)">
                        <g fill="var(--ink)">
                            <path class="rise" style="--d:1.05s" d="M108.612 49.214Q108.612 53.262 105.783 55.631Q102.95400000000001 58.0 97.894 58.0H82.852V25.708H97.388Q102.31 25.708 105.093 27.962Q107.876 30.216 107.876 34.08Q107.876 36.932 106.381 38.818Q104.886 40.704 102.402 41.44Q105.208 42.038 106.91 44.223Q108.612 46.408 108.612 49.214ZM90.718 38.772000000000006H95.87Q97.80199999999999 38.772000000000006 98.83699999999999 37.92100000000001Q99.872 37.07 99.872 35.414Q99.872 33.757999999999996 98.83699999999999 32.884Q97.80199999999999 32.010000000000005 95.87 32.010000000000005H90.718ZM100.654 48.156Q100.654 46.454 99.527 45.488Q98.4 44.522 96.422 44.522H90.718V51.652H96.514Q98.492 51.652 99.57300000000001 50.755Q100.654 49.858000000000004 100.654 48.156Z"/>
                            <path class="rise" style="--d:1.12s" d="M122.41799999999999 31.964000000000002Q125.13199999999999 31.964000000000002 127.179 33.068Q129.226 34.172 130.32999999999998 35.966V32.332H138.196V58.0H130.32999999999998V54.366Q129.18 56.16 127.13300000000001 57.263999999999996Q125.086 58.368 122.37199999999999 58.368Q119.244 58.368 116.668 56.735Q114.092 55.102 112.597 52.089Q111.10199999999999 49.076 111.10199999999999 45.120000000000005Q111.10199999999999 41.164 112.597 38.174Q114.092 35.184 116.668 33.574Q119.244 31.964000000000002 122.41799999999999 31.964000000000002ZM124.71799999999999 38.818Q122.37199999999999 38.818 120.73899999999999 40.497Q119.106 42.176 119.106 45.120000000000005Q119.106 48.064 120.73899999999999 49.789Q122.37199999999999 51.514 124.71799999999999 51.514Q127.064 51.514 128.697 49.812Q130.32999999999998 48.11 130.32999999999998 45.166Q130.32999999999998 42.222 128.697 40.519999999999996Q127.064 38.818 124.71799999999999 38.818Z"/>
                            <path class="rise" style="--d:1.19s" d="M153.152 31.964000000000002Q155.68200000000002 31.964000000000002 157.775 33.022Q159.868 34.08 161.064 35.873999999999995V23.96H168.93V58.0H161.064V54.32Q159.96 56.16 157.913 57.263999999999996Q155.866 58.368 153.152 58.368Q149.978 58.368 147.402 56.735Q144.826 55.102 143.33100000000002 52.089Q141.836 49.076 141.836 45.120000000000005Q141.836 41.164 143.33100000000002 38.174Q144.826 35.184 147.402 33.574Q149.978 31.964000000000002 153.152 31.964000000000002ZM155.452 38.818Q153.106 38.818 151.473 40.497Q149.84 42.176 149.84 45.120000000000005Q149.84 48.064 151.473 49.789Q153.106 51.514 155.452 51.514Q157.798 51.514 159.43099999999998 49.812Q161.064 48.11 161.064 45.166Q161.064 42.222 159.43099999999998 40.519999999999996Q157.798 38.818 155.452 38.818Z"/>
                            <path class="rise" style="--d:1.26s" d="M173.39800000000002 25.432000000000002Q173.39800000000002 23.592 174.709 22.373Q176.02 21.154000000000003 178.09 21.154000000000003Q180.114 21.154000000000003 181.425 22.373Q182.73600000000002 23.592 182.73600000000002 25.432000000000002Q182.73600000000002 27.226 181.425 28.445Q180.114 29.664 178.09 29.664Q176.02 29.664 174.709 28.445Q173.39800000000002 27.226 173.39800000000002 25.432000000000002ZM182.0 32.332V58.0H174.13400000000001V32.332Z"/>
                        </g>
                        <g fill="url(#bcg)">
                            <path class="rise" style="--d:1.40s" d="M202.108 25.340000000000003Q207.858 25.340000000000003 211.952 28.376Q216.046 31.412 217.426 36.656H208.778Q207.812 34.632000000000005 206.041 33.574000000000005Q204.27 32.516000000000005 202.01600000000002 32.516000000000005Q198.382 32.516000000000005 196.128 35.04600000000001Q193.874 37.576 193.874 41.808Q193.874 46.04 196.128 48.57Q198.382 51.1 202.01600000000002 51.1Q204.27 51.1 206.041 50.042Q207.812 48.984 208.778 46.96H217.426Q216.046 52.204 211.952 55.217Q207.858 58.23 202.108 58.23Q197.416 58.23 193.713 56.137Q190.01 54.044 187.94 50.318Q185.87 46.592 185.87 41.808Q185.87 37.024 187.94 33.275Q190.01 29.526 193.713 27.433Q197.416 25.340000000000003 202.108 25.340000000000003Z"/>
                            <path class="rise" style="--d:1.47s" d="M247.286 43.004V58.0H239.466V44.062Q239.466 41.486000000000004 238.132 40.06Q236.798 38.634 234.54399999999998 38.634Q232.29 38.634 230.956 40.06Q229.62199999999999 41.486000000000004 229.62199999999999 44.062V58.0H221.756V23.96H229.62199999999999V35.782Q230.81799999999998 34.08 232.88799999999998 33.068Q234.958 32.056 237.534 32.056Q241.95 32.056 244.618 34.977Q247.286 37.897999999999996 247.286 43.004Z"/>
                            <path class="rise" style="--d:1.54s" d="M262.012 31.964000000000002Q264.726 31.964000000000002 266.773 33.068Q268.82 34.172 269.924 35.966V32.332H277.78999999999996V58.0H269.924V54.366Q268.774 56.16 266.727 57.263999999999996Q264.68 58.368 261.966 58.368Q258.83799999999997 58.368 256.26199999999994 56.735Q253.68599999999998 55.102 252.19099999999997 52.089Q250.696 49.076 250.696 45.120000000000005Q250.696 41.164 252.19099999999997 38.174Q253.68599999999998 35.184 256.26199999999994 33.574Q258.83799999999997 31.964000000000002 262.012 31.964000000000002ZM264.312 38.818Q261.966 38.818 260.33299999999997 40.497Q258.7 42.176 258.7 45.120000000000005Q258.7 48.064 260.33299999999997 49.789Q261.966 51.514 264.312 51.514Q266.658 51.514 268.291 49.812Q269.924 48.11 269.924 45.166Q269.924 42.222 268.291 40.519999999999996Q266.658 38.818 264.312 38.818Z"/>
                            <path class="rise" style="--d:1.61s" d="M298.90999999999997 32.056V40.382000000000005H296.748Q293.804 40.382000000000005 292.332 41.647000000000006Q290.86 42.912 290.86 46.086V58.0H282.99399999999997V32.332H290.86V36.61Q292.24 34.494 294.31 33.275Q296.38 32.056 298.90999999999997 32.056Z"/>
                            <path class="rise" style="--d:1.68s" d="M316.488 51.33V58.0H312.486Q308.20799999999997 58.0 305.816 55.907Q303.424 53.814 303.424 49.076V38.864000000000004H300.296V32.332H303.424V26.076H311.28999999999996V32.332H316.442V38.864000000000004H311.28999999999996V49.168Q311.29 50.318 311.842 50.824Q312.394 51.33 313.68199999999996 51.33Z"/>
                            <path class="rise" style="--d:1.75s" d="M318.97799999999995 49.582H326.75199999999995Q326.89 50.916 327.99399999999997 51.744Q329.09799999999996 52.572 330.70799999999997 52.572Q332.17999999999995 52.572 332.98499999999996 51.997Q333.78999999999996 51.422 333.78999999999996 50.502Q333.78999999999996 49.397999999999996 332.64 48.869Q331.48999999999995 48.34 328.914 47.696Q326.154 47.052 324.31399999999996 46.339Q322.474 45.626 321.14 44.084999999999994Q319.806 42.544 319.806 39.922Q319.806 37.714 321.025 35.897Q322.24399999999997 34.08 324.61299999999994 33.022Q326.98199999999997 31.964000000000002 330.248 31.964000000000002Q335.078 31.964000000000002 337.861 34.356Q340.64399999999995 36.748000000000005 341.058 40.704H333.78999999999996Q333.606 39.370000000000005 332.61699999999996 38.588Q331.628 37.806 330.018 37.806Q328.638 37.806 327.902 38.335Q327.166 38.864000000000004 327.166 39.784Q327.166 40.888000000000005 328.33899999999994 41.440000000000005Q329.51199999999994 41.992000000000004 331.996 42.544Q334.84799999999996 43.28 336.64199999999994 43.993Q338.436 44.706 339.793 46.293000000000006Q341.15 47.88 341.19599999999997 50.548Q341.19599999999997 52.802 339.931 54.573Q338.666 56.344 336.297 57.356Q333.928 58.368 330.79999999999995 58.368Q327.44199999999995 58.368 324.81999999999994 57.218Q322.198 56.068 320.67999999999995 54.067Q319.162 52.066 318.97799999999995 49.582Z"/>
                        </g>
                    </g>
                    <g clip-path="url(#bcword)">
                        <rect class="shine" x="40" y="14" width="34" height="50" fill="url(#bcs)"/>
                    </g>
                    <g fill="var(--tag)">
                        <path class="fade" style="--d:2.30s" d="M86.508 73.904Q87.7845 73.904 88.77924999999999 74.53075Q89.774 75.1575 90.2225 76.3075H88.647Q88.3365 75.675 87.78450000000001 75.36449999999999Q87.2325 75.054 86.508 75.054Q85.7145 75.054 85.0935 75.4105Q84.4725 75.767 84.12174999999999 76.434Q83.771 77.101 83.771 77.9865Q83.771 78.872 84.12174999999999 79.539Q84.4725 80.206 85.0935 80.56825Q85.7145 80.9305 86.508 80.9305Q87.2325 80.9305 87.78450000000001 80.62Q88.3365 80.3095 88.647 79.677H90.2225Q89.774 80.827 88.77924999999999 81.44800000000001Q87.7845 82.069 86.508 82.069Q85.381 82.069 84.4495 81.54575Q83.518 81.0225 82.97175 80.091Q82.4255 79.1595 82.4255 77.9865Q82.4255 76.8135 82.97175 75.882Q83.518 74.9505 84.45525 74.42725Q85.3925 73.904 86.508 73.904Z"/>
                        <path class="fade" style="--d:2.33s" d="M101.7345 74.0075V82.0H100.42349999999999V78.504H96.663V82.0H95.35199999999999V74.0075H96.663V77.4345H100.42349999999999V74.0075Z"/>
                        <path class="fade" style="--d:2.37s" d="M111.87799999999999 80.367H108.5315L107.95649999999999 82.0H106.588L109.45149999999998 73.996H110.96949999999998L113.83299999999998 82.0H112.45299999999999ZM111.50999999999999 79.2975 110.21049999999998 75.583 108.89949999999999 79.2975Z"/>
                        <path class="fade" style="--d:2.40s" d="M122.82649999999998 82.0 120.98649999999999 78.803H119.98599999999999V82.0H118.67499999999998V74.0075H121.43499999999999Q122.35499999999999 74.0075 122.99324999999999 74.3295Q123.63149999999999 74.6515 123.94774999999998 75.19200000000001Q124.26399999999998 75.7325 124.26399999999998 76.3995Q124.26399999999998 77.1815 123.80974999999998 77.81975Q123.35549999999999 78.458 122.41249999999998 78.688L124.39049999999999 82.0ZM119.98599999999999 77.7565H121.43499999999999Q122.17099999999999 77.7565 122.54475 77.3885Q122.91849999999998 77.0205 122.91849999999998 76.3995Q122.91849999999998 75.7785 122.55049999999999 75.42775Q122.18249999999999 75.077 121.43499999999999 75.077H119.98599999999999Z"/>
                        <path class="fade" style="--d:2.44s" d="M134.7065 74.0075V75.077H132.579V82.0H131.268V75.077H129.129V74.0075Z"/>
                        <path class="fade" style="--d:2.47s" d="M140.94 74.0075V82.0H139.62900000000002V74.0075Z"/>
                        <path class="fade" style="--d:2.51s" d="M152.8315 82.0H151.5205L147.576 76.0315V82.0H146.26500000000001V73.996H147.576L151.5205 79.953V73.996H152.8315Z"/>
                        <path class="fade" style="--d:2.54s" d="M163.941 76.3075Q163.6305 75.7095 163.07850000000002 75.40475Q162.5265 75.1 161.80200000000002 75.1Q161.0085 75.1 160.3875 75.4565Q159.7665 75.813 159.41575 76.4685Q159.065 77.124 159.065 77.9865Q159.065 78.849 159.41575 79.51025Q159.7665 80.1715 160.3875 80.52799999999999Q161.0085 80.8845 161.80200000000002 80.8845Q162.8715 80.8845 163.5385 80.2865Q164.2055 79.6885 164.35500000000002 78.665H161.3535V77.6185H165.758V78.642Q165.63150000000002 79.5735 165.09675000000001 80.3555Q164.562 81.1375 163.70525 81.60325Q162.8485 82.069 161.80200000000002 82.069Q160.675 82.069 159.7435 81.54575Q158.812 81.0225 158.26575000000003 80.091Q157.7195 79.1595 157.7195 77.9865Q157.7195 76.8135 158.26575000000003 75.882Q158.812 74.9505 159.74925000000002 74.42725Q160.68650000000002 73.904 161.80200000000002 73.904Q163.07850000000002 73.904 164.07325000000003 74.53075Q165.068 75.1575 165.5165 76.3075Z"/>
                        <path class="fade" style="--d:2.61s" d="M178.547 75.0655V77.4115H181.30700000000002V78.481H178.547V80.9305H181.65200000000002V82.0H177.23600000000002V73.996H181.65200000000002V75.0655Z"/>
                        <path class="fade" style="--d:2.65s" d="M193.4285 82.0H192.1175L188.173 76.0315V82.0H186.86200000000002V73.996H188.173L192.1175 79.953V73.996H193.4285Z"/>
                        <path class="fade" style="--d:2.68s" d="M204.538 76.3075Q204.22750000000002 75.7095 203.6755 75.40475Q203.1235 75.1 202.39900000000003 75.1Q201.6055 75.1 200.98450000000003 75.4565Q200.36350000000002 75.813 200.01275 76.4685Q199.662 77.124 199.662 77.9865Q199.662 78.849 200.01275 79.51025Q200.36350000000002 80.1715 200.98450000000003 80.52799999999999Q201.6055 80.8845 202.39900000000003 80.8845Q203.4685 80.8845 204.1355 80.2865Q204.8025 79.6885 204.95200000000003 78.665H201.95050000000003V77.6185H206.35500000000002V78.642Q206.22850000000003 79.5735 205.69375000000002 80.3555Q205.15900000000002 81.1375 204.30225000000002 81.60325Q203.4455 82.069 202.39900000000003 82.069Q201.27200000000002 82.069 200.34050000000002 81.54575Q199.40900000000002 81.0225 198.86275 80.091Q198.31650000000002 79.1595 198.31650000000002 77.9865Q198.31650000000002 76.8135 198.86275 75.882Q199.40900000000002 74.9505 200.34625000000003 74.42725Q201.28350000000003 73.904 202.39900000000003 73.904Q203.67550000000003 73.904 204.67025 74.53075Q205.66500000000002 75.1575 206.11350000000002 76.3075Z"/>
                        <path class="fade" style="--d:2.72s" d="M212.554 74.0075V82.0H211.24300000000002V74.0075Z"/>
                        <path class="fade" style="--d:2.75s" d="M224.4455 82.0H223.1345L219.19 76.0315V82.0H217.87900000000002V73.996H219.19L223.1345 79.953V73.996H224.4455Z"/>
                        <path class="fade" style="--d:2.79s" d="M231.0815 75.0655V77.4115H233.84150000000002V78.481H231.0815V80.9305H234.18650000000002V82.0H229.77050000000003V73.996H234.18650000000002V75.0655Z"/>
                    </g>
                </svg>
            </div>
        </div>
        <script>
            (function() {
                var svg = document.querySelector('.bc');
                function play() {
                    svg.classList.remove('play');
                    void svg.getBoundingClientRect();
                    svg.classList.add('play');
                }
                document.getElementById('stage').addEventListener('click', play);
                play();
            }
            )();
        </script>
    </body>
</html>
'''


def build_embedded_html(boot_json, theme_json):
    """صفحة الاستوديو المدمجة: studio.html + badi-chart.js المحلي + جسر سطح المكتب + ثيم التطبيق."""
    html = STUDIO_HTML
    html = html.replace(
        '<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.13.0/chart.js"></script>',
        '<script src="badi-chart.js"></script>', 1)
    pre = BRIDGE_PRE.replace("__BOOT_JSON__", boot_json.replace("</", "<\\/"))
    pre = pre.replace("__THEME_JSON__", theme_json.replace("</", "<\\/"))
    html = html.replace("<body>", "<body>\n" + pre, 1)
    html = html.replace("</body>", BRIDGE_POST + "\n</body>", 1)
    return html


def _write_if_changed(path, text):
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == text:
                return
    except Exception:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


SPLASH_URL = ""   # يُضبط داخل ensure_web_files — رابط شاشة الشعار لصفحة QML


def ensure_web_files(boot_json, theme_json):
    """كتابة صفحة الويب + شاشة الشعار + مكتبة BADI المحلية بجانب التطبيق وإرجاع file:// URL."""
    global SPLASH_URL
    html = build_embedded_html(boot_json, theme_json)
    try:
        dark = bool(json.loads(theme_json).get("dark"))
    except Exception:
        dark = True
    # نفس ملف الديمو حرفياً — فقط ستيج الصفحة يأخذ ثيم التطبيق الحالي
    # (تنبيه: الاستبدال على وسم الـ div نفسه — 'data-bg="light"' يظهر أيضاً في مُحدِّد CSS ويجب ألا يُلمس)
    splash = SPLASH_HTML.replace('<div class="stage" id="stage" data-bg="light">',
                                 '<div class="stage" id="stage" data-bg="' + ("dark" if dark else "light") + '">', 1)
    lib = _b64_decode(BADI_LIB_B64)
    bases = [os.path.join(CFG_DIR, "web"),
             os.path.join(os.path.expanduser("~"), ".badi-charts", "web")]
    for base in bases:
        try:
            os.makedirs(base, exist_ok=True)
            hp = os.path.join(base, "studio.html")
            lp = os.path.join(base, "badi-chart.js")
            sp = os.path.join(base, "splash.html")
            _write_if_changed(hp, html)
            _write_if_changed(lp, lib)
            _write_if_changed(sp, splash)
            SPLASH_URL = QUrl.fromLocalFile(sp).toString()
            return QUrl.fromLocalFile(hp).toString()
        except Exception:
            continue
    raise RuntimeError("cannot create the embedded web directory")


# ---------------------------------------------------------------- الواجهة (QML)
QML = r'''
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtWebEngine

ApplicationWindow {
    id: win
    width: 1280; height: 800
    minimumWidth: 1000; minimumHeight: 640
    visible: true
    title: "BadiCharts Studio"
    color: backend.c.bg

    palette {
        window: backend.c.bg; windowText: backend.c.fg
        base: backend.c.card; text: backend.c.fg
        button: backend.c.card; buttonText: backend.c.fg
        highlight: backend.c.accent; highlightedText: "#FFFFFF"
        placeholderText: backend.c.sub
    }

    // ───────────── الحالة ─────────────
    property bool loggedIn: false
    property bool splash: true           // شاشة الشعار عند الإقلاع (نقرة تُخفيها)
    property int page: 0
    property bool edOpen: false          // حالة المحرر داخل صفحة الويب (مرآة)
    property string filter: "all"
    // جسر صفحة الويب المدمجة (BADI chart + Monaco)
    property bool webReady: false
    property bool webSound: true          // حالة أصوات الإشارات (مرآة صفحة الويب)
    property bool webSB: true             // شريط الحالة السفلي (مرآة صفحة الويب)
    property bool webCd: true             // العد التنازلي على الشارت (مرآة صفحة الويب)
    property bool webThemeDark: backend.dark
    property string lastAsset: ""
    property string lastTf: ""
    property int lastLen: -1
    property bool lastLoading: false      // v13.2: حالة دائرة التحميل في الشارت
    property var prependSentAt: 0         // v14.4: لحظة إرسال آخر دفعة تاريخية (فورية — بلا سباق)
    property bool histChain: backend.histChainActive   // v14.5: سلسلة التاريخ تجري الآن — لا إعادة ضبط للشارت أثناءها
    property var filesAcc: ({})
    property var pendingExport: null      // مؤشر معلّق ينتظر إدخال معرّف المشتري (ترخيص)

    // ───────────── جسر صفحة الويب المدمجة ─────────────
    function webCall(js, cb) {
        if (!win.webReady) return
        try { webView.runJavaScript(js, cb) } catch (e) { }
    }
    function webLog(kind, text) {
        webCall("__badiApp.log(" + JSON.stringify(kind) + "," + JSON.stringify(text) + ")")
    }
    /* فحص لون صالح — أي صيغة hex أو rgba بلا قوائم محدودة (الإعدادات) */
    function isColor(v) {
        var s = String(v || "").trim()
        if (/^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(s)) return true
        if (/^rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*(?:,\s*[\d.]+\s*)?\)$/.test(s)) return true
        return false
    }
    function pushTheme() {
        webCall("__badiApp.setTheme(" + JSON.stringify({ dark: backend.dark, c: backend.c, lang: backend.lang }) + ")")
    }
    function syncFull() {
        if (!win.webReady) return
        win.lastAsset = backend.assetLabel
        win.lastTf = backend.tfLabel
        win.lastLen = backend.candlesCount
        win.pushTheme()
        webCall("__badiApp.setAssets(" + JSON.stringify(backend.added) + ")")
        webCall("__badiApp.setChartTheme(" + backend.chartThemeJson + ")")
        /* معرّف المستخدم الثابت — يُعرض في الشريط السفلي ويُستخدم للترخيص (طلب المستخدم) */
        webCall("__badiApp.setUserId(" + JSON.stringify(backend.userId) + ")")
        webCall("__badiApp.setMarket(" + JSON.stringify({ label: backend.assetLabel, tf: backend.tfLabel,
                 tfMs: backend.tfSec * 1000, dec: backend.dec }) + ");" +
                "__badiApp.setCandles(" + backend.candlesJson + ");" +
                "__badiApp.setLive(" + (backend.live ? "true" : "false") + ");" +
                /* v13.2 (طلب المستخدم): دائرة تحميل في الشارت حتى تصل شموع العملة */
                "__badiApp.setChartLoading(" + (backend.chartLoading ? "true" : "false") + ")")
        win.lastLoading = backend.chartLoading
    }
    function doLogout() {
        win.loggedIn = false
        win.page = 0
        userF.text = ""
        passF.text = ""
    }
    function onCandlesWeb() {
        if (!win.webReady) return
        /* v13.2 (طلب المستخدم): دائرة تحميل داخل الشارت بدل شارت أسود — تظهر
           عندما تكون شموع العملة الحالية تُجلب من الخادم وتختفي عند وصولها */
        if (backend.chartLoading !== win.lastLoading) {
            win.lastLoading = backend.chartLoading
            webCall("__badiApp.setChartLoading(" + (backend.chartLoading ? "true" : "false") + ")")
        }
        /* v14.4: حماية سلسلة التاريخ (300 ثم 300) — دفعة candlesChanged التي
           تلي دفعة "older" خلال نافذة الدفعات (20 ثانية) لا تعيد ضبط الشارت
           أبداً: الصفحة دمجت الدفعة فعلاً عبر prependCandles، فالعدّاد فقط
           يتزامن هنا. الزوم والموضع يبقيان حرين تماماً أثناء جلب التاريخ.
           العلامة تُضبط فوراً عند الإرسال (prependSentAt) — لا سباق مع callback */
        if ((Date.now() - (win.prependSentAt || 0)) < 20000
                && backend.assetLabel === win.lastAsset && backend.tfLabel === win.lastTf
                && backend.candlesCount >= win.lastLen) {
            win.lastLen = backend.candlesCount
            return
        }
        if ((Date.now() - (win.prependAt || 0)) < 5000
                && backend.assetLabel === win.lastAsset && backend.tfLabel === win.lastTf
                && backend.candlesCount >= win.lastLen) {
            win.lastLen = backend.candlesCount
            return
        }
        /* v14.5 (طلب المستخدم حرفياً: «الشارت لا نريده ان يتاثر اطلاقا يجب ان
           يبقا حر ولا يتاثر ولا نريد فقدان الشموع»): أثناء سلسلة التاريخ
           (طلب واحد بمدى الأيام وكل دفعة تُدمج عبر prependCandles) يُمنع
           إعادة ضبط الشارت نهائياً — الفروقات الكبيرة هنا ناتجة عن الدفعات
           نفسها وليست خطأً. الزوم والموضع يبقيان حرين طوال السلسلة. */
        if (win.histChain && backend.assetLabel === win.lastAsset
                && backend.tfLabel === win.lastTf) {
            var dchain = backend.candlesCount - win.lastLen
            if (dchain > 60 || dchain < 0) {
                win.lastLen = backend.candlesCount
                return
            }
        }
        if (backend.assetLabel !== win.lastAsset || backend.tfLabel !== win.lastTf) {
            win.syncFull()
            return
        }
        /* v13.1 (طلب المستخدم: بلا قفزات): عند تراكم أكثر من شمعة بين نبضتين
           تُدفع دفعة الذيل الأخيرة فقط عبر pushTail نفسها — لا إعادة إرسال
           المصفوفة كاملة (syncFull كانت تعيد ضبط العرض فتظهر الشموع وكأنها تقفز) */
        var diff = backend.candlesCount - win.lastLen
        /* v14.8 (سبب اختفاء الشموع): لنفس العملة والفريم لا إعادة ضبط
           للشارت إطلاقاً (لا syncFull ولا setCandles):
           - نقص العدّاد = الصفحة تمتلك شموعاً أكثر من الغذاء المقتطع —
             العدّاد فقط يتزامن ولا يُلمس العرض.
           - زيادة كبيرة = دمج في مكانها عبر patchCandles — بلا setData.
           الزوم والموضع يبقيان حرين ولا تُفقد شمعة واحدة. */
        if (diff < 0) { win.lastLen = backend.candlesCount; return }
        if (diff > 60) { win.lastLen = backend.candlesCount;
            webCall("__badiApp.patchCandles(" + backend.candlesJson + ")"); return }
        if (diff > 1) {
            win.lastLen = backend.candlesCount
            webCall("__badiApp.pushTail(" + backend.tailJsonN(diff) + ")")
            return
        }
        if (diff !== 0) win.lastLen = backend.candlesCount
        /* آخر 3 شموع (الشمعة الحية + إغلاق شمعتين مغلقتين) — دفعة خفيفة بدون
           إعادة ضبط العرض، وتُصلح الشمعة المغلقة داخل المكتبة مباشرة */
        webCall("__badiApp.pushTail(" + backend.tailJson + ")")
    }
    function filesAccPart(cmd, arg) {
        var meta = cmd.substring(6)
        var slash = meta.indexOf("/")
        var idx = parseInt(meta.substring(0, slash), 10)
        var total = parseInt(meta.substring(slash + 1), 10)
        if (isNaN(idx) || isNaN(total) || total < 1) return
        if (idx === 1) win.filesAcc = { total: total, parts: [] }
        if (!win.filesAcc || win.filesAcc.total !== total) return
        win.filesAcc.parts.push(arg)
        if (win.filesAcc.parts.length === win.filesAcc.total) {
            var full = win.filesAcc.parts.join("")
            win.filesAcc = ({})
            backend.saveFiles(full)
        }
    }
    function runPyFile(f) {
        var res = JSON.parse(backend.compilePyOne(f.id, f.fileName, f.code))
        if (!res.ok) {
            webCall("__badiApp.pyError(" + JSON.stringify(f.id) + "," + JSON.stringify(String(res.error)) + ")")
            return
        }
        webCall("__badiApp.pyMeta(" + JSON.stringify(f.id) + "," + JSON.stringify(res) + "," + JSON.stringify(f.fileName) + ")")
        backend.refreshPy()
    }
    function onWebMessage(cmd, arg) {
        if (cmd === "ready") { win.webReady = true; win.syncFull(); return }
        if (cmd === "editor") { win.edOpen = (arg === "1"); return }
        if (cmd === "page") {
            var p = Math.max(0, Math.min(2, parseInt(arg, 10) || 0))
            /* زر تلجرام/المؤشرات في شريط الصفحة: نقرة ثانية تُعيد للاستوديو */
            win.page = (p !== 0 && win.page === p) ? 0 : p
            return
        }
        if (cmd === "dbg") { console.log("PAGEDBG " + arg); return }
        if (cmd === "shot") { win.takeShot(); return }
        if (cmd === "asset") { backend.switch(arg, backend.tfLabel); return }
        if (cmd === "tf") { backend.switch(backend.assetLabel, arg); return }
        if (cmd === "older") { backend.fetchOlder(arg); return }   // LIVE SERVER EDITION: دفعة 170 شمعة أقدم
        if (cmd === "live") { backend.setLive(arg === "1"); return }
        if (cmd === "dark") { backend.dark = (arg === "1"); return }
        if (cmd === "joinch") { Qt.openUrlExternally("https://t.me/badicharts"); return }
        if (cmd === "settings") { settingsPop.open(); return }
        if (cmd === "logout") { win.doLogout(); return }
        if (cmd === "assets") { backend.setAddedJson(arg); return }
        if (cmd === "theme") { win.webThemeDark = (arg === "1"); return }
        if (cmd === "files") { backend.saveFiles(arg); return }
        if (cmd.indexOf("files~") === 0) { win.filesAccPart(cmd, arg); return }
        if (cmd === "rescan") { backend.rescanFiles(); return }
        if (cmd === "badi-open") { win.badiOpenByName(arg); return }
        /* نسخ معرّف المستخدم من الشريط السفلي + فتح مجلد التطبيق (طلب المستخدم) */
        if (cmd === "copyuid") { backend.copyText(arg); win.webLog("ok", backend.s.uidCopied); return }
        if (cmd === "opendir") { var dp = backend.openBadiDir(); if (dp !== "") win.webLog("ok", backend.s.folderOpen + " — " + dp); return }
        /* صورة المؤشر المصغرة: طلب التقاط واحد عند أول تشغيل (طلب المستخدم) */
        if (cmd === "badi-thumb") { win.grabThumb(arg); return }
        if (cmd === "signal") {
            var s = JSON.parse(arg)
            backend.fireSignal(s.id, s.label, s.dir, Number(s.price || 0),
                               String(s.asset || ""), String(s.chats || ""))
            return
        }
        if (cmd === "runpy") { win.runPyFile(JSON.parse(arg)); return }
        if (cmd === "stopy") {
            var p = JSON.parse(arg)
            backend.stopPy(p.id)
            webCall("__badiApp.pyRemove(" + JSON.stringify(p.id) + ")")
        }
        if (cmd === "badi-export") { win.badiExportPick(); return }
        if (cmd === "badi-import") { badiOpenDialog.open(); return }
    }
    function addLib(key) {
        webCall("__badiApp.addFile(JSON.parse(" + JSON.stringify(backend.libFile(key)) + "))")
        win.page = 0
    }
    function takeShot() {
        webCall("__badiApp.shot()", function (res) { if (res && res.length > 32) backend.saveShot(res) })
    }
    /* ───── BADI: تصدير المؤشر المشفر بجوار ملفه الأصلي في BadiCharts (مثل ميتاتريدر) واستيراده ─────
       المفتاح 256-بت مدموج داخل التطبيق ولا يُكتب داخل ملف المؤشر أبدًا */
    function badiExportPick() {
        win.webCall("(function(){ try { var f = activeFile(); return JSON.stringify({ n: f ? f.fileName : '', k: f ? f.kind : '', c: f ? f.code : '' }); } catch (e) { return '{}'; } })()",
                    function (res) {
                        var o = {}
                        try { o = JSON.parse(res || "{}") } catch (e) { o = {} }
                        if (!o.c || o.c.length < 2) { win.webLog("err", backend.s.badiEmpty); return }
                        if (o.k === "py") { win.webLog("err", backend.s.badiJsOnly); return }
                        /* حوار ترخيص المشتري: معرّف المشتري يُدمج داخل الملف المشفر —
                           لا يعمل المؤشر إلا على جهازه (طلب المستخدم) */
                        win.pendingExport = { c: o.c, n: o.n || "indicator", k: o.k || "indicator" }
                        licField.text = ""
                        licPop.open()
                    })
    }
    function badiExportConfirm() {
        var pe = win.pendingExport
        if (!pe) { licPop.close(); return }
        var r = JSON.parse(backend.badiExport(pe.c, pe.n, pe.k, licField.text, paidSrvField.text.trim(), paidIdField.text.trim()))
        licPop.close()
        win.pendingExport = null
        if (r.ok) win.webLog("ok", backend.s.badiSaved + " ← " + r.path)
        else win.webLog("err", backend.s.badiFail + ": " + r.error)
    }
    /* فتح ملف .badi من قائمة BadiCharts بالنقر عليه — فك التشفير داخل التطبيق بمفتاحه،
       والتشغيل داخليًا مباشرة على الشارت: الكود لا يُفتح في المحرر ولا يُحفظ (طلب المستخدم) */
    function badiOpenByName(name) {
        var r = JSON.parse(backend.badiOpenName(String(name || "")))
        if (!r.ok) { win.webLog("err", backend.s.badiFail + ": " + r.error); return }
        webCall("__badiApp.loadHidden(" + JSON.stringify({ id: r.id, fileName: r.fileName, code: r.code }) + ")")
        win.page = 0
        win.webLog("ok", backend.s.badiOk + " — " + r.fileName)
    }
    function badiImportAt(url) {
        var r = JSON.parse(backend.badiImport(String(url)))
        if (!r.ok) { win.webLog("err", backend.s.badiFail + ": " + r.error); return }
        webCall("__badiApp.loadHidden(" + JSON.stringify({ id: r.id, fileName: r.fileName, code: r.code }) + ")")
        win.page = 0
        win.webLog("ok", backend.s.badiOk + " — " + r.fileName)
    }
    /* ── صورة المؤشر المصغرة: التقاط ذكي واحد عند أول تشغيل (طلب المستخدم) ── */
    function grabThumb(name) {
        win.webCall("__badiApp.thumbData(" + JSON.stringify(String(name)) + ")",
                    function (res) {
                        if (res && res.length > 1200 && res.indexOf("data:image") === 0)
                            backend.saveIndThumb(name, res)
                        else
                            win.webCall("__badiApp.thumbRetry(" + JSON.stringify(String(name)) + ")")
                    })
    }
    /* ── مؤشراتي: إضافة إلى الشارت + مشاركة عبر تلجرام (طلب المستخدم) ── */
    function addMy(fileName, enc) {
        if (enc) { win.badiOpenByName(fileName); return }   /* المشفر: فك التشفير داخليًا + تشغيل */
        webCall("__badiApp.openRun(" + JSON.stringify(String(fileName)) + ")",
                function (res) {
                    if (String(res || "").indexOf("no:") === 0)
                        toastPop.show(true, backend.s.myinds + ": " + fileName)
                })
        win.page = 0
    }
    function shareMy(fileName) {
        var r = {}
        try { r = JSON.parse(backend.shareIndicator(String(fileName))) } catch (e) {}
        if (r.ok) toastPop.show(false, backend.s.shareOk + "\n" + (r.path || ""))
        else toastPop.show(true, backend.s.shareFail + ": " + (r.error || ""))
    }
    function histRows() {
        var arr = JSON.parse(backend.histJson).slice().reverse()
        if (win.filter === "all") return arr
        return arr.filter(function (r) { return win.filter === "sent" ? r.sent === true : r.sent === false })
    }
    function syncStudioIfVisible() {
        if (win.loggedIn && !win.splash && win.page === 0) webCall("__badiApp.rescale()")
    }
    onPageChanged: win.syncStudioIfVisible()
    onLoggedInChanged: win.syncStudioIfVisible()
    onSplashChanged: win.syncStudioIfVisible()

    Connections {
        target: backend
        function onConsoleMsg(kind, text) { win.webLog(kind, text) }
        function onCandlesChanged() { win.onCandlesWeb() }
        function onPyValues(id, seriesJson, rangeJson) {
            webCall("__badiApp.setPy(" + JSON.stringify(id) + "," + seriesJson + "," + rangeJson + ")")
        }
        function onTestResult(ok, info) { win.webLog(ok ? "ok" : "err", "Telegram: " + info) }
        function onShotSaved(ok, path) { if (ok) win.webLog("ok", backend.s.shotdone + " → " + path) }
        function onNeedShot() { win.webCall("__badiApp.shot()", function (res) { backend.chartShot(res || "") }) }
        function onLiveChanged() { win.webCall("__badiApp.setLive(" + (backend.live ? "true" : "false") + ")") }
        function onDarkChanged() { win.pushTheme() }
        function onChartThemeChanged() {
            /* ألوان الشارت تغيّرت من الإعدادات — طبّقها على الشارت فورًا */
            win.webCall("__badiApp.setChartTheme(" + backend.chartThemeJson + ")")
        }
        function onAddedChanged() {
            win.webCall("__badiApp.setAssets(" + JSON.stringify(backend.added) + ")")
        }
        function onFilesChanged() {
            /* مزامنة مجلد BadiCharts أضافت/حذفت ملفات — ادفع القائمة الجديدة للصفحة */
            win.webCall("__badiApp.setFiles(" + backend.filesJson + ")")
        }
        function onSigResult(js) {
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
            if (e.type === "chartload") {
                /* v15.2 (طلب المستخدم): دائرة تحميل الشموع عند فتح العملة من
                   قائمة العملات — تظهر عند بداية جلب الشموع وتبقى حتى ينتهي
                   الجلب فيظهر الشارت. بلا شارة في الزاوية وبلا تحميل خلفي. */
                win.webCall("__badiApp.setChartLoading(" + (e.active ? "true" : "false")
                            + "," + JSON.stringify(String(e.asset || "")) + ")")
                return
            }
            if (e.type === "resync") {
                /* v14.4 (طلب المستخدم حرفياً: «الشارت لا نريده ان يتاثر اطلاقا
                   يجب ان يبقا حر ولا يتاثر ولا نريد فقدان الشموع»): إصلاح سد
                   الثغرات يُدمج في الشارت في مكانه — تحديث الشموع بالوقت وإضافة
                   الناقص بلا setData وبلا أي إعادة ضبط — الزوم والموضع يبقان
                   حرين تماماً كما هما */
                /* v14.6: مزامنة العدّاد بعد الدمج — أي نبضة candlesChanged تالية
                   ترى الفرق صفراً فلا تُعيد ضبط الشارت أبداً (syncFull محظورة) */
                win.lastLen = backend.candlesCount
                win.lastAsset = backend.assetLabel
                win.lastTf = backend.tfLabel
                win.webCall("__badiApp.patchCandles(" + backend.candlesJson + ")")
                return
            }
            if (e.type === "older") {
                /* v14.1: الدفعة موسومة بالعملة والفريم — prependCandles ترفض
                   أي دفعة لا تطابق الشارت الحالي (حماية من الاخلاط عند التبديل السريع) */
                /* v14.4: العلامة تُضبط هنا فوراً (وليس في callback) — أي نبضة
                   candlesChanged قادمة خلال نافذة الدفعات لا تعيد ضبط الشارت */
                win.prependSentAt = Date.now()
                win.webCall("__badiApp.prependCandles(" + JSON.stringify(e.candles || []) + ","
                            + JSON.stringify(String(e.asset || "")) + ","
                            + JSON.stringify(String(e.tf || "")) + ")",
                            function (res) {
                                /* مزامنة عدّاد الشموع حتى لا تُعاد تهيئة الشارت
                                   بعد دمج الدفعة — العرض يبقى ثابتاً تماماً */
                                var n = parseInt(res || "0", 10) || 0
                                if (n > 0) {
                                    win.prependAt = Date.now()
                                    win.lastLen = backend.candlesCount
                                    return
                                }
                                /* v14.8: دفعة تملأ ثغرة داخل المدى (ليست
                                   أقدم من أول شمعة) — تُدمج في مكانها عبر
                                   patchCandles بلا setData ولا إعادة ضبط
                                   — لا دفعة تضيع بعد الآن */
                                win.webCall("__badiApp.patchCandles("
                                            + JSON.stringify(e.candles || []) + ")",
                                            function (res2) {
                                                var n2 = parseInt(res2 || "0", 10) || 0
                                                if (n2 > 0) {
                                                    win.prependAt = Date.now()
                                                    win.lastLen = backend.candlesCount
                                                }
                                            })
                            })
                return
            }
        }
        function onPaidCmd(js) {
            /* أمر التحكم البعيد الصالح (تشغيل/إيقاف) — يُنفذ في صفحة الويب فورًا (طلب المستخدم) */
            win.webCall("__badiApp.remoteSet(" + js + ")")
        }
    }

    Component.onCompleted: {
        if (win.dbgDir !== "") dbgT.restart()
    }

    // وضع التقاط لقطات للفحص الآلي — يُفعَّل فقط بمتغير البيئة BADI_SHOTS
    property string dbgDir: (typeof dbgShotDir !== "undefined") ? dbgShotDir : ""
    property int dbgStep: 0
    property var dbgCur: null
    Timer { id: dbgT; interval: 1400; onTriggered: win.dbgNext() }
    Timer { id: snapT; interval: 900; onTriggered: win.dbgSnap() }
    function dbgNext() {
        var steps = [
            { sel: "splash" },
            { sel: "login", act: "skip", light: true },
            { sel: "page", idx: 0, tag: "studio-dark", act: "in" },
            { sel: "window", tag: "window-dark" },
            { sel: "settings", tag: "settings-pop" },
            { sel: "page", idx: 1, tag: "indicators" },
            { sel: "page", idx: 2, tag: "signals" },
            { sel: "page", idx: 0, tag: "panels-hidden", act: "hidep", wait: 1800 },
            { sel: "page", idx: 0, tag: "thumb-e2e", act: "thumbtest", wait: 5200 },
            { sel: "page", idx: 0, tag: "enc-e2e", act: "enctest", wait: 5200 },
            { sel: "page", idx: 0, tag: "studio-light", light: false, act: "showp", wait: 1600 }
        ]
        if (win.dbgStep >= steps.length) { Qt.callLater(Qt.quit); return }
        var s = steps[win.dbgStep]
        if (s.act === "skip") win.splash = false
        if (s.act === "in") win.loggedIn = true
        if (s.light !== undefined) backend.dark = s.light
        if (s.idx !== undefined) win.page = s.idx
        if (s.act === "hidep") win.webCall("try { __badiApp.setSigHidden(true) } catch (e) {}")
        if (s.act === "showp") win.webCall("try { __badiApp.setSigHidden(false) } catch (e) {}")
        /* فحص شامل: إضافة مؤشر للشارت + التقاط المصغرة التلقائي + تشغيل المشفر داخليًا */
        if (s.act === "thumbtest") {
            /* التأكد من وجود المؤشر التجريبي في المجلد ثم تشغيله لالتقاط المصغرة تلقائيًا */
            backend.seedTestInd()
            win.webCall('__badiApp.openRun("Test RSI.js")')
            win.webCall('setTimeout(function () { console.log("BADI::dbg enabled=" + JSON.stringify(files.filter(function (f) { return f.enabled; }).map(function (f) { return f.fileName; }))) }, 2600)')
        }
        if (s.act === "enctest") win.addMy("Test Enc.badi", true)
        if (s.sel === "settings") settingsPop.open()
        win.dbgCur = s
        snapT.interval = s.snap || 900
        dbgT.interval = s.wait || 1400
        snapT.restart()
    }
    function dbgSnap() {
        var s = win.dbgCur
        if (!s) return
        var it = null
        if (s.sel === "splash") it = mainStack.children[0]
        else if (s.sel === "login") it = mainStack.children[1]
        else if (s.sel === "window") it = win.header
        else if (s.sel === "settings") it = settingsPop.visible ? settingsCol : null
        else it = appPages.children[win.page]
        var tag = s.tag || s.sel
        if (s.sel === "window") {
            console.log("PAGEDBG shell dark=" + backend.dark + " webThemeDark=" + win.webThemeDark)
            win.webCall("console.log('BADI::dbg app=' + (!!window.__badiApp) + ' theme=' + JSON.stringify(window.__BADI_APP_THEME__).substring(0,80) + ' bodybg=' + getComputedStyle(document.body).backgroundColor)")
        }
        if (it) it.grabToImage(function (r) {
            console.log("DBGSHOT " + tag + " " + r.saveToFile(win.dbgDir + "/" + tag + ".png"))
        })
        win.dbgStep++
        dbgT.restart()
    }

    // ───────────── النوافذ ─────────────
    // (إنشاء الملفات والحذف يُداران داخل صفحة الويب المدمجة)

    // ════════════════ الشريط العلوي الاقصى (الشعار + الحساب والرصيد + الإعدادات) ════════════════
    header: Rectangle {
        height: 54
        color: backend.c.side
        visible: !win.splash
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: backend.c.border }
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 8
            Column {
                spacing: 1
                Item {
                    width: 120; height: 120 * 80 / 354
                    Logo { animate: false; anchors.fill: parent }
                    MouseArea {
                        anchors.fill: parent; enabled: win.loggedIn; cursorShape: Qt.PointingHandCursor
                        onClicked: win.page = 0
                    }
                }
            }
            Item { Layout.fillWidth: true }
            /* زرا الوضع الليلي/النهاري والإعدادات جنب بعض مباشرة (طلب المستخدم) */
            IBtn {
                iconName: backend.dark ? "sun" : "moon"
                onClicked: backend.dark = !backend.dark
            }
            /* زر الإشعارات جنب زر الإعدادات مباشرة + شارة حمراء بعدد غير المقروء (طلب المستخدم) */
            IBtn {
                id: notifBtn
                visible: win.loggedIn
                iconName: "bell"
                onClicked: {
                    backend.notifsMarkAll()
                    notifPop.open()
                }
                Rectangle {
                    anchors.top: parent.top; anchors.right: parent.right
                    anchors.topMargin: 1; anchors.rightMargin: 1
                    width: 15; height: 15; radius: 7.5
                    color: "#FF4D5E"
                    visible: backend.notifsUnread > 0
                    Label { text: backend.notifsUnread; font.pixelSize: 9; font.bold: true
                            color: "#FFFFFF"; anchors.centerIn: parent }
                }
            }
            IBtn {
                visible: win.loggedIn
                iconName: "sett"
                onClicked: settingsPop.open()
            }
            LangBox { }
            /* زر قناة تلجرام — ظاهر دائمًا حتى قبل الدخول (واجهة الدخول الجديدة) */
            Rectangle {
                Layout.preferredHeight: 32
                Layout.preferredWidth: tgRow.implicitWidth + 22
                radius: 8
                color: tgMs.containsMouse ? Qt.rgba(0.08, 0.55, 0.96, 0.28) : Qt.rgba(0.08, 0.55, 0.96, 0.14)
                border.width: 1; border.color: Qt.rgba(0.08, 0.55, 0.96, 0.45)
                Row {
                    id: tgRow; anchors.centerIn: parent; spacing: 6
                    Icon { name: "send"; sz: 14; tint: backend.c.accent; anchors.verticalCenter: parent.verticalCenter }
                    Label { text: "Join Channel"; font.pixelSize: 11; font.bold: true
                            color: backend.c.accent; anchors.verticalCenter: parent.verticalCenter }
                }
                MouseArea { id: tgMs; anchors.fill: parent; hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Qt.openUrlExternally("https://t.me/badicharts") }
            }
        }
    }

    // ════════════════ لوحة الإعدادات: إدارة عملات الشريط ════════════════
    Popup {
        id: settingsPop
        parent: Overlay.overlay
        anchors.centerIn: Overlay.overlay
        width: 380
        height: Math.min(580, win.height - 80)
        padding: 0
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        /* عند الفتح: قراءة حالة أصوات الإشارات الحقيقية من صفحة الويب */
        onOpened: {
            win.webCall("__badiApp.getSound()", function (r) {
                if (r !== undefined && r !== null) win.webSound = !!r
            })
            win.webCall("__badiApp.getStatusBar()", function (r) {
                if (r !== undefined && r !== null) win.webSB = !!r
            })
            win.webCall("__badiApp.getCd()", function (r) {
                if (r !== undefined && r !== null) win.webCd = !!r
            })
        }
        background: Rectangle {
            radius: 16; color: backend.c.card
            border.width: 1; border.color: backend.c.border
        }
        /* كل محتوى الإعدادات في تمرير واحد بشريط SlimBar رقيق بروح شريط المحرر —
           كانت قائمة العملات تُسحق إلى ارتفاع صفر بسبب الأقسام الثابتة تحتها
           (طلب المستخدم: شريط رقيق مثل تبع المحرر أو انزعه) */
        Flickable {
            id: settScroll
            anchors.fill: parent; clip: true
            contentWidth: width
            contentHeight: settingsCol.implicitHeight + 24
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: SlimBar { }
            ColumnLayout {
                id: settingsCol
                x: 16; y: 12
                width: settScroll.width - 32
                spacing: 8
            RowLayout {
                spacing: 9
                Rectangle {
                    width: 34; height: 34; radius: 10
                    color: Qt.rgba(0.08, 0.55, 0.96, 0.14)
                    Icon { anchors.centerIn: parent; name: "sett"; sz: 18; tint: backend.c.accent }
                }
                Label { text: backend.s.sett; font.pixelSize: 16; font.bold: true; color: backend.c.fg }
                Item { Layout.fillWidth: true }
                /* زر إغلاق لوحة الإعدادات بأيقونة X (طلب المستخدم) */
                IBtn { iconName: "x"; onClicked: settingsPop.close() }
            }
            /* قائمة العملات أُزيلت من بطاقة الإعدادات نهائيًا — الإضافة والإزالة من قائمة + فقط (طلب المستخدم) */
            /* ───── إعدادات أخرى: الوضع الليلي + اللغة + أصوات الإشارات (طلب المستخدم) ───── */
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border }
            RowLayout {
                spacing: 8
                Icon { name: "sett"; sz: 14; tint: backend.c.accent }
                Label { text: backend.s.otherSett; font.pixelSize: 13; font.bold: true; color: backend.c.fg }
                Item { Layout.fillWidth: true }
            }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Icon { name: backend.dark ? "sun" : "moon"; sz: 14; tint: backend.c.sub }
                Label { text: backend.s.darkMode; font.pixelSize: 11; color: backend.c.fg; Layout.fillWidth: true }
                MiniSwitch { on: backend.dark; onToggled: backend.dark = !backend.dark }
            }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Icon { name: "globe"; sz: 14; tint: backend.c.sub }
                Label { text: backend.s.langLbl; font.pixelSize: 11; color: backend.c.fg; Layout.fillWidth: true }
                LangBox { }
            }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Icon { name: "bell"; sz: 14; tint: backend.c.sub }
                Label { text: backend.s.sndLbl; font.pixelSize: 11; color: backend.c.fg; Layout.fillWidth: true }
                MiniSwitch {
                    on: win.webSound
                    onToggled: {
                        win.webSound = !win.webSound
                        win.webCall("__badiApp.setSound(" + win.webSound + ")")
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Icon { name: "eye"; sz: 14; tint: backend.c.sub }
                Label { text: backend.s.sbLbl; font.pixelSize: 11; color: backend.c.fg; Layout.fillWidth: true }
                MiniSwitch {
                    on: win.webSB
                    onToggled: {
                        win.webSB = !win.webSB
                        win.webCall("__badiApp.setStatusBar(" + win.webSB + ")")
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Icon { name: "clock"; sz: 14; tint: backend.c.sub }
                Label { text: backend.s.cdLbl; font.pixelSize: 11; color: backend.c.fg; Layout.fillWidth: true }
                MiniSwitch {
                    on: win.webCd
                    onToggled: {
                        win.webCd = !win.webCd
                        win.webCall("__badiApp.setCd(" + win.webCd + ")")
                    }
                }
            }
            /* ───── v14.3 (طلب المستخدم): عدد أيام شموع التاريخ — يُكتب الرقم
               ويُضغط حفظ (0.5 حتى 30 يوم، الافتراضي يومان). عند فتح العملة
               تُجلب دفعة 300 ثم 300 حتى بلوغ هذا العدد وكل دفعة تُرفع للشارت ───── */
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border }
            RowLayout {
                spacing: 8
                Icon { name: "candle"; sz: 14; tint: backend.c.accent }
                Label { text: backend.s.histDays; font.pixelSize: 13; font.bold: true; color: backend.c.fg }
                Item { Layout.fillWidth: true }
                Btn { text: backend.s.histSave; iconName: "ok"; implicitHeight: 30; font.pixelSize: 10
                      onClicked: backend.setHistDays(histDaysField.text) }
            }
            Label {
                text: backend.s.histDaysHint; font.pixelSize: 10; color: backend.c.sub
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }
            TextField {
                id: histDaysField
                Layout.fillWidth: true
                implicitHeight: 38
                font.pixelSize: 12; font.family: "monospace"
                color: backend.c.fg
                text: backend.histDaysStr
                placeholderText: "2"
                placeholderTextColor: backend.c.sub
                selectByMouse: true
                leftPadding: 12; rightPadding: 12
                inputMethodHints: Qt.ImhPreferNumbers
                validator: DoubleValidator { bottom: 0.5; top: 30; decimals: 1; locale: "C"; notation: DoubleValidator.StandardNotation }
                background: Rectangle {
                    radius: 10; color: backend.c.bg
                    border.width: histDaysField.activeFocus ? 2 : 1
                    border.color: histDaysField.activeFocus ? backend.c.accent : backend.c.border
                }
                onAccepted: backend.setHistDays(histDaysField.text)
            }
            /* ───── v14.7 (طلب المستخدم حرفياً): «اريد ان تجلب 700 شمعة بدل
               300 شمعة كدفعة مباشرة للعملة ويمكن تعديلها في الاعدادات الى 1000
               شمعة في الدفعة» — يُكتب الرقم ويُضغط حفظ (الافتراضي 700) ───── */
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border }
            RowLayout {
                spacing: 8
                Icon { name: "candle"; sz: 14; tint: backend.c.accent }
                Label { text: backend.s.batchCandles; font.pixelSize: 13; font.bold: true; color: backend.c.fg }
                Item { Layout.fillWidth: true }
                Btn { text: backend.s.batchSave; iconName: "ok"; implicitHeight: 30; font.pixelSize: 10
                      onClicked: backend.setBatchCandles(batchField.text) }
            }
            Label {
                text: backend.s.batchCandlesHint; font.pixelSize: 10; color: backend.c.sub
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }
            TextField {
                id: batchField
                Layout.fillWidth: true
                implicitHeight: 38
                font.pixelSize: 12; font.family: "monospace"
                color: backend.c.fg
                text: backend.batchCandlesStr
                placeholderText: "700"
                placeholderTextColor: backend.c.sub
                selectByMouse: true
                leftPadding: 12; rightPadding: 12
                inputMethodHints: Qt.ImhPreferNumbers
                validator: IntValidator { bottom: 100; top: 1000; locale: "C" }
                background: Rectangle {
                    radius: 10; color: backend.c.bg
                    border.width: batchField.activeFocus ? 2 : 1
                    border.color: batchField.activeFocus ? backend.c.accent : backend.c.border
                }
                onAccepted: backend.setBatchCandles(batchField.text)
            }
            /* ───── مظهر الشارت: تغيير الخلفية وألوان الشموع بحرية (طلب المستخدم) ───── */
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border }
            RowLayout {
                spacing: 8
                Icon { name: "candle"; sz: 14; tint: backend.c.accent }
                Label { text: backend.s.chartLook; font.pixelSize: 13; font.bold: true; color: backend.c.fg }
                Item { Layout.fillWidth: true }
                Btn { text: backend.s.resetLook; iconName: "rotate"; outline: true
                      implicitHeight: 30; font.pixelSize: 10
                      onClicked: backend.resetChartTheme() }
            }
            Label {
                text: backend.s.lookHint; font.pixelSize: 10; color: backend.c.sub
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }
            Repeater {
                model: [ { k: "bg", s: "cBg" }, { k: "bull", s: "cBull" }, { k: "bear", s: "cBear" },
                         { k: "grid", s: "cGrid" }, { k: "axisText", s: "cAxis" },
                         { k: "crosshair", s: "cCross" }, { k: "drawing", s: "cDraw" } ]
                delegate: RowLayout {
                    spacing: 8
                    property string curVal: {
                        try { return (JSON.parse(backend.chartThemeFullJson)[modelData.k] || "") } catch (e) { return "" }
                    }
                    property bool okCol: win.isColor(curVal) || win.isColor(colorField.text.trim())
                    Layout.fillWidth: true
                    Label { text: backend.s[modelData.s]; font.pixelSize: 11; color: backend.c.fg; Layout.preferredWidth: 128 }
                    Rectangle {
                        width: 24; height: 24; radius: 8
                        color: win.isColor(colorField.text.trim()) ? colorField.text.trim()
                             : (win.isColor(curVal) ? curVal : "transparent")
                        border.width: 1; border.color: backend.c.border
                        /* النقر على المربّع يفتح نافذة اختيار لون حرة — بلا قوائم محدودة (طلب المستخدم) */
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                chartColorPicker.targetKey = modelData.k
                                chartColorPicker.selectedColor = win.isColor(curVal) ? curVal : "#22c55e"
                                chartColorPicker.open()
                            }
                        }
                    }
                    Field {
                        id: colorField
                        Layout.fillWidth: true; Layout.preferredHeight: 34
                        font.pixelSize: 11; font.family: "monospace"
                        color: win.isColor(text.trim()) ? backend.c.fg : backend.c.bad
                        text: curVal
                        placeholderText: "#RRGGBB"
                        selectByMouse: true
                        onEditingFinished: {
                            var v = text.trim()
                            if (!win.isColor(v)) return
                            if (v === curVal) return
                            var o = {}; o[modelData.k] = v
                            backend.setChartTheme(JSON.stringify(o))
                        }
                    }
                }
            }
            /* ───── BADI: المفتاح المشفر يبقى داخل التطبيق — بصمته فقط تُعرض هنا ───── */
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border }
            Label { text: backend.s.badiSect; font.pixelSize: 13; font.bold: true; color: backend.c.fg }
            /* مجلد BadiCharts: المؤشرات والأدوات تُحفظ فيه كملفات حقيقية */
            ColumnLayout {
                Layout.fillWidth: true; spacing: 3
                Label { text: backend.s.badiFolder + ":"; font.pixelSize: 11; color: backend.c.sub }
                Label {
                    text: backend.badiDirPath(); font.pixelSize: 10; font.family: "monospace"
                    color: backend.c.accent; Layout.fillWidth: true
                    wrapMode: Text.WrapAnywhere
                }
                Label { text: backend.s.badiFolderHint; font.pixelSize: 10; color: backend.c.sub
                        wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            RowLayout {
                spacing: 8
                Icon { name: "lock"; sz: 14; tint: backend.c.accent }
                Label { text: backend.s.keyFp; font.pixelSize: 11; color: backend.c.sub }
                Label {
                    text: backend.badiFp; font.pixelSize: 11; font.bold: true
                    color: backend.c.fg; font.family: "monospace"
                }
                Item { Layout.fillWidth: true }
                /* لا يوجد أي زر نسخ للمفتاح — المفتاح يبقى مخبأ داخل الكود فقط (طلب المستخدم) */
            }
            Label {
                text: backend.s.badiHint; font.pixelSize: 10; color: backend.c.sub
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }
            }
        }
    }

    /* ═══════ بطاقة الإشعارات الصغيرة (طلب المستخدم): ليست صفحة كبيرة — بطاقة تحت الزر.
       بلا إشعارات جاهزة إطلاقًا: المبرمج يرسلها من خادمه عبر أمر notify فقط ═══════ */
    Popup {
        id: notifPop
        parent: Overlay.overlay
        width: Math.min(360, win.width - 24)
        height: Math.min(430, win.height - 120)
        x: win.width - width - 14
        y: 62
        padding: 0
        modal: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle {
            radius: 14; color: backend.c.card
            border.width: 1; border.color: backend.c.border
        }
        contentItem: ColumnLayout {
            spacing: 10
            /* رأس البطاقة (تصميم محسّن — طلب المستخدم): شارة جرس متدرجة + عنوان
               + سطر حالة + عدّاد أحمر + إغلاق */
            RowLayout {
                spacing: 10
                Rectangle {
                    width: 38; height: 38; radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0; color: backend.c.g1 }
                        GradientStop { position: 1; color: backend.c.g2 }
                    }
                    Icon { anchors.centerIn: parent; name: "bell"; sz: 18; tint: "#FFFFFF" }
                }
                ColumnLayout {
                    spacing: 1
                    Layout.fillWidth: true
                    Label { text: backend.s.notifT; font.pixelSize: 15; font.bold: true; color: backend.c.fg }
                    Label {
                        text: backend.notifsUnread > 0
                              ? backend.s.notifUnreadX.arg(backend.notifsUnread)
                              : backend.s.notifAllRead
                        font.pixelSize: 10; color: backend.c.sub
                    }
                }
                Label {
                    text: backend.notifsUnread
                    visible: backend.notifsUnread > 0
                    font.pixelSize: 10; font.bold: true; color: "#FFFFFF"
                    leftPadding: 8; rightPadding: 8; topPadding: 3; bottomPadding: 3
                    background: Rectangle { radius: 9; color: "#FF4D5E" }
                }
                IBtn { iconName: "x"; onClicked: notifPop.close() }
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border; opacity: 0.8 }
            /* الحالة الفارغة — بطاقة أيقونة كبيرة أنيقة بدل جرس باهت صغير */
            ColumnLayout {
                visible: backend.notifs.length === 0
                Layout.fillWidth: true
                spacing: 8
                Item { Layout.fillWidth: true; implicitHeight: 26 }
                Rectangle {
                    width: 64; height: 64; radius: 20; Layout.alignment: Qt.AlignHCenter
                    color: Qt.rgba(0.08, 0.55, 0.96, 0.10)
                    border.width: 1; border.color: Qt.rgba(0.08, 0.55, 0.96, 0.22)
                    Icon { anchors.centerIn: parent; name: "bell"; sz: 28; tint: backend.c.accent }
                }
                Label { text: backend.s.notifEmpty; font.pixelSize: 13; font.bold: true
                        color: backend.c.fg; Layout.alignment: Qt.AlignHCenter }
                Label { text: backend.s.notifHint; font.pixelSize: 10; color: backend.c.sub
                        wrapMode: Text.WordWrap; Layout.fillWidth: true
                        Layout.maximumWidth: 290
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter }
                Item { Layout.fillWidth: true; implicitHeight: 14 }
            }
            ListView {
                id: notifList
                visible: backend.notifs.length > 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 8
                model: backend.notifs
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: SlimBar { }
                delegate: Rectangle {
                    width: notifList.width
                    height: ncol.implicitHeight + 22
                    radius: 12
                    color: backend.c.bg
                    border.width: 1
                    border.color: modelData.read ? backend.c.border : Qt.rgba(0.08, 0.55, 0.96, 0.5)
                    /* شريط جانبي أزرق للإشعار غير المقروء */
                    Rectangle {
                        x: 0; y: 10
                        width: 3; height: parent.height - 20; radius: 2
                        color: backend.c.accent
                        visible: !modelData.read
                    }
                    ColumnLayout {
                        id: ncol
                        x: 14; y: 11
                        width: parent.width - 28
                        spacing: 4
                        RowLayout {
                            Layout.fillWidth: true; spacing: 6
                            Rectangle {
                                width: 7; height: 7; radius: 3.5
                                color: backend.c.accent
                                visible: !modelData.read
                            }
                            Label {
                                text: modelData.t
                                font.pixelSize: 12; font.bold: !modelData.read
                                color: backend.c.fg
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                        RowLayout {
                            spacing: 5
                            Icon { name: "clock"; sz: 10; tint: backend.c.sub }
                            Label {
                                text: (modelData.ind ? modelData.ind + " · " : "")
                                      + Qt.formatDateTime(new Date(modelData.at * 1000), "dd/MM hh:mm")
                                font.pixelSize: 9; color: backend.c.sub
                            }
                        }
                    }
                }
            }
            RowLayout {
                spacing: 8
                Item { Layout.fillWidth: true }
                Btn {
                    text: backend.s.notifClear; iconName: "trash"; outline: true
                    implicitHeight: 30; font.pixelSize: 10
                    visible: backend.notifs.length > 0
                    onClicked: backend.notifsClear()
                }
            }
        }
    }

    /* نافذة اختيار لون حرة لألوان الشارت — أي لون وليس قوائم محدودة (طلب المستخدم) */
    ColorDialog {
        id: chartColorPicker
        title: backend.s.pickColor
        options: ColorDialog.ShowAlphaControls
        property string targetKey: ""
        onAccepted: {
            var c = String(selectedColor)
            if (!win.isColor(c) || !targetKey) return
            var o = {}; o[targetKey] = c
            backend.setChartTheme(JSON.stringify(o))
        }
    }

    /* حوار اختيار ملف .badi المشفر — فك التشفير يجري داخل التطبيق بمفتاحه */
    FileDialog {
        id: badiOpenDialog
        title: backend.s.badiImp
        nameFilters: ["BADI encrypted indicator (*.badi)", "All files (*)"]
        onAccepted: win.badiImportAt(badiOpenDialog.selectedFile)
    }

    /* ───── حوار ترخيص المؤشر المشفر (طلب المستخدم) ─────
       البائع يضع معرّف المشتري (USER ID) ثم يشفّر — المؤشر لا يعمل إلا على جهاز
       يطابق معرّفه المدمج. فارغ = يعمل مع الجميع. المعرف يُفحص صيغةً قبل التشفير. */
    Popup {
        id: licPop
        parent: Overlay.overlay
        onOpened: { paidSrvField.text = ""; paidIdField.text = "" }
        anchors.centerIn: Overlay.overlay
        width: Math.min(430, win.width - 48)
        padding: 16
        modal: true
        closePolicy: Popup.CloseOnEscape
        background: Rectangle {
            radius: 16; color: backend.c.card
            border.width: 1; border.color: backend.c.border
        }
        contentItem: ColumnLayout {
            spacing: 10
            RowLayout {
                spacing: 9
                Rectangle {
                    width: 34; height: 34; radius: 10
                    color: Qt.rgba(0.08, 0.55, 0.96, 0.14)
                    Icon { anchors.centerIn: parent; name: "lock"; sz: 17; tint: backend.c.accent }
                }
                Label { text: backend.s.licTitle; font.pixelSize: 15; font.bold: true
                        color: backend.c.fg; Layout.fillWidth: true
                        elide: Text.ElideRight }
                IBtn { iconName: "x"; onClicked: licPop.close() }
            }
            Label {
                text: backend.s.licHint
                font.pixelSize: 11; color: backend.c.sub
                wrapMode: Text.WordWrap; Layout.fillWidth: true
            }
            TextField {
                id: licField
                Layout.fillWidth: true
                implicitHeight: 42
                font.pixelSize: 13; font.bold: true; font.letterSpacing: 1
                font.family: "monospace"
                color: backend.c.fg
                placeholderText: "BADI-7K9X-4M2P-8Q6R, BADI-8F3K-2T9W-5H1D"
                placeholderTextColor: backend.c.sub
                verticalAlignment: TextInput.AlignVCenter
                selectByMouse: true
                leftPadding: 12; rightPadding: 12
                background: Rectangle {
                    radius: 10; color: backend.c.bg
                    border.width: licField.activeFocus ? 2 : 1
                    border.color: licField.activeFocus ? backend.c.accent : backend.c.border
                }
                onAccepted: win.badiExportConfirm()
            }
            /* حقول المؤشر المدفوع (طلب المستخدم): خادم المبرمج + معرف المؤشر عنده —
               يُدمان داخل المغلف المشفر نفسه، والتحكم لاحقًا من خادمه فقط بأوامر بيضاء */
            Label { text: backend.s.paidSrvLbl; font.pixelSize: 11; color: backend.c.sub
                    wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField {
                id: paidSrvField
                Layout.fillWidth: true
                implicitHeight: 38
                font.pixelSize: 12
                color: backend.c.fg
                placeholderText: "https://your-server.com/badi/api"
                placeholderTextColor: backend.c.sub
                selectByMouse: true
                leftPadding: 12; rightPadding: 12
                background: Rectangle {
                    radius: 10; color: backend.c.bg
                    border.width: paidSrvField.activeFocus ? 2 : 1
                    border.color: paidSrvField.activeFocus ? backend.c.accent : backend.c.border
                }
            }
            Label { text: backend.s.paidIdLbl; font.pixelSize: 11; color: backend.c.sub
                    wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField {
                id: paidIdField
                Layout.fillWidth: true
                implicitHeight: 38
                font.pixelSize: 12; font.family: "monospace"
                color: backend.c.fg
                placeholderText: "PRO_SIGNAL_1"
                placeholderTextColor: backend.c.sub
                selectByMouse: true
                leftPadding: 12; rightPadding: 12
                background: Rectangle {
                    radius: 10; color: backend.c.bg
                    border.width: paidIdField.activeFocus ? 2 : 1
                    border.color: paidIdField.activeFocus ? backend.c.accent : backend.c.border
                }
            }
            /* معرّف هذا الجهاز — نسخة سريعة ليرسلها المشتري للبائع */
            Rectangle {
                Layout.fillWidth: true; implicitHeight: 40; radius: 10
                color: backend.c.bg; border.width: 1; border.color: backend.c.border
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 8; spacing: 8
                    Label { text: backend.s.yourUid; font.pixelSize: 11; color: backend.c.sub }
                    Label { text: backend.userId; font.pixelSize: 13; font.bold: true
                            color: backend.c.accent; Layout.fillWidth: true; elide: Text.ElideRight }
                    IBtn { iconName: "copy"; onClicked: backend.copyText(backend.userId) }
                }
            }
            RowLayout {
                spacing: 8
                Item { Layout.fillWidth: true }
                Btn { text: backend.s.licCancel; iconName: "x"; outline: true
                      implicitHeight: 34; onClicked: { win.pendingExport = null; licPop.close() } }
                Btn { id: licPopConfirm; text: backend.s.licOk; iconName: "lock"; implicitHeight: 34
                      onClicked: win.badiExportConfirm() }
            }
        }
    }

    /* تنبيه سريع (توست) — نتيجة المشاركة وغيرها */
    Popup {
        id: toastPop
        parent: Overlay.overlay
        width: Math.min(480, win.width - 48)
        x: (parent ? (parent.width - width) / 2 : 0)
        y: parent ? parent.height - 130 : 0
        padding: 12
        modal: false
        closePolicy: Popup.NoAutoClose
        property string toastText: ""
        property bool toastIsErr: false
        background: Rectangle {
            radius: 12
            color: backend.dark ? "#101418" : "#FFFFFF"
            border.width: 1
            border.color: toastPop.toastIsErr ? backend.c.bad : backend.c.border
        }
        contentItem: RowLayout {
            spacing: 10
            Icon { name: toastPop.toastIsErr ? "no" : "ok"; sz: 20
                   tint: toastPop.toastIsErr ? backend.c.bad : backend.c.good }
            Label {
                text: toastPop.toastText
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                font.pixelSize: 12
                color: backend.c.fg
            }
        }
        function show(err, txt) {
            toastPop.toastIsErr = err
            toastPop.toastText = txt
            open()
            toastTimer.restart()
        }
        Timer { id: toastTimer; interval: 3600; onTriggered: toastPop.close() }
    }

    /* عارض صورة المؤشر المكبر — بحجم الصفحة مع سهم رجوع (طلب المستخدم) */
    Popup {
        id: thumbPop
        parent: Overlay.overlay
        anchors.centerIn: Overlay.overlay
        width: Math.min(1080, (parent ? parent.width : 800) - 48)
        height: (parent ? parent.height : 600) - 84
        padding: 14
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        property string src: ""
        property string indName: ""
        function openThumb(url, nm) { thumbPop.src = url; thumbPop.indName = nm; open() }
        background: Rectangle {
            radius: 18
            color: backend.c.side
            border.width: 1
            border.color: backend.c.border
        }
        contentItem: ColumnLayout {
            spacing: 10
            RowLayout {
                spacing: 8
                /* سهم الرجوع (اتجاهه يتبع لغة الواجهة) */
                IBtn { iconName: backend.rtl ? "chevr" : "chevl"; onClicked: thumbPop.close() }
                Label {
                    text: thumbPop.indName
                    font.pixelSize: 14; font.bold: true
                    color: backend.c.fg
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                IBtn { iconName: "x"; onClicked: thumbPop.close() }
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                Image {
                    anchors.centerIn: parent
                    source: thumbPop.src
                    fillMode: Image.PreserveAspectFit
                    sourceSize: Qt.size(thumbPop.width, thumbPop.height)
                    smooth: true
                }
            }
        }
    }

    // ════════════════ المحتوى ════════════════
    StackLayout {
        id: mainStack
        anchors.fill: parent
        currentIndex: win.splash ? 0 : (win.loggedIn ? 2 : 1)

        // ─────────── شاشة الشعار (BadiCharts) — حركة الظهور المطلوبة نفسها تماماً ───────────
        // صفحة الديمو نفسها (splash.html): رسم الأيقونة خطاً خطاً، نبضة الجسم، صعود الحروف،
        // اللمعة العابرة، ثم ظهور السطر النصي — نقرة تُخطي الشاشة.
        Item {
            WebEngineView {
                id: splashWeb
                anchors.fill: parent
                // splashUrl غير متاح في بعض سكربتات الفحص القديمة — احتياط حتى لا تنكسر
                url: (typeof splashUrl !== "undefined" && splashUrl) ? splashUrl : ""
                backgroundColor: backend.dark ? "#000000" : "#FFFFFF"
            }
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.splash = false }
            Timer { interval: 3900; running: win.splash; onTriggered: win.splash = false }
        }

        // ─────────── تسجيل الدخول — الواجهة الجديدة (طلب المستخدم) ───────────
        // جهة تعريفية (شعار + شارة + عنوان كبير + مميزات) | فاصل | بطاقة الدخول
        // فوقها خلفية حية: شبكة نقاط + توهج + شموع متحركة خفيفة
        Item {
            id: loginPage
            clip: true
            property real t: 0
            property bool busy: false
            property bool ok: false
            property bool remember: true
            property string err: ""
            property string qxStatus: ""       // LIVE SERVER EDITION: خط تقدم الاتصال بالخادم
            readonly property int ha: backend.rtl ? Text.AlignRight : Text.AlignLeft
            readonly property int al: backend.rtl ? Qt.AlignRight : Qt.AlignLeft
            function ease(i) {
                var v = Math.max(0, Math.min(1, t * 1.8 - i * 0.14))
                return 1 - Math.pow(1 - v, 3)
            }
            NumberAnimation { id: enterAnim; target: loginPage; property: "t"; from: 0; to: 1; duration: 1300 }
            Component.onCompleted: {
                enterAnim.restart()
                /* LIVE SERVER EDITION: تعبئة البريد المحفوظ لدى الخادم (تذكّرني) */
                try { userF.text = backend.savedEmail } catch (e) {}
            }
            /* v15.2 (طلب المستخدم): البريد المحفوظ («تذكّرني») يظهر معبأ في
               واجهة تسجيل الدخول في كل مرة تظهر فيها الصفحة */
            onVisibleChanged: {
                if (visible) {
                    t = 0
                    enterAnim.restart()
                    try { userF.text = backend.savedEmail } catch (e) {}
                }
            }

            function attempt() {
                if (busy) return
                ok = false
                if (userF.text.trim() === "" || passF.text === "") {
                    err = backend.s.errEmpty
                    shake.restart()
                    return
                }
                err = ""
                qxStatus = ""
                busy = true
                /* LIVE SERVER EDITION (طلب المستخدم): تسجيل الدخول الوهمي انزع —
                   الدخول حقيقي الآن عبر خادم Quotex الخاص بنا (qx_server_v13):
                   نفس connect_quotex، نفس الجلسة، ونفس طريقة جلب الشموع الأصلية */
                backend.qxLogin(userF.text.trim(), passF.text, remember)
            }

            // ── الخلفية ──
            Rectangle { anchors.fill: parent; color: backend.c.bg }   /* أساس الصفحة */
            DotGrid { anchors.fill: parent }
            Glow {
                width: 900; height: 900; y: -520
                x: (parent.width - width) / 2
                col: backend.dark ? "#FFFFFF" : "#2F5BF0"; amt: 0.05
            }
            Glow {
                width: 700; height: 700
                anchors.right: parent.right; anchors.rightMargin: -240
                anchors.bottom: parent.bottom; anchors.bottomMargin: -300
                col: backend.c.g2; amt: backend.dark ? 0.10 : 0.07
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.4; duration: 5200; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 5200; easing.type: Easing.InOutSine }
                }
            }
            ChartBg { anchors.fill: parent }

            // تذييل خفيف يملأ أسفل الصفحة
            Row {
                anchors.bottom: parent.bottom; anchors.bottomMargin: 14
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                opacity: loginPage.ease(2.5)
                Label { text: "BADI STUDIO v2.13.1"; font.pixelSize: 10; font.bold: true
                        font.letterSpacing: 1.4; color: backend.c.sub }
                Label { text: "·"; font.pixelSize: 10; color: backend.c.border }
                Label { text: "© BadiCharts"; font.pixelSize: 10; color: backend.c.sub }
            }

            RowLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width - 64, 1120)
                spacing: 40
                LayoutMirroring.enabled: backend.rtl
                LayoutMirroring.childrenInherit: false

                // ═════ الجهة التعريفية ═════
                ColumnLayout {
                    id: hero
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 16

                    // الشعار
                    Row {
                        Layout.alignment: loginPage.al
                        spacing: 10
                        layoutDirection: backend.rtl ? Qt.RightToLeft : Qt.LeftToRight
                        opacity: loginPage.ease(0)
                        Image {
                            width: 40; height: 40
                            source: backend.mark(backend.dark)
                            sourceSize: Qt.size(80, 80); smooth: true
                        }
                        Label {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Badi<font color='" + backend.c.accent + "'>Charts</font>"
                            textFormat: Text.RichText
                            font.pixelSize: 26; font.bold: true; color: backend.c.fg
                        }
                    }

                    // شارة صغيرة نابضة
                    Rectangle {
                        Layout.alignment: loginPage.al
                        implicitWidth: pillRow.implicitWidth + 28; implicitHeight: 30; radius: 15
                        color: backend.c.card
                        border.width: 1; border.color: backend.c.border
                        opacity: loginPage.ease(0.5)
                        transform: Translate { y: (1 - loginPage.ease(0.5)) * 24 }
                        Row {
                            id: pillRow
                            anchors.centerIn: parent; spacing: 8
                            layoutDirection: backend.rtl ? Qt.RightToLeft : Qt.LeftToRight
                            Rectangle {
                                width: 8; height: 8; radius: 4; color: backend.c.accent
                                anchors.verticalCenter: parent.verticalCenter
                                SequentialAnimation on opacity {
                                    loops: Animation.Infinite
                                    NumberAnimation { to: 0.25; duration: 900 }
                                    NumberAnimation { to: 1.0; duration: 900 }
                                }
                            }
                            Label { text: backend.s.badge; font.pixelSize: 12; font.bold: true
                                    font.letterSpacing: 1; color: backend.c.sub }
                        }
                    }

                    // العنوان الكبير
                    Label {
                        Layout.fillWidth: true
                        text: backend.s.h1 + "<br><font color='" + backend.c.accent + "'>" + backend.s.h2 + "</font>"
                        textFormat: Text.RichText
                        wrapMode: Text.WordWrap
                        horizontalAlignment: loginPage.ha
                        font.pixelSize: 36; font.bold: true; lineHeight: 1.12
                        color: backend.c.fg
                        opacity: loginPage.ease(1)
                        transform: Translate { y: (1 - loginPage.ease(1)) * 30 }
                    }

                    // السطر التعريفي
                    Label {
                        Layout.fillWidth: true; Layout.maximumWidth: 520
                        Layout.alignment: loginPage.al
                        text: backend.s.lead
                        wrapMode: Text.WordWrap
                        horizontalAlignment: loginPage.ha
                        font.pixelSize: 15; lineHeight: 1.25
                        color: backend.c.sub
                        opacity: loginPage.ease(1.5)
                        transform: Translate { y: (1 - loginPage.ease(1.5)) * 30 }
                    }

                    // شبكة المميزات 2×3
                    GridLayout {
                        Layout.fillWidth: true; Layout.topMargin: 8
                        columns: 2; columnSpacing: 12; rowSpacing: 12
                        layoutDirection: backend.rtl ? Qt.RightToLeft : Qt.LeftToRight
                        Repeater {
                            model: [ { i: "code", k: "f1" }, { i: "zap", k: "f2" }, { i: "bell", k: "f3" },
                                     { i: "camera", k: "f4" }, { i: "wallet", k: "f5" }, { i: "panel", k: "f6" } ]
                            delegate: Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredWidth: 100
                                Layout.preferredHeight: 64
                                radius: 14
                                color: lh.hovered ? backend.c.hover : backend.c.card
                                border.width: 1
                                border.color: lh.hovered ? backend.c.accent : backend.c.border
                                Behavior on color { ColorAnimation { duration: 120 } }
                                Behavior on border.color { ColorAnimation { duration: 120 } }
                                opacity: loginPage.ease(2 + index * 0.5)
                                transform: Translate { y: (1 - loginPage.ease(2 + index * 0.5)) * 26 }
                                HoverHandler { id: lh }
                                RowLayout {
                                    anchors.fill: parent; anchors.margins: 10; spacing: 12
                                    layoutDirection: backend.rtl ? Qt.RightToLeft : Qt.LeftToRight
                                    Rectangle {
                                        implicitWidth: 36; implicitHeight: 36; radius: 11
                                        Layout.alignment: Qt.AlignVCenter
                                        color: backend.c.hover
                                        Icon { anchors.centerIn: parent; name: modelData.i; sz: 26
                                               tint: lh.hovered ? backend.c.accent : backend.c.fg }
                                    }
                                    Label {
                                        Layout.fillWidth: true
                                        text: backend.s[modelData.k]
                                        wrapMode: Text.WordWrap; maximumLineCount: 3; elide: Text.ElideRight
                                        horizontalAlignment: loginPage.ha
                                        font.pixelSize: 12; color: backend.c.fg
                                    }
                                }
                            }
                        }
                    }
                }

                // فاصل عمودي متلاشى الطرفين
                Rectangle {
                    Layout.preferredWidth: 1; Layout.preferredHeight: 400
                    Layout.alignment: Qt.AlignVCenter
                    opacity: loginPage.ease(1)
                    gradient: Gradient {
                        GradientStop { position: 0; color: "transparent" }
                        GradientStop { position: 0.5; color: backend.c.border }
                        GradientStop { position: 1; color: "transparent" }
                    }
                }

                // ═════ بطاقة الدخول ═════
                Item {
                    id: cardWrap
                    Layout.preferredWidth: 400
                    Layout.preferredHeight: 520
                    Layout.alignment: Qt.AlignVCenter
                    property real shakeX: 0
                    /* تحويل صريح إلى لون — c.card نص في بايثون ولا يحمل .r مباشرة */
                    readonly property color cc: backend.c.card
                    opacity: loginPage.ease(1)
                    transform: Translate { x: cardWrap.shakeX; y: (1 - loginPage.ease(1)) * 40 }

                    SequentialAnimation {
                        id: shake
                        NumberAnimation { target: cardWrap; property: "shakeX"; to: -12; duration: 50 }
                        NumberAnimation { target: cardWrap; property: "shakeX"; to: 10; duration: 80 }
                        NumberAnimation { target: cardWrap; property: "shakeX"; to: -7; duration: 80 }
                        NumberAnimation { target: cardWrap; property: "shakeX"; to: 5; duration: 70 }
                        NumberAnimation { target: cardWrap; property: "shakeX"; to: 0; duration: 60 }
                    }

                    Rectangle {
                        anchors.fill: parent; radius: 26
                        gradient: Gradient {
                            GradientStop { position: 0; color: backend.c.g1 }
                            GradientStop { position: 1; color: backend.c.g2 }
                        }
                    }
                    Rectangle {
                        anchors.fill: parent; anchors.margins: 1.5; radius: 24.5
                        color: Qt.rgba(cardWrap.cc.r, cardWrap.cc.g, cardWrap.cc.b, 0.96)
                    }

                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 32; spacing: 12

                        Rectangle {
                            Layout.alignment: loginPage.al
                            implicitWidth: 46; implicitHeight: 46; radius: 14
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0; color: backend.c.g1 }
                                GradientStop { position: 1; color: backend.c.g2 }
                            }
                            Icon { anchors.centerIn: parent; name: "idcard"; sz: 28; tint: "#FFFFFF" }
                        }
                        Label {
                            Layout.fillWidth: true; Layout.topMargin: 4
                            text: backend.s.welcome
                            horizontalAlignment: loginPage.ha
                            font.pixelSize: 25; font.bold: true; color: backend.c.fg
                        }
                        Label {
                            Layout.fillWidth: true
                            text: backend.s.cardSub
                            wrapMode: Text.WordWrap
                            horizontalAlignment: loginPage.ha
                            font.pixelSize: 12; color: backend.c.sub
                        }
                        Item { Layout.preferredHeight: 6 }

                        IField {
                            id: userF
                            Layout.fillWidth: true; implicitHeight: 52
                            font.pixelSize: 14; iconName: "user"
                            placeholderText: backend.s.user
                            onTextChanged: { loginPage.err = ""; loginPage.ok = false }
                            Keys.onReturnPressed: passF.forceActiveFocus()
                        }
                        IField {
                            id: passF
                            Layout.fillWidth: true; implicitHeight: 52
                            font.pixelSize: 14; iconName: "lock"; secret: true
                            placeholderText: backend.s.pass
                            onTextChanged: { loginPage.err = ""; loginPage.ok = false }
                            Keys.onReturnPressed: loginPage.attempt()
                        }

                        // تذكّرني
                        Item {
                            Layout.alignment: loginPage.al
                            implicitWidth: remRow.implicitWidth; implicitHeight: 26
                            Row {
                                id: remRow; spacing: 9; anchors.verticalCenter: parent.verticalCenter
                                layoutDirection: backend.rtl ? Qt.RightToLeft : Qt.LeftToRight
                                Rectangle {
                                    width: 20; height: 20; radius: 6
                                    anchors.verticalCenter: parent.verticalCenter
                                    color: loginPage.remember ? backend.c.accent : "transparent"
                                    border.width: 1
                                    border.color: loginPage.remember ? backend.c.accent : backend.c.border
                                    Behavior on color { ColorAnimation { duration: 120 } }
                                    Icon { anchors.centerIn: parent; name: "check"; sz: 20; tint: "#FFFFFF"
                                           visible: loginPage.remember }
                                }
                                Label { text: backend.s.remember; font.pixelSize: 12; color: backend.c.sub
                                        anchors.verticalCenter: parent.verticalCenter }
                            }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: loginPage.remember = !loginPage.remember }
                        }

                        // LIVE SERVER EDITION: خط تقدم الاتصال الحقيقي بالخادم
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
                            text: loginPage.ok ? backend.s.signinok : loginPage.err
                            opacity: (loginPage.ok || loginPage.err !== "") ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: 150 } }
                            horizontalAlignment: loginPage.ha
                            font.pixelSize: 12
                            color: loginPage.ok ? backend.c.good : backend.c.bad
                        }

                        Item { Layout.fillHeight: true }

                        Btn {
                            text: loginPage.busy ? backend.s.signing : backend.s.signin
                            iconName: loginPage.busy ? "loader" : "login"
                            fs: 14
                            Layout.fillWidth: true; implicitHeight: 54
                            enabled: !loginPage.busy
                            onClicked: loginPage.attempt()
                        }
                    }
                }
            }
        }

        // ─────────── التطبيق ───────────
        RowLayout {
            spacing: 0
            LayoutMirroring.enabled: backend.rtl
            StackLayout {
                id: appPages
                Layout.fillWidth: true; Layout.fillHeight: true
                currentIndex: win.page
'''
QML += r'''
                // ═══════ 0 — الاستوديو: صفحة HTML مدمجة (شارت BADI-CHARTS v2.13.0 + محرر Monaco) ═══════
                Item {
                    WebEngineView {
                        id: webView
                        objectName: "webView"
                        anchors.fill: parent
                        url: webUrl
                        settings.localContentCanAccessRemoteUrls: true
                        settings.localContentCanAccessFileUrls: true
                        settings.focusOnNavigationEnabled: true
                        settings.javascriptCanAccessClipboard: true
                        // ── الحافظة: منح إذن القراءة/الكتابة تلقائيًا حتى يعمل Ctrl+V داخل Monaco ──
                        onFeaturePermissionRequested: function (securityOrigin, feature) {
                            var clip = (typeof WebEngineView.ClipboardReadWrite !== "undefined") ? WebEngineView.ClipboardReadWrite : -1
                            webView.grantFeaturePermission(securityOrigin, feature, feature === clip)
                        }
                        // javascriptCanPaste غير موجودة قبل Qt 6.8 — تُضاف ديناميكيًا فقط إن كانت متاحة
                        Component.onCompleted: {
                            try { if ("javascriptCanPaste" in settings) settings.javascriptCanPaste = true } catch (e) {}
                        }
                        onJavaScriptConsoleMessage: function (level, message, line, sourceID) {
                            if (message.indexOf("BADI::") !== 0) return
                            var payload = message.substring(6)
                            var sp = payload.indexOf(" ")
                            if (sp < 0) return
                            win.onWebMessage(payload.substring(0, sp), payload.substring(sp + 1))
                        }
                        onRenderProcessTerminated: function (terminationStatus, exitCode) { webView.reload() }
                    }
                    // احتياط اللصق: Ctrl+V يستدعي لصق Chromium الأصلي مباشرة — لا يحتاج أي إذن
                    // ويعمل على كل الأنظمة. السياق مقصور على صفحة الاستوديو فقط
                    // حتى لا يسرق اللصق من حقول النص في نوافذ QML الأخرى.
                    Shortcut {
                        sequences: [StandardKey.Paste]
                        context: Qt.WidgetWithChildrenShortcut
                        onActivated: webView.triggerWebAction(WebEngineView.Paste)
                    }
                }

                // ═══════ 1 — المؤشرات: مؤشراتي (مجلد BadiCharts) + المكتبة الجاهزة ═══════
                Item {
                    id: pageInd
                    property var myInds: []
                    function refresh() {
                        try { myInds = JSON.parse(backend.myIndsJson) } catch (e) { myInds = [] }
                    }
                    function fileUrl(p) {
                        var s = String(p || "").replace(/\\/g, "/")
                        if (/^[A-Za-z]:/.test(s)) s = "/" + s      /* ويندوز: C:/ → /C:/ */
                        if (s.charAt(0) !== "/") s = "/" + s
                        /* encodeURI: يشفّر الفراغات والأحرف الخاصة في أسماء الملفات */
                        return encodeURI("file://" + s)
                    }
                    Component.onCompleted: pageInd.refresh()
                    Connections { target: backend; function onMyIndsChanged() { pageInd.refresh() } }
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 20; spacing: 12
                        LayoutMirroring.enabled: backend.rtl
                        LayoutMirroring.childrenInherit: true
                        RowLayout {
                            spacing: 10
                            /* زر الرجوع إلى الشارت من صفحة المؤشرات (طلب المستخدم) */
                            Btn { text: backend.s.backChart; iconName: backend.rtl ? "chevr" : "chevl"
                                  outline: true; implicitHeight: 34; font.pixelSize: 11
                                  onClicked: win.page = 0 }
                            Item { Layout.fillWidth: true }
                            Icon { name: "candle"; sz: 26; tint: backend.c.accent }
                            Label { text: backend.s.ind; font.pixelSize: 18; font.bold: true; color: backend.c.fg }
                            Item { Layout.fillWidth: true }
                            Btn { text: backend.s.rescan; iconName: "rotate"; outline: true; implicitHeight: 34
                                  onClicked: backend.rescanFiles() }
                        }
                        Flickable {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            contentWidth: width
                            contentHeight: indCol.implicitHeight + 20
                            clip: true
                            ScrollBar.vertical: SlimBar { }
                            ColumnLayout {
                                id: indCol
                                width: parent.width - 10
                                spacing: 16
                                // ─── مؤشراتي: كل ما في مجلد BadiCharts — يُكتشف تلقائيًا (طلب المستخدم) ───
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 10
                                    RowLayout {
                                        spacing: 8
                                        Icon { name: "file"; sz: 18; tint: backend.c.accent }
                                        Label { text: backend.s.myinds; font.pixelSize: 15; font.bold: true; color: backend.c.fg }
                                        Rectangle {
                                            implicitWidth: 26; implicitHeight: 20; radius: 10
                                            color: Qt.rgba(0.08, 0.55, 0.96, 0.14)
                                            Label { text: pageInd.myInds.length; anchors.centerIn: parent
                                                    font.pixelSize: 11; font.bold: true; color: backend.c.accent }
                                        }
                                        Item { Layout.fillWidth: true }
                                    }
                                    Label { text: backend.s.myindsHint; font.pixelSize: 11; color: backend.c.sub
                                            wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    GridLayout {
                                        Layout.fillWidth: true
                                        visible: pageInd.myInds.length > 0
                                        columns: Math.max(1, Math.floor(width / 330))
                                        columnSpacing: 12; rowSpacing: 12
                                        Repeater {
                                            model: pageInd.myInds
                                            delegate: Rectangle {
                                                id: myCard
                                                Layout.fillWidth: true
                                                Layout.preferredHeight: 224
                                                radius: 16
                                                color: backend.c.card
                                                border.width: 1
                                                border.color: modelData.enc ? Qt.rgba(0.08, 0.55, 0.96, 0.5) : backend.c.border
                                                ColumnLayout {
                                                    anchors.fill: parent; anchors.margins: 12; spacing: 7
                                                    /* الصورة المصغرة فوق اسم المؤشر — تُلتقط عند الحفظ فقط،
                                                       والنقر عليها يكبّرها (طلب المستخدم) */
                                                    Rectangle {
                                                        id: thumbBox
                                                        Layout.fillWidth: true
                                                        Layout.preferredHeight: 100
                                                        radius: 10
                                                        clip: true
                                                        color: backend.c.hover
                                                        border.width: 1; border.color: backend.c.border
                                                        Image {
                                                            anchors.fill: parent
                                                            source: modelData.thumb ? pageInd.fileUrl(modelData.thumb) : ""
                                                            /* المصغرة كاملة الظهور (طلب المستخدم): ملاءمة الأبعاد
                                                               تُظهر محتوى اللقطة كله لا جزءًا مقصوصًا منه */
                                                            fillMode: Image.PreserveAspectFit
                                                            smooth: true
                                                            asynchronous: true
                                                            visible: modelData.thumb !== ""
                                                        }
                                                        Column {
                                                            anchors.centerIn: parent; spacing: 6
                                                            visible: modelData.thumb === ""
                                                            Icon { name: "camera"; sz: 26; tint: backend.c.sub
                                                                   anchors.horizontalCenter: parent.horizontalCenter }
                                                            Label { text: backend.s.myindThumbNone; font.pixelSize: 10
                                                                    color: backend.c.sub
                                                                    anchors.horizontalCenter: parent.horizontalCenter }
                                                        }
                                                        MouseArea {
                                                            anchors.fill: parent
                                                            cursorShape: Qt.PointingHandCursor
                                                            enabled: modelData.thumb !== ""
                                                            onClicked: thumbPop.openThumb(pageInd.fileUrl(modelData.thumb), modelData.fileName)
                                                        }
                                                    }
                                                    /* اسم المؤشر + شارة التشفير — الحذف انتقل بجوار زر الإضافة (طلب المستخدم) */
                                                    RowLayout {
                                                        spacing: 6
                                                        Icon { visible: modelData.enc; name: "lock"; sz: 13; tint: backend.c.accent }
                                                        Label {
                                                            text: modelData.fileName
                                                            font.pixelSize: 13; font.bold: true; color: backend.c.fg
                                                            Layout.fillWidth: true
                                                            elide: Text.ElideRight
                                                        }
                                                    }
                                                    Label {
                                                        text: modelData.enc ? backend.s.kindbadi
                                                            : (modelData.kind === "py" ? backend.s.kindpy
                                                            : (modelData.kind === "tool" ? backend.s.kindtool : backend.s.kindjs))
                                                        font.pixelSize: 10
                                                        color: modelData.enc ? backend.c.accent : backend.c.sub
                                                    }
                                                    Item { Layout.fillHeight: true }
                                                    RowLayout {
                                                        spacing: 8
                                                        /* الإضافة إلى الشارت (المشفر يُفك داخليًا ويُشغل مباشرة) */
                                                        Btn {
                                                            Layout.fillWidth: true; implicitHeight: 34
                                                            text: backend.s.add; iconName: "plus"; fs: 12
                                                            onClicked: win.addMy(modelData.fileName, modelData.enc)
                                                        }
                                                        /* زر الحذف بجوار زر الإضافة مباشرة (طلب المستخدم) */
                                                        IBtn { iconName: "trash"; onClicked: backend.delMy(modelData.fileName) }
                                                        /* مشاركة عبر تلجرام — ينسخ ملف .badi المشفر */
                                                        IBtn { iconName: "send"; onClicked: win.shareMy(modelData.fileName) }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                Rectangle { Layout.fillWidth: true; height: 1; color: backend.c.border; opacity: 0.6 }
                                // ─── المكتبة الجاهزة ───
                                RowLayout {
                                    spacing: 8
                                    Icon { name: "zap"; sz: 18; tint: backend.c.accent }
                                    Label { text: backend.s.f2; font.pixelSize: 15; font.bold: true; color: backend.c.fg }
                                    Item { Layout.fillWidth: true }
                                    Label { text: backend.s.libDesc; font.pixelSize: 11; color: backend.c.sub
                                            Layout.maximumWidth: 420; wrapMode: Text.WordWrap }
                                }
                                GridLayout {
                                    id: libGrid
                                    Layout.fillWidth: true
                                    columns: Math.max(1, Math.floor(width / 330))
                                    columnSpacing: 12; rowSpacing: 12
                                    Repeater {
                                        model: backend.libs
                                        delegate: Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 148
                                            radius: 16
                                            color: backend.c.card
                                            border.width: 1; border.color: backend.c.border
                                            ColumnLayout {
                                                anchors.fill: parent; anchors.margins: 14; spacing: 6
                                                RowLayout {
                                                    spacing: 8
                                                    Rectangle {
                                                        width: 34; height: 34; radius: 10
                                                        color: Qt.rgba(0.08, 0.55, 0.96, 0.14)
                                                        Icon { anchors.centerIn: parent; name: "trend"; sz: 19; tint: backend.c.g1 }
                                                    }
                                                    ColumnLayout {
                                                        spacing: 0
                                                        Label { text: modelData.name; font.pixelSize: 14; font.bold: true; color: backend.c.fg }
                                                        Label { text: backend.s.kindjs; font.pixelSize: 10; color: backend.c.sub }
                                                    }
                                                    Item { Layout.fillWidth: true }
                                                }
                                                Label { text: modelData.desc; font.pixelSize: 11; color: backend.c.sub
                                                        wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                Item { Layout.fillHeight: true }
                                                Btn {
                                                    Layout.fillWidth: true; implicitHeight: 36
                                                    text: backend.s.add; iconName: "plus"
                                                    onClicked: win.addLib(modelData.key)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // ═══════ 2 — الإشارات ═══════
                Item {
                    id: sigPage
                    property string token: ""
                    property bool attach: true
                    property string status: ""
                    Component.onCompleted: {
                        var d = JSON.parse(backend.loadTg())
                        sigPage.token = d.token; sigPage.attach = d.attach
                    }
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 20; spacing: 12
                        LayoutMirroring.enabled: backend.rtl
                        LayoutMirroring.childrenInherit: true
                        RowLayout {
                            spacing: 10
                            Icon { name: "send"; sz: 24; tint: backend.c.accent }
                            Label { text: backend.s.tgbot; font.pixelSize: 18; font.bold: true; color: backend.c.fg }
                            Item { Layout.fillWidth: true }
                            Btn { text: backend.s.backchart; iconName: "chevl"; outline: true
                                  onClicked: win.page = 0 }
                        }
                        RowLayout {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            spacing: 14
                            Rectangle {
                                Layout.fillWidth: true; Layout.fillHeight: true
                                Layout.maximumWidth: 470
                                radius: 16; color: backend.c.card; border.width: 1; border.color: backend.c.border
                                ColumnLayout {
                                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                                    Label { text: "Telegram"; font.pixelSize: 14; font.bold: true; color: backend.c.fg }
                                    Label { text: backend.s.token; font.pixelSize: 11; color: backend.c.sub }
                                    Field {
                                        Layout.fillWidth: true
                                        placeholderText: "123456789:AAxxxxxxx"
                                        text: sigPage.token
                                        onTextEdited: sigPage.token = text
                                    }
                                    /* لا حقل لمعرف المحادثة ولا قالب رسالة هنا — معرف المحادثة
                                       يضعه مبرمج المؤشر داخل كود المؤشر نفسه (طلب المستخدم) */
                                    Label {
                                        text: backend.s.tghint
                                        font.pixelSize: 11; color: backend.c.sub
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                    RowLayout {
                                        spacing: 10
                                        Rectangle {
                                            width: 42; height: 22; radius: 11
                                            color: sigPage.attach ? backend.c.accent : backend.c.hover
                                            border.width: sigPage.attach ? 0 : 1
                                            border.color: backend.c.border
                                            Behavior on color { ColorAnimation { duration: 120 } }
                                            Rectangle {
                                                x: sigPage.attach ? parent.width - width - 3 : 3
                                                width: 16; height: 16; radius: 8
                                                anchors.verticalCenter: parent.verticalCenter
                                                color: "#FFFFFF"
                                                Behavior on x { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
                                            }
                                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: sigPage.attach = !sigPage.attach }
                                        }
                                        Label { text: backend.s.attach; font.pixelSize: 12; color: backend.c.fg }
                                        Item { Layout.fillWidth: true }
                                    }
                                    RowLayout {
                                        spacing: 10
                                        Btn {
                                            text: backend.s.save; iconName: "check"
                                            onClicked: {
                                                backend.saveTg(sigPage.token, "",
                                                               JSON.stringify({ attach: sigPage.attach }))
                                                sigPage.status = backend.s.saved
                                            }
                                        }
                                        Label { text: sigPage.status; font.pixelSize: 11; color: backend.c.good }
                                        Item { Layout.fillWidth: true }
                                    }
                                    /* طلب المستخدم: بطاقة تحت زر الحفظ تعرض التوكن المحفوظ مختصرًا (يظهر قليلًا منه)
                                       وبجانبه أيقونة حذف — وبوت واحد فقط: التوكن الجديد يستبدل السابق */
                                    Rectangle {
                                        visible: sigPage.token !== ""
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 46
                                        radius: 12
                                        color: backend.c.bg; border.width: 1; border.color: backend.c.border
                                        RowLayout {
                                            anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 8; spacing: 8
                                            Icon { name: "lock"; sz: 14; tint: backend.c.good }
                                            ColumnLayout {
                                                spacing: 0
                                                Layout.fillWidth: true
                                                Label { text: backend.s.tgsave1; font.pixelSize: 9; font.bold: true; color: backend.c.sub }
                                                Label {
                                                    text: sigPage.token.length > 24 ? sigPage.token.substring(0, 14) + "…" + sigPage.token.substring(sigPage.token.length - 4) : sigPage.token
                                                    font.pixelSize: 11; font.family: "monospace"; color: backend.c.fg
                                                    Layout.fillWidth: true; elide: Text.ElideRight
                                                }
                                            }
                                            Rectangle {
                                                width: 30; height: 30; radius: 8
                                                color: tgDelMa.containsMouse ? Qt.rgba(0.94, 0.27, 0.27, 0.14) : "transparent"
                                                Icon { name: "trash"; sz: 14; tint: backend.c.bad; anchors.centerIn: parent }
                                                MouseArea {
                                                    id: tgDelMa; anchors.fill: parent; hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        backend.saveTg("", "", JSON.stringify({ attach: sigPage.attach }))
                                                        sigPage.token = ""
                                                        sigPage.status = backend.s.tgcleared
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    Label {
                                        text: backend.s.tgonly
                                        font.pixelSize: 10; color: backend.c.sub
                                        wrapMode: Text.WordWrap; Layout.fillWidth: true
                                    }
                                    Item { Layout.fillHeight: true }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true; Layout.fillHeight: true
                                radius: 16; color: backend.c.card; border.width: 1; border.color: backend.c.border
                                ColumnLayout {
                                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                                    RowLayout {
                                        spacing: 8
                                        Icon { name: "bell"; sz: 18; tint: backend.c.accent }
                                        Label { text: backend.s.hist; font.pixelSize: 14; font.bold: true; color: backend.c.fg }
                                        Item { Layout.fillWidth: true }
                                        Chip { text: backend.s.sent; iconName: "ok"; tint: backend.c.good
                                               active: win.filter === "sent"
                                               onClicked: win.filter = win.filter === "sent" ? "all" : "sent" }
                                        Chip { text: backend.s.fail; iconName: "no"; tint: backend.c.bad
                                               active: win.filter === "fail"
                                               onClicked: win.filter = win.filter === "fail" ? "all" : "fail" }
                                    }
                                    Label {
                                        visible: win.histRows().length === 0
                                        text: backend.s.nosig; font.pixelSize: 12; color: backend.c.sub
                                    }
                                    ListView {
                                        id: histList
                                        Layout.fillWidth: true; Layout.fillHeight: true
                                        clip: true; spacing: 6
                                        model: win.histRows()
                                        ScrollBar.vertical: SlimBar { }
                                        delegate: Rectangle {
                                            width: histList.width - 8; height: 46; radius: 12
                                            color: backend.c.bg; border.width: 1; border.color: backend.c.border
                                            RowLayout {
                                                anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
                                                Label { text: modelData.time; font.pixelSize: 10; font.family: "monospace"
                                                        color: backend.c.sub; Layout.preferredWidth: 118 }
                                                Label { text: modelData.asset + " · " + modelData.tf; font.pixelSize: 12
                                                        font.bold: true; color: backend.c.fg }
                                                Label { text: modelData.indicator; font.pixelSize: 11; color: backend.c.sub
                                                        Layout.fillWidth: true; elide: Text.ElideRight }
                                                Rectangle {
                                                    height: 24; radius: 12; width: hd.implicitWidth + 18
                                                    color: Qt.rgba(modelData.dir === "up" ? 0.13 : 0.94,
                                                                   modelData.dir === "up" ? 0.77 : 0.27,
                                                                   modelData.dir === "up" ? 0.37 : 0.27, 0.15)
                                                    Label { id: hd; anchors.centerIn: parent
                                                            text: modelData.dir === "up" ? "▲ " + backend.s.up : "▼ " + backend.s.down
                                                            font.pixelSize: 10; font.bold: true
                                                            color: modelData.dir === "up" ? backend.c.good : backend.c.bad }
                                                }
                                                Label { text: modelData.price; font.pixelSize: 11; font.family: "monospace"
                                                        color: backend.c.fg; Layout.preferredWidth: 78 }
                                                Rectangle {
                                                    height: 24; radius: 12; width: hs.implicitWidth + 18
                                                    color: modelData.sent === null ? backend.c.hover
                                                         : Qt.rgba(modelData.sent ? 0.13 : 0.94,
                                                                   modelData.sent ? 0.77 : 0.27,
                                                                   modelData.sent ? 0.37 : 0.27, 0.15)
                                                    Label { id: hs; anchors.centerIn: parent
                                                            text: modelData.sent === null ? "…" : (modelData.sent ? backend.s.sent : backend.s.fail)
                                                            font.pixelSize: 10; font.bold: true
                                                            color: modelData.sent === null ? backend.c.sub
                                                                 : (modelData.sent ? backend.c.good : backend.c.bad) }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
'''
QML += r'''
    // ════════════════ المكونات ════════════════
    /* شريط تمرير رقيق وناعم لقوائم واجهة سطح المكتب — بروح شريط المحرر الرقيق
       في صفحة الويب (طلب المستخدم: شريط العملات كان خشنًا فصار رقيقًا هكذا) */
    component SlimBar: ScrollBar {
        id: slim
        implicitWidth: 10
        hoverEnabled: true
        padding: 2
        background: Item { }
        contentItem: Rectangle {
            implicitWidth: 6
            radius: 3
            /* رمادي واضح مثل مقبض شريط المحرر في الويب، ويتوهج بلون التمييز عند السحب */
            color: slim.pressed ? backend.c.accent : backend.c.sub
            opacity: (slim.active || slim.hovered) ? 1.0 : 0.5
            Behavior on opacity { NumberAnimation { duration: 180 } }
            Behavior on color { ColorAnimation { duration: 140 } }
        }
    }

    /* مفتاح صغير لأقسام الإعدادات — بلون التمييز عند التشغيل ورمادي عند الإيقاف */
    component MiniSwitch: Rectangle {
        id: ms
        property bool on: false
        signal toggled()
        implicitWidth: 40; implicitHeight: 22; radius: 11
        color: ms.on ? backend.c.accent : backend.c.border
        Rectangle {
            width: 16; height: 16; radius: 8; color: "#FFFFFF"
            x: ms.on ? ms.width - width - 3 : 3
            anchors.verticalCenter: parent.verticalCenter
            Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: ms.toggled() }
    }

    component Icon: Image {
        property string name: ""
        property string tint: "#FFFFFF"
        property int sz: 20
        readonly property int px: Math.round(sz * 0.75)
        width: px; height: px
        Layout.preferredWidth: px; Layout.preferredHeight: px
        Layout.maximumWidth: px; Layout.maximumHeight: px
        source: name === "" ? "" : backend.icon(name, tint)
        sourceSize: Qt.size(px * 2, px * 2)
        smooth: true; mipmap: true
        fillMode: Image.PreserveAspectFit
    }

    component Logo: Item {
        id: lg
        property bool animate: true
        implicitWidth: 360
        implicitHeight: width * 80 / 354
        Repeater {
            model: backend.logoLayers
            delegate: Image {
                id: im
                anchors.fill: parent
                source: backend.logo(modelData.n, backend.dark)
                sourceSize: Qt.size(Math.max(lg.width, 1) * 2, Math.max(lg.height, 1) * 2)
                fillMode: Image.PreserveAspectFit
                smooth: true
                opacity: lg.animate ? 0 : 1
                transform: Translate { id: tr }
                SequentialAnimation {
                    running: lg.animate
                    PauseAnimation { duration: modelData.delay }
                    ParallelAnimation {
                        NumberAnimation { target: im; property: "opacity"; to: 1; duration: 650; easing.type: Easing.OutCubic }
                        NumberAnimation { target: tr; property: "y"; from: modelData.kind === "rise" ? lg.height * 0.58 : 0
                                          to: 0; duration: 750; easing.type: Easing.OutCubic }
                        NumberAnimation { target: tr; property: "x"; from: modelData.kind === "icon" ? -lg.width * 0.05 : 0
                                          to: 0; duration: 800; easing.type: Easing.OutBack }
                    }
                }
            }
        }
    }

    component Field: TextField {
        id: f
        selectByMouse: true
        implicitHeight: 42
        font.pixelSize: 13
        color: backend.c.fg
        leftPadding: 12
        background: Rectangle {
            radius: 11; color: backend.c.bg
            border.width: f.activeFocus ? 2 : 1
            border.color: f.activeFocus ? backend.c.accent : backend.c.border
            Behavior on border.color { ColorAnimation { duration: 120 } }
        }
    }

    component Area: TextArea {
        id: ta
        selectByMouse: true
        color: backend.c.fg
        font.pixelSize: 13
        padding: 10
        background: Rectangle {
            radius: 11; color: backend.c.bg
            border.width: ta.activeFocus ? 2 : 1
            border.color: ta.activeFocus ? backend.c.accent : backend.c.border
        }
    }

    component Btn: Button {
        id: b
        property bool outline: false
        property color c0: backend.c.g1
        property color c1: backend.c.g2
        property string iconName: ""
        property int fs: 13
        implicitHeight: 40
        leftPadding: 16; rightPadding: 16
        scale: down ? 0.96 : (hovered ? 1.02 : 1)
        Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutCubic } }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
        contentItem: Item {
            implicitWidth: row.implicitWidth; implicitHeight: row.implicitHeight
            Row {
                id: row; spacing: 8; anchors.centerIn: parent
                Icon { visible: b.iconName !== ""; name: b.iconName; sz: b.fs + 3
                       tint: b.outline ? backend.c.fg : "#FFFFFF" }
                Text { text: b.text; font.pixelSize: b.fs; font.bold: true
                       color: b.outline ? backend.c.fg : "#FFFFFF" }
            }
        }
        background: Rectangle {
            radius: 11
            border.width: b.outline ? 1 : 0
            border.color: b.hovered ? backend.c.accent : backend.c.border
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0
                    color: b.outline ? (b.hovered ? backend.c.hover : backend.c.card)
                                     : (b.hovered ? Qt.lighter(b.c0, 1.15) : b.c0) }
                GradientStop { position: 1
                    color: b.outline ? (b.hovered ? backend.c.hover : backend.c.card)
                                     : (b.hovered ? Qt.lighter(b.c1, 1.15) : b.c1) }
            }
        }
    }

    component Chip: Rectangle {
        id: ch
        property string text: ""
        property string iconName: ""
        property bool active: false
        property color tint: backend.c.accent
        signal clicked()
        implicitHeight: 30
        implicitWidth: crow.implicitWidth + 22
        radius: 15
        color: active ? tint : (cm.containsMouse ? backend.c.hover : backend.c.card)
        border.width: active ? 0 : 1; border.color: backend.c.border
        Behavior on color { ColorAnimation { duration: 120 } }
        Row {
            id: crow; spacing: 6; anchors.centerIn: parent
            Icon { visible: ch.iconName !== ""; name: ch.iconName; sz: 14
                   tint: ch.active ? "#FFFFFF" : backend.c.sub }
            Text { text: ch.text; font.pixelSize: 11; font.bold: true
                   color: ch.active ? "#FFFFFF" : backend.c.fg }
        }
        MouseArea { id: cm; anchors.fill: parent; hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor; onClicked: ch.clicked() }
    }

    component IBtn: Rectangle {
        id: ib
        property string iconName: ""
        property string label: ""
        property bool active: false
        property bool danger: false
        signal clicked()
        implicitWidth: lbl.text !== "" ? rowi.implicitWidth + 24 : 32
        implicitHeight: 32; radius: 8
        color: active ? backend.c.accent
                      : (danger ? (im.containsMouse ? Qt.rgba(0.94, 0.27, 0.27, 0.16) : "transparent")
                                : (im.containsMouse ? backend.c.hover : "transparent"))
        border.width: danger ? 1 : (active ? 0 : 1)
        border.color: danger ? backend.c.bad : backend.c.border
        Row {
            id: rowi
            anchors.centerIn: parent
            spacing: 7
            visible: ib.label !== ""
            Icon { name: ib.iconName; sz: 15
                   tint: ib.active ? "#FFFFFF" : (ib.danger ? backend.c.bad
                                                 : (im.containsMouse ? backend.c.fg : backend.c.sub)) }
            Label { id: lbl; text: ib.label; font.pixelSize: 12; font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                    color: ib.active ? "#FFFFFF" : (ib.danger ? backend.c.bad : backend.c.fg) }
        }
        Icon { anchors.centerIn: parent; visible: ib.label === ""; name: ib.iconName; sz: 16
               tint: ib.active ? "#FFFFFF" : (ib.danger ? backend.c.bad
                                             : (im.containsMouse ? backend.c.fg : backend.c.sub)) }
        MouseArea { id: im; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: ib.clicked() }
    }

    component NavBtn: Rectangle {
        id: nb
        property string iconName: ""
        property string label: ""
        property bool active: false
        signal clicked()
        Layout.fillWidth: true
        implicitHeight: 40; radius: 11
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: nb.active ? Qt.lighter(backend.c.accent, 1.2)
                                               : (nm.containsMouse ? backend.c.hover : "transparent") }
            GradientStop { position: 1; color: nb.active ? backend.c.accent
                                               : (nm.containsMouse ? backend.c.hover : "transparent") }
        }
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 12
            Icon { name: nb.iconName; sz: 19; tint: nb.active ? "#FFFFFF" : backend.c.sub }
            Label { text: nb.label; Layout.fillWidth: true; font.pixelSize: 13; font.bold: nb.active
                    color: nb.active ? "#FFFFFF" : backend.c.fg; elide: Text.ElideRight }
        }
        MouseArea { id: nm; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: nb.clicked() }
    }

    component LangBox: ComboBox {
        id: lbx
        implicitWidth: 116; implicitHeight: 32
        model: [ { code: "en", name: "English" }, { code: "ar", name: "العربية" } ]
        textRole: "name"
        valueRole: "code"
        currentIndex: backend.lang === "ar" ? 1 : 0
        font.pixelSize: 12
        onActivated: backend.lang = currentValue
        background: Rectangle { radius: 10; color: backend.c.card; border.width: 1; border.color: backend.c.border }
        contentItem: Text { text: lbx.displayText; font.pixelSize: 12; color: backend.c.fg
                            verticalAlignment: Text.AlignVCenter; leftPadding: 10 }
    }

    /* ── مكونات صفحة الدخول الجديدة (طلب المستخدم) ── */
    // حقل مع أيقونة + كشف كلمة المرور
    component IField: TextField {
        id: ifd
        selectByMouse: true
        implicitHeight: 48
        font.pixelSize: 14
        color: backend.c.fg
        placeholderTextColor: backend.c.sub
        horizontalAlignment: backend.rtl ? TextInput.AlignRight : TextInput.AlignLeft
        leftPadding: backend.rtl ? (secret ? 46 : 14) : 46
        rightPadding: backend.rtl ? 46 : (secret ? 46 : 14)
        property string iconName: ""
        property bool secret: false
        property bool reveal: false
        echoMode: secret && !reveal ? TextInput.Password : TextInput.Normal
        background: Rectangle {
            radius: 12; color: backend.c.bg
            border.width: ifd.activeFocus ? 2 : 1
            border.color: ifd.activeFocus ? backend.c.accent : backend.c.border
            Behavior on border.color { ColorAnimation { duration: 120 } }
        }
        Icon {
            anchors.verticalCenter: parent.verticalCenter
            x: backend.rtl ? ifd.width - width - 16 : 16
            name: ifd.iconName; sz: 24
            tint: ifd.activeFocus ? backend.c.accent : backend.c.sub
        }
        Item {
            visible: ifd.secret
            width: 30; height: 30
            anchors.verticalCenter: parent.verticalCenter
            x: backend.rtl ? 10 : ifd.width - width - 10
            Icon { anchors.centerIn: parent; name: ifd.reveal ? "eyeoff" : "eye"; sz: 24; tint: backend.c.sub }
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: ifd.reveal = !ifd.reveal }
        }
    }

    // شبكة نقاط ناعمة محايدة
    component DotGrid: Canvas {
        renderTarget: Canvas.Image        /* يضمن الشفافية في كل أنماط العرض */
        property color dc: backend.dark ? "#FFFFFF" : "#0A1A3A"
        onDcChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.fillStyle = Qt.rgba(dc.r, dc.g, dc.b, 0.10)
            for (var x = 14; x < width; x += 28)
                for (var y = 14; y < height; y += 28)
                    ctx.fillRect(x, y, 1.4, 1.4)
        }
    }

    // توهّج لوني ناعم — SVG radial gradient: ناعم بلا حلقات ولا يحتاج إعادة رسم
    component Glow: Image {
        property color col: "#3B8BFF"
        property real amt: 0.2
        source: {
            var c = col.toString()
            var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">'
                    + '<defs><radialGradient id="g"><stop offset="0" stop-color="' + c + '" stop-opacity="' + amt + '"/>'
                    + '<stop offset="0.55" stop-color="' + c + '" stop-opacity="' + (amt * 0.35) + '"/>'
                    + '<stop offset="1" stop-color="' + c + '" stop-opacity="0"/></radialGradient></defs>'
                    + '<rect width="200" height="200" fill="url(#g)"/></svg>'
            return "data:image/svg+xml;utf8," + encodeURIComponent(svg)
        }
        fillMode: Image.Stretch
        smooth: true
        asynchronous: false
    }

    // شموع متحركة خفيفة في خلفية صفحة الدخول — تعمل فقط وهي ظاهرة
    component ChartBg: Canvas {
        id: cv
        renderTarget: Canvas.Image        /* يضمن الشفافية في كل أنماط العرض */
        property real off: 0
        property var cs: []
        property real amp: 0.2
        property int cw: 24
        property color cUp: backend.dark ? "#3A5B7D" : "#2A3344"
        property color cDn: backend.dark ? "#26323C" : "#9AA5B8"
        onCUpChanged: requestPaint()
        onCDnChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        function mk(o) {
            var c = o + (Math.random() - 0.5) * 0.34 - o * 0.04
            return { o: o, c: c, h: Math.max(o, c) + Math.random() * 0.12, l: Math.min(o, c) - Math.random() * 0.12 }
        }
        Component.onCompleted: {
            var a = [], p = 0
            for (var i = 0; i < 110; i++) { var k = mk(p); a.push(k); p = k.c }
            cs = a
        }
        Timer {
            interval: 40; repeat: true; running: cv.visible
            onTriggered: {
                cv.off += 0.5
                if (cv.off >= cv.cw) {
                    cv.off -= cv.cw
                    cv.cs.shift()
                    cv.cs.push(cv.mk(cv.cs[cv.cs.length - 1].c))
                }
                cv.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            var a = cs
            if (!a || a.length < 10 || width < 10) return
            var mid = height * 0.56, sc = height * amp
            function Y(v) { return mid - v * sc }
            ctx.globalAlpha = backend.dark ? 0.20 : 0.28
            ctx.lineCap = "round"
            var start = Math.floor(off / cw)
            for (var i = start; i * cw - off < width + cw; i++) {
                var k = a[(i % a.length + a.length) % a.length]
                if (!k || i < 0) continue
                var x = i * cw - off
                var colC = k.c >= k.o ? cUp : cDn
                ctx.strokeStyle = colC; ctx.fillStyle = colC; ctx.lineWidth = 1.6
                ctx.beginPath(); ctx.moveTo(x + cw / 2, Y(k.h)); ctx.lineTo(x + cw / 2, Y(k.l)); ctx.stroke()
                var top = Y(Math.max(k.o, k.c)), bh = Math.max(2, Math.abs(Y(k.o) - Y(k.c)))
                ctx.beginPath()
                if (ctx.roundRect) ctx.roundRect(x + 3, top, cw - 6, bh, 2); else ctx.rect(x + 3, top, cw - 6, bh)
                ctx.fill()
            }
            ctx.globalAlpha = backend.dark ? 0.15 : 0.20
            ctx.beginPath()
            for (var j = 0; j < a.length; j++) {
                var vx = j * cw - off + cw / 2
                if (vx < -cw) continue
                if (vx > width + cw) break
                var vy = Y(a[j].c)
                if (j === 0 || vx - cw < 0) ctx.moveTo(vx, vy); else ctx.lineTo(vx, vy)
            }
            ctx.lineWidth = 2.2
            ctx.strokeStyle = backend.c.g1
            ctx.stroke()
            ctx.globalAlpha = 1
        }
    }

    // الحساب والرصيد (الشريط العلوي الاقصى): نوع الحساب + الرصيد + بطاقة التبديل حقيقي/تجريبي
}
'''

# ══════════════════════════════ التشغيل ══════════════════════════════
if __name__ == "__main__":
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    # محرك الويب (Chromium): تسريع GPU على سطح المكتب (أخف وأسرع)،
    # ووضع برمجي آمن تلقائياً في الحاويات/الفحص الآلي (BADI_SHOTS أو لينكس بدون شاشة)
    _soft = bool(os.environ.get("BADI_SHOTS")) or (
        sys.platform.startswith("linux") and not os.environ.get("DISPLAY"))
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS",
                          "--no-sandbox --disable-gpu" if _soft else "--no-sandbox")
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("BadiCharts")
    app.setApplicationName("BadiChartsStudio")
    app.setWindowIcon(make_app_icon())   # شعار التطبيق في شريط العنوان وشريط المهام
    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("dbgShotDir", os.environ.get("BADI_SHOTS", ""))
    theme_json = json.dumps({"dark": backend.dark, "c": (DARK if backend.dark else LIGHT),
                             "lang": backend.lang})
    engine.rootContext().setContextProperty("webUrl",
                                            ensure_web_files(backend.boot_files_json(), theme_json))
    engine.rootContext().setContextProperty("splashUrl", SPLASH_URL)
    engine.loadData(QML.encode("utf-8"))
    if not engine.rootObjects():
        sys.exit(-1)
    rc = app.exec()
    del engine
    del backend
    sys.exit(rc)


# ==========================================================================
#  نهاية الكود — آخر سطر يعمل هو تشغيل التطبيق من PART 3 أعلاه.
#  END OF SOURCE — the app boots from the __main__ block of PART 3.
# ==========================================================================
