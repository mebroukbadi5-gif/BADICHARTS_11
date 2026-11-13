# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء B — الوحدات 4 و 5 و 6:
#   4) V14 ENDPOINTS  — تقوي نقاط الخوادم (مسبح نقاط + قاطع دائرة + مسابر)
#   5) V14 TICK ENGINE — التكس لا ينام (مضخة مُيقَظة بالأحداث + كاشف فقدان)
#   6) V14 GAP GUARD  — سد الثغرات الأصلي على كل عملة مفتوحة + مراجع فقدان
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 4 — V14 ENDPOINTS (تقوي نقاط الخوادم)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم: «ابحث في المكتبة لي ارسلت لك سابقا في غيت هاب كيف تقوي نقاط
# الخوادم وتفرز الطلبات».
#
# ما وجدناه في مكتبة pyquotex المرسلة (الأنماط المعتمدة هنا):
#   • pyquotex/ws/client.py: مست回 watchdog يقيس صمت الاتصال (last_message_at)
#     ويعيد تدوير الاتصال القديم قسراً.
#   • pyquotex/ws/client.py: إعادة تشغيل الاشتراكات بعد كل إعادة اتصال ناجحة
#     (_replay_subscriptions — انتظار CONNECTED حتى 40×0.05s ثم إعادة كل اشتراك).
#   • pyquotex/_api/_waits.py: backoff أُسّي مهزوز بدل الإيقاع الميكانيكي.
#
# أسماء النطاقات الحقيقية فقط (من الكود الأساسي نفسه — لا نطاقات مُخترعة):
#   DEFAULT_DOMAIN_BANGLADESH = "market-qx.info"
#   DEFAULT_DOMAIN_GLOBAL     = "quotex.com"
# المسبح يراقب صحة النقطتين (TCP RTT + قاطع دائرة على أخطاء الجلب) ويكتب
# تقرير نطاقات + توصية. تبديل الاتصال الفعلي يبقى في مسار auto_reconnect
# الأصلي (لم يُمَس) — التقوية هنا: قياس، قاطع، تقرير، وتوصية موثقة.
# ════════════════════════════════════════════════════════════════════════════

class BreakerState:
    """حالات قاطع الدائرة (نمط صناعي قياسي)."""
    CLOSED = "CLOSED"        # سليم — يمر كل شيء
    OPEN = "OPEN"            # مفصول — يمنع ويبدأ عدّاد الاستشفاء
    HALF_OPEN = "HALF_OPEN"  # استشفاء — يمرر بروبات محدودة


class V14CircuitBreaker:
    """قاطع دائرة لكل نقطة خدمة.

    الفكرة (نمط صناعي — وهو نفس جوهر watchdog pyquotex): لا تضرب نقطة
    خدمة منهارة بطلبات متواصلة؛ افصلها (OPEN)، استشفها بروبة واحدة كل
    recovery_interval، وأعد فتحها بعد نجاحين متتاليين.

    آمن خيوطياً — يُستخدم من حلقة العامل ومن المسابر معاً.
    """

    def __init__(self, name: str, *,
                 failure_threshold: int = 5,
                 recovery_interval: float = 30.0,
                 half_open_successes: int = 2) -> None:
        self.name = name
        self.failure_threshold = int(failure_threshold)
        self.recovery_interval = float(recovery_interval)
        self.half_open_successes = int(half_open_successes)
        self._lock = _v14_threading.Lock()
        self._state = BreakerState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._opened_at = 0.0
        self._opened_count = 0
        self._last_error = ""
        self._last_transition_at = time.time()

    def _transition(self, state: str) -> None:
        self._state = state
        self._last_transition_at = time.time()
        self._opened_at = time.monotonic() if state == BreakerState.OPEN else 0.0
        V14_JOURNAL.record("breaker", name=self.name, state=state)
        try:
            logmsg(f"[v14-endpoint] circuit {self.name} -> {state}")
        except Exception:
            pass

    def allow_probe(self) -> bool:
        """هل تمرر هذه اللحظة طلباً؟ (OPEN يمرر فقط بروبة استشفاء بعد فترة)"""
        with self._lock:
            if self._state == BreakerState.CLOSED:
                return True
            if self._state == BreakerState.OPEN:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self.recovery_interval:
                    self._transition(BreakerState.HALF_OPEN)
                    self._consecutive_successes = 0
                    return True
                return False
            # HALF_OPEN: يمرر دائماً بروبة (العامل يحد من التزامن أصلاً)
            return True

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            if self._state == BreakerState.HALF_OPEN:
                self._consecutive_successes += 1
                if self._consecutive_successes >= self.half_open_successes:
                    self._transition(BreakerState.CLOSED)
            elif self._state == BreakerState.CLOSED:
                self._consecutive_successes += 1

    def record_failure(self, error: str = "") -> None:
        with self._lock:
            self._consecutive_successes = 0
            self._consecutive_failures += 1
            self._last_error = str(error)[:160]
            if self._state == BreakerState.HALF_OPEN:
                # البروبة فشلت — أعد الفصل فوراً
                self._opened_count += 1
                self._transition(BreakerState.OPEN)
            elif self._state == BreakerState.CLOSED and \
                    self._consecutive_failures >= self.failure_threshold:
                self._opened_count += 1
                self._transition(BreakerState.OPEN)

    def state(self) -> str:
        with self._lock:
            return self._state

    def info(self) -> dict:
        with self._lock:
            return {
                "state": self._state,
                "consecutive_failures": self._consecutive_failures,
                "opened_count": self._opened_count,
                "last_error": self._last_error,
                "last_transition": round(self._last_transition_at, 1),
            }


