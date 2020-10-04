from datetime import datetime
from pydantic import BaseModel, Field, validator


class DeviceIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    owner_id: int = Field(..., gt=0)
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
