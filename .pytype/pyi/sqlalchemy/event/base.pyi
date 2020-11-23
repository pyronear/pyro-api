# (generated with --quick)

import __future__
import collections
from typing import Any, Generator, Optional, Tuple, TypeVar

_ClsLevelDispatch: Any
_EmptyListener: Any
_JoinedListener: Any
_registrars: collections.defaultdict
absolute_import: __future__._Feature
util: module
weakref: module

_T0 = TypeVar('_T0')
_T_Dispatch = TypeVar('_T_Dispatch', bound=_Dispatch)

class Events(Any):
    __doc__: str
    @classmethod
    def _accept_with(cls, target: _T0) -> Optional[_T0]: ...
    @classmethod
    def _clear(cls) -> None: ...
    @classmethod
    def _listen(cls, event_key, propagate = ..., insert = ..., named = ...) -> None: ...
    @classmethod
    def _remove(cls, event_key) -> None: ...
    @staticmethod
    def _set_dispatch(cls, dispatch_cls) -> Any: ...

class _Dispatch:
    __slots__ = ["__dict__", "_empty_listeners", "_instance_cls", "_parent"]
    __doc__: str
    _empty_listener_reg: weakref.WeakKeyDictionary[nothing, nothing]
    _empty_listeners: Any
    _event_descriptors: Generator[Any, Any, None]
    _instance_cls: Any
    _joined_dispatch_cls: Any
    _listen: Any
    _parent: Any
    def __getattr__(self, name) -> Any: ...
    def __init__(self, parent, instance_cls = ...) -> None: ...
    def __reduce__(self) -> Tuple[_UnpickleDispatch, Tuple[Any]]: ...
    def _clear(self) -> None: ...
    def _for_class(self: _T_Dispatch, instance_cls) -> _T_Dispatch: ...
    def _for_instance(self, instance) -> Any: ...
    def _join(self, other) -> Any: ...
    def _update(self, other, only_propagate = ...) -> None: ...

class _EventMeta(type):
    __doc__: str
    def __init__(cls: _EventMeta, classname, bases, dict_) -> None: ...

class _JoinedDispatcher:
    __slots__ = ["_instance_cls", "local", "parent"]
    __doc__: str
    _events: Any
    _instance_cls: Any
    _listen: Any
    local: Any
    parent: Any
    def __getattr__(self, name) -> Any: ...
    def __init__(self, local, parent) -> None: ...

class _UnpickleDispatch:
    __doc__: str
    def __call__(self, _instance_cls) -> Any: ...

class dispatcher:
    __doc__: str
    dispatch: Any
    events: Any
    def __get__(self, obj, cls) -> Any: ...
    def __init__(self, events) -> None: ...

def _create_dispatcher_class(cls, classname, bases, dict_) -> None: ...
def _is_event_name(name) -> Any: ...
def _remove_dispatcher(cls) -> None: ...
