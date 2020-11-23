# (generated with --quick)

import starlette.responses
from typing import Optional, Type

FileResponse: Type[starlette.responses.FileResponse]
HTMLResponse: Type[starlette.responses.HTMLResponse]
JSONResponse: Type[starlette.responses.JSONResponse]
PlainTextResponse: Type[starlette.responses.PlainTextResponse]
RedirectResponse: Type[starlette.responses.RedirectResponse]
Response: Type[starlette.responses.Response]
StreamingResponse: Type[starlette.responses.StreamingResponse]
UJSONResponse: Type[starlette.responses.UJSONResponse]
orjson: Optional[module]

class ORJSONResponse(starlette.responses.JSONResponse):
    media_type: str
    def render(self, content) -> bytes: ...
