# (generated with --quick)

import __builtin__
import collections
import http.cookies
import io
import typing
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union
import urllib.parse

Callable: Type[typing.Callable]
Mapping: Type[typing.Mapping]
Morsel: Type[http.cookies.Morsel]
MutableMapping: Type[typing.MutableMapping]
OrderedDict: Type[collections.OrderedDict]
StringIO: Type[io.StringIO]
_ver: Tuple[int, int, int, __builtin__.str, int]
basestring: Tuple[Type[__builtin__.str], Type[__builtin__.bytes]]
builtin_str: Type[__builtin__.str]
bytes: Type[__builtin__.bytes]
chardet: module
cookielib: module
getproxies_environment: Any
integer_types: Tuple[Type[int]]
is_py2: bool
is_py3: bool
json: module
numeric_types: Tuple[Type[int], Type[float]]
proxy_bypass_environment: Any
str: Type[__builtin__.str]
sys: module

AnyStr = TypeVar('AnyStr', str, bytes)

def getproxies() -> Dict[__builtin__.str, __builtin__.str]: ...
def parse_http_list(s: __builtin__.str) -> List[__builtin__.str]: ...
def proxy_bypass(host: __builtin__.str) -> Any: ...
@overload
def quote(string: __builtin__.str, safe: Union[bytearray, __builtin__.bytes, memoryview, __builtin__.str] = ..., encoding: Optional[__builtin__.str] = ..., errors: Optional[__builtin__.str] = ...) -> __builtin__.str: ...
@overload
def quote(string: Union[bytearray, __builtin__.bytes, memoryview], safe: Union[bytearray, __builtin__.bytes, memoryview, __builtin__.str] = ...) -> __builtin__.str: ...
@overload
def quote_plus(string: __builtin__.str, safe: Union[bytearray, __builtin__.bytes, memoryview, __builtin__.str] = ..., encoding: Optional[__builtin__.str] = ..., errors: Optional[__builtin__.str] = ...) -> __builtin__.str: ...
@overload
def quote_plus(string: Union[bytearray, __builtin__.bytes, memoryview], safe: Union[bytearray, __builtin__.bytes, memoryview, __builtin__.str] = ...) -> __builtin__.str: ...
def unquote(string: __builtin__.str, encoding: __builtin__.str = ..., errors: __builtin__.str = ...) -> __builtin__.str: ...
def unquote_plus(string: __builtin__.str, encoding: __builtin__.str = ..., errors: __builtin__.str = ...) -> __builtin__.str: ...
@overload
def urldefrag(url: __builtin__.str) -> urllib.parse.DefragResult: ...
@overload
def urldefrag(url: Optional[Union[bytearray, __builtin__.bytes, memoryview]]) -> urllib.parse.DefragResultBytes: ...
def urlencode(query: Union[typing.Mapping, Sequence[Tuple[Any, Any]]], doseq: bool = ..., safe: AnyStr = ..., encoding: __builtin__.str = ..., errors: __builtin__.str = ..., quote_via: typing.Callable[[__builtin__.str, AnyStr, __builtin__.str, __builtin__.str], __builtin__.str] = ...) -> __builtin__.str: ...
def urljoin(base: AnyStr, url: Optional[AnyStr], allow_fragments: bool = ...) -> AnyStr: ...
@overload
def urlparse(url: __builtin__.str, scheme: Optional[__builtin__.str] = ..., allow_fragments: bool = ...) -> urllib.parse.ParseResult: ...
@overload
def urlparse(url: Optional[Union[bytearray, __builtin__.bytes, memoryview]], scheme: Optional[Union[bytearray, __builtin__.bytes, memoryview]] = ..., allow_fragments: bool = ...) -> urllib.parse.ParseResultBytes: ...
@overload
def urlsplit(url: __builtin__.str, scheme: Optional[__builtin__.str] = ..., allow_fragments: bool = ...) -> urllib.parse.SplitResult: ...
@overload
def urlsplit(url: Optional[Union[bytearray, __builtin__.bytes, memoryview]], scheme: Optional[Union[bytearray, __builtin__.bytes, memoryview]] = ..., allow_fragments: bool = ...) -> urllib.parse.SplitResultBytes: ...
def urlunparse(components: Union[Sequence[Optional[AnyStr]], Tuple[Optional[AnyStr], Optional[AnyStr], Optional[AnyStr], Optional[AnyStr], Optional[AnyStr], Optional[AnyStr]]]) -> AnyStr: ...
