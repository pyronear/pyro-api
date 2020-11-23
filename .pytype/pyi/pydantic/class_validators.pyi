# (generated with --quick)

import inspect
import itertools
import pydantic.errors
import pydantic.fields
import pydantic.main
import typing
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Type

ValidatorCallable = Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]
ValidatorListDict = Dict[str, List[Validator]]
ValidatorsList = List[Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]]

AnyCallable: Type[Callable]
BaseConfig: Type[pydantic.main.BaseConfig]
ChainMap: Type[typing.ChainMap]
ConfigError: Type[pydantic.errors.ConfigError]
FunctionType: Type[Callable]
ModelField: Type[pydantic.fields.ModelField]
ModelOrDc: Type[type]
ROOT_KEY: str
ROOT_VALIDATOR_CONFIG_KEY: str
Signature: Type[inspect.Signature]
VALIDATOR_CONFIG_KEY: str
_FUNCS: Set[str]
all_kwargs: Set[str]
chain: Type[itertools.chain]
warnings: module

class Validator:
    __slots__ = ["always", "check_fields", "each_item", "func", "pre", "skip_on_failure"]
    always: bool
    check_fields: bool
    each_item: bool
    func: Callable
    pre: bool
    skip_on_failure: bool
    def __init__(self, func: Callable, pre: bool = ..., each_item: bool = ..., always: bool = ..., check_fields: bool = ..., skip_on_failure: bool = ...) -> None: ...

class ValidatorGroup:
    used_validators: Set[str]
    validators: Dict[str, List[Validator]]
    def __init__(self, validators: Dict[str, List[Validator]]) -> None: ...
    def check_for_unused(self) -> None: ...
    def get_validators(self, name: str) -> Optional[Dict[str, Validator]]: ...

def _generic_validator_basic(validator: Callable, sig: inspect.Signature, args: Set[str]) -> Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]: ...
def _generic_validator_cls(validator: Callable, sig: inspect.Signature, args: Set[str]) -> Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]: ...
def _prepare_validator(function: Callable, allow_reuse: bool) -> classmethod: ...
def extract_root_validators(namespace: Dict[str, Any]) -> Tuple[List[Callable], List[Tuple[bool, Callable]]]: ...
def extract_validators(namespace: Dict[str, Any]) -> Dict[str, List[Validator]]: ...
def gather_all_validators(type_: type) -> Dict[str, classmethod]: ...
def in_ipython() -> bool: ...
def inherit_validators(base_validators: Dict[str, List[Validator]], validators: Dict[str, List[Validator]]) -> Dict[str, List[Validator]]: ...
def make_generic_validator(validator: Callable) -> Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]: ...
def prep_validators(v_funcs: Iterable[Callable]) -> List[Callable[[Optional[type], Any, Dict[str, Any], pydantic.fields.ModelField, Type[pydantic.main.BaseConfig]], Any]]: ...
@overload
def root_validator(_func: Callable) -> classmethod: ...
@overload
def root_validator(*, pre: bool = ..., allow_reuse: bool = ..., skip_on_failure: bool = ...) -> Callable[[Callable], classmethod]: ...
def validator(*fields: str, pre: bool = ..., each_item: bool = ..., always: bool = ..., check_fields: bool = ..., whole: bool = ..., allow_reuse: bool = ...) -> Callable[[Callable], classmethod]: ...
def wraps(wrapped: Callable, assigned: Sequence[str] = ..., updated: Sequence[str] = ...) -> Callable[[Callable], Callable]: ...
