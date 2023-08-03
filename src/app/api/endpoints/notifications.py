# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import APIRouter, HTTPException, Path, Security, status

from app.api import crud
from app.api.deps import get_current_access
from app.api.endpoints.recipients import get_recipient
from app.db import notifications
from app.models import AccessType, NotificationType
from app.schemas import NotificationIn, NotificationOut, RecipientOut
from app.services import send_telegram_msg

router = APIRouter(dependencies=[Security(get_current_access, scopes=[AccessType.admin])])


@router.post(
    "/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED, summary="Send and log notification"
)
async def send_notification(payload: NotificationIn):
    """
    Send a notification to the recipients of the same group as the device that issued the alert; log notification to db

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    recipient = RecipientOut(**(await get_recipient(recipient_id=payload.recipient_id)))
    if recipient.notification_type == NotificationType.telegram:
        send_telegram_msg(recipient.address, payload.message)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid NotificationType, not treated")

    notification: NotificationOut = NotificationOut(**(await crud.create_entry(notifications, payload)))
    return notification


@router.get(
    "/{notification_id}/", response_model=NotificationOut, summary="Get information about a specific notification"
)
async def get_notification(notification_id: int = Path(..., gt=0)):
    """
    Retrieve information about the notification with the given notification_id
    """
    return await crud.get_entry(notifications, notification_id)


@router.get("/", response_model=List[NotificationOut], summary="Get the list of all notifications")
async def fetch_notifications():
    """
    Retrieves the list of all notifications and their information
    """
    return await crud.fetch_all(notifications)


@router.delete("/{notification_id}/", response_model=NotificationOut, summary="Delete a specific notification")
async def delete_notification(notification_id: int = Path(..., gt=0)):
    """
    Based on a notification_id, deletes the specified notification from the db
    """
    return await crud.delete_entry(notifications, notification_id)
