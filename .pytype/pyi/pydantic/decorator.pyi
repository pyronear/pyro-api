# (generated with --quick)

import pydantic.errors
import pydantic.main
import typing
from typing import Any, Dict, Optional, Sequence, Set, Tuple, Type, TypeVar

ALT_V_ARGS: str
ALT_V_KWARGS: str
AnyCallable: Type[typing.Callable]
BaseModel: Type[pydantic.main.BaseModel]
ConfigError: Type[pydantic.errors.ConfigError]
Extra: Type[pydantic.main.Extra]
V_POSITIONAL_ONLY_NAME: str
__all__: Tuple[str]
validator: Any

Callable = TypeVar('Callable', bound=Callable)

class ValidatedFunction:
    arg_mapping: Dict[int, str]
    positional_only_args: Set[str]
    raw_function: typing.Callable
    v_args_name: str
    v_kwargs_name: str
    def __init__(self, function: Callable) -> None: ...
    def build_values(self, args: tuple, kwargs: Dict[str, Any]) -> Dict[str, Any]: ...
    def call(self, *args, **kwargs) -> Any: ...
    def create_model(self, fields: Dict[str, Any], takes_args: bool, takes_kwargs: bool) -> None: ...
    def execute(self, m: pydantic.main.BaseModel) -> Any: ...

def create_model(__model_name: str, *, __config__: Type[pydantic.main.BaseConfig] = ..., __base__: Type[pydantic.main.BaseModel] = ..., __module__: Optional[str] = ..., __validators__: Dict[str, classmethod] = ..., **field_definitions) -> Type[pydantic.main.BaseModel]: ...
def to_camel(string: str) -> str: ...
def validate_arguments(function: Callable) -> Callable: ...
def wraps(wrapped: typing.Callable, assigned: Sequence[str] = ..., updated: Sequence[str] = ...) -> typing.Callable[[typing.Callable], typing.Callable]: ...
