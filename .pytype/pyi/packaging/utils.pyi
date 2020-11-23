# (generated with --quick)

import __future__
import packaging.version
from typing import Pattern, Type, TypeVar, Union

InvalidVersion: Type[packaging.version.InvalidVersion]
TYPE_CHECKING: bool
Version: Type[packaging.version.Version]
_canonicalize_regex: Pattern[str]
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
re: module

_T1 = TypeVar('_T1')

class NormalizedName(str):
    def __init__(self, val: str) -> None: ...

def canonicalize_name(name: str) -> NormalizedName: ...
def canonicalize_version(_version: str) -> Union[str, packaging.version.Version]: ...
def cast(type_, value: _T1) -> _T1: ...
