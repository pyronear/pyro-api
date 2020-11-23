# (generated with --quick)

import __future__
import cryptography.exceptions
from typing import Any, Type, TypeVar

CBC: Any
InvalidSignature: Type[cryptography.exceptions.InvalidSignature]
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_Reasons: Type[cryptography.exceptions._Reasons]
absolute_import: __future__._Feature
constant_time: module
division: __future__._Feature
print_function: __future__._Feature
utils: module

_T_CMACContext = TypeVar('_T_CMACContext', bound=_CMACContext)

class _CMACContext:
    _algorithm: Any
    _backend: Any
    _ctx: Any
    _key: Any
    _output_length: Any
    algorithm: Any
    def __init__(self, backend, algorithm, ctx = ...) -> None: ...
    def copy(self: _T_CMACContext) -> _T_CMACContext: ...
    def finalize(self) -> Any: ...
    def update(self, data) -> None: ...
    def verify(self, signature) -> None: ...
