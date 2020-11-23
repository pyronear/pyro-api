# (generated with --quick)

from typing import Any, List, Tuple, Type

UnmappedColumnError: None
_version_token: None
compat: module

class AmbiguousForeignKeysError(ArgumentError):
    __doc__: str
    code: Any

class ArgumentError(SQLAlchemyError):
    __doc__: str
    code: Any

class CircularDependencyError(SQLAlchemyError):
    __doc__: str
    code: Any
    cycles: Any
    edges: Any
    def __init__(self, message, cycles, edges, msg = ..., code = ...) -> None: ...
    def __reduce__(self) -> Tuple[Type[CircularDependencyError], Tuple[None, Any, Any, Any]]: ...

class CompileError(SQLAlchemyError):
    __doc__: str
    code: Any

class DBAPIError(StatementError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any
    def __init__(self, statement, params, orig, hide_parameters = ..., connection_invalidated = ..., code = ..., ismulti = ...) -> None: ...
    def __reduce__(self) -> Tuple[Type[DBAPIError], Tuple[Any, Any, Any, Any, Any, Any]]: ...
    @classmethod
    def instance(cls, statement, params, orig, dbapi_base_err, hide_parameters = ..., connection_invalidated = ..., dialect = ..., ismulti = ...) -> Any: ...

class DataError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class DatabaseError(DBAPIError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class DisconnectionError(SQLAlchemyError):
    __doc__: str
    code: Any
    invalidate_pool: bool

class DontWrapMixin:
    __doc__: str

class IdentifierError(SQLAlchemyError):
    __doc__: str
    code: Any

class IntegrityError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class InterfaceError(DBAPIError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class InternalError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class InvalidRequestError(SQLAlchemyError):
    __doc__: str
    code: Any

class InvalidatePoolError(DisconnectionError):
    __doc__: str
    code: Any
    invalidate_pool: bool

class NoForeignKeysError(ArgumentError):
    __doc__: str
    code: Any

class NoInspectionAvailable(InvalidRequestError):
    __doc__: str
    code: Any

class NoReferenceError(InvalidRequestError):
    __doc__: str
    code: Any

class NoReferencedColumnError(NoReferenceError):
    __doc__: str
    column_name: Any
    table_name: Any
    def __init__(self, message, tname, cname) -> None: ...
    def __reduce__(self) -> Tuple[Type[NoReferencedColumnError], Tuple[Any, Any, Any]]: ...

class NoReferencedTableError(NoReferenceError):
    __doc__: str
    table_name: Any
    def __init__(self, message, tname) -> None: ...
    def __reduce__(self) -> Tuple[Type[NoReferencedTableError], Tuple[Any, Any]]: ...

class NoSuchColumnError(KeyError, InvalidRequestError):
    __doc__: str
    code: Any

class NoSuchModuleError(ArgumentError):
    __doc__: str
    code: Any

class NoSuchTableError(InvalidRequestError):
    __doc__: str
    code: Any

class NotSupportedError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class ObjectNotExecutableError(ArgumentError):
    __doc__: str
    def __init__(self, target) -> None: ...

class OperationalError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class ProgrammingError(DatabaseError):
    __doc__: str
    code: Any
    connection_invalidated: Any
    detail: List[nothing]
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any

class ResourceClosedError(InvalidRequestError):
    __doc__: str
    code: Any

class SADeprecationWarning(DeprecationWarning):
    __doc__: str

class SAPendingDeprecationWarning(PendingDeprecationWarning):
    __doc__: str

class SAWarning(RuntimeWarning):
    __doc__: str

class SQLAlchemyError(Exception):
    __doc__: str
    code: Any
    def __init__(self, *arg, **kw) -> None: ...
    def __str__(self) -> Any: ...
    def __unicode__(self) -> Any: ...
    def _code_str(self) -> str: ...
    def _message(self, as_unicode = ...) -> Any: ...
    def _sql_message(self, as_unicode) -> Any: ...

class StatementError(SQLAlchemyError):
    __doc__: str
    code: Any
    detail: list
    hide_parameters: Any
    ismulti: Any
    orig: Any
    params: Any
    statement: Any
    def __init__(self, message, statement, params, orig, hide_parameters = ..., code = ..., ismulti = ...) -> None: ...
    def __reduce__(self) -> Tuple[Type[StatementError], Tuple[Any, Any, Any, Any, Any, Any]]: ...
    def _sql_message(self, as_unicode) -> str: ...
    def add_detail(self, msg) -> None: ...

class TimeoutError(SQLAlchemyError):
    __doc__: str
    code: Any

class UnboundExecutionError(InvalidRequestError):
    __doc__: str
    code: Any

class UnreflectableTableError(InvalidRequestError):
    __doc__: str
    code: Any

class UnsupportedCompilationError(CompileError):
    __doc__: str
    code: str
    def __init__(self, compiler, element_type) -> None: ...
