# (generated with --quick)

import starlette.requests
import starlette.responses
from typing import Any, Awaitable, Callable, Coroutine, MutableMapping, Type

ASGIApp = Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
DispatchFunction = Callable[[starlette.requests.Request, Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]], Awaitable[starlette.responses.Response]]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
RequestResponseEndpoint = Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

Request: Type[starlette.requests.Request]
Response: Type[starlette.responses.Response]
StreamingResponse: Type[starlette.responses.StreamingResponse]
asyncio: module
typing: module

class BaseHTTPMiddleware:
    app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
    dispatch_func: Callable[[starlette.requests.Request, Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]], Awaitable[starlette.responses.Response]]
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]], dispatch: Callable[[starlette.requests.Request, Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]], Awaitable[starlette.responses.Response]] = ...) -> None: ...
    def call_next(self, request: starlette.requests.Request) -> Coroutine[Any, Any, starlette.responses.Response]: ...
    def dispatch(self, request: starlette.requests.Request, call_next: Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]) -> Coroutine[Any, Any, starlette.responses.Response]: ...
