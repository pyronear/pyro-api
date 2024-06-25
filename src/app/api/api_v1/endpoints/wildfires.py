# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_camera_crud, get_jwt, get_wildfire_crud
from app.crud import CameraCRUD, WildfireCRUD
from app.models import Role, UserRole, Wildfire
from app.schemas.login import TokenPayload
from app.schemas.wildfires import WildfireCreate, WildfireUpdate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new wildfire")
async def register_wildfire(
    payload: WildfireCreate,
    wildfires: WildfireCRUD = Depends(get_wildfire_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Wildfire:
    telemetry_client.capture(token_payload.sub, event="wildfire-create", properties={"device_login": payload.camera_id})
    if await wildfires.get_ending_time_null(payload.camera_id):  # check that the last wildfire has ended
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unclosed Wildfire in the database.")

    return await wildfires.create(payload)


@router.get("/{wildfire_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific wildfire")
async def get_wildfire(
    wildfire_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    wildfires: WildfireCRUD = Depends(get_wildfire_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Wildfire:
    telemetry_client.capture(token_payload.sub, event="wildfires-get", properties={"wildfire_id": wildfire_id})
    wildfire = cast(Wildfire, await wildfires.get(wildfire_id, strict=True))
    camera = await cameras.get(wildfire.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return wildfire


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the wildfires")
async def fetch_wildfires(
    wildfires: WildfireCRUD = Depends(get_wildfire_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Wildfire]:
    telemetry_client.capture(token_payload.sub, event="wildfires-fetch")
    all_wildfires = [elt for elt in await wildfires.fetch_all()]
    if UserRole.ADMIN in token_payload.scopes:
        return all_wildfires
    filtered_wildfires = []
    for wildifire in all_wildfires:
        camera = await cameras.get(wildifire.camera_id, strict=True)
        if camera is not None and camera.organization_id == token_payload.organization_id:
            filtered_wildfires.append(wildifire)
    return filtered_wildfires


@router.delete("/{wildfire_id}", status_code=status.HTTP_200_OK, summary="Delete a wildfire")
async def delete_wildfire(
    wildfire_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    wildfires: WildfireCRUD = Depends(get_wildfire_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="wildfires-deletion", properties={"wildfire_id": wildfire_id})
    wildfire = cast(Wildfire, await wildfires.get(wildfire_id, strict=True))
    camera = await cameras.get(wildfire.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    await wildfires.delete(wildfire_id)


@router.patch("/{wildfire_id}", status_code=status.HTTP_200_OK, summary="Close a wildfire")
async def update_wildfire(
    payload: WildfireUpdate,
    wildfire_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    wildfires: WildfireCRUD = Depends(get_wildfire_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="wildfires-deletion", properties={"wildfire_id": wildfire_id})
    wildfire = cast(Wildfire, await wildfires.get(wildfire_id, strict=True))
    camera = await cameras.get(wildfire.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    await wildfires.update(wildfire_id, payload)
