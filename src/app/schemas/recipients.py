# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from pydantic import EmailStr, Field

from app.models.recipient import NotificationType
from app.schemas.base import _CreatedAt, _GroupId, _Id


class RecipientIn(_GroupId):
    notification_type: NotificationType = Field(description="type of notification")
    address: EmailStr = Field(description="address to send notification")
    subject_template: str = Field(
        description="template for notification subject. Can contain fields like $date that are replaced when the notification is sent"
    )
    message_template: str = Field(
        description="template for notification message. Can contain fields like $date that are replaced when the notification is sent"
    )


class RecipientOut(RecipientIn, _Id, _CreatedAt):
    pass
