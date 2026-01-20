# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Annotated

from pydantic import AnyHttpUrl, BaseModel, Field

__all__ = ["WebhookCreate", "WebhookCreation"]


class WebhookCreate(BaseModel):
    url: AnyHttpUrl


class WebhookCreation(BaseModel):
    url: Annotated[str, Field(min_length=1, examples=["https://example.com"])]
