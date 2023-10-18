# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Union

from pydantic import BaseModel, Field, HttpUrl, field_validator

from .base import _Id

__all__ = ["WebhookIn", "WebhookOut"]


# Webhooks
class WebhookIn(BaseModel):
    callback: str = Field(..., max_length=50, description="name of the route that triggers the callback")
    url: Union[HttpUrl, str] = Field(..., description="URL to post to in the callback")

    @field_validator("url")
    def validate_url(cls, v: Union[HttpUrl, str]):
        return str(HttpUrl(v) if isinstance(v, str) else v)


class WebhookOut(WebhookIn, _Id):
    pass
