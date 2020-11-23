# (generated with --quick)

import __builtin__
import abc
import enum
import functools
import inspect
import pathlib
import pydantic.errors
import pydantic.parse
import pydantic.types
import pydantic.utils
import typing
from typing import AbstractSet, Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

ConfigType = Type[BaseConfig]

ABCMeta: Type[abc.ABCMeta]
AbstractSetIntStr: Any
AnyCallable: Type[Callable]
CallableGenerator: Any
ClassAttribute: Type[pydantic.utils.ClassAttribute]
ConfigError: Type[pydantic.errors.ConfigError]
DictAny: Any
DictError: Type[pydantic.errors.DictError]
DictStrAny: Any
EXTRA_LINK: str
Enum: Type[enum.Enum]
ErrorWrapper: Any
ExtraError: Type[pydantic.errors.ExtraError]
ForwardRef: Any
FunctionType: Type[Callable]
GetterDict: Type[pydantic.utils.GetterDict]
MappingIntStrAny: Any
MissingError: Type[pydantic.errors.MissingError]
ModelField: Any
ModelOrDc: Type[type]
Path: Type[pathlib.Path]
Protocol: Type[pydantic.parse.Protocol]
PyObject: Type[pydantic.types.PyObject]
ROOT_KEY: Any
ReprArgs: Any
Representation: Type[pydantic.utils.Representation]
SHAPE_MAPPING: Any
SetStr: Any
Signature: Type[inspect.Signature]
StrBytes: Type[Union[bytes, str]]
TupleGenerator: Any
UNTOUCHED_TYPES: Tuple[Type[Callable], Type[property], Type[type], Type[classmethod], Type[staticmethod]]
Undefined: Any
ValidationError: Any
ValidatorGroup: Any
ValidatorListDict: Any
ValueItems: Type[pydantic.utils.ValueItems]
__all__: Tuple[str, str, str, str, str, str]
_is_base_model_class_defined: bool
_missing: Any
compiled: bool
cython: Any
extract_root_validators: Any
extract_validators: Any
inherit_validators: Any
json: module
partial: Type[functools.partial]
sys: module
typing_extensions: module
warnings: module

Model = TypeVar('Model', bound=BaseModel)
T = TypeVar('T')
_T = TypeVar('_T')

class BaseConfig:
    alias_generator: Optional[Callable[[str], str]]
    allow_mutation: bool
    allow_population_by_field_name: bool
    anystr_strip_whitespace: bool
    arbitrary_types_allowed: bool
    error_msg_templates: Dict[str, str]
    extra: Any
    fields: Dict[str, Union[str, Dict[str, str]]]
    getter_dict: Type[pydantic.utils.GetterDict]
    json_dumps: Callable[..., str]
    json_encoders: Dict[type, Callable]
    json_loads: Callable[[str], Any]
    keep_untouched: Tuple[type, ...]
    max_anystr_length: None
    min_anystr_length: None
    orm_mode: bool
    schema_extra: Union[SchemaExtraCallable, Dict[str, Any]]
    title: None
    use_enum_values: bool
    validate_all: bool
    validate_assignment: bool
    @classmethod
    def get_field_info(cls, name: str) -> Dict[str, Any]: ...
    @classmethod
    def prepare_field(cls, field) -> None: ...

