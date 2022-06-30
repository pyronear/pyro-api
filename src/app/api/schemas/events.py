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
    type: EventType = EventType.wildfire
    start_ts: Optional[datetime] = None
    end_ts: Optional[datetime] = None
    is_acknowledged: bool = Field(False)

    @validator("start_ts", pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class EventOut(EventIn, _CreatedAt, _Id):
    pass


class Acknowledgement(BaseModel):
    is_acknowledged: bool = Field(False)


class AcknowledgementOut(Acknowledgement, _Id):
    pass


class EventUpdate(_FlatLocation):
    type: EventType
    start_ts: datetime
    end_ts: Optional[datetime]
    is_acknowledged: bool
