# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import AccessType

from .base import Cred, DefaultPosition, Login, _CreatedAt, _GroupId, _Id

__all__ = [
    "DeviceIn",
    "DeviceOut",
    "DeviceCreation",
    "DeviceAuth",
    "SoftwareHash",
    "AdminDeviceAuth",
    "MyDeviceAuth",
    "DeviceUpdate",
]


# Device
class SoftwareHash(BaseModel):
    software_hash: str = Field(
        ...,
        min_length=8,
        max_length=16,
        example="0123456789ABCDEF",
        description="the unique version of the current software being run on the device",
    )


class MyDeviceIn(Login, DefaultPosition):
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1", description="hardware setup version")
    last_ping: Optional[datetime] = Field(
        default=None, example=datetime.utcnow(), description="timestamp of last communication with the API"
    )
    angle_of_view: float = Field(..., ge=0, le=360, example=10, description="angle between left and right camera view")
    software_hash: Optional[str] = Field(
        None,
        min_length=8,
        max_length=16,
        example="0123456789ABCDEF",
        description="the unique version of the current software being run on the device",
    )


class DeviceIn(MyDeviceIn):
    owner_id: int = Field(..., gt=0, description="the user ID of the device's owner")


class MyDeviceAuth(MyDeviceIn, Cred):
    scope: AccessType = Field(AccessType.device, description="access level")


class CommonDeviceAuth(DeviceIn, Cred):
    scope: AccessType = Field(AccessType.device, description="access level")


class AdminDeviceAuth(CommonDeviceAuth):
    group_id: Optional[int] = Field(None, gt=0, description="linked group entry")  # Defined here as optionnal


class DeviceAuth(CommonDeviceAuth, _GroupId):
    pass


class DeviceCreation(DeviceIn):
    access_id: int = Field(..., gt=0, description="linked access entry")


class DeviceOut(DeviceIn, _CreatedAt, _Id):
    pass


class DeviceUpdate(Login):
    lat: Optional[float] = Field(..., gt=-90, lt=90, example=44.765181, description="latitude")
    lon: Optional[float] = Field(..., gt=-180, lt=180, example=4.514880, description="longitude")
    elevation: Optional[float] = Field(
        ..., gt=0.0, lt=10000, example=1582, description="number of meters from sea level"
    )
    azimuth: Optional[float] = Field(
        ..., ge=0, le=360, example=110.0, description="angle between north and direction in degrees"
    )
    pitch: Optional[float] = Field(
        ..., ge=-90, le=90, example=-5, description="angle between horizontal plane and direction"
    )
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1", description="hardware setup version")
    last_ping: Optional[datetime] = Field(
        ..., example=datetime.utcnow(), description="timestamp of last communication with the API"
    )
    angle_of_view: float = Field(..., ge=0, le=360, example=10, description="angle between left and right camera view")
    owner_id: int = Field(..., gt=0, description="the user ID of the device's owner")
    software_hash: Optional[str] = Field(
        ...,
        min_length=8,
        max_length=16,
        example="0123456789ABCDEF",
        description="the unique version of the current software being run on the device",
    )
