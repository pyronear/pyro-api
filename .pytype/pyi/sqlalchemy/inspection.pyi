# (generated with --quick)

import collections
from typing import Any, Callable, TypeVar

_registrars: collections.defaultdict
exc: module
util: module

_T0 = TypeVar('_T0')

def _inspects(*types) -> Callable[[Any], Any]: ...
def _self_inspects(cls: _T0) -> _T0: ...
def inspect(subject, raiseerr = ...) -> Any: ...