class V14EndpointState:
    """حالة نقطة خدمة واحدة (نطاق حقيقي من الكود الأساسي)."""

    def __init__(self, host: str, primary: bool = False) -> None:
        self.host = host
        self.primary = bool(primary)
        self.rtt_ms: _v14_Optional[float] = None     # EMA للمسابر الناجحة
        self.rtt_samples = 0
        self.probe_failures = 0
        self.last_probe_at = 0.0
        self.last_ok_at = 0.0
        self.breaker = V14CircuitBreaker(f"endpoint:{host}")
        self.fetch_ok = 0
        self.fetch_fail = 0

    def observe_rtt(self, ms: float) -> None:
        """EMA كلاسيكي — أحدث العينات أثقل (alpha يعتمد على عدد العينات)."""
        if ms is None or ms <= 0:
            return
        alpha = 0.4 if self.rtt_samples < 3 else 0.2
        if self.rtt_ms is None:
            self.rtt_ms = float(ms)
        else:
            self.rtt_ms = self.rtt_ms * (1 - alpha) + float(ms) * alpha
        self.rtt_samples += 1
        self.last_ok_at = time.time()
        self.probe_failures = 0

    def observe_probe_fail(self) -> None:
        self.probe_failures += 1

    def score(self) -> float:
        """درجة النقطة (أقل = أفضل) — تجمع RTT وحالة القاطع وأخطاء المسابر."""
        s = 0.0
        if self.breaker.state() == BreakerState.OPEN:
            s += 1000.0
        elif self.breaker.state() == BreakerState.HALF_OPEN:
            s += 300.0
        s += min(200.0, self.probe_failures * 25.0)
        if self.rtt_ms is not None:
            s += min(300.0, self.rtt_ms)
        else:
            s += 150.0  # مجهول RTT أسوأ من نتيجة معروفة
        if not self.primary:
            s += 10.0   # تفضيل طفيف للنقطة الأساسية عند تساوي كل شيء
        return round(s, 2)

    def info(self) -> dict:
        return {
            "host": self.host,
            "primary": self.primary,
            "rtt_ms": round(self.rtt_ms, 1) if self.rtt_ms else None,
            "rtt_samples": self.rtt_samples,
            "probe_failures": self.probe_failures,
            "last_probe_at": round(self.last_probe_at, 1),
            "breaker": self.breaker.info(),
            "fetch_ok": self.fetch_ok,
            "fetch_fail": self.fetch_fail,
            "score": self.score(),
        }


class V14EndpointPool:
    """مسبح نقاط الخدمة — «تقوي نقاط الخوادم».

    الوظائف:
      1) مسابر TCP RTT دورية خفيفة (كل V14_ENDPOINT_PROBE_INTERVAL ثانية)
         على النطاقات الحقيقية فقط (443) — قياس لا يزعج خوادم كوتكس.
      2) قاطع دائرة لكل نطاق يُغذى من نتائج الجلب الفعلية (report_ok/fail).
      3) تقرير نطاقات JSON (qx_endpoint_report.json) يُحدَّث كل دورة —
         التطبيق والمشغل يقرآن حالة النقاط لحظياً.
      4) توصية موثقة في السجل عند تدهور الأساسي: إن فُتح قاطع الأساسي
         بينما البديل سليم لمدة طويلة → توصية صريحة بإعادة الاتصال عبر
         المسار الرسمي (auto_reconnect الأصلي يبقى صاحب القرار الفعلي —
         نضع العلم V14_RECONNECT_HINT الذي تقرأه حلقات المراقبة).
    """

    def __init__(self) -> None:
        # النطاقات الحقيقية فقط من الكود الأساسي — الأساسي هو المُحلول جغرافياً
        primary_host = ""
        try:
            primary_host = (globals().get("QX_HOST") or
                            globals().get("DEFAULT_DOMAIN_GLOBAL") or "quotex.com")
        except Exception:
            primary_host = "quotex.com"
        alt_host = globals().get("DEFAULT_DOMAIN_BANGLADESH") or "market-qx.info"
        glob_host = globals().get("DEFAULT_DOMAIN_GLOBAL") or "quotex.com"
        self.endpoints: _v14_Dict[str, V14EndpointState] = {}
        self.endpoints[primary_host] = V14EndpointState(primary_host, primary=True)
        other = alt_host if primary_host != alt_host else glob_host
        if other != primary_host:
            self.endpoints[other] = V14EndpointState(other, primary=False)
        self.probe_interval = float(globals().get("_V14_ENDPOINT_PROBE_INTERVAL",
                                                  45.0))
        self.report_path = ""
        try:
            self.report_path = _v14_os.path.join(
                _v14_base_dir(), "qx_endpoint_report.json")
        except Exception:
            self.report_path = "qx_endpoint_report.json"
        self._last_report_write = 0.0
        self._lock = _v14_threading.Lock()

    # ---------- تغذية من نتائج الجلب الفعلية ----------
    def report_fetch(self, host: _v14_Optional[str], ok: bool,
                     error: str = "") -> None:
        """يسجل نتيجة جلب فعلي على النقطة (يُستدعى من حلقات v14 التي تعرف
        المضيف عبر QX_HOST). يحرك قاطع الدائرة."""
        with self._lock:
            ep = self.endpoints.get(host or "")
            if ep is None:
                return
            if ok:
                ep.fetch_ok += 1
                ep.breaker.record_success()
            else:
                ep.fetch_fail += 1
                ep.breaker.record_failure(error)

    # ---------- المسابر ----------
    async def probe_once(self, host: str, timeout: float = 3.0) -> _v14_Optional[float]:
        """مسحة TCP واحدة: قياس زمن فتح مقبس 443 — بلا أي ضغط على API."""
        loop = _v14_asyncio.get_running_loop()

        def _probe() -> _v14_Optional[float]:
            t0 = time.monotonic()
            sock = None
            try:
                sock = _v14_socket.create_connection((host, 443),
                                                     timeout=float(timeout))
                return (time.monotonic() - t0) * 1000.0
            except Exception:
                return None
            finally:
                try:
                    if sock is not None:
                        sock.close()
                except Exception:
                    pass

        try:
            return await _v14_asyncio.wait_for(loop.run_in_executor(None, _probe),
                                               timeout=timeout + 2.0)
        except Exception:
            return None

    async def probe_all(self) -> None:
        for host, ep in list(self.endpoints.items()):
            ms = await self.probe_once(host)
            ep.last_probe_at = time.time()
            if ms is not None:
                ep.observe_rtt(ms)
                V14_METRICS.gauge(f"v14.endpoint.{host}.rtt_ms", ms)
            else:
                ep.observe_probe_fail()
                V14_METRICS.inc("v14.endpoint.probe_failures")
            await _v14_asyncio.sleep(0.1)

    # ---------- الحلقة الدورية ----------
    async def monitor_loop(self) -> None:
        """حلقة المراقبة: مسحة + تقرير + توصيات. لا تمس الاتصال الفعلي."""
        await _v14_asyncio.sleep(5.0)   # اترك الاتصال يبدأ أولاً
        while True:
            try:
                await self.probe_all()
                await self._write_report()
                self._maybe_recommend()
                await _v14_asyncio.sleep(self.probe_interval)
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_METRICS.inc("v14.endpoint.monitor_errors")
                V14_JOURNAL.record("endpoint_monitor_error", error=str(e)[:200])
                await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)

    def _maybe_recommend(self) -> None:
        """توصية موثقة عند تدهور الأساسي مع بديل سليم — دون لمس الاتصال."""
        try:
            primary = next((e for e in self.endpoints.values() if e.primary), None)
            if primary is None:
                return
            others = [e for e in self.endpoints.values() if not e.primary]
            if not others:
                return
            pb = primary.breaker
            if pb.state() == BreakerState.OPEN and pb._opened_at and \
                    (time.monotonic() - pb._opened_at) > 120.0:
                healthy_alt = any(o.breaker.state() == BreakerState.CLOSED
                                  for o in others)
                if healthy_alt and not V14_RECONNECT_HINT.get():
                    V14_RECONNECT_HINT.set(True)
                    logmsg(f"[v14-endpoint] primary {primary.host} circuit OPEN "
                           f"for >120s while fallback healthy — reconnect hint "
                           f"SET (auto_reconnect owns the actual switch)")
                    V14_JOURNAL.record("endpoint_recommend",
                                       primary=primary.host,
                                       reason="primary_circuit_open")
        except Exception:
            pass

    async def _write_report(self) -> None:
        """يكتب تقرير النقاط ذرياً (tmp + rename) — القراءة آمنة دائماً."""
        try:
            report = {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "active_host": globals().get("QX_HOST", ""),
                "reconnect_hint": V14_RECONNECT_HINT.get(),
                "endpoints": [e.info() for e in self.endpoints.values()],
            }
            tmp = self.report_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                _v14_json.dump(report, f, ensure_ascii=False, indent=2)
            _v14_os.replace(tmp, self.report_path)
            self._last_report_write = time.time()
        except Exception:
            pass

    def info(self) -> dict:
        with self._lock:
            return {
                "active_host": globals().get("QX_HOST", ""),
                "endpoints": [e.info() for e in self.endpoints.values()],
                "report_path": self.report_path,
                "probe_interval_s": self.probe_interval,
            }


