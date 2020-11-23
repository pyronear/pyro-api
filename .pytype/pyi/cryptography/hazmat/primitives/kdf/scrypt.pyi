# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.hazmat.backends.interfaces
import cryptography.hazmat.primitives.kdf
from typing import Any, Type

AlreadyFinalized: Type[cryptography.exceptions.AlreadyFinalized]
InvalidKey: Type[cryptography.exceptions.InvalidKey]
KeyDerivationFunction: Type[cryptography.hazmat.primitives.kdf.KeyDerivationFunction]
Scrypt: Any
ScryptBackend: Type[cryptography.hazmat.backends.interfaces.ScryptBackend]
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_MEM_LIMIT: int
_Reasons: Type[cryptography.exceptions._Reasons]
absolute_import: __future__._Feature
constant_time: module
division: __future__._Feature
print_function: __future__._Feature
sys: module
utils: module

def _get_backend(backend) -> Any: ...
