# (generated with --quick)

from typing import Any, Callable, Coroutine, Dict, List, Sequence, TypeVar

asyncio: module
typing: module

T = TypeVar('T')

class BackgroundTask:
    args: tuple
    func: Callable
    is_async: bool
    kwargs: Dict[str, Any]
    def __call__(self) -> Coroutine[Any, Any, None]: ...
    def __init__(self, func: Callable, *args, **kwargs) -> None: ...

class BackgroundTasks(BackgroundTask):
    tasks: List[BackgroundTask]
    def __call__(self) -> Coroutine[Any, Any, None]: ...
    def __init__(self, tasks: Sequence[BackgroundTask] = ...) -> None: ...
    def add_task(self, func: Callable, *args, **kwargs) -> None: ...

def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> coroutine: ...
