# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pydantic import Field

from app.db.models import SiteType

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["SiteBase", "SiteIn", "SiteOut", "SiteUpdate"]


# Sites
class SiteBase(_FlatLocation):
    name: str = Field(..., min_length=3, max_length=50, example="watchtower12")
    group_id: int = Field(None, gt=0)
    country: str = Field(..., max_length=5, example="FR")
    geocode: str = Field(..., max_length=10, example="01")


class SiteIn(SiteBase):
    type: SiteType = SiteType.tower


class SiteOut(SiteIn, _CreatedAt, _Id):
    group_id: int = Field(..., gt=0)


class SiteUpdate(SiteBase):
    group_id: int = Field(..., gt=0)
