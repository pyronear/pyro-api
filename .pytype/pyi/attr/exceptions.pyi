# (generated with --quick)

import __future__
from typing import Any, List

absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature

class AttrsAttributeNotFoundError(ValueError):
    __doc__: str

class DefaultAlreadySetError(RuntimeError):
    __doc__: str

class FrozenAttributeError(FrozenError):
    __doc__: str

class FrozenError(AttributeError):
    __doc__: str
    args: List[str]
    msg: str

class FrozenInstanceError(FrozenError):
    __doc__: str

class NotAnAttrsClassError(ValueError):
    __doc__: str

class NotCallableError(TypeError):
    __doc__: str
    msg: Any
    value: Any
    def __init__(self, msg, value) -> None: ...
    def __str__(self) -> str: ...

class PythonTooOldError(RuntimeError):
    __doc__: str

class UnannotatedAttributeError(RuntimeError):
    __doc__: str
