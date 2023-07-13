# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

from pydantic import Field

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["AlertIn", "AlertOut", "AlertBase"]


class AlertBase(_FlatLocation):
    media_id: int = Field(..., gt=0, description="linked media entry")
    event_id: Optional[int] = Field(None, gt=0, description="linked event entry")
    azimuth: Optional[float] = Field(None, ge=0, le=360, description="angle between north and direction in degrees")
    localization: Optional[str] = Field(None, description="list of bounding boxes")


class AlertIn(AlertBase):
    device_id: int = Field(..., gt=0, description="linked device entry")
    azimuth: float = Field(..., ge=0, le=360, description="angle between north and direction in degrees")


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass
