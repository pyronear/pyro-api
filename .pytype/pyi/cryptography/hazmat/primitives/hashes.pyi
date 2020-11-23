# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.hazmat.backends.interfaces
from typing import Any, Type

AlreadyFinalized: Type[cryptography.exceptions.AlreadyFinalized]
BLAKE2b: Any
BLAKE2s: Any
Hash: Any
HashBackend: Type[cryptography.hazmat.backends.interfaces.HashBackend]
MD5: Any
SHA1: Any
SHA224: Any
SHA256: Any
SHA384: Any
SHA3_224: Any
SHA3_256: Any
SHA3_384: Any
SHA3_512: Any
SHA512: Any
SHA512_224: Any
SHA512_256: Any
SHAKE128: Any
SHAKE256: Any
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_Reasons: Type[cryptography.exceptions._Reasons]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module
utils: module

class ExtendableOutputFunction(metaclass=abc.ABCMeta):
    __doc__: str

class HashAlgorithm(metaclass=abc.ABCMeta):
    digest_size: Any
    name: Any

class HashContext(metaclass=abc.ABCMeta):
    algorithm: Any
    @abstractmethod
    def copy(self) -> Any: ...
    @abstractmethod
    def finalize(self) -> Any: ...
    @abstractmethod
    def update(self, data) -> Any: ...

def _get_backend(backend) -> Any: ...
