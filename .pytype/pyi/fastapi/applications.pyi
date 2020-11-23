# (generated with --quick)

import fastapi.exceptions
import fastapi.params
import logging
import starlette.applications
import starlette.datastructures
import starlette.exceptions
import starlette.middleware
import starlette.requests
import starlette.responses
import starlette.routing
from typing import Any, Awaitable, Callable, Coroutine, Dict, List, MutableMapping, Optional, Sequence, Set, Type, Union

DictIntStrAny = Dict[Union[int, str], Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]
SetIntStr = Set[Union[int, str]]

AsyncExitStack: Any
BaseRoute: Type[starlette.routing.BaseRoute]
Depends: Type[fastapi.params.Depends]
HTMLResponse: Type[starlette.responses.HTMLResponse]
HTTPException: Type[starlette.exceptions.HTTPException]
JSONResponse: Type[starlette.responses.JSONResponse]
Middleware: Type[starlette.middleware.Middleware]
Request: Type[starlette.requests.Request]
RequestValidationError: Type[fastapi.exceptions.RequestValidationError]
Response: Type[starlette.responses.Response]
Starlette: Type[starlette.applications.Starlette]
State: Type[starlette.datastructures.State]
logger: logging.Logger
routing: Any

class FastAPI(starlette.applications.Starlette):
    _debug: bool
    default_response_class: Type[starlette.responses.Response]
    dependency_overrides: Dict[nothing, nothing]
    description: str
    docs_url: Optional[str]
    exception_handlers: dict
    extra: Dict[str, Any]
    middleware_stack: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
    openapi_schema: None
    openapi_tags: Optional[List[Dict[str, Any]]]
    openapi_url: Optional[str]
    openapi_version: str
    redoc_url: Optional[str]
    root_path: str
    root_path_in_servers: bool
    router: Any
    servers: List[Dict[str, Any]]
    state: starlette.datastructures.State
    swagger_ui_init_oauth: Optional[dict]
    swagger_ui_oauth2_redirect_url: Optional[str]
    title: str
    user_middleware: List[starlette.middleware.Middleware]
    version: str
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, *, debug: bool = ..., routes: Optional[List[starlette.routing.BaseRoute]] = ..., title: str = ..., description: str = ..., version: str = ..., openapi_url: Optional[str] = ..., openapi_tags: Optional[List[Dict[str, Any]]] = ..., servers: Optional[List[Dict[str, Any]]] = ..., default_response_class: Type[starlette.responses.Response] = ..., docs_url: Optional[str] = ..., redoc_url: Optional[str] = ..., swagger_ui_oauth2_redirect_url: Optional[str] = ..., swagger_ui_init_oauth: Optional[dict] = ..., middleware: Optional[Sequence[starlette.middleware.Middleware]] = ..., exception_handlers: Optional[Dict[Union[int, Type[Exception]], Callable]] = ..., on_startup: Optional[Sequence[Callable]] = ..., on_shutdown: Optional[Sequence[Callable]] = ..., openapi_prefix: str = ..., root_path: str = ..., root_path_in_servers: bool = ..., **extra) -> None: ...
    def add_api_route(self, path: str, endpoint: Callable, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., methods: Optional[List[str]] = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ...) -> None: ...
    def add_api_websocket_route(self, path: str, endpoint: Callable, name: Optional[str] = ...) -> None: ...
    def api_route(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., methods: Optional[List[str]] = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ...) -> Callable: ...
    def delete(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def get(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def head(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def include_router(self, router, *, prefix: str = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., default_response_class: Optional[Type[starlette.responses.Response]] = ...) -> None: ...
    def openapi(self) -> dict: ...
    def options(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def patch(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def post(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def put(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def setup(self) -> None: ...
    def trace(self, path: str, *, response_model: Optional[type] = ..., status_code: int = ..., tags: Optional[List[str]] = ..., dependencies: Optional[Sequence[fastapi.params.Depends]] = ..., summary: Optional[str] = ..., description: Optional[str] = ..., response_description: str = ..., responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = ..., deprecated: bool = ..., operation_id: Optional[str] = ..., response_model_include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., response_model_by_alias: bool = ..., response_model_exclude_unset: bool = ..., response_model_exclude_defaults: bool = ..., response_model_exclude_none: bool = ..., include_in_schema: bool = ..., response_class: Optional[Type[starlette.responses.Response]] = ..., name: Optional[str] = ..., callbacks: Optional[list] = ...) -> Callable: ...
    def websocket(self, path: str, name: Optional[str] = ...) -> Callable: ...

def get_openapi(*, title: str, version: str, openapi_version: str = ..., description: Optional[str] = ..., routes: Sequence[starlette.routing.BaseRoute], tags: Optional[List[Dict[str, Any]]] = ..., servers: Optional[List[Dict[str, Any]]] = ...) -> dict: ...
def get_redoc_html(*, openapi_url: str, title: str, redoc_js_url: str = ..., redoc_favicon_url: str = ..., with_google_fonts: bool = ...) -> starlette.responses.HTMLResponse: ...
def get_swagger_ui_html(*, openapi_url: str, title: str, swagger_js_url: str = ..., swagger_css_url: str = ..., swagger_favicon_url: str = ..., oauth2_redirect_url: Optional[str] = ..., init_oauth: Optional[dict] = ...) -> starlette.responses.HTMLResponse: ...
def get_swagger_ui_oauth2_redirect_html() -> starlette.responses.HTMLResponse: ...
def http_exception_handler(request: starlette.requests.Request, exc: starlette.exceptions.HTTPException) -> Coroutine[Any, Any, starlette.responses.JSONResponse]: ...
def request_validation_exception_handler(request: starlette.requests.Request, exc: fastapi.exceptions.RequestValidationError) -> Coroutine[Any, Any, starlette.responses.JSONResponse]: ...
