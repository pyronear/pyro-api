# (generated with --quick)

from typing import Any, Awaitable, Callable, MutableMapping

ASGIApp = Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[None]]], Awaitable[None]]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]
Scope = MutableMapping[str, Any]
Send = Callable[[MutableMapping[str, Any]], Awaitable[None]]

typing: module
