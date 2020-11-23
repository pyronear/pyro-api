# (generated with --quick)

import _importlib_modulespec
import pathlib
from typing import Any, ContextManager, Optional, Union

_CACERT_CTX: Optional[ContextManager[pathlib.Path]]
_CACERT_PATH: Optional[str]
os: module

def contents() -> Any: ...
def get_path(package: Union[str, _importlib_modulespec.ModuleType], resource: Union[_PathLike, str]) -> ContextManager[pathlib.Path]: ...
@overload
def read_text(_module, _path, encoding = ...) -> str: ...
@overload
def read_text(package: Union[str, _importlib_modulespec.ModuleType], resource: Union[_PathLike, str], encoding: str = ..., errors: str = ...) -> str: ...
def where() -> Any: ...
