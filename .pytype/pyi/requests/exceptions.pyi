# (generated with --quick)

from typing import Any, Type
import urllib3.exceptions

BaseHTTPError: Type[urllib3.exceptions.HTTPError]

class ChunkedEncodingError(RequestException):
    __doc__: str
    request: Any
    response: Any

class ConnectTimeout(ConnectionError, Timeout):
    __doc__: str
    request: Any
    response: Any

class ConnectionError(RequestException):
    __doc__: str
    request: Any
    response: Any

class ContentDecodingError(RequestException, urllib3.exceptions.HTTPError):
    __doc__: str
    request: Any
    response: Any

class FileModeWarning(RequestsWarning, DeprecationWarning):
    __doc__: str

class HTTPError(RequestException):
    __doc__: str
    request: Any
    response: Any

class InvalidHeader(RequestException, ValueError):
    __doc__: str
    request: Any
    response: Any

class InvalidProxyURL(InvalidURL):
    __doc__: str
    request: Any
    response: Any

class InvalidSchema(RequestException, ValueError):
    __doc__: str
    request: Any
    response: Any

class InvalidURL(RequestException, ValueError):
    __doc__: str
    request: Any
    response: Any

class MissingSchema(RequestException, ValueError):
    __doc__: str
    request: Any
    response: Any

class ProxyError(ConnectionError):
    __doc__: str
    request: Any
    response: Any

class ReadTimeout(Timeout):
    __doc__: str
    request: Any
    response: Any

class RequestException(OSError):
    __doc__: str
    request: Any
    response: Any
    def __init__(self, *args, **kwargs) -> None: ...

class RequestsDependencyWarning(RequestsWarning):
    __doc__: str

class RequestsWarning(Warning):
    __doc__: str

class RetryError(RequestException):
    __doc__: str
    request: Any
    response: Any

class SSLError(ConnectionError):
    __doc__: str
    request: Any
    response: Any

class StreamConsumedError(RequestException, TypeError):
    __doc__: str
    request: Any
    response: Any

class Timeout(RequestException):
    __doc__: str
    request: Any
    response: Any

class TooManyRedirects(RequestException):
    __doc__: str
    request: Any
    response: Any

class URLRequired(RequestException):
    __doc__: str
    request: Any
    response: Any

class UnrewindableBodyError(RequestException):
    __doc__: str
    request: Any
    response: Any