class BaseModel(pydantic.utils.Representation, metaclass=ModelMetaclass):
    __slots__ = ["__dict__", "__fields_set__"]
    Config: Type[BaseConfig]
    __config__: Type[BaseConfig]
    __custom_root_type__: bool
    __dict__: __builtin__.dict
    __doc__: str
    __field_defaults__: __builtin__.dict[str, Any]
    __fields__: __builtin__.dict[str, Any]
    __fields_set__: set
    __json_encoder__: Callable[[Any], Any]
    __post_root_validators__: List[Tuple[bool, Callable]]
    __pre_root_validators__: List[Callable]
    __root__: Any
    __schema_cache__: Any
    __signature__: inspect.Signature
    __validators__: __builtin__.dict[str, Callable]
    __values__: Any
    fields: __builtin__.dict[str, Any]
    def __eq__(self, other) -> bool: ...
    @classmethod
    def __get_validators__(cls) -> Any: ...
    def __getstate__(self) -> Any: ...
    def __init__(__pydantic_self__: BaseModel, **data) -> None: ...
    def __iter__(self) -> Any: ...
    def __repr_args__(self) -> Any: ...
    def __setattr__(self, name, value) -> None: ...
    def __setstate__(self, state) -> None: ...
    def _calculate_keys(self, include, exclude, exclude_unset: bool, update = ...) -> Optional[AbstractSet[str]]: ...
    @classmethod
    def _decompose_class(cls: Type[Model], obj) -> pydantic.utils.GetterDict: ...
    @classmethod
    def _get_value(cls, v, to_dict: bool, by_alias: bool, include, exclude, exclude_unset: bool, exclude_defaults: bool, exclude_none: bool) -> Any: ...
    def _iter(self, to_dict: bool = ..., by_alias: bool = ..., include = ..., exclude = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ...) -> Any: ...
    @classmethod
    def construct(cls: Type[Model], _fields_set = ..., **values) -> Model: ...
    def copy(self: Model, *, include = ..., exclude = ..., update = ..., deep: bool = ...) -> Model: ...
    def dict(self, *, include = ..., exclude = ..., by_alias: bool = ..., skip_defaults: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ...) -> Any: ...
    @classmethod
    def from_orm(cls: Type[Model], obj) -> Model: ...
    def json(self, *, include = ..., exclude = ..., by_alias: bool = ..., skip_defaults: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., encoder: Optional[Callable[[Any], Any]] = ..., **dumps_kwargs) -> str: ...
    @classmethod
    def parse_file(cls: Type[Model], path: Union[str, pathlib.Path], *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ...) -> Model: ...
    @classmethod
    def parse_obj(cls: Type[Model], obj) -> Model: ...
    @classmethod
    def parse_raw(cls: Type[Model], b: Union[bytes, str], *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ...) -> Model: ...
    @classmethod
    def schema(cls, by_alias: bool = ...) -> Any: ...
    @classmethod
    def schema_json(cls, *, by_alias: bool = ..., **dumps_kwargs) -> str: ...
    def to_string(self, pretty: bool = ...) -> str: ...
    @classmethod
    def update_forward_refs(cls, **localns) -> None: ...
    @classmethod
    def validate(cls: Type[Model], value) -> Model: ...

class Extra(str, enum.Enum):
    allow: str
    forbid: str
    ignore: str

class ModelMetaclass(abc.ABCMeta):
    def __new__(mcs: Type[ModelMetaclass], name, bases, namespace, **kwargs) -> Any: ...

class SchemaExtraCallable(typing.Protocol):
    @overload
    def __call__(self, schema: Dict[str, Any]) -> None: ...
    @overload
    def __call__(self, schema: Dict[str, Any], model_class: Type[Model]) -> None: ...

def create_model(__model_name: str, *, __config__: Type[BaseConfig] = ..., __base__: Type[BaseModel] = ..., __module__: Optional[str] = ..., __validators__: Dict[str, classmethod] = ..., **field_definitions) -> Type[BaseModel]: ...
def custom_pydantic_encoder(type_encoders: Dict[Any, Callable[[type], Any]], obj) -> Any: ...
def deepcopy(x: _T, memo: Optional[Dict[int, _T]] = ..., _nil = ...) -> _T: ...
def generate_model_signature(init: Callable[..., None], fields: Dict[str, Any], config: type) -> inspect.Signature: ...
def inherit_config(self_config: Type[BaseConfig], parent_config: Type[BaseConfig]) -> Type[BaseConfig]: ...
def is_classvar(ann_type) -> bool: ...
def is_valid_field(name: str) -> bool: ...
def lenient_issubclass(cls, class_or_tuple: Union[type, Tuple[type, ...]]) -> bool: ...
def load_file(path: Union[str, pathlib.Path], *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ...) -> Any: ...
def load_str_bytes(b, *, content_type: str = ..., encoding: str = ..., proto: pydantic.parse.Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ...) -> Any: ...
def model_schema(model: type, by_alias: bool = ..., ref_prefix: Optional[str] = ...) -> Dict[str, Any]: ...
def prepare_config(config: Type[BaseConfig], cls_name: str) -> None: ...
def pydantic_encoder(obj) -> Any: ...
def resolve_annotations(raw_annotations, module_name) -> Any: ...
def sequence_like(v: type) -> bool: ...
def unique_list(input_list: Union[List[T], Tuple[T, ...]]) -> List[T]: ...
def update_field_forward_refs(field, globalns, localns) -> None: ...
def validate_custom_root_type(fields: Dict[str, Any]) -> None: ...
def validate_field_name(bases: List[type], field_name: str) -> None: ...
def validate_model(model: Type[BaseModel], input_data, cls: type = ...) -> Tuple[Any, Any, Any]: ...
