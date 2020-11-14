from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError

from app.api import crud
from app.db import accesses, users, devices
import app.config as cfg
from app.api.schemas import AccessRead, TokenPayload, DeviceOut, UserRead


# Scope definition
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="login/access-token",
    scopes={
        "me": "Read information about the current user.",
        "admin": "Admin rights on all routes.",
        "device": "Send heartbeat signal and media to the API for only one device"
    }
)


def unauthorized_exception(detail: str, authenticate_value: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": authenticate_value},
    )


async def get_current_access(security_scopes: SecurityScopes, token: str = Depends(reusable_oauth2)) -> AccessRead:
    """Dependency to use as fastapi.security.Security with scopes.

    >>> @app.get("/users/me")
    >>> async def read_users_me(current_user: User = Security(get_current_access, scopes=["me"])):
    >>>     return current_user
    """

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.JWT_ENCODING_ALGORITHM])
        access_id = int(payload["sub"])
        token_scopes = payload.get("scopes", [])
        token_data = TokenPayload(access_id=access_id, scopes=token_scopes)

    except (JWTError, ValidationError, KeyError):
        raise unauthorized_exception("Invalid credentials", authenticate_value)

    entry = await crud.get(entry_id=access_id, table=accesses)

    if entry is None:
        raise unauthorized_exception("Invalid credentials", authenticate_value)

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise unauthorized_exception("Permission denied", authenticate_value)

    return AccessRead(**entry)


async def get_current_user(access: AccessRead = Depends(get_current_access)) -> UserRead:
    user = await crud.fetch_one(users, [('access_id', access.id)])

    if user is None:
        raise HTTPException(status_code=400, detail="Permission denied")

    return UserRead(**user)


async def get_current_device(access: AccessRead = Depends(get_current_access)) -> DeviceOut:
    device = await crud.fetch_one(devices, [('access_id', access.id)])
    if device is None:
        raise HTTPException(status_code=400, detail="Permission denied")

    return DeviceOut(**device)
