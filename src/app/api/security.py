from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app import config as cfg


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_unlimited_access_token(content: dict) -> str:
    # Used for devices
    return await create_access_token(content, timedelta(minutes=cfg.ACCESS_TOKEN_UNLIMITED_MINUTES))


async def create_access_token(content: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encode content dict using security algorithm, setting expiration."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({**content, "exp": expire}, cfg.SECRET_KEY, algorithm=cfg.JWT_ENCODING_ALGORITHM)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)
