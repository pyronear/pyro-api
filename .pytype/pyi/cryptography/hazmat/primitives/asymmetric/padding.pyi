# (generated with --quick)

import __future__
from typing import Any

OAEP: Any
PKCS1v15: Any
PSS: Any
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
hashes: module
print_function: __future__._Feature
rsa: module
six: module
utils: module

class AsymmetricPadding(metaclass=abc.ABCMeta):
    name: Any

class MGF1:
    MAX_LENGTH: Any
    _algorithm: Any
    def __init__(self, algorithm) -> None: ...

def calculate_max_pss_salt_length(key, hash_algorithm) -> Any: ...
