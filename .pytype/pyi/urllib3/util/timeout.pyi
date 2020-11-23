# (generated with --quick)

import __future__
from typing import Any, Type, TypeVar
import urllib3.exceptions

TimeoutStateError: Type[urllib3.exceptions.TimeoutStateError]
_Default: Any
_GLOBAL_DEFAULT_TIMEOUT: Any
absolute_import: __future__._Feature
current_time: Any
time: module

_TTimeout = TypeVar('_TTimeout', bound=Timeout)

class Timeout:
    DEFAULT_TIMEOUT: Any
    __doc__: str
    _connect: Any
    _read: Any
    _start_connect: Any
    connect_timeout: Any
    read_timeout: Any
    total: Any
    def __init__(self, total = ..., connect = ..., read = ...) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @classmethod
    def _validate_timeout(cls, value, name) -> Any: ...
    def clone(self: _TTimeout) -> _TTimeout: ...
    @classmethod
    def from_float(cls: Type[_TTimeout], timeout) -> _TTimeout: ...
    def get_connect_duration(self) -> Any: ...
    def start_connect(self) -> Any: ...
