# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from dateutil.parser import isoparse
from pydantic import BaseModel, Field, validator

from .base import _CreatedAt, _Id

__all__ = ["InstallationIn", "InstallationOut", "InstallationUpdate"]


# Installations
class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0, description="linked device entry")
    site_id: int = Field(..., gt=0, description="linked site entry")
    start_ts: datetime = Field(
        ..., description="timestamp of event start", example=datetime.utcnow().replace(tzinfo=None)
    )
    end_ts: Optional[datetime] = Field(
        None, description="timestamp of event end", example=datetime.utcnow().replace(tzinfo=None)
    )
    is_trustworthy: bool = Field(True, description="whether alerts from this installation can be trusted")

    @validator("start_ts", pre=True, always=True)
    def validate_start_ts(v):
        return (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)

    @validator("end_ts", pre=True, always=True)
    def validate_end_ts(v):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


class InstallationUpdate(InstallationIn):
    end_ts: Optional[datetime] = Field(
        ..., description="timestamp of event end", example=datetime.utcnow().replace(tzinfo=None)
    )
    is_trustworthy: bool = Field(..., description="whether alerts from this installation can be trusted")

    @validator("end_ts", pre=True, always=True)
    def validate_end_ts(v):
        return None if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)
