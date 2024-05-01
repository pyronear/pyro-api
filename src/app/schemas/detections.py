# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from pydantic import BaseModel, Field

__all__ = ["DetectionCreate", "DetectionLabel", "DetectionUrl"]


class DetectionLabel(BaseModel):
    is_wildfire: bool


class DetectionCreate(BaseModel):
    camera_id: int = Field(..., gt=0)
    bucket_key: str


class DetectionUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")
