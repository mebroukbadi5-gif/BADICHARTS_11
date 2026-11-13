# ════════════════════════════════════════════════════════════════════════════
# v14 الجزء C — الوحدات 7 و 8 و 9 + نقاط الربط:
#   7) V14 SUPERVISOR — دون انهيار الخوادم (مشرف كل حلقة + خطافات استثناء
#      + حصاد المهام + حارس ذاكرة/قرص + تفريغ حمل + نبضة حياة)
#   8) V14 RESILIENCE — إعادة تشغيل البث بعد العودة (نمط pyquotex) + مراقب
#      جلسة + خطافات التركيب على المسارات الرسمية (بلا تعديل المسارات)
#   9) V14 API — الواجهة العامة للتطبيق + بناء حلقات الخلفية المشرفة
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 7 — V14 SUPERVISOR (دون انهيار الخوادم)
# ════════════════════════════════════════════════════════════════════════════
# طلب المستخدم: «تخص في تقويت السرفر وطريقة العمل دون انهيار الخوادم».
#
# الفكرة الجوهرية — نفس عقد pyquotex/ws/client.py::run_forever مطبق على كل
# حلقة خلفية في الخادم:
#   while True:
#       try: await connect_once(); attempt = 0      # النجاح يصفّر العداد
#       except: backoff_sleep(attempt); attempt += 1
#
# أي حلقة تموت (استثناء غير متوقع) يُعاد تشغيلها بـ backoff مهزوز — الخادم
# لا ينهار من انهيار حلقة واحدة. فوق ذلك:
#   - خطافات استثناء عامة (sys + threading + حلقة asyncio): كل شيء يُسجل.
#   - حصاد المهام الميتة الصامتة كل 30 ثانية.
#   - حارس ذاكرة (gc عند العتبات) وحارس قرص (تفريغ الحمل عند امتلاء).
#   - تفريغ حمل GRREN/AMBER/RED — RED يوقف الصيانة فقط؛ البث الحي وسد
#     الثغرات وفتح الشموع للمستخدم لا يتوقفان أبداً.
#   - نبضة حياة heartbeat JSON كل 10 ثوانٍ — إثبات حياة للخادم والتطبيق.
# ════════════════════════════════════════════════════════════════════════════

class V14LoopStatus:
    """حالة حلقة واحدة تحت المشرف."""
    __slots__ = ("name", "runs", "crashes", "last_alive_at", "last_error",
                 "last_error_at", "ever_started")

    def __init__(self, name: str) -> None:
        self.name = name
        self.runs = 0
        self.crashes = 0
        self.last_alive_at = 0.0
        self.last_error = ""
        self.last_error_at = 0.0
        self.ever_started = False


