# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.sequences import SequenceRead

__all__ = ["AlertBase", "AlertCreate", "AlertRead", "AlertReadWithSequences", "AlertUpdate"]


class AlertBase(BaseModel):
    organization_id: Annotated[int | None, Field(gt=0)] = None
    lat: float | None = None
    lon: float | None = None
    started_at: datetime | None = None
    last_seen_at: datetime | None = None


class AlertCreate(AlertBase):
    organization_id: Annotated[int, Field(..., gt=0)]
    started_at: datetime
    last_seen_at: datetime


class AlertUpdate(AlertBase):
    pass


class AlertRead(AlertCreate):
    id: int


class AlertReadWithSequences(AlertRead):
    sequences: Annotated[list[SequenceRead], Field(default_factory=list)]
