from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app import config, security
from app.db import devices
from app.api import crud
from app.api.schemas import Device, TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authorization/token")


async def get_current_device(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[security.ALGORITHM])
        sub: int = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
    device = await crud.get(token_data.sub, devices)
    if device is None:
        raise credentials_exception
    return device


async def get_current_active_device(current_device: Device = Depends(get_current_device)) -> Device:
    # If one include the notion of active/disabled, the following code may be useful.
    # if current_device.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive device")

    return current_device