class V14Supervisor:
    """مشرف الحلقات — كل حلقة خلفية في v14 تعيش تحت إشرافه.

    الضمانات:
      - إعادة تشغيل تلقائية بـ backoff مهزوز (نمط pyquotex run_forever).
      - سقف معدل إعادة التشغيل: بعد 6 انهيارات/ساعة للحلقة الواحدة تُترك
        تنام 300 ثانية (حماية من دوران انهيار يشعل المعالج).
      - كل انهيار: عدّاد + سجل جلسة + رسالة ترمينال — لا صمت.
      - status() يعيد حالة كل الحلقات للنبضة والتقارير.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._statuses: _v14_Dict[str, V14LoopStatus] = {}
        self._restart_timestamps: _v14_Dict[str, _v14_List[float]] = {}
        self.started_at = time.time()

    def status_of(self, name: str) -> V14LoopStatus:
        with self._lock:
            st = self._statuses.get(name)
            if st is None:
                st = V14LoopStatus(name)
                self._statuses[name] = st
            return st

    def _restart_backoff(self, name: str) -> float:
        """سقف معدل الإعادة: 6/ساعة لكل حلقة → نوم طويل 300 ثانية."""
        now = time.monotonic()
        with self._lock:
            stamps = self._restart_timestamps.setdefault(name, [])
            while stamps and (now - stamps[0]) > 3600.0:
                stamps.pop(0)
            stamps.append(now)
            rate_ok = len(stamps) <= 6
        if rate_ok:
            return 0.0
        return 300.0

    async def supervise(self, name: str,
                        factory: Callable[[], _v14_Awaitable]) -> None:
        """يشغل الحلقة للأبد — يعيد تشغيلها عند كل موت بلا استسلام."""
        st = self.status_of(name)
        attempt = 0
        while True:
            try:
                st.ever_started = True
                st.runs += 1
                st.last_alive_at = time.time()
                V14_JOURNAL.record("loop_start", loop=name, run=st.runs)
                await factory()
                # الحلقة اللانهائية لا تعود عادة — عودتها تعامل كتوقف لطيف
                st.last_alive_at = time.time()
                V14_JOURNAL.record("loop_returned", loop=name)
                await _v14_asyncio.sleep(1.0)
                attempt = 0
            except _v14_asyncio.CancelledError:
                V14_JOURNAL.record("loop_cancelled", loop=name)
                raise
            except Exception as e:
                attempt += 1
                st.crashes += 1
                st.last_error = f"{type(e).__name__}: {e}"[:200]
                st.last_error_at = time.time()
                V14_METRICS.inc("v14.supervisor.loop_crashes")
                V14_METRICS.inc(f"v14.supervisor.crash.{name}")
                V14_JOURNAL.record("loop_crash", loop=name,
                                   run=st.runs, attempt=attempt,
                                   error=st.last_error)
                try:
                    logmsg(f"[v14-supervisor] loop '{name}' crashed "
                           f"(run {st.runs}, attempt {attempt}): "
                           f"{st.last_error} — restarting")
                except Exception:
                    pass
                # سقف معدل الإعادة ثم backoff مهزوز (نمط pyquotex)
                extra = self._restart_backoff(name)
                if extra:
                    try:
                        logmsg(f"[v14-supervisor] loop '{name}' restart-rate "
                               f"cap hit — cooling down {extra:.0f}s")
                    except Exception:
                        pass
                    await _v14_asyncio.sleep(extra)
                await v14_backoff_sleep(attempt, base=0.5, cap=30.0, jitter=0.15)

    def status(self) -> dict:
        with self._lock:
            out = {}
            for name, st in self._statuses.items():
                out[name] = {
                    "runs": st.runs,
                    "crashes": st.crashes,
                    "ever_started": st.ever_started,
                    "age_since_alive_s": round(time.time() - st.last_alive_at, 1)
                    if st.last_alive_at else None,
                    "last_error": st.last_error,
                }
            return out

    def alive_count(self) -> int:
        with self._lock:
            return sum(1 for st in self._statuses.values()
                       if st.ever_started and not st.last_error)


# المشرف العام
V14_SUPERVISOR = V14Supervisor()


async def v14_supervise(name: str,
                        factory: Callable[[], _v14_Awaitable]) -> None:
    """نقطة دخول موحدة: يشغّل أي حلقة تحت المشرف — تستخدم من __main__ ومن
    التطبيق بنفس الطريقة."""
    await V14_SUPERVISOR.supervise(name, factory)


def install_v14_exception_hooks() -> None:
    """خطافات استثناء عامة — كل خطأ غير ملتقط يُسجل ولا يُسقط الخادم.

    يغطي الثلاثة:
      - sys.excepthook: الاستثناءات في الخيط الرئيسي.
      - threading.excepthook: الاستثناءات في خيوط النظام (العدّاء الكاتب...).
      - loop.set_exception_handler: المهام الصامتة في حلقة asyncio.
    """
    def _hook(exc_type, exc_value, exc_tb) -> None:
        try:
            V14_METRICS.inc("v14.hooks.uncaught")
            V14_JOURNAL.record("uncaught",
                               kind="sys",
                               error=f"{exc_type.__name__}: {exc_value}")
            try:
                logmsg(f"[v14-hook] uncaught exception: "
                       f"{exc_type.__name__}: {exc_value}")
            except Exception:
                pass
        except Exception:
            pass

    try:
        old_hook = getattr(sys, "excepthook", None)
        sys.excepthook = _hook
    except Exception:
        pass

    try:
        import threading as _th
        _old_th = getattr(_th, "excepthook", None)

        def _thread_hook(args) -> None:
            try:
                V14_METRICS.inc("v14.hooks.uncaught")
                V14_JOURNAL.record(
                    "uncaught", kind="thread",
                    thread=getattr(args, "thread", None) and
                    args.thread.name or "?",
                    error=f"{getattr(args, 'exc_type', type(None)).__name__}: "
                          f"{getattr(args, 'exc_value', None)}")
                try:
                    logmsg(f"[v14-hook] uncaught in thread: {args}")
                except Exception:
                    pass
            except Exception:
                pass
        _th.excepthook = _thread_hook
    except Exception:
        pass

    # معالج استثناءات حلقة asyncio — يُثبَّت عند بدء الحلقات المشرفة
    def _loop_handler(loop, context) -> None:
        try:
            exc = context.get("exception")
            msg = context.get("message", "")
            V14_METRICS.inc("v14.hooks.loop_exceptions")
            V14_JOURNAL.record("loop_exception",
                               message=str(msg)[:160],
                               error=f"{type(exc).__name__}: {exc}" if exc else "")
        except Exception:
            pass

    try:
        loop = globals().get("ASYNC_LOOP")
        if loop is not None:
            loop.set_exception_handler(_loop_handler)
    except Exception:
        pass


class V14TaskHarvester:
    """حصاد المهام الميتة الصامتة — يستيقظ كل 30 ثانية ويمسح كل المهام
    المنتهية باستثناء لم تُقرأ نتيجتها (تلك التي كانت ستُخفى بصمت)."""

    def __init__(self) -> None:
        self._seen: _v14_Set[int] = set()
        self.harvested = 0

    async def loop(self) -> None:
        await _v14_asyncio.sleep(15.0)
        while True:
            try:
                await _v14_asyncio.sleep(30.0)
                pending_harvest = []
                for t in list(_v14_asyncio.all_tasks()):
                    try:
                        if t.done() and not t.cancelled():
                            exc = t.exception()
                            if exc is not None and \
                                    id(t) not in self._seen:
                                self._seen.add(id(t))
                                pending_harvest.append((t, exc))
                    except Exception:
                        continue
                if len(self._seen) > 4096:
                    self._seen.clear()
                for t, exc in pending_harvest:
                    self.harvested += 1
                    V14_METRICS.inc("v14.supervisor.harvested_exceptions")
                    V14_JOURNAL.record("harvested_task_exception",
                                       task=t.get_name(),
                                       error=f"{type(exc).__name__}: {exc}")
                    try:
                        logmsg(f"[v14-supervisor] harvested silent task "
                               f"exception: {type(exc).__name__}: {exc}")
                    except Exception:
                        pass
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=1.0, cap=10.0)


class V14MemoryGuard:
    """حارس ذاكرة — يأخذ RSS كل 30 ثانية ويستجيب بالعتبات:

      soft (افتراضي 512MB): gc.collect() + عدّاد.
      hard (افتراضي 768MB): gc.collect() كامل + تنظيف كاشات v14 المملوكة
                            فقط (لا يلمس شموع الأصول ولا أي بيانات رسمية
                            أبداً) + سجل + نبضة.

    RSS يقرأ من /proc/self/statm على لينكس ومن resource على غيره — بلا
    مكتبات خارجية.
    """

    def __init__(self, soft_mb: float = 512.0, hard_mb: float = 768.0) -> None:
        self.soft_mb = float(soft_mb)
        self.hard_mb = float(hard_mb)
        self.soft_events = 0
        self.hard_events = 0
        self.last_rss_mb = 0.0

    def rss_mb(self) -> float:
        try:
            # /proc/self/statm: الحقل الثاني = صفحات مقيمة (resident)
            with open("/proc/self/statm", "r") as f:
                parts = f.read().split()
            pages = int(parts[1])
            return pages * 4096.0 / (1024.0 * 1024.0)
        except Exception:
            try:
                import resource as _res
                ru = _res.getrusage(_res.RUSAGE_SELF).ru_maxrss
                return float(ru) / 1024.0   # KB→MB (لينكس)
            except Exception:
                return 0.0

    def _drop_owned_caches(self) -> None:
        """تنظيف الكاشات المملوكة لـ v14 فقط — صفر لمس للبيانات الرسمية."""
        try:
            try:
                V14_GATE._FETCH_CACHE_TTL_FLUSH = True  # noqa — لا شيء فعلي
            except Exception:
                pass
            # كاش debounce البوابة الأصلية يملكه v13 — لا نلمسه.
            # فقط المتتبعات الغنية والسجلات الفارغة:
            with V14_TICKS._lock:
                idle = [s for s, t in V14_TICKS.trackers.items()
                        if t.silence_seconds() > 600.0 and not t.ring]
                for s in idle:
                    V14_TICKS.trackers.pop(s, None)
            V14_GATE._prune_chains()
        except Exception:
            pass

    async def loop(self) -> None:
        await _v14_asyncio.sleep(20.0)
        while True:
            try:
                await _v14_asyncio.sleep(30.0)
                rss = self.rss_mb()
                self.last_rss_mb = rss
                V14_METRICS.gauge("v14.memory.rss_mb", round(rss, 1))
                if rss <= 0:
                    continue
                if rss >= self.hard_mb:
                    self.hard_events += 1
                    V14_METRICS.inc("v14.memory.hard_events")
                    collected = _v14_gc.collect(2)
                    self._drop_owned_caches()
                    V14_JOURNAL.record("memory_hard", rss_mb=round(rss, 1),
                                       collected=collected)
                    try:
                        logmsg(f"[v14-memory] HARD {rss:.0f}MB — "
                               f"gc({collected}) + owned-caches cleanup")
                    except Exception:
                        pass
                elif rss >= self.soft_mb:
                    self.soft_events += 1
                    V14_METRICS.inc("v14.memory.soft_events")
                    collected = _v14_gc.collect()
                    V14_JOURNAL.record("memory_soft", rss_mb=round(rss, 1),
                                       collected=collected)
                V14_METRICS.gauge("v14.memory.soft_events", self.soft_events)
                V14_METRICS.gauge("v14.memory.hard_events", self.hard_events)
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14DiskGuard:
    """حارس قرص — يفحص المساحة الحرة كل 10 دقائق على مجلدات HST وقاعدة
    الشموع. عند الانخفاض يفعّل تفريغ الحمل (يوقف الجلب الخلفي فقط —
    البث الحي وسد الثغرات للمفتوحات لا يتوقفان أبداً) ويسجل.

    العتبات: warn < 1GB ، shed < 500MB ، critical < 200MB.
    """

    def __init__(self) -> None:
        self.warn_free_mb = 1024.0
        self.shed_free_mb = 500.0
        self.critical_free_mb = 200.0
        self.last_free_mb = 0.0
        self.shed_active = False

    def _targets(self) -> _v14_List[str]:
        out = []
        try:
            out.append(globals().get("MT4_HISTORY_PATH") or ".")
        except Exception:
            out.append(".")
        return out

    def min_free_mb(self) -> float:
        vals = []
        for t in self._targets():
            try:
                usage = _v14_shutil.disk_usage(t)
                vals.append(usage.free / (1024.0 * 1024.0))
            except Exception:
                continue
        return min(vals) if vals else 0.0

    async def loop(self) -> None:
        await _v14_asyncio.sleep(30.0)
        while True:
            try:
                await _v14_asyncio.sleep(600.0)
                free = self.min_free_mb()
                self.last_free_mb = free
                V14_METRICS.gauge("v14.disk.free_mb", round(free, 1))
                if free <= 0:
                    continue
                if free <= self.critical_free_mb:
                    self.shed_active = True
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                    V14_JOURNAL.record("disk_critical", free_mb=round(free, 1))
                    try:
                        logmsg(f"[v14-disk] CRITICAL {free:.0f}MB free — "
                               f"background fetching paused (live streams "
                               f"and gap-fill continue)")
                    except Exception:
                        pass
                elif free <= self.shed_free_mb:
                    self.shed_active = True
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                    V14_JOURNAL.record("disk_shed", free_mb=round(free, 1))
                else:
                    if self.shed_active:
                        self.shed_active = False
                        V14_PAUSE_PRELOAD.set(False)
                        V14_JOURNAL.record("disk_recovered",
                                           free_mb=round(free, 1))
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14LoadShedder:
    """مفرّغ الحمل — يصنف الضغط GREEN/AMBER/RED من أربعة مؤشرات:

      - عمق بوابة الطلبات (تكدس = ضغط).
      - ذاكرة RSS.
      - معدل إعادة الاتصال الأخير.
      - مساحة القرص (من الحارس).

    RED: يوقف الصيانة فقط (يعلّم V14_PAUSE_PRELOAD و V14_SHED_PRESSURE).
    البث الحي، سد الثغرات للمفتوحات، وفتح الشموع للمستخدم لا يتوقفان أبداً.
    """

    def __init__(self) -> None:
        self.state = "GREEN"

    def evaluate(self) -> str:
        try:
            depth = V14_GATE.depth()
            rss = V14_MEMORY.last_rss_mb if "V14_MEMORY" in globals() else 0.0
            reconnect_hint = V14_RECONNECT_HINT.get()
            disk = V14_DISK.last_free_mb if "V14_DISK" in globals() else 0.0
            if depth >= 40 or reconnect_hint or \
                    (disk > 0 and disk <= V14_DISK.critical_free_mb):
                return "RED"
            if depth >= 15 or (rss and rss >= V14_MEMORY.soft_mb):
                return "AMBER"
            return "GREEN"
        except Exception:
            return "GREEN"

    async def loop(self) -> None:
        await _v14_asyncio.sleep(25.0)
        while True:
            try:
                await _v14_asyncio.sleep(15.0)
                new_state = self.evaluate()
                if new_state != self.state:
                    old = self.state
                    self.state = new_state
                    V14_METRICS.gauge("v14.pressure_state",
                                      {"GREEN": 0, "AMBER": 1, "RED": 2}
                                      .get(new_state, 0))
                    V14_JOURNAL.record("pressure", old=old, new=new_state)
                    try:
                        logmsg(f"[v14-shed] pressure {old} -> {new_state}")
                    except Exception:
                        pass
                if self.state == "RED":
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(True)
                elif self.state == "AMBER":
                    V14_PAUSE_PRELOAD.set(True)
                    V14_SHED_PRESSURE.set(False)
                else:
                    # GREEN: أزل العلم فقط لو حارس القرص ليس هو الفاعل
                    if not V14_DISK.shed_active:
                        V14_PAUSE_PRELOAD.set(False)
                    V14_SHED_PRESSURE.set(False)
                V14_METRICS.gauge("v14.gate.depth", V14_GATE.depth())
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=2.0, cap=15.0)


class V14Heartbeat:
    """نبضة الحياة — تكتب qx_server_heartbeat.json كل 10 ثوانٍ:

      وقت، pid، uptime، حالة الحلقات المشرفة، عمق البوابة، تيكات/ثانية،
      حالة الضغط، الذاكرة، القرص، سد الثغرات، النقاط، الجلسة.

    كتابة ذرية (tmp + rename) — القراءة آمنة دائماً من التطبيق أو المشغل.
    """

    def __init__(self, interval: float = 10.0) -> None:
        self.interval = float(interval)
        try:
            self.path = _v14_os.path.join(
                _v14_base_dir(), "qx_server_heartbeat.json")
        except Exception:
            self.path = "qx_server_heartbeat.json"
        self.writes = 0

    def payload(self) -> dict:
        try:
            mem = V14_MEMORY.rss_mb()
        except Exception:
            mem = 0.0
        try:
            disk = V14_DISK.last_free_mb
        except Exception:
            disk = 0.0
        try:
            endpoint_info = V14_ENDPOINTS.info()
        except Exception:
            endpoint_info = {}
        try:
            session = V14_SESSION.info()
        except Exception:
            session = {}
        try:
            shed = V14_LOAD_SHEDDER.state
        except Exception:
            shed = "GREEN"
        return {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": time.time(),
            "pid": _v14_os.getpid(),
            "uptime_s": round(time.time() - _V14_STARTED_AT, 1),
            "connection_alive": bool(globals().get("CONNECTION_ALIVE")),
            "active_host": globals().get("QX_HOST", ""),
            "streaming_assets": len(globals().get("ALL_STREAMING_ASSETS") or []),
            "opened_assets": len(V14_OPENED),
            "pressure": shed,
            "memory_rss_mb": round(mem, 1),
            "disk_free_mb": round(disk, 1),
            "gate": v14_gate_snapshot(),
            "ticks_rate_30s": round(V14_TICKS_RATE.rate(30.0), 2),
            "gap_fills": V14_METRICS.counter("v14.gap.fill_runs"),
            "gap_audits_holes": V14_METRICS.counter("v14.gap.holes_found"),
            "supervisor": V14_SUPERVISOR.status(),
            "endpoints": endpoint_info,
            "session": session,
            "journal": V14_JOURNAL.info(),
        }

    async def loop(self) -> None:
        await _v14_asyncio.sleep(10.0)
        while True:
            try:
                await _v14_asyncio.sleep(self.interval)
                data = self.payload()
                tmp = self.path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    _v14_json.dump(data, f, ensure_ascii=False, indent=1)
                _v14_os.replace(tmp, self.path)
                self.writes += 1
                V14_METRICS.gauge("v14.heartbeat.writes", self.writes)
            except _v14_asyncio.CancelledError:
                raise
            except Exception:
                await v14_backoff_sleep(1, base=1.0, cap=10.0)


# الكائنات العامة للحارس (تُنشأ هنا — تستعملها الحلقات ومفرّغ الحمل)
V14_MEMORY = V14MemoryGuard()
V14_DISK = V14DiskGuard()
V14_LOAD_SHEDDER = V14LoadShedder()
V14_HEARTBEAT = V14Heartbeat()


async def v14_harvester_loop() -> None:
    await V14TaskHarvester().loop()


async def v14_memory_guard_loop() -> None:
    await V14_MEMORY.loop()


async def v14_disk_guard_loop() -> None:
    await V14_DISK.loop()


async def v14_load_shedder_loop() -> None:
    await V14_LOAD_SHEDDER.loop()


async def v14_heartbeat_loop() -> None:
    await V14_HEARTBEAT.loop()


async def v14_metrics_loop() -> None:
    """لوحة المقاييس الدورية في الترمينال — كل 90 ثانية كتلة مرتبة."""
    await _v14_asyncio.sleep(45.0)
    while True:
        try:
            try:
                report = V14_METRICS.format_report(
                    f"V14 METRICS — host={globals().get('QX_HOST', '?')} "
                    f"assets={len(globals().get('ALL_STREAMING_ASSETS') or [])} "
                    f"opened={len(V14_OPENED)} pressure={V14_LOAD_SHEDDER.state}")
                logmsg(report)
            except Exception:
                pass
            await _v14_asyncio.sleep(90.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=2.0, cap=15.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 8 — V14 RESILIENCE (إعادة تشغيل البث بعد العودة + مراقب جلسة)
# ════════════════════════════════════════════════════════════════════════════
# منقول من pyquotex/ws/client.py:
#   _replay_subscriptions(): بعد كل إعادة اتصال ناجحة (open_count > 1)
#   انتظر حتى CONNECTED (حتى 40 × 0.05s) ثم أعد إصدار كل اشتراك متتبع.
#
# الخادم الأساسي auto_reconnect يعيد الاتصال نفسه — لكنه (بحسب توقيت انقطاع)
# يعيد تشغيل البث للأصول المتدفقة فقط، ويعيد الجلب الكامل فقط للانقطاع
# الطويل. v14 يضيف طبقة ضمان مستقلة: مراقب انتقال CONNECTION_ALIVE
# False→True يعيد تشغيل بث كل أصل متدفق له ماتت مهمته (بنفس نمط
# auto_reconnect حرفياً: إلغاء المهمة القديمة ثم run_coroutine_threadsafe
# لـ realtime_stream / subsecond_stream) — بلا أي مسار اتصال جديد.
# ════════════════════════════════════════════════════════════════════════════

class V14SessionStateMachine:
    """آلة حالات الجلسة — BOOT→CONNECTING→CONNECTED→DEGRADED→
    RECONNECTING→CONNECTED ... توثق كل انتقال بمدته في السجل والمقاييس.

    لا تتحكم في الاتصال — تراقب وتوثق فقط (المسار الرسمي أصحاب القرار).
    """

    BOOT = "BOOT"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"          # اتصال حي لكن بلا تيكات/صمت طويل
    RECONNECTING = "RECONNECTING"  # الكود الأساسي يعيد الاتصال الآن

    def __init__(self) -> None:
        self.state = self.BOOT
        self.entered_at = time.time()
        self.transitions = 0
        self.drops = 0
        self.longest_connected_s = 0.0
        self.last_connected_at = 0.0
        self.total_connected_s = 0.0
        self._lock = _v14_threading.Lock()

    def _enter(self, state: str, note: str = "") -> None:
        now = time.time()
        with self._lock:
            prev = self.state
            dur = now - self.entered_at
            self.state = state
            self.entered_at = now
            self.transitions += 1
            if prev == self.CONNECTED:
                self.total_connected_s += dur
                self.longest_connected_s = max(self.longest_connected_s, dur)
        if state == self.CONNECTED:
            self.last_connected_at = now
        if state == self.RECONNECTING:
            self.drops += 1
        V14_JOURNAL.record("session_state", old=prev, new=state,
                           prev_duration_s=round(dur, 1), note=note[:120])
        V14_METRICS.inc("v14.session.transitions")
        try:
            logmsg(f"[v14-session] {prev} -> {state} "
                   f"(prev lasted {dur:.0f}s)")
        except Exception:
            pass

    def observe(self) -> None:
        """قراءة الواقع الحالي وتحديث الحالة وفقها — بلا أي تدخل."""
        alive = bool(globals().get("CONNECTION_ALIVE"))
        client = globals().get("CLIENT")
        has_client = client is not None and getattr(client, "api", None) is not None
        with self._lock:
            state = self.state
        if alive and has_client:
            if state in (self.BOOT, self.RECONNECTING, self.DEGRADED):
                self._enter(self.CONNECTED)
        elif alive and not has_client:
            if state == self.CONNECTED:
                self._enter(self.DEGRADED, "alive but client lost")
        elif not alive:
            if state in (self.CONNECTED, self.DEGRADED):
                self._enter(self.RECONNECTING, "connection lost")

    def info(self) -> dict:
        with self._lock:
            cur_dur = time.time() - self.entered_at
            return {
                "state": self.state,
                "state_age_s": round(cur_dur, 1),
                "transitions": self.transitions,
                "drops": self.drops,
                "longest_connected_s": round(self.longest_connected_s, 1),
                "total_connected_s": round(self.total_connected_s, 1),
            }


V14_SESSION = V14SessionStateMachine()


class V14SubscriptionReplay:
    """إعادة تشغيل البث بعد العودة — نمط pyquotex _replay_subscriptions.

    يعمل مع مراقب الجلسة: عند انتقال RECONNECTING→CONNECTED بعد انقطاع
    يُعاد تشغيل بث كل أصل متدفق مهمته ماتة — بنفس نمط auto_reconnect
    (إلغاء + run_coroutine_threadsafe + إيقاع 0.05s). المهمة الحية
    لا تُلمس (لا ازدواجية بث).
    """

    def __init__(self) -> None:
        self.replays = 0
        self.restarted_assets = 0
        self._last_replay_at = 0.0

    async def replay_all(self) -> int:
        """يعيد تشغيل البث لكل أصل متدفق مهمته ماتة — يعيد عدد المعادين."""
        loop = _v14_asyncio.get_running_loop()
        # انتظار جاهزية الاتصال — نمط pyquotex (حتى 40 × 0.05s = 2s)
        for _ in range(40):
            client = globals().get("CLIENT")
            if client is not None and getattr(client, "api", None) is not None \
                    and globals().get("CONNECTION_ALIVE"):
                break
            await _v14_asyncio.sleep(0.05)
        client = globals().get("CLIENT")
        if client is None or getattr(client, "api", None) is None:
            return 0
        restarted = 0
        for asset in list(globals().get("ALL_STREAMING_ASSETS") or []):
            try:
                task = getattr(asset, "stream_task", None)
                alive = False
                try:
                    alive = task is not None and not task.done()
                except Exception:
                    alive = False
                if alive and getattr(asset, "streaming", False):
                    continue   # حي — لا تلمس (بلا ازدواجية)
                try:
                    if task is not None and not task.done():
                        task.cancel()
                except Exception:
                    pass
                asset.streaming = False
                asset.stream_task = asyncio.run_coroutine_threadsafe(
                    subsecond_stream(asset) if globals().get("IS_SUBSECOND")
                    else realtime_stream(asset), loop)
                restarted += 1
                await _v14_asyncio.sleep(0.05)  # نفس إيقاع auto_reconnect
            except Exception as e:
                V14_JOURNAL.record("replay_asset_fail",
                                   asset=getattr(asset, "api_symbol", "?"),
                                   error=str(e)[:160])
        if restarted:
            self.replays += 1
            self.restarted_assets += restarted
            self._last_replay_at = time.time()
            V14_METRICS.inc("v14.resilience.replays")
            V14_METRICS.inc("v14.resilience.restarted_assets", restarted)
            V14_JOURNAL.record("subscription_replay", restarted=restarted)
            try:
                logmsg(f"[v14-resilience] subscription replay: restarted "
                       f"{restarted} dead stream(s) after reconnect")
            except Exception:
                pass
        return restarted

    async def loop(self) -> None:
        """المراقب الدوري: يلاحظ انتقالات الجلسة ويشغل الإعادة عند العودة."""
        await _v14_asyncio.sleep(10.0)
        prev_state = None
        while True:
            try:
                await _v14_asyncio.sleep(2.0)
                V14_SESSION.observe()
                state = V14_SESSION.state
                if prev_state is not None and \
                        prev_state == V14SessionStateMachine.RECONNECTING and \
                        state == V14SessionStateMachine.CONNECTED:
                    # العودة من انقطاع — أعد الاشتراكات (نمط pyquotex)
                    await self.replay_all()
                    # أيضاً: سد ثغرات سريع لكل المفتوحات بعد الانقطاع
                    for sym in V14_OPENED.opened():
                        asyncio.ensure_future(
                            v14_gap_fill_for_asset(sym, reason="reconnect"))
                        await _v14_asyncio.sleep(0.05)
                prev_state = state
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                V14_JOURNAL.record("replay_watcher_error", error=str(e)[:200])
                await v14_backoff_sleep(1, base=1.0, cap=15.0)


V14_REPLAY = V14SubscriptionReplay()


async def v14_replay_watcher_loop() -> None:
    await V14_REPLAY.loop()


async def v14_session_watcher_loop() -> None:
    """مراقب الجلسة — يحدّث آلة الحالات كل ثانيتين."""
    await _v14_asyncio.sleep(5.0)
    while True:
        try:
            V14_SESSION.observe()
            info = V14_SESSION.info()
            V14_METRICS.gauge("v14.session.drops", info["drops"])
            await _v14_asyncio.sleep(2.0)
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            await v14_backoff_sleep(1, base=1.0, cap=15.0)


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 9 — V14 API + التركيب على المسارات الرسمية + بناء الحلقات المشرفة
# ════════════════════════════════════════════════════════════════════════════
# التركيب (hooking) قاعدة الذهبي فيه: كل غلاف يستدعي الأصل الكامل أولاً
# ثم يضيف سلوك v14 — المسارات الرسمية لم تُمَس حرفياً.
# ════════════════════════════════════════════════════════════════════════════

def _v14_wrap_cache_tick() -> None:
    """غلاف _cache_tick: يخزن بالطريقة الرسمية ثم يوقظ مضخة التيكات.
    «التكس لا ينام» — نقطة الالتقاط هذه هي الحدث الذي يوقظ المضخة فوراً."""
    global _cache_tick
    if bool(globals().get("_V14_CACHE_TICK_WRAPPED", False)):
        return
    orig = globals().get("_cache_tick")
    if orig is None:
        return

    def _wrapped(api_symbol, ts, price):
        try:
            orig(api_symbol, ts, price)       # الطريقة الرسمية كما هي
        except Exception:
            pass
        try:
            V14_TICKS.ingest_tick(api_symbol, ts, price)   # الإيقاظ الفوري
        except Exception:
            pass
    globals()["_cache_tick"] = _wrapped
    globals()["_V14_CACHE_TICK_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="_cache_tick")


def _v14_wrap_ensure_asset_loaded() -> None:
    """غلاف ensure_asset_loaded: ينادي الأصل كاملاً ثم يسجل الفتح ويجدول
    سد ثغرات فوري — «على كل عملة تم فتحها»."""
    global ensure_asset_loaded
    if bool(globals().get("_V14_ENSURE_WRAPPED", False)):
        return
    orig = globals().get("ensure_asset_loaded")
    if orig is None:
        return

    async def _wrapped(api_symbol):
        n = await orig(api_symbol)               # الأصل الكامل كما هو
        try:
            if n:
                v14_note_asset_opened(api_symbol, "ensure_asset_loaded")
        except Exception:
            pass
        return n

    globals()["ensure_asset_loaded"] = _wrapped
    globals()["_V14_ENSURE_WRAPPED"] = True
    # حدّث واجهة الخادم للفتح المبطن (التطبيق يقرأها من PAGINATION_API)
    try:
        pag = globals().get("PAGINATION_API")
        if isinstance(pag, dict):
            pag["ensure_asset_loaded"] = _wrapped
    except Exception:
        pass
    V14_JOURNAL.record("hook_installed", hook="ensure_asset_loaded")


def _v14_wrap_fetch_older_batch() -> None:
    """غلاف fetch_older_batch: الأصل كاملاً ثم تسجيل الفتح + سد فوري —
    التمرير للخلف كجزء من تغطية «كل عملة مفتوحة»."""
    global fetch_older_batch
    if bool(globals().get("_V14_OLDER_WRAPPED", False)):
        return
    orig = globals().get("fetch_older_batch")
    if orig is None:
        return

    async def _wrapped(api_symbol, *args, **kwargs):
        n = await orig(api_symbol, *args, **kwargs)   # الأصل الكامل
        try:
            v14_note_asset_opened(api_symbol, "fetch_older_batch")
        except Exception:
            pass
        return n

    globals()["fetch_older_batch"] = _wrapped
    globals()["_V14_OLDER_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="fetch_older_batch")


def _v14_wrap_preload_one_asset() -> None:
    """غلاف preload_one_asset: الأصل كاملاً ثم تسجيل الفتح — يغطي أيضاً
    عملة فتح الشارت الافتراضية (opener) عند جلبها الأولى."""
    global preload_one_asset
    if bool(globals().get("_V14_PRELOAD_WRAPPED", False)):
        return
    orig = globals().get("preload_one_asset")
    if orig is None:
        return

    async def _wrapped(api_symbol, *args, **kwargs):
        t0 = time.monotonic()
        n = await orig(api_symbol, *args, **kwargs)   # الأصل الكامل
        try:
            dt = time.monotonic() - t0
            V14_METRICS.observe("v14.preload.exec_s", dt)
            if n:
                v14_note_asset_opened(api_symbol, "preload_one_asset")
        except Exception:
            pass
        return n

    globals()["preload_one_asset"] = _wrapped
    globals()["_V14_PRELOAD_WRAPPED"] = True
    V14_JOURNAL.record("hook_installed", hook="preload_one_asset")


def install_v14_hooks() -> None:
    """يستبق تثبيت كل الأغلفة مرتين — idempotent."""
    global _V14_HOOKS_INSTALLED
    if globals().get("_V14_HOOKS_INSTALLED"):
        return
    _v14_wrap_cache_tick()
    _v14_wrap_ensure_asset_loaded()
    _v14_wrap_fetch_older_batch()
    _v14_wrap_preload_one_asset()
    install_v14_exception_hooks()
    globals()["_V14_HOOKS_INSTALLED"] = True
    V14_JOURNAL.record("v14_hooks_installed")


# ─── واجهة v14 العامة للتطبيق والمشغل ───

V14_API = {
    "version": _V14_VERSION,
    # جلب بأولوية عبر بوابة التفرز (نفس الرد الخام الرسمي):
    "fetch": v14_fetch,
    "fetch_with_priority": v14_fetch,
    "gate_stats": v14_gate_snapshot,
    # سد الثغرات الأصلي لعملة محددة (بلا تغيير طريقة):
    "gap_fill_for_asset": v14_gap_fill_for_asset,
    "note_asset_opened": v14_note_asset_opened,
    "opened_registry": lambda: V14_OPENED.snapshot(),
    # التيكات: لا تنام — اشتراك + قراءة فورية:
    "ticks": V14_TICKS,
    "subscribe_ticks": V14_TICKS.subscribe,
    "unsubscribe_ticks": V14_TICKS.unsubscribe,
    "recent_ticks": V14_TICKS.recent_ticks,
    "ticks_snapshot": V14_TICKS.snapshot,
    # النقاط والجلسة والمقاييس:
    "endpoints": lambda: V14_ENDPOINTS.info(),
    "session": lambda: V14_SESSION.info(),
    "metrics": lambda: V14_METRICS.snapshot(),
    "metrics_report": V14_METRICS.format_report,
    "supervisor_status": lambda: V14_SUPERVISOR.status(),
    "journal_tail": V14_JOURNAL.tail,
    "journal_info": V14_JOURNAL.info,
    "heartbeat_path": lambda: V14_HEARTBEAT.path,
    "heartbeat_payload": V14_HEARTBEAT.payload,
    "pressure_state": lambda: V14_LOAD_SHEDDER.state,
    "pause_preload_flag": V14_PAUSE_PRELOAD,
    # السياسات (منقولة من pyquotex):
    "policy": V14_POLICY,
    "backoff_delay": v14_backoff_delay,
    "slots": V14_SLOTS,
}


def v14_build_background_loops() -> _v14_List[Tuple[str, Callable[[], _v14_Awaitable]]]:
    """يبني قائمة كل حلقات v14 الخلفية المشرفة — تستدعى مرة واحدة عند
    التشغيل (من __main__ في وضع الترمينال، ومن التطبيق بعد الدخول).

    كل عنصر (اسم، مُصنع coroutine) — المشرف يستدعي المصنع عند كل إعادة
    تشغيل فتكون الحلقة جديدة نظيفة كل مرة (نمط pyquotex run_forever).
    التركيب (hooks) يثبت هنا أيضاً قبل تشغيل أي شيء.
    """
    install_v14_hooks()

    async def _gate_worker():
        await V14_GATE.worker()

    async def _tick_pump():
        await V14_TICKS.pump_loop()

    async def _tick_sampler():
        await V14_TICKS.sampler_loop()

    async def _tick_silence():
        await V14_TICKS.silence_watchdog()

    async def _gap_guard():
        await v14_gap_guard_loop()

    async def _gap_audit():
        await V14_GAP_AUDITOR.loop()

    async def _endpoint_probe():
        await v14_endpoint_probe_loop()

    async def _replay_watcher():
        await v14_replay_watcher_loop()

    async def _session_watcher():
        await v14_session_watcher_loop()

    async def _harvester():
        await v14_harvester_loop()

    async def _memory_guard():
        await v14_memory_guard_loop()

    async def _disk_guard():
        await v14_disk_guard_loop()

    async def _load_shedder():
        await v14_load_shedder_loop()

    async def _heartbeat():
        await v14_heartbeat_loop()

    async def _metrics():
        await v14_metrics_loop()

    async def _selftest():
        await v14_selftest_loop()

    return [
        ("gate_worker", _gate_worker),           # تفرز الطلبات
        ("tick_pump", _tick_pump),               # التكس لا ينام
        ("tick_sampler", _tick_sampler),
        ("tick_silence", _tick_silence),
        ("gap_guard", _gap_guard),               # سد الثغرات لكل مفتوح
        ("gap_audit", _gap_audit),               # ولا يتم فقدان
        ("endpoint_probe", _endpoint_probe),     # تقوي نقاط الخوادم
        ("replay_watcher", _replay_watcher),     # دون انهيار
        ("session_watcher", _session_watcher),
        ("harvester", _harvester),
        ("memory_guard", _memory_guard),
        ("disk_guard", _disk_guard),
        ("load_shedder", _load_shedder),
        ("heartbeat", _heartbeat),
        ("metrics", _metrics),
        ("selftest", _selftest),                 # تشخيص ذاتي دوري
    ]


def v14_print_banner() -> None:
    """يطبع بانر طبقة التقوية — يُستدعى من __main__ بعد نجاح الدخول."""
    try:
        print()
        print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
        print(f"{Colors.BOLD}  V14 STRENGTHENING LAYER ACTIVE "
              f"(طبقة تقوية الخادم){Colors.RESET}")
        modules = [
            "تفرز الطلبات: بوابة أولوية (OPENING > GAP_FILL > SCROLL > PRELOAD)",
            "سد الثغرات الأصلي يُنفَّذ على كل عملة تم فتحها — ولا فقدان",
            "التكس لا ينام: مضخة مُيقَظة بالأحداث + كاشف فقدان التيكات",
            "تقوي نقاط الخوادم: مسابر RTT + قاطع دائرة + تقرير نطاقات",
            "دون انهيار: مشرف كل حلقة + خطافات استثناء + حارس ذاكرة/قرص",
            "إعادة تشغيل البث بعد كل عودة (نمط pyquotex subscription replay)",
            "نبضة حياة qx_server_heartbeat.json كل 10 ثوانٍ",
        ]
        for i, m in enumerate(modules, 1):
            print(f"  {Colors.DIM}{i}) {m}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 64}{Colors.RESET}")
    except Exception:
        pass


def v14_line_inventory() -> dict:
    """جرد أسطر الخادم — إثبات وصول الكود للعدد المطلوب (طلب المستخدم:
    «الكود يجب ان يصل الى 15الف سطر على الاقل» مع التطبيق)."""
    try:
        src_file = globals().get("__file__", "")
        total = 0
        if src_file and _v14_os.path.exists(src_file):
            with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
                total = sum(1 for _ in f)
        return {
            "server_lines": total,
            "v14_layer_marker": "# v14 الجزء C — الوحدات 7 و 8 و 9",
        }
    except Exception:
        return {"server_lines": 0, "v14_layer_marker": ""}
