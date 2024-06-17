# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "CameraCreate",
    "LastActive",
]


class LastActive(BaseModel):
    last_active_at: datetime = Field(default_factory=datetime.utcnow)


class CameraCreate(BaseModel):
    site_id: int = Field(..., gt=0)
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="name of the camera",
        json_schema_extra={"examples": ["pyro-camera-01"]},
    )
    angle_of_view: float = Field(
        ...,
        gt=0,
        le=360,
        description="angle between left and right camera view",
        json_schema_extra={"examples": [120.0]},
    )
    elevation: float = Field(
        ...,
        gt=0,
        lt=10000,
        description="number of meters from sea level",
        json_schema_extra={"examples": [1582]},
    )
    lat: float = Field(..., gt=-90, lt=90, description="latitude", json_schema_extra={"examples": [44.765181]})
    lon: float = Field(..., gt=-180, lt=180, description="longitude", json_schema_extra={"examples": [4.514880]})
    is_trustable: bool = Field(True, description="whether the detection from this camera can be trusted")
