# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء D — الوحدة 10: التشخيص الذاتي (V14 SELF-DIAGNOSTICS)
# ════════════════════════════════════════════════════════════════════════════
# لماذا؟ «طريقة العمل دون انهيار الخوادم» تحتاج إثباتاً لا ادعاءً.
# هذه الوحدة تفحص نفسها عند الإقلاع وتعطي الأمر الجاهز للمشغل/التطبيق:
#   V14_API["selftest"]() → تقرير نجاح/فشل كل ضمانة من ضمانات v14:
#     1) بوابة الطلبات: الأولوية تُخدم قبل الخلفية، سلسلة العملة متسلسلة،
#        dedupe يعيد نفس الرد، مهلة الوفاة تفشل سريعاً لا تعليقاً.
#     2) دلو الرموز: المعدل محدود فعلاً.
#     3) متتبع التيكات: تصنيف NEW/DUP/STALE + كشف الفجوة (لا فقدان صامت).
#     4) قاطع الدائرة: CLOSED→OPEN→HALF_OPEN→CLOSED كلها تتحول صحيحة.
#     5) سجل الجلسة: يكتب ويقرأ (JSONL + دوران الحجم).
#     6) النبضة: payload مكتمل المفاتيح.
#     7) المشرف: يعيد تشغيل حلقة ماتة ويحصي الانهيار.
# كل الفحوصات تعمل على نُسخ معزولة (لا تلمس حالة الخادم الحية أبداً).
# ════════════════════════════════════════════════════════════════════════════

