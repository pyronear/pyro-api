# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

__all__ = ["OcclusionMaskCreate", "OcclusionMaskRead", "OcclusionMaskUpdate"]


class OcclusionMaskCreate(BaseModel):
    pose_id: Annotated[int, Field(gt=0, description="ID of the pose")]
    mask: Annotated[
        str,
        Field(
            min_length=2,
            max_length=255,
            description="string representation of tuple where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax",
            json_schema_extra={"examples": ["(0.1,0.1,0.9,0.9)"]},
        ),
    ]


class OcclusionMaskUpdate(BaseModel):
    mask: Annotated[
        str,
        Field(
            min_length=2,
            max_length=255,
            description="string representation of tuple where each tuple is a relative coordinate in order xmin, ymin, xmax, ymax",
            json_schema_extra={"examples": ["(0.1,0.1,0.9,0.9)"]},
        ),
    ]


class OcclusionMaskRead(BaseModel):
    id: int
    pose_id: int
    mask: str
    created_at: datetime
