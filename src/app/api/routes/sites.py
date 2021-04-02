# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List
from fastapi import APIRouter, Path, Security, status, HTTPException
from app.api import crud
from app.db import sites, SiteType
from app.api.schemas import SiteOut, SiteIn, SiteBase, AccessType
from app.api.deps import get_current_access


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201, summary="Create a new site")
async def create_site(payload: SiteIn, _=Security(get_current_access, scopes=[AccessType.admin])):
    """Creates a new site based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(sites, payload)


@router.post("/no-alert/", response_model=SiteOut, status_code=201, summary="Create a new no-alert site")
async def create_noalert_site(payload: SiteBase,
                              requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])):
    """Creates a new no-alert site based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """

    return await crud.create_entry(sites, SiteIn(**payload.dict(), type=SiteType.no_alert))


@router.get("/{site_id}/", response_model=SiteOut, summary="Get information about a specific site")
async def get_site(site_id: int = Path(..., gt=0),
                   requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])):
    """
    Based on a site_id, retrieves information about the specified site
    """
    entry = await crud.get_entry(sites, site_id)
    return entry


@router.get("/", response_model=List[SiteOut], summary="Get the list of all sites in your group")
async def fetch_sites(requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])):
    """
    Retrieves the list of all sites and their information
    """
    group_filtering = {}
    return await crud.fetch_all(sites, group_filtering)


@router.put("/{site_id}/", response_model=SiteOut, summary="Update information about a specific site")
async def update_site(
    payload: SiteIn,
    site_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a site_id, updates information about the specified site
    """
    return await crud.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut, summary="Delete a specific site")
async def delete_site(site_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a site_id, deletes the specified site
    """
    return await crud.delete_entry(sites, site_id)
