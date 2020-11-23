# (generated with --quick)

import passlib.context
from typing import Any, Coroutine, Optional, Type

CryptContext: Type[passlib.context.CryptContext]
cfg: module
datetime: Type[datetime.datetime]
jwt: module
pwd_context: passlib.context.CryptContext
timedelta: Type[datetime.timedelta]

def create_access_token(content: dict, expires_delta: Optional[datetime.timedelta] = ...) -> Coroutine[Any, Any, str]: ...
def create_unlimited_access_token(content: dict) -> Coroutine[Any, Any, str]: ...
def hash_password(password: str) -> Coroutine[Any, Any, str]: ...
def verify_password(plain_password: str, hashed_password: str) -> Coroutine[Any, Any, bool]: ...
