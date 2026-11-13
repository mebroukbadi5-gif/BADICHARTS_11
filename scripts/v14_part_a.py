# ════════════════════════════════════════════════════════════════════════════
# ═══════════════════ QX SERVER v14 — STRENGTHENING LAYER (طبقة التقوية) ═════
# ════════════════════════════════════════════════════════════════════════════
#
# v14.0 (طلب المستخدم الحرفي):
#
#   «من المفترض السرفر والتطبيق يصلو الى 15الف سطر لو دمجا بشكل صحيح وليس
#    11الف سطر مزالت 4000 سطر تخص في تقويت السرفر وطريقة العمل دون انهيار
#    الخوادم»
#
#   «طريقة سد الثغرات لا تغيرها عن الكود لي اريتك يجب ان تنفذ على كل عملة
#    تم فتحها ولا يتم فقدان»
#
#   «ولا تيكس النوم ايضا لا يجب ان ينام مثل الكود لي اريتك»
#
#   «ابحث في المكتبة لي ارسلت لك سابقا في غيت هاب كيف تقوي نقاط الخوادم
#    وتفرز الطلبات»
#
#   «الكود يجب ان يصل الى 15الف سطر على الاقل»
#
# ────────────────────────────────────────────────────────────────────────────
# إجابة كل بند أعلاه موجودة في هذه الطبقة — والقاعدة الذهبية:
#
#   1) تسجيل الدخول (connect_quotex) وطريقة جلب الشموع الأصلية
#      (CLIENT.get_candles → history/load) وطريقة سد الثغرات الأصلية
#      (MT4Writer.fill_gap_once + _fill_missing_slots + mt4_gap_filler)
#      لم تُمَس حرفياً — صفر تغيير على الكود الأساسي.
#      v14 يبني فوقها فقط.
#
#   2) الأنماط المستخدمة هنا مأخوذة من مكتبة pyquotex التي أرسلها المستخدم
#      على GitHub (pyquotex/ws/client.py، pyquotex/_api/_waits.py،
#      pyquotex/qxtypes.py — ReconnectPolicy) وهي:
#        • ReconnectPolicy: backoff أُسّي مع jitter + ساعة كسر الاتصال القديم
#          (stale watchdog) + إعادة تشغيل الاشتراكات بعد إعادة الاتصال.
#        • backoff_sleep:  delay = min(cap, base * 2**attempt) مع ±jitter.
#        • WaitableSlot / SlotRegistry: انتظار موجّه بالأحداث بدل النوم
#          (event-driven waits) — وهذا أساس «التكس لا ينام».
#        • send() الذي يسجّل الخطأ بدل الانهيار (log instead of crash).
#
# ────────────────────────────────────────────────────────────────────────────
# الوحدات التسع (الوحدات 1-3 في هذا الملف الجزء A، 4-6 في الجزء B، 7-9 في C):
#
#   1) V14 CORE POLICY      — سياسة إعادة الاتصال + backoff + WaitableSlot
#                             (منقول من pyquotex كما هو).
# ═══ (بقية الوحدات مفهرسة في الأسفل) ═══
#   2) V14 METRICS          — عدادات + نافذة متدحرجة + سجل جلسة JSONL.
#   3) V14 REQUEST GATE     — بوابة الطلبات ذات الأولوية «تفرز الطلبات»:
#                             طلب واحد في كل لحظة، سلسلة لكل عملة (لا اختلاط)،
#                             أعمار للطلبات ضد الجوع، مهل وفاة، dedupe.
#   4) V14 ENDPOINTS        — تقوي نقاط الخوادم: مسبح نقاط + قاطع دائرة
#                             (circuit breaker) + مسابر RTT + تقرير نطاقات.
#   5) V14 TICK ENGINE      — «التكس لا ينام»: مضخة تيكات مُيقَظة بالأحداث
#                             (لا sleep في مسار المعالجة) + ترقيم متسلسل
#                             وكاشف فقدان + توزيع على المشتركين.
#   6) V14 GAP GUARD        — طريقة سد الثغرات نفسها بلا تغيير لكن تُنفَّذ
#                             على كل عملة تم فتحها + مراجع فقدان دوري
#                             (لا يتم فقدان).
#   7) V14 SUPERVISOR       — دون انهيار الخوادم: مشرف على كل حلقة خلفية
#                             (إعادة تشغيل مع backoff) + خطاف استثناءات عام
#                             + حصاد المهام الميتة + حارس ذاكرة/قرص + تفريغ
#                             حمل + نبضة حياة heartbeat.
#   8) V14 RESILIENCE       — مراقب إعادة الاتصال + إعادة تشغيل البث لكل
#                             الأصول بعد العودة (subscription replay من
#                             pyquotex) + ساعة كسر الاتصال القديم.
#   9) V14 RATE LIMITER     — دلو رموز (token bucket) لكل صنف طلب + إيقاع
#                             مهزوز بين الطلبات — خوادم كوتكس لا تُتعب.
#
# كل الحلقات الجديدة تُشغَّل عبر المشرف (Supervisor) في وضع الترمينال (__main__)
# وفي وضع التطبيق (BadiChartsStudio_live يبدأها بعد الدخول بنفس الطريقة).
# ════════════════════════════════════════════════════════════════════════════

# ─── v14: استيرادات الطبقة (كلها مكتبة قياسية — لا تبعيات جديدة إطلاقاً) ───
import asyncio as _v14_asyncio
import collections as _v14_collections
import errno as _v14_errno
import gc as _v14_gc
import heapq as _v14_heapq
import inspect as _v14_inspect
import itertools as _v14_itertools
import json as _v14_json
import os as _v14_os
import random as _v14_random
import resource as _v14_resource  # noqa: F401  (غير متاح على ويندوز — مستخدم بحذر أدناه)
import shutil as _v14_shutil
import socket as _v14_socket
import statistics as _v14_statistics
import sys as _v14_sys
import threading as _v14_threading
import time as _v14_time
import traceback as _v14_traceback
from collections import deque as _v14_deque
from dataclasses import dataclass as _v14_dataclass
from dataclasses import field as _v14_field
from enum import IntEnum as _v14_IntEnum
from typing import Any as _v14_Any
from typing import Awaitable as _v14_Awaitable
from typing import Callable as _v14_Callable
from typing import Dict as _v14_Dict
from typing import List as _v14_List
from typing import Optional as _v14_Optional
from typing import Set as _v14_Set
from typing import Tuple as _v14_Tuple

_V14_VERSION = "14.0"
_V14_STARTED_AT = time.time()


