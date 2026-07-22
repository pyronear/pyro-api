# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional, Union

from pydantic import BaseModel, Field

from app.core.config import settings
from app.models import AnnotationType, Detection

__all__ = ["EMPTY_BBOXES", "DetectionCreate", "DetectionLabel", "DetectionRead", "DetectionUrl", "DetectionWithUrl"]


class DetectionLabel(BaseModel):
    is_wildfire: AnnotationType


# Regex for a float between 0 and 1, with a maximum of 3 decimals
FLOAT_PATTERN = r"(0?\.[0-9]{1,3}|0|1)"
BOX_PATTERN = rf"\({FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN}\)"
# An empty list is valid: a frame with no detection (kept for sequence continuity).
BOXES_PATTERN = rf"^\[({BOX_PATTERN}(,{BOX_PATTERN})*)?\]$"

# Stored bbox of a continuity detection: a frame attached to a sequence with no detection on it.
EMPTY_BBOXES = "[]"


class DetectionCreate(BaseModel):
    camera_id: int = Field(..., gt=0)
    pose_id: int = Field(..., gt=0)
    bucket_key: str
    crop_bucket_key: Optional[str] = None
    bbox: str = Field(
        ...,
        min_length=2,
        max_length=settings.MAX_BBOX_STR_LENGTH_SINGLE,
        description="string representation of list of tuples where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf",
        json_schema_extra={"examples": ["[(0.1, 0.1, 0.9, 0.9, 0.5)]"]},
    )
    others_bboxes: Optional[str] = Field(None, max_length=settings.MAX_BBOX_STR_LENGTH_OTHERS)


class DetectionUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")
    crop_url: Optional[str] = Field(None, description="temporary URL to access the cropped media content, if any")


class DetectionRead(Detection):
    pass


class DetectionWithUrl(Detection):
    url: str = Field(..., description="temporary URL to access the media content")
    crop_url: Optional[str] = Field(None, description="temporary URL to access the cropped media content, if any")


class DetectionSequence(BaseModel):
    sequence_id: Union[int, None] = Field(..., gt=0)
