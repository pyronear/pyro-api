# (generated with --quick)

import __future__
import attr._make
from typing import Any, Callable, List, TypeVar

NOTHING: attr._make._Nothing
__all__: List[str]
absolute_import: __future__._Feature
division: __future__._Feature
pipe: Any
print_function: __future__._Feature

_T0 = TypeVar('_T0')

def Factory(factory: Callable[..., _T0], takes_self: bool = ...) -> _T0: ...
def default_if_none(default = ..., factory = ...) -> Callable[[Any], Any]: ...
def optional(converter) -> Callable[[Any], Any]: ...
