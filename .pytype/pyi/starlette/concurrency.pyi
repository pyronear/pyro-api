# (generated with --quick)

from typing import Any, Callable, Coroutine, Iterator, Optional, Tuple, TypeVar

asyncio: module
contextvars: Optional[module]
functools: module
typing: module

T = TypeVar('T')

class _StopIteration(Exception): ...

def _next(iterator: Iterator) -> Any: ...
def iterate_in_threadpool(iterator: Iterator) -> asyncgenerator: ...
def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> coroutine: ...
def run_until_first_complete(*args: Tuple[Callable, dict]) -> Coroutine[Any, Any, None]: ...
