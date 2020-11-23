# (generated with --quick)

import __future__
import attr.exceptions
from typing import Any, Callable, NoReturn, Type, TypeVar

FrozenAttributeError: Type[attr.exceptions.FrozenAttributeError]
NO_OP: Any
_config: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature

_T2 = TypeVar('_T2')

def convert(instance, attrib, new_value) -> Any: ...
def frozen(_, __, ___) -> NoReturn: ...
def pipe(*setters) -> Callable[[Any, Any, Any], Any]: ...
def validate(instance, attrib, new_value: _T2) -> _T2: ...
