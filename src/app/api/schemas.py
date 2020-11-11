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


# Accesses
class Cred(BaseModel):
    password: str = Field(..., example="PickARobustOne")


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
# Abstract information about a user
class UserInfo(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="JohnDoe")


# Visible info
class UserRead(UserInfo, _CreatedAt, _Id):
    pass


# Authentication request
class UserAuth(UserInfo, Cred):
    scopes: str = Field("me")


# Creation payload
class UserCreation(UserInfo):
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
    lon: float = Field(..., gt=-180, lt=180, exempl=4.514880)


class Location(_FlatLocation):
    elevation: float = Field(..., gt=0., lt=10000, example=1582)


class DefaultLocation(BaseModel):
    lat: float = Field(None, gt=-90, lt=90, example=44.765181)
    lon: float = Field(None, gt=-180, lt=180, exempl=4.514880)
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
class DeviceIn(DefaultPosition):
    name: str = Field(..., min_length=3, max_length=50, example="pyronearEngine51")
    owner_id: int = Field(..., gt=0)
    specs: str = Field(..., min_length=3, max_length=100, example="systemV0.1")
    last_ping: datetime = None


class DeviceAuth(DeviceIn):
    password: str = Field(..., example="PickARobustOne")
    scopes: str = Field("device", example="device")


class DeviceCreation(DeviceIn):
    access_id: int = Field(..., gt=0)


class DeviceOut(DeviceIn, _CreatedAt, _Id):
    pass


class HeartbeatOut(BaseModel):
    last_ping: datetime = None


# Media
class MediaIn(BaseModel):
    device_id: int = Field(..., gt=0)
    type: MediaType = MediaType.image


class MediaOut(MediaIn, _CreatedAt, _Id):
    pass


# Installations
class InstallationIn(Location, _Rotation):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    start_ts: datetime = None
    end_ts: datetime = None


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


# Alerts
class AlertIn(_FlatLocation):
    device_id: int = Field(..., gt=0)
    event_id: int = Field(..., gt=0)
    media_id: int = Field(None, gt=0)
    type: AlertType = AlertType.start
    is_acknowledged: bool = Field(False)


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass
