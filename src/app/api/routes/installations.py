from typing import List
from fastapi import APIRouter, Path
from sqlalchemy import and_, or_
from datetime import datetime
from app.api import crud
from app.db import installations, database
from app.api.schemas import InstallationOut, InstallationIn


router = APIRouter()


@router.post("/", response_model=InstallationOut, status_code=201, summary="Create a new installation")
async def create_installation(payload: InstallationIn):
    """Creates a new installation based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(installations, payload)


@router.get("/{installation_id}/", response_model=InstallationOut,
            summary="Get information about a specific installation")
async def get_installation(installation_id: int = Path(..., gt=0)):
    """
    Based on a installation_id, retrieves information about the specified installation
    """
    return await crud.get_entry(installations, installation_id)


@router.get("/", response_model=List[InstallationOut], summary="Get the list of all installations")
async def fetch_installations():
    """
    Retrieves the list of all installations and their information
    """
    return await crud.fetch_all(installations)


@router.put("/{installation_id}/", response_model=InstallationOut,
            summary="Update information about a specific installation")
async def update_installation(payload: InstallationIn, installation_id: int = Path(..., gt=0)):
    """
    Based on a installation_id, updates information about the specified installation
    """
    return await crud.update_entry(installations, payload, installation_id)


@router.delete("/{installation_id}/", response_model=InstallationOut, summary="Delete a specific installation")
async def delete_installation(installation_id: int = Path(..., gt=0)):
    """
    Based on a installation_id, deletes the specified installation
    """
    return await crud.delete_entry(installations, installation_id)


@router.get("/site-devices/{site_id}", response_model=List[int],
            summary="Get all devices related to a specific site")
async def get_active_devices_on_site(site_id: int = Path(..., gt=0)):
    """
    Based on a site_id, retrieves the list of all the related devices and their information
    """
    current_ts = datetime.utcnow()

    query = installations.select().where(and_(installations.c.site_id == site_id,
                                              installations.c.start_ts <= current_ts,
                                              or_(installations.c.end_ts.is_(None),
                                                  installations.c.end_ts >= current_ts)))

    return [entry['device_id'] for entry in await database.fetch_all(query=query)]
