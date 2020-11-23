# (generated with --quick)

import __future__
import cryptography.hazmat.primitives.ciphers.base
import cryptography.hazmat.primitives.ciphers.modes
from typing import Any, Type, TypeVar

AES: Any
ARC4: Any
BlockCipherAlgorithm: Type[cryptography.hazmat.primitives.ciphers.base.BlockCipherAlgorithm]
Blowfish: Any
CAST5: Any
Camellia: Any
ChaCha20: Any
CipherAlgorithm: Type[cryptography.hazmat.primitives.ciphers.base.CipherAlgorithm]
IDEA: Any
ModeWithNonce: Type[cryptography.hazmat.primitives.ciphers.modes.ModeWithNonce]
SEED: Any
TripleDES: Any
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
utils: module

_T1 = TypeVar('_T1')

def _verify_key_size(algorithm, key: _T1) -> _T1: ...
