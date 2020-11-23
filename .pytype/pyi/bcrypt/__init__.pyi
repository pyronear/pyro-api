# (generated with --quick)

import __future__
from typing import Any, List, Pattern

__all__: List[str]
__author__: str
__copyright__: str
__email__: str
__license__: str
__summary__: str
__title__: str
__uri__: str
__version__: str
_bcrypt: Any
_normalize_re: Pattern[bytes]
absolute_import: __future__._Feature
division: __future__._Feature
os: module
re: module
six: module
warnings: module

def _bcrypt_assert(ok: bool) -> None: ...
def checkpw(password: bytes, hashed_password: bytes) -> bool: ...
def gensalt(rounds: int = ..., prefix: bytes = ...) -> bytes: ...
def hashpw(password: bytes, salt: bytes) -> bytes: ...
def kdf(password: bytes, salt: bytes, desired_key_bytes: int, rounds: int, ignore_few_rounds: bool = ...) -> bytes: ...
