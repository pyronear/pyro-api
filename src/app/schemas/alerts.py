# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["AlertBase", "AlertCreate", "AlertRead", "AlertUpdate"]


class AlertBase(BaseModel):
    organization_id: Optional[int] = Field(None, gt=0)
    lat: Optional[float] = None
    lon: Optional[float] = None
    started_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    organization_id: int = Field(..., gt=0)
    started_at: datetime
    last_seen_at: datetime


class AlertUpdate(AlertBase):
    pass


class AlertRead(AlertCreate):
    id: int
