# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

from app import config as cfg

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_unlimited_access_token(content: Dict[str, Any]) -> str:
    # Used for devices
    return await create_access_token(content, timedelta(minutes=cfg.ACCESS_TOKEN_UNLIMITED_MINUTES))


async def create_access_token(content: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encode content dict using security algorithm, setting expiration."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({**content, "exp": expire}, cfg.SECRET_KEY, algorithm=cfg.JWT_ENCODING_ALGORITHM)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def hash_content_file(content: bytes, use_md5: bool = False) -> str:
    hash_fn = hashlib.md5 if use_md5 else hashlib.sha256
    return hash_fn(content).hexdigest()
