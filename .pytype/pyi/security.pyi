# (generated with --quick)

from typing import Any, Coroutine, Optional, Type

CryptContext: Any
cfg: module
datetime: Type[datetime.datetime]
jwt: module
pwd_context: Any
timedelta: Type[datetime.timedelta]

def create_access_token(content: dict, expires_delta: Optional[datetime.timedelta] = ...) -> Coroutine[Any, Any, str]: ...
def hash_password(password: str) -> Coroutine[Any, Any, str]: ...
def verify_password(plain_password: str, hashed_password: str) -> Coroutine[Any, Any, bool]: ...
