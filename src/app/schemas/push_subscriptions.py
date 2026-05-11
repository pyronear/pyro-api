# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "PushSubscriptionCreate",
    "PushSubscriptionRead",
    "PushSubscriptionUpdate",
    "PushSubscriptionUpsert",
    "PushSubscriptionVapidPublicKey",
]


class PushSubscriptionKeys(BaseModel):
    auth: str = Field(..., min_length=1, max_length=255)
    p256dh: str = Field(..., min_length=1, max_length=255)


class PushSubscriptionUpsert(BaseModel):
    endpoint: str = Field(..., min_length=1)
    keys: PushSubscriptionKeys
    expiration_time: datetime | None = None
    user_agent: str | None = Field(default=None, max_length=512)


class PushSubscriptionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    organization_id: int = Field(..., gt=0)
    endpoint: str = Field(..., min_length=1)
    auth: str = Field(..., min_length=1, max_length=255)
    p256dh: str = Field(..., min_length=1, max_length=255)
    expiration_time: datetime | None = None
    user_agent: str | None = Field(default=None, max_length=512)


class PushSubscriptionUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    organization_id: int | None = Field(default=None, gt=0)
    endpoint: str | None = Field(default=None, min_length=1)
    auth: str | None = Field(default=None, min_length=1, max_length=255)
    p256dh: str | None = Field(default=None, min_length=1, max_length=255)
    expiration_time: datetime | None = None
    user_agent: str | None = Field(default=None, max_length=512)
    updated_at: datetime | None = None


class PushSubscriptionRead(BaseModel):
    id: int
    endpoint: str
    expiration_time: datetime | None
    user_agent: str | None
    created_at: datetime
    updated_at: datetime


class PushSubscriptionVapidPublicKey(BaseModel):
    public_key: str = Field(..., min_length=1)
