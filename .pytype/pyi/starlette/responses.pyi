# (generated with --quick)

import starlette.background
import starlette.datastructures
from typing import Any, Awaitable, Callable, Coroutine, Iterator, Mapping, MutableMapping, Optional, Tuple, Type, Union

Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

BackgroundTask: Type[starlette.background.BackgroundTask]
MutableHeaders: Type[starlette.datastructures.MutableHeaders]
URL: Type[starlette.datastructures.URL]
aio_stat: Any
aiofiles: Any
hashlib: module
http: module
inspect: module
json: module
os: module
stat: module
typing: module
ujson: Optional[module]

class FileResponse(Response):
    background: starlette.background.BackgroundTask
    chunk_size: int
    filename: str
    media_type: str
    path: str
    send_header_only: bool
    stat_result: os.stat_result
    status_code: int
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, path: str, status_code: int = ..., headers: dict = ..., media_type: str = ..., background: starlette.background.BackgroundTask = ..., filename: str = ..., stat_result: os.stat_result = ..., method: str = ...) -> None: ...
    def set_stat_headers(self, stat_result: os.stat_result) -> None: ...

class HTMLResponse(Response):
    background: starlette.background.BackgroundTask
    body: Any
    media_type: str
    status_code: int

class JSONResponse(Response):
    background: starlette.background.BackgroundTask
    body: Any
    media_type: str
    status_code: int
    def render(self, content) -> bytes: ...

class PlainTextResponse(Response):
    background: starlette.background.BackgroundTask
    body: Any
    media_type: str
    status_code: int

class RedirectResponse(Response):
    background: starlette.background.BackgroundTask
    body: Any
    media_type: str
    status_code: int
    def __init__(self, url: Union[str, starlette.datastructures.URL], status_code: int = ..., headers: dict = ..., background: starlette.background.BackgroundTask = ...) -> None: ...

class Response:
    background: starlette.background.BackgroundTask
    body: Any
    charset: str
    headers: starlette.datastructures.MutableHeaders
    media_type: Optional[str]
    status_code: int
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, content = ..., status_code: int = ..., headers: dict = ..., media_type: str = ..., background: starlette.background.BackgroundTask = ...) -> None: ...
    def delete_cookie(self, key: str, path: str = ..., domain: str = ...) -> None: ...
    def init_headers(self, headers: Mapping[str, str] = ...) -> None: ...
    def render(self, content) -> bytes: ...
    def set_cookie(self, key: str, value: str = ..., max_age: int = ..., expires: int = ..., path: str = ..., domain: str = ..., secure: bool = ..., httponly: bool = ..., samesite: str = ...) -> None: ...

class StreamingResponse(Response):
    background: starlette.background.BackgroundTask
    body_iterator: Any
    media_type: str
    status_code: int
    def __call__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...
    def __init__(self, content, status_code: int = ..., headers: dict = ..., media_type: str = ..., background: starlette.background.BackgroundTask = ...) -> None: ...
    def listen_for_disconnect(self, receive: Callable[[], Awaitable[MutableMapping[str, Any]]]) -> Coroutine[Any, Any, None]: ...
    def stream_response(self, send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> Coroutine[Any, Any, None]: ...

class UJSONResponse(JSONResponse):
    background: starlette.background.BackgroundTask
    body: Any
    media_type: str
    status_code: int
    def render(self, content) -> bytes: ...

def formatdate(timeval: Optional[float] = ..., localtime: bool = ..., usegmt: bool = ...) -> str: ...
def guess_type(url: Union[str, _PathLike[str]], strict: bool = ...) -> Tuple[Optional[str], Optional[str]]: ...
def iterate_in_threadpool(iterator: Iterator) -> asyncgenerator: ...
@overload
def quote(string: str, safe: Union[bytes, str] = ..., encoding: Optional[str] = ..., errors: Optional[str] = ...) -> str: ...
@overload
def quote(string: bytes, safe: Union[bytes, str] = ...) -> str: ...
@overload
def quote_plus(string: str, safe: Union[bytes, str] = ..., encoding: Optional[str] = ..., errors: Optional[str] = ...) -> str: ...
@overload
def quote_plus(string: bytes, safe: Union[bytes, str] = ...) -> str: ...
def run_until_first_complete(*args: Tuple[Callable, dict]) -> Coroutine[Any, Any, None]: ...
