# (generated with --quick)

import starlette.requests
import starlette.responses
from typing import Any, Awaitable, Callable, Coroutine, MutableMapping, Type, TypeVar

ASGIApp = Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

CENTER_LINE: str
FRAME_TEMPLATE: str
HTMLResponse: Type[starlette.responses.HTMLResponse]
JS: str
LINE: str
PlainTextResponse: Type[starlette.responses.PlainTextResponse]
Request: Type[starlette.requests.Request]
Response: Type[starlette.responses.Response]
STYLES: str
TEMPLATE: str
asyncio: module
html: module
inspect: module
traceback: module
typing: module

T = TypeVar('T')

class ServerErrorMiddleware:
    __doc__: str
    app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
    debug: bool
    handler: Callable
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, app: Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]], handler: Callable = ..., debug: bool = ...) -> None: ...
    def debug_response(self, request: starlette.requests.Request, exc: Exception) -> starlette.responses.Response: ...
    def error_response(self, request: starlette.requests.Request, exc: Exception) -> starlette.responses.Response: ...
    def format_line(self, index: int, line: str, frame_lineno: int, frame_index: int) -> str: ...
    def generate_frame_html(self, frame: inspect.FrameInfo, is_collapsed: bool) -> str: ...
    def generate_html(self, exc: Exception, limit: int = ...) -> str: ...
    def generate_plain_text(self, exc: Exception) -> str: ...

def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> coroutine: ...
