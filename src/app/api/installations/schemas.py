from datetime import datetime
from pydantic import BaseModel, Field, validator


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
