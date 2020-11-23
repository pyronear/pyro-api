# (generated with --quick)

from typing import Any, Callable, Generic, Optional, Tuple, Type, TypeVar

Protocol: Any
TEST_OUTCOME: Tuple[Type[OutcomeException], Type[Exception]]
TYPE_CHECKING: bool
exit: _WithException[Callable, Type[Exit]]
fail: _WithException[Callable, Type[Failed]]
skip: _WithException[Callable, Type[Skipped]]
sys: module
xfail: _WithException[Callable, Type[XFailed]]

_ET = TypeVar('_ET', bound=Any)
_F = TypeVar('_F', bound=Callable[..., object])

class Exit(Exception):
    __doc__: str
    msg: str
    returncode: Optional[int]
    def __init__(self, msg: str = ..., returncode: Optional[int] = ...) -> None: ...

class Failed(OutcomeException):
    __doc__: str
    msg: Optional[str]
    pytrace: bool

class OutcomeException(BaseException):
    __doc__: str
    msg: Any
    pytrace: bool
    def __init__(self, msg: Optional[str] = ..., pytrace: bool = ...) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Skipped(OutcomeException):
    allow_module_level: bool
    msg: Optional[str]
    pytrace: bool
    def __init__(self, msg: Optional[str] = ..., pytrace: bool = ..., allow_module_level: bool = ...) -> None: ...

class XFailed(Failed):
    __doc__: str
    msg: Any
    pytrace: bool

class _WithException(Generic[_F, _ET]):
    Exception: Any
    __call__: Any

def _with_exception(exception_type: _ET) -> Callable[[_F], _WithException[_F, _ET]]: ...
def importorskip(modname: str, minversion: Optional[str] = ..., reason: Optional[str] = ...) -> Any: ...
