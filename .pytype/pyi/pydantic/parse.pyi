# (generated with --quick)

import enum
import pathlib
from typing import Any, Callable, Type, Union

Enum: Type[enum.Enum]
Path: Type[pathlib.Path]
StrBytes: Type[Union[bytes, str]]
json: module
pickle: module

class Protocol(str, enum.Enum):
    json: str
    pickle: str

def load_file(path: Union[str, pathlib.Path], *, content_type: str = ..., encoding: str = ..., proto: Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ...) -> Any: ...
def load_str_bytes(b: Union[bytes, str], *, content_type: str = ..., encoding: str = ..., proto: Protocol = ..., allow_pickle: bool = ..., json_loads: Callable[[str], Any] = ...) -> Any: ...
