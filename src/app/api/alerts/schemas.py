from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.db import AlertType


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
