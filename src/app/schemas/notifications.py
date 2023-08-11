# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from app.schemas.base import _CreatedAt, _Id


class NotificationIn(BaseModel):
    alert_id: int = Field(description="linked alert entry")
    recipient_id: int = Field(description="linked recipient entry")
    subject: str = Field(description="subject of notification")
    message: str = Field(description="message of notification")
    media_id: Optional[PositiveInt] = Field(description="id of media to be sent (or None)")


class NotificationOut(NotificationIn, _Id, _CreatedAt):
    pass
