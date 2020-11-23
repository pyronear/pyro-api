# (generated with --quick)

import sqlalchemy.engine.base
import sqlalchemy.engine.threadlocal
from typing import Any, Callable, Dict, NoReturn, Type

base: module
event: module
poollib: module
schema: module
strategies: Dict[Any, EngineStrategy]
threadlocal: module
url: module
util: module

class DefaultEngineStrategy(EngineStrategy):
    __doc__: str
    def create(self, name_or_url, **kwargs) -> Any: ...

class EngineStrategy:
    __doc__: str
    def __init__(self) -> None: ...
    def create(self, *args, **kwargs) -> NoReturn: ...

class MockEngineStrategy(EngineStrategy):
    MockConnection: type
    __doc__: str
    name: str
    def create(self, name_or_url, executor, **kwargs) -> Any: ...

class PlainEngineStrategy(DefaultEngineStrategy):
    __doc__: str
    engine_cls: Type[sqlalchemy.engine.base.Engine]
    name: str

class ThreadLocalEngineStrategy(DefaultEngineStrategy):
    __doc__: str
    engine_cls: Type[sqlalchemy.engine.threadlocal.TLEngine]
    name: str

def attrgetter(*attrs: str) -> Callable[[Any], tuple]: ...
