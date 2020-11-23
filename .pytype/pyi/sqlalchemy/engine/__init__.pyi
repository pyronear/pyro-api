# (generated with --quick)

import sqlalchemy.engine.base
import sqlalchemy.engine.interfaces
import sqlalchemy.engine.result
from typing import Any, NoReturn, Tuple, Type

BaseRowProxy: Any
BufferedColumnResultProxy: Type[sqlalchemy.engine.result.BufferedColumnResultProxy]
BufferedColumnRow: Type[sqlalchemy.engine.result.BufferedColumnRow]
BufferedRowResultProxy: Type[sqlalchemy.engine.result.BufferedRowResultProxy]
Compiled: Any
Connectable: Type[sqlalchemy.engine.interfaces.Connectable]
Connection: Type[sqlalchemy.engine.base.Connection]
CreateEnginePlugin: Type[sqlalchemy.engine.interfaces.CreateEnginePlugin]
Dialect: Type[sqlalchemy.engine.interfaces.Dialect]
Engine: Type[sqlalchemy.engine.base.Engine]
ExceptionContext: Type[sqlalchemy.engine.interfaces.ExceptionContext]
ExecutionContext: Type[sqlalchemy.engine.interfaces.ExecutionContext]
FullyBufferedResultProxy: Type[sqlalchemy.engine.result.FullyBufferedResultProxy]
NestedTransaction: Type[sqlalchemy.engine.base.NestedTransaction]
ResultProxy: Type[sqlalchemy.engine.result.ResultProxy]
RootTransaction: Type[sqlalchemy.engine.base.RootTransaction]
RowProxy: Type[sqlalchemy.engine.result.RowProxy]
Transaction: Type[sqlalchemy.engine.base.Transaction]
TwoPhaseTransaction: Type[sqlalchemy.engine.base.TwoPhaseTransaction]
TypeCompiler: Any
__all__: Tuple[str, str]
ddl: module
default_strategy: str
strategies: module
util: module

def connection_memoize(key) -> Any: ...
def create_engine(*args, **kwargs) -> NoReturn: ...
def engine_from_config(configuration, prefix = ..., **kwargs) -> Any: ...
