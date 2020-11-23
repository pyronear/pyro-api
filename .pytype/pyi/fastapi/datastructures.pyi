# (generated with --quick)

import starlette.datastructures
from typing import Any, Callable, Iterable, Type

StarletteUploadFile: Type[starlette.datastructures.UploadFile]

class UploadFile(starlette.datastructures.UploadFile):
    @classmethod
    def __get_validators__(cls) -> Iterable[Callable]: ...
    @classmethod
    def validate(cls, v) -> Any: ...
