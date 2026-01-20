# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from bcrypt import checkpw, gensalt, hashpw

from app.core.config import settings

__all__ = ["create_access_token", "hash_password", "verify_password"]


def create_access_token(content: dict[str, Any], expires_minutes: int | None = None) -> str:
    """Encode content dict using security algorithm, setting expiration.

    Args:
        content: The content to encode.
        expires_minutes: The expiration time in minutes.

    Returns:
        The encoded token.
    """
    expire_delta = timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    expire = datetime.now(UTC).replace(tzinfo=None) + expire_delta
    return jwt.encode({**content, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def hash_password(password: str) -> str:
    return hashpw(
        bytes(password, encoding="utf-8"),
        gensalt(),
    ).decode("utf-8")
