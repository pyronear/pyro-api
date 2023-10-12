# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import List, Optional, cast

from fastapi import APIRouter, Depends, Path, Query, Security, status
from sqlalchemy import and_, or_
from typing_extensions import Annotated

from app.api import crud
from app.api.crud.authorizations import check_group_read, check_group_update, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_db
from app.db import installations, sites
from app.models import AccessType, Installation, Site
from app.schemas import InstallationIn, InstallationOut, InstallationUpdate

router = APIRouter()


@router.post(
    "/", response_model=InstallationOut, status_code=status.HTTP_201_CREATED, summary="Create a new installation"
)
async def create_installation(payload: InstallationIn, _=Security(get_current_access, scopes=[AccessType.admin])):
    """Creates a new installation based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(installations, payload)


@router.get(
    "/{installation_id}/", response_model=InstallationOut, summary="Get information about a specific installation"
)
async def get_installation(
    installation_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
):
    """
    Based on a installation_id, retrieves information about the specified installation
    """
    requested_group_id = await get_entity_group_id(installations, installation_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(installations, installation_id)


@router.get("/", response_model=List[InstallationOut], summary="Get the list of all installations")
async def fetch_installations(
    limit: Annotated[int, Query(description="maximum number of items", ge=1, le=1000)] = 50,
    offset: Annotated[Optional[int], Query(description="number of items to skip", ge=0)] = None,
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
    session=Depends(get_db),
):
    """
    Retrieves the list of all installations and their information
    """
    return await crud.fetch_all(
        installations,
        query=None
        if await is_admin_access(requester.id)
        else session.query(Installation).join(Site).filter(Site.group_id == requester.group_id),
        limit=limit,
        offset=offset,
    )


@router.put(
    "/{installation_id}/", response_model=InstallationOut, summary="Update information about a specific installation"
)
async def update_installation(
    payload: InstallationUpdate,
    installation_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
):
    """
    Based on a installation_id, updates information about the specified installation
    """
    requested_group_id = await get_entity_group_id(installations, installation_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(installations, payload, installation_id)


@router.delete("/{installation_id}/", response_model=InstallationOut, summary="Delete a specific installation")
async def delete_installation(
    installation_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a installation_id, deletes the specified installation
    """
    return await crud.delete_entry(installations, installation_id)


@router.get("/site-devices/{site_id}", response_model=List[int], summary="Get all devices related to a specific site")
async def get_active_devices_on_site(
    site_id: int = Path(..., gt=0),
    limit: Annotated[int, Query(description="maximum number of items", ge=1, le=1000)] = 50,
    offset: Annotated[Optional[int], Query(description="number of items to skip", ge=0)] = None,
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
    session=Depends(get_db),
):
    """
    Based on a site_id, retrieves the list of all the related devices and their information
    """
    requested_group_id = await get_entity_group_id(sites, site_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    current_ts = datetime.utcnow()
    return [
        item["device_id"]
        for item in await crud.fetch_all(
            installations,
            query=(
                session.query(Installation)
                .join(Site)
                .filter(
                    and_(
                        Site.id == site_id,
                        Installation.start_ts <= current_ts,
                        or_(Installation.end_ts.is_(None), Installation.end_ts >= current_ts),
                    )
                )
            ),
            limit=limit,
            offset=offset,
        )
    ]
