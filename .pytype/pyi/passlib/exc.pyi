# (generated with --quick)

from typing import Any, NoReturn

ENABLE_DEBUG_ONLY_REPR: bool

class InternalBackendError(RuntimeError):
    __doc__: str

class InvalidTokenError(TokenError):
    __doc__: str
    _default_message: str

class MalformedTokenError(TokenError):
    __doc__: str
    _default_message: str

class MissingBackendError(RuntimeError):
    __doc__: str

class PasslibConfigWarning(PasslibWarning):
    __doc__: str

class PasslibHashWarning(PasslibWarning):
    __doc__: str

class PasslibRuntimeWarning(PasslibWarning):
    __doc__: str

class PasslibSecurityError(RuntimeError):
    __doc__: str

class PasslibSecurityWarning(PasslibWarning):
    __doc__: str

class PasslibWarning(UserWarning):
    __doc__: str

class PasswordSizeError(PasswordValueError):
    __doc__: str
    max_size: Any
    def __init__(self, max_size, msg = ...) -> None: ...

class PasswordTruncateError(PasswordSizeError):
    __doc__: str
    max_size: Any
    def __init__(self, cls, msg = ...) -> None: ...

class PasswordValueError(ValueError):
    __doc__: str

class TokenError(ValueError):
    __doc__: str
    _default_message: str
    def __init__(self, msg = ..., *args, **kwds) -> None: ...

class UnknownBackendError(ValueError):
    __doc__: str
    backend: Any
    hasher: Any
    def __init__(self, hasher, backend) -> None: ...

class UnknownHashError(ValueError):
    __doc__: str
    message: Any
    value: Any
    def __init__(self, message = ..., value = ...) -> None: ...
    def __str__(self) -> Any: ...

class UsedTokenError(TokenError):
    __doc__: str
    _default_message: str
    expire_time: Any
    def __init__(self, *args, **kwds) -> None: ...

def ChecksumSizeError(handler, raw = ...) -> Any: ...
def CryptBackendError(handler, config, hash, source = ...) -> NoReturn: ...
def ExpectedStringError(value, param) -> Any: ...
def ExpectedTypeError(value, expected, param) -> TypeError: ...
def InvalidHashError(handler = ...) -> ValueError: ...
def MalformedHashError(handler = ..., reason = ...) -> ValueError: ...
def MissingDigestError(handler = ...) -> ValueError: ...
def NullPasswordError(handler = ...) -> PasswordValueError: ...
def ZeroPaddedRoundsError(handler = ...) -> Any: ...
def _get_name(handler) -> Any: ...
def debug_only_repr(value, param = ...) -> str: ...
def type_name(value) -> Any: ...
