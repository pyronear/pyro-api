# (generated with --quick)

import datetime
import sqlalchemy.sql.base
import sqlalchemy.sql.elements
import sqlalchemy.sql.type_api
from typing import Any, Callable, FrozenSet, Optional, Tuple, Type, TypeVar, Union

INT = INTEGER

BOOLEANTYPE: Boolean
Binary: Any
Emulated: Type[sqlalchemy.sql.type_api.Emulated]
INTEGERTYPE: Integer
MATCHTYPE: MatchType
NO_ARG: Any
NULLTYPE: NullType
NativeForEmulated: Type[sqlalchemy.sql.type_api.NativeForEmulated]
STRINGTYPE: String
SchemaEventTarget: Type[sqlalchemy.sql.base.SchemaEventTarget]
Slice: Type[sqlalchemy.sql.elements.Slice]
TypeDecorator: Type[sqlalchemy.sql.type_api.TypeDecorator]
TypeEngine: Type[sqlalchemy.sql.type_api.TypeEngine]
Variant: Type[sqlalchemy.sql.type_api.Variant]
_defer_name: Type[sqlalchemy.sql.elements._defer_name]
_type_map: dict
array: module
codecs: module
compat: module
decimal: module
dt: module
elements: module
event: module
exc: module
inspection: module
json: module
langhelpers: module
operators: module
pickle: module
processors: module
quoted_name: Type[sqlalchemy.sql.elements.quoted_name]
type_api: module
type_coerce: Type[sqlalchemy.sql.elements.TypeCoerce]
util: module

_T0 = TypeVar('_T0')
_V = TypeVar('_V')
_V2 = TypeVar('_V2')

class ARRAY(sqlalchemy.sql.base.SchemaEventTarget, Indexable, Concatenable, sqlalchemy.sql.type_api.TypeEngine):
    Comparator: type
    __doc__: str
    __visit_name__: str
    as_tuple: Any
    comparator_factory: type
    dimensions: Any
    hashable: Any
    item_type: Any
    python_type: Type[list]
    zero_indexes: Any
    def __init__(self, item_type, as_tuple = ..., dimensions = ..., zero_indexes = ...) -> None: ...
    def _set_parent(self, column) -> None: ...
    def _set_parent_with_dispatch(self, parent) -> None: ...
    def compare_values(self, x, y) -> Any: ...

class BIGINT(BigInteger):
    __doc__: str
    __visit_name__: str

class BINARY(_Binary):
    __doc__: str
    __visit_name__: str
    length: Any

class BLOB(LargeBinary):
    __doc__: str
    __visit_name__: str
    length: Any

class BOOLEAN(Boolean):
    __doc__: str
    __visit_name__: str
    _create_events: Any
    create_constraint: Any
    name: Any

class BigInteger(Integer):
    __doc__: str
    __visit_name__: str

class Boolean(sqlalchemy.sql.type_api.Emulated, sqlalchemy.sql.type_api.TypeEngine, SchemaType):
    __doc__: str
    __visit_name__: str
    _create_events: Any
    _set_table: Any
    _strict_bools: FrozenSet[Optional[bool]]
    create_constraint: Any
    name: Any
    native: bool
    python_type: Type[bool]
    def __init__(self, create_constraint = ..., name = ..., _create_events = ...) -> None: ...
    def _should_create_constraint(self, compiler, **kw) -> Any: ...
    def _strict_as_bool(self, value: _T0) -> _T0: ...
    def bind_processor(self, dialect) -> Callable[[Any], Any]: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Any: ...

class CHAR(String):
    __doc__: str
    __visit_name__: str

class CLOB(Text):
    __doc__: str
    __visit_name__: str

class Concatenable:
    Comparator: type
    __doc__: str
    comparator_factory: type

class DATE(Date):
    __doc__: str
    __visit_name__: str

class DATETIME(DateTime):
    __doc__: str
    __visit_name__: str
    timezone: Any

class DECIMAL(Numeric):
    __doc__: str
    __visit_name__: str
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any
    scale: Any

