# (generated with --quick)

import fastapi.exceptions
import starlette.exceptions
import starlette.requests
import starlette.responses
from typing import Any, Coroutine, Dict, Optional, Set, Type, Union

HTTPException: Type[starlette.exceptions.HTTPException]
HTTP_422_UNPROCESSABLE_ENTITY: int
JSONResponse: Type[starlette.responses.JSONResponse]
Request: Type[starlette.requests.Request]
RequestValidationError: Type[fastapi.exceptions.RequestValidationError]

def http_exception_handler(request: starlette.requests.Request, exc: starlette.exceptions.HTTPException) -> Coroutine[Any, Any, starlette.responses.JSONResponse]: ...
def jsonable_encoder(obj, include: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., exclude: Optional[Union[Dict[Union[int, str], Any], Set[Union[int, str]]]] = ..., by_alias: bool = ..., exclude_unset: bool = ..., exclude_defaults: bool = ..., exclude_none: bool = ..., custom_encoder: dict = ..., sqlalchemy_safe: bool = ...) -> Any: ...
def request_validation_exception_handler(request: starlette.requests.Request, exc: fastapi.exceptions.RequestValidationError) -> Coroutine[Any, Any, starlette.responses.JSONResponse]: ...
