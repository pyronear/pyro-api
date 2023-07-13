# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from dateutil.parser import isoparse
from pydantic import BaseModel, Field, field_validator

from app.models import EventType

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["EventIn", "EventOut", "EventUpdate", "Acknowledgement", "AcknowledgementOut"]


# Events
class EventIn(_FlatLocation):
    type: Optional[EventType] = Field(EventType.wildfire, description="event type")
    start_ts: Optional[datetime] = Field(
        None,
        description="timestamp of event start",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    end_ts: Optional[datetime] = Field(
        None,
        description="timestamp of event end",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    is_acknowledged: bool = Field(False, description="whether the event has been acknowledged")

    @field_validator("start_ts")
    def validate_start_ts(v):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)

    @field_validator("end_ts")
    def validate_end_ts(v):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)


class EventOut(EventIn, _CreatedAt, _Id):
    pass


class Acknowledgement(BaseModel):
    is_acknowledged: bool = Field(False, description="whether the event has been acknowledged")


class AcknowledgementOut(Acknowledgement, _Id):
    pass


class EventUpdate(_FlatLocation):
    type: EventType = Field(..., description="event type")
    start_ts: datetime = Field(
        ...,
        description="timestamp of event start",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    end_ts: Optional[datetime] = Field(
        ...,
        description="timestamp of event end",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    is_acknowledged: bool = Field(..., description="whether the event has been acknowledged")

    @field_validator("start_ts")
    def validate_start_ts(v):
        return (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)
