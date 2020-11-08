from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db import SiteType, EventType, MediaType, AlertType


# Template class
class _CreatedAt(BaseModel):
    created_at: datetime = None

    @staticmethod
    @validator('created_at', pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


# Abstract information about a user
class UserInfo(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="JohnDoe")


# Sensitive information about the user
class Cred(BaseModel):
    password: str = Field(..., example="PickARobustOne")


class CredHash(BaseModel):
    hashed_password: str


# Visible info
class UserRead(UserInfo, _CreatedAt):
    id: int = Field(..., gt=0)


# Authentication request
class UserAuth(UserInfo, Cred):
    scopes: Optional[str] = "me"


# Creation payload
class UserCreation(UserInfo):
    access_id: int = Field(..., gt=0)


class AccessBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, example="JohnDoe")
    scopes: str = Field(..., example="me")


class AccessAuth(AccessBase):
    password: str = Field(..., example="PickARobustOne")


class AccessCreation(AccessBase):
    hashed_password: str


class AccessRead(AccessBase):
    id: int = Field(..., gt=0)


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwic2NvcGVzIjpbImFkbWluIl0sImV4cCI6MTYwNDg0NTAyNH0.423fgFGTfttrvU6D1k7vF92hH5Flcd9LkvaJHCGFYd8E")
    token_type: str = Field(..., example="bearer")


class TokenPayload(BaseModel):
    user_id: Optional[str] = None  # token sub
    scopes: List[str] = []


class SiteIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, example="watchtower12")
    lat: float = Field(..., gt=-90, lt=90, example=44.758673)
    lon: float = Field(..., gt=-180, lt=180, example=4.516586)
    type: SiteType = SiteType.tower


class SiteOut(SiteIn, _CreatedAt):
    id: int = Field(..., gt=0)


class EventIn(BaseModel):
    lat: float = Field(..., gt=-90, lt=90, example=44.765181)
    lon: float = Field(..., gt=-180, lt=180, exempl=4.514880)
    type: EventType = EventType.wildfire
    end_ts: datetime = None
    start_ts: datetime = None


class EventOut(EventIn, _CreatedAt):
    id: int = Field(..., gt=0)


class DeviceIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, example="pyronearEngine51")
    owner_id: int = Field(..., gt=0)
    specs: str = Field(..., min_length=3, max_length=100)
    elevation: float = Field(None, gt=0., lt=10000, example=1582)
    lat: float = Field(None, gt=-90, lt=90, example = 44.123456)
    lon: float = Field(None, gt=-180, lt=180, example=4.123456)
    yaw: float = Field(None, gt=-180, lt=180, example=110)
    pitch: float = Field(None, gt=-90, lt=90, example=-5)
    last_ping: datetime = None


class DeviceAuth(DeviceIn):
    password: str
    scopes: Optional[str] = "device"

    class Config:
        schema_extra = { "example": {
            "password": "PickARobustOne",
            "scopes": "device"}}


class DeviceCreation(DeviceIn):
    access_id: int = Field(..., gt=0)


class DeviceOut(DeviceIn, _CreatedAt):
    id: int = Field(..., gt=0)


class UpdatedLocation(BaseModel):
    elevation: float = Field(None, ge=0., lt=10000, example=855)
    lat: float = Field(None, gt=-90, lt=90, example=48.8534)
    lon: float = Field(None, gt=-180, lt=180, example=2.3488)
    yaw: float = Field(None, gt=-180, lt=180, example=10)
    pitch: float = Field(None, gt=-90, lt=90, example=-7)


class HeartbeatOut(BaseModel):
    last_ping: datetime = None


class MediaIn(BaseModel):
    device_id: int = Field(..., gt=0)
    type: MediaType = MediaType.image


class MediaOut(MediaIn, _CreatedAt):
    id: int = Field(..., gt=0)


class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    elevation: float = Field(..., gt=0., lt=10000, example=1110)
    lat: float = Field(..., gt=-90, lt=90, example=48.8534)
    lon: float = Field(..., gt=-180, lt=180, example=2.3488)
    yaw: float = Field(..., gt=-180, lt=180, example=42)
    pitch: float = Field(..., gt=-90, lt=90, example=16)
    start_ts: datetime = None
    end_ts: datetime = None


class InstallationOut(InstallationIn, _CreatedAt):
    id: int = Field(..., gt=0)


class AlertIn(BaseModel):
    device_id: int = Field(..., gt=0)
    event_id: int = Field(..., gt=0)
    media_id: int = Field(None, gt=0)
    lat: float = Field(..., gt=-90, lt=90, example=48.654321)
    lon: float = Field(..., gt=-180, lt=180, example=2.654321)
    type: AlertType = AlertType.start
    is_acknowledged: bool = False


class AlertOut(AlertIn, _CreatedAt):
    id: int = Field(..., gt=0)
