# (generated with --quick)

from typing import Any

_unused_module_Queue: module
collections: module
queue: Any
six: module

class LifoQueue(Any):
    queue: collections.deque
    def _get(self) -> Any: ...
    def _init(self, _) -> None: ...
    def _put(self, item) -> None: ...
    def _qsize(self, len = ...) -> Any: ...
