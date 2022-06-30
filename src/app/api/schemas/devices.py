# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import AccessType
from .base import Login, DefaultPosition, Cred, _GroupId, _CreatedAt, _Id

__all__ = ["DeviceIn", "DeviceOut", "DeviceCreation", "DeviceAuth", "SoftwareHash", "AdminDeviceAuth", "MyDeviceAuth"]


# Device
class SoftwareHash(BaseModel):
    software_hash: str = Field(..., min_length=8, max_length=16)


class MyDeviceIn(Login, DefaultPosition):
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1")
    last_ping: Optional[datetime] = Field(default=None, example=datetime.utcnow())
    angle_of_view: float = Field(..., ge=0, le=360, example=10)
    software_hash: Optional[str] = Field(None, min_length=8, max_length=16, example="0123456789ABCDEF")


class DeviceIn(MyDeviceIn):
    owner_id: int = Field(..., gt=0)


class MyDeviceAuth(MyDeviceIn, Cred):
    scope: AccessType = AccessType.device


class CommonDeviceAuth(DeviceIn, Cred):
    scope: AccessType = AccessType.device


class AdminDeviceAuth(CommonDeviceAuth):
    group_id: Optional[int] = Field(None, gt=0)  # Defined here as optionnal


class DeviceAuth(CommonDeviceAuth, _GroupId):
    pass


class DeviceCreation(DeviceIn):
    access_id: int = Field(..., gt=0)


class DeviceOut(DeviceIn, _CreatedAt, _Id):
    pass
