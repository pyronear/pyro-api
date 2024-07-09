# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["Azimuth", "DetectionCreate", "DetectionLabel", "DetectionUrl"]


class DetectionLabel(BaseModel):
    is_wildfire: bool


class Azimuth(BaseModel):
    azimuth: float = Field(
        ...,
        gt=0,
        lt=360,
        description="angle between north and direction in degrees",
        json_schema_extra={"examples": [110]},
    )


class DetectionCreate(Azimuth):
    camera_id: int = Field(..., gt=0)
    bucket_key: str
    localization: Optional[str]


class DetectionUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")
