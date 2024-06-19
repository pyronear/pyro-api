# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_jwt, get_organization_crud
from app.crud import OrganizationCRUD
from app.models import Organization, UserRole
from app.schemas.login import TokenPayload
from app.schemas.organizations import OrganizationCreate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new organization")
async def register_organization(
    payload: OrganizationCreate,
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Organization:
    telemetry_client.capture(token_payload.sub, event="organization-create", properties={"device_login": payload.name})
    return await organizations.create(payload)


@router.get(
    "/{organization_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific organization"
)
async def get_organization(
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Organization:
    telemetry_client.capture(
        token_payload.sub, event="organizations-get", properties={"organization_id": organization_id}
    )
    organization = cast(Organization, await organizations.get(organization_id, strict=True))
    if token_payload.organization_id != organization.id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return organization


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the organizations")
async def fetch_organizations(
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Organization]:
    telemetry_client.capture(token_payload.sub, event="organizations-fetch")
    all_orgas = [elt for elt in await organizations.fetch_all()]
    if UserRole.ADMIN in token_payload.scopes:
        return all_orgas
    return [organization for organization in all_orgas if organization.id == token_payload.organization_id]


@router.delete("/{organization_id}", status_code=status.HTTP_200_OK, summary="Delete a organization")
async def delete_organization(
    organization_id: int = Path(..., gt=0),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(
        token_payload.sub, event="organizations-deletion", properties={"organization_id": organization_id}
    )
    await organizations.delete(organization_id)
