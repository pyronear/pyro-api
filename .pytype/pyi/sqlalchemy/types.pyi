# (generated with --quick)

import sqlalchemy.sql.sqltypes
import sqlalchemy.sql.type_api
from typing import Any, List, Type

ARRAY: Type[sqlalchemy.sql.sqltypes.ARRAY]
BIGINT: Type[sqlalchemy.sql.sqltypes.BIGINT]
BINARY: Type[sqlalchemy.sql.sqltypes.BINARY]
BLOB: Type[sqlalchemy.sql.sqltypes.BLOB]
BOOLEAN: Type[sqlalchemy.sql.sqltypes.BOOLEAN]
BigInteger: Type[sqlalchemy.sql.sqltypes.BigInteger]
Binary: Any
Boolean: Type[sqlalchemy.sql.sqltypes.Boolean]
CHAR: Type[sqlalchemy.sql.sqltypes.CHAR]
CLOB: Type[sqlalchemy.sql.sqltypes.CLOB]
Concatenable: Type[sqlalchemy.sql.sqltypes.Concatenable]
DATE: Type[sqlalchemy.sql.sqltypes.DATE]
DATETIME: Type[sqlalchemy.sql.sqltypes.DATETIME]
DECIMAL: Type[sqlalchemy.sql.sqltypes.DECIMAL]
Date: Type[sqlalchemy.sql.sqltypes.Date]
DateTime: Type[sqlalchemy.sql.sqltypes.DateTime]
Enum: Type[sqlalchemy.sql.sqltypes.Enum]
FLOAT: Type[sqlalchemy.sql.sqltypes.FLOAT]
Float: Type[sqlalchemy.sql.sqltypes.Float]
INT: Type[sqlalchemy.sql.sqltypes.INTEGER]
INTEGER: Type[sqlalchemy.sql.sqltypes.INTEGER]
Indexable: Type[sqlalchemy.sql.sqltypes.Indexable]
Integer: Type[sqlalchemy.sql.sqltypes.Integer]
Interval: Type[sqlalchemy.sql.sqltypes.Interval]
JSON: Type[sqlalchemy.sql.sqltypes.JSON]
LargeBinary: Type[sqlalchemy.sql.sqltypes.LargeBinary]
MatchType: Type[sqlalchemy.sql.sqltypes.MatchType]
NCHAR: Type[sqlalchemy.sql.sqltypes.NCHAR]
NULLTYPE: sqlalchemy.sql.sqltypes.NullType
NUMERIC: Type[sqlalchemy.sql.sqltypes.NUMERIC]
NVARCHAR: Type[sqlalchemy.sql.sqltypes.NVARCHAR]
NullType: Type[sqlalchemy.sql.sqltypes.NullType]
Numeric: Type[sqlalchemy.sql.sqltypes.Numeric]
PickleType: Type[sqlalchemy.sql.sqltypes.PickleType]
REAL: Type[sqlalchemy.sql.sqltypes.REAL]
SMALLINT: Type[sqlalchemy.sql.sqltypes.SMALLINT]
STRINGTYPE: sqlalchemy.sql.sqltypes.String
SchemaType: Type[sqlalchemy.sql.sqltypes.SchemaType]
SmallInteger: Type[sqlalchemy.sql.sqltypes.SmallInteger]
String: Type[sqlalchemy.sql.sqltypes.String]
TEXT: Type[sqlalchemy.sql.sqltypes.TEXT]
TIME: Type[sqlalchemy.sql.sqltypes.TIME]
TIMESTAMP: Type[sqlalchemy.sql.sqltypes.TIMESTAMP]
Text: Type[sqlalchemy.sql.sqltypes.Text]
Time: Type[sqlalchemy.sql.sqltypes.Time]
TypeDecorator: Type[sqlalchemy.sql.type_api.TypeDecorator]
TypeEngine: Type[sqlalchemy.sql.type_api.TypeEngine]
Unicode: Type[sqlalchemy.sql.sqltypes.Unicode]
UnicodeText: Type[sqlalchemy.sql.sqltypes.UnicodeText]
UserDefinedType: Type[sqlalchemy.sql.type_api.UserDefinedType]
VARBINARY: Type[sqlalchemy.sql.sqltypes.VARBINARY]
VARCHAR: Type[sqlalchemy.sql.sqltypes.VARCHAR]
Variant: Type[sqlalchemy.sql.type_api.Variant]
_Binary: Type[sqlalchemy.sql.sqltypes._Binary]
__all__: List[str]

def adapt_type(typeobj, colspecs) -> Any: ...
def to_instance(typeobj, *arg, **kw) -> Any: ...