def _v14_base_dir() -> str:
    """المجلد الأساس لملفات v14 (سجل الجلسة، النبضة، تقرير النقاط).

    القاعدة: بجانب ملف الخادم نفسه (__file__) — يعمل صحيحاً سواء شُغّل
    الخادم من الترمينال أو استورد من التطبيق؛ ولو تعذر تحديده: مجلد العمل.
    """
    try:
        base = _v14_os.path.dirname(
            _v14_os.path.abspath(globals().get("__file__") or ""))
        if base and _v14_os.path.isdir(base):
            return base
    except Exception:
        pass
    try:
        return _v14_os.getcwd()
    except Exception:
        return "."

try:
    # ملف قفل يمنع تثبيت خطافات v14 مرتين إذا وُردد الموديول مرتين
    _V14_HOOKS_INSTALLED = False
except Exception:
    pass


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 1 — V14 CORE POLICY (منقولة من مكتبة pyquotex المرسلة)
# ════════════════════════════════════════════════════════════════════════════
# المصدر: pyquotex/qxtypes.py (ReconnectPolicy) + pyquotex/_api/_waits.py
# (backoff_sleep / wait_until / WaitableSlot / SlotRegistry) — نفس الأنماط
# حرفياً مع تسمية v14 حتى لا تتصادم مع أي شيء في الكود الأساسي.
# ════════════════════════════════════════════════════════════════════════════

class V14ReconnectPolicy:
    """منقول من pyquotex (qxtypes.ReconnectPolicy).

    يضبط سلوك إعادة الاتصال التلقائي لكل مكونات v14:

    enabled:
        المفتاح الرئيسي. عند False تتصرف كل الحلقات بلا إعادة تشغيل.
    max_attempts:
        التوقف بعد هذا العدد من المحاولات الفاشلة المتتالية. 0 = محاولات
        لا نهائية (الموصى به لخادم يعمل شهوراً — كما يقول مستند pyquotex).
    base_delay / max_delay / jitter:
        معاملات الـ backoff الأُسّي. التأخير = base_delay * 2**attempt
        مقيّد بـ max_delay مع jitter نسبة ±jitter (0.1 = ±10%).
    stale_timeout:
        ثوانٍ بدون أي رسالة واردة قبل اعتبار الاتصال قديماً وإعادة تدويره.
        0 يعطل الساعة (الاعتماد على ping/pong فقط).
    """

    __slots__ = ("enabled", "max_attempts", "base_delay", "max_delay",
                 "jitter", "stale_timeout")

    def __init__(self,
                 enabled: bool = True,
                 max_attempts: int = 0,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 jitter: float = 0.1,
                 stale_timeout: float = 60.0) -> None:
        self.enabled = enabled
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.stale_timeout = stale_timeout

    def delay_for(self, attempt: int) -> float:
        """نفس صيغة pyquotex backoff_sleep: min(cap, base*2**attempt)*jitter."""
        return v14_backoff_delay(attempt, base=self.base_delay,
                                 cap=self.max_delay, jitter=self.jitter)

    def as_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "jitter": self.jitter,
            "stale_timeout": self.stale_timeout,
        }


# السياسة الافتراضية للخادم — قيم pyquotex نفسها (موصى بها للبوتات طويلة العمر)
V14_POLICY = V14ReconnectPolicy(
    enabled=True,
    max_attempts=0,        # لا استسلام أبداً — خادم يجب ألا ينهار
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.1,
    stale_timeout=60.0,
)

# سياسة أسرع للحلقات القصيرة (فحوصات/مراقبات) — إعادة أسرع وبلا استسلام
V14_POLICY_FAST = V14ReconnectPolicy(
    enabled=True,
    max_attempts=0,
    base_delay=0.5,
    max_delay=10.0,
    jitter=0.15,
    stale_timeout=30.0,
)


def v14_backoff_delay(attempt: int, *,
                      base: float = 1.0,
                      cap: float = 30.0,
                      jitter: float = 0.1) -> float:
    """منقول من pyquotex/_api/_waits.py::backoff_sleep (نسخة متزامنة).

    تأخير أُسّي مع jitter: delay = min(cap, base * 2**attempt) ثم يُضرب في
    (1 ± jitter). «attempt» يبدأ من صفر (0, 1, 2, ...).

    يستخدم في كل حلقات إعادة المحاولة في v14 حتى لا تضرب الخوادم العليا
    بإيقاع ثابت ميكانيكي (نمط pyquotex نفسه).
    """
    try:
        attempt = max(0, int(attempt))
    except Exception:
        attempt = 0
    delay = min(float(cap), float(base) * (2 ** attempt))
    if jitter and jitter > 0:
        delay = delay * (1.0 + _v14_random.uniform(-abs(jitter), abs(jitter)))
    return max(0.0, delay)


async def v14_backoff_sleep(attempt: int, *,
                            base: float = 1.0,
                            cap: float = 30.0,
                            jitter: float = 0.1) -> None:
    """منقول من pyquotex/_api/_waits.py::backoff_sleep — نسخة async كما هي."""
    await _v14_asyncio.sleep(
        v14_backoff_delay(attempt, base=base, cap=cap, jitter=jitter))


async def v14_wait_until(predicate: Callable[[], bool], *,
                         timeout: float = 10.0,
                         poll_interval: float = 0.05) -> None:
    """منقول من pyquotex/_api/_waits.py::wait_until.

    يفحص predicate() حتى يصبح صحيحاً أو يرفع asyncio.TimeoutError.
    يُستعمل فقط حين لا يمكن إشارة الحالة المطلوبة من معالج الرسائل.
    """
    async def _loop() -> None:
        while not predicate():
            await _v14_asyncio.sleep(poll_interval)

    await _v14_asyncio.wait_for(_loop(), timeout=timeout)


