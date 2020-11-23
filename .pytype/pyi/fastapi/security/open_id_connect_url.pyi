# (generated with --quick)

import fastapi.openapi.models
import fastapi.security.base
import starlette.exceptions
import starlette.requests
from typing import Any, Coroutine, Optional, Type

HTTPException: Type[starlette.exceptions.HTTPException]
HTTP_403_FORBIDDEN: int
OpenIdConnectModel: Type[fastapi.openapi.models.OpenIdConnect]
Request: Type[starlette.requests.Request]
SecurityBase: Type[fastapi.security.base.SecurityBase]

class OpenIdConnect(fastapi.security.base.SecurityBase):
    auto_error: bool
    model: fastapi.openapi.models.OpenIdConnect
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, *, openIdConnectUrl: str, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...
