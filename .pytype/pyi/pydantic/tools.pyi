# (generated with --quick)

import functools
import pathlib
import pydantic.parse
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

NameFactory: Type[Union[Callable[[type], str], str]]
Path: Type[pathlib.Path]
Protocol: Type[pydantic.parse.Protocol]
__all__: Tuple[str, str]
_get_parsing_type: functools._lru_cache_wrapper
json: module

T = TypeVar('T')
_T = TypeVar('_T')

def _generate_parsing_type_name(type_) -> str: ...
def display_as_type(v) -> str: ...
def load_file(path: Union[str, pathlib.Path], *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ...) -> Any: ...
@overload
def lru_cache(maxsize: Callable[..., _T], typed: bool = ...) -> functools._lru_cache_wrapper[_T]: ...
@overload
def lru_cache(maxsize: Optional[int] = ..., typed: bool = ...) -> Callable[[Callable[..., _T]], functools._lru_cache_wrapper[_T]]: ...
def parse_file_as(type_: Type[T], path: Union[str, pathlib.Path], *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ..., type_name: Optional[Union[Callable[[type], str], str]] = ...) -> T: ...
def parse_obj_as(type_: Type[T], obj, *, type_name: Optional[Union[Callable[[type], str], str]] = ...) -> T: ...