class WaitableSlot:
    """منقول من pyquotex/_api/_waits.py::WaitableSlot.

    خانة انتظار بمنتج/مستهلك:
      - المستهلك: await slot.wait(timeout)
      - المنتج (معالج الرسائل عادة): slot.set(value)
    هذا هو البديل الموجّه بالأحداث عن asyncio.sleep polling — وهو أساس
    مبدأ «التكس لا ينام»: يُعالَج التكس لحظة وصوله لا عند نوم مؤقت.

    تحسين v14: set() آمن من أي خيط (آمن التوليد عبر call_soon_threadsafe)
    لأن الخادم يخلط خيط UI (التطبيق) وحلقة asyncio.
    """

    __slots__ = ("_value", "_event", "_loop")

    def __init__(self, loop: Optional[Any] = None) -> None:
        self._value = None
        self._loop = loop
        try:
            self._event = _v14_asyncio.Event()
        except Exception:
            self._event = None

    def _bind_loop(self, loop) -> None:
        if self._loop is None and loop is not None:
            self._loop = loop
            try:
                self._event = _v14_asyncio.Event()
            except Exception:
                pass

    def set(self, value) -> None:
        """يخزن القيمة ويوقظ كل المنتظرين. يرفع ValueError لو القيمة None —
        استعمل clear() لتصفير الخانة (نفس عقد pyquotex)."""
        if value is None:
            raise ValueError("WaitableSlot.set() does not accept None; "
                             "use clear() to reset")
        self._value = value
        ev = self._event
        if ev is None:
            return
        try:
            loop = ev._loop  # noqa: SLF001 — الطريق الوحيد الآمن للتحقق
        except Exception:
            loop = self._loop
        current = None
        try:
            current = _v14_asyncio.get_running_loop()
        except Exception:
            current = None
        try:
            if loop is not None and current is not None and loop is not current:
                # مناداة من خيط آخر — أرسل التعيين إلى حلقة الحدث نفسها
                loop.call_soon_threadsafe(ev.set)
            else:
                ev.set()
        except Exception:
            try:
                ev.set()
            except Exception:
                pass

    def clear(self) -> None:
        self._value = None
        try:
            self._event.clear()
        except Exception:
            pass

    def is_set(self) -> bool:
        try:
            return self._event.is_set()
        except Exception:
            return False

    async def wait(self, timeout: float = 10.0):
        """يحجب حتى set() أو يرفع asyncio.TimeoutError عند انتهاء المهلة."""
        await _v14_asyncio.wait_for(self._event.wait(), timeout=timeout)
        return self._value


class SlotRegistry:
    """منقول من pyquotex/_api/_waits.py::SlotRegistry.

    حاوية خانات انتظار مسماة ومفتاحية تستعملها مكونات v14:
      - المسماة: أحداث لمرة واحدة (اتصال جاهز، إعادة اتصال اكتملت ...).
      - المفتاحية: تُنشأ عند الطلب لكل (asset) أو (request_id) وتحرر بعد
        قراءتها — نفس عقد pyquotex تماماً.
    """

    def __init__(self) -> None:
        # خانات مسماة (أحداث دورة حياة الخادم)
        self.connection_ready: WaitableSlot = WaitableSlot()
        self.reconnect_done: WaitableSlot = WaitableSlot()
        self.gate_drained: WaitableSlot = WaitableSlot()
        self.opener_ready: WaitableSlot = WaitableSlot()

        # خانات مفتاحية — لكل عملة
        self._window_ready: Dict[str, WaitableSlot] = {}
        self._gap_done: Dict[str, WaitableSlot] = {}
        self._stream_ready: Dict[str, WaitableSlot] = {}

    def window_ready(self, api_symbol: str) -> WaitableSlot:
        slot = self._window_ready.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._window_ready[api_symbol] = slot
        return slot

    def release_window_ready(self, api_symbol: str) -> None:
        self._window_ready.pop(api_symbol, None)

    def gap_done(self, api_symbol: str) -> WaitableSlot:
        slot = self._gap_done.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._gap_done[api_symbol] = slot
        return slot

    def release_gap_done(self, api_symbol: str) -> None:
        self._gap_done.pop(api_symbol, None)

    def stream_ready(self, api_symbol: str) -> WaitableSlot:
        slot = self._stream_ready.get(api_symbol)
        if slot is None:
            slot = WaitableSlot()
            self._stream_ready[api_symbol] = slot
        return slot

    def release_stream_ready(self, api_symbol: str) -> None:
        self._stream_ready.pop(api_symbol, None)

    def stats(self) -> dict:
        return {
            "named": 3,
            "window_ready": len(self._window_ready),
            "gap_done": len(self._gap_done),
            "stream_ready": len(self._stream_ready),
        }


# السجل العام — كل مكونات v14 تستعمله
V14_SLOTS = SlotRegistry()


class V14Retryer:
    """مُعيد محاولة عام بنمط pyquotex run_forever.

    من pyquotex/ws/client.py::run_forever:
      attempt = 0  # النجاح يصفّر العداد
      ...
      if self.policy.max_attempts and attempt >= self.policy.max_attempts:
          give up
      await backoff_sleep(attempt, ...)
      attempt += 1

    V14Retryer يلف أي دالة async بهذا النمط مع تصنيف الأخطاء:
      - أخطاء عابرة (شبكة/مهلة/كسر اتصال) → إعادة محاولة بالسياسة.
      - أخطاء قاتلة (رفض منطقي، بيانات سيئة) → فشل فوري بلا إعادة.

    لا يلمس أي مسار رسمي — الكود الأساسي كما هو؛ هذا المُعيد تستعمله
    مكونات v14 فقط.
    """

    TRANSIENT_MARKERS = (
        "timeout", "timed out", "connection", "disconnect", "reset",
        "closed", "broken", "socket", "network", "temporarily",
        "unavailable", "busy", "ssl", "websocket", "handshake", "eof",
    )
    FATAL_MARKERS = (
        "invalid", "unauthorized", "forbidden", "bad request", "wrong",
        "not found", "denied", "syntax", "keyerror", "valueerror",
    )

    def __init__(self, policy: Optional[V14ReconnectPolicy] = None,
                 label: str = "retryer") -> None:
        self.policy = policy or V14_POLICY
        self.label = label
        self.attempts = 0
        self.last_error = None
        self.last_error_at = 0.0

    @classmethod
    def is_transient(cls, exc: Exception) -> bool:
        """تصنيف الخطأ: عابر (يعاد) أم قاتل (يفشل فوراً)."""
        s = str(exc).lower()
        if any(m in s for m in cls.FATAL_MARKERS):
            return False
        if any(m in s for m in cls.TRANSIENT_MARKERS):
            return True
        # الأخطاء المجهولة تعتبر عابرة افتراضياً (خادم لا يستسلم)
        return True

    def reset(self) -> None:
        self.attempts = 0
        self.last_error = None

    async def run(self, fn: Callable[[], _v14_Awaitable], *,
                  give_up_after: Optional[float] = None):
        """يشغّل fn() حتى النجاح أو العتبات.

        give_up_after: مهلة كلية اختيارية بالثواني (منذ البداية) — لو انقضت
        قبل النجاح يرفع آخر خطأ. None = بلا مهلة كلية (السياسة تحكم).
        """
        t0 = time.monotonic()
        while True:
            try:
                result = await fn()
                # النجاح يصفّر العداد — نمط pyquotex run_forever حرفياً
                self.attempts = 0
                return result
            except _v14_asyncio.CancelledError:
                raise
            except Exception as e:
                self.last_error = e
                self.last_error_at = time.time()
                if not self.policy.enabled:
                    raise
                if not self.is_transient(e):
                    raise
                if (self.policy.max_attempts
                        and self.attempts >= self.policy.max_attempts):
                    raise
                if give_up_after is not None and \
                        (time.monotonic() - t0) >= give_up_after:
                    raise
                await v14_backoff_sleep(
                    self.attempts,
                    base=self.policy.base_delay,
                    cap=self.policy.max_delay,
                    jitter=self.policy.jitter,
                )
                self.attempts += 1


