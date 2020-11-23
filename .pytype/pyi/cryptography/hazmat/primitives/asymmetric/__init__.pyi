# (generated with --quick)

import __future__
from typing import Any

abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module

class AsymmetricSignatureContext(metaclass=abc.ABCMeta):
    @abstractmethod
    def finalize(self) -> Any: ...
    @abstractmethod
    def update(self, data) -> Any: ...

class AsymmetricVerificationContext(metaclass=abc.ABCMeta):
    @abstractmethod
    def update(self, data) -> Any: ...
    @abstractmethod
    def verify(self) -> Any: ...
