# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.
from typing import Optional

from pydantic import Field

from app.models import SiteType

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["SiteBase", "SiteIn", "SiteOut", "SiteUpdate"]


# Sites
class SiteBase(_FlatLocation):
    name: str = Field(
        ..., min_length=3, max_length=50, description="site name", json_schema_extra={"examples": ["watchtower12"]}
    )
    group_id: Optional[int] = Field(None, gt=0, description="linked group entry")
    country: str = Field(..., max_length=5, description="country identifier", json_schema_extra={"examples": ["FR"]})
    geocode: str = Field(..., max_length=10, description="region geocode", json_schema_extra={"examples": ["01"]})


class SiteIn(SiteBase):
    type: SiteType = Field(SiteType.tower, description="site type")


class SiteOut(SiteIn, _CreatedAt, _Id):
    group_id: int = Field(..., gt=0, description="linked group entry")


class SiteUpdate(SiteBase):
    group_id: int = Field(..., gt=0, description="linked group entry")
