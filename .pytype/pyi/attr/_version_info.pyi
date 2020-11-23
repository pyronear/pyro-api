# (generated with --quick)

import __future__
import attr._make
from typing import Any, Type, TypeVar

VersionInfo: Any
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature

_T = TypeVar('_T')

def astuple(inst, recurse = ..., filter = ..., tuple_factory = ..., retain_collection_types = ...) -> Any: ...
def attrib(default = ..., validator = ..., repr = ..., cmp = ..., hash = ..., init: bool = ..., metadata = ..., type = ..., converter = ..., factory = ..., kw_only = ..., eq = ..., order = ..., on_setattr = ...) -> attr._make._CountingAttr: ...
def attrs(maybe_cls = ..., these = ..., repr_ns = ..., repr = ..., cmp = ..., hash = ..., init: bool = ..., slots = ..., frozen = ..., weakref_slot = ..., str = ..., auto_attribs = ..., kw_only = ..., cache_hash = ..., auto_exc = ..., eq = ..., order = ...) -> Any: ...
def total_ordering(cls: Type[_T]) -> Type[_T]: ...
