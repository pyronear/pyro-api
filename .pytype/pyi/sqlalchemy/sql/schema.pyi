# (generated with --quick)

import __future__
import sqlalchemy.sql.base
import sqlalchemy.sql.elements
import sqlalchemy.sql.selectable
import sqlalchemy.sql.visitors
import sqlalchemy.util._collections
from typing import Any, Callable, Dict, Generator, List, NoReturn, Optional, Set, Tuple, Type, TypeVar, Union

BLANK_SCHEMA: Any
ClauseElement: Type[sqlalchemy.sql.elements.ClauseElement]
ColumnClause: Type[sqlalchemy.sql.elements.ColumnClause]
ColumnCollection: Type[sqlalchemy.sql.base.ColumnCollection]
ColumnElement: Type[sqlalchemy.sql.elements.ColumnElement]
DEFAULT_NAMING_CONVENTION: sqlalchemy.util._collections.immutabledict
DialectKWArgs: Type[sqlalchemy.sql.base.DialectKWArgs]
PassiveDefault: Any
RETAIN_SCHEMA: Any
SchemaEventTarget: Type[sqlalchemy.sql.base.SchemaEventTarget]
TableClause: Type[sqlalchemy.sql.selectable.TableClause]
TextClause: Type[sqlalchemy.sql.elements.TextClause]
_default_schema_map: _SchemaTranslateMap
absolute_import: __future__._Feature
collections: module
ddl: module
event: module
exc: module
inspection: module
operator: module
quoted_name: Type[sqlalchemy.sql.elements.quoted_name]
sqlalchemy: module
type_api: module
util: module
visitors: module

_T0 = TypeVar('_T0')
_TComputed = TypeVar('_TComputed', bound=Computed)
_TFetchedValue = TypeVar('_TFetchedValue', bound=FetchedValue)
_TIndex = TypeVar('_TIndex', bound=Index)

class CheckConstraint(ColumnCollectionConstraint):
    __doc__: str
    __init__: Any
    __visit_name__: str
    _allow_multiple_tables: bool
    def copy(self, target_table = ..., **kw) -> Any: ...

class Column(sqlalchemy.sql.base.DialectKWArgs, SchemaItem, sqlalchemy.sql.elements.ColumnClause):
    __doc__: str
    __visit_name__: str
    _proxies: Any
    autoincrement: Any
    comment: Any
    computed: None
    constraints: Set[nothing]
    default: Any
    doc: Any
    foreign_keys: Set[nothing]
    index: Any
    info: Any
    key: Any
    nullable: Any
    onupdate: Any
    primary_key: Any
    server_default: Any
    server_onupdate: Any
    system: Any
    table: Any
    unique: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> Any: ...
    def _extra_kwargs(self, **kwargs) -> None: ...
    def _make_proxy(self, selectable, name = ..., key = ..., name_is_truncatable = ..., **kw) -> Any: ...
    def _on_table_attach(self, fn) -> None: ...
    def _set_parent(self, table) -> None: ...
    def _setup_on_memoized_fks(self, fn) -> None: ...
    def append_foreign_key(self, fk) -> None: ...
    def copy(self, **kw) -> Any: ...
    def get_children(self, schema_visitor = ..., **kwargs) -> Any: ...
    def references(self, column) -> bool: ...

class ColumnCollectionConstraint(ColumnCollectionMixin, Constraint):
    __doc__: str
    _column_flag: Any
    _create_rule: None
    _pending_colargs: Any
    _type_bound: bool
    columns: Optional[sqlalchemy.sql.base.ColumnCollection]
    deferrable: None
    initially: None
    name: None
    def __contains__(self, x) -> bool: ...
    def __init__(self, *columns, **kw) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def _set_parent(self, table) -> None: ...
    def contains_column(self, col) -> bool: ...
    def copy(self, **kw) -> Any: ...

class ColumnCollectionMixin:
    _allow_multiple_tables: bool
    _cols_wo_table: set
    _column_flag: Any
    _pending_colargs: Any
    columns: Optional[sqlalchemy.sql.base.ColumnCollection]
    def __init__(self, *columns, **kw) -> None: ...
    def _check_attach(self, evt = ...) -> None: ...
    def _col_expressions(self, table) -> Any: ...
    @classmethod
    def _extract_col_expression_collection(cls, expressions) -> Generator[Tuple[Any, None, Any, Any], Any, None]: ...
    def _set_parent(self, table) -> None: ...

