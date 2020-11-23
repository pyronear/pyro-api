# (generated with --quick)

import itertools
import sqlalchemy.sql.base
import sqlalchemy.sql.dml
import sqlalchemy.sql.elements
import sqlalchemy.sql.functions
import sqlalchemy.sql.selectable
import sqlalchemy.sql.visitors
import sqlalchemy.util.langhelpers
from typing import Any, Callable, Type, TypeVar, Union

Alias: Type[sqlalchemy.sql.selectable.Alias]
BinaryExpression: Type[sqlalchemy.sql.elements.BinaryExpression]
BindParameter: Type[sqlalchemy.sql.elements.BindParameter]
BooleanClauseList: Type[sqlalchemy.sql.elements.BooleanClauseList]
CTE: Type[sqlalchemy.sql.selectable.CTE]
Case: Type[sqlalchemy.sql.elements.Case]
Cast: Type[sqlalchemy.sql.elements.Cast]
ClauseElement: Type[sqlalchemy.sql.elements.ClauseElement]
ClauseList: Type[sqlalchemy.sql.elements.ClauseList]
CollectionAggregate: Type[sqlalchemy.sql.elements.CollectionAggregate]
ColumnClause: Type[sqlalchemy.sql.elements.ColumnClause]
ColumnCollection: Type[sqlalchemy.sql.base.ColumnCollection]
ColumnElement: Type[sqlalchemy.sql.elements.ColumnElement]
CompoundSelect: Type[sqlalchemy.sql.selectable.CompoundSelect]
Delete: Type[sqlalchemy.sql.dml.Delete]
Executable: Type[sqlalchemy.sql.base.Executable]
Exists: Type[sqlalchemy.sql.selectable.Exists]
Extract: Type[sqlalchemy.sql.elements.Extract]
False_: Type[sqlalchemy.sql.elements.False_]
FromClause: Type[sqlalchemy.sql.selectable.FromClause]
FromGrouping: Type[sqlalchemy.sql.selectable.FromGrouping]
Function: Type[sqlalchemy.sql.functions.Function]
FunctionElement: Type[sqlalchemy.sql.functions.FunctionElement]
FunctionFilter: Type[sqlalchemy.sql.elements.FunctionFilter]
Generative: Type[sqlalchemy.sql.base.Generative]
GenerativeSelect: Type[sqlalchemy.sql.selectable.GenerativeSelect]
Grouping: Type[sqlalchemy.sql.elements.Grouping]
HasCTE: Type[sqlalchemy.sql.selectable.HasCTE]
HasPrefixes: Type[sqlalchemy.sql.selectable.HasPrefixes]
HasSuffixes: Type[sqlalchemy.sql.selectable.HasSuffixes]
Insert: Type[sqlalchemy.sql.dml.Insert]
Join: Type[sqlalchemy.sql.selectable.Join]
Label: Type[sqlalchemy.sql.elements.Label]
Lateral: Type[sqlalchemy.sql.selectable.Lateral]
Null: Type[sqlalchemy.sql.elements.Null]
Over: Type[sqlalchemy.sql.elements.Over]
PARSE_AUTOCOMMIT: Any
ReleaseSavepointClause: Type[sqlalchemy.sql.elements.ReleaseSavepointClause]
RollbackToSavepointClause: Type[sqlalchemy.sql.elements.RollbackToSavepointClause]
SavepointClause: Type[sqlalchemy.sql.elements.SavepointClause]
ScalarSelect: Type[sqlalchemy.sql.selectable.ScalarSelect]
Select: Type[sqlalchemy.sql.selectable.Select]
SelectBase: Type[sqlalchemy.sql.selectable.SelectBase]
Selectable: Type[sqlalchemy.sql.selectable.Selectable]
TableClause: Type[sqlalchemy.sql.selectable.TableClause]
TableSample: Type[sqlalchemy.sql.selectable.TableSample]
TextAsFrom: Type[sqlalchemy.sql.selectable.TextAsFrom]
TextClause: Type[sqlalchemy.sql.elements.TextClause]
True_: Type[sqlalchemy.sql.elements.True_]
Tuple: Type[sqlalchemy.sql.elements.Tuple]
TypeClause: Type[sqlalchemy.sql.elements.TypeClause]
TypeCoerce: Type[sqlalchemy.sql.elements.TypeCoerce]
UnaryExpression: Type[sqlalchemy.sql.elements.UnaryExpression]
Update: Type[sqlalchemy.sql.dml.Update]
UpdateBase: Type[sqlalchemy.sql.dml.UpdateBase]
ValuesBase: Type[sqlalchemy.sql.dml.ValuesBase]
Visitable: Type[sqlalchemy.sql.visitors.Visitable]
WithinGroup: Type[sqlalchemy.sql.elements.WithinGroup]
_BinaryExpression: Type[sqlalchemy.sql.elements.BinaryExpression]
_BindParamClause: Type[sqlalchemy.sql.elements.BindParameter]
_Case: Type[sqlalchemy.sql.elements.Case]
_Cast: Type[sqlalchemy.sql.elements.Cast]
_Executable: Type[sqlalchemy.sql.base.Executable]
_Exists: Type[sqlalchemy.sql.selectable.Exists]
_Extract: Type[sqlalchemy.sql.elements.Extract]
_False: Type[sqlalchemy.sql.elements.False_]
_FromGrouping: Type[sqlalchemy.sql.selectable.FromGrouping]
_Generative: Type[sqlalchemy.sql.base.Generative]
_Grouping: Type[sqlalchemy.sql.elements.Grouping]
_Label: Type[sqlalchemy.sql.elements.Label]
_Null: Type[sqlalchemy.sql.elements.Null]
_Over: Type[sqlalchemy.sql.elements.Over]
_ScalarSelect: Type[sqlalchemy.sql.selectable.ScalarSelect]
_SelectBase: Type[sqlalchemy.sql.selectable.SelectBase]
_TextClause: Type[sqlalchemy.sql.elements.TextClause]
_True: Type[sqlalchemy.sql.elements.True_]
_Tuple: Type[sqlalchemy.sql.elements.Tuple]
_TypeClause: Type[sqlalchemy.sql.elements.TypeClause]
_UnaryExpression: Type[sqlalchemy.sql.elements.UnaryExpression]
__all__: list
_labeled: Any
_truncated_label: Type[sqlalchemy.sql.elements._truncated_label]
alias: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
all_: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
and_: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
any_: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
asc: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
bindparam: Type[Union[sqlalchemy.sql.elements.BindParameter, sqlalchemy.util.langhelpers.symbol]]
case: Type[Union[sqlalchemy.sql.elements.Case, sqlalchemy.util.langhelpers.symbol]]
cast: Type[Union[sqlalchemy.sql.elements.Cast, sqlalchemy.util.langhelpers.symbol]]
column: Type[Union[sqlalchemy.sql.elements.ColumnClause, sqlalchemy.util.langhelpers.symbol]]
cte: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
delete: Type[Union[sqlalchemy.sql.dml.Delete, sqlalchemy.util.langhelpers.symbol]]
desc: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
distinct: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
except_: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
except_all: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
exists: Type[Union[sqlalchemy.sql.selectable.Exists, sqlalchemy.util.langhelpers.symbol]]
extract: Type[Union[sqlalchemy.sql.elements.Extract, sqlalchemy.util.langhelpers.symbol]]
false: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
func: sqlalchemy.sql.functions._FunctionGenerator
funcfilter: Type[Union[sqlalchemy.sql.elements.FunctionFilter, sqlalchemy.util.langhelpers.symbol]]
insert: Type[Union[sqlalchemy.sql.dml.Insert, sqlalchemy.util.langhelpers.symbol]]
intersect: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
intersect_all: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
join: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
label: Type[Union[sqlalchemy.sql.elements.Label, sqlalchemy.util.langhelpers.symbol]]
lateral: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
modifier: sqlalchemy.sql.functions._FunctionGenerator
null: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
nullsfirst: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
nullslast: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
or_: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
outerjoin: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
over: Type[Union[sqlalchemy.sql.elements.Over, sqlalchemy.util.langhelpers.symbol]]
quoted_name: Type[sqlalchemy.sql.elements.quoted_name]
select: Type[Union[sqlalchemy.sql.selectable.Select, sqlalchemy.util.langhelpers.symbol]]
table: Type[Union[sqlalchemy.sql.selectable.TableClause, sqlalchemy.util.langhelpers.symbol]]
tablesample: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
text: Any
true: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
tuple_: Type[Union[sqlalchemy.sql.elements.Tuple, sqlalchemy.util.langhelpers.symbol]]
type_coerce: Type[Union[sqlalchemy.sql.elements.TypeCoerce, sqlalchemy.util.langhelpers.symbol]]
union: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
union_all: Union[Callable, Type[sqlalchemy.util.langhelpers.symbol]]
update: Type[Union[sqlalchemy.sql.dml.Update, sqlalchemy.util.langhelpers.symbol]]
within_group: Type[Union[sqlalchemy.sql.elements.WithinGroup, sqlalchemy.util.langhelpers.symbol]]

