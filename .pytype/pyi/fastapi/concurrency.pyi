# (generated with --quick)

from typing import Any, Callable, Coroutine, Iterator, Tuple, TypeVar

AsyncExitStack: Any
asynccontextmanager: Any
asynccontextmanager_error_message: str
contextmanager_in_threadpool: Any

T = TypeVar('T')

def _fake_asynccontextmanager(func: Callable) -> Callable: ...
def iterate_in_threadpool(iterator: Iterator) -> asyncgenerator: ...
def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> coroutine: ...
def run_until_first_complete(*args: Tuple[Callable, dict]) -> Coroutine[Any, Any, None]: ...