class ColumnDefault(DefaultGenerator):
    __doc__: str
    __visit_name__: str
    _arg_is_typed: Any
    arg: Any
    for_update: bool
    is_callable: Any
    is_clause_element: Any
    is_scalar: Any
    def __init__(self, arg, **kwargs) -> None: ...
    def __repr__(self) -> str: ...
    def _maybe_wrap_callable(self, fn) -> Any: ...
    def _visit_name(self) -> str: ...

class Computed(FetchedValue, SchemaItem):
    __doc__: str
    __init__: Any
    __visit_name__: str
    column: Any
    def _as_for_update(self: _TComputed, for_update) -> _TComputed: ...
    def _set_parent(self, parent) -> None: ...
    def copy(self, target_table = ..., **kw) -> Any: ...

class Constraint(sqlalchemy.sql.base.DialectKWArgs, SchemaItem):
    __doc__: str
    __visit_name__: str
    _create_rule: Any
    _type_bound: Any
    deferrable: Any
    info: Any
    initially: Any
    name: Any
    parent: Any
    table: Any
    def __init__(self, name = ..., deferrable = ..., initially = ..., _create_rule = ..., info = ..., _type_bound = ..., **dialect_kw) -> None: ...
    def _set_parent(self, parent) -> None: ...
    def copy(self, **kw) -> NoReturn: ...

class DefaultClause(FetchedValue):
    __doc__: str
    arg: Any
    for_update: Any
    has_argument: bool
    reflected: Any
    def __init__(self, arg, for_update = ..., _reflected = ...) -> None: ...
    def __repr__(self) -> str: ...

class DefaultGenerator(_NotAColumnExpr, SchemaItem):
    __doc__: str
    __visit_name__: str
    bind: Any
    column: Any
    for_update: Any
    is_sequence: bool
    is_server_default: bool
    def __init__(self, for_update = ...) -> None: ...
    def _execute_on_connection(self, connection, multiparams, params) -> Any: ...
    def _set_parent(self, column) -> None: ...
    def execute(self, bind = ..., **kwargs) -> Any: ...

class FetchedValue(_NotAColumnExpr, sqlalchemy.sql.base.SchemaEventTarget):
    __doc__: str
    column: Any
    for_update: Any
    has_argument: bool
    is_server_default: bool
    reflected: bool
    def __init__(self, for_update = ...) -> None: ...
    def __repr__(self) -> Any: ...
    def _as_for_update(self, for_update) -> Any: ...
    def _clone(self: _TFetchedValue, for_update) -> _TFetchedValue: ...
    def _set_parent(self, column) -> None: ...

class ForeignKey(sqlalchemy.sql.base.DialectKWArgs, SchemaItem):
    __doc__: str
    __visit_name__: str
    _colspec: Any
    _column_tokens: Any
    _referred_schema: Any
    _table_column: Any
    _unvalidated_dialect_kw: dict
    column: Any
    constraint: Any
    deferrable: Any
    info: Any
    initially: Any
    link_to_name: Any
    match: Any
    name: Any
    ondelete: Any
    onupdate: Any
    parent: Any
    target_fullname: Any
    use_alter: Any
    def __init__(self, column, _constraint = ..., use_alter = ..., name = ..., onupdate = ..., ondelete = ..., deferrable = ..., initially = ..., link_to_name = ..., match = ..., info = ..., **dialect_kw) -> None: ...
    def __repr__(self) -> str: ...
    def _get_colspec(self, schema = ..., table_name = ...) -> Any: ...
    def _link_to_col_by_colstring(self, parenttable, table, colname) -> None: ...
    def _remove_from_metadata(self, metadata) -> None: ...
    def _resolve_col_tokens(self) -> Tuple[Any, Any, Any]: ...
    def _set_parent(self, column) -> None: ...
    def _set_remote_table(self, table) -> None: ...
    def _set_table(self, column, table) -> None: ...
    def _set_target_column(self, column) -> None: ...
    def _table_key(self) -> Any: ...
    def copy(self, schema = ...) -> Any: ...
    def get_referent(self, table) -> Any: ...
    def references(self, table) -> bool: ...

