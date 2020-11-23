# (generated with --quick)

import __future__
import enum
from typing import Any, Type

BestAvailableEncryption: Any
Enum: Type[enum.Enum]
NoEncryption: Any
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module
utils: module

class Encoding(enum.Enum):
    DER: str
    OpenSSH: str
    PEM: str
    Raw: str
    X962: str

class KeySerializationEncryption(metaclass=abc.ABCMeta): ...

class ParameterFormat(enum.Enum):
    PKCS3: str

class PrivateFormat(enum.Enum):
    OpenSSH: str
    PKCS8: str
    Raw: str
    TraditionalOpenSSL: str

class PublicFormat(enum.Enum):
    CompressedPoint: str
    OpenSSH: str
    PKCS1: str
    Raw: str
    SubjectPublicKeyInfo: str
    UncompressedPoint: str

def _get_backend(backend) -> Any: ...
def load_der_parameters(data, backend = ...) -> Any: ...
def load_der_private_key(data, password, backend = ...) -> Any: ...
def load_der_public_key(data, backend = ...) -> Any: ...
def load_pem_parameters(data, backend = ...) -> Any: ...
def load_pem_private_key(data, password, backend = ...) -> Any: ...
def load_pem_public_key(data, backend = ...) -> Any: ...
