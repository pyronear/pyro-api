# (generated with --quick)

import __future__
import cryptography.exceptions
from typing import Any, Type

UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_ED25519_KEY_SIZE: int
_ED25519_SIG_SIZE: int
_Reasons: Type[cryptography.exceptions._Reasons]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module

class Ed25519PrivateKey(metaclass=abc.ABCMeta):
    @classmethod
    def from_private_bytes(cls, data) -> Any: ...
    @classmethod
    def generate(cls) -> Any: ...
    @abstractmethod
    def private_bytes(self, encoding, format, encryption_algorithm) -> Any: ...
    @abstractmethod
    def public_key(self) -> Any: ...
    @abstractmethod
    def sign(self, data) -> Any: ...

class Ed25519PublicKey(metaclass=abc.ABCMeta):
    @classmethod
    def from_public_bytes(cls, data) -> Any: ...
    @abstractmethod
    def public_bytes(self, encoding, format) -> Any: ...
    @abstractmethod
    def verify(self, signature, data) -> Any: ...
