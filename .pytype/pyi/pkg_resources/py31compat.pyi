# (generated with --quick)

from typing import Any, Union

errno: module
needs_makedirs: Any
os: module
six: Any
sys: module

def _makedirs_31(path, exist_ok = ...) -> None: ...
@overload
def makedirs(name: Union[_PathLike, bytes, str], mode: int = ..., exist_ok: bool = ...) -> None: ...
@overload
def makedirs(path, exist_ok = ...) -> None: ...
