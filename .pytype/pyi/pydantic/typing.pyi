# (generated with --quick)

import __builtin__
import enum
import pydantic.fields
import typing

AnyCallable = typing.Callable
NoArgAnyCallable = typing.Callable[[], typing.Any]

AbstractSet: typing.Any
AbstractSetIntStr: typing.Any
Any: typing.Any
Callable: typing.Type[typing.Callable]
CallableGenerator: typing.Any
ClassVar: typing.Any
Dict: typing.Any
DictAny: typing.Any
DictIntStrAny: typing.Any
DictStrAny: typing.Any
Enum: typing.Type[enum.Enum]
ForwardRef: typing.Any
Generator: typing.Any
IntStr: typing.Any
List: typing.Any
ListStr: typing.Any
Mapping: typing.Any
MappingIntStrAny: typing.Any
ModelField: typing.Type[pydantic.fields.ModelField]
NewType: typing.Any
NoneType: typing.Type[__builtin__.NoneType]
Optional: typing.Any
ReprArgs: typing.Any
Sequence: typing.Any
Set: typing.Any
SetStr: typing.Any
TYPE_CHECKING: typing.Any
Tuple: typing.Any
TupleGenerator: typing.Any
Type: typing.Any
TypingCallable: typing.Any
Union: typing.Any
__all__: typing.Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str]
_eval_type: typing.Any
sys: module
test_type: typing.Any
typing_base: typing.Any

def _check_classvar(v: typing.Any) -> bool: ...
def all_literal_values(type_: typing.Any) -> typing.Any: ...
def display_as_type(v: typing.Any) -> str: ...
def evaluate_forwardref(type_: typing.Any, globalns: typing.Any, localns: typing.Any) -> typing.Any: ...
def get_class(type_: typing.Any) -> typing.Any: ...
def is_callable_type(type_: typing.Any) -> bool: ...
def is_classvar(ann_type: typing.Any) -> bool: ...
def is_literal_type(type_: typing.Any) -> bool: ...
def is_new_type(type_: typing.Any) -> bool: ...
def literal_values(type_: typing.Any) -> typing.Any: ...
def new_type_supertype(type_: typing.Any) -> typing.Any: ...
def resolve_annotations(raw_annotations: typing.Any, module_name: typing.Any) -> typing.Any: ...
def update_field_forward_refs(field: pydantic.fields.ModelField, globalns: typing.Any, localns: typing.Any) -> __builtin__.NoneType: ...
