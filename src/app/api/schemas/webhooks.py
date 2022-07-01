# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


from pydantic import BaseModel, Field, HttpUrl

from .base import _Id

__all__ = ["WebhookIn", "WebhookOut"]


# Webhooks
class WebhookIn(BaseModel):
    callback: str = Field(..., max_length=50)
    url: HttpUrl


class WebhookOut(WebhookIn, _Id):
    pass
