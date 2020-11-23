# (generated with --quick)

import __future__
from typing import Any

abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module

class KeyDerivationFunction(metaclass=abc.ABCMeta):
    @abstractmethod
    def derive(self, key_material) -> Any: ...
    @abstractmethod
    def verify(self, key_material, expected_key) -> Any: ...
