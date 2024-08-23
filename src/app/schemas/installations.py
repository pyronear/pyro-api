# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .base import _CreatedAt, _Id, validate_datetime_none

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
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None) + timedelta(weeks=52)]},
    )
    is_trustworthy: bool = Field(True, description="whether alerts from this installation can be trusted")

    _validate_start_ts = field_validator("start_ts")(validate_datetime_none)
    _validate_end_ts = field_validator("end_ts")(validate_datetime_none)


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


class InstallationUpdate(InstallationIn):
    end_ts: Optional[datetime] = Field(
        ...,
        description="timestamp of event end",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None) + timedelta(weeks=52)]},
    )
    is_trustworthy: bool = Field(..., description="whether alerts from this installation can be trusted")
    _validate_end_ts = field_validator("end_ts")(validate_datetime_none)
