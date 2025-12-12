# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

from pydantic import BaseModel, Field

__all__ = [
    "PoseCreate",
    "PoseRead",
    "PoseUpdate",
]


class PoseCreate(BaseModel):
    camera_id: int = Field(..., gt=0, description="ID of the camera")
    azimuth: float = Field(..., ge=0, lt=360, description="Azimuth of the centre of the position in degrees")
    patrol_id: Optional[str] = Field(None, max_length=100, description="External patrol identifier")


class PoseUpdate(BaseModel):
    azimuth: Optional[float] = Field(None, ge=0, lt=360)
    patrol_id: Optional[str] = Field(None, max_length=100)


class PoseRead(BaseModel):
    id: int
    camera_id: int
    azimuth: float
    patrol_id: Optional[str] = None
