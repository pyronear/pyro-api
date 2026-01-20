# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.poses import PoseRead
from app.utils import utc_now

__all__ = [
    "CameraCreate",
    "LastActive",
]


class LastActive(BaseModel):
    last_active_at: Annotated[datetime, Field(default_factory=utc_now)]


class LastImage(LastActive):
    last_image: str


class CameraEdit(BaseModel):
    elevation: Annotated[
        float,
        Field(
            gt=0,
            lt=10000,
            description="number of meters from sea level",
            json_schema_extra={"examples": [1582]},
        ),
    ]
    lat: Annotated[
        float, Field(..., gt=-90, lt=90, description="latitude", json_schema_extra={"examples": [44.765181]})
    ]
    lon: Annotated[
        float, Field(..., gt=-180, lt=180, description="longitude", json_schema_extra={"examples": [4.514880]})
    ]


class CameraCreate(CameraEdit):
    organization_id: Annotated[int, Field(..., gt=0)]
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="name of the camera",
            json_schema_extra={"examples": ["pyro-camera-01"]},
        ),
    ]
    angle_of_view: Annotated[
        float,
        Field(
            gt=0,
            le=360,
            description="angle between left and right camera view",
            json_schema_extra={"examples": [120.0]},
        ),
    ]
    is_trustable: Annotated[bool, Field(True, description="whether the detection from this camera can be trusted")]


class CameraName(BaseModel):
    name: Annotated[str, Field(min_length=5, max_length=100, description="name of the camera")]


class CameraRead(CameraCreate):
    id: int
    last_active_at: datetime | None
    last_image: str | None
    last_image_url: Annotated[str | None, Field(None, description="URL of the last image of the camera")]
    poses: Annotated[list[PoseRead], Field(default_factory=list)]
    created_at: datetime