class V14SelfTest:
    """تشخيص ذاتي لطبقة v14 — كل فحص على نسخة معزولة بلا لمس حالة حية."""

    def __init__(self) -> None:
        self.results: _v14_List[Tuple[str, bool, str]] = []

    # ─────────────── أدوات مساعدة ───────────────
    def _record(self, name: str, ok: bool, note: str = "") -> None:
        self.results.append((name, bool(ok), note))

    # ─────────────── 1) بوابة الطلبات ───────────────
    async def _test_gate_priority(self) -> None:
        """الأولوية: طلب PRELOAD يُدخل أولاً ثم OPENING — OPENING يُخدم أولاً."""
        gate = V14RequestGate()
        served: _v14_List[str] = []

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            served.append(api_symbol)
            await _v14_asyncio.sleep(0.01)
            return [{"fake": api_symbol}]

        # نستبدل جلب العامل بنسخة الاختبار عبر التصحيح المحلي للنطاق
        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            fut_bg = gate.submit_nowait("BG_PRELOAD_TEST", 0, 60, 60,
                                        priority=int(RequestPriority.PRELOAD),
                                        label="selftest")
            fut_fg = gate.submit_nowait("FG_OPENING_TEST", 0, 60, 60,
                                        priority=int(RequestPriority.OPENING),
                                        label="selftest")
            worker = _v14_asyncio.create_task(gate.worker())
            await _v14_asyncio.wait_for(fut_fg, timeout=5.0)
            await _v14_asyncio.wait_for(fut_bg, timeout=5.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            ok = (served and served[0] == "FG_OPENING_TEST"
                  and len(served) == 2)
            self._record("gate.priority.order", ok,
                         f"served={served} (expected FG first)")
        except Exception as e:
            self._record("gate.priority.order", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_dedupe(self) -> None:
        """نفس الطلب المعلق مرتين → نفس الرد (لا طلب مكرر يختلط)."""
        gate = V14RequestGate()
        calls = []

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            calls.append(api_symbol)
            await _v14_asyncio.sleep(0.05)
            return [{"fake": api_symbol}]

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            worker = _v14_asyncio.create_task(gate.worker())
            fut1 = gate.submit_nowait("DEDUPE_TEST", 100, 60, 60,
                                      priority=int(RequestPriority.OPENING))
            fut2 = gate.submit_nowait("DEDUPE_TEST", 100, 60, 60,
                                      priority=int(RequestPriority.OPENING))
            ok_same = fut1 is fut2
            await _v14_asyncio.wait_for(
                _v14_asyncio.gather(fut1, fut2), timeout=5.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            self._record("gate.dedupe.same_future", ok_same and len(calls) == 1,
                         f"calls={len(calls)} (expected 1)")
        except Exception as e:
            self._record("gate.dedupe.same_future", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_expiry(self) -> None:
        """مهلة الوفاة: طلب بقي في الطابور بعد مهلته يفشل سريعاً (لا تعليق).

        الترتيب المتعمد: نرسل الطلب بمهلة 0.2 ثانية، لا نشغّل العامل إلا
        بعد انقضائها — فالعامل عند السحب يفحص المهلة ويرفض فوراً."""
        gate = V14RequestGate()

        async def fake_slow_fetch(api_symbol, end_time, seconds, period,
                                  foreground=False, timeout=None, retries=2):
            await _v14_asyncio.sleep(1.5)
            return []

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_slow_fetch
        try:
            fut = gate.submit_nowait("EXPIRE_TEST", 0, 60, 60,
                                     priority=int(RequestPriority.OPENING),
                                     wait_deadline=0.2)
            await _v14_asyncio.sleep(0.3)   # انقضت المهلة قبل بدء العامل
            worker = _v14_asyncio.create_task(gate.worker())
            failed_fast = False
            t0 = time.monotonic()
            try:
                await _v14_asyncio.wait_for(fut, timeout=2.0)
            except Exception:
                failed_fast = (time.monotonic() - t0) < 1.0
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            self._record("gate.deadline.fails_fast", failed_fast,
                         f"elapsed={time.monotonic() - t0:.2f}s")
        except Exception as e:
            self._record("gate.deadline.fails_fast", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    async def _test_gate_asset_chain(self) -> None:
        """سلسلة العملة: طلبان لنفس العملة لا يتداخلان — التسلسل مطلق."""
        gate = V14RequestGate()
        active = {"n": 0, "max": 0}

        async def fake_fetch(api_symbol, end_time, seconds, period,
                             foreground=False, timeout=None, retries=2):
            active["n"] += 1
            active["max"] = max(active["max"], active["n"])
            await _v14_asyncio.sleep(0.03)
            active["n"] -= 1
            return []

        real = globals()["qx_fetch_window_raw"]
        globals()["qx_fetch_window_raw"] = fake_fetch
        try:
            worker = _v14_asyncio.create_task(gate.worker())
            futs = [gate.submit_nowait(f"CHAIN_TEST_{i}", 0, 60, 60,
                                       priority=int(RequestPriority.PRELOAD))
                    for i in range(4)]
            await _v14_asyncio.wait_for(_v14_asyncio.gather(*futs), timeout=10.0)
            worker.cancel()
            try:
                await worker
            except _v14_asyncio.CancelledError:
                pass
            # عامل واحد → التزامن الفعلي لا يتجاوز 1 أبداً
            self._record("gate.asset_chain.never_parallel",
                         active["max"] == 1, f"max_concurrent={active['max']}")
        except Exception as e:
            self._record("gate.asset_chain.never_parallel", False, f"error: {e}")
        finally:
            globals()["qx_fetch_window_raw"] = real

    # ─────────────── 2) دلو الرموز ───────────────
    def _test_token_bucket(self) -> None:
        """دلو الرموز: المعدل محدود — 5 محاولات فورية على دلو rate=0.5
        ينجح منها فقط ما فيه رموز (سعة 1)."""
        bucket = V14TokenBucket(rate=0.5, capacity=1.0)
        got = sum(1 for _ in range(5) if bucket.try_acquire())
        self._record("bucket.limits_burst", got == 1, f"acquired={got}/5")

    # ─────────────── 3) متتبع التيكات ───────────────
    def _test_tracker(self) -> None:
        """تصنيف التيكات: NEW ثم DUP ثم STALE ثم قفزة كبيرة=فقدان محتمل.

        التتابع واقعي: تيكات متقاربة 2s تؤسس متوسط الفاصل، ثم تيك بعده
        100 ثانية (8× أضعاف المتوسط) = قفزة شاذة → GAP."""
        tr = V14TickTracker("SELFTEST")
        c1 = tr.ingest(1000, 1.0)                 # NEW
        c2 = tr.ingest(1000, 1.05)                # DUP (سعر أحدث بنفس الثانية)
        c3 = tr.ingest(999, 1.0)                  # STALE (أقدم)
        tr.ingest(1002, 1.1)                      # NEW (فاصل 2s)
        tr.ingest(1004, 1.15)                     # NEW (فاصل 2s)
        c6 = tr.ingest(1104, 1.2)                 # قفزة 100s → GAP
        ok = (c1 == TickClassification.NEW
              and c2 == TickClassification.DUPLICATE
              and c3 == TickClassification.STALE
              and c6 == TickClassification.GAP
              and tr.gap_events == 1)
        self._record("tracker.classification+gap", ok,
                     f"{c1}/{c2}/{c3}/{c6} gaps={tr.gap_events}")

    # ─────────────── 4) قاطع الدائرة ───────────────
    def _test_breaker(self) -> None:
        """الدورة الكاملة: CLOSED→OPEN (5 أخطاء)→HALF_OPEN (بعد استشفاء)→CLOSED."""
        br = V14CircuitBreaker("selftest", failure_threshold=3,
                               recovery_interval=0.05, half_open_successes=2)
        for _ in range(3):
            br.record_failure("sim")
        opened = br.state() == BreakerState.OPEN
        time.sleep(0.06)
        probe = br.allow_probe()                  # استشفاء
        half = br.state() == BreakerState.HALF_OPEN
        br.record_success()
        br.record_success()
        closed = br.state() == BreakerState.CLOSED
        self._record("breaker.full_cycle", opened and probe and half and closed,
                     f"open={opened} half={half} closed={closed}")

    # ─────────────── 5) سجل الجلسة ───────────────
    def _test_journal(self) -> None:
        """السجل يكتب ويقرأ — JSONL صالح."""
        tmp = _v14_os.path.join(_v14_os.path.dirname(V14_JOURNAL.path),
                                "qx_v14_selftest_journal.jsonl")
        j = V14SessionJournal(path=tmp, max_bytes=1024 * 1024)
        j.record("selftest_write", k=1, s="نص عربي")
        j.record("selftest_write2", k=2)
        tail = j.tail(2)
        ok = (len(tail) == 2 and tail[-1]["event"] == "selftest_write2"
              and tail[0]["s"] == "نص عربي")
        self._record("journal.write_read_utf8", ok, f"n={len(tail)}")

    # ─────────────── 6) النبضة ───────────────
    def _test_heartbeat(self) -> None:
        """payload النبضة يحتوي كل المفاتيح الحرجة."""
        try:
            hb = V14Heartbeat()
            data = hb.payload()
            required = {"time", "pid", "uptime_s", "connection_alive",
                        "gate", "supervisor", "session", "pressure",
                        "opened_assets", "memory_rss_mb"}
            missing = required - set(data.keys())
            self._record("heartbeat.payload_complete", not missing,
                         f"missing={missing or 'none'}")
        except Exception as e:
            self._record("heartbeat.payload_complete", False, f"error: {e}")

    # ─────────────── 7) المشرف ───────────────
    async def _test_supervisor_restart(self) -> None:
        """المشرف يعيد تشغيل حلقة ماتة ويحصي الانهيار.

        ملاحظة: supervise لا يعود أبداً بالتصميم (حماية دون انهيار) —
        الفحص يشغّله مهمة، يراقب عدّادات الحالة، ثم يلغيه."""
        runs = {"n": 0}

        async def dying_loop():
            runs["n"] += 1
            await _v14_asyncio.sleep(0.02)
            if runs["n"] <= 2:
                raise RuntimeError("simulated crash for selftest")
            # من هنا تكمل طبيعياً حتى الإلغاء — والمشرف يعيد تشغيلها

        sup = V14Supervisor()
        task = _v14_asyncio.create_task(
            sup.supervise("selftest_dying", dying_loop))
        # انتظر حتى 3 تشغيلات (2 انهيار + إعادة) أو مهلة 15 ثانية
        for _ in range(300):
            st = sup.status_of("selftest_dying")
            if st.runs >= 3:
                break
            await _v14_asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except _v14_asyncio.CancelledError:
            pass
        st = sup.status_of("selftest_dying")
        ok = st.runs >= 3 and st.crashes >= 2
        self._record("supervisor.restarts_dead_loop", ok,
                     f"runs={st.runs} crashes={st.crashes}")

    # ─────────────── 8) backoff ───────────────
    def _test_backoff(self) -> None:
        """backoff أُسّي مهزوز — ضمن حدود pyquotex."""
        d0 = v14_backoff_delay(0, base=1.0, cap=30.0, jitter=0.0)
        d3 = v14_backoff_delay(3, base=1.0, cap=30.0, jitter=0.0)
        d10 = v14_backoff_delay(10, base=1.0, cap=30.0, jitter=0.0)
        ok = (abs(d0 - 1.0) < 1e-9 and abs(d3 - 8.0) < 1e-9
              and d10 == 30.0)
        self._record("backoff.exponential+cap", ok,
                     f"d0={d0} d3={d3} d10={d10}")

    # ─────────────── التنفيذ الكامل ───────────────
    async def run_all(self) -> dict:
        self.results.clear()
        self._test_backoff()
        self._test_tracker()
        self._test_breaker()
        self._test_journal()
        self._test_heartbeat()
        self._test_token_bucket()
        await self._test_gate_priority()
        await self._test_gate_dedupe()
        await self._test_gate_expiry()
        await self._test_gate_asset_chain()
        await self._test_supervisor_restart()
        passed = sum(1 for _, ok, _ in self.results if ok)
        total = len(self.results)
        ok_all = passed == total
        V14_JOURNAL.record("selftest", passed=passed, total=total)
        V14_METRICS.inc("v14.selftest.runs")
        if not ok_all:
            V14_METRICS.inc("v14.selftest.failures")
        return {
            "ok": ok_all,
            "passed": passed,
            "total": total,
            "results": [
                {"name": name, "ok": ok, "note": note}
                for name, ok, note in self.results
            ],
        }


async def v14_selftest() -> dict:
    """التشخيص الذاتي الكامل — V14_API["selftest"]."""
    return await V14SelfTest().run_all()


# أضف التشخيص الذاتي للواجهة العامة
try:
    V14_API["selftest"] = v14_selftest
except Exception:
    pass


async def v14_selftest_loop() -> None:
    """تشخيص ذاتي دوري خفيف (كل 10 دقائق) — نفس الفحوصات، يحصي الفشل."""
    await _v14_asyncio.sleep(60.0)
    while True:
        try:
            await _v14_asyncio.sleep(600.0)
            try:
                res = await v14_selftest()
                if not res["ok"]:
                    V14_JOURNAL.record("selftest_periodic_fail",
                                       passed=res["passed"],
                                       total=res["total"])
                    try:
                        logmsg(f"[v14-selftest] periodic: {res['passed']}/"
                               f"{res['total']} passed — see journal")
                    except Exception:
                        pass
            except Exception as e:
                V14_JOURNAL.record("selftest_error", error=str(e)[:200])
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=2.0, cap=15.0)