class V14SupervisedFlag:
    """علم مشترك آمن بين الخيوط تستعمله حلقات v14 للتنسيق (تفريغ حمل، إيقاف
    مؤقت، إشارات ضغط) — بديل آمن عن المتغيرات العالمية المجردة."""

    __slots__ = ("_event", "_value")

    def __init__(self, initial: bool = False) -> None:
        self._value = initial
        self._event = _v14_asyncio.Event()
        if initial:
            self._event.set()

    def set(self, value: bool = True) -> None:
        self._value = bool(value)
        try:
            if self._value:
                self._event.set()
            else:
                self._event.clear()
        except Exception:
            pass

    def get(self) -> bool:
        return self._value

    async def wait_off(self, timeout: Optional[float] = None) -> None:
        """ينتظر حتى يُسقط العلم (قيمة False)."""
        ev = self._event
        if ev is None:
            return
        if timeout is None:
            await ev.wait()
        else:
            try:
                await _v14_asyncio.wait_for(ev.wait(), timeout=timeout)
            except _v14_asyncio.TimeoutError:
                pass


# أعلام التنسيق العامة لطبقة v14
V14_PAUSE_PRELOAD = V14SupervisedFlag(False)   # تفريغ الحمل: أوقف الجلب الخلفي فقط
V14_SHED_PRESSURE = V14SupervisedFlag(False)   # حالة ضغط RED
V14_RECONNECT_HINT = V14SupervisedFlag(False)  # توصية قاطع الدائرة بإعادة اتصال


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 2 — V14 METRICS (عدادات + نافذة متدحرجة + سجل جلسة)
# ════════════════════════════════════════════════════════════════════════════
# لماذا؟ «دون انهيار الخوادم» يحتاج عيناً: لو انهارت حلقة أو تجمّدت البوابة
# أو فقدت تيكات — يجب أن يظهر في لوحة الترمينال وسجل الجلسة فوراً، لا أن
# نكتشفه من شارت فارغ عند المستخدم.
# ════════════════════════════════════════════════════════════════════════════

class V14RollingRate:
    """نافذة متدحرجة لحساب معدل (تيكات/ثانية، رسائل/ثانية ...) — deque
    بطوابع زمنية مع حذف الأقدم من رأس الصف. آمنة على حلقة واحدة + قفل خفيف."""

    __slots__ = ("_dq", "_window", "_lock")

    def __init__(self, window_seconds: float = 30.0,
                 maxlen: int = 20000) -> None:
        self._dq = _v14_deque(maxlen=maxlen)
        self._window = float(window_seconds)
        self._lock = _v14_threading.Lock()

    def mark(self, ts: Optional[float] = None) -> None:
        ts = time.monotonic() if ts is None else ts
        with self._lock:
            self._dq.append(ts)

    def rate(self, window: Optional[float] = None) -> float:
        w = self._window if window is None else float(window)
        cutoff = time.monotonic() - w
        with self._lock:
            while self._dq and self._dq[0] < cutoff:
                self._dq.popleft()
            return len(self._dq) / max(w, 1e-6)

    def count(self, window: Optional[float] = None) -> int:
        w = self._window if window is None else float(window)
        cutoff = time.monotonic() - w
        with self._lock:
            while self._dq and self._dq[0] < cutoff:
                self._dq.popleft()
            return len(self._dq)

    def __len__(self) -> int:
        with self._lock:
            return len(self._dq)


class V14Metrics:
    """سجل مقاييس مركزي لطبقة v14.

    أنواع القياس:
      - counters: عدادات تراكمية فقط تزيد (طلبات، تيكات، إعادة اتصال...)
      - gauges:   قياسات لحظية تُحدَّث (عمق البوابة، الذاكرة، الحالة...)
      - hists:    توزيع زمني مبسّط بقيم ملخصة (انتظار البوابة، تنفيذ الجلب)

    snapshot() يعيد قاموساً نظيفاً للتقارير و heartbeat.
    format_report() يطبع كتلة مرتبة في الترمينال.
    """

    def __init__(self) -> None:
        self._lock = _v14_threading.RLock()
        self._counters: _v14_Dict[str, float] = {}
        self._gauges: _v14_Dict[str, float] = {}
        self._hists: _v14_Dict[str, _v14_List[float]] = {}
        self.started_at = time.time()

    # ---------- العدادات ----------
    def inc(self, name: str, amount: float = 1.0) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0.0) + amount

    def counter(self, name: str) -> float:
        with self._lock:
            return self._counters.get(name, 0.0)

    # ---------- القياسات اللحظية ----------
    def gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = float(value)

    def get_gauge(self, name: str) -> float:
        with self._lock:
            return self._gauges.get(name, 0.0)

    # ---------- التوزيعات ----------
    def observe(self, name: str, value: float, keep: int = 512) -> None:
        with self._lock:
            h = self._hists.get(name)
            if h is None:
                h = []
                self._hists[name] = h
            h.append(float(value))
            if len(h) > keep:
                del h[: len(h) - keep]

    def hist_summary(self, name: str) -> Optional[dict]:
        with self._lock:
            h = self._hists.get(name)
            if not h:
                return None
            vals = sorted(h)
            n = len(vals)
            return {
                "n": n,
                "avg": sum(vals) / n,
                "p50": vals[n // 2],
                "p90": vals[min(n - 1, int(n * 0.9))],
                "p99": vals[min(n - 1, int(n * 0.99))],
                "max": vals[-1],
            }

    # ---------- لقطة كاملة ----------
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptime_s": round(time.time() - self.started_at, 1),
                "counters": dict(self._counters),
                "gauges": {k: round(v, 3) for k, v in self._gauges.items()},
                "hists": {k: self._hist_summary_unlocked(v)
                          for k, v in self._hists.items() if v},
            }

    def _hist_summary_unlocked(self, vals: _v14_List[float]) -> Optional[dict]:
        if not vals:
            return None
        svals = sorted(vals)
        n = len(svals)
        return {
            "n": n,
            "avg": round(sum(svals) / n, 4),
            "p90": round(svals[min(n - 1, int(n * 0.9))], 4),
            "max": round(svals[-1], 4),
        }

    # ---------- تقرير الترمينال ----------
    def format_report(self, title: str = "V14 METRICS") -> str:
        snap = self.snapshot()
        lines = [
            f"{Colors.CYAN}┌─ {title} "
            f"(uptime {snap['uptime_s']:.0f}s){Colors.RESET}"
        ]
        counters = snap["counters"]
        if counters:
            lines.append(f"{Colors.BOLD}│ counters:{Colors.RESET}")
            width = max(len(k) for k in counters)
            for k in sorted(counters):
                lines.append(f"│   {k:<{width}}  {counters[k]:,.0f}")
        gauges = snap["gauges"]
        if gauges:
            lines.append(f"{Colors.BOLD}│ gauges:{Colors.RESET}")
            width = max(len(k) for k in gauges)
            for k in sorted(gauges):
                lines.append(f"│   {k:<{width}}  {gauges[k]}")
        hists = snap["hists"]
        if hists:
            lines.append(f"{Colors.BOLD}│ timings (avg/p90/max):{Colors.RESET}")
            width = max(len(k) for k in hists)
            for k in sorted(hists):
                h = hists[k]
                if h:
                    lines.append(
                        f"│   {k:<{width}}  {h['avg']:.3f} / "
                        f"{h['p90']:.3f} / {h['max']:.3f} (n={h['n']})")
        lines.append(f"{Colors.CYAN}└{'─' * 50}{Colors.RESET}")
        return "\n".join(lines)


