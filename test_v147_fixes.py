#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات v14.7 — شكاوى المستخدم الحرفية:
1) «لماذا تختفي شموعها» — الآلة الأصلية fill_gap_once (حرفياً من الكود
   المرجعي) تقص ذاكرة العملة إلى آخر 1000 شمعة؛ v14_gap_fill_for_asset
   يجب أن يعيد الخط الكامل بعد كل سد (بلا أي فقدان) وأن يسد كل الثغرات
   ≤ يوم كامل على الخط كاملاً (وليس آخر 1000 شمعة فقط).
2) «لم تسد ثغرتها» — ثغرة عميقة (خارج نافذة 1000 شمعة) يجب أن تُسدّ
   بالتعبئة الأصلية بعد سد واحد.
3) الواجهة: الاستيعاب بلا تقليص — إن عاد المحرك مقصوصاً تبقى شموع الغذاء كلها.
"""
import asyncio
import importlib.util
import time

spec = importlib.util.spec_from_file_location('qxv14', '/home/z/my-project/download/qx_server_v14.py')
qx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qx)

PERIOD = 60


def _mk_candle(t, base=1.0):
    return {'time': t, 'open': base, 'high': base + 0.01,
            'low': base - 0.01, 'close': base, 'volume': 100}


class FakeClient:
    """عميل وهمي — get_candles تعيد آخر 10 شموع حقيقية (نفس نداء الآلة الأصلية)."""

    def __init__(self, real_tail):
        self.real_tail = real_tail
        self.api = type('A', (), {'state': None})()   # v14_gap_fill_for_asset يفحصه

    async def get_candles(self, asset, end_time, offset, period):
        t0 = int(end_time) - int(offset)
        return [c for c in self.real_tail if c['time'] >= t0]


async def test_no_truncation_and_deep_gap_sealed():
    # ==== خط كامل: 3000 شمعة مع ثغرة عميقة حقيقية (80 شمعة) عند المنتصف ====
    # تُحقن مباشرة في الذاكرة وsync_state (كما يصل الخط من مسار لا يمرّ
    # بالتعبئة — صفحة/محرك) ثم يجب أن يسدّها سد واحد بلا أي فقدان.
    now = (int(time.time()) // PERIOD) * PERIOD
    t_start = now - 3000 * PERIOD
    full = []
    for i in range(3000):
        t = t_start + i * PERIOD
        if 800 <= i < 880:      # ثغرة عميقة خارج نافذة الآلة (آخر 1000)
            continue
        full.append(_mk_candle(t))
    asset = qx._get_or_create_asset('TESTV147_otc')
    asset.api_symbol = 'TESTV147_otc'
    asset.symbol = 'TESTV147_otc'
    asset.candles = list(full)   # حقن مباشر بلا تعبئة (خط مثقوب فعلاً)
    qx.MT4_WRITER.sync_state['TESTV147_otc'] = {
        'period': 1, 'candles': list(full), 'last_write': 0, 'last_price': 0.0,
    }

    holes_before = _count_holes(asset.candles)
    assert holes_before == 80, f"setup: deep gap expected (got {holes_before})"

    # ==== الآلة الأصلية عبر v14_gap_fill_for_asset (طبقة التقوية) ====
    qx.ALL_STREAMING_ASSETS.append(asset)
    qx.CONNECTION_ALIVE = True
    qx.CLIENT = FakeClient([_mk_candle(now - i * PERIOD) for i in range(10)])
    # ارفع أي تجمّد قديم لهذا الرمز التجريبي
    for v in ('TESTV147_otc',):
        try:
            qx.clear_gap_flag_any([v])
        except Exception:
            pass
    qx.MT4_WRITER._gap_filled.pop(v, None)
    qx.MT4_WRITER._gap_filled_at.pop(v, None)

    ok = await qx.v14_gap_fill_for_asset('TESTV147_otc', reason="test")
    assert ok, "v14_gap_fill_for_asset should succeed"

    n_after = len(asset.candles)
    holes_after = _count_holes(asset.candles)
    print(f"candles before fill : {len(full)} (3000 - 79 gap)")
    print(f"candles after fill  : {n_after}")
    print(f"holes before        : {holes_before}")
    print(f"holes after         : {holes_after}")

    assert n_after >= len(full), \
        f"FAILED: engine memory truncated! {n_after} < {len(full)} (candles disappear)"
    assert holes_after == 0, \
        f"FAILED: deep gap NOT sealed ({holes_after} holes left) — 'لم تسد ثغرتها'"
    # كل شمعة أصلية ما زالت موجودة (لا فقدان)
    have = {c['time'] for c in asset.candles}
    missing = [c['time'] for c in full if c['time'] not in have]
    assert not missing, f"FAILED: {len(missing)} original candles lost"
    print("PASS: no truncation + deep gap sealed + zero loss")


def _count_holes(candles):
    ts = sorted(c['time'] for c in candles)
    holes = 0
    for i in range(1, len(ts)):
        g = (ts[i] - ts[i - 1]) // PERIOD
        if g > 1:
            holes += g - 1
    return holes


def test_absorb_no_shrink():
    # بلا Qt: تُستخرج الدالة الحقيقية من ملف التطبيق عبر AST وتُنفَّذ كما هي
    import ast
    import types
    APP = "/home/z/my-project/download/BadiChartsStudio_live.py"
    src = open(APP, encoding="utf-8").read()
    tree = ast.parse(src)
    got = {}

    class V(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            for st in node.body:
                if isinstance(st, ast.FunctionDef) and st.name == "_qx_absorb_engine_no_shrink":
                    got[st.name] = ast.get_source_segment(src, st)
            self.generic_visit(node)

    V().visit(tree)
    assert "_qx_absorb_engine_no_shrink" in got, "function not found in app"
    ns = {"time": time}
    exec(compile(got["_qx_absorb_engine_no_shrink"], "<ast>", "exec"), ns)
    f = ns["_qx_absorb_engine_no_shrink"]

    # غذاء فيه 3000 شمعة، والمحرك عاد مقصوصاً إلى آخر 1000
    host = types.SimpleNamespace()
    now = (int(time.time()) // 60) * 60
    host._QX_FEED_CAP = 45000
    host._candles = [{'t': now - i * 60, 'o': 1.0, 'h': 1.01, 'l': 0.99, 'c': 1.0, 'v': 1}
                     for i in range(2999, -1, -1)]
    engine = [{'t': c['t'], 'o': c['o'], 'h': c['h'], 'l': c['l'], 'c': c['c'], 'v': c['v']}
              for c in host._candles[-1000:]]
    # إصلاح سد في ذيل المحرك (قيمة مختلفة)
    engine[-1] = dict(engine[-1], c=9.99)
    f(host, engine)
    assert len(host._candles) == 3000, \
        f"FAILED: feed shrank to {len(host._candles)} (candles disappear)"
    assert host._candles[-1]['c'] == 9.99, "FAILED: repair did not reach the feed"
    assert host._candles[0]['t'] == now - 2999 * 60, "FAILED: oldest candle lost"
    print(f"PASS: absorb keeps {len(host._candles)} candles (engine was 1000) + repair applied")


if __name__ == '__main__':
    test_absorb_no_shrink()
    asyncio.run(test_no_truncation_and_deep_gap_sealed())
    print("ALL v14.7 CHECKS PASSED")
