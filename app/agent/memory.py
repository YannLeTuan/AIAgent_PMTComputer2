import threading
import time

SESSION_TTL_SECONDS = 1800  # 30 min
CLEANUP_INTERVAL = 60       # cleanup check interval

DEFAULT_CONTEXT: dict = {
    "last_order_code": None,
    "last_product_name": None,
    "last_customer_email": None,
    "last_customer_name": None,
    "last_order_codes": [],
    "context_summary": ""
}


class InMemorySessionStore:
    def __init__(self, ttl: int = SESSION_TTL_SECONDS):
        self.histories: dict[str, list] = {}
        self.contexts: dict[str, dict] = {}
        self.last_access: dict[str, float] = {}
        self.ttl = ttl
        self._last_cleanup = time.time()
        self._lock = threading.Lock()

    def _default_context(self):
        return DEFAULT_CONTEXT.copy()

    def _touch(self, thread_id: str):
        # Must be called with self._lock held
        self.last_access[thread_id] = time.time()
        self._maybe_cleanup()

    def _maybe_cleanup(self):
        # Must be called with self._lock held
        now = time.time()
        if now - self._last_cleanup < CLEANUP_INTERVAL:
            return
        self._last_cleanup = now
        expired = [
            tid for tid, ts in list(self.last_access.items())
            if now - ts > self.ttl
        ]
        for tid in expired:
            self.histories.pop(tid, None)
            self.contexts.pop(tid, None)
            self.last_access.pop(tid, None)

    def get_history(self, thread_id: str) -> list:
        with self._lock:
            self._touch(thread_id)
            return self.histories.get(thread_id, [])

    def set_history(self, thread_id: str, history: list):
        with self._lock:
            self._touch(thread_id)
            self.histories[thread_id] = history

    def get_context(self, thread_id: str) -> dict:
        with self._lock:
            self._touch(thread_id)
            return self.contexts.get(thread_id, self._default_context())

    def set_context(self, thread_id: str, context: dict):
        with self._lock:
            self._touch(thread_id)
            self.contexts[thread_id] = context

    def clear_session(self, thread_id: str):
        with self._lock:
            self.histories.pop(thread_id, None)
            self.contexts.pop(thread_id, None)
            self.last_access.pop(thread_id, None)

    def active_session_count(self) -> int:
        with self._lock:
            return len(self.last_access)


session_store = InMemorySessionStore()
