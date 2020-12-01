from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db import SiteType, EventType, MediaType, AlertType


# Template classes
class _CreatedAt(BaseModel):
    created_at: datetime = None

    @staticmethod
    @validator('created_at', pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class _Id(BaseModel):
    id: int = Field(..., gt=0)


class Timestamp(BaseModel):
    timestamp: datetime = Field(..., example=datetime.utcnow())


# Accesses
class Cred(BaseModel):
    password: str = Field(..., min_length=3, example="PickARobustOne")


class CredHash(BaseModel):
    hashed_password: str


class AccessBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, example="JohnDoe")
    scopes: str = Field(..., example="me")


class AccessAuth(AccessBase, Cred):
    pass


class AccessCreation(AccessBase, CredHash):
    pass


class AccessRead(AccessBase, _Id):
    pass


# Users
class UserInfo(BaseModel):
    # Abstract information about a user
    login: str = Field(..., min_length=3, max_length=50, example="JohnDoe")


class UserRead(UserInfo, _CreatedAt, _Id):
    # Visible info
    pass


class UserAuth(UserInfo, Cred):
    # Authentication request
    scopes: str = Field("me")


class UserCreation(UserInfo):
    # Creation payload
    access_id: int = Field(..., gt=0)


# Token
class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E")
    token_type: str = Field(..., example="bearer")


class TokenPayload(BaseModel):
    user_id: Optional[str] = None  # token sub
    scopes: List[str] = []


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
class SiteIn(_FlatLocation):
    name: str = Field(..., min_length=3, max_length=50, example="watchtower12")
    type: SiteType = SiteType.tower
    country: str = Field(..., max_length=5, example="FR")
    geocode: str = Field(..., max_length=10, example="01")


class SiteOut(SiteIn, _CreatedAt, _Id):
    pass


# Events
class EventIn(_FlatLocation):
    type: EventType = EventType.wildfire
    end_ts: datetime = None
    start_ts: datetime = None


class EventOut(EventIn, _CreatedAt, _Id):
    pass


# Device
class MyDeviceIn(DefaultPosition):
    login: str = Field(..., min_length=3, max_length=50, example="pyronearEngine51")
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1")
    last_ping: datetime = Field(default=None, example=datetime.utcnow())


class DeviceIn(MyDeviceIn):
    owner_id: int = Field(..., gt=0)


class MyDeviceAuth(MyDeviceIn, Cred):
    scopes: str = Field("device", example="device")


class DeviceAuth(DeviceIn, Cred):
    scopes: str = Field("device", example="device")


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
class InstallationIn(Location, _Rotation):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    start_ts: datetime
    end_ts: datetime = None


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


# Alerts
class AlertMediaId(BaseModel):
    media_id: int = Field(None, gt=0)


class AlertBase(_FlatLocation, AlertMediaId):
    event_id: int = Field(..., gt=0)
    type: AlertType = AlertType.start
    is_acknowledged: bool = Field(False)


class AlertIn(AlertBase):
    device_id: int = Field(..., gt=0)


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass
