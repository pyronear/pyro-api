# (generated with --quick)

import fastapi.exceptions
import fastapi.openapi.models
import fastapi.security.base
import starlette.requests
from typing import Any, Coroutine, Optional, Tuple, Type, Union

BaseModel: Any
HTTPBaseModel: Type[fastapi.openapi.models.HTTPBase]
HTTPBearerModel: Type[fastapi.openapi.models.HTTPBearer]
HTTPException: Type[fastapi.exceptions.HTTPException]
HTTP_401_UNAUTHORIZED: int
HTTP_403_FORBIDDEN: int
Request: Type[starlette.requests.Request]
SecurityBase: Type[fastapi.security.base.SecurityBase]
binascii: module

class HTTPAuthorizationCredentials(Any):
    credentials: str
    scheme: str

class HTTPBase(fastapi.security.base.SecurityBase):
    auto_error: bool
    model: fastapi.openapi.models.HTTPBase
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[HTTPAuthorizationCredentials]]: ...
    def __init__(self, *, scheme: str, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class HTTPBasic(HTTPBase):
    auto_error: bool
    model: fastapi.openapi.models.HTTPBase
    realm: Optional[str]
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[HTTPBasicCredentials]]: ...
    def __init__(self, *, scheme_name: Optional[str] = ..., realm: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class HTTPBasicCredentials(Any):
    password: str
    username: str

class HTTPBearer(HTTPBase):
    auto_error: bool
    model: fastapi.openapi.models.HTTPBearer
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[HTTPAuthorizationCredentials]]: ...
    def __init__(self, *, bearerFormat: Optional[str] = ..., scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class HTTPDigest(HTTPBase):
    auto_error: bool
    model: fastapi.openapi.models.HTTPBase
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[HTTPAuthorizationCredentials]]: ...
    def __init__(self, *, scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

def b64decode(s: Union[bytes, str], altchars: Optional[bytes] = ..., validate: bool = ...) -> bytes: ...
def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]: ...