class ForeignKeyConstraint(ColumnCollectionConstraint):
    __doc__: str
    __visit_name__: str
    _col_description: str
    _column_flag: bool
    _create_rule: None
    _elements: sqlalchemy.util._collections.OrderedDict
    _pending_colargs: Any
    _referred_schema: Any
    _type_bound: bool
    column_keys: Any
    columns: Optional[sqlalchemy.sql.base.ColumnCollection]
    deferrable: Any
    elements: Any
    info: Any
    initially: Any
    link_to_name: Any
    match: Any
    name: Any
    ondelete: Any
    onupdate: Any
    referred_table: Any
    use_alter: Any
    def __init__(self, columns, refcolumns, name = ..., onupdate = ..., ondelete = ..., deferrable = ..., initially = ..., use_alter = ..., link_to_name = ..., match = ..., table = ..., info = ..., **dialect_kw) -> None: ...
    def _append_element(self, column, fk) -> None: ...
    def _set_parent(self, table) -> None: ...
    def _validate_dest_table(self, table) -> None: ...
    def copy(self, schema = ..., target_table = ..., **kw) -> Any: ...

class IdentityOptions:
    __doc__: str
    cache: Any
    cycle: Any
    increment: Any
    maxvalue: Any
    minvalue: Any
    nomaxvalue: Any
    nominvalue: Any
    order: Any
    start: Any
    def __init__(self, start = ..., increment = ..., minvalue = ..., maxvalue = ..., nominvalue = ..., nomaxvalue = ..., cycle = ..., cache = ..., order = ...) -> None: ...

class Index(sqlalchemy.sql.base.DialectKWArgs, ColumnCollectionMixin, SchemaItem):
    __doc__: str
    __visit_name__: str
    _column_flag: Any
    _pending_colargs: Any
    bind: Any
    columns: sqlalchemy.sql.base.ColumnCollection
    expressions: Any
    info: Any
    name: Any
    table: Any
    unique: Any
    def __init__(self, name, *expressions, **kw) -> None: ...
    def __repr__(self) -> str: ...
    def _set_parent(self, table) -> None: ...
    def create(self: _TIndex, bind = ...) -> _TIndex: ...
    def drop(self, bind = ...) -> None: ...

class MetaData(SchemaItem):
    __doc__: str
    __init__: Any
    __visit_name__: str
    _bind: None
    _bind_to: Any
    _fk_memos: Any
    _schemas: Any
    _sequences: Any
    append_ddl_listener: Any
    bind: Any
    naming_convention: Any
    schema: Any
    sorted_tables: Any
    tables: Any
    def __contains__(self, table_or_key) -> bool: ...
    def __getstate__(self) -> Dict[str, Any]: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state) -> None: ...
    def _add_table(self, name, schema, table) -> None: ...
    def _remove_table(self, name, schema) -> None: ...
    def clear(self) -> None: ...
    def create_all(self, bind = ..., tables = ..., checkfirst = ...) -> None: ...
    def drop_all(self, bind = ..., tables = ..., checkfirst = ...) -> None: ...
    def is_bound(self) -> bool: ...
    def reflect(self, bind = ..., schema = ..., views = ..., only = ..., extend_existing = ..., autoload_replace = ..., resolve_fks = ..., **dialect_kwargs) -> None: ...
    def remove(self, table) -> None: ...

class PrimaryKeyConstraint(ColumnCollectionConstraint):
    __doc__: str
    __visit_name__: str
    _autoincrement_column: Any
    _column_flag: Any
    _create_rule: None
    _implicit_generated: Any
    _pending_colargs: Any
    _type_bound: bool
    columns: sqlalchemy.sql.base.ColumnCollection
    columns_autoinc_first: list
    deferrable: None
    initially: None
    name: None
    def __init__(self, *columns, **kw) -> None: ...
    def _reload(self, columns) -> None: ...
    def _replace(self, col) -> None: ...
    def _set_parent(self, table) -> None: ...

class SchemaItem(sqlalchemy.sql.base.SchemaEventTarget, sqlalchemy.sql.visitors.Visitable):
    __doc__: str
    __visit_name__: str
    info: Any
    quote: Any
    def __repr__(self) -> Any: ...
    def _init_items(self, *args) -> None: ...
    def _schema_item_copy(self, schema_item: _T0) -> _T0: ...
    def _translate_schema(self, effective_schema, map_) -> Any: ...
    def get_children(self, **kwargs) -> List[nothing]: ...

