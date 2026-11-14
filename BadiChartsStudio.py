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
#    PART 2 — BADI-CHARTS-V2 v2.16.0 CHART LIBRARY (badi-chart.js)
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
#  أحدث الدفعات (v2.16.0):
#   • المكتبة المدمجة ترقّيت إلى BADI-CHARTS-V2 v2.16.0 (نفس الواجهة، بلا كسور)
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
<!-- ═══ BADI-CHARTS-V2 v2.16.0 chart library ═══ -->
<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.16.0/chart.js"></script>
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
   BADI-CHARTS v2.16.0: يُرسم داخل الشارت بإحداثياته نفسها، فيحافظ على مسافته عن
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
        <span id="stBrand" class="mono">BADI STUDIO v2.16.0</span>
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
   chart + indicator editor and drawing tools on top of BADI-CHARTS-V2 v2.16.0
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
   نستخدم ميزة countdown الأصلية في المكتبة (v2.16.0): تُرسم داخل الشارت بإحداثياته
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
#  PART 2 — BADI-CHARTS-V2 v2.16.0 CHART LIBRARY (badi-chart.js)
#  مكتبة الشارت (خارجية ثابتة — النسخة الرسمية الحرفية v2.16.0 الكاملة من CDN بلا تعديل
#  فقط دون أي تغيير في السلوك، ومضغوطة لتوفير الحجم)
# ═══════════════════════════════════════════════════════════════════════════
BADI_LIB_B64 = """
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
jvd+Pdh7I+7MDZkkCjdP1jMKDG1ChLI5fj4SnzbzxTvx/ue060ixO9o1SkdkMCRzdRz9cnBycvDSZBHhj5Kvsc5RxZXVJ3TLoHqQ
5RkZzyTzPaXYMbohdGtjwNwpnhDIcOA90cLRJAH/oZhxGtEWQRRw5Jm4phGxLQAJTb3pVFEFSMirhG9hninWPngC1+RJMg6eKkku
u1m1uToitw1C8fGKn8WlL52nZ+GNLu5ueoq3XI9DHDSqrUbd1Qeta05a2tPPevqZFSq887USYNlWbsnn4BGj9eiV4hIvkPKHQYcZ
aBQazaJiPomxDEYJNvPLhmkxk4hF60fvPpUJDFizz+/rhmqfs9laEh0tNQN/+m//ov4b7TAsLA2ouJoS4iWlB+x0leDGhf7c/9Vd
Ojh30YSoS5TrE/6ExYycxAa2uy0O3iX3rMkJ+FmoeQ35GOFUIcKXRKqKQ9/B96Qmg3mCq82u0yECA6RabFH6JqS/9ttw0HGIUE6z
ItW+oCaPCXX51OGFP9hHheP0ah++w/gcgcK+Kjn9ovc7lA3jE8CKbwmfeI47R3NMtJNkQ9k9Abl9ktzYPVoK+ufITPvpjp6r+izN
YUpu7wPllhq6967dqjJdAnfp+fbuwYfdveevfyZzfpGNk07CyZrfPY+H6Q4Bhb/39rTuNJWLGmAA6PlatNrsqzs9qbCZlQD/GbU+
JsxYvTHMjqCVbyv616YbLdhkgaJ/WPgzIXwZWxcC44M3e+5cVBGR6N5UM4puu7xhurRjbnv8q4dfnnMDMTZDx+xRweS47gnWh2lY
Nn14Xa4i3CUYcp3fRs9GkGp4b1IgxAsgDClIBGtgK2axI7Dw4ROh51UTT8F5wW9V3Pa55FbETJerjAV12N17sf368NRsDuFaNEY+
Uzy3KS1EUsGmeLQaHsOhgpz/Fw2RypnZjU7VUHToS+mRGlCjbksiS1L1q450rXI7VM6laxWrfPyFHTENNEvWterr2H58cUZn/h9H
ee14jXgqExvu5H+pCoHlaxUrf4EX91fccuU5oxN5x81Xdzu9poVacD1xT2U9v+DOLF9wFd9vVIyqZT/6Z73qZAbcu65mir/8/uOR
qJtlfdojsem2tz7vAXLQuwbPklF8nWZ5c9FZhElmyyo160pNe4QsrtZicbnbnu8PV1Vm3nOd9z4v1q/UTV4oDSwsF0gIcGCDXRC1
+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
"""


# ═══════════════════════════════════════════════════════════════════════════
#  PART 3 — THE DESKTOP APP (Python + QML) — التطبيق كاملاً كود واضح
#  (سطر واحد فقط مُعدَّل هنا: الصفحة تُقرأ من STUDIO_HTML الموجود أعلاه
#   بدل فك الضغط — انظر دالة build_embedded_html أسفل)
# ═══════════════════════════════════════════════════════════════════════════
"""
BadiCharts Studio — desktop indicator studio (Python + PySide6/QML)
Splash + login (same BadiCharts logo & flow) → studio:
  • the chart & editor are the embedded HTML app (BADI-CHARTS-V2 v2.16.0 chart
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
# الشارت هنا هو مكتبة BADI-CHARTS-V2 v2.16.0 نفسها والمحرر هو Monaco — كلاهما داخل صفحة HTML
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
   يربط صفحة HTML (شارت BADI-CHARTS v2.16.0 + محرر Monaco) بمحرك Python:
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
        '<script src="https://cdn.jsdelivr.net/gh/salahbadi19/BADI-CHARTS-V2@v2.16.0/chart.js"></script>',
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
                Label { text: "BADI STUDIO v2.16.0"; font.pixelSize: 10; font.bold: true
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
                // ═══════ 0 — الاستوديو: صفحة HTML مدمجة (شارت BADI-CHARTS v2.16.0 + محرر Monaco) ═══════
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
