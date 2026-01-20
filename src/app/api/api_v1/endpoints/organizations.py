# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_jwt
from app.crud import OrganizationCRUD
from app.db import get_session
from app.models import Organization, UserRole
from app.schemas.login import TokenPayload
from app.schemas.organizations import OrganizationCreate, SlackHook, TelegramChannelId
from app.services.slack import slack_client
from app.services.storage import s3_service
from app.services.telegram import telegram_client
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new organization")
async def register_organization(
    payload: OrganizationCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organization-create", properties={"organization_name": payload.name}
    )
    organization = await OrganizationCRUD(session=session).create(payload)
    bucket_name = s3_service.resolve_bucket_name(organization.id)
    if not s3_service.create_bucket(bucket_name):
        # Delete the organization if the bucket creation failed
        await OrganizationCRUD(session=session).delete(organization.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bucket")
    return organization


@router.get(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific organization"
)
async def get_organization(
    organization_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-get", properties={"organization_id": organization_id}
    )
    return cast(Organization, await OrganizationCRUD(session=session).get(organization_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the organizations")
async def fetch_organizations(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> list[Organization]:
    telemetry_client.capture(token_payload.sub, event="organizations-fetch")
    return [elt for elt in await OrganizationCRUD(session=session).fetch_all()]


@router.delete("/{organization_id}", status_code=status.HTTP_200_OK, summary="Delete a organization")
async def delete_organization(
    organization_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> None:
    telemetry_client.capture(
        token_payload.sub, event="organizations-deletion", properties={"organization_id": organization_id}
    )
    bucket_name = s3_service.resolve_bucket_name(organization_id)
    if not (await s3_service.delete_bucket(bucket_name)):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bucket")
    await OrganizationCRUD(session=session).delete(organization_id)


@router.patch(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Update telegram channel ID of an organization"
)
async def update_telegram_id(
    payload: TelegramChannelId,
    organization_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-update-telegram-id", properties={"organization_id": organization_id}
    )
    # Check if the telegram channel ID is valid
    if payload.telegram_id and not telegram_client.has_channel_access(payload.telegram_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to access Telegram channel")
    return await OrganizationCRUD(session=session).update(organization_id, payload)


@router.patch(
    "/slack-hook/{organization_id}", status_code=status.HTTP_200_OK, summary="Update slack token of an organization"
)
async def update_slack_hook(
    payload: SlackHook,
    organization_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Organization:
    # Check if the Slack hook is valid
    check = slack_client.has_channel_access(payload.slack_hook)

    if payload.slack_hook and not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to access Slack channel")
    return await OrganizationCRUD(session=session).update(organization_id, payload)
