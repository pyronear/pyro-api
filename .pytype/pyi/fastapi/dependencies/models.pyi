# (generated with --quick)

import fastapi.security.base
import pydantic.fields
from typing import Any, Callable, List, Optional, Sequence, Tuple, Type

ModelField: Type[pydantic.fields.ModelField]
SecurityBase: Type[fastapi.security.base.SecurityBase]
param_supported_types: Tuple[Type[str], Type[int], Type[float], Type[bool]]

class Dependant:
    background_tasks_param_name: Any
    body_params: List[pydantic.fields.ModelField]
    cache_key: Tuple[Any, tuple]
    call: Any
    cookie_params: List[pydantic.fields.ModelField]
    dependencies: List[Dependant]
    header_params: List[pydantic.fields.ModelField]
    http_connection_param_name: Any
    name: Any
    path: Any
    path_params: List[pydantic.fields.ModelField]
    query_params: List[pydantic.fields.ModelField]
    request_param_name: Any
    response_param_name: Any
    security_requirements: Any
    security_scopes: Any
    security_scopes_param_name: Any
    use_cache: bool
    websocket_param_name: Any
    def __init__(self, *, path_params: Optional[List[pydantic.fields.ModelField]] = ..., query_params: Optional[List[pydantic.fields.ModelField]] = ..., header_params: Optional[List[pydantic.fields.ModelField]] = ..., cookie_params: Optional[List[pydantic.fields.ModelField]] = ..., body_params: Optional[List[pydantic.fields.ModelField]] = ..., dependencies: Optional[List[Dependant]] = ..., security_schemes: Optional[List[SecurityRequirement]] = ..., name: Optional[str] = ..., call: Optional[Callable] = ..., request_param_name: Optional[str] = ..., websocket_param_name: Optional[str] = ..., http_connection_param_name: Optional[str] = ..., response_param_name: Optional[str] = ..., background_tasks_param_name: Optional[str] = ..., security_scopes_param_name: Optional[str] = ..., security_scopes: Optional[List[str]] = ..., use_cache: bool = ..., path: Optional[str] = ...) -> None: ...

class SecurityRequirement:
    scopes: Any
    security_scheme: fastapi.security.base.SecurityBase
    def __init__(self, security_scheme: fastapi.security.base.SecurityBase, scopes: Optional[Sequence[str]] = ...) -> None: ...
