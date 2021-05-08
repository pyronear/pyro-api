# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator, HttpUrl

from app.db.tables import SiteType, EventType, MediaType, AccessType


# Template classes
class _CreatedAt(BaseModel):
    created_at: datetime = None

    @staticmethod
    @validator('created_at', pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class _Id(BaseModel):
    id: int = Field(..., gt=0)


class _GroupId(BaseModel):
    group_id: int = Field(..., gt=0)


# Accesses
class Login(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, example="JohnDoe")


class Cred(BaseModel):
    password: str = Field(..., min_length=3, example="PickARobustOne")


class CredHash(BaseModel):
    hashed_password: str


class AccessBase(Login, _GroupId):
    scope: AccessType = AccessType.user


class AccessAuth(AccessBase, Cred):
    pass


class AccessCreation(AccessBase, CredHash):
    pass


class AccessRead(AccessBase, _Id):
    pass


# Users
class UserInfo(Login):
    # Abstract information about a user
    pass


class UserRead(UserInfo, _CreatedAt, _Id):
    # Visible info
    pass


class UserAuth(UserInfo, Cred, _GroupId):
    # Authentication request
    scope: AccessType = AccessType.user


class UserCreation(UserInfo):
    # Creation payload
    access_id: int = Field(..., gt=0)


# Groups
class GroupIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, example="Fireman85")


class GroupOut(GroupIn, _Id):
    pass


# Token
class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E")
    token_type: str = Field(..., example="bearer")


class TokenPayload(BaseModel):
    user_id: Optional[str] = None  # token sub
    scopes: List[AccessType] = []


# Location
class _FlatLocation(BaseModel):
    lat: float = Field(..., gt=-90, lt=90, example=44.765181)
    lon: float = Field(..., gt=-180, lt=180, example=4.514880)


class Location(_FlatLocation):
    elevation: float = Field(..., gt=0., lt=10000, example=1582)


class DefaultLocation(BaseModel):
    lat: float = Field(None, gt=-90, lt=90, example=44.765181)
    lon: float = Field(None, gt=-180, lt=180, example=4.514880)
    elevation: float = Field(None, gt=0., lt=10000, example=1582)


class _Rotation(BaseModel):
    yaw: float = Field(..., gt=-180, lt=180, example=110)
    pitch: float = Field(..., gt=-90, lt=90, example=-5)


class _DefaultRotation(BaseModel):
    yaw: float = Field(None, gt=-180, lt=180, example=110)
    pitch: float = Field(None, gt=-90, lt=90, example=-5)


class DefaultPosition(DefaultLocation, _DefaultRotation):
    pass


# Sites
class SiteBase(_FlatLocation):
    name: str = Field(..., min_length=3, max_length=50, example="watchtower12")
    group_id: int = Field(None, gt=0)
    country: str = Field(..., max_length=5, example="FR")
    geocode: str = Field(..., max_length=10, example="01")


class SiteIn(SiteBase):
    type: SiteType = SiteType.tower


class SiteOut(SiteIn, _CreatedAt, _Id):
    pass


# Events
class EventIn(_FlatLocation):
    type: EventType = EventType.wildfire
    end_ts: datetime = None
    start_ts: datetime = None
    is_acknowledged: bool = Field(False)


class EventOut(EventIn, _CreatedAt, _Id):
    pass


# Device
class SoftwareHash(BaseModel):
    software_hash: str = Field(..., min_length=8, max_length=16)


class MyDeviceIn(Login, DefaultPosition):
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1")
    last_ping: datetime = Field(default=None, example=datetime.utcnow())
    angle_of_view: float = Field(..., gt=0, lt=360, example=10)
    software_hash: str = Field(None, min_length=8, max_length=16, example="0123456789ABCDEF")


class DeviceIn(MyDeviceIn):
    owner_id: int = Field(..., gt=0)


class MyDeviceAuth(MyDeviceIn, Cred):
    scope: AccessType = AccessType.device


class CommonDeviceAuth(DeviceIn, Cred):
    scope: AccessType = AccessType.device


class AdminDeviceAuth(CommonDeviceAuth):
    group_id: int = Field(None, gt=0)  # Defined here as optionnal


class DeviceAuth(CommonDeviceAuth, _GroupId):
    pass


class DeviceCreation(DeviceIn):
    access_id: int = Field(..., gt=0)


class DeviceOut(DeviceIn, _CreatedAt, _Id):
    pass


# Media
class BaseMedia(BaseModel):
    type: MediaType = MediaType.image


class MediaIn(BaseMedia):
    device_id: int = Field(..., gt=0)


class MediaCreation(MediaIn):
    bucket_key: str = Field(...)


class MediaOut(MediaIn, _CreatedAt, _Id):
    pass


class MediaUrl(BaseModel):
    url: str


# Installations
class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    start_ts: datetime
    end_ts: datetime = None
    is_trustworthy: bool = Field(True)


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


# Alerts
class AlertMediaId(BaseModel):
    media_id: int = Field(None, gt=0)


class AlertBase(_FlatLocation, AlertMediaId):
    event_id: int = Field(None, gt=0)
    azimuth: float = Field(default=None, gt=0, lt=360)


class AlertIn(AlertBase):
    device_id: int = Field(..., gt=0)


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass


class Acknowledgement(BaseModel):
    is_acknowledged: bool = Field(False)


class AcknowledgementOut(Acknowledgement, _Id):
    pass


# Webhooks
class WebhookIn(BaseModel):
    callback: str = Field(..., max_length=50)
    url: HttpUrl


class WebhookOut(WebhookIn, _Id):
    pass
