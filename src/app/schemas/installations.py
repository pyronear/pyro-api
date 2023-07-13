# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional, Union

from dateutil.parser import isoparse
from pydantic import BaseModel, Field, field_validator

from .base import _CreatedAt, _Id

__all__ = ["InstallationIn", "InstallationOut", "InstallationUpdate"]


# Installations
class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0, description="linked device entry")
    site_id: int = Field(..., gt=0, description="linked site entry")
    start_ts: datetime = Field(
        ...,
        description="timestamp of event start",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    end_ts: Optional[datetime] = Field(
        None,
        description="timestamp of event end",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    is_trustworthy: bool = Field(True, description="whether alerts from this installation can be trusted")

    @field_validator("start_ts")
    def validate_start_ts(cls, v: Union[datetime, str]):
        return (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)

    @field_validator("end_ts")
    def validate_end_ts(cls, v: Union[datetime, str, None]):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


class InstallationUpdate(InstallationIn):
    end_ts: Optional[datetime] = Field(
        ...,
        description="timestamp of event end",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )
    is_trustworthy: bool = Field(..., description="whether alerts from this installation can be trusted")

    @field_validator("end_ts")
    def validate_end_ts(cls, v: Union[datetime, str, None]):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)
