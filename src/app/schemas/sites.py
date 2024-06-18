# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from pydantic import BaseModel, Field

__all__ = ["SiteCreate", "SiteUpdate"]


class SiteCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="name of the camera",
        json_schema_extra={"examples": ["pyro-camera-01"]},
    )
    type: str


class SiteUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="name of the camera",
        json_schema_extra={"examples": ["pyro-camera-01"]},
    )
