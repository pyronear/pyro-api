# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Union

from pydantic import BaseModel, Field

from app.models import Detection

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
    localization: Union[str, None]


class DetectionUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")


class DetectionWithUrl(Detection):
    url: str = Field(..., description="temporary URL to access the media content")

    @classmethod
    def from_detection(cls, detection: Detection, url: str) -> "DetectionWithUrl":
        return DetectionWithUrl(
            id=detection.id,
            camera_id=detection.camera_id,
            azimuth=detection.azimuth,
            bucket_key=detection.bucket_key,
            localization=detection.localization,
            is_wildfire=detection.is_wildfire,
            created_at=detection.created_at,
            updated_at=detection.updated_at,
            url=url,
        )
