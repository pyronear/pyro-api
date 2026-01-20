# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from typing import Annotated

from pydantic import BaseModel, Field

__all__ = ["OrganizationCreate", "OrganizationUpdate"]


class OrganizationCreate(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="name of the organization",
            json_schema_extra={"examples": ["pyro-org-01"]},
        ),
    ]


class OrganizationUpdate(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="name of the organization",
            json_schema_extra={"examples": ["pyro-org-01"]},
        ),
    ]


class TelegramChannelId(BaseModel):
    telegram_id: Annotated[str | None, Field(pattern=r"^@[a-zA-Z0-9_-]+$")] = None


class SlackHook(BaseModel):
    slack_hook: Annotated[str, Field(pattern=r"^https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+$")]
