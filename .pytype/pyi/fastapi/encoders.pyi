# (generated with --quick)

import collections
import enum
import pathlib
import types
from typing import Any, Callable, Dict, Optional, Set, Type, Union

DictIntStrAny = Dict[Union[int, str], Any]
SetIntStr = Set[Union[int, str]]

BaseModel: Any
ENCODERS_BY_TYPE: Dict[Any, Callable[[Any], Any]]
Enum: Type[enum.Enum]
GeneratorType: Type[types.GeneratorType]
PurePath: Type[pathlib.PurePath]
defaultdict: Type[collections.defaultdict]
encoders_by_class_tuples: Dict[Callable, tuple]

def generate_encoders_by_class_tuples(type_encoder_map: Dict[Any, Callable]) -> Dict[Callable, tuple]: ...
def jsonable_encoder(obj, include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., custom_encoder: dict = ..., sqlalchemy_safe: bool = ...) -> Any: ...