# السجل العام للمقاييس
V14_METRICS = V14Metrics()


class V14SessionJournal:
    """سجل جلسة JSONL بحلقة (ring) — يوثّق أحداث دورة الحياة:
    اتصال، كسر، إعادة اتصال، سد ثغرات، إعادة تشغيل حلقة، ضغط، تفريغ حمل.

    سياسة القرص الصارمة (نفس فلسفة التيكات في v13):
      - حد أقصى للملف V14_JOURNAL_MAX_BYTES (افتراضي 2MB).
      - عند التجاوز: دوران لملف .old واحد فقط (لا ينمو بلا حدود أبداً).
      - لا يُكتب أي شيء عند فشل الكتابة بصمت تام — السجل لا يُسقط الخادم.
    """

    def __init__(self, path: str = "qx_server_v14_journal.jsonl",
                 max_bytes: int = 2 * 1024 * 1024) -> None:
        self.path = path
        self.max_bytes = int(max_bytes)
        self._lock = _v14_threading.Lock()
        self._seq = 0
        self._dropped = 0
        try:
            self.path = _v14_os.path.join(_v14_base_dir(),
                                          _v14_os.path.basename(path))
        except Exception:
            pass

    def record(self, event: str, **fields) -> None:
        """يكتب سطر JSONL واحداً — آمن من أي خيط، لا يرفع أبداً."""
        try:
            now = time.time()
            with self._lock:
                self._seq += 1
                rec = {
                    "t": round(now, 3),
                    "iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
                    "seq": self._seq,
                    "event": event,
                }
                if fields:
                    rec.update(fields)
                line = _v14_json.dumps(rec, ensure_ascii=False,
                                       separators=(",", ":")) + "\n"
                try:
                    if _v14_os.path.exists(self.path) and \
                            _v14_os.path.getsize(self.path) > self.max_bytes:
                        old = self.path + ".old"
                        try:
                            if _v14_os.path.exists(old):
                                _v14_os.remove(old)
                        except Exception:
                            pass
                        try:
                            _v14_os.replace(self.path, old)
                        except Exception:
                            pass
                    with open(self.path, "a", encoding="utf-8") as f:
                        f.write(line)
                except Exception:
                    self._dropped += 1
        except Exception:
            pass

    def tail(self, n: int = 30) -> _v14_List[dict]:
        """آخر n سجل — للتقارير والفحص اليدوي."""
        out: _v14_List[dict] = []
        try:
            with self._lock:
                if not _v14_os.path.exists(self.path):
                    return out
                with open(self.path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-int(n):]
                for ln in lines:
                    try:
                        out.append(_v14_json.loads(ln))
                    except Exception:
                        continue
        except Exception:
            pass
        return out

    def info(self) -> dict:
        size = 0
        try:
            size = _v14_os.path.getsize(self.path) \
                if _v14_os.path.exists(self.path) else 0
        except Exception:
            pass
        return {"path": self.path, "bytes": size,
                "seq": self._seq, "dropped": self._dropped}


# سجل الجلسة العام
V14_JOURNAL = V14SessionJournal()


# ════════════════════════════════════════════════════════════════════════════
# الوحدة 3 — V14 REQUEST GATE (بوابة الطلبات ذات الأولوية — «تفرز الطلبات»)
# ════════════════════════════════════════════════════════════════════════════
# هذا هو الحل الجذري لمشكلة المستخدم:
#   «اضنها بسبب تعليق والاختلاط بين عمليات الجلب يختلط بين اكمال كل تلك
#    العملات وجلب جلب عملة نريد رجوع للخلف يجب ان تجد حلا لمشكل السرفر»
#
# البوابة الأصلية في v13 (qx_fetch_window_raw) تضمن «طلب واحد في كل لحظة»
# لكن لا تفرز الأولويات ولا تمنع اختلاط سلاسل العمل الواحدة. v14 يبني فوقها:
#
#   1) طابور أولوية كومة (heapq): صنف قبل أخر — فتح شارت عملة (OPENING)
#      يسبق سد الثغرات (GAP_FILL) يسبق التمرير للخلف (SCROLL_BACK) يسبق
#      الخلفية (PRELOAD) يسبق الفحوصات (HEALTH/MAINTENANCE).
#   2) سلسلة لكل عملة (per-asset chain): طلبات العملة الواحدة تُنفَّذ
#      بترتيب وصولها واحد تلو الآخر — لا يختلط أبداً «إكمال العملات» مع
#      «جلب دفعة أقدم لنفس العملة».
#   3) أعمار ضد الجوع (aging): كل 10 ثوانٍ انتظار ترتفع أولوية الطلب مستوى
#      واحد (بلا تجاوز OPENING) — طلب الخلفية لا يموت جوعاً لو تأخر.
#   4) مهل وفاة (deadline): الطلب الذي تجاوز مهلته يفشل سريعاً بدل أن
#      يعلّق السلسلة كلها — لا «تعليق» بين عمليات الجلب.
#   5) dedupe: نفس النافذة (عملة/فريم/نهاية) أثناء تعليقها يعيد نفس
#      النتيجة بلا طلب مكرر يختلط مع السابق.
#   6) طلب واحد فعلي في كل لحظة على مستوى الخادم كله (عامل واحد).
#
# وطريقة الجلب نفسها كما هي حرفياً: العامل يستدعي qx_fetch_window_raw()
# (البوابة الرسمية التي تدعو CLIENT.get_candles → history/load) — صفر
# تغيير على طريقة الجلب الأصلية.
# ════════════════════════════════════════════════════════════════════════════

