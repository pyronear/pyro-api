# (generated with --quick)

import __builtin__
import pydantic.error_wrappers
import pydantic.errors
import pydantic.main
import pydantic.types
import pydantic.utils
import typing
from typing import Any, Dict, Generator, Iterable, List, Sequence, Tuple, Type, TypeVar, Union

NoArgAnyCallable = typing.Callable[[], Any]
ValidateReturn = Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]

BaseConfig: Type[pydantic.main.BaseConfig]
BaseModel: Type[pydantic.main.BaseModel]
BoolUndefined: Type[Union[UndefinedType, bool]]
Callable: Type[typing.Callable]
CollectionsIterable: Type[Iterable]
ErrorList: Type[Union[pydantic.error_wrappers.ErrorWrapper, Sequence]]
ErrorWrapper: Type[pydantic.error_wrappers.ErrorWrapper]
ForwardRef: Any
Json: Type[pydantic.types.Json]
JsonWrapper: Type[pydantic.types.JsonWrapper]
LocStr: Type[Union[str, Tuple[Union[int, str], ...]]]
ModelOrDc: Type[type]
NoneIsNotAllowedError: Type[pydantic.errors.NoneIsNotAllowedError]
NoneType: Type[__builtin__.NoneType]
PyObjectStr: Type[pydantic.utils.PyObjectStr]
ReprArgs: Any
Representation: Type[pydantic.utils.Representation]
Required: Any
SHAPE_FROZENSET: int
SHAPE_GENERIC: int
SHAPE_ITERABLE: int
SHAPE_LIST: int
SHAPE_MAPPING: int
SHAPE_NAME_LOOKUP: Dict[int, str]
SHAPE_SEQUENCE: int
SHAPE_SET: int
SHAPE_SINGLETON: int
SHAPE_TUPLE: int
SHAPE_TUPLE_ELLIPSIS: int
Undefined: UndefinedType
Validator: Any
ValidatorsList: Any
errors_: module
make_generic_validator: Any
prep_validators: Any
warnings: module

_T = TypeVar('_T')
_TModelField = TypeVar('_TModelField', bound=ModelField)

class FieldInfo(pydantic.utils.Representation):
    __slots__ = ["alias", "alias_priority", "const", "default", "default_factory", "description", "extra", "ge", "gt", "le", "lt", "max_items", "max_length", "min_items", "min_length", "multiple_of", "regex", "title"]
    __doc__: str
    alias: Any
    alias_priority: Any
    const: Any
    default: Any
    default_factory: Any
    description: Any
    extra: Dict[str, Any]
    ge: Any
    gt: Any
    le: Any
    lt: Any
    max_items: Any
    max_length: Any
    min_items: Any
    min_length: Any
    multiple_of: Any
    regex: Any
    title: Any
    def __init__(self, default = ..., **kwargs) -> __builtin__.NoneType: ...

class ModelField(pydantic.utils.Representation):
    __slots__ = ["alias", "allow_none", "class_validators", "default", "default_factory", "field_info", "has_alias", "key_field", "model_config", "name", "outer_type_", "parse_json", "post_validators", "pre_validators", "required", "shape", "sub_fields", "type_", "validate_always", "validators"]
    alias: str
    allow_none: bool
    alt_alias: bool
    class_validators: Dict[str, Any]
    default: Any
    default_factory: Union[typing.Callable[[], Any], __builtin__.NoneType]
    field_info: FieldInfo
    has_alias: bool
    key_field: __builtin__.NoneType
    model_config: Type[pydantic.main.BaseConfig]
    name: str
    outer_type_: Any
    parse_json: bool
    post_validators: __builtin__.NoneType
    pre_validators: __builtin__.NoneType
    required: Union[UndefinedType, bool]
    shape: int
    sub_fields: __builtin__.NoneType
    type_: Any
    validate_always: bool
    validators: List[nothing]
    def __init__(self, *, name: str, type_: type, class_validators: Union[__builtin__.NoneType, Dict[str, Any]], model_config: Type[pydantic.main.BaseConfig], default = ..., default_factory: Union[typing.Callable[[], Any], __builtin__.NoneType] = ..., required: Union[UndefinedType, __builtin__.NoneType, bool] = ..., alias: str = ..., field_info: Union[FieldInfo, __builtin__.NoneType] = ...) -> __builtin__.NoneType: ...
    def __repr_args__(self) -> Any: ...
    def _apply_validators(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type], validators) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def _create_sub_type(self: _TModelField, type_: type, name: str, *, for_keys: Union[__builtin__.NoneType, bool] = ...) -> _TModelField: ...
    def _set_default_and_type(self) -> __builtin__.NoneType: ...
    def _type_analysis(self) -> __builtin__.NoneType: ...
    def _type_display(self) -> pydantic.utils.PyObjectStr: ...
    def _validate_iterable(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type]) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def _validate_mapping(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type]) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def _validate_sequence_like(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type]) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def _validate_singleton(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type]) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def _validate_tuple(self, v, values: Dict[str, Any], loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type]) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...
    def get_default(self) -> Any: ...
    def include_in_schema(self) -> bool: ...
    @classmethod
    def infer(cls, *, name: str, value, annotation, class_validators: Union[__builtin__.NoneType, Dict[str, Any]], config: Type[pydantic.main.BaseConfig]) -> ModelField: ...
    def is_complex(self) -> bool: ...
    def populate_validators(self) -> __builtin__.NoneType: ...
    def prepare(self) -> __builtin__.NoneType: ...
    def set_config(self, config: Type[pydantic.main.BaseConfig]) -> __builtin__.NoneType: ...
    def validate(self, v, values: Dict[str, Any], *, loc: Union[str, Tuple[Union[int, str], ...]], cls: Union[__builtin__.NoneType, type] = ...) -> Tuple[Any, Union[__builtin__.NoneType, pydantic.error_wrappers.ErrorWrapper, Sequence]]: ...

class UndefinedType:
    def __repr__(self) -> str: ...

def Field(default = ..., *, default_factory: Union[typing.Callable[[], Any], __builtin__.NoneType] = ..., alias: str = ..., title: str = ..., description: str = ..., const: bool = ..., gt: float = ..., ge: float = ..., lt: float = ..., le: float = ..., multiple_of: float = ..., min_items: int = ..., max_items: int = ..., min_length: int = ..., max_length: int = ..., regex: str = ..., **extra) -> Any: ...
def Schema(default, **kwargs) -> Any: ...
def constant_validator(v, field) -> Any: ...
def deepcopy(x: _T, memo: Union[__builtin__.NoneType, Dict[int, _T]] = ..., _nil = ...) -> _T: ...
def dict_validator(v) -> dict: ...
def display_as_type(v) -> str: ...
def find_validators(type_: type, config: type) -> Generator[Any, __builtin__.NoneType, __builtin__.NoneType]: ...
def is_literal_type(type_) -> bool: ...
def is_new_type(type_) -> bool: ...
def lenient_issubclass(cls, class_or_tuple: Union[type, Tuple[type, ...]]) -> bool: ...
def new_type_supertype(type_) -> Any: ...
def sequence_like(v: type) -> bool: ...
def validate_json(v, config) -> Any: ...
