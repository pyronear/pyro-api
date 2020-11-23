# (generated with --quick)

import pydantic.error_wrappers
import starlette.exceptions
from typing import Any, Dict, Optional, Sequence, Type, Union

ErrorList: Type[Union[pydantic.error_wrappers.ErrorWrapper, Sequence]]
RequestErrorModel: Any
StarletteHTTPException: Type[starlette.exceptions.HTTPException]
ValidationError: Any
WebSocketErrorModel: Any
create_model: Any

class FastAPIError(RuntimeError):
    __doc__: str

class HTTPException(starlette.exceptions.HTTPException):
    headers: Optional[Dict[str, Any]]
    def __init__(self, status_code: int, detail = ..., headers: Optional[Dict[str, Any]] = ...) -> None: ...

class RequestValidationError(Any):
    body: Any
    def __init__(self, errors: Sequence[Union[pydantic.error_wrappers.ErrorWrapper, Sequence]], *, body = ...) -> None: ...

class WebSocketRequestValidationError(Any):
    def __init__(self, errors: Sequence[Union[pydantic.error_wrappers.ErrorWrapper, Sequence]]) -> None: ...