class RequestPriority(_v14_IntEnum):
    """أصناف الطلبات بترتيب الخدمة (الأقل رقم = يخدم أولاً)."""
    OPENING = 0        # عملة فُتح شارتها للتو — المستخدم ينتظر الشارت الآن
    GAP_FILL = 1       # سد ثغرات عملة مفتوحة (طريقة أصلية بلا تغيير)
    SCROLL_BACK = 2    # دفعة تمرير للخلف (300 شمعة أقدم)
    PRELOAD = 3        # جلب خلفي عادي
    HEALTH = 4         # فحوصات صحة/مسابر
    MAINTENANCE = 5    # صيانة دورية

    @classmethod
    def name_of(cls, value: int) -> str:
        try:
            return cls(int(value)).name
        except Exception:
            return "UNKNOWN"


# معدلات دلو الرموز لكل صنف (طلبات/ثانية) — تمنع إرهاق خوادم كوتكس العليا
V14_BUCKET_RATES: _v14_Dict[int, Tuple[float, float]] = {
    # priority: (rate/s, capacity)
    RequestPriority.OPENING: (3.0, 4.0),
    RequestPriority.GAP_FILL: (1.0, 2.0),
    RequestPriority.SCROLL_BACK: (1.2, 2.0),
    RequestPriority.PRELOAD: (0.8, 1.5),
    RequestPriority.HEALTH: (0.5, 1.0),
    RequestPriority.MAINTENANCE: (0.5, 1.0),
}

# أقل فاصل زمني بين طلبين متتاليين للخادم العليا (إيقاع مهزوز)
V14_PACER_MIN_INTERVAL = 0.05
V14_PACER_JITTER = 0.03

# عمر الانتظار الذي يرفع الأولوية مستوى (أعمار ضد الجوع)
V14_AGING_STEP_SECONDS = 10.0


