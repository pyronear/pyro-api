# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel

from app.models import Sequence

__all__ = ["SequenceUpdate", "SequenceWithCone"]


# Accesses
class SequenceUpdate(BaseModel):
    last_seen_at: datetime


class SequenceLabel(BaseModel):
    is_wildfire: bool


class SequenceWithCone(Sequence):
    cone_azimuth: float
    cone_angle: float
