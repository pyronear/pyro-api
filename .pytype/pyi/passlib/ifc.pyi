# (generated with --quick)

import abc
from typing import Any, Callable, List, NoReturn, Type, TypeVar

ABCMeta: Type[abc.ABCMeta]
PasswordHash: Any
__all__: List[str]
abstractproperty: Type[abc.abstractproperty]
log: logging.Logger
logging: module
sys: module

_FuncT = TypeVar('_FuncT', bound=Callable)

class DisabledHash(Any):
    __doc__: str
    is_disabled: bool
    @classmethod
    def disable(cls, hash = ...) -> Any: ...
    @classmethod
    def enable(cls, hash) -> NoReturn: ...

def abstractmethod(callable: _FuncT) -> _FuncT: ...
def deprecated_method(msg = ..., deprecated = ..., removed = ..., updoc = ..., replacement = ...) -> Any: ...
def recreate_with_metaclass(meta) -> Callable[[Any], Any]: ...
