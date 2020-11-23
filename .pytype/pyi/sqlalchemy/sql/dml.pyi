# (generated with --quick)

import itertools
import sqlalchemy.sql.base
import sqlalchemy.sql.elements
import sqlalchemy.sql.selectable
import sqlalchemy.util._collections
from typing import Any, List, NoReturn, Tuple, Type

ClauseElement: Any
DialectKWArgs: Type[sqlalchemy.sql.base.DialectKWArgs]
Executable: Type[sqlalchemy.sql.base.Executable]
HasCTE: Type[sqlalchemy.sql.selectable.HasCTE]
HasPrefixes: Type[sqlalchemy.sql.selectable.HasPrefixes]
Null: Type[sqlalchemy.sql.elements.Null]
_generative: Any
exc: module
util: module

class Delete(UpdateBase):
    __doc__: str
    __visit_name__: str
    _bind: Any
    _extra_froms: List[nothing]
    _returning: Any
    _whereclause: Any
    table: Any
    where: Any
    def __init__(self, table, whereclause = ..., bind = ..., returning = ..., prefixes = ..., **dialect_kw) -> None: ...
    def _copy_internals(self, clone = ..., **kw) -> None: ...
    def get_children(self, **kwargs) -> tuple: ...

class Insert(ValuesBase):
    __doc__: str
    __visit_name__: str
    _bind: Any
    _has_multi_parameters: Any
    _return_defaults: Any
    _returning: Any
    _supports_multi_parameters: bool
    from_select: Any
    include_insert_from_select_defaults: bool
    inline: Any
    parameters: Any
    select: Any
    select_names: None
    table: Any
    def __init__(self, table, values = ..., inline = ..., bind = ..., prefixes = ..., returning = ..., return_defaults = ..., **dialect_kw) -> None: ...
    def _copy_internals(self, clone = ..., **kw) -> None: ...
    def get_children(self, **kwargs) -> tuple: ...

class Update(ValuesBase):
    __doc__: str
    __visit_name__: str
    _bind: Any
    _extra_froms: List[nothing]
    _has_multi_parameters: Any
    _preserve_parameter_order: Any
    _return_defaults: Any
    _returning: Any
    _whereclause: Any
    inline: Any
    parameters: Any
    table: Any
    where: Any
    def __init__(self, table, whereclause = ..., values = ..., inline = ..., bind = ..., prefixes = ..., returning = ..., return_defaults = ..., preserve_parameter_order = ..., **dialect_kw) -> None: ...
    def _copy_internals(self, clone = ..., **kw) -> None: ...
    def get_children(self, **kwargs) -> tuple: ...

class UpdateBase(sqlalchemy.sql.selectable.HasCTE, sqlalchemy.sql.base.DialectKWArgs, sqlalchemy.sql.selectable.HasPrefixes, sqlalchemy.sql.base.Executable, Any):
    __doc__: str
    __visit_name__: str
    _bind: Any
    _execution_options: Any
    _hints: sqlalchemy.util._collections.immutabledict
    _parameter_ordering: Any
    _prefixes: Tuple[()]
    bind: Any
    named_with_column: bool
    returning: Any
    with_hint: Any
    def _process_colparams(self, parameters) -> Tuple[Any, bool]: ...
    def _set_bind(self, bind) -> None: ...
    def params(self, *arg, **kw) -> NoReturn: ...

class ValuesBase(UpdateBase):
    __doc__: str
    __visit_name__: str
    _has_multi_parameters: Any
    _post_values_clause: None
    _preserve_parameter_order: bool
    _supports_multi_parameters: bool
    parameters: Any
    return_defaults: Any
    select: None
    table: Any
    values: Any
    def __init__(self, table, values, prefixes) -> None: ...

def _clone(element, **kw) -> Any: ...
def _column_as_key(element) -> Any: ...
def _from_objects(*elements) -> itertools.chain[nothing]: ...
def _interpret_as_from(element) -> Any: ...
def _interpret_as_select(element) -> Any: ...
def _literal_as_text(element, allow_coercion_to_text = ...) -> Any: ...
def and_(*clauses) -> Any: ...
