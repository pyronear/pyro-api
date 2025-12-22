# Copyright (C) 2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["AlertCreate", "AlertRead", "AlertUpdate"]


class AlertCreate(BaseModel):
    organization_id: int = Field(..., gt=0)
    lat: Optional[float] = None
    lon: Optional[float] = None
    start_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    organization_id: Optional[int] = Field(None, gt=0)
    lat: Optional[float] = None
    lon: Optional[float] = None
    start_at: Optional[datetime] = None


class AlertRead(AlertCreate):
    id: int
    created_at: datetime
