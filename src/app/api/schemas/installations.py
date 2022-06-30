# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .base import _CreatedAt, _Id

__all__ = ["InstallationIn", "InstallationOut", "InstallationUpdate"]


# Installations
class InstallationIn(BaseModel):
    device_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    start_ts: datetime
    end_ts: Optional[datetime] = None
    is_trustworthy: bool = Field(True)


class InstallationOut(InstallationIn, _CreatedAt, _Id):
    pass


class InstallationUpdate(InstallationIn):
    end_ts: Optional[datetime]
    is_trustworthy: bool
