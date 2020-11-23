# (generated with --quick)

import __future__
from typing import Any, Tuple, Type

ConnectionError = ProtocolError

absolute_import: __future__._Feature
httplib_IncompleteRead: Any

class BodyNotHttplibCompatible(HTTPError):
    __doc__: str

class ClosedPoolError(PoolError):
    __doc__: str
    pool: Any

class ConnectTimeoutError(TimeoutError):
    __doc__: str

class DecodeError(HTTPError):
    __doc__: str

class DependencyWarning(HTTPWarning):
    __doc__: str

class EmptyPoolError(PoolError):
    __doc__: str
    pool: Any

class HTTPError(Exception):
    __doc__: str

class HTTPWarning(Warning):
    __doc__: str

class HeaderParsingError(HTTPError):
    __doc__: str
    def __init__(self, defects, unparsed_data) -> None: ...

class HostChangedError(RequestError):
    __doc__: str
    pool: Any
    retries: Any
    url: Any
    def __init__(self, pool, url, retries = ...) -> None: ...

class IncompleteRead(HTTPError, Any):
    __doc__: str
    def __init__(self, partial, expected) -> None: ...
    def __repr__(self) -> str: ...

class InsecurePlatformWarning(SecurityWarning):
    __doc__: str

class InsecureRequestWarning(SecurityWarning):
    __doc__: str

class InvalidHeader(HTTPError):
    __doc__: str

class InvalidProxyConfigurationWarning(HTTPWarning):
    __doc__: str

class LocationParseError(LocationValueError):
    __doc__: str
    location: Any
    def __init__(self, location) -> None: ...

class LocationValueError(ValueError, HTTPError):
    __doc__: str

class MaxRetryError(RequestError):
    __doc__: str
    pool: Any
    reason: Any
    url: Any
    def __init__(self, pool, url, reason = ...) -> None: ...

class NewConnectionError(ConnectTimeoutError, PoolError):
    __doc__: str
    pool: Any

class PoolError(HTTPError):
    __doc__: str
    pool: Any
    def __init__(self, pool, message) -> None: ...
    def __reduce__(self) -> Tuple[Type[PoolError], Tuple[None, None]]: ...

class ProtocolError(HTTPError):
    __doc__: str

class ProxyError(HTTPError):
    __doc__: str
    original_error: Any
    def __init__(self, message, error, *args) -> None: ...

class ProxySchemeUnknown(AssertionError, ValueError):
    __doc__: str
    def __init__(self, scheme) -> None: ...

class ReadTimeoutError(TimeoutError, RequestError):
    __doc__: str
    pool: Any
    url: Any

class RequestError(PoolError):
    __doc__: str
    pool: Any
    url: Any
    def __init__(self, pool, url, message) -> None: ...
    def __reduce__(self) -> Tuple[Type[RequestError], Tuple[None, Any, None]]: ...

class ResponseError(HTTPError):
    GENERIC_ERROR: str
    SPECIFIC_ERROR: str
    __doc__: str

class ResponseNotChunked(ProtocolError, ValueError):
    __doc__: str

class SNIMissingWarning(HTTPWarning):
    __doc__: str

class SSLError(HTTPError):
    __doc__: str

class SecurityWarning(HTTPWarning):
    __doc__: str

class SubjectAltNameWarning(SecurityWarning):
    __doc__: str

class SystemTimeWarning(SecurityWarning):
    __doc__: str

class TimeoutError(HTTPError):
    __doc__: str

class TimeoutStateError(HTTPError):
    __doc__: str

class UnrewindableBodyError(HTTPError):
    __doc__: str
