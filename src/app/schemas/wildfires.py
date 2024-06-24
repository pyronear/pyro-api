# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.
from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ["WildfireCreate", "WildfireUpdate"]


class WildfireCreate(BaseModel):
    camera_id: int = Field(..., gt=0)
    starting_time: datetime = Field(default_factory=datetime.utcnow)


class WildfireUpdate(BaseModel):
    ending_time: datetime = Field(default_factory=datetime.utcnow)
