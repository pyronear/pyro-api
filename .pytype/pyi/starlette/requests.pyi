# (generated with --quick)

import starlette.datastructures
import starlette.formparsers
import typing
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Dict, Iterator, MutableMapping, Optional, Set, Tuple, Type

Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

Address: Type[starlette.datastructures.`namedtuple-Address-host-port`]
FormData: Type[starlette.datastructures.FormData]
FormParser: Type[starlette.formparsers.FormParser]
Headers: Type[starlette.datastructures.Headers]
Mapping: Type[typing.Mapping]
MultiPartParser: Type[starlette.formparsers.MultiPartParser]
QueryParams: Type[starlette.datastructures.QueryParams]
SERVER_PUSH_HEADERS_TO_COPY: Set[str]
State: Type[starlette.datastructures.State]
URL: Type[starlette.datastructures.URL]
asyncio: module
http_cookies: module
json: module
parse_options_header: Optional[Callable[[Any], Tuple[Any, Dict[bytes, bytes]]]]
typing: module

class ClientDisconnect(Exception): ...

class HTTPConnection(typing.Mapping):
    __doc__: str
    app: Any
    auth: Any
    base_url: starlette.datastructures.URL
    client: starlette.datastructures.`namedtuple-Address-host-port`
    cookies: Dict[str, str]
    headers: starlette.datastructures.Headers
    path_params: dict
    query_params: starlette.datastructures.QueryParams
    scope: MutableMapping[str, Any]
    session: dict
    state: starlette.datastructures.State
    url: starlette.datastructures.URL
    user: Any
    def __getitem__(self, key: str) -> str: ...
    def __init__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]] = ...) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def url_for(self, name: str, **path_params) -> str: ...

class Request(HTTPConnection):
    _is_disconnected: bool
    _receive: Callable[[], Awaitable[MutableMapping[str, Any]]]
    _send: Callable[[MutableMapping[str, Any]], Awaitable[None]]
    _stream_consumed: bool
    method: str
    receive: Callable[[], Awaitable[MutableMapping[str, Any]]]
    scope: MutableMapping[str, Any]
    def __init__(self, scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]] = ..., send: Callable[[MutableMapping[str, Any]], Awaitable[None]] = ...) -> None: ...
    def body(self) -> Coroutine[Any, Any, bytes]: ...
    def close(self) -> Coroutine[Any, Any, None]: ...
    def form(self) -> Coroutine[Any, Any, starlette.datastructures.FormData]: ...
    def is_disconnected(self) -> Coroutine[Any, Any, bool]: ...
    def json(self) -> coroutine: ...
    def send_push_promise(self, path: str) -> Coroutine[Any, Any, None]: ...
    def stream(self) -> AsyncGenerator[bytes, None]: ...

def cookie_parser(cookie_string: str) -> Dict[str, str]: ...
def empty_receive() -> Coroutine[Any, Any, MutableMapping[str, Any]]: ...
def empty_send(message: MutableMapping[str, Any]) -> Coroutine[Any, Any, None]: ...
