# (generated with --quick)

from typing import Any

Depends: Any
HTTPException: Any
JWTError: Any
OAuth2PasswordBearer: Any
SecurityScopes: Any
TokenPayload: Any
UserRead: Any
ValidationError: Any
cfg: module
crud: module
jwt: module
reusable_oauth2: Any
status: Any
users: Any

def get_current_user(security_scopes, token: str = ...) -> coroutine: ...
def unauthorized_exception(detail: str, authenticate_value: str) -> Any: ...