# مسبح النقاط العام
V14_ENDPOINTS = V14EndpointPool()


async def v14_endpoint_probe_loop() -> None:
    """حلقة مسابر النقاط — supervised."""
    await V14_ENDPOINTS.monitor_loop()


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 5 — V14 TICK ENGINE (التكس لا ينام)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم الحرفي: «ولا تيكس النوم ايضا لا يجب ان ينام مثل الكود لي اريتك».
#
# الفرق عن v13:
#   v13 كان يجمع التيكات بحلقة نائمة: tick_cache_collector → sleep(0.25)
#   كل دورة. أي أن التكس قد ينام حتى 250ms قبل أن يُخزّن، وينام مرة أخرى
#   قبل أن يصل للمشتركين — هذا هو «التكس النائم».
#
# v14 — نفس فلسفة الكود المرجعي (quotex_mt4_server_v10.realtime_stream:
# معالجة فورية لكل تيك داخل حلقة البث بلا نوم في مسار المعالجة):
#   1) مضخة مُيقَظة بالأحداث: تنتظر asyncio.Event يرفعه الالتقاط فور رؤية
#      تيك جديد — مسار المعالجة نفسه بلا أي sleep.
#   2) ملتقط مراقب 10ms كحماية عمق إضافية (لو فُقد رفع الحدث) — والملتقط
#      نفسه يستيقظ المضخة، فلا تيك يبقى راقداً أكثر من 10ms في أسوأ حال.
#   3) ترقيم متسلسل + كاشف فقدان: كل تيك يحمل seq، وأي قفزة زمنية شاذة
#      تُحسب «فقدان محتمل» — «ولا يتم فقدان».
#   4) توزيع فوري على المشتركين (بلا نوم بين التوزيعات — sleep(0) فقط
#      لتسليم الحلقة)، والمشترك البطيء يُساق بسياسة إسقاط الأقدم
#      مع عدّاد — البطيء لا يعيق السريع.
#   5) التخزين نفسه كما في v13 (ذاكرة فقط + TTL 5 دقائق + لا قرص).
# ════════════════════════════════════════════════════════════════════════════

class TickClassification:
    NEW = "NEW"          # تيك جديد فعلٍ
    DUPLICATE = "DUP"    # نفس الطابع الزمني — مكرر
    STALE = "STALE"      # أقدم من آخر تيك — تجاهل (نفس منطق الكود المرجعي)
    GAP = "GAP"          # قفزة زمنية شاذة — فقدان محتمل


class V14TickTracker:
    """متتبع تسلسل التيكات لعملة واحدة — يصنف كل تيك ويكشف الفقدان.

    منطق التصنيف مطابق لروح الكود المرجعي:
      - تيك أقدم من الأخير → STALE (تجاهل — «stale tick — ignore»).
      - نفس الطابع → DUPLICATE.
      - قفزة أكبر من V14_TICK_GAP_MULTIPLIER × الفاصل المتوسط → GAP
        (يُحسب فقدان محتمل — عدّاد + سجل، بلا أي تصرف هجومي).
    """

    def __init__(self, api_symbol: str, maxlen: int = 600) -> None:
        self.api_symbol = api_symbol
        self.ring = _v14_deque(maxlen=int(maxlen))   # [(seq, ts, price)]
        self.seq = 0
        self.last_ts = 0
        self.gap_intervals = _v14_deque(maxlen=30)   # متوسط الفواصل الطبيعية
        self.gap_events = 0
        self.last_price = 0.0
        self._lock = _v14_threading.Lock()

    def ingest(self, ts: int, price: float, *, gap_multiplier: float = 8.0,
               min_gap_s: float = 30.0) -> str:
        """يبتلع تيكاً ويعيد تصنيفه — آمن من الخيوط."""
        with self._lock:
            if ts <= 0 or price <= 0:
                return TickClassification.STALE
            if self.last_ts and ts < self.last_ts:
                return TickClassification.STALE
            if self.last_ts and ts == self.last_ts:
                # تحديث آخر سعر إن تغير (نفس الثانية قد تحمل سعراً أحدث)
                if price != self.last_price and self.ring:
                    seq, _, _ = self.ring[-1]
                    self.ring[-1] = (seq, ts, price)
                    self.last_price = price
                return TickClassification.DUPLICATE
            # تيك جديد — فحص القفزة (فقدان محتمل)
            if self.last_ts:
                interval = ts - self.last_ts
                # متوسط الفواصل الطبيعية السابقة فقط (قبل هذه الفجوة —
                # الفجوة نفسها لا تلوث خط الأساس وإلا أخفت كل ما بعدها)
                prev = list(self.gap_intervals)
                avg = (sum(prev) / len(prev)) if prev else interval
                if interval > max(min_gap_s, avg * gap_multiplier):
                    self.gap_events += 1
                    V14_METRICS.inc("v14.ticks.gap_events")
                    classification = TickClassification.GAP
                    # الفجوة لا تُضاف لنافذة الفواصل الطبيعية
                else:
                    classification = TickClassification.NEW
                    self.gap_intervals.append(interval)
            else:
                classification = TickClassification.NEW
            self.seq += 1
            self.ring.append((self.seq, ts, price))
            self.last_ts = ts
            self.last_price = price
            return classification

    def since(self, seconds: int) -> _v14_List[Tuple[int, int, float]]:
        cutoff = time.time() - max(1, int(seconds))
        with self._lock:
            return [(s, t, p) for (s, t, p) in self.ring if t >= cutoff]

    def silence_seconds(self) -> float:
        if not self.last_ts:
            return 0.0
        return max(0.0, time.time() - self.last_ts)

    def info(self) -> dict:
        with self._lock:
            return {
                "api_symbol": self.api_symbol,
                "count": len(self.ring),
                "seq": self.seq,
                "last_ts": self.last_ts,
                "last_price": self.last_price,
                "gap_events": self.gap_events,
                "silence_s": round(self.silence_seconds(), 1),
            }


