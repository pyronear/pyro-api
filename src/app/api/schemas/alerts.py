# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Optional

from pydantic import Field

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["AlertIn", "AlertOut", "AlertBase"]


class AlertBase(_FlatLocation):
    media_id: int = Field(..., gt=0)
    event_id: Optional[int] = Field(None, gt=0)
    azimuth: float = Field(..., ge=0, le=360)


class AlertIn(AlertBase):
    device_id: int = Field(..., gt=0)


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass
