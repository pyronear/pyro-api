# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from pydantic import BaseModel, Field

from app.models import MediaType

from .base import _CreatedAt, _Id

__all__ = ["MediaIn", "MediaCreation", "MediaOut", "MediaUrl", "BaseMedia"]


# Media
class BaseMedia(BaseModel):
    type: MediaType = Field(MediaType.image, description="media type")


class MediaIn(BaseMedia):
    device_id: int = Field(..., gt=0, description="linked device entry")


class MediaCreation(MediaIn):
    bucket_key: str = Field(..., description="file location on the storage bucket")


class MediaOut(MediaIn, _CreatedAt, _Id):
    pass


class MediaUrl(BaseModel):
    url: str = Field(..., description="temporary URL to access the media content")
