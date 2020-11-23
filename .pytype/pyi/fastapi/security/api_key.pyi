# (generated with --quick)

import fastapi.openapi.models
import fastapi.security.base
import starlette.exceptions
import starlette.requests
from typing import Any, Coroutine, Optional, Type

APIKey: Type[fastapi.openapi.models.APIKey]
APIKeyIn: Type[fastapi.openapi.models.APIKeyIn]
HTTPException: Type[starlette.exceptions.HTTPException]
HTTP_403_FORBIDDEN: int
Request: Type[starlette.requests.Request]
SecurityBase: Type[fastapi.security.base.SecurityBase]

class APIKeyBase(fastapi.security.base.SecurityBase): ...

class APIKeyCookie(APIKeyBase):
    auto_error: bool
    model: fastapi.openapi.models.APIKey
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, *, name: str, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class APIKeyHeader(APIKeyBase):
    auto_error: bool
    model: fastapi.openapi.models.APIKey
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, *, name: str, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class APIKeyQuery(APIKeyBase):
    auto_error: bool
    model: fastapi.openapi.models.APIKey
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, *, name: str, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...
