// اختبار منطق دمج دفعة التمرير للخلف — يجب أن تبقى كل شمعة في مكانها بالضبط
const fs = require("fs");
const src = fs.readFileSync("/tmp/jscheck/bridge_post.js", "utf-8");

// استخراج دالتي prependCandles و __badiMaybeLoadOlder من الجسر
const mPre = src.match(/prependCandles: function \(arr\) \{[\s\S]*?\n    \},/);
if (!mPre) { console.log("FAIL: prependCandles not found"); process.exit(1); }
const mOld = src.match(/window\.__badiMaybeLoadOlder = function \(p\) \{[\s\S]*?\n\};/);
if (!mOld) { console.log("FAIL: maybeLoadOlder not found"); process.exit(1); }

// ---- بناء بيئة وهمية ----
function idxToX(ch, N, i) { return ch.chartRight - (N - 1 - i + ch.rightOffset) * ch.barSpacing; }

function makeEnv(nCandles, rightOffset) {
  const candles = [];
  const t0 = 1_700_000_000;
  for (let i = 0; i < nCandles; i++)
    candles.push({ t: t0 + i, o: 1, h: 2, l: 0.5, c: 1.5, time: t0 + i, open: 1, high: 2, low: 0.5, close: 1.5, volume: 1 });
  const sim = { candles: candles.map(c => ({ ...c })), _norm: (c) => ({ ...c }) };
  const chart = {
    sim, rightOffset, barSpacing: 8,
    chartLeft: 0, chartRight: 800,            // visible = 100 candles
    computeTimeWeights() {}, computeIndicators() {}, invalidateTimeMarks() {},
    autoScale() {}, invalidate() {},
  };
  const pane = { dataArr: candles.map(c => ({ ...c })), chart, asset: "BRL/USD OTC", tf: "1m" };
  return { pane, chart, sim, t0 };
}

// ---- الجسر المبسّط (نفس منطق BRIDGE_POST) ----
const OLDER = { loading: false, at: 0, asset: "", tf: "" };
let olderRequests = [];
function send(cmd, obj) { olderRequests.push({ cmd, obj }); }
function norm1(c) {
  if (c.time !== undefined && c.close !== undefined) {
    if (c.t === undefined) c.t = c.time;
    return c;
  }
  return { time: c.t, open: c.o, high: c.h, low: c.l, close: c.c, volume: c.v || 0 };
}
function normArr(a) { return a.map(c => norm1({ ...c })); }
const sandbox = {
  OLDER, send, normArr, norm1,
  window: { __BADI_EMBEDDED: true, __badiPrimary: null },
  console: { log: () => {} },
};
const run = (code) => new Function("OLDER", "send", "normArr", "norm1", "window", "console", "runSignals", code + "; return { prependCandles: (typeof __o !== 'undefined' ? __o.prependCandles : undefined), maybeOlder: window.__badiMaybeLoadOlder };")(
  sandbox.OLDER, sandbox.send, sandbox.normArr, sandbox.norm1, sandbox.window, sandbox.console, () => {});

let fail = 0;
function expect(cond, msg) {
  console.log("[" + (cond ? "OK " : "FAIL") + "] " + msg);
  if (!cond) fail++;
}

// ============ اختبار 1: maybeLoadOlder يطلب عند الاقتراب من البداية ============
{
  const env = makeEnv(300, -200);                       // firstIdx = 299-200-100 = -1 ≤ 4
  sandbox.window.__badiPrimary = () => env.pane;
  const api = run(mOld[0]);
  api.maybeOlder(env.pane);
  expect(olderRequests.length === 1, "maybeLoadOlder: طلبت دفعة عند firstIdx=-1");
  const req = JSON.parse(olderRequests[0].obj);
  expect(req.before === env.t0, "maybeLoadOlder: before = أول شمعة (" + req.before + ")");
  expect(OLDER.loading === true, "maybeLoadOlder: القفل مرفوع أثناء الانتظار");
  // حارس التكرار: نداء ثانٍ فوري لا يرسل شيئاً
  api.maybeOlder(env.pane);
  expect(olderRequests.length === 1, "maybeLoadOlder: لا تكرار أثناء التحميل");
}

