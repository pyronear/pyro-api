# (generated with --quick)

import collections
import sqlalchemy.sql.base
import sqlalchemy.sql.elements
import sqlalchemy.sql.selectable
import sqlalchemy.sql.sqltypes
import sqlalchemy.sql.visitors
from typing import Any, Dict, List, Tuple, Type, Union

Alias: Type[sqlalchemy.sql.selectable.Alias]
BinaryExpression: Type[sqlalchemy.sql.elements.BinaryExpression]
BindParameter: Type[sqlalchemy.sql.elements.BindParameter]
Cast: Type[sqlalchemy.sql.elements.Cast]
ClauseList: Type[sqlalchemy.sql.elements.ClauseList]
ColumnCollection: Type[sqlalchemy.sql.base.ColumnCollection]
ColumnElement: Type[sqlalchemy.sql.elements.ColumnElement]
Executable: Type[sqlalchemy.sql.base.Executable]
Extract: Type[sqlalchemy.sql.elements.Extract]
FromClause: Type[sqlalchemy.sql.selectable.FromClause]
FunctionFilter: Type[sqlalchemy.sql.elements.FunctionFilter]
Grouping: Type[sqlalchemy.sql.elements.Grouping]
Over: Type[sqlalchemy.sql.elements.Over]
Select: Type[sqlalchemy.sql.selectable.Select]
VisitableType: Type[sqlalchemy.sql.visitors.VisitableType]
WithinGroup: Type[sqlalchemy.sql.elements.WithinGroup]
_CASE_SENSITIVE: Any
_case_sensitive_registry: collections.defaultdict
_registry: collections.defaultdict
annotation: module
func: _FunctionGenerator
modifier: _FunctionGenerator
operators: module
schema: module
sqltypes: module
sqlutil: module
util: module

class AnsiFunction(GenericFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def __init__(self, *args, **kwargs) -> None: ...

class Function(FunctionElement):
    __doc__: str
    __visit_name__: str
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    name: Any
    packagenames: Any
    type: Any
    def __init__(self, name, *clauses, **kw) -> None: ...
    def _bind_param(self, operator, obj, type_ = ...) -> sqlalchemy.sql.elements.BindParameter: ...

class FunctionAsBinary(sqlalchemy.sql.elements.BinaryExpression):
    left: Any
    left_index: Any
    right: Any
    right_index: Any
    sql_function: Any
    def __init__(self, fn, left_index, right_index) -> None: ...
    def _copy_internals(self, **kw) -> None: ...

class FunctionElement(sqlalchemy.sql.base.Executable, sqlalchemy.sql.elements.ColumnElement, sqlalchemy.sql.selectable.FromClause):
    __doc__: str
    _from_objects: Any
    _has_args: bool
    clause_expr: Any
    clauses: Any
    columns: sqlalchemy.sql.base.ColumnCollection
    packagenames: Tuple[()]
    def __init__(self, *clauses, **kwargs) -> None: ...
    def _bind_param(self, operator, obj, type_ = ...) -> sqlalchemy.sql.elements.BindParameter: ...
    def _copy_internals(self, clone = ..., **kw) -> None: ...
    def _execute_on_connection(self, connection, multiparams, params) -> Any: ...
    def alias(self, name = ..., flat = ...) -> Any: ...
    def as_comparison(self, left_index, right_index) -> FunctionAsBinary: ...
    def execute(self) -> Any: ...
    def filter(self, *criterion) -> Union[FunctionElement, sqlalchemy.sql.elements.FunctionFilter]: ...
    def get_children(self, **kwargs) -> Tuple[Any]: ...
    def over(self, partition_by = ..., order_by = ..., rows = ..., range_ = ...) -> sqlalchemy.sql.elements.Over: ...
    def scalar(self) -> Any: ...
    def select(self) -> Any: ...
    def self_group(self, against = ...) -> sqlalchemy.sql.elements.ColumnElement: ...
    def within_group(self, *order_by) -> sqlalchemy.sql.elements.WithinGroup: ...
    def within_group_type(self, within_group) -> None: ...

class GenericFunction(Any):
    __doc__: str
    _bind: Any
    _has_args: Any
    _register: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    coerce_arguments: bool
    packagenames: List[nothing]
    type: Any
    def __init__(self, *args, **kwargs) -> None: ...

class OrderedSetAgg(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    array_for_multi_clause: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def within_group_type(self, within_group) -> Any: ...

class ReturnTypeFromArgs(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def __init__(self, *args, **kwargs) -> None: ...

class _FunctionGenerator:
    _FunctionGenerator__names: list
    __doc__: str
    opts: Dict[str, Any]
    def __call__(self, *c, **kwargs) -> Any: ...
    def __getattr__(self, name) -> Any: ...
    def __init__(self, **opts) -> None: ...

class _GenericMeta(sqlalchemy.sql.visitors.VisitableType):
    _register: Any
    identifier: Any
    name: Any
    type: Any
    def __init__(cls: _GenericMeta, clsname, bases, clsdict) -> None: ...

class array_agg(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def __init__(self, *args, **kwargs) -> None: ...

class char_length(GenericFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def __init__(self, arg, **kwargs) -> None: ...

class coalesce(ReturnTypeFromArgs):
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class concat(GenericFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class count(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any
    def __init__(self, expression = ..., **kwargs) -> None: ...

class cube(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class cume_dist(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class current_date(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class current_time(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class current_timestamp(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class current_user(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class dense_rank(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class grouping_sets(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class localtime(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class localtimestamp(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class max(ReturnTypeFromArgs):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class min(ReturnTypeFromArgs):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class mode(OrderedSetAgg):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class next_value(GenericFunction):
    __doc__: str
    _bind: Any
    _from_objects: List[nothing]
    name: str
    sequence: Any
    type: sqlalchemy.sql.sqltypes.Integer
    def __init__(self, seq, **kw) -> None: ...

class now(GenericFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class percent_rank(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class percentile_cont(OrderedSetAgg):
    __doc__: str
    _bind: Any
    _has_args: Any
    array_for_multi_clause: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class percentile_disc(OrderedSetAgg):
    __doc__: str
    _bind: Any
    _has_args: Any
    array_for_multi_clause: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class random(GenericFunction):
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class rank(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class rollup(GenericFunction):
    __doc__: str
    _bind: Any
    _has_args: bool
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class session_user(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class sum(ReturnTypeFromArgs):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class sysdate(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

class user(AnsiFunction):
    _bind: Any
    _has_args: Any
    clause_expr: Union[sqlalchemy.sql.elements.ClauseList, sqlalchemy.sql.elements.Grouping]
    packagenames: List[nothing]
    type: Any

def _clone(element, **kw) -> Any: ...
def _literal_as_binds(element, name = ..., type_ = ...) -> Any: ...
def _type_from_args(args) -> Any: ...
def literal_column(text, type_ = ...) -> sqlalchemy.sql.elements.ColumnClause: ...
def register_function(identifier, fn, package = ...) -> None: ...
