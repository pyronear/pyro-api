# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api import crud
from app.api.crud.authorizations import is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_current_device, get_current_user, get_db
from app.db import accesses, devices, users
from app.models import Access, AccessType, Device
from app.schemas import (
    AdminDeviceAuth,
    Cred,
    DeviceAuth,
    DeviceCreation,
    DeviceOut,
    DeviceUpdate,
    MyDeviceAuth,
    Position,
    SoftwareHash,
    UserRead,
)
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, summary="Create a new device")
async def register_device(payload: AdminDeviceAuth, access=Security(get_current_access, scopes=[AccessType.admin])):
    """Creates a new device based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(
        access.id, event="devices-create", properties={"device_login": payload.login, "group_id": payload.group_id}
    )
    await crud.get_entry(users, payload.owner_id)

    if payload.group_id is None:
        _payload = payload.model_dump()
        _payload["group_id"] = await get_entity_group_id(users, _payload["owner_id"])
        payload = DeviceAuth(**_payload)  # type: ignore[assignment]
    return await crud.accesses.create_accessed_entry(devices, accesses, cast(DeviceAuth, payload), DeviceCreation)


@router.post("/register", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, summary="Register your device")
async def register_my_device(
    payload: MyDeviceAuth, me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """Creates a new device with the current user being the owner based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(
        me.id, event="devices-create-personal", properties={"device_id": payload.login, "owner_id": me.id}
    )
    group_id = await get_entity_group_id(users, me.id)
    if group_id is None:  # for mypy to convert int | None -> int ; should never happen
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid group_id for user {me.id}")
    device_payload = DeviceAuth(**payload.model_dump(), owner_id=me.id, group_id=group_id)
    return await crud.accesses.create_accessed_entry(devices, accesses, device_payload, DeviceCreation)


@router.get("/{device_id}/", response_model=DeviceOut, summary="Get information about a specific device")
async def get_device(
    device_id: int = Path(..., gt=0), user: UserRead = Security(get_current_user, scopes=[AccessType.admin])
):
    """
    Based on a device_id, retrieves information about the specified device
    """
    telemetry_client.capture(user.id, event="devices-get", properties={"device_id": device_id})
    return await crud.get_entry(devices, device_id)


@router.get("/me", response_model=DeviceOut, summary="Get information about the current device")
async def get_my_device(me: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Retrieves information about the current device
    """
    telemetry_client.capture(me.id, event="devices-get-me")
    return me


@router.get("/", response_model=List[DeviceOut], summary="Get the list of all devices")
async def fetch_devices(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all devices and their information
    """
    telemetry_client.capture(requester.id, event="devices-fetch")
    if await is_admin_access(requester.id):
        return await crud.fetch_all(devices)
    else:
        retrieved_devices = session.query(Device).join(Access).filter(Access.group_id == requester.group_id).all()
        retrieved_devices = [x.__dict__ for x in retrieved_devices]

        return retrieved_devices


@router.put("/{device_id}/", response_model=DeviceOut, summary="Update information about a specific device")
async def update_device(
    payload: DeviceUpdate,
    device_id: int = Path(..., gt=0),
    access=Security(get_current_access, scopes=[AccessType.admin]),
):
    """
    Based on a device_id, updates information about the specified device
    """
    telemetry_client.capture(access.id, event="devices-update", properties={"device_id": device_id})
    return await crud.accesses.update_accessed_entry(devices, accesses, device_id, payload)


@router.delete("/{device_id}/", response_model=DeviceOut, summary="Delete a specific device")
async def delete_device(
    device_id: int = Path(..., gt=0), access=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, deletes the specified device
    """
    telemetry_client.capture(access.id, event="devices-update", properties={"device_id": device_id})
    return await crud.accesses.delete_accessed_entry(devices, accesses, device_id)


@router.get(
    "/my-devices", response_model=List[DeviceOut], summary="Get the list of all devices belonging to the current user"
)
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])):
    """
    Retrieves the list of all devices and the information which are owned by the current user
    """
    telemetry_client.capture(me.id, event="devices-fetch-mines")
    return await crud.fetch_all(devices, {"owner_id": me.id})


@router.put("/heartbeat", response_model=DeviceOut, summary="Update the last ping of the current device")
async def heartbeat(device: DeviceOut = Security(get_current_device, scopes=[AccessType.device])):
    """
    Updates the last ping of the current device with the current datetime
    """
    telemetry_client.capture(
        device.id, event="devices-hearbeat", properties={"device_name": device.login, "owner_id": device.owner_id}
    )
    device.last_ping = datetime.utcnow()
    await crud.update_entry(devices, device, device.id)
    return device


@router.put("/{device_id}/location", response_model=DeviceOut, summary="Update the location of a specific device")
async def update_device_location(
    payload: Position,
    device_id: int = Path(..., gt=0),
    user: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user]),
):
    """
    Based on a device_id, updates the location of the specified device
    """
    # Check that device is accessible to this user
    device = await crud.get_entry(devices, device_id)
    telemetry_client.capture(
        user.id,
        event="devices-update-location",
        properties={"device_id": device_id, "device_name": device["login"], "owner_id": device["owner_id"]},
    )
    if device["owner_id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied to modify device with id={device_id}."
        )
    # Update only the location
    device.update(payload.model_dump())
    _device = DeviceOut(**device)
    await crud.update_entry(devices, _device, _device.id)
    return _device


@router.put("/my-location", response_model=DeviceOut, summary="Update the location of the current device")
async def update_my_location(
    payload: Position, device: DeviceOut = Security(get_current_device, scopes=[AccessType.device])
):
    """
    Updates the location of the current device
    """
    telemetry_client.capture(
        device.id,
        event="devices-update-my-location",
        properties={"owner_id": device.owner_id, "device_name": device.login},
    )
    # Update only the position
    for k, v in payload.model_dump().items():
        setattr(device, k, v)
    await crud.update_entry(devices, device, device.id)
    return device


@router.put("/{device_id}/hash", response_model=DeviceOut, summary="Update the software hash of a specific device")
async def update_device_hash(
    payload: SoftwareHash,
    device_id: int = Path(..., gt=0),
    access=Security(get_current_access, scopes=[AccessType.admin]),
):
    """
    Updates the expected software hash of the device
    """
    telemetry_client.capture(
        access.id,
        event="devices-update-hash",
        properties={"device_id": device_id, "software_hash": payload.software_hash},
    )
    device = await crud.get_entry(devices, device_id)
    # Update only the corresponding field
    device.update(payload.model_dump())
    _device = DeviceOut(**device)
    await crud.update_entry(devices, _device, device_id)
    return _device


@router.put("/{device_id}/pwd", response_model=DeviceOut, summary="Update the password of a specific device")
async def update_device_password(
    payload: Cred, device_id: int = Path(..., gt=0), access=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a device_id, updates the password of the specified device
    """
    telemetry_client.capture(access.id, event="devices-update-pwd", properties={"device_id": device_id})
    entry = await crud.get_entry(devices, device_id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry
