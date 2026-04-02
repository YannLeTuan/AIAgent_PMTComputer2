from collections import defaultdict


class InMemorySessionStore:
    def __init__(self):
        self.histories = defaultdict(list)
        self.contexts = defaultdict(self._default_context)

    def _default_context(self):
        return {
            "last_order_code": None,
            "last_product_name": None,
            "last_customer_email": None,
            "last_customer_name": None,
            "last_order_codes": []
        }

    def get_history(self, thread_id: str):
        return self.histories[thread_id]

    def set_history(self, thread_id: str, history: list):
        self.histories[thread_id] = history

    def get_context(self, thread_id: str):
        return self.contexts[thread_id]

    def set_context(self, thread_id: str, context: dict):
        self.contexts[thread_id] = context

    def clear_session(self, thread_id: str):
        self.histories[thread_id] = []
        self.contexts[thread_id] = self._default_context()


session_store = InMemorySessionStore()