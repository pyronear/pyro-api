from datetime import datetime, timedelta
from typing import Any, Union, Dict

from jose import jwt
from passlib.context import CryptContext

from app import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_unlimited_access_token(data: Dict) -> str:
    return create_access_token(data, timedelta(minutes=config.ACCESS_TOKEN_UNLIMITED_MINUTES))


def create_access_token(
    data: Dict, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    data["sub"] = str(data["sub"])
    to_encode = {**data, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
