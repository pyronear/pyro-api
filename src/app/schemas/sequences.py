from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, ConfigDict, Field

from app.models import AnnotationType  # keep this import if you still use SequenceUpdate and SequenceLabel

__all__ = ["SequenceUpdate", "SequenceWithCone"]


class SequenceUpdate(BaseModel):
    last_seen_at: datetime


class SequenceLabel(BaseModel):
    is_wildfire: AnnotationType


class SequenceWithCone(BaseModel):
    # accept all attributes coming from the SQLModel Sequence instance
    model_config = ConfigDict(from_attributes=True, extra="allow")

    cone_azimuth: float
    cone_angle: float
    event_groups: List[Tuple[int, ...]] = Field(default_factory=list)
    event_smoke_locations: List[Tuple[float, float]] = Field(default_factory=list)
