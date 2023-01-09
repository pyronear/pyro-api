# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List, cast

from fastapi import APIRouter, Depends, Path, Security, status

from app.api import crud
from app.api.crud.authorizations import check_group_read, check_group_update, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_db
from app.db import sites
from app.models import AccessType, SiteType
from app.schemas import SiteBase, SiteIn, SiteOut, SiteUpdate

router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=status.HTTP_201_CREATED, summary="Create a new site")
async def create_site(payload: SiteIn, _=Security(get_current_access, scopes=[AccessType.admin])):
    """Creates a new site based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """

    return await crud.create_entry(sites, payload)


@router.post(
    "/no-alert/", response_model=SiteOut, status_code=status.HTTP_201_CREATED, summary="Create a new no-alert site"
)
async def create_noalert_site(
    payload: SiteBase, requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """Creates a new no-alert site based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    await check_group_update(requester.id, payload.group_id)
    _payload = payload.dict()

    if _payload["group_id"] is None:
        _payload["group_id"] = requester.group_id

    return await crud.create_entry(sites, SiteIn(**_payload, type=SiteType.no_alert))


@router.get("/{site_id}/", response_model=SiteOut, summary="Get information about a specific site")
async def get_site(
    site_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a site_id, retrieves information about the specified site
    """
    requested_group_id = await get_entity_group_id(sites, site_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(sites, site_id)


@router.get("/", response_model=List[SiteOut], summary="Get the list of all sites in your group")
async def fetch_sites(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all sites and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(sites)
    else:
        return await crud.fetch_all(sites, {"group_id": requester.group_id})


@router.put("/{site_id}/", response_model=SiteOut, summary="Update information about a specific site")
async def update_site(
    payload: SiteUpdate,
    site_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
):
    """
    Based on a site_id, updates information about the specified site
    """
    # TODO: validate this one
    requested_group_id = await get_entity_group_id(sites, site_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut, summary="Delete a specific site")
async def delete_site(site_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a site_id, deletes the specified site
    """
    return await crud.delete_entry(sites, site_id)
