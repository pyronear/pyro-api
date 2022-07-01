# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


from pydantic import BaseModel, Field

from app.db.models import MediaType

from .base import _CreatedAt, _Id

__all__ = ["MediaIn", "MediaCreation", "MediaOut", "MediaUrl", "BaseMedia"]


# Media
class BaseMedia(BaseModel):
    type: MediaType = MediaType.image


class MediaIn(BaseMedia):
    device_id: int = Field(..., gt=0)


class MediaCreation(MediaIn):
    bucket_key: str = Field(...)


class MediaOut(MediaIn, _CreatedAt, _Id):
    pass


class MediaUrl(BaseModel):
    url: str
