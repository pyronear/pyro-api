# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

from pydantic import BaseModel, Field

__all__ = [
    "PoseCreate",
    "PoseImage",
    "PoseRead",
    "PoseReadWithoutImgInfo",
    "PoseUpdate",
]


class PoseBase(BaseModel):
    azimuth: float = Field(..., ge=0, lt=360, description="Azimuth of the centre of the position in degrees")
    patrol_id: Optional[int] = Field(None, ge=0, description="External patrol identifier")


class PoseCreate(PoseBase):
    camera_id: int = Field(..., gt=0, description="ID of the camera")


class PoseUpdate(BaseModel):
    azimuth: Optional[float] = Field(None, ge=0, lt=360, description="Azimuth of the centre of the position in degrees")
    patrol_id: Optional[int] = Field(None, ge=0, description="External patrol identifier")


class PoseImage(BaseModel):
    image: str


class PoseReadWithoutImgInfo(PoseBase):
    id: int
    camera_id: int


class PoseRead(PoseBase):
    id: int
    camera_id: int
    image: str | None
    image_url: str | None = Field(None, description="URL of the image of the pose")