class Sequence(IdentityOptions, DefaultGenerator):
    __doc__: str
    __visit_name__: str
    _key: Any
    bind: Any
    cache: Any
    cycle: Any
    for_update: Any
    increment: Any
    is_callable: Any
    is_clause_element: Any
    is_sequence: bool
    maxvalue: Any
    metadata: Any
    minvalue: Any
    name: Any
    next_value: Any
    nomaxvalue: Any
    nominvalue: Any
    optional: Any
    order: Any
    schema: Any
    start: Any
    def __init__(self, name, start = ..., increment = ..., minvalue = ..., maxvalue = ..., nominvalue = ..., nomaxvalue = ..., cycle = ..., schema = ..., cache = ..., order = ..., optional = ..., quote = ..., metadata = ..., quote_schema = ..., for_update = ...) -> None: ...
    def _not_a_column_expr(self) -> NoReturn: ...
    def _set_metadata(self, metadata) -> None: ...
    def _set_parent(self, column) -> None: ...
    def _set_table(self, column, table) -> None: ...
    def create(self, bind = ..., checkfirst = ...) -> None: ...
    def drop(self, bind = ..., checkfirst = ...) -> None: ...

class Table(sqlalchemy.sql.base.DialectKWArgs, SchemaItem, sqlalchemy.sql.selectable.TableClause):
    __doc__: str
    __new__: Any
    __visit_name__: str
    _autoincrement_column: Any
    _columns: sqlalchemy.sql.base.ColumnCollection
    _extra_dependencies: set
    _prefixes: Any
    _sorted_constraints: list
    append_ddl_listener: Any
    bind: Any
    comment: Any
    constraints: Set[nothing]
    foreign_key_constraints: set
    foreign_keys: Set[nothing]
    fullname: Any
    implicit_returning: Any
    indexes: Set[nothing]
    info: Any
    key: Any
    metadata: Any
    quote_schema: Any
    schema: Any
    def __init__(self, *args, **kw) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> Any: ...
    def _autoload(self, metadata, autoload_with, include_columns, exclude_columns = ..., resolve_fks = ..., _extend_on = ...) -> None: ...
    def _extra_kwargs(self, **kwargs) -> None: ...
    def _init(self, name, metadata, *args, **kwargs) -> None: ...
    def _init_collections(self) -> None: ...
    def _init_existing(self, *args, **kwargs) -> None: ...
    def _reset_exported(self) -> None: ...
    def _set_parent(self, metadata) -> None: ...
    def add_is_dependent_on(self, table) -> None: ...
    def append_column(self, column) -> None: ...
    def append_constraint(self, constraint) -> None: ...
    def create(self, bind = ..., checkfirst = ...) -> None: ...
    def drop(self, bind = ..., checkfirst = ...) -> None: ...
    def exists(self, bind = ...) -> Any: ...
    def get_children(self, column_collections = ..., schema_visitor = ..., **kw) -> Any: ...
    def tometadata(self, metadata, schema = ..., referred_schema_fn = ..., name = ...) -> Any: ...

class ThreadLocalMetaData(MetaData):
    _ThreadLocalMetaData__engines: Dict[nothing, nothing]
    __doc__: str
    __visit_name__: str
    _bind_to: Any
    bind: Any
    context: Any
    def __init__(self) -> None: ...
    def dispose(self) -> None: ...
    def is_bound(self) -> bool: ...

class UniqueConstraint(ColumnCollectionConstraint):
    __doc__: str
    __visit_name__: str
    _column_flag: Any
    _create_rule: None
    _pending_colargs: Any
    _type_bound: bool
    columns: sqlalchemy.sql.base.ColumnCollection
    deferrable: None
    initially: None
    name: None

class _NotAColumnExpr:
    _from_objects: Any
    def __clause_element__(self) -> Any: ...
    def _not_a_column_expr(self) -> NoReturn: ...
    def self_group(self) -> Any: ...

class _SchemaTranslateMap:
    __slots__ = ["__call__", "hash_key", "is_default", "map_"]
    __call__: Callable[[Any], Any]
    __doc__: str
    _default_schema_getter: Callable[[Any], Any]
    hash_key: Union[int, str]
    is_default: bool
    map_: Any
    def __init__(self, map_) -> None: ...
    @classmethod
    def _schema_getter(cls, map_: _T0) -> Union[_SchemaTranslateMap, _T0]: ...

def _as_truncated(value) -> Any: ...
def _bind_or_error(schemaitem, msg = ...) -> Any: ...
def _copy_expression(expression, source_table, target_table) -> Any: ...
def _document_text_coercion(paramname, meth_rst, param_rst) -> Any: ...
def _get_table_key(name, schema) -> Any: ...
def _literal_as_text(element, allow_coercion_to_text = ...) -> Any: ...
def _schema_getter(map_: _T0) -> Union[_SchemaTranslateMap, _T0]: ...
def _to_schema_column(element) -> Any: ...
def _to_schema_column_or_string(element) -> Any: ...