class Date(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __visit_name__: str
    _expression_adaptations: Any
    python_type: Type[datetime.date]
    def get_dbapi_type(self, dbapi) -> Any: ...

class DateTime(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __visit_name__: str
    _expression_adaptations: Any
    python_type: Type[datetime.datetime]
    timezone: Any
    def __init__(self, timezone = ...) -> None: ...
    def get_dbapi_type(self, dbapi) -> Any: ...

class Enum(sqlalchemy.sql.type_api.Emulated, String, SchemaType):
    Comparator: type
    __doc__: str
    __init__: Any
    __visit_name__: str
    _create_events: Any
    _enums_argument: Any
    _object_lookup: dict
    _set_table: Any
    _sort_key_function: Any
    _valid_lookup: dict
    comparator_factory: type
    create_constraint: Any
    enum_class: Any
    enums: list
    inherit_schema: Any
    metadata: Any
    name: Any
    native: Any
    native_enum: Any
    python_type: Any
    schema: Any
    sort_key_function: Any
    validate_strings: Any
    values_callable: Any
    def __repr__(self) -> Any: ...
    def _db_value_for_elem(self, elem) -> Any: ...
    def _enum_init(self, enums, kw) -> None: ...
    def _object_value_for_elem(self, elem) -> Any: ...
    def _parse_into_values(self, enums, kw) -> Tuple[Any, Any]: ...
    def _setup_for_values(self, values, objects, kw) -> None: ...
    def _should_create_constraint(self, compiler, **kw) -> bool: ...
    def adapt(self, impltype, **kw) -> Any: ...
    def adapt_to_emulated(self, impltype, **kw) -> Any: ...
    def bind_processor(self, dialect) -> Callable[[Any], Any]: ...
    def copy(self, **kw) -> Any: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Callable[[Any], Any]: ...

class FLOAT(Float):
    __doc__: str
    __visit_name__: str
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any

class Float(Numeric):
    __doc__: str
    __visit_name__: str
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any
    scale: None
    def __init__(self, precision = ..., asdecimal = ..., decimal_return_scale = ...) -> None: ...
    def result_processor(self, dialect, coltype) -> Any: ...

class INTEGER(Integer):
    __doc__: str
    __visit_name__: str

class Indexable:
    Comparator: type
    __doc__: str
    comparator_factory: type

class Integer(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __visit_name__: str
    _expression_adaptations: Any
    python_type: Type[int]
    def get_dbapi_type(self, dbapi) -> Any: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...

class Interval(sqlalchemy.sql.type_api.Emulated, _AbstractInterval, sqlalchemy.sql.type_api.TypeDecorator):
    __doc__: str
    day_precision: Any
    epoch: datetime.datetime
    impl: Type[DateTime]
    native: Any
    python_type: Type[datetime.timedelta]
    second_precision: Any
    def __init__(self, native = ..., second_precision = ..., day_precision = ...) -> None: ...
    def adapt_to_emulated(self, impltype, **kw) -> Any: ...
    def bind_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Callable[[Any], Any]: ...

class JSON(Indexable, sqlalchemy.sql.type_api.TypeEngine):
    Comparator: type
    JSONElementType: type
    JSONIndexType: type
    JSONPathType: type
    NULL: Any
    __doc__: str
    __visit_name__: str
    _str_impl: Any
    comparator_factory: type
    hashable: bool
    none_as_null: Any
    python_type: Type[dict]
    should_evaluate_none: bool
    def __init__(self, none_as_null = ...) -> None: ...
    def bind_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Callable[[Any], Any]: ...

class LargeBinary(_Binary):
    __doc__: str
    __visit_name__: str
    length: Any
    def __init__(self, length = ...) -> None: ...

class MatchType(Boolean):
    __doc__: str
    _create_events: Any
    create_constraint: Any
    name: Any

class NCHAR(Unicode):
    __doc__: str
    __visit_name__: str

class NUMERIC(Numeric):
    __doc__: str
    __visit_name__: str
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any
    scale: Any

class NVARCHAR(Unicode):
    __doc__: str
    __visit_name__: str

class NullType(sqlalchemy.sql.type_api.TypeEngine):
    Comparator: type
    __doc__: str
    __visit_name__: str
    _isnull: bool
    comparator_factory: type
    hashable: bool
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...

class Numeric(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __visit_name__: str
    _default_decimal_return_scale: int
    _effective_decimal_return_scale: Any
    _expression_adaptations: Any
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any
    python_type: Type[Union[float, decimal.Decimal]]
    scale: Any
    def __init__(self, precision = ..., scale = ..., decimal_return_scale = ..., asdecimal = ...) -> None: ...
    def bind_processor(self, dialect) -> Any: ...
    def get_dbapi_type(self, dbapi) -> Any: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Any: ...

class PickleType(sqlalchemy.sql.type_api.TypeDecorator):
    __doc__: str
    impl: Type[LargeBinary]
    pickler: Any
    protocol: Any
    def __init__(self, protocol = ..., pickler = ..., comparator = ...) -> None: ...
    def __reduce__(self) -> Tuple[Type[PickleType], Tuple[Any, None, Any]]: ...
    def bind_processor(self, dialect) -> Callable[[Any], Any]: ...
    def comparator(self, _1, _2) -> Any: ...
    def compare_values(self, x, y) -> Any: ...
    def result_processor(self, dialect, coltype) -> Callable[[Any], Any]: ...

class REAL(Float):
    __doc__: str
    __visit_name__: str
    asdecimal: Any
    decimal_return_scale: Any
    precision: Any

class SMALLINT(SmallInteger):
    __doc__: str
    __visit_name__: str

class SchemaType(sqlalchemy.sql.base.SchemaEventTarget):
    __doc__: str
    _create_events: Any
    bind: Any
    inherit_schema: Any
    metadata: Any
    name: Any
    schema: Any
    def __init__(self, name = ..., schema = ..., metadata = ..., inherit_schema = ..., quote = ..., _create_events = ...) -> None: ...
    def _is_impl_for_variant(self, dialect, kw) -> Optional[bool]: ...
    def _on_metadata_create(self, target, bind, **kw) -> None: ...
    def _on_metadata_drop(self, target, bind, **kw) -> None: ...
    def _on_table_create(self, target, bind, **kw) -> None: ...
    def _on_table_drop(self, target, bind, **kw) -> None: ...
    def _set_parent(self, column) -> None: ...
    def _set_table(self, column, table) -> None: ...
    def _translate_schema(self, effective_schema, map_) -> Any: ...
    def _variant_mapping_for_set_table(self, column) -> Any: ...
    def adapt(self, impltype, **kw) -> Any: ...
    def copy(self, **kw) -> Any: ...
    def create(self, bind = ..., checkfirst = ...) -> None: ...
    def drop(self, bind = ..., checkfirst = ...) -> None: ...

class SmallInteger(Integer):
    __doc__: str
    __visit_name__: str

class String(Concatenable, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __init__: Any
    __visit_name__: str
    python_type: Type[str]
    @classmethod
    def _warn_deprecated_unicode(cls) -> None: ...
    def bind_processor(self, dialect) -> Optional[Callable[[Any], Any]]: ...
    def get_dbapi_type(self, dbapi) -> Any: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Any: ...

class TEXT(Text):
    __doc__: str
    __visit_name__: str

class TIME(Time):
    __doc__: str
    __visit_name__: str
    timezone: Any

class TIMESTAMP(DateTime):
    __doc__: str
    __visit_name__: str
    timezone: Any
    def __init__(self, timezone = ...) -> None: ...
    def get_dbapi_type(self, dbapi) -> Any: ...

class Text(String):
    __doc__: str
    __visit_name__: str

class Time(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    __visit_name__: str
    _expression_adaptations: Any
    python_type: Type[datetime.time]
    timezone: Any
    def __init__(self, timezone = ...) -> None: ...
    def get_dbapi_type(self, dbapi) -> Any: ...

class Unicode(String):
    __doc__: str
    __visit_name__: str
    def __init__(self, length = ..., **kwargs) -> None: ...

class UnicodeText(Text):
    __doc__: str
    __visit_name__: str
    def __init__(self, length = ..., **kwargs) -> None: ...
    def _warn_deprecated_unicode(self) -> None: ...

class VARBINARY(_Binary):
    __doc__: str
    __visit_name__: str
    length: Any

class VARCHAR(String):
    __doc__: str
    __visit_name__: str

class _AbstractInterval(_LookupExpressionAdapter, sqlalchemy.sql.type_api.TypeEngine):
    _expression_adaptations: Any
    _type_affinity: Type[Interval]
    def coerce_compared_value(self, op, value) -> Any: ...

class _Binary(sqlalchemy.sql.type_api.TypeEngine):
    __doc__: str
    length: Any
    python_type: Type[bytes]
    def __init__(self, length = ...) -> None: ...
    def bind_processor(self, dialect) -> Optional[Callable[[Any], Any]]: ...
    def coerce_compared_value(self, op, value) -> Any: ...
    def get_dbapi_type(self, dbapi) -> Any: ...
    def literal_processor(self, dialect) -> Callable[[Any], Any]: ...
    def result_processor(self, dialect, coltype) -> Callable[[Any], Any]: ...

class _LookupExpressionAdapter:
    Comparator: type
    __doc__: str
    comparator_factory: type

def _bind_or_error(schemaitem, msg = ...) -> Any: ...
def _literal_as_binds(element, name = ..., type_ = ...) -> Any: ...
def _resolve_value_to_type(value) -> Any: ...
@overload
def _type_map_get(k) -> Optional[_V]: ...
@overload
def _type_map_get(k, d: _V2) -> Union[_V, _V2]: ...
def to_instance(typeobj, *arg, **kw) -> Any: ...
