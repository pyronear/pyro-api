# (generated with --quick)

import sqlalchemy.sql.base
import sqlalchemy.sql.ddl
import sqlalchemy.sql.schema
from typing import Any, Type

AddConstraint: Type[sqlalchemy.sql.ddl.AddConstraint]
BLANK_SCHEMA: Any
CheckConstraint: Type[sqlalchemy.sql.schema.CheckConstraint]
Column: Type[sqlalchemy.sql.schema.Column]
ColumnCollectionConstraint: Type[sqlalchemy.sql.schema.ColumnCollectionConstraint]
ColumnCollectionMixin: Type[sqlalchemy.sql.schema.ColumnCollectionMixin]
ColumnDefault: Type[sqlalchemy.sql.schema.ColumnDefault]
Computed: Type[sqlalchemy.sql.schema.Computed]
Constraint: Type[sqlalchemy.sql.schema.Constraint]
CreateColumn: Type[sqlalchemy.sql.ddl.CreateColumn]
CreateIndex: Type[sqlalchemy.sql.ddl.CreateIndex]
CreateSchema: Type[sqlalchemy.sql.ddl.CreateSchema]
CreateSequence: Type[sqlalchemy.sql.ddl.CreateSequence]
CreateTable: Type[sqlalchemy.sql.ddl.CreateTable]
DDL: Type[sqlalchemy.sql.ddl.DDL]
DDLBase: Type[sqlalchemy.sql.ddl.DDLBase]
DDLElement: Type[sqlalchemy.sql.ddl.DDLElement]
DefaultClause: Type[sqlalchemy.sql.schema.DefaultClause]
DefaultGenerator: Type[sqlalchemy.sql.schema.DefaultGenerator]
DropColumnComment: Type[sqlalchemy.sql.ddl.DropColumnComment]
DropConstraint: Type[sqlalchemy.sql.ddl.DropConstraint]
DropIndex: Type[sqlalchemy.sql.ddl.DropIndex]
DropSchema: Type[sqlalchemy.sql.ddl.DropSchema]
DropSequence: Type[sqlalchemy.sql.ddl.DropSequence]
DropTable: Type[sqlalchemy.sql.ddl.DropTable]
DropTableComment: Type[sqlalchemy.sql.ddl.DropTableComment]
FetchedValue: Any
ForeignKey: Type[sqlalchemy.sql.schema.ForeignKey]
ForeignKeyConstraint: Type[sqlalchemy.sql.schema.ForeignKeyConstraint]
IdentityOptions: Type[sqlalchemy.sql.schema.IdentityOptions]
Index: Type[sqlalchemy.sql.schema.Index]
MetaData: Type[sqlalchemy.sql.schema.MetaData]
PassiveDefault: Any
PrimaryKeyConstraint: Type[sqlalchemy.sql.schema.PrimaryKeyConstraint]
SchemaItem: Any
SchemaVisitor: Type[sqlalchemy.sql.base.SchemaVisitor]
Sequence: Type[sqlalchemy.sql.schema.Sequence]
SetColumnComment: Type[sqlalchemy.sql.ddl.SetColumnComment]
SetTableComment: Type[sqlalchemy.sql.ddl.SetTableComment]
Table: Type[sqlalchemy.sql.schema.Table]
ThreadLocalMetaData: Type[sqlalchemy.sql.schema.ThreadLocalMetaData]
UniqueConstraint: Type[sqlalchemy.sql.schema.UniqueConstraint]
_CreateDropBase: Type[sqlalchemy.sql.ddl._CreateDropBase]
_DDLCompiles: Type[sqlalchemy.sql.ddl._DDLCompiles]
_DropView: Type[sqlalchemy.sql.ddl._DropView]
conv: Any

def _get_table_key(name, schema) -> Any: ...
def sort_tables(tables, skip_fn = ..., extra_dependencies = ...) -> Any: ...
def sort_tables_and_constraints(tables, filter_fn = ..., extra_dependencies = ..., _warn_for_cycles = ...) -> Any: ...
