# (generated with --quick)

import sqlalchemy.pool.base
import sqlalchemy.pool.impl
from typing import Any, List, Type

AssertionPool: Type[sqlalchemy.pool.impl.AssertionPool]
NullPool: Type[sqlalchemy.pool.impl.NullPool]
Pool: Type[sqlalchemy.pool.base.Pool]
QueuePool: Type[sqlalchemy.pool.impl.QueuePool]
SingletonThreadPool: Type[sqlalchemy.pool.impl.SingletonThreadPool]
StaticPool: Type[sqlalchemy.pool.impl.StaticPool]
_ConnectionFairy: Type[sqlalchemy.pool.base._ConnectionFairy]
_ConnectionRecord: Type[sqlalchemy.pool.base._ConnectionRecord]
__all__: List[str]
_refs: set
manage: Any
reset_commit: Any
reset_none: Any
reset_rollback: Any

def _finalize_fairy(connection, connection_record, pool, ref, echo, fairy = ...) -> None: ...
def clear_managers() -> None: ...
