# (generated with --quick)

import fastapi.exceptions
import fastapi.openapi.models
import fastapi.security.base
import starlette.requests
from typing import Any, Coroutine, List, Optional, Tuple, Type

HTTPException: Type[fastapi.exceptions.HTTPException]
HTTP_401_UNAUTHORIZED: int
HTTP_403_FORBIDDEN: int
OAuth2Model: Type[fastapi.openapi.models.OAuth2]
OAuthFlowsModel: Type[fastapi.openapi.models.OAuthFlows]
Request: Type[starlette.requests.Request]
SecurityBase: Type[fastapi.security.base.SecurityBase]

class OAuth2(fastapi.security.base.SecurityBase):
    auto_error: Optional[bool]
    model: fastapi.openapi.models.OAuth2
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, *, flows: fastapi.openapi.models.OAuthFlows = ..., scheme_name: Optional[str] = ..., auto_error: bool = ...) -> None: ...

class OAuth2AuthorizationCodeBearer(OAuth2):
    auto_error: Optional[bool]
    model: fastapi.openapi.models.OAuth2
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, authorizationUrl: str, tokenUrl: str, refreshUrl: Optional[str] = ..., scheme_name: Optional[str] = ..., scopes: Optional[dict] = ..., auto_error: bool = ...) -> None: ...

class OAuth2PasswordBearer(OAuth2):
    auto_error: Optional[bool]
    model: fastapi.openapi.models.OAuth2
    scheme_name: Any
    def __call__(self, request: starlette.requests.Request) -> Coroutine[Any, Any, Optional[str]]: ...
    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = ..., scopes: Optional[dict] = ..., auto_error: bool = ...) -> None: ...

class OAuth2PasswordRequestForm:
    __doc__: str
    client_id: Optional[str]
    client_secret: Optional[str]
    grant_type: str
    password: str
    scopes: List[str]
    username: str
    def __init__(self, grant_type: str = ..., username: str = ..., password: str = ..., scope: str = ..., client_id: Optional[str] = ..., client_secret: Optional[str] = ...) -> None: ...

class OAuth2PasswordRequestFormStrict(OAuth2PasswordRequestForm):
    __doc__: str
    client_id: Optional[str]
    client_secret: Optional[str]
    grant_type: str
    password: str
    scopes: List[str]
    username: str
    def __init__(self, grant_type: str = ..., username: str = ..., password: str = ..., scope: str = ..., client_id: Optional[str] = ..., client_secret: Optional[str] = ...) -> None: ...

class SecurityScopes:
    scope_str: str
    scopes: List[str]
    def __init__(self, scopes: Optional[List[str]] = ...) -> None: ...

def Form(default, *, media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...
def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]: ...
