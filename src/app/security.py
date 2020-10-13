from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app import config as cfg


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


async def create_access_token(content: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encode content dict using security algorithm, setting expiration"""
    expires_delta = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES) if not expires_delta else expires_delta
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({**content, "exp": expire}, cfg.SECRET_KEY, algorithm=ALGORITHM)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
