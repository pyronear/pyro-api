# (generated with --quick)

from typing import Any, Dict, Generic, List, TypeVar, Union

__all__: List[str]

D = TypeVar('D')
T = TypeVar('T')

class Store:
    __slots__ = ["_store"]
    __doc__: str
    _store: Dict[StoreKey, Any]
    def __contains__(self, key: StoreKey[T]) -> bool: ...
    def __delitem__(self, key: StoreKey[T]) -> None: ...
    def __getitem__(self, key: StoreKey[T]) -> T: ...
    def __init__(self) -> None: ...
    def __setitem__(self, key: StoreKey[T], value: T) -> None: ...
    def get(self, key: StoreKey[T], default: D) -> Union[D, T]: ...
    def setdefault(self, key: StoreKey[T], default: T) -> T: ...

class StoreKey(Generic[T]):
    __slots__ = []
    __doc__: str
