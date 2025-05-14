# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_jwt, get_organization_crud
from app.crud import OrganizationCRUD
from app.models import Organization, UserRole
from app.schemas.login import TokenPayload
from app.schemas.organizations import OrganizationCreate, TelegramChannelId, SlackHook
from app.services.storage import s3_service
from app.services.telegram import telegram_client
from app.services.slack import slack_client
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new organization")
async def register_organization(
    payload: OrganizationCreate,
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organization-create", properties={"organization_name": payload.name}
    )
    organization = await organizations.create(payload)
    bucket_name = s3_service.resolve_bucket_name(organization.id)
    if not s3_service.create_bucket(bucket_name):
        # Delete the organization if the bucket creation failed
        await organizations.delete(organization.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bucket")
    return organization


@router.get(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific organization"
)
async def get_organization(
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-get", properties={"organization_id": organization_id}
    )
    return cast(Organization, await organizations.get(organization_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the organizations")
async def fetch_organizations(
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> List[Organization]:
    telemetry_client.capture(token_payload.sub, event="organizations-fetch")
    return [elt for elt in await organizations.fetch_all()]


@router.delete("/{organization_id}", status_code=status.HTTP_200_OK, summary="Delete a organization")
async def delete_organization(
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(
        token_payload.sub, event="organizations-deletion", properties={"organization_id": organization_id}
    )
    bucket_name = s3_service.resolve_bucket_name(organization_id)
    if not (await s3_service.delete_bucket(bucket_name)):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bucket")
    await organizations.delete(organization_id)


@router.patch(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Update telegram channel ID of an organization"
)
async def update_telegram_id(
    payload: TelegramChannelId,
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-update-telegram-id", properties={"organization_id": organization_id}
    )
    # Check if the telegram channel ID is valid
    if payload.telegram_id and not telegram_client.has_channel_access(payload.telegram_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to access Telegram channel")
    return await organizations.update(organization_id, payload)


@router.patch(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Update slack token of an organization"
)
async def update_slack_hook(
    payload: SlackHook,
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-update-slack-hook", properties={"organization_id": organization_id}
    )
    # Check if the Slack hook is valid
    if payload.slack_hook and not slack_client.has_channel_access(payload.slack_hook):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to access Slack channel")
    return await organizations.update(organization_id, payload)