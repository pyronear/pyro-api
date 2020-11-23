# (generated with --quick)

import __future__
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union
import urllib3.exceptions

ACCEPT_ENCODING: str
UnrewindableBodyError: Type[urllib3.exceptions.UnrewindableBodyError]
_FAILEDTELL: Any
_unused_module_brotli: Any
absolute_import: __future__._Feature
integer_types: Tuple[Type[int]]

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')

def b(s) -> Any: ...
def b64encode(s: bytes, altchars: Optional[bytes] = ...) -> bytes: ...
def make_headers(keep_alive = ..., accept_encoding: _T1 = ..., user_agent: _T2 = ..., basic_auth = ..., proxy_basic_auth = ..., disable_cache = ...) -> Dict[str, Union[str, _T1, _T2]]: ...
def rewind_body(body, body_pos) -> None: ...
def set_file_position(body, pos) -> Any: ...
