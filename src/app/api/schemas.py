from typing import List, Optional
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.db import SiteType, EventType, MediaType, AlertType


class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserIn):
    password: str
    scopes: Optional[str]


class UserOut(UserIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class UserInDb(UserOut):
    hashed_password: str
    scopes: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: Optional[str] = None  # token sub
    scopes: List[str] = []


class SiteIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    type: SiteType = SiteType.tower


class SiteOut(SiteIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class EventIn(BaseModel):
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    type: EventType = EventType.wildfire
    end_ts: datetime = None
    start_ts: datetime = None


class EventOut(EventIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class DeviceIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    owner_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    specs: str = Field(..., min_length=3, max_length=100)
    last_elevation: float = Field(None, gt=0., lt=10000)
    last_lat: float = Field(None, gt=-90, lt=90)
    last_lon: float = Field(None, gt=-180, lt=180)
    last_yaw: float = Field(None, gt=-180, lt=180)
    last_pitch: float = Field(None, gt=-90, lt=90)
    last_ping: datetime = None


class DeviceOut(DeviceIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class UpdatedLocation(BaseModel):
    elevation: float = Field(None, ge=0., lt=10000)
    lat: float = Field(None, gt=-90, lt=90)
    lon: float = Field(None, gt=-180, lt=180)
    yaw: float = Field(None, gt=-180, lt=180)
    pitch: float = Field(None, gt=-90, lt=90)


class HeartbeatOut(BaseModel):
    last_ping: datetime = None


class MediaIn(BaseModel):
    device_id: int = Field(..., gt=0)
    type: MediaType = MediaType.image


class MediaOut(MediaIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    elevation: float = Field(..., gt=0., lt=10000)
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    yaw: float = Field(..., gt=-180, lt=180)
    pitch: float = Field(..., gt=-90, lt=90)
    start_ts: datetime = None
    end_ts: datetime = None


class InstallationOut(InstallationIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()


class AlertIn(BaseModel):
    device_id: int = Field(..., gt=0)
    event_id: int = Field(..., gt=0)
    media_id: int = Field(None, gt=0)
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    type: AlertType = AlertType.start
    is_acknowledged: bool = False


class AlertOut(AlertIn):
    id: int = Field(..., gt=0)
    created_at: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        return v or datetime.utcnow()
