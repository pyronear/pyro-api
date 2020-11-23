# (generated with --quick)

import __future__
import cryptography.hazmat.primitives.serialization.base
from typing import Any, List, Type

BestAvailableEncryption: Any
Encoding: Type[cryptography.hazmat.primitives.serialization.base.Encoding]
KeySerializationEncryption: Type[cryptography.hazmat.primitives.serialization.base.KeySerializationEncryption]
NoEncryption: Any
ParameterFormat: Type[cryptography.hazmat.primitives.serialization.base.ParameterFormat]
PrivateFormat: Type[cryptography.hazmat.primitives.serialization.base.PrivateFormat]
PublicFormat: Type[cryptography.hazmat.primitives.serialization.base.PublicFormat]
__all__: List[str]
absolute_import: __future__._Feature
division: __future__._Feature
load_ssh_private_key: Any
load_ssh_public_key: Any
print_function: __future__._Feature

def load_der_parameters(data, backend = ...) -> Any: ...
def load_der_private_key(data, password, backend = ...) -> Any: ...
def load_der_public_key(data, backend = ...) -> Any: ...
def load_pem_parameters(data, backend = ...) -> Any: ...
def load_pem_private_key(data, password, backend = ...) -> Any: ...
def load_pem_public_key(data, backend = ...) -> Any: ...