_T0 = TypeVar('_T0')

def _clause_element_as_expr(element) -> Any: ...
def _clone(element, **kw) -> Any: ...
def _cloned_difference(a, b) -> set: ...
def _cloned_intersection(a, b) -> set: ...
def _column_as_key(element) -> Any: ...
def _corresponding_column_or_error(fromclause, column, require_embedded = ...) -> Any: ...
def _expression_literal_as_text(element) -> Any: ...
def _from_objects(*elements) -> itertools.chain[nothing]: ...
def _interpret_as_from(element) -> Any: ...
def _is_column(col) -> bool: ...
def _literal_as_binds(element, name = ..., type_ = ...) -> Any: ...
def _literal_as_column(element) -> Any: ...
def _literal_as_label_reference(element) -> Any: ...
def _literal_as_text(element, allow_coercion_to_text = ...) -> Any: ...
def _only_column_elements(element, name) -> Any: ...
def _select_iterables(elements) -> itertools.chain[nothing]: ...
def _string_or_unprintable(element: _T0) -> Union[str, _T0]: ...
def between(expr, lower_bound, upper_bound, symmetric = ...) -> Any: ...
def collate(expression, collation) -> sqlalchemy.sql.elements.BinaryExpression: ...
def literal(value, type_ = ...) -> sqlalchemy.sql.elements.BindParameter: ...
def literal_column(text, type_ = ...) -> sqlalchemy.sql.elements.ColumnClause: ...
def not_(clause) -> Any: ...
def outparam(key, type_ = ...) -> sqlalchemy.sql.elements.BindParameter: ...
def public_factory(target: _T0, location, class_location = ...) -> Union[Type[sqlalchemy.util.langhelpers.symbol], _T0]: ...
def subquery(alias, *args, **kwargs) -> Any: ...