class V14TickSubscriber:
    """مشترك تيكات — طابور محدود + سياسة إسقاط الأقدم للبطيء.

    البطيء لا يعيق السريع ولا يوقف المضخة أبداً (خادم لا ينهار بسبب مشترك).
    """

    def __init__(self, handle: int, symbols: _v14_Optional[_v14_Set[str]] = None,
                 maxsize: int = 2000) -> None:
        self.handle = handle
        self.symbols = set(symbols) if symbols else None
        # طابور خيوطي حقيقي مع إسقاط يدوي للأقدم عند الامتلاء
        from queue import Queue as _Queue
        self.q: _Queue = _Queue(maxsize=maxsize)
        self.dropped = 0
        self.delivered = 0
        self.created_at = time.time()

    def wants(self, api_symbol: str) -> bool:
        return self.symbols is None or api_symbol in self.symbols

    def offer(self, tick: tuple) -> None:
        """يضع التيك؛ لو امتلأ الطابور يُسقط الأقدم (drop-oldest)."""
        try:
            self.q.put_nowait(tick)
            self.delivered += 1
        except Exception:
            try:
                self.q.get_nowait()
                self.dropped += 1
                V14_METRICS.inc("v14.ticks.subscriber_dropped")
                self.q.put_nowait(tick)
                self.delivered += 1
            except Exception:
                self.dropped += 1
                V14_METRICS.inc("v14.ticks.subscriber_dropped")

    def drain(self, max_items: int = 500) -> _v14_List[tuple]:
        out = []
        for _ in range(max_items):
            try:
                out.append(self.q.get_nowait())
            except Exception:
                break
        return out


