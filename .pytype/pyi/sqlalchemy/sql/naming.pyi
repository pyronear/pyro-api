# (generated with --quick)

import sqlalchemy.sql.elements
import sqlalchemy.sql.schema
from typing import Any, Dict, Type, Union

CheckConstraint: Type[sqlalchemy.sql.schema.CheckConstraint]
Column: Type[sqlalchemy.sql.schema.Column]
Constraint: Type[sqlalchemy.sql.schema.Constraint]
ForeignKeyConstraint: Type[sqlalchemy.sql.schema.ForeignKeyConstraint]
Index: Type[sqlalchemy.sql.schema.Index]
PrimaryKeyConstraint: Type[sqlalchemy.sql.schema.PrimaryKeyConstraint]
Table: Type[sqlalchemy.sql.schema.Table]
UniqueConstraint: Type[sqlalchemy.sql.schema.UniqueConstraint]
_constraint_name: Any
_defer_name: Type[sqlalchemy.sql.elements._defer_name]
_defer_none_name: Type[sqlalchemy.sql.elements._defer_none_name]
_prefix_dict: Dict[Type[Union[sqlalchemy.sql.schema.CheckConstraint, sqlalchemy.sql.schema.ForeignKeyConstraint, sqlalchemy.sql.schema.Index, sqlalchemy.sql.schema.PrimaryKeyConstraint, sqlalchemy.sql.schema.UniqueConstraint]], str]
conv: Type[sqlalchemy.sql.elements.conv]
event: module
events: module
exc: module
re: module

class ConventionDict:
    _const_name: Any
    _is_fk: bool
    const: Any
    convention: Any
    table: Any
    def __getitem__(self, key) -> Any: ...
    def __init__(self, const, table, convention) -> None: ...
    def _column_X(self, idx) -> Any: ...
    def _key_column_X_key(self, idx) -> Any: ...
    def _key_column_X_label(self, idx) -> Any: ...
    def _key_column_X_name(self, idx) -> Any: ...
    def _key_constraint_name(self) -> Any: ...
    def _key_referred_column_X_name(self, idx) -> Any: ...
    def _key_referred_table_name(self) -> Any: ...
    def _key_table_name(self) -> Any: ...

def _constraint_name_for_table(const, table) -> Any: ...
def _get_convention(dict_, key) -> Any: ...
