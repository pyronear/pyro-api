# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from pydantic import BaseModel, Field

__all__ = [
    "PoseCreate",
    "PoseRead",
    "PoseUpdate",
]


class PoseBase(BaseModel):
    azimuth: float = Field(..., ge=0, lt=360, description="Azimuth of the centre of the position in degrees")
    patrol_id: int | None = Field(None, gt=0, description="External patrol identifier")


class PoseCreate(PoseBase):
    camera_id: int = Field(..., gt=0, description="ID of the camera")


class PoseUpdate(BaseModel):
    azimuth: float | None = Field(None, ge=0, lt=360, description="Azimuth of the centre of the position in degrees")
    patrol_id: int | None = Field(None, gt=0, description="External patrol identifier")


class PoseRead(PoseBase):
    id: int
    camera_id: int