class V14TokenBucket:
    """دلو رموز كلاسيكي — يحدّ معدل الطلبات لكل صنف.

    rate:    الرموز المضافة في الثانية.
    capacity: حجم الدلو (سماحية انفجار قصيرة).
    acquire(): ينتظر حتى يتوفر رمز — لا يكسر أبداً، فقط يُبطئ بلطف.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = float(rate)
        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = _v14_threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = max(0.0, now - self._last)
        self._tokens = min(self.capacity,
                           self._tokens + elapsed * self.rate)
        self._last = now

    def try_acquire(self) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    async def acquire(self, timeout: float = 30.0) -> None:
        """ينتظر رمزاً مع مهلة أمان — بعد المهلة يمرر إجبارياً (خادم لا يعلق)."""
        t0 = time.monotonic()
        while True:
            if self.try_acquire():
                return
            if (time.monotonic() - t0) >= timeout:
                # مهلة الدلو: نمرر (خادم لا يعلق بسبب دلو) — عدّاد فقط
                V14_METRICS.inc("v14.bucket.timeout_pass")
                return
            await _v14_asyncio.sleep(0.02)

    def state(self) -> dict:
        with self._lock:
            self._refill()
            return {"rate": self.rate, "capacity": self.capacity,
                    "tokens": round(self._tokens, 2)}


class V14UpstreamPacer:
    """إيقاع مهزوز بين الطلبات المتتالية للخادم العليا.

    v8.3 في الكود المرجعي علّمنا: «the server was throttling us after a few
    assets because we hammered it at 30 req/s». الطلبات بدون إيقاع تُتعب
    الخوادم العليا → throttling → فجوات وشومع مفقودة. الـ pacer يفرض فاصلاً
    أدنى مهزوزاً (0.05s ± 0.03) بين أي طلبين — الخوادم لا تُتعب.
    """

    def __init__(self, min_interval: float = V14_PACER_MIN_INTERVAL,
                 jitter: float = V14_PACER_JITTER) -> None:
        self.min_interval = float(min_interval)
        self.jitter = float(jitter)
        self._last = 0.0
        self._lock = _v14_threading.Lock()

    async def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait_for = self.min_interval - (now - self._last)
        if wait_for > 0:
            jittered = wait_for + _v14_random.uniform(0.0, max(0.0, self.jitter))
            if jittered > 0:
                await _v14_asyncio.sleep(jittered)
        with self._lock:
            self._last = time.monotonic()


@_v14_dataclass(order=True)
class V14FetchRequest:
    """طلب جلب واحد داخل بوابة v14.

    الترتيب الطبيعي للفئة (order=True) يستخدم فقط داخل الكومة بعد أن
    يحسب العامل effective_priority — لذلك sort_index يحمل الأولوية المؤقتة.
    """
    sort_index: int = 0                      # الأولوية الفعلية لحظة الخدمة
    seq: int = 0                             # تسلسل الوصول (كسر تعادل FIFO)
    api_symbol: str = ""
    end_time: int = 0
    seconds: int = 0
    period: int = 0
    priority: int = int(RequestPriority.PRELOAD)
    label: str = ""
    foreground: bool = False
    timeout: float = 25.0
    enqueued_at: float = _v14_field(default_factory=time.monotonic)
    deadline: float = 0.0                    # monotonic — 0 = بلا مهلة وفاة
    attempts: int = 0
    future: _v14_Any = None                  # asyncio.Future (حلقة واحدة)
    dedupe_key: tuple = ()

    def describe(self) -> str:
        return (f"#{self.seq} [{RequestPriority.name_of(self.priority)}] "
                f"{self.api_symbol} win={self.seconds}s "
                f"per={self.period}s label={self.label or '-'}")


class V14RequestGate:
    """بوابة الطلبات ذات الأولوية — قلب «تفرز الطلبات» في v14.

    خصائص الضمان:
      - عامل واحد (worker واحد): طلب واحد فعلي في كل لحظة.
      - سلسلة لكل عملة: طلبات نفس العملة متسلسلة بلا اختلاط.
      - أعمار ضد الجوع + مهل وفاة + dedupe + دلو رموز + إيقاع مهزوز.
      - لا ترفع أبداً خارج future الطلب — الخادم لا ينهار من طلب سيئ.

    العامل يستدعي qx_fetch_window_raw الرسمية — طريقة الجلب الأصلية
    لم تُمَس (نفس CLIENT.get_candles ونفس رسالة history/load).
    """

    def __init__(self) -> None:
        self._heap: _v14_List[_v14_List] = []       # [eff_priority, seq, req]
        self._counter = _v14_itertools.count(1)
        self._wake = _v14_asyncio.Event()
        self._worker_task: _v14_Any = None
        self._pending: _v14_Dict[tuple, _v14_Any] = {}   # dedupe key -> future
        self._asset_chains: _v14_Dict[str, _v14_asyncio.Lock] = {}
        self._buckets: _v14_Dict[int, V14TokenBucket] = {}
        for prio, (rate, cap) in V14_BUCKET_RATES.items():
            self._buckets[int(prio)] = V14TokenBucket(rate, cap)
        self._pacer = V14UpstreamPacer()
        self._running = False
        self._stats_lock = _v14_threading.Lock()
        self._submitted = 0
        self._deduped = 0
        self._expired = 0
        self._executed = 0
        self._failed = 0
        self._cancelled = 0
        # عائلات الانتظار المشتركة (نمط pyquotex SlotRegistry)
        self._done_slots = SlotRegistry()

    # ---------- سلاسل العملات ----------
    def _chain(self, api_symbol: str) -> _v14_asyncio.Lock:
        """قفل تسلسل لكل عملة — طلبات العملة الواحدة لا تتداخل أبداً."""
        lock = self._asset_chains.get(api_symbol)
        if lock is None:
            lock = _v14_asyncio.Lock()
            self._asset_chains[api_symbol] = lock
        return lock

    def _prune_chains(self) -> None:
        """تنظيف أقفال العملات غير المستعملة (منع نمو بلا حدود)."""
        if len(self._asset_chains) <= 512:
            return
        with self._stats_lock:
            locked = {s for s, lk in self._asset_chains.items() if lk.locked()}
        for sym in list(self._asset_chains.keys()):
            if sym not in locked:
                self._asset_chains.pop(sym, None)

    # ---------- الإرسال ----------
    def submit_nowait(self, api_symbol: str, end_time: int, seconds: int,
                      period: int, *,
                      priority: int = int(RequestPriority.PRELOAD),
                      label: str = "", foreground: bool = False,
                      timeout: float = 25.0,
                      wait_deadline: float = 90.0) -> _v14_Any:
        """يسجل الطلب في الطابور ويعيد Future فوراً (بلا انتظار).

        wait_deadline: مهلة انتظار داخل الطابور (ثوانٍ monotonic) — بعد
        رفضها يفشل الطلب سريعاً بدل تعليق السلسلة (مضاد «التعليق»).
        """
        loop = _v14_asyncio.get_running_loop()
        fut = loop.create_future()
        api_symbol = str(api_symbol or "").strip()
        key = (api_symbol, int(period), int(end_time), int(seconds))
        # dedupe: نفس الطلب معلّق بالفعل → نفس النتيجة (لا خلط)
        existing = self._pending.get(key)
        if existing is not None and not existing.done():
            self._deduped += 1
            V14_METRICS.inc("v14.gate.deduped")
            return existing
        req = V14FetchRequest(
            seq=next(self._counter),
            api_symbol=api_symbol,
            end_time=int(end_time),
            seconds=int(seconds),
            period=int(period),
            priority=int(priority),
            label=str(label or ""),
            foreground=bool(foreground),
            timeout=float(timeout),
            future=fut,
            dedupe_key=key,
            deadline=(time.monotonic() + wait_deadline) if wait_deadline else 0.0,
        )
        self._pending[key] = fut
        self._push(req)
        with self._stats_lock:
            self._submitted += 1
        V14_METRICS.inc("v14.gate.submitted")
        V14_METRICS.inc(f"v14.gate.submitted.{RequestPriority.name_of(req.priority)}")
        V14_JOURNAL.record("gate_submit", asset=api_symbol,
                           prio=req.priority, label=req.label,
                           seconds=req.seconds, seq=req.seq)
        self._wake.set()
        return fut

    async def submit(self, api_symbol: str, end_time: int, seconds: int,
                     period: int, *,
                     priority: int = int(RequestPriority.PRELOAD),
                     label: str = "", foreground: bool = False,
                     timeout: float = 25.0,
                     wait_deadline: float = 90.0):
        """يسجل ثم ينتظر النتيجة — يعيد الرد الخام كما تعيده البوابة الرسمية
        أو يرفع استثناء الطلب (المستدعي يعالجه كما يعالج رد البوابة الأصلية)."""
        fut = self.submit_nowait(api_symbol, end_time, seconds, period,
                                 priority=priority, label=label,
                                 foreground=foreground, timeout=timeout,
                                 wait_deadline=wait_deadline)
        return await fut

    def _push(self, req: V14FetchRequest) -> None:
        _v14_heapq.heappush(self._heap, [int(req.priority), req.seq, req])
        self._wake.set()

    def _next_request(self) -> _v14_Optional[V14FetchRequest]:
        """يسحب الطلب الأعلى أولوية مع تطبيق الأعمار وفحص المهل.

        الأعمار (aging): أولوية الطلب تتحسن مستوى كل AGING_STEP ثانية انتظار
        (بلا تجاوز OPENING) — ضد تجوع الطلبات الخلفية عند ضغط أمامي طويل.
        """
        now = time.monotonic()
        aged: _v14_List[_v14_List] = []
        chosen = None
        while self._heap:
            eff, seq, req = _v14_heapq.heappop(self._heap)
            if req.future is None or req.future.done():
                continue  # أُلغي أثناء الانتظار — تجاهل
            if req.deadline and now > req.deadline:
                # مهلة وفاة انقضت → فشل سريع (لا تعليق)
                self._expired += 1
                V14_METRICS.inc("v14.gate.expired")
                V14_JOURNAL.record("gate_expired", asset=req.api_symbol,
                                   label=req.label, waited_s=round(now - req.enqueued_at, 1))
                self._pop_pending(req)
                if not req.future.done():
                    req.future.set_exception(
                        TimeoutError(f"v14 gate: request expired after "
                                     f"{now - req.enqueued_at:.1f}s in queue "
                                     f"({req.describe()})"))
                continue
            # حساب الأولوية المؤقتة بالأعمار
            waited = now - req.enqueued_at
            aged_level = int(waited // V14_AGING_STEP_SECONDS)
            new_eff = max(int(RequestPriority.OPENING),
                          req.priority - aged_level)
            entry = [new_eff, seq, req]
            if chosen is None:
                chosen = entry
            else:
                aged.append(entry)
        if chosen is not None:
            aged.append(chosen)
        if aged:
            # أعِد الباقي للكومة بأولوياتهم المحدثة (الأعمار مكتوبة فعلياً)
            for entry in aged:
                if entry is not chosen:
                    _v14_heapq.heappush(self._heap, entry)
            if chosen is not None:
                return chosen[2]
        return None

    def _pop_pending(self, req: V14FetchRequest) -> None:
        try:
            if self._pending.get(req.dedupe_key) is req.future:
                self._pending.pop(req.dedupe_key, None)
        except Exception:
            pass

    # ---------- العامل ----------
    async def worker(self) -> None:
        """عامل البوابة — يعمل للأبد، طلب واحد فعلي في كل لحظة.

        كل خطأ يُسجل ويُحصَّد — العامل لا يموت أبداً (دون انهيار الخوادم).
        """
        self._running = True
        V14_JOURNAL.record("gate_worker_start")
        while True:
            try:
                req = self._next_request()
                if req is None:
                    self._wake.clear()
                    # انتظار موجّه بالأحداث — لا نوم دوري (نمط pyquotex)
                    await self._wake.wait()
                    continue
                await self._execute(req)
            except _v14_asyncio.CancelledError:
                self._running = False
                raise
            except Exception as e:
                # آخر خط دفاع: العامل لا يموت — سجّل واستمر
                V14_METRICS.inc("v14.gate.worker_errors")
                V14_JOURNAL.record("gate_worker_error", error=str(e)[:200])
                try:
                    logmsg(f"[v14-gate] worker caught: {e}")
                except Exception:
                    pass
                await v14_backoff_sleep(1, base=0.3, cap=2.0, jitter=0.2)

    async def _execute(self, req: V14FetchRequest) -> None:
        """ينفذ طلباً واحداً داخل سلسلة عملته — هنا يجتمع كل الضمانات."""
        t_wait = time.monotonic() - req.enqueued_at
        V14_METRICS.observe("v14.gate.wait_s", t_wait)
        try:
            bucket = self._buckets.get(req.priority) or \
                self._buckets[int(RequestPriority.PRELOAD)]
            await bucket.acquire()
            await self._pacer.wait()
        except _v14_asyncio.CancelledError:
            raise
        except Exception:
            pass  # الدلو/الإيقاع لا يمنعان التنفيذ أبداً — عدّادات فقط
        # سلسلة العملة: طلبات العملة الواحدة متسلسلة بلا اختلاط
        chain = self._chain(req.api_symbol)
        async with chain:
            if req.future.done():
                self._pop_pending(req)
                return
            t0 = time.monotonic()
            try:
                raw = await qx_fetch_window_raw(
                    req.api_symbol, req.end_time, req.seconds, req.period,
                    foreground=req.foreground, timeout=req.timeout)
                dt = time.monotonic() - t0
                V14_METRICS.observe("v14.gate.exec_s", dt)
                with self._stats_lock:
                    self._executed += 1
                V14_METRICS.inc("v14.gate.executed")
                V14_METRICS.inc(f"v14.gate.executed."
                                f"{RequestPriority.name_of(req.priority)}")
                V14_JOURNAL.record("gate_done", asset=req.api_symbol,
                                   label=req.label, exec_s=round(dt, 3),
                                   wait_s=round(t_wait, 3), seq=req.seq)
                if not req.future.done():
                    req.future.set_result(raw)
            except _v14_asyncio.CancelledError:
                with self._stats_lock:
                    self._cancelled += 1
                if not req.future.done():
                    req.future.cancel()
                raise
            except Exception as e:
                dt = time.monotonic() - t0
                with self._stats_lock:
                    self._failed += 1
                V14_METRICS.inc("v14.gate.failed")
                V14_METRICS.observe("v14.gate.fail_exec_s", dt)
                V14_JOURNAL.record("gate_fail", asset=req.api_symbol,
                                   label=req.label, error=str(e)[:200],
                                   exec_s=round(dt, 3))
                try:
                    logmsg(f"[v14-gate] request failed ({req.describe()}): {e}")
                except Exception:
                    pass
                if not req.future.done():
                    req.future.set_exception(e)
            finally:
                self._pop_pending(req)
                self._prune_chains()

    # ---------- إحصاءات ----------
    def depth(self) -> int:
        return len(self._heap)

    def depth_by_priority(self) -> dict:
        out: _v14_Dict[str, int] = {}
        for eff, seq, req in list(self._heap):
            name = RequestPriority.name_of(req.priority)
            out[name] = out.get(name, 0) + 1
        return out

    def stats(self) -> dict:
        with self._stats_lock:
            return {
                "submitted": self._submitted,
                "deduped": self._deduped,
                "executed": self._executed,
                "failed": self._failed,
                "expired": self._expired,
                "cancelled": self._cancelled,
                "depth": self.depth(),
                "depth_by_priority": self.depth_by_priority(),
                "buckets": {RequestPriority.name_of(p): b.state()
                            for p, b in self._buckets.items()},
            }

    @property
    def running(self) -> bool:
        return self._running


# البوابة العامة — تستعملها كل مكونات v14 (سد الثغرات، المدقق، المسابر)
V14_GATE = V14RequestGate()


async def v14_fetch(api_symbol: str, end_time: int, seconds: int, period: int, *,
                    priority: int = int(RequestPriority.PRELOAD),
                    label: str = "", timeout: float = 25.0,
                    wait_deadline: float = 90.0):
    """واجهة مريحة: جلب عبر بوابة الأولوية (نفس الرد الخام الرسمي)."""
    return await V14_GATE.submit(api_symbol, end_time, seconds, period,
                                 priority=priority, label=label,
                                 timeout=timeout,
                                 wait_deadline=wait_deadline)


def v14_fetch_foreground_pending() -> int:
    """عدد الطلبات الأمامية المعلقة في بوابة v14 (للتطبيق)."""
    return sum(1 for fut in V14_GATE._pending.values() if not fut.done())


def v14_gate_snapshot() -> dict:
    """لقطة حالة البوابة للـ heartbeat والتقارير."""
    st = V14_GATE.stats()
    st["worker_running"] = V14_GATE.running
    return st
