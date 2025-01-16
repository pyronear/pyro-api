# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import re

from pydantic import BaseModel, Field

from app.core.config import settings
from app.models import Detection

__all__ = ["Azimuth", "DetectionCreate", "DetectionLabel", "DetectionUrl"]


class DetectionLabel(BaseModel):
    is_wildfire: bool


class Azimuth(BaseModel):
    azimuth: float = Field(
        ...,
        ge=0,
        lt=360,
        description="angle between north and direction in degrees",
        json_schema_extra={"examples": [110]},
    )


# Regex for a float between 0 and 1, with a maximum of 3 decimals
FLOAT_PATTERN = r"(0?\.[0-9]{1,3}|0|1)"
BOX_PATTERN = rf"\({FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN}\)"
BOXES_PATTERN = rf"^\[{BOX_PATTERN}(,{BOX_PATTERN})*\]$"
COMPILED_BOXES_PATTERN = re.compile(BOXES_PATTERN)


class DetectionCreate(Azimuth):
    camera_id: int = Field(..., gt=0)
    bucket_key: str
    bboxes: str = Field(
        ...,
        min_length=2,
        max_length=settings.MAX_BBOX_STR_LENGTH,
        description="string representation of list of tuples where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf",
        json_schema_extra={"examples": ["[(0.1, 0.1, 0.9, 0.9, 0.5)]"]},
    )


class DetectionUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")


class DetectionWithUrl(Detection):
    url: str = Field(..., description="temporary URL to access the media content")


class DetectionSequence(BaseModel):
    sequence_id: int = Field(..., gt=0)
