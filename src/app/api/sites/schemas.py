from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.db import SiteType


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
