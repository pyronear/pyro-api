# (generated with --quick)

import __future__
import cryptography.exceptions
from typing import Any, Type

UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_Reasons: Type[cryptography.exceptions._Reasons]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module

class X448PrivateKey(metaclass=abc.ABCMeta):
    @abstractmethod
    def exchange(self, peer_public_key) -> Any: ...
    @classmethod
    def from_private_bytes(cls, data) -> Any: ...
    @classmethod
    def generate(cls) -> Any: ...
    @abstractmethod
    def private_bytes(self, encoding, format, encryption_algorithm) -> Any: ...
    @abstractmethod
    def public_key(self) -> Any: ...

class X448PublicKey(metaclass=abc.ABCMeta):
    @classmethod
    def from_public_bytes(cls, data) -> Any: ...
    @abstractmethod
    def public_bytes(self, encoding, format) -> Any: ...
