# (generated with --quick)

import __future__
import cryptography.hazmat._der
from typing import Any, Tuple, Type

DERReader: Type[cryptography.hazmat._der.DERReader]
INTEGER: int
SEQUENCE: int
absolute_import: __future__._Feature
division: __future__._Feature
hashes: module
print_function: __future__._Feature
utils: module

class Prehashed:
    _algorithm: Any
    _digest_size: Any
    digest_size: Any
    def __init__(self, algorithm) -> None: ...

def decode_dss_signature(signature) -> Tuple[Any, Any]: ...
def encode_der(tag, *children) -> bytes: ...
def encode_der_integer(x) -> Any: ...
def encode_dss_signature(r, s) -> bytes: ...