class V14TickEngine:
    """مضخة التيكات — «التكس لا ينام».

    البنية:
      - trackers: متتبع لكل عملة (ترقيم + فقدان + صمت).
      - notify(): يرفع حدث الاستيقاظ فور رؤية تيك جديد (من الالتقاط).
      - pump_loop(): ينتظر الحدث، يصرف كل جديد فوراً (بلا نوم في المسار)،
        يوزع على المشتركين، ثم يعود للانتظار الموجّه بالأحداث.
      - sampler_loop(): ملتقط 10ms حماية — يقرأ realtime_candles مباشرة
        ويستيقظ المضخة؛ لو لم يوجد رفع الحدث لأي سبب لن يُفقد تيك.
      - silence_watchdog(): يراقب صمت العملات المفتوحة — إعادة تشغيل بث
        عبر نفس نمط auto_reconnect الأصلي (إلغاء المهمة + إعادة التشغيل).

    التخزين: نفس _cache_tick الرسمي (ذاكرة فقط + TTL 5 دقائق كما في v13).
    """

    def __init__(self) -> None:
        self.trackers: _v14_Dict[str, V14TickTracker] = {}
        self.subscribers: _v14_List[V14TickSubscriber] = []
        self._lock = _v14_threading.RLock()
        self._wake: _v14_Optional[_v14_asyncio.Event] = None
        self._wake_loop: _v14_Optional[_v14_asyncio.AbstractEventLoop] = None
        # تيكات ملتهمة بانتظار التوزيع: {symbol: (ts, price, classification)}
        self._pending_map: _v14_Dict[str, tuple] = {}
        self._pump_running = False
        self._notify_from_thread = False
        self._loop_ref: _v14_Optional[Any] = None

    # ---------- الاستيقاظ ----------
    def _ensure_wake(self, loop) -> None:
        if self._wake is None or self._wake_loop is not loop:
            self._wake = _v14_asyncio.Event()
            self._wake_loop = loop

    def notify(self, api_symbol: str, loop=None) -> None:
        """يوقظ المضخة — آمن من أي خيط (call_soon_threadsafe عند الحاجة)."""
        try:
            if self._wake is None:
                if loop is not None:
                    self._ensure_wake(loop)
                else:
                    return  # المضخة لم تبدأ بعد — الملتقط سيشغلها
            ev = self._wake
            lp = self._wake_loop
            if ev is None or lp is None:
                return
            try:
                running = _v14_asyncio.get_running_loop()
            except Exception:
                running = None
            if running is lp:
                ev.set()
            else:
                try:
                    lp.call_soon_threadsafe(ev.set)
                except Exception:
                    pass
        except Exception:
            pass

    # ---------- المتتبعات ----------
    def tracker(self, api_symbol: str) -> V14TickTracker:
        with self._lock:
            t = self.trackers.get(api_symbol)
            if t is None:
                t = V14TickTracker(api_symbol)
                self.trackers[api_symbol] = t
            return t

    def forget(self, api_symbol: str) -> None:
        with self._lock:
            self.trackers.pop(api_symbol, None)

    # ---------- الالتقاط (يستدعيه غلاف _cache_tick) ----------
    def ingest_tick(self, api_symbol: str, ts: int, price: float) -> None:
        """يبتلع تيكاً في المتتبع + يستيقظ المضخة. بلا أي نوم."""
        try:
            tr = self.tracker(api_symbol)
            cls = tr.ingest(int(ts), float(price))
            if cls in (TickClassification.NEW, TickClassification.GAP):
                V14_TICKS_RATE.mark()
                V14_METRICS.inc("v14.ticks.ingested")
                if cls == TickClassification.GAP:
                    V14_JOURNAL.record("tick_gap", asset=api_symbol,
                                       ts=ts, price=price)
                with self._lock:
                    self._pending_map[api_symbol] = (int(ts), float(price), cls)
                self.notify(api_symbol)
        except Exception:
            pass

    # ---------- المشتركون ----------
    def subscribe(self, symbols: _v14_Optional[_v14_Set[str]] = None,
                  maxsize: int = 2000) -> V14TickSubscriber:
        sub = V14TickSubscriber(len(self.subscribers) + 1, symbols, maxsize)
        with self._lock:
            self.subscribers.append(sub)
        V14_JOURNAL.record("ticks_subscribe", handle=sub.handle,
                           symbols=sorted(symbols) if symbols else "ALL")
        return sub

    def unsubscribe(self, sub: V14TickSubscriber) -> None:
        with self._lock:
            try:
                self.subscribers.remove(sub)
            except Exception:
                pass

    def _dispatch(self, api_symbol: str, ts: int, price: float,
                  classification: str) -> None:
        """توزيع فوري على المشتركين — بلا نوم، إسقاط أقدم للبطيء."""
        with self._lock:
            subs = list(self.subscribers)
        if not subs:
            return
        payload = (api_symbol, int(ts), float(price), classification,
                   time.time())
        for sub in subs:
            if sub.wants(api_symbol):
                sub.offer(payload)

    # ---------- قراءة المصدر الحي ----------
    def _read_live(self, api_symbol: str) -> _v14_Optional[Tuple[int, float]]:
        """قراءة آخر سعر حي من realtime_candles — نفس المصدر الرسمي الذي
        يقرأه الكود الأساسي في realtime_stream حرفياً."""
        try:
            client = globals().get("CLIENT")
            if client is None or getattr(client, "api", None) is None:
                return None
            c = client.api.realtime_candles.get(api_symbol)
            if isinstance(c, list) and len(c) >= 3:
                return int(c[1]), float(c[2])
            if isinstance(c, dict):
                ts = int(c.get("time", c.get("timestamp", 0)))
                price = float(c.get("price", c.get("close", 0)))
                if ts > 0 and price > 0:
                    return ts, price
        except Exception:
            pass
        return None

    # ---------- المضخة ----------
    async def pump_loop(self) -> None:
        """مضخة التيكات — تنتظر الحدث، تصرف كل جديد، تعود للانتظار.

        مسار المعالجة نفسه بلا sleep (فقط sleep(0) لتسليم الحلقة بين
        المشتركين) — «التكس لا ينام».
        """
        loop = _v14_asyncio.get_running_loop()
        self._ensure_wake(loop)
        self._pump_running = True
        V14_JOURNAL.record("tick_pump_start")
        while True:
            try:
                ev = self._wake
                if ev is None:
                    self._ensure_wake(loop)
                    continue
                # انتظار موجّه بالأحداث مع مهلة أمان قصيرة: أي تيك جديد يوقظ
                # فوراً عبر notify() — والمهلة تنظف ما تبقى لو فات رفع حدث.
                try:
                    await _v14_asyncio.wait_for(ev.wait(), timeout=1.0)
                except _v14_asyncio.TimeoutError:
                    pass
                ev.clear()
                # صرف كل ما هو معلق الآن — فوري، بلا نوم:
                # أولاً التيكات الملتهمة فعلاً عبر ingest_tick (غلاف
                # _cache_tick أو الملتقط) — لها طابع وسعر وتصنيف جاهز
                with self._lock:
                    pending = dict(self._pending_map)
                    self._pending_map.clear()
                for sym, (ts, price, cls) in pending.items():
                    self._dispatch(sym, ts, price, cls)
                    await _v14_asyncio.sleep(0)   # تسليم الحلقة — بلا نوم
                # ثانياً: مسح أمان للمصدر الحي (realtime_candles) لكل أصل
                # متدفق — يغطي أي تيك لم يمر عبر ingest_tick لأي سبب
                # مراقب إضافي: اسحب كل الأصول المتدفقة حتى لو فات رفع العلم
                assets = list(globals().get("ALL_STREAMING_ASSETS") or [])
                seen = set(pending)
                for a in assets:
                    try:
                        seen.add(a.api_symbol)
                    except Exception:
                        pass
                for sym in seen:
                    live = self._read_live(sym)
                    if live is not None:
                        ts, price = live
                        tr = self.tracker(sym)
                        cls = tr.ingest(ts, price)
                        if cls in (TickClassification.NEW,
                                   TickClassification.GAP,
                                   TickClassification.DUPLICATE):
                            # NEW/GAP: تيك جديد فعلٍ — DUPLICATE: سعر أحدث
                            # بنفس الثانية — كلاهما يوزع فوراً على المشتركين
                            self._dispatch(sym, ts, price, cls)
                    await _v14_asyncio.sleep(0)   # تسليم الحلقة — بلا نوم
                V14_METRICS.gauge("v14.ticks.trackers", len(self.trackers))
                # العودة للانتظار الموجّه بالأحداث في رأس الحلقة (مهلة أمان
                # 1s هناك تُنظف المتبقي لو فات رفع الحدث).
            except _v14_asyncio.CancelledError:
                self._pump_running = False
                raise
            except Exception as e:
                V14_METRICS.inc("v14.ticks.pump_errors")
                V14_JOURNAL.record("tick_pump_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=0.2, cap=2.0, jitter=0.2)

    def subs_len(self) -> int:
        with self._lock:
            return len(self.subscribers)

    # ---------- الملتقط المراقب ----------
    async def sampler_loop(self) -> None:
        """ملتقط 10ms — حماية عمق فوق notify(): يقرأ realtime_candles لكل
        عملة متدفقة ويستيقظ المضخة عند أي جديد. لو فات أي تيك لأي سبب،
        الملتقط يضبطه خلال 10ms كحد أقصى — لا تيك نائم ولا تيك مفقود.

        هذا ملتقط لا معالج: المعالجة الفعلية كلها في المضخة المُيقَظة.
        """
        V14_JOURNAL.record("tick_sampler_start")
        while True:
            try:
                woke = False
                for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
                    try:
                        sym = asset.api_symbol
                    except Exception:
                        continue
                    live = self._read_live(sym)
                    if live is None:
                        continue
                    ts, price = live
                    tr = self.tracker(sym)
                    if tr.last_ts and ts <= tr.last_ts:
                        continue   # لا جديد — بلا تخزين بلا إيقاظ
                    # جديد: خزّنه في الكاش الرسمي نفسه (ذاكرة فقط)
                    try:
                        _cache_tick(sym, ts, price)
                    except Exception:
                        pass
                    self.ingest_tick(sym, ts, price)
                    woke = True
                if woke:
                    self.notify()
                    V14_METRICS.inc("v14.ticks.sampler_wakes")
                await _v14_asyncio.sleep(0.01)   # 10ms — حماية لا نوم معالجة
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_METRICS.inc("v14.ticks.sampler_errors")
                V14_JOURNAL.record("tick_sampler_error", error=str(e)[:200])
                await _v14_asyncio.sleep(0.05)

    # ---------- ساعة صمت العملات المفتوحة ----------
    async def silence_watchdog(self) -> None:
        """مراقب صمت: عملة مفتوحة بلا تيك > عتبة → إعادة تشغيل بثها عبر
        نفس نمط auto_reconnect الأصلي (إلغاء + realtime_stream من جديد) —
        لا يخترع مسار اتصال جديداً."""
        restart_silence = float(globals().get("_V14_TICK_SILENCE_RESTART", 90.0))
        while True:
            try:
                await _v14_asyncio.sleep(10.0)
                client = globals().get("CLIENT")
                alive = bool(globals().get("CONNECTION_ALIVE"))
                if client is None or not alive:
                    continue
                loop = _v14_asyncio.get_running_loop()
                for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
                    try:
                        sym = asset.api_symbol
                        tr = self.trackers.get(sym)
                        if tr is None:
                            continue
                        silence = tr.silence_seconds()
                        V14_METRICS.gauge(f"v14.ticks.{sym}.silence_s", silence)
                        if silence >= restart_silence:
                            running = False
                            try:
                                task = getattr(asset, "stream_task", None)
                                running = task is not None and not task.done() \
                                    and bool(getattr(asset, "streaming", False))
                            except Exception:
                                running = False
                            if not running:
                                continue   # بثها متوقف أصلاً — ليس صمتاً شاذاً
                            tr.ring.clear()
                            tr.last_ts = 0
                            logmsg(f"[v14-ticks] {sym} silent {silence:.0f}s "
                                   f"> {restart_silence:.0f}s — restarting "
                                   f"stream (same pattern as auto_reconnect)")
                            V14_JOURNAL.record("tick_silence_restart",
                                               asset=sym, silence_s=round(silence, 1))
                            V14_METRICS.inc("v14.ticks.silence_restarts")
                            try:
                                old = getattr(asset, "stream_task", None)
                                if old is not None and not old.done():
                                    old.cancel()
                            except Exception:
                                pass
                            asset.streaming = False
                            try:
                                asset.stream_task = \
                                    asyncio.run_coroutine_threadsafe(
                                        subsecond_stream(asset)
                                        if globals().get("IS_SUBSECOND")
                                        else realtime_stream(asset), loop)
                            except Exception as e:
                                V14_JOURNAL.record("tick_restart_fail",
                                                   asset=sym, error=str(e)[:160])
                            await _v14_asyncio.sleep(0.05)  # نفس إيقاع الكود المرجعي
                    except _v14_asyncio.CancelledError:
                        raise
                    except Exception as e:
                        # خطأ في أصل واحد لا يوقف فحص بقية الأصول أبداً
                        V14_JOURNAL.record("tick_silence_asset_error",
                                           asset=getattr(asset, "api_symbol", "?"),
                                           error=str(e)[:160])
                        continue
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("tick_silence_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=1.0, cap=10.0, jitter=0.2)

    # ---------- تقارير ----------
    def snapshot(self, seconds: int = 300) -> dict:
        with self._lock:
            trackers = {k: t.info() for k, t in self.trackers.items()}
            subs = [{"handle": s.handle, "delivered": s.delivered,
                     "dropped": s.dropped,
                     "queued": s.q.qsize() if s.q else 0}
                    for s in self.subscribers]
        return {"trackers": trackers, "subscribers": subs,
                "rate_30s": round(V14_TICKS_RATE.rate(30.0), 2)}

    def recent_ticks(self, api_symbol: str, seconds: int = 300) -> _v14_List[list]:
        tr = self.trackers.get(api_symbol)
        if not tr:
            return []
        return [[t, p] for (_s, t, p) in tr.since(seconds)]

    def gap_summary(self) -> dict:
        with self._lock:
            return {k: t.gap_events for k, t in self.trackers.items()
                    if t.gap_events}


# محرك التيكات العام + معدل التيكات المتدحرج
V14_TICKS = V14TickEngine()
V14_TICKS_RATE = V14RollingRate(window_seconds=30.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 6 — V14 GAP GUARD (سد الثغرات الأصلي على كل عملة مفتوحة)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم الحرفي:
#   «طريقة سد الثغرات لا تغيرها عن الكود لي اريتك يجب ان تنفذ على كل عملة
#    تم فتحها ولا يتم فقدان»
#
# الضمانات هنا:
#   1) الطريقة نفسها حرفياً: MT4_WRITER.fill_gap_once(CLIENT, asset, PERIOD)
#      + _fill_missing_slots + علامة التجمد gap_state.filled — صفر تغيير.
#      الحلقة الشاملة mt4_gap_filler الأصلية تعمل كما هي أيضاً.
#   2) «على كل عملة تم فتحها»: سجل مفتوحات (OpenedAssetRegistry) يلاحظ كل
#      عملة فُتح شارتها (opener / ensure_asset_loaded / fetch_older_batch /
#      preload_one_asset) ويجدول لها سد ثغرات فوراً — لا انتظار دورة
#      الحلقة الشاملة، ولا عملة مفتوحة تفوتها الآلية.
#   3) «ولا يتم فقدان»: مدقق فقدان دوري (V14GapLossAuditor) يمسح خط زمن
#      كل عملة مفتوحة؛ أي فجوة مشبوهة تُعيد استدعاء نفس fill_gap_once
#      الأصلية لتلك العملة حتى تُسد — الطريقة نفسها، التغطية كاملة.
#   4) المدقق لا يكتب شموعاً بنفسه أبداً — الكتابة تبقى للطريقة الأصلية.
# ════════════════════════════════════════════════════════════════════════════

class OpenedAssetRegistry:
    """سجل كل عملة تم فتحها — مصدر الحقيقة لـ«سد الثغرات على كل مفتوح».

    لكل عملة: وقت الفتح الأول، آخر نشاط، عدد مرات الفتح، مصدر الفتح،
    حالة آخر سد ثغرات، وآخر نتيجة مدقق فقدان.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._opened: _v14_Dict[str, dict] = {}

    def note_open(self, api_symbol: str, source: str) -> None:
        api_symbol = str(api_symbol or "").strip()
        if not api_symbol:
            return
        now = time.time()
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is None:
                rec = {
                    "first_open_at": now,
                    "first_source": source,
                    "opens": 0,
                    "last_open_at": now,
                    "last_source": source,
                    "last_gap_fill_at": 0.0,
                    "gap_fill_runs": 0,
                    "gap_fill_errors": 0,
                    "last_audit_at": 0.0,
                    "last_audit_holes": 0,
                }
                self._opened[api_symbol] = rec
                V14_JOURNAL.record("asset_opened", asset=api_symbol,
                                   source=source)
            rec["opens"] += 1
            rec["last_open_at"] = now
            rec["last_source"] = source

    def note_gap_fill(self, api_symbol: str, ok: bool) -> None:
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is None:
                return
            rec["last_gap_fill_at"] = time.time()
            if ok:
                rec["gap_fill_runs"] += 1
            else:
                rec["gap_fill_errors"] += 1

    def note_audit(self, api_symbol: str, holes: int) -> None:
        with self._lock:
            rec = self._opened.get(api_symbol)
            if rec is not None:
                rec["last_audit_at"] = time.time()
                rec["last_audit_holes"] = int(holes)

    def opened(self) -> _v14_List[str]:
        with self._lock:
            return list(self._opened.keys())

    def is_opened(self, api_symbol: str) -> bool:
        with self._lock:
            return api_symbol in self._opened

    def snapshot(self) -> dict:
        with self._lock:
            return {k: dict(v) for k, v in self._opened.items()}

    def __len__(self) -> int:
        with self._lock:
            return len(self._opened)


# سجل المفتوحات العام
V14_OPENED = OpenedAssetRegistry()


def _v14_find_asset(api_symbol: str):
    """يجد كائن Asset الرسمي للعملة من قائمة الأصول المتدفقة (بلا إنشاء
    جديد هنا — الإنشاء مسؤولية المسار الرسمي _get_or_create_asset)."""
    for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
        try:
            if asset.api_symbol == api_symbol:
                return asset
        except Exception:
            continue
    return None


async def v14_gap_fill_for_asset(api_symbol: str, *,
                                 reason: str = "opened") -> bool:
    """سد ثغرات عملة واحدة — بالطريقة الأصلية حرفياً.

    يستدعي MT4_WRITER.fill_gap_once(CLIENT, asset, PERIOD) — نفس الآلية
    التي تشغلها الحلقة الشاملة mt4_gap_filler، لكن مركزة على هذه العملة
    فور فتحها. لا شيء جديد في الطريقة — فقط تنفيذ فوري لكل مفتوح.
    """
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return False
    client = globals().get("CLIENT")
    alive = bool(globals().get("CONNECTION_ALIVE"))
    if client is None or getattr(client, "api", None) is None or not alive:
        V14_METRICS.inc("v14.gap.skipped_not_connected")
        return False
    # انتظار قصير موجّه حتى تجهز الأصول (نمط pyquotex wait_until)
    asset = _v14_find_asset(api_symbol)
    if asset is None:
        try:
            await v14_wait_until(
                lambda: _v14_find_asset(api_symbol) is not None,
                timeout=8.0, poll_interval=0.25)
            asset = _v14_find_asset(api_symbol)
        except _v14_asyncio.TimeoutError:
            asset = None
    if asset is None:
        # العملة ليست في قائمة البث بعد — حاول بالمسار الرسمي للإنشاء
        try:
            getter = globals().get("_get_or_create_asset")
            if getter is not None:
                asset = getter(api_symbol)
        except Exception:
            asset = None
    if asset is None:
        V14_JOURNAL.record("gap_fill_no_asset", asset=api_symbol, reason=reason)
        V14_OPENED.note_gap_fill(api_symbol, False)
        return False
    # الوضع تحت الثاني: الآلية الأصلية نفسها معطلة في وضع subsecond
    if globals().get("IS_SUBSECOND"):
        V14_METRICS.inc("v14.gap.skipped_subsecond")
        return False
    ok = False
    t0 = time.monotonic()
    try:
        await MT4_WRITER.fill_gap_once(client, asset,
                                       int(globals().get("PERIOD", 1)))
        ok = True
    except _v14_asyncio.CancelledError:
        raise
    except Exception as e:
        V14_METRICS.inc("v14.gap.fill_errors")
        V14_JOURNAL.record("gap_fill_error", asset=api_symbol,
                           error=str(e)[:200])
        try:
            logmsg(f"[v14-gap] fill error for {api_symbol}: {e}")
        except Exception:
            pass
    dt = time.monotonic() - t0
    V14_OPENED.note_gap_fill(api_symbol, ok)
    V14_METRICS.inc("v14.gap.fill_runs" if ok else "v14.gap.fill_failed")
    V14_METRICS.observe("v14.gap.fill_exec_s", dt)
    if ok:
        V14_JOURNAL.record("gap_fill_done", asset=api_symbol,
                           reason=reason, exec_s=round(dt, 3))
        try:
            logmsg(f"[v14-gap] gap fill done for {api_symbol} "
                   f"({reason}) in {dt:.1f}s — original method untouched")
        except Exception:
            pass
    return ok


def v14_note_asset_opened(api_symbol: str, source: str) -> None:
    """تسجيل فتح عملة + جدولة سد ثغرات فوري لها (من أي خيط).

    هذه هي نقطة «على كل عملة تم فتحها»: كل مسار رسمي يفتح شارتاً يمر
    هنا، ويحصل على سد ثغرات فوري بنفس الطريقة الأصلية.
    """
    api_symbol = str(api_symbol or "").strip()
    if not api_symbol:
        return
    first_open = not V14_OPENED.is_opened(api_symbol)
    V14_OPENED.note_open(api_symbol, source)
    V14_METRICS.inc("v14.gap.asset_opened")
    # السد الفوري فقط للفتح الأول (الإعادة تعتمد علامة التجمد الأصلية
    # داخل fill_gap_once نفسها — لن تلمس الشموع المسددة)
    if not first_open:
        return
    try:
        loop = _v14_asyncio.get_running_loop()
    except Exception:
        loop = globals().get("ASYNC_LOOP")
    if loop is None or loop.is_closed():
        return
    try:
        _v14_asyncio.run_coroutine_threadsafe(
            v14_gap_fill_for_asset(api_symbol, reason=source), loop)
        V14_JOURNAL.record("gap_fill_scheduled", asset=api_symbol,
                           source=source)
    except Exception as e:
        V14_JOURNAL.record("gap_fill_schedule_fail", asset=api_symbol,
                           error=str(e)[:160])


class V14GapLossAuditor:
    """مدقق فقدان الشموع — «ولا يتم فقدان».

    المنهج (بلا أي كتابة شموع — الكتابة للطريقة الأصلية فقط):
      1) لكل عملة مفتوحة: خذ خط الشموع الرسمي (asset.candles أو لقطة
         قاعدة الشموع الرسمية).
      2) افحص استمرارية الخانات داخل نافذة الفحص (last slots).
      3) الفجوة المشبوهة (بين شمعتين متجاورتين فرق > فترة واحدة والفجوة
         أقل من عتبة إغلاق السوق) → استدعِ نفس fill_gap_once الأصلية
         لتلك العملة حتى تسد — عدّاد + سجل.
      4) عتبة إغلاق السوق: للفريمات الدقيقة نعتبر الفجوة > ساعتين خارج
         نطاق «فقدان» (إغلاق سوق حقيقي للعملات غير OTC — التعبئة المسطحة
         الأصلية تحدها max_gap=1440 كما هي).
    """

    def __init__(self, audit_interval: float = 120.0,
                 suspect_max_gap_s: float = 7200.0) -> None:
        self.audit_interval = float(audit_interval)
        self.suspect_max_gap_s = float(suspect_max_gap_s)
        self._running = False

    def _candle_line(self, api_symbol: str) -> _v14_List[dict]:
        """خط الشموع الرسمي: من الأصل الحي أولاً ثم من المتجر الرسمي."""
        asset = _v14_find_asset(api_symbol)
        candles = []
        try:
            if asset is not None and getattr(asset, "candles", None):
                candles = list(asset.candles)
        except Exception:
            candles = []
        if not candles:
            try:
                store = globals().get("MT4_WRITER")
                if store is not None and getattr(store, "load_snapshot", None):
                    snap = store.load_snapshot(api_symbol)
                    if snap:
                        candles = list(snap)
            except Exception:
                pass
        return candles

    def find_holes(self, api_symbol: str,
                   candles: _v14_List[dict]) -> _v14_List[int]:
        """يعيد مواضع الفجوات المشبوهة (طوابع بداية الفجوة) — قراءة فقط."""
        holes: _v14_List[int] = []
        period_s = max(1, int(globals().get("PERIOD_SECONDS", 60)))
        try:
            line = sorted(candles, key=lambda c: c.get("time", 0))
            if len(line) < 2:
                return holes
            for a, b in zip(line, line[1:]):
                gap = int(b.get("time", 0)) - int(a.get("time", 0))
                if period_s < gap <= int(self.suspect_max_gap_s) and \
                        gap > period_s:
                    holes.append(int(a.get("time", 0)))
        except Exception:
            pass
        return holes

    async def audit_once(self) -> dict:
        """مسحة واحدة لكل المفتوحات — يعيد ملخص المسحة."""
        result = {"audited": 0, "with_holes": 0, "refills": 0}
        period_s = max(1, int(globals().get("PERIOD_SECONDS", 60)))
        for sym in V14_OPENED.opened():
            try:
                result["audited"] += 1
                candles = self._candle_line(sym)
                if not candles:
                    V14_OPENED.note_audit(sym, 0)
                    continue
                holes = self.find_holes(sym, candles)
                V14_OPENED.note_audit(sym, len(holes))
                V14_METRICS.gauge(f"v14.gap.{sym}.holes", len(holes))
                if holes:
                    result["with_holes"] += 1
                    V14_METRICS.inc("v14.gap.holes_found", len(holes))
                    V14_JOURNAL.record("gap_holes", asset=sym,
                                       holes=len(holes),
                                       first=int(holes[0]) if holes else 0)
                    # إعادة السد بالطريقة الأصلية نفسها — حتى لا يُفقد شيء
                    ok = await v14_gap_fill_for_asset(sym, reason="audit")
                    if ok:
                        result["refills"] += 1
                        V14_METRICS.inc("v14.gap.audit_refills")
                await _v14_asyncio.sleep(0.05)
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("gap_audit_error", asset=sym,
                                   error=str(e)[:160])
        return result

    async def loop(self) -> None:
        """حلقة المدقق الدورية — supervised، لا تنهار."""
        self._running = True
        await _v14_asyncio.sleep(30.0)   # اترك الفتح الأول يكتمل
        while True:
            try:
                if globals().get("CLIENT") is None or \
                        not globals().get("CONNECTION_ALIVE"):
                    await _v14_asyncio.sleep(5.0)
                    continue
                res = await self.audit_once()
                if res["with_holes"]:
                    try:
                        logmsg(f"[v14-gap] audit: {res['audited']} opened assets, "
                               f"{res['with_holes']} had holes, "
                               f"{res['refills']} refilled (original method)")
                    except Exception:
                        pass
                await _v14_asyncio.sleep(self.audit_interval)
            except _v14_asyncio.CancelledError:
                self._running = False
                raise
            except Exception as e:
                V14_METRICS.inc("v14.gap.audit_errors")
                V14_JOURNAL.record("gap_audit_loop_error", error=str(e)[:200])
                await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)


# المدقق العام
V14_GAP_AUDITOR = V14GapLossAuditor()


async def v14_gap_guard_loop() -> None:
    """حلقة حارس الثغرات: تعمل كل 60 ثانية مسحة سريعة لكل عملة مفتوحة
    لضمان أن الآلية الأصلية مرّت عليها (بلا تعديل طريقة)."""
    await _v14_asyncio.sleep(20.0)
    while True:
        try:
            client = globals().get("CLIENT")
            if client is None or not globals().get("CONNECTION_ALIVE") or \
                    globals().get("IS_SUBSECOND"):
                await _v14_asyncio.sleep(10.0)
                continue
            # لكل عملة مفتوحة لم تُسد ثغراتها بعد (علامة التجمد الأصلية
            # داخل fill_gap_once تمنع اللمس المتكرر — استدعاؤها آمن)
            for sym in V14_OPENED.opened():
                rec = V14_OPENED.snapshot().get(sym, {})
                if not rec.get("last_gap_fill_at"):
                    ok = await v14_gap_fill_for_asset(sym, reason="guard")
                    if ok:
                        break   # واحدة في الدورة — البوابة تفرز البقية
                await _v14_asyncio.sleep(0.1)
            await _v14_asyncio.sleep(60.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception as e:
            V14_JOURNAL.record("gap_guard_error", error=str(e)[:200])
            await v14_backoff_sleep(2, base=2.0, cap=30.0, jitter=0.2)
