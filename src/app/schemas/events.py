# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models import EventType

from .base import _CreatedAt, _FlatLocation, _Id, validate_datetime_none

__all__ = ["EventIn", "EventOut", "EventUpdate", "EventPayload", "Acknowledgement", "AcknowledgementOut"]


# Events
class EventIn(_FlatLocation):
    type: EventType = Field(EventType.wildfire, description="event type")
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

    _validate_start_ts = field_validator("start_ts")(validate_datetime_none)
    _validate_end_ts = field_validator("end_ts")(validate_datetime_none)


class EventOut(EventIn, _CreatedAt, _Id):
    pass


class EventPayload(EventOut):
    media_url: str = Field(..., description="url of the media associated to the event")
    localization: Optional[str] = Field(
        None,
        max_length=200,
        description="list of bounding boxes",
        json_schema_extra={"strip_whitespace": True},
    )
    device_id: int = Field(..., gt=0, description="device ID")
    alert_id: int = Field(..., gt=0, description="alert ID")
    device_login: str = Field(..., description="device name")
    device_azimuth: Optional[float] = Field(None, ge=0, le=360, description="angle between north and direction in degrees")


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

    _validate_start_ts = field_validator("start_ts")(validate_datetime_none)
