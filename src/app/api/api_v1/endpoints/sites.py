# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_jwt, get_site_crud
from app.crud import SiteCRUD
from app.models import Site, UserRole
from app.schemas.login import TokenPayload
from app.schemas.sites import SiteCreate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new site")
async def register_site(
    payload: SiteCreate,
    sites: SiteCRUD = Depends(get_site_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Site:
    telemetry_client.capture(token_payload.sub, event="site-create", properties={"device_login": payload.name})
    return await sites.create(payload)


@router.get("/{site_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific site")
async def get_site(
    site_id: int = Path(..., gt=0),
    sites: SiteCRUD = Depends(get_site_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Site:
    site = cast(Site, await sites.get(site_id, strict=True))
    if token_payload.site_id != site.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    telemetry_client.capture(token_payload.sub, event="sites-get", properties={"site_id": site_id})
    return site


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the sites")
async def fetch_sites(
    sites: SiteCRUD = Depends(get_site_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Site]:
    telemetry_client.capture(token_payload.sub, event="sites-fetch")
    all_sites = [elt for elt in await sites.fetch_all()]
    return [site for site in all_sites if site.id == token_payload.site_id]


@router.delete("/{site_id}", status_code=status.HTTP_200_OK, summary="Delete a site")
async def delete_site(
    site_id: int = Path(..., gt=0),
    sites: SiteCRUD = Depends(get_site_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="sites-deletion", properties={"site_id": site_id})
    await sites.delete(site_id)
