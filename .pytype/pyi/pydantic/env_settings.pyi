# (generated with --quick)

import pathlib
import pydantic.fields
import pydantic.main
from typing import Any, Dict, Optional, Type, TypeVar, Union

BaseModel: Type[pydantic.main.BaseModel]
Extra: Type[pydantic.main.Extra]
ModelField: Type[pydantic.fields.ModelField]
Path: Type[pathlib.Path]
env_file_sentinel: str
os: module
warnings: module

KeyType = TypeVar('KeyType')

class BaseSettings(pydantic.main.BaseModel):
    Config: type
    __config__: Any
    __doc__: str
    def __init__(__pydantic_self__: BaseSettings, _env_file: Optional[Union[str, pathlib.Path]] = ..., _env_file_encoding: Optional[str] = ..., **values) -> None: ...
    def _build_environ(self, _env_file: Optional[Union[str, pathlib.Path]] = ..., _env_file_encoding: Optional[str] = ...) -> Dict[str, Optional[str]]: ...
    def _build_values(self, init_kwargs: Dict[str, Any], _env_file: Optional[Union[str, pathlib.Path]] = ..., _env_file_encoding: Optional[str] = ...) -> Dict[str, Any]: ...

class SettingsError(ValueError): ...

def deep_update(mapping: Dict[KeyType, Any], updating_mapping: Dict[KeyType, Any]) -> Dict[KeyType, Any]: ...
def display_as_type(v) -> str: ...
def read_env_file(file_path: pathlib.Path, *, encoding: str = ..., case_sensitive: bool = ...) -> Dict[str, Optional[str]]: ...
def sequence_like(v: type) -> bool: ...
