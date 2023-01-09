# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .base import _CreatedAt, _Id

__all__ = ["InstallationIn", "InstallationOut", "InstallationUpdate"]


# Installations
class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0, description="linked device entry")
    site_id: int = Field(..., gt=0, description="linked site entry")
    start_ts: datetime = Field(..., description="timestamp of event start")
    end_ts: Optional[datetime] = Field(None, description="timestamp of event end")
    is_trustworthy: bool = Field(True, description="whether alerts from this installation can be trusted")


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


class InstallationUpdate(InstallationIn):
    end_ts: Optional[datetime] = Field(..., description="timestamp of event end")
    is_trustworthy: bool = Field(..., description="whether alerts from this installation can be trusted")
