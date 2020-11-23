# (generated with --quick)

import __future__
import cryptography.exceptions
from typing import Any, Type

InvalidSignature: Type[cryptography.exceptions.InvalidSignature]
_POLY1305_KEY_SIZE: int
_POLY1305_TAG_SIZE: int
absolute_import: __future__._Feature
constant_time: module
division: __future__._Feature
print_function: __future__._Feature

class _Poly1305Context:
    _backend: Any
    _ctx: Any
    _evp_pkey: Any
    def __init__(self, backend, key) -> None: ...
    def finalize(self) -> Any: ...
    def update(self, data) -> None: ...
    def verify(self, tag) -> None: ...
