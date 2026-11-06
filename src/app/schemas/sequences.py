# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, Field

from app.models import AnnotationType, Sequence

__all__ = ["SequenceCompletionRead", "SequenceLabel", "SequenceRead", "SequenceUpdate"]


# Accesses
class SequenceUpdate(BaseModel):
    last_seen_at: datetime


class SequenceLabel(BaseModel):
    is_wildfire: AnnotationType


class SequenceRead(Sequence):
    detections_count: int = 0
    # Validation-job plumbing: re-declared so the subclass gets plain None defaults (the
    # inherited attributes are SQLAlchemy-instrumented) and stays excluded from responses.
    validation_due_at: Union[datetime, None] = Field(None, exclude=True)
    validation_lease_until: Union[datetime, None] = Field(None, exclude=True)
    validation_status: Union[str, None] = Field(None, exclude=True)
    validation_attempts: int = Field(0, exclude=True)
    completion_status: Union[str, None] = Field(None, exclude=True)
    completion_attempts: int = Field(0, exclude=True)


class SequenceCompletionRead(BaseModel):
    """Admin-only view of recoverable post-validation work."""

    id: int
    camera_id: int
    validation_status: str | None
    completion_status: Literal["pending", "completed", "failed"]
    completion_attempts: int
    validation_due_at: datetime | None
