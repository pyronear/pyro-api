# (generated with --quick)

import fastapi.applications
import fastapi.datastructures
import fastapi.exceptions
import fastapi.routing
import starlette.background
import starlette.requests
import starlette.responses
import starlette.websockets
from typing import Any, Callable, Optional, Sequence, Type

APIRouter: Type[fastapi.routing.APIRouter]
BackgroundTasks: Type[starlette.background.BackgroundTasks]
FastAPI: Type[fastapi.applications.FastAPI]
HTTPException: Type[fastapi.exceptions.HTTPException]
Request: Type[starlette.requests.Request]
Response: Type[starlette.responses.Response]
UploadFile: Type[fastapi.datastructures.UploadFile]
WebSocket: Type[starlette.websockets.WebSocket]
WebSocketDisconnect: Type[starlette.websockets.WebSocketDisconnect]
__version__: str
status: module

def Body(default, *, embed: bool = ..., media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...
def Cookie(default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
def Depends(dependency: Optional[Callable] = ..., *, use_cache: bool = ...) -> Any: ...
def File(default, *, media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...
def Form(default, *, media_type: str = ..., alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., **extra) -> Any: ...
def Header(default, *, alias: Optional[str] = ..., convert_underscores: bool = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
def Path(default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
def Query(default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
def Security(dependency: Optional[Callable] = ..., *, scopes: Optional[Sequence[str]] = ..., use_cache: bool = ...) -> Any: ...
