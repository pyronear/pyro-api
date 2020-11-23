# (generated with --quick)

import __future__
import enum
from typing import Any, Type

Enum: Type[enum.Enum]
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature

class AlreadyFinalized(Exception): ...

class AlreadyUpdated(Exception): ...

class InternalError(Exception):
    err_code: Any
    def __init__(self, msg, err_code) -> None: ...

class InvalidKey(Exception): ...

class InvalidSignature(Exception): ...

class InvalidTag(Exception): ...

class NotYetFinalized(Exception): ...

class UnsupportedAlgorithm(Exception):
    _reason: Any
    def __init__(self, message, reason = ...) -> None: ...

class _Reasons(enum.Enum):
    BACKEND_MISSING_INTERFACE: int
    UNSUPPORTED_CIPHER: int
    UNSUPPORTED_DIFFIE_HELLMAN: int
    UNSUPPORTED_ELLIPTIC_CURVE: int
    UNSUPPORTED_EXCHANGE_ALGORITHM: int
    UNSUPPORTED_HASH: int
    UNSUPPORTED_MAC: int
    UNSUPPORTED_MGF: int
    UNSUPPORTED_PADDING: int
    UNSUPPORTED_PUBLIC_KEY_ALGORITHM: int
    UNSUPPORTED_SERIALIZATION: int
    UNSUPPORTED_X509: int
