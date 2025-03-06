from __future__ import annotations

from functools import wraps


def visit_after(fn):
    @wraps(fn)
    def wrapper(self, name: str, node):
        fn(self, name, node)
        if not node.is_leaf:
            self.visit(node)

    return wrapper


class EventMixin:
    def __init__(self):
        self._context = []

    def _emit(self, event: str):
        _, value = self._context[-1]
        for i in range(len(self._context)):
            name = "_".join([x[0] for x in self._context[i:]])
            handler = f"handle_{name}_{event}"
            if hasattr(self, handler):
                getattr(self, handler)(value)

    def em(self, scope, value):
        self._context.append((scope, value))
        self._emit("start")
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._emit("end")
        self._context.pop()
