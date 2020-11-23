# (generated with --quick)

from typing import Any, NoReturn, Type, TypeVar

_py3: bool
sys: module
warnings: module

_T_Result = TypeVar('_T_Result', bound=_Result)

class HookCallError(Exception):
    __doc__: str

class _LegacyMultiCall:
    __doc__: str
    caller_kwargs: Any
    firstresult: Any
    hook_impls: Any
    results: list
    def __init__(self, hook_impls, kwargs, firstresult = ...) -> None: ...
    def __repr__(self) -> str: ...
    def execute(self) -> Any: ...

class _Result:
    _excinfo: Any
    _result: Any
    excinfo: Any
    result: Any
    def __init__(self, result, excinfo) -> None: ...
    def force_result(self, result) -> None: ...
    @classmethod
    def from_call(cls: Type[_T_Result], func) -> _T_Result: ...
    def get_result(self) -> Any: ...

def _legacymulticall(hook_impls, caller_kwargs, firstresult = ...) -> Any: ...
def _multicall(hook_impls, caller_kwargs, firstresult = ...) -> Any: ...
def _raise_wrapfail(wrap_controller, msg) -> NoReturn: ...
def _wrapped_call(wrap_controller, func) -> Any: ...
