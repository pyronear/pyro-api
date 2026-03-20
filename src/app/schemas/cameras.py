# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.poses import PoseReadWithoutImgInfo

__all__ = [
    "CameraCreate",
    "LastActive",
]


class LastActive(BaseModel):
    last_active_at: datetime = Field(default_factory=datetime.utcnow)


class LastImage(LastActive):
    last_image: str


class CameraEdit(BaseModel):
    elevation: float = Field(
        ...,
        gt=0,
        lt=10000,
        description="number of meters from sea level",
        json_schema_extra={"examples": [1582]},
    )
    lat: float = Field(..., gt=-90, lt=90, description="latitude", json_schema_extra={"examples": [44.765181]})
    lon: float = Field(..., gt=-180, lt=180, description="longitude", json_schema_extra={"examples": [4.514880]})


class CameraCreate(CameraEdit):
    organization_id: int = Field(..., gt=0)
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
    is_trustable: bool = Field(True, description="whether the detection from this camera can be trusted")


class CameraName(BaseModel):
    name: str = Field(..., min_length=5, max_length=100, description="name of the camera")


class CameraDeviceConfig(BaseModel):
    """Internal-only: set the device connection details for a camera. Never returned in public responses."""

    camera_ip: str | None = Field(default=None, description="IP of the camera within the device's local network")
    device_ip: str | None = Field(
        default=None, description="IP of the device box (VPN-reachable) running the camera API"
    )


class CameraOut(CameraCreate):
    """
    Returned by mutation endpoints
    """

    id: int
    last_active_at: datetime | None
    last_image: str | None
    created_at: datetime


class CameraRead(CameraOut):
    """
    Returned by read endpoints
    """

    last_image_url: str | None = Field(None, description="URL of the last image of the camera")
    poses: list[PoseReadWithoutImgInfo] = Field(default_factory=list)