// ============ اختبار 2: الدمج يبقي العرض ثابتاً بالضبط ============
{
  const env = makeEnv(300, -200);
  const N0 = env.sim.candles.length;
  // خذ شمعة مرئية (index 150 مثلاً) وسجل إحداثيتها قبل الدمج
  const probeIdx = 150;
  const xBefore = idxToX(env.chart, N0, probeIdx);
  const probeCandle = env.sim.candles[probeIdx];

  // دفعة 170 شمعة أقدم
  const batch = [];
  for (let i = 1; i <= 170; i++)
    batch.push({ t: env.t0 - i, o: 1, h: 2, l: 0.5, c: 1.5, time: env.t0 - i, open: 1, high: 2, low: 0.5, close: 1.5, volume: 1 });

  sandbox.window.__badiPrimary = () => env.pane;
  const api = run("const __o = { " + mPre[0].replace(/,\s*$/, "") + " };");
  const added = api.prependCandles(batch);

  expect(added === 170, "prependCandles: أضافت 170 شمعة");
  expect(env.sim.candles.length === N0 + 170, "prependCandles: sim أصبح " + env.sim.candles.length);
  expect(env.pane.dataArr.length === N0 + 170, "prependCandles: dataArr أصبح " + env.pane.dataArr.length);
  expect(env.sim.candles[0].time === env.t0 - 170, "prependCandles: الأقدم في البداية");
  expect(env.sim.candles[170].time === env.t0, "prependCandles: القديمة بعد الدفعة");
  // نفس الشمعة في نفس المكان: بعد الدمج فهرسها 150+170 والمسافة من النهاية ثابتة
  const newIdx = env.sim.candles.findIndex(c => c.time === probeCandle.time);
  const xAfter = idxToX(env.chart, env.sim.candles.length, newIdx);
  expect(Math.abs(xAfter - xBefore) < 1e-9, "العرض ثابت: نفس الشمعة في نفس البكسل (" + xBefore + " → " + xAfter + ")");
  expect(env.chart.rightOffset === -200, "rightOffset لم يُلمس (" + env.chart.rightOffset + ")");
  expect(OLDER.loading === false, "prependCandles: فك القفل");
}

// ============ اختبار 3: التمرير للخلف مرتين متتاليتين ============
{
  const env = makeEnv(300, -200);
  sandbox.window.__badiPrimary = () => env.pane;
  OLDER.loading = false;
  const apiP = run("const __o = { " + mPre[0].replace(/,\s*$/, "") + " };");
  const batch = (t0, from, n) => Array.from({ length: n }, (_, i) =>
    ({ t: t0 - from - i, o: 1, h: 2, l: 0.5, c: 1.5, time: t0 - from - i, open: 1, high: 2, low: 0.5, close: 1.5, volume: 1 }));
  apiP.prependCandles(batch(env.t0, 1, 170));
  apiP.prependCandles(batch(env.t0, 171, 170));
  expect(env.sim.candles.length === 640, "دفعتان متتاليتان: sim = 640");
  expect(env.pane.dataArr[0].time === env.t0 - 340, "دفعتان متتاليتان: الأقدم أولاً");
}

// ============ اختبار 4: pushTick أثناء التمرير للخلف يبقي العرض ثابتاً ============
{
  const env = makeEnv(300, -200);
  const probeIdx = 150;
  const xBefore = idxToX(env.chart, 300, probeIdx);
  // محاكاة منطق pushTick من الجسر: شمعة جديدة + rightOffset -= 1
  env.pane.dataArr.push({ time: env.t0 + 300, open: 1, high: 2, low: 0.5, close: 1.5, volume: 1 });
  env.chart.sim.candles.push({ time: env.t0 + 300, open: 1, high: 2, low: 0.5, close: 1.5, volume: 1 });
  if (env.chart.rightOffset < 0) env.chart.rightOffset -= 1;
  const xAfter = idxToX(env.chart, 301, probeIdx);
  expect(Math.abs(xAfter - xBefore) < 1e-9, "pushTick للخلف: الشموع الثابتة لا تتحرك (" + xBefore + " → " + xAfter + ")");
}

console.log(fail === 0 ? "\nALL JS TESTS PASSED" : "\nJS TEST FAILURES: " + fail);
process.exit(fail === 0 ? 0 : 1);
