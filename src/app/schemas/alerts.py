# Copyright (C) 2020-2023, Pyronear.
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.
import ast
from typing import Optional

from pydantic import Field, validator

from .base import _CreatedAt, _FlatLocation, _Id

__all__ = ["AlertIn", "AlertOut", "AlertBase"]


def validate_localization(v: Optional[str]) -> Optional[str]:
    """Validate localization field or raises ValueError otherwise.

    Check if type is list or None, length is <= 5 and each element is a list of length 5.
    """
    if v is None:
        return v
    try:
        localization = ast.literal_eval(v)
    except Exception:
        raise ValueError("localization must be a str that is converted to a list")
    max_num_boxes: int = 5
    if not isinstance(localization, list):
        raise ValueError("localization must be a list")
    if any(coord > 1 or coord < 0 for bbox in localization for coord in bbox):
        raise ValueError("coordinates are expected to be relative")
    if any(len(bbox) != 5 for bbox in localization):
        raise ValueError("Each bbox is expected to be in format xmin, ymin, xmax, ymax, conf")
    if len(localization) > max_num_boxes:
        raise ValueError(f"Please limit the number of boxes to {max_num_boxes}")
    return v


class AlertBase(_FlatLocation):
    media_id: int = Field(..., gt=0, description="linked media entry")
    event_id: Optional[int] = Field(None, gt=0, description="linked event entry")
    azimuth: Optional[float] = Field(None, ge=0, le=360, description="angle between north and direction in degrees")
    localization: Optional[str] = Field(
        None, max_length=200, strip_whitespace=True, description="list of bounding boxes"
    )

    _validate_localization = validator("localization", pre=True, always=True, allow_reuse=True)(validate_localization)


class AlertIn(AlertBase):
    device_id: int = Field(..., gt=0, description="linked device entry")
    azimuth: float = Field(..., ge=0, le=360, description="angle between north and direction in degrees")


class AlertOut(AlertIn, _CreatedAt, _Id):
    pass
