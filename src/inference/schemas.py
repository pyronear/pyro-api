# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SequenceRecord(BaseModel):
    id: int = Field(gt=0)
    pose_id: int | None = None
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)
    sequence_azimuth: float = Field(allow_inf_nan=False)
    cone_angle: float = Field(ge=0, le=360, allow_inf_nan=False)
    is_wildfire: Literal["wildfire_smoke", "other_smoke", "other"] | None = None
    started_at: datetime
    last_seen_at: datetime


class TriangulationRequest(BaseModel):
    sequences: list[SequenceRecord]

    @field_validator("sequences")
    @classmethod
    def validate_unique_ids(cls, sequences: list[SequenceRecord]) -> list[SequenceRecord]:
        ids = [sequence.id for sequence in sequences]
        if len(ids) != len(set(ids)):
            raise ValueError("sequence ids must be unique")
        return sequences


class SmokeLocation(BaseModel):
    lat: float
    lon: float


class TriangulationGroup(BaseModel):
    sequence_ids: list[int]
    smoke_location: SmokeLocation | None


class TriangulationResponse(BaseModel):
    groups: list[TriangulationGroup]


class TimezoneRequest(BaseModel):
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)


class TimezoneResponse(BaseModel):
    timezone: str
