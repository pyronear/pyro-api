# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import EventType
from .base import _FlatLocation, _CreatedAt, _Id

__all__ = ["EventIn", "EventOut", "Acknowledgement", "AcknowledgementOut"]


# Events
class EventIn(_FlatLocation):
    type: EventType = EventType.wildfire
    start_ts: Optional[datetime] = None
    end_ts: Optional[datetime] = None
    is_acknowledged: bool = Field(False)


class EventOut(EventIn, _CreatedAt, _Id):
    pass


class Acknowledgement(BaseModel):
    is_acknowledged: bool = Field(False)


class AcknowledgementOut(Acknowledgement, _Id):
    pass
