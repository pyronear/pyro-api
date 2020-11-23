# (generated with --quick)

import __future__
import collections
from typing import Any, Callable, FrozenSet, Iterable, Iterator, Sized, Tuple, Type, TypeVar, Union
import urllib3.exceptions

RequestHistory = `namedtuple-RequestHistory-method-url-error-status-redirect_location`

ConnectTimeoutError: Type[urllib3.exceptions.ConnectTimeoutError]
InvalidHeader: Type[urllib3.exceptions.InvalidHeader]
MaxRetryError: Type[urllib3.exceptions.MaxRetryError]
ProtocolError: Type[urllib3.exceptions.ProtocolError]
ProxyError: Type[urllib3.exceptions.ProxyError]
ReadTimeoutError: Type[urllib3.exceptions.ReadTimeoutError]
ResponseError: Type[urllib3.exceptions.ResponseError]
absolute_import: __future__._Feature
email: module
log: logging.Logger
logging: module
re: module
six: module
time: module

_T = TypeVar('_T')
_T0 = TypeVar('_T0')
_T2 = TypeVar('_T2')
_TRetry = TypeVar('_TRetry', bound=Retry)
_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location = TypeVar('_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location', bound=`namedtuple-RequestHistory-method-url-error-status-redirect_location`)

class Retry:
    BACKOFF_MAX: int
    DEFAULT: Retry
    DEFAULT_METHOD_WHITELIST: FrozenSet[str]
    DEFAULT_REDIRECT_HEADERS_BLACKLIST: FrozenSet[str]
    RETRY_AFTER_STATUS_CODES: FrozenSet[int]
    __doc__: str
    backoff_factor: Any
    connect: Any
    history: Any
    method_whitelist: Any
    raise_on_redirect: Any
    raise_on_status: Any
    read: Any
    redirect: Any
    remove_headers_on_redirect: frozenset
    respect_retry_after_header: Any
    status: Any
    status_forcelist: Any
    total: Any
    def __init__(self, total = ..., connect = ..., read = ..., redirect = ..., status = ..., method_whitelist = ..., status_forcelist = ..., backoff_factor = ..., raise_on_redirect = ..., raise_on_status = ..., history = ..., respect_retry_after_header = ..., remove_headers_on_redirect = ...) -> None: ...
    def __repr__(self) -> Any: ...
    def _is_connection_error(self, err) -> bool: ...
    def _is_method_retryable(self, method) -> bool: ...
    def _is_read_error(self, err) -> bool: ...
    def _sleep_backoff(self) -> None: ...
    @classmethod
    def from_int(cls, retries: _T0, redirect = ..., default: _T2 = ...) -> Union[Retry, _T0, _T2]: ...
    def get_backoff_time(self) -> Any: ...
    def get_retry_after(self, response) -> Any: ...
    def increment(self, method = ..., url = ..., response = ..., error = ..., _pool = ..., _stacktrace = ...) -> Any: ...
    def is_exhausted(self) -> Any: ...
    def is_retry(self, method, status_code, has_retry_after: _T2 = ...) -> Any: ...
    def new(self: _TRetry, **kw) -> _TRetry: ...
    def parse_retry_after(self, retry_after) -> Union[float, int]: ...
    def sleep(self, response = ...) -> None: ...
    def sleep_for_retry(self, response = ...) -> bool: ...

class `namedtuple-RequestHistory-method-url-error-status-redirect_location`(tuple):
    __slots__ = ["error", "method", "redirect_location", "status", "url"]
    __dict__: collections.OrderedDict[str, Any]
    _fields: Tuple[str, str, str, str, str]
    error: Any
    method: Any
    redirect_location: Any
    status: Any
    url: Any
    def __getnewargs__(self) -> Tuple[Any, Any, Any, Any, Any]: ...
    def __getstate__(self) -> None: ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __new__(cls: Type[`_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`], method, url, error, status, redirect_location) -> `_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`: ...
    def _asdict(self) -> collections.OrderedDict[str, Any]: ...
    @classmethod
    def _make(cls: Type[`_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`], iterable: Iterable, new = ..., len: Callable[[Sized], int] = ...) -> `_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`: ...
    def _replace(self: `_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`, **kwds) -> `_Tnamedtuple-RequestHistory-method-url-error-status-redirect_location`: ...

def namedtuple(typename: str, field_names: Union[str, Iterable[str]], *, verbose: bool = ..., rename: bool = ...) -> type: ...
def takewhile(predicate: Callable[[_T], object], iterable: Iterable[_T]) -> Iterator[_T]: ...
