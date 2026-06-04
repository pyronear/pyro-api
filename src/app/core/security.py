# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt

from app.core.config import settings
from app.core.time import utcnow

__all__ = ["create_access_token", "hash_password", "verify_password"]


def create_access_token(content: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    """Encode content dict using security algorithm, setting expiration."""
    expire_delta = timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    expire = utcnow() + expire_delta
    return jwt.encode({**content, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _encode_password(password: str) -> bytes:
    # bcrypt only hashes the first 72 bytes of the password. passlib's
    # CryptContext used to silently truncate; mirror that here so hashes
    # generated under the previous implementation keep verifying.
    return password.encode("utf-8")[:72]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed stored hash — match the previous CryptContext.verify
        # behaviour which returned False rather than raising.
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_encode_password(password), bcrypt.gensalt()).decode("utf-8")
