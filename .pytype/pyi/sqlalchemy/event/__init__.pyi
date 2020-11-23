# (generated with --quick)

import sqlalchemy.event.attr
import sqlalchemy.event.base
from typing import Any, Callable, Type

CANCEL: Any
Events: Type[sqlalchemy.event.base.Events]
NO_RETVAL: Any
RefCollection: Type[sqlalchemy.event.attr.RefCollection]
dispatcher: Type[sqlalchemy.event.base.dispatcher]

def _legacy_signature(since, argnames, converter = ...) -> Callable[[Any], Any]: ...
def contains(target, identifier, fn) -> Any: ...
def listen(target, identifier, fn, *args, **kw) -> None: ...
def listens_for(target, identifier, *args, **kw) -> Callable[[Any], Any]: ...
def remove(target, identifier, fn) -> None: ...
