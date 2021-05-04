# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List
from datetime import datetime
from fastapi import APIRouter, Path, Security, HTTPException, status, Depends

from app.api import crud
from app.db import devices, accesses, users, get_session, models
from app.api.schemas import (
    DeviceOut,
    DeviceAuth,
    MyDeviceAuth,
    AdminDeviceAuth,
    DeviceCreation,
    DeviceIn,
    UserRead,
    DefaultPosition,
    Cred,
    SoftwareHash,
    AccessType
)
from app.api.deps import get_current_device, get_current_user, get_current_access
from app.api.crud.groups import get_entity_group_id
from app.api.crud.authorizations import is_admin_access


router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201, summary="Create a new device")
async def register_device(
    payload: AdminDeviceAuth,
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """Creates a new device based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    if await crud.get(payload.owner_id, users) is None:
        raise HTTPException(status_code=404, detail=f"Unknown user for owner_id={payload.owner_id}")
    if payload.group_id is None:
        payload = payload.dict()
        payload["group_id"] = await get_entity_group_id(users, payload["owner_id"])
        payload = DeviceAuth(**payload)
    return await crud.accesses.create_accessed_entry(devices, accesses, payload, DeviceCreation)


@router.post("/register", response_model=DeviceOut, status_code=201, summary="Reg   ister your device")
async def register_my_device(
    payload: MyDeviceAuth,
    me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """Creates a new device with the current user being the owner based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    device_payload = DeviceAuth(**payload.dict(), owner_id=me.id, group_id=await get_entity_group_id(users, me.id))
    return await crud.accesses.create_accessed_entry(devices, accesses, device_payload, DeviceCreation)


@router.get("/{device_id}/", response_model=DeviceOut, summary="Get information about a specific device")
async def get_device(
    device_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, retrieves information about the specified device
    """
    return await crud.get_entry(devices, device_id)


@router.get("/me", response_model=DeviceOut, summary="Get information about the current device")
async def get_my_device(me: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Retrieves information about the current device
    """
    return me


@router.get("/", response_model=List[DeviceOut], summary="Get the list of all devices")
async def fetch_devices(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
    session=Depends(get_session)
):
    """
    Retrieves the list of all devices and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(devices)
    else:
        retrieved_devices = (session.query(models.Devices)
                             .join(models.Accesses)
                             .filter(models.Accesses.group_id == requester.group_id).all())
        retrieved_devices = [x.__dict__ for x in retrieved_devices]

        return retrieved_devices


@router.put("/{device_id}/", response_model=DeviceOut, summary="Update information about a specific device")
async def update_device(
    payload: DeviceIn,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, updates information about the specified device
    """
    return await crud.accesses.update_accessed_entry(devices, accesses, device_id, payload, only_specified=True)


@router.delete("/{device_id}/", response_model=DeviceOut, summary="Delete a specific device")
async def delete_device(
    device_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, deletes the specified device
    """
    return await crud.accesses.delete_accessed_entry(devices, accesses, device_id)


@router.get(
    "/my-devices", response_model=List[DeviceOut], summary="Get the list of all devices belonging to the current user"
)
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])):
    """
    Retrieves the list of all devices and the information which are owned by the current user
    """
    return await crud.fetch_all(devices, {"owner_id": me.id})


@router.put("/heartbeat", response_model=DeviceOut, summary="Update the last ping of the current device")
async def heartbeat(device: DeviceOut = Security(get_current_device, scopes=[AccessType.device])):
    """
    Updates the last ping of the current device with the current datetime
    """
    device.last_ping = datetime.utcnow()
    await crud.update_entry(devices, device, device.id)
    return device


@router.put("/{device_id}/location", response_model=DeviceOut, summary="Update the location of a specific device")
async def update_device_location(
    payload: DefaultPosition,
    device_id: int = Path(..., gt=0),
    user: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user]),
):
    """
    Based on a device_id, updates the location of the specified device
    """
    # Check that device is accessible to this user
    device = await crud.get_entry(devices, device_id)
    if device["owner_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission denied")
    # Update only the location
    device.update(payload.dict())
    device = DeviceOut(**device)
    await crud.update_entry(devices, device, device.id)
    return device


@router.put("/my-location", response_model=DeviceOut, summary="Update the location of the current device")
async def update_my_location(
    payload: DefaultPosition,
    device: DeviceOut = Security(get_current_device, scopes=[AccessType.device])
):
    """
    Updates the location of the current device
    """
    # Update only the position
    for k, v in payload.dict().items():
        setattr(device, k, v)
    await crud.update_entry(devices, device, device.id)
    return device


@router.put("/{device_id}/hash", response_model=DeviceOut, summary="Update the software hash of a specific device")
async def update_device_hash(
    payload: SoftwareHash,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Updates the expected software hash of the device
    """
    device = await crud.get_entry(devices, device_id)
    # Update only the corresponding field
    device.update(payload.dict())
    device = DeviceOut(**device)
    await crud.update_entry(devices, device, device_id)
    return device


@router.put("/{device_id}/pwd", response_model=DeviceOut, summary="Update the password of a specific device")
async def update_device_password(
    payload: Cred,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, updates the password of the specified device
    """
    entry = await crud.get_entry(devices, device_id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry
