# (generated with --quick)

import fastapi.routing
from typing import Any, Callable, Optional, Sequence, Type

APIRouter: Type[fastapi.routing.APIRouter]
Cred: Any
UserAuth: Any
UserInfo: Any
UserRead: Any
create_user: Any
delete_user: Any
fetch_users: Any
get_current_user: Any
get_my_user: Any
get_user: Any
reset_password: Any
router: fastapi.routing.APIRouter
routing: module
update_my_info: Any
update_my_password: Any
update_user: Any
users: Any

def Path(default, *, alias: Optional[str] = ..., title: Optional[str] = ..., description: Optional[str] = ..., gt: Optional[float] = ..., ge: Optional[float] = ..., lt: Optional[float] = ..., le: Optional[float] = ..., min_length: Optional[int] = ..., max_length: Optional[int] = ..., regex: Optional[str] = ..., deprecated: bool = ..., **extra) -> Any: ...
def Security(dependency: Optional[Callable] = ..., *, scopes: Optional[Sequence[str]] = ..., use_cache: bool = ...) -> Any: ...
