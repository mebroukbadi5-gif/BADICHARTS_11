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
#    PART 2 — BADI-CHARTS-V2 v2.15.0 CHART LIBRARY (badi-chart.js)
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
#  أحدث الدفعات (v2.15.0):
#   • المكتبة المدمجة ترقّيت إلى BADI-CHARTS-V2 v2.15.0 (نفس الواجهة، بلا كسور)
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
<!-- ═══ BADI-CHARTS-V2 v2.15.0 chart library ═══ -->
<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.15.0/chart.js"></script>
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
   BADI-CHARTS v2.15.0: يُرسم داخل الشارت بإحداثياته نفسها، فيحافظ على مسافته عن
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
.sig-pair .aflag{width:22px;height:12px;border-radius:2px}
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
.aflag{display:block;width:16px;height:11px;border-radius:2px}
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
.am-row .aflag{width:24px;height:13px;flex-shrink:0}
.am-row b{flex:1;min-width:0;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.am-row .apay{font-style:normal;font-size:10px;font-weight:800;color:var(--ok);flex-shrink:0}
.am-tog{display:grid;width:20px;height:20px;flex-shrink:0;place-items:center;border-radius:6px;border:1px solid var(--border2);color:var(--t-dim);cursor:pointer}
.am-tog.on{background:var(--accent);border-color:var(--accent);color:#fff}
.am-tog:hover{border-color:var(--accent)}
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
        <span id="stBrand" class="mono">BADI STUDIO v2.15.0</span>
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
   chart + indicator editor and drawing tools on top of BADI-CHARTS-V2 v2.15.0
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
  const chart = new window.BadiCharts(cv, {
    symbol: { label: cfg.label, priceScale: 100, decimals: cfg.decimals },
    timeframe: { label: "1m", ms: tfMs("1m") },
    theme: window.__BADI_CHART_THEME__ || { drawing: "#38bdf8", drawingActive: "#7dd3fc" },
    /* العدّ التنازلي الأصلي للمكتبة بجانب الشمعة الحية (طلب المستخدم): رقمان فقط
       بلا إطار أو خلفية، بإزاحة ثابتة (14px) عن حافة الشمعة مهما كان الزوم */
    countdown: { enabled: !!(window.__BADI_UI__ && window.__BADI_UI__.cd), format: "ss", fontSize: 13, offsetX: 14, offsetY: 0, color: "#22E08A" }
  });
  const p = { el: el, head: el.querySelector(".pane-head"), cv: cv, chart: chart, asset: name, tf: "1m", dataArr: [], tick: 0 };
  setupChart(chart, p);
  chart.start();
  p.dataArr = generateCandles(cfg, p.tf, 620);
  chart.setData(p.dataArr);
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
    p.chart.setSymbol({ label: cfg.label, priceScale: 100, decimals: cfg.decimals });
    p.chart.setTimeframe({ label: p.tf, ms: tfMs(p.tf) });
  } catch (e) {}
  if (!(window.__BADI_EMBEDDED && i === primaryPane)) {
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
        p.chart.setSymbol({ label: CUR_ASSET, priceScale: 100, decimals: Number(m.dec || assetCfg(CUR_ASSET).decimals) });
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
   نستخدم ميزة countdown الأصلية في المكتبة (v2.15.0): تُرسم داخل الشارت بإحداثياته
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
/* currency list popup (+ button): click a currency row = add it to the bar AND open its chart
   (طلب المستخدم: الاثنان معًا لا إضافة فقط) — the small tog icon toggles the strip only */
function renderAssetMenu() {
  const box = $("amList");
  if (!box) return;
  const q = (($("amSearch") && $("amSearch").value) || "").trim().toLowerCase();
  const rows = BOARD.filter((it) => !q || it.name.toLowerCase().indexOf(q) >= 0);
  const ar = window.__BADI_LANG__ === "ar";
  box.innerHTML = rows.map((it) => {
    const on = addedNames().indexOf(it.name) >= 0;
    const open = (typeof badiMarketOpen === "function") ? badiMarketOpen(it.name) : true;
    /* الضغط على العملة نفسها في القائمة = الاثنان معًا: تُضاف إلى الشريط إن لم تكن عليه ثم يُفتح شارتها (طلب المستخدم).
       أيقونة التبديل الصغيرة تبقى لإضافة/إزالة العملة من الشريط فقط دون فتح الشارت. */
    const rowT = ar ? ("افتح شارت " + it.name + " ويُضاف إلى الشريط") : ("Open the " + it.name + " chart and add it to the bar");
    const togT = ar ? (on ? "إزالة " + it.name + " من الشريط" : "إضافة " + it.name + " إلى الشريط")
                    : (on ? "Remove " + it.name + " from the bar" : "Add " + it.name + " to the bar");
    return '<button class="am-row" data-am="' + esc(it.name) + '" title="' + esc(rowT) + '">'
      + (it.flag ? '<img class="aflag" src="' + it.flag + '" alt="">' : "")
      + "<b>" + esc(it.name) + "</b>"
      + '<i class="apay">' + Number(it.payout || 0) + "%</i>"
      + '<i class="amstate ' + (open ? "open" : "closed") + '">' + (ar ? (open ? "مفتوح" : "مغلوق") : (open ? "Open" : "Closed")) + "</i>"
      + '<span class="am-tog' + (on ? " on" : "") + '" data-amtog="' + esc(it.name) + '" title="' + esc(togT) + '">'
      + icon(on ? "check" : "plus", 11) + "</span></button>";
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
  /* currency list popup: + opener, search box, row click = add to the bar + open chart,
     tog icon = strip only, click-outside closes */
  $("assetAdd").addEventListener("click", function (e) {
    e.stopPropagation();
    if ($("assetMenu").hidden) assetMenuOpen(); else assetMenuClose();
  });
  $("assetMenu").addEventListener("click", function (e) { e.stopPropagation(); });
  $("amSearch").addEventListener("input", renderAssetMenu);
  $("amList").addEventListener("click", function (e) {
    const r = e.target.closest("[data-am]");
    if (!r) return;
    const n = r.dataset.am;
    /* أيقونة التبديل الصغيرة = إضافة/إزالة من الشريط فقط بلا فتح الشارت */
    if (e.target.closest("[data-amtog]")) { toggleAsset(n); return; }
    /* الضغط على العملة نفسها = الاثنان معًا: تُضاف إلى الشريط إن لم تكن عليه ثم يُفتح شارتها فورًا (طلب المستخدم) */
    if (addedNames().indexOf(n) < 0) toggleAsset(n);
    assetMenuClose();
    openAssetChart(n);
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
#  PART 2 — BADI-CHARTS-V2 v2.15.0 CHART LIBRARY (badi-chart.js)
#  مكتبة الشارت (خارجية ثابتة — نسخة v2.15.0 مصغّرة: حُذفت التعليقات والمسافات
#  فقط دون أي تغيير في السلوك، ومضغوطة لتوفير الحجم)
# ═══════════════════════════════════════════════════════════════════════════
BADI_LIB_B64 = """
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
u7Z5WmhKHem4nSlnWbHt42WXRH9G15Y/w8KC9Ab0rx09g8UpSFGtUDiBmcwYT023ixbzc1SstjUK7QyD5esmkF3r33Q3G9FPpZ7b
s4m4GA4ZVg559UE+yaCvRc7bAHhc/G8ATUrVZBqfz3rKhzUu8MjVMVJfdsTtQSiMJXB9CRydc1mV0y/bm+NuUPGFccO22nAcOZIp
bBXxe4QJTS+z1mwaj4sJXH/jGfs9qwBa1HcRR0d8VrFRbT/YbtL/2js+ZIpK6KJQyN7Lv8/N4aYz4JkulmDyiKODdZgs80QxaAOf
AX8v6O85/T1sagS4UBhlJTg9phvox1M/YUzA8SDUDeV3gJ2xPs/FegLd4k/7wSQxWgNCHhbxdCWcmPR17XnpPjSvRpYLDbnsw4Po
qJxIkTHWgZPHLS0pvfCkq06h5QK6HCM7Wl51805CF1EvfrgsotW2iCPI17dNi1MFg3x31AAH/mzQ5hlBOLJTDdIRySbobOtJ6Oxa
u57glPpXMKnjqP5rY43tuLbtallKI+mV2okPTee2y9mNvMJdU/jhypa7d2n5Ybjl0nl4Zm5wVPico8VWKu7sfzOfT8vj4Bw3PLyB
L8y1QcOWQWautcO8PXauwMasTXWOo35oO2SdjCdXIHfkN47vDPlcSL1HUC/DSTtHe/qcH9AKYHbEDHeS4mmWjrF/UWUgRi+JjBrH
9pb7kN2V+obepkhrpolsJiQ2EwK7syTzhPGninzj611RUZdhnwKnwVDG4s1tBw4w8wvMyzkjsgHTIp8awa3AbTXJvQTjK2ngMFY7
RxGlHC+9w4tOICY8KuYYDVKJMixdqQAzpj7QfHe3pSc7TSBzTUPqjMoB9yswyNueJ9FpfI3OFkfEcQlBLCyepj8bfzCnXO7Nna7F
PmDFVaSf2112PcqpwtfBJQWfupYH5NfyDZUvxA1LI5TN+/0jePGO+2J3y65Feb4VwH+NZ9fcZnvbur8arlMWcWVSugF2Yul8CDF6
dKd1uAvAqh4XdtiMSt4bGtx9vBvWSkrKmyRaG8fa1mG9fP30OKqDzLbd3t5s9ChPTP8qG81aiA8sLWMq3D6mgn97/PL1u+Onklb0
EMFLOPMBxZKBAIQ1iqYVQdMkjKGZASZrkHYMc9BgdrVpjiY5bg5k5ItpfHkZK8wqB/z+qg+iRHT45qRHpTcktwy9H2UUnIV6bYY+
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
bvkPRNaZVaPJBAA=
"""


# ═══════════════════════════════════════════════════════════════════════════
#  PART 3 — THE DESKTOP APP (Python + QML) — التطبيق كاملاً كود واضح
#  (سطر واحد فقط مُعدَّل هنا: الصفحة تُقرأ من STUDIO_HTML الموجود أعلاه
#   بدل فك الضغط — انظر دالة build_embedded_html أسفل)
# ═══════════════════════════════════════════════════════════════════════════
"""
BadiCharts Studio — desktop indicator studio (Python + PySide6/QML)
Splash + login (same BadiCharts logo & flow) → studio:
  • the chart & editor are the embedded HTML app (BADI-CHARTS-V2 v2.15.0 chart
    + Monaco editor) rendered inside the window with QtWebEngine
  • program indicators & tools in JavaScript or Python (Python runs in the
    desktop engine and its values are pushed into the chart)
  • advanced ready-made indicators library
  • Quotex real market & OTC assets (simulated live feed, pluggable)
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
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from math import ceil

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QUrl, QFileSystemWatcher, QMimeData
from PySide6.QtGui import QGuiApplication, QDesktopServices
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick

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
        "badiSect": "Encrypted indicators (BADI)", "keyFp": "Key fingerprint:",
        "notifT": "Notifications", "notifEmpty": "No notifications yet",
        "notifHint": "Notifications from your paid indicators appear here — the developer sends them from his own server (updates, subscription reminders). No files can ever pass through this channel.",
        "notifClear": "Clear all",
        "notifUnreadX": "%1 unread notification(s)", "notifAllRead": "All notifications read",
        "badiEnc": "Encrypt the indicator — export a .badi file", "badiImp": "Import an encrypted indicator (.badi)",
        "badiSaved": "Encrypted indicator saved", "badiEmpty": "There is no code to encrypt",
        "badiJsOnly": "Only JavaScript indicators can be encrypted", "badiOk": "Loaded — runs internally, its code stays hidden",
        "badiFail": "BADI import failed", "badiHint": "The 256-bit key is fused into the app — it is never written to any file, never shown and cannot be copied. The encrypted indicator runs inside the chart directly: its code never opens in the editor and is never saved anywhere. The .badi file sits next to the real indicator file — like MetaTrader.",
        "licTitle": "Encrypt indicator — buyer license", "licHint": "The buyer's USER ID is fetched automatically from your Telegram bot — click his name above to embed it into the encrypted indicator. The manual field below is a fallback only (multiple IDs: commas). Empty = works for everyone.",
        "licOk": "Encrypt", "licCancel": "Cancel", "yourUid": "Your USER ID:",
        "buyersTitle": "Buyers from your Telegram bot — click one to embed his USER ID into the indicator:",
        "buyersFetch": "Fetching buyers from the bot…",
        "buyersNone": "No buyers yet — the buyer opens your bot and sends his USER ID, then reopen this dialog.", "buyersErr": "Could not fetch buyers — save the bot token in settings first",
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
        "badiSect": "المؤشرات المشفرة (BADI)", "keyFp": "بصمة المفتاح:",
        "notifT": "الإشعارات", "notifEmpty": "لا توجد إشعارات بعد",
        "notifHint": "تظهر هنا إشعارات المؤشرات المدفوعة — المبرمج يرسلها من خادمه (تحديثات، تذكير بالاشتراك). لا يمكن لأي ملف أن يمر عبر هذه القناة إطلاقًا.",
        "notifClear": "مسح الكل",
        "notifUnreadX": "%1 إشعار غير مقروء", "notifAllRead": "كل الإشعارات مقروءة",
        "badiEnc": "تشفير المؤشر وتصديره إلى ملف .badi", "badiImp": "استيراد مؤشر مشفر (.badi)",
        "badiSaved": "تم حفظ المؤشر المشفر", "badiEmpty": "لا يوجد كود لتشفيره",
        "badiJsOnly": "التشفير لمؤشرات JavaScript فقط — ملفات Python غير مدعومة", "badiOk": "تم التحميل — يعمل داخليًا وكودــه مخفي",
        "badiFail": "فشل استيراد BADI", "badiHint": "المفتاح 256-بت مدموج داخل التطبيق — لا يُكتب أبدًا في أي ملف، ولا يُعرض، ولا يمكن نسخه. المؤشر المشفر يعمل داخل الشارت مباشرة: كودــه لا يُفتح في المحرر ولا يُحفظ في أي مكان. الملف المشفر .badi يُحفظ بجوار ملف المؤشر الأصلي — مثل ميتاتريدر.",
        "licTitle": "تشفير المؤشر — ترخيص المشتري", "licHint": "معرّف المشتري يُجلب تلقائيًا من بوت تلجرام — انقر على اسمه بالأعلى ليُدمَج داخل المؤشر المشفر مباشرة. الحقل اليدوي بالأسفل احتياط فقط (لعدة معرفات: فاصلة). اتركه فارغًا ليعمل مع الجميع.",
        "licOk": "تشفير", "licCancel": "إلغاء", "yourUid": "معرّفك (USER ID):",
        "buyersTitle": "المشترون من بوت تلجرام — انقر على مشترٍ لدمج معرّفه داخل المؤشر:",
        "buyersFetch": "جلب المشترين من البوت…",
        "buyersNone": "لا مشترين بعد — المشتري يفتح بوتك ويرسل له معرّفه ثم أعد فتح هذه النافذة.", "buyersErr": "تعذّر جلب المشترين — احفظ توكن البوت في الإعدادات أولًا",
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


def asset_flag(name):
    """علم العملة الأولى في الزوج كـ data-URI (BTC/ETH/XAU لها أيقونة خاصة)."""
    base = name.split("/")[0]
    return _flag_uri(FLAGS[base]) if base in FLAGS else ""


_RIM_GRAY = ('<rect x="0.4" y="0.4" width="19.2" height="13.2" rx="2" fill="none"'
             ' stroke="rgba(128,128,128,.35)" stroke-width="0.8"/>')
_RIM_WHITE = ('<rect x="0.4" y="0.4" width="19.2" height="13.2" rx="2" fill="none"'
              ' stroke="rgba(255,255,255,.9)" stroke-width="1.4"/>')


def pair_flag_uri(name):
    """علمان جنب بعض في SVG واحد مدموجين بشكل نظيف (العملة الأولى + عملة الاقتباس)."""
    parts = name.split("/")
    base = parts[0]
    quote = parts[1].replace(" OTC", "") if len(parts) > 1 else ""
    if not quote or quote not in FLAGS or base not in FLAGS:
        return asset_flag(name)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 27 14">'
           f'<g transform="translate(0,2.1) scale(0.7)">{FLAGS[base]}{_RIM_GRAY}</g>'
           f'<g transform="translate(13,2.1) scale(0.7)">{FLAGS[quote]}{_RIM_WHITE}</g></svg>')
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


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
#  صيغة الملف .badi (v2):  MAGIC "BADI" (4) + VERSION (1) + NONCE (12) +
#                          AES-256-GCM(ciphertext+tag) + SHA-256 مملح (32)
#  • BADI Vault — Multi-Layer Key Protection: المفتاح 256-بت واحد لكل نسخ
#    التطبيق (لا يُولَّد عند التثبيت)، مدموج بطبقات متعددة داخل هذا الملف —
#    لا يظهر بأي صيغة صريحة (لا hex ولا base64 ولا بايتات متتالية)، لا يُكتب
#    في أي ملف، ولا يُعرض، ولا يُرسل؛ البصمة المعروضة SHA-256 مقطوعة لا تكشفه.
#  • طبقة السلامة: SHA-256 مملح للمغلف كله — أي تعديل في أي بايت يُرفض قبل
#    فك التشفير، وفوقه تواقيع AES-GCM مع AAD = MAGIC+VERSION.
#  • المؤشر يُفك داخل الذاكرة فقط، يُفحص (ماسح أنماط ممنوعة + QuickJS معزولة
#    بلا ملفات ولا شبكة) ثم يُشغَّل داخليًا على الشارت: لا يُفتح في المحرر،
#    لا يُحفظ، ولا يظهر كوده للمستخدم إطلاقًا — المؤشرات المدفوعة آمنة.
#  • الملف المشفر .badi يُكتب بجوار ملف المؤشر الأصلي — مثل ميتاتريدر.
#    ملفات الإصدار v1 القديمة تُقبل للقراءة كما هي.
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
BADI_VERSION = b"\x02"             # v2 = مغلف بطبقة سلامة صريحة (SHA-256 مملح)
BADI_VERSION_V1 = b"\x01"          # إصدار قديم — قراءة فقط (تواقيع GCM تحميه)
BADI_INTEG_SALT = b"BADI-integrity-v2"
BADI_MSGS = {
    "en": {
        "noaes": "Encryption library missing — run: pip install cryptography",
        "notbadi": "Not a BADI file",
        "badver": "Unsupported BADI version",
        "short": "Corrupted file — data is incomplete",
        "key": "Decryption failed — the file is corrupted or the app key does not match",
        "integ": "Tampered file — integrity check failed",
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
        "integ": "الملف معدَّل — فحص السلامة لم يطابق",
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
    """تشفير/فك تشفير مؤشرات JavaScript بصيغة .badi — BADI Vault.

    المفتاح 256-بت واحد لكل نسخ التطبيق (طلب المستخدم: لا يُولَّد عند التثبيت
    ولا يُكتب أبدًا داخل ملف المؤشر) — مدموج بطبقات متعددة (BADI Vault —
    Multi-Layer Key Protection) ولا يظهر في الكود بأي صيغة صريحة: طبقاته
    تُجمَع داخل الذاكرة لحظة الاستخدام فقط ثم تُرمى."""

    # ═══ BADI Vault — Multi-Layer Key Protection (طلب المستخدم) ═══
    # الطبقة 1: قسمان متكاملان يُدمجان بـ XOR — لا يكفي أي منهما وحده
    # الطبقة 2: تدوير دوري للبايتات
    # الطبقة 3: قناع XOR مستقل لكل بايت
    # الطبقة 4: توقيع SHA-256 يفحص صحة التجميع — أي طبقة فاسدة = رفض فوري
    _V_A = (
        24, 187, 32, 30, 15, 98, 167, 54,
        136, 52, 138, 188, 34, 37, 48, 185,
        98, 149, 67, 107, 136, 90, 225, 37,
        78, 94, 244, 60, 176, 19, 123, 235)
    _V_B = (
        4, 71, 102, 44, 237, 186, 189, 76,
        118, 161, 175, 3, 189, 100, 13, 8,
        123, 202, 176, 236, 219, 202, 223, 89,
        36, 82, 152, 212, 162, 47, 217, 143)
    _V_M = (
        166, 174, 230, 10, 175, 193, 83, 219,
        193, 11, 7, 108, 210, 127, 196, 100,
        185, 218, 230, 54, 47, 159, 193, 131,
        145, 208, 115, 59, 48, 188, 75, 245)
    _V_R = 7
    _V_SIG = (28, 107, 240, 17)

    @classmethod
    def master_key(cls):
        """BADI Vault: تجميع المفتاح 256-بت من طبقاته داخل الذاكرة فقط."""
        raw = bytes(((a ^ b) & 0xFF) for a, b in zip(cls._V_A, cls._V_B))
        r = cls._V_R % 32
        raw = raw[-r:] + raw[:-r] if r else raw
        key = bytes(((x ^ m) & 0xFF) for x, m in zip(raw, cls._V_M))
        if hashlib.sha256(key + b"badi-vault-check").digest()[:4] != bytes(cls._V_SIG):
            raise RuntimeError("BADI Vault key assembly failed")
        return key

    @classmethod
    def fingerprint(cls):
        """بصمة قصيرة للمفتاح للعرض في الإعدادات (لا تكشف المفتاح نفسه)."""
        return hashlib.sha256(cls.master_key()).hexdigest()[:12].upper()

    @classmethod
    def encrypt(cls, source: str) -> bytes:
        """تشفير AES-256-GCM + مغلف v2 بطبقة سلامة صريحة (SHA-256 مملح)."""
        if not _HAS_AESGCM:
            raise BADIError("noaes")
        nonce = os.urandom(12)
        aes = AESGCM(cls.master_key())
        enc = aes.encrypt(nonce, source.encode("utf-8"), BADI_MAGIC + BADI_VERSION)
        blob = BADI_MAGIC + BADI_VERSION + nonce + enc
        return blob + hashlib.sha256(blob + BADI_INTEG_SALT).digest()

    @classmethod
    def decrypt(cls, blob: bytes) -> str:
        """فك التشفير بعد فحص السلامة أولًا: أي تعديل في أي بايت = رفض فوري.
        ملفات v1 القديمة تُقبل للقراءة وتحميها تواقيع AES-GCM نفسها."""
        if not _HAS_AESGCM:
            raise BADIError("noaes")
        if len(blob) < 5 or blob[:4] != BADI_MAGIC:
            raise BADIError("notbadi")
        ver = blob[4:5]
        if ver == BADI_VERSION:
            body = blob[:-32]
            if len(body) < 5 + 12 + 16:
                raise BADIError("short")
            if hashlib.sha256(body + BADI_INTEG_SALT).digest() != blob[-32:]:
                raise BADIError("integ")          # الملف معدَّل — رفض قبل أي فك تشفير
            nonce, ct = body[5:17], body[17:]
        elif ver == BADI_VERSION_V1:
            if len(blob) < 5 + 12 + 16:
                raise BADIError("short")
            nonce, ct = blob[5:17], blob[17:]
        else:
            raise BADIError("badver")
        try:
            aes = AESGCM(cls.master_key())
            plain = aes.decrypt(nonce, ct, BADI_MAGIC + ver)
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
    buyersFetched = Signal(str)            # قائمة المشترين المجلوبة من بوت تلجرام (طلب المستخدم)

    def __init__(self):
        super().__init__()
        cfg = _read_json(CFG_FILE, {})
        self._lang = cfg.get("lang", "en")
        self._dark = bool(cfg.get("dark", True))
        self._market = "real"        # قسم الحساب الحقيقي/التجريبي حُذف — يبقى وسم السوق للعملات OTC فقط
        self._asset = cfg.get("asset", "EUR/USD")
        self._tf = cfg.get("tf", "1m")
        if not any(a["name"] == self._asset for a in ASSETS["real"] + ASSETS["otc"]):
            self._asset = "EUR/USD"
        board_names = [b["name"] for b in BOARD]
        saved_added = [n for n in (cfg.get("added") or []) if isinstance(n, str) and n in board_names]
        if not saved_added:
            saved_added = [n for n in ("EUR/USD", "BTC/USD") if n in board_names] or board_names[:2]
        self._added = list(dict.fromkeys(saved_added))
        self._live = True        # البث الحي يعمل مباشرة دائمًا — الشموع متحركة بلا زر (طلب المستخدم)
        self._tick = 0
        self._candles = generate_candles(self._asset, self._tf)
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
        """حالة السوق لبطاقات العملات (طلب المستخدم): OTC والرقمية مفتوحة دائمًا —
        الفوركس مفتوح من الأحد 22:00 إلى الجمعة 22:00 بتوقيت UTC — نفس قاعدة الويب."""
        n = str(name or "")
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

    @Slot(str)
    def toggleAdded(self, name):
        """إضافة/إزالة عملة من الشريط — مع إبقاء عملة واحدة على الأقل دائمًا."""
        if not isinstance(name, str) or name not in [b["name"] for b in BOARD]:
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
        board_names = [b["name"] for b in BOARD]
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

    @Property(int, notify=candlesChanged)
    def candlesCount(self):
        return len(self._candles)

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
        cfg = self._asset_cfg()
        return cfg["dec"]

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
                               "chart_theme": self._chart_theme})

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
            # فتح تلجرام مع محادثة المشاركة نفسها (طلب المستخدم): tg://msg_url يفتح
            # نافذة المشاركة في تطبيق تلجرام لاختيار المحادثة مباشرة — إن لم يوجد
            # التطبيق: رابط t.me/share في المتصفح، وإلا تلجرام ويب. فتح التطبيق
            # بلا معاملات لا يُظهر شيئًا — هنا تُمرَّر المشاركة نفسها (رابط + نص).
            try:
                _su = urllib.parse.quote("https://t.me/badicharts", safe="")
                _st = urllib.parse.quote(
                    "BadiCharts indicator — " + os.path.basename(path), safe="")
                if not QDesktopServices.openUrl(QUrl(
                        "tg://msg_url?url=" + _su + "&text=" + _st)):
                    if not QDesktopServices.openUrl(QUrl(
                            "https://t.me/share/url?url=" + _su + "&text=" + _st)):
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
        self._asset = asset if any(a["name"] == asset for a in ASSETS["real"] + ASSETS["otc"]) else self._asset
        self._tf = tf if tf in dict(TFS) else self._tf
        self._market = "otc" if "OTC" in self._asset else "real"
        self._candles = generate_candles(self._asset, self._tf)
        self._tick = 0
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
        self._check_sig_results()

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
                           "market": {"assets": [a["name"] for a in ASSETS["real"] + ASSETS["otc"]],
                                      "board": BOARD,
                                      "added": self._added,
                                      "tfs": [k for k, _ in TFS],
                                      "asset": self._asset, "tf": self._tf, "live": self._live}})

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

    @Slot()
    def badiBotBuyers(self):
        """جلب المشترين من بوت تلجرام (طلب المستخدم): الخادم يجلب معرّف المستخدم
        الذي يريد البائع البيع له ويُدمَج داخل المؤشر — لا بطاقة خادم ولا إدخال
        يدوي إلا كاحتياط. كل مستخدم تواصل مع البوت يظهر هنا، ومعرّفه BADI
        يُستخرج تلقائيًا من رسائله. النتيجة عبر buyersFetched (خيط منفصل)."""
        def run():
            out = {"ok": False, "error": "", "buyers": []}
            try:
                tok = str(_read_json(CFG_FILE, {}).get("token") or "").strip()
                if not tok:
                    out["error"] = "notoken"
                else:
                    req = urllib.request.Request(
                        "https://api.telegram.org/bot" + tok
                        + "/getUpdates?limit=100&allowed_updates=%5B%22message%22%5D",
                        headers={"User-Agent": "BadiCharts-Studio"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read().decode("utf-8", "ignore"))
                    users = {}
                    for upd in data.get("result") or []:
                        msg = upd.get("message") or upd.get("edited_message") or {}
                        frm = msg.get("from") or {}
                        num = frm.get("id")
                        if not num:
                            continue
                        ent = users.setdefault(int(num), {
                            "name": ((frm.get("first_name") or "") + " "
                                     + (frm.get("last_name") or "")).strip(),
                            "user": ("@" + str(frm.get("username"))) if frm.get("username") else "",
                            "uid": ""})
                        for cand in re.findall(
                                r"BADI-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}",
                                str(msg.get("text") or "").upper()):
                            if not ent["uid"]:
                                ent["uid"] = cand
                    out["ok"] = True
                    out["buyers"] = [dict(v, id=str(k)) for k, v in users.items()]
            except Exception as e:
                out["error"] = str(e)[:120]
            self.buyersFetched.emit(json.dumps(out))
        threading.Thread(target=run, daemon=True).start()

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
# الشارت هنا هو مكتبة BADI-CHARTS-V2 v2.15.0 نفسها والمحرر هو Monaco — كلاهما داخل صفحة HTML
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
   يربط صفحة HTML (شارت BADI-CHARTS v2.15.0 + محرر Monaco) بمحرك Python:
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
      } catch (e) { console.log("BADI::dbg setCandles ERR " + e); }
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
            if (pr.dataArr.length > 1500) pr.dataArr = pr.dataArr.slice(-1200);
          } else pr.dataArr[pr.dataArr.length - 1] = k;
        }
        pr.chart.update(k);
        syncCdColor(pr);
        runSignals();
      } catch (e) {}
    },
    setLive: function (on) {
      /* البث الحي يعمل دائمًا الآن (طلب المستخدم) — يبقى مفعّلاً مهما وصل */
      live = true;
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
        '<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.15.0/chart.js"></script>',
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
                "__badiApp.setLive(" + (backend.live ? "true" : "false") + ")")
    }
    function doLogout() {
        win.loggedIn = false
        win.page = 0
        userF.text = ""
        passF.text = ""
    }
    function onCandlesWeb() {
        if (!win.webReady) return
        if (backend.assetLabel !== win.lastAsset || backend.tfLabel !== win.lastTf
                || backend.candlesCount < win.lastLen || backend.candlesCount > win.lastLen + 1) {
            win.syncFull()
            return
        }
        if (backend.candlesCount !== win.lastLen) win.lastLen = backend.candlesCount
        /* شمعة جديدة واحدة أو تحديث الشمعة الأخيرة — دفعة خفيفة بدون إعادة ضبط العرض */
        webCall("__badiApp.pushTick(" + backend.lastTickJson + ")")
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
        var r = JSON.parse(backend.badiExport(pe.c, pe.n, pe.k, licField.text, "", ""))
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
        onOpened: {
            licField.text = ""
            buyersLbl.text = backend.s.buyersFetch
            buyers = []
            backend.badiBotBuyers()
        }
        property var buyers: []
        function fillBuyers(js) {
            var o = {}
            try { o = JSON.parse(js || "{}") } catch (e) { o = {} }
            if (!o.ok) { buyers = []; buyersLbl.text = backend.s.buyersErr; return }
            buyers = o.buyers || []
            buyersLbl.text = buyers.length ? backend.s.buyersTitle : backend.s.buyersNone
        }
        Connections {
            target: backend
            function onBuyersFetched(js) { licPop.fillBuyers(js) }
        }
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
            /* المشترين من البوت (طلب المستخدم): الخادم يجلب معرّف المشتري الذي يريد
               البائع البيع له ويُدمَج داخل المؤشر المشفر مباشرة — لا بطاقة خادم،
               ولا يُظهر المفتاح أبدًا، والإدخال اليدوي بالأسفل احتياط فقط */
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Label { id: buyersLbl; text: backend.s.buyersTitle; font.pixelSize: 11
                        color: backend.c.sub; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                IBtn { iconName: "rotate"
                       onClicked: { buyersLbl.text = backend.s.buyersFetch; backend.badiBotBuyers() } }
            }
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: buyersCol.height + 10
                visible: licPop.buyers.length > 0
                color: backend.c.bg; radius: 10; border.width: 1; border.color: backend.c.border
                Column {
                    id: buyersCol
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.margins: 5
                    spacing: 2
                    Repeater {
                        model: licPop.buyers
                        delegate: Rectangle {
                            required property var modelData
                            width: buyersCol.width
                            height: 28
                            radius: 7
                            color: buyMouse.containsMouse && modelData && modelData.uid
                                   ? backend.c.accent : "transparent"
                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                                spacing: 6
                                Label { text: (modelData.name || "") + (modelData.user ? "  " + modelData.user : "")
                                        font.pixelSize: 11; color: backend.c.fg; elide: Text.ElideRight
                                        Layout.fillWidth: true }
                                Label { text: modelData.uid || "—"; font.pixelSize: 11
                                        font.family: "monospace"; font.bold: true
                                        color: buyMouse.containsMouse && modelData.uid
                                               ? backend.c.card : backend.c.accent }
                            }
                            MouseArea {
                                id: buyMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: modelData && modelData.uid
                                             ? Qt.PointingHandCursor : Qt.ArrowCursor
                                onClicked: {
                                    if (!modelData || !modelData.uid) return
                                    var t = licField.text.trim()
                                    licField.text = t ? t + ", " + modelData.uid : modelData.uid
                                }
                            }
                        }
                    }
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
            readonly property int ha: backend.rtl ? Text.AlignRight : Text.AlignLeft
            readonly property int al: backend.rtl ? Qt.AlignRight : Qt.AlignLeft
            function ease(i) {
                var v = Math.max(0, Math.min(1, t * 1.8 - i * 0.14))
                return 1 - Math.pow(1 - v, 3)
            }
            NumberAnimation { id: enterAnim; target: loginPage; property: "t"; from: 0; to: 1; duration: 1300 }
            Component.onCompleted: enterAnim.restart()
            onVisibleChanged: if (visible) { t = 0; enterAnim.restart() }

            function attempt() {
                if (busy) return
                ok = false
                if (userF.text.trim() === "" || passF.text === "") {
                    err = backend.s.errEmpty
                    shake.restart()
                    return
                }
                err = ""
                busy = true
                fakeAuth.restart()
            }
            Timer { id: fakeAuth; interval: 900; onTriggered: { loginPage.busy = false; loginPage.ok = true; win.loggedIn = true } }

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
                Label { text: "BADI STUDIO v2.15.0"; font.pixelSize: 10; font.bold: true
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
                // ═══════ 0 — الاستوديو: صفحة HTML مدمجة (شارت BADI-CHARTS v2.15.0 + محرر Monaco) ═══════
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
