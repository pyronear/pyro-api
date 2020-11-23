# (generated with --quick)

import __future__
import sqlalchemy.event.registry
from typing import Any, Callable, Type

CANCEL: Any
NO_RETVAL: Any
_EventKey: Type[sqlalchemy.event.registry._EventKey]
_registrars: Any
absolute_import: __future__._Feature
exc: module
util: module

def _event_key(target, identifier, fn) -> sqlalchemy.event.registry._EventKey: ...
def contains(target, identifier, fn) -> Any: ...
def listen(target, identifier, fn, *args, **kw) -> None: ...
def listens_for(target, identifier, *args, **kw) -> Callable[[Any], Any]: ...
def remove(target, identifier, fn) -> None: ...
