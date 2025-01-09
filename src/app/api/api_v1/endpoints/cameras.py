# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from typing import List, cast

from fastapi import APIRouter, Depends, File, HTTPException, Path, Security, UploadFile, status

from app.api.dependencies import get_camera_crud, get_jwt
from app.core.config import settings
from app.core.security import create_access_token
from app.crud import CameraCRUD
from app.models import Camera, Role, UserRole
from app.schemas.cameras import CameraCreate, LastActive, LastImage
from app.schemas.login import Token, TokenPayload
from app.services.storage import s3_service, upload_file
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new camera")
async def register_camera(
    payload: CameraCreate,
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Camera:
    telemetry_client.capture(token_payload.sub, event="cameras-create", properties={"device_login": payload.name})
    if token_payload.organization_id != payload.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return await cameras.create(payload)


@router.get("/{camera_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific camera")
async def get_camera(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Camera:
    telemetry_client.capture(token_payload.sub, event="cameras-get", properties={"camera_id": camera_id})
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return camera


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the cameras")
async def fetch_cameras(
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Camera]:
    telemetry_client.capture(token_payload.sub, event="cameras-fetch")
    all_cameras = [elt for elt in await cameras.fetch_all()]
    if UserRole.ADMIN in token_payload.scopes:
        return all_cameras
    return [camera for camera in all_cameras if camera.organization_id == token_payload.organization_id]


@router.patch("/heartbeat", status_code=status.HTTP_200_OK, summary="Update last ping of a camera")
async def heartbeat(
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Camera:
    # telemetry_client.capture(f"camera|{token_payload.sub}", event="cameras-heartbeat")
    return await cameras.update(token_payload.sub, LastActive(last_active_at=datetime.utcnow()))


@router.patch("/image", status_code=status.HTTP_200_OK, summary="Update last image of a camera")
async def update_image(
    file: UploadFile = File(..., alias="file"),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Camera:
    # telemetry_client.capture(f"camera|{token_payload.sub}", event="cameras-image")
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    # If the upload succeeds, delete the previous image
    cam = cast(Camera, await cameras.get(token_payload.sub, strict=True))
    if isinstance(cam.last_image, str):
        s3_service.get_bucket(s3_service.resolve_bucket_name(token_payload.organization_id)).delete_file(cam.last_image)
    # Update the DB entry
    return await cameras.update(token_payload.sub, LastImage(last_image=bucket_key, last_active_at=datetime.utcnow()))


@router.post("/{camera_id}/token", status_code=status.HTTP_200_OK, summary="Request an access token for the camera")
async def create_camera_token(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Token:
    telemetry_client.capture(token_payload.sub, event="cameras-token", properties={"camera_id": camera_id})
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    # create access token using user user_id/user_scopes
    token_data = {"sub": str(camera_id), "scopes": ["camera"], "organization_id": camera.organization_id}
    token = create_access_token(token_data, settings.JWT_UNLIMITED)
    return Token(access_token=token, token_type="bearer")  # noqa S106


@router.delete("/{camera_id}", status_code=status.HTTP_200_OK, summary="Delete a camera")
async def delete_camera(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="cameras-deletion", properties={"camera_id": camera_id})
    await cameras.delete(camera_id)
