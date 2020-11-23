# (generated with --quick)

from typing import Any, Dict, Type

ModuleType: Type[module]
_winerrnomap: Dict[int, int]
errno: module
error: ErrorMaker
os: module
sys: module

class Error(OSError):
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class ErrorMaker(module):
    Error: Type[Error]
    __doc__: str
    _errno2class: dict
    def __getattr__(self, name) -> Any: ...
    def _geterrnoclass(self, eno) -> Any: ...
    def checked_call(self, func, *args, **kwargs) -> Any: ...
