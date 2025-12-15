# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ["OcclusionMaskCreate", "OcclusionMaskRead", "OcclusionMaskUpdate"]


class OcclusionMaskCreate(BaseModel):
    pose_id: int = Field(..., gt=0, description="ID of the pose")
    mask: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="string representation of tuple where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf",
        json_schema_extra={"examples": ["(0.1,0.1,0.9,0.9,0.5)"]},
    )


class OcclusionMaskUpdate(BaseModel):
    mask: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="string representation of tuple where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax, conf",
        json_schema_extra={"examples": ["(0.1,0.1,0.9,0.9,0.5)"]},
    )


class OcclusionMaskRead(BaseModel):
    id: int
    pose_id: int
    mask: str
    created_at: datetime
