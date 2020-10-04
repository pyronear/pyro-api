from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.db import EventType


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
