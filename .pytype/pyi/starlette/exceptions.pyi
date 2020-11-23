# (generated with --quick)

import starlette.requests
import starlette.responses
from typing import Any, Awaitable, Callable, Coroutine, Dict, MutableMapping, Optional, Type, TypeVar, Union

ASGIApp = Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

PlainTextResponse: Type[starlette.responses.PlainTextResponse]
Request: Type[starlette.requests.Request]
Response: Type[starlette.responses.Response]
asyncio: module
http: module
typing: module

T = TypeVar('T')

class ExceptionMiddleware:
    _exception_handlers: Dict[Type[Exception], Callable]
    _status_handlers: Dict[int, Callable]
    app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
    debug: bool
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]], handlers: dict = ..., debug: bool = ...) -> None: ...
    def _lookup_exception_handler(self, exc: Exception) -> Optional[Callable]: ...
    def add_exception_handler(self, exc_class_or_status_code: Union[int, Type[Exception]], handler: Callable) -> None: ...
    def http_exception(self, request: starlette.requests.Request, exc: HTTPException) -> starlette.responses.Response: ...

class HTTPException(Exception):
    detail: str
    status_code: int
    def __init__(self, status_code: int, detail: str = ...) -> None: ...
    def __repr__(self) -> str: ...

def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> coroutine: ...
