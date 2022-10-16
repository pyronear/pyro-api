# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.db.models import EventType

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["EventIn", "EventOut", "EventUpdate", "Acknowledgement", "AcknowledgementOut"]


# Events
class EventIn(_FlatLocation):
    type: EventType = Field(EventType.wildfire, description="event type")
    start_ts: Optional[datetime] = Field(None, description="timestamp of event start")
    end_ts: Optional[datetime] = Field(None, description="timestamp of event end")
    is_acknowledged: bool = Field(False, description="whether the event has been acknowledged")

    @validator("start_ts", pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class EventOut(EventIn, _CreatedAt, _Id):
    pass


class Acknowledgement(BaseModel):
    is_acknowledged: bool = Field(False, description="whether the event has been acknowledged")


class AcknowledgementOut(Acknowledgement, _Id):
    pass


class EventUpdate(_FlatLocation):
    type: EventType = Field(..., description="event type")
    start_ts: datetime = Field(..., description="timestamp of event start")
    end_ts: Optional[datetime] = Field(..., description="timestamp of event end")
    is_acknowledged: bool = Field(..., description="whether the event has been acknowledged")
