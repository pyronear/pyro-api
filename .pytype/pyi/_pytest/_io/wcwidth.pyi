# (generated with --quick)

import functools
from typing import Any, Callable, Optional, TypeVar

unicodedata: module
wcwidth: functools._lru_cache_wrapper[int]

_T = TypeVar('_T')

@overload
def lru_cache(maxsize: Callable[..., _T], typed: bool = ...) -> functools._lru_cache_wrapper[_T]: ...
@overload
def lru_cache(maxsize: Optional[int] = ..., typed: bool = ...) -> Callable[[Callable[..., _T]], functools._lru_cache_wrapper[_T]]: ...
def wcswidth(s: str) -> int: ...
