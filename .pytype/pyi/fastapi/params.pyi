# (generated with --quick)

import enum
import pydantic.fields
from typing import Any, Callable, List, Optional, Sequence, Type, Union

Enum: Type[enum.Enum]
FieldInfo: Type[pydantic.fields.FieldInfo]

class Body(pydantic.fields.FieldInfo):
    embed: bool
    media_type: str
    def __init__(self, default, *, embed: bool = ..., media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...
    def __repr__(self) -> str: ...

class Cookie(Param):
    deprecated: Optional[bool]
    in_: Any
    def __init__(self, default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...

class Depends:
    dependency: Optional[Callable]
    use_cache: bool
    def __init__(self, dependency: Optional[Callable] = ..., *, use_cache: bool = ...) -> None: ...
    def __repr__(self) -> str: ...

class File(Form):
    embed: bool
    media_type: str
    def __init__(self, default, *, media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...

class Form(Body):
    embed: bool
    media_type: str
    def __init__(self, default, *, media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...

class Header(Param):
    convert_underscores: bool
    deprecated: Optional[bool]
    in_: Any
    def __init__(self, default, *, alias: Optional[str] = ..., convert_underscores: bool = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...

class Param(pydantic.fields.FieldInfo):
    deprecated: Optional[bool]
    in_: ParamTypes
    def __init__(self, default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
    def __repr__(self) -> str: ...

class ParamTypes(enum.Enum):
    cookie: str
    header: str
    path: str
    query: str

class Path(Param):
    deprecated: Optional[bool]
    in_: Any
    def __init__(self, default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...

class Query(Param):
    deprecated: Optional[bool]
    in_: Any
    def __init__(self, default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...

class Security(Depends):
    dependency: Optional[Callable]
    scopes: Union[List[nothing], Sequence[str]]
    use_cache: bool
    def __init__(self, dependency: Optional[Callable] = ..., *, scopes: Optional[Sequence[str]] = ..., use_cache: bool = ...) -> None: ...
