# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
from typing import Any, List, cast

from anyio import CapacityLimiter, to_thread
from fastapi import APIRouter, Depends, File, HTTPException, Path, Security, UploadFile, status

from app.api.dependencies import get_camera_crud, get_jwt, get_pose_crud
from app.core.config import settings
from app.core.security import create_access_token
from app.core.time import utcnow
from app.crud import CameraCRUD
from app.crud.crud_pose import PoseCRUD
from app.models import Camera, Role, UserRole
from app.schemas.cameras import (
    CameraCreate,
    CameraDeviceConfig,
    CameraEdit,
    CameraName,
    CameraOut,
    CameraRead,
    CameraTrustable,
    LastActive,
    LastImage,
)
from app.schemas.login import Token, TokenPayload
from app.schemas.poses import PoseReadWithoutImgInfo
from app.services.storage import s3_service, upload_file
from app.services.telemetry import telemetry_client

router = APIRouter()
_image_url_limiter = CapacityLimiter(8)


async def _last_image_url(organization_id: int, last_image: str | None) -> str | None:
    if not last_image:
        return None
    bucket = await to_thread.run_sync(
        s3_service.get_bucket, s3_service.resolve_bucket_name(organization_id), limiter=_image_url_limiter
    )
    exists = await to_thread.run_sync(bucket.check_file_existence, last_image, limiter=_image_url_limiter)
    if not exists:
        return None
    # Presigning is local; keep its mutable URL cache on the event loop.
    return bucket.get_public_url(last_image, verify_exists=False)


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new camera")
async def register_camera(
    payload: CameraCreate,
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> CameraOut:
    telemetry_client.capture(token_payload.sub, event="cameras-create", properties={"device_login": payload.name})
    if token_payload.organization_id != payload.organization_id and not token_payload.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    camera = await cameras.create(payload)
    return CameraOut(**camera.model_dump())


@router.get(
    "/{camera_id}",
    status_code=status.HTTP_200_OK,
    summary="Fetch the information of a specific camera",
    description="Returns camera details including a presigned S3 URL for the last captured image. `last_image_url` is null if no image has been uploaded yet or if the image is temporarily unavailable in storage.",
)
async def get_camera(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    poses: PoseCRUD = Depends(get_pose_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> CameraRead:
    telemetry_client.capture(token_payload.sub, event="cameras-get", properties={"camera_id": camera_id})
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and not token_payload.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    cam_poses = await poses.fetch_all(
        filters=[("camera_id", camera_id), ("active", True)],
        order_by="id",
    )
    pose_reads = [PoseReadWithoutImgInfo(**p.model_dump()) for p in cam_poses]

    last_image_url = await _last_image_url(camera.organization_id, camera.last_image)
    return CameraRead(**camera.model_dump(), last_image_url=last_image_url, poses=pose_reads)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Fetch all the cameras",
    description="Returns all cameras accessible to the current user. `last_image_url` is null for a given camera if no image has been uploaded yet or if the image is temporarily unavailable in storage.",
)
async def fetch_cameras(
    include_non_trustable: bool = False,
    cameras: CameraCRUD = Depends(get_camera_crud),
    poses: PoseCRUD = Depends(get_pose_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[CameraRead]:
    telemetry_client.capture(token_payload.sub, event="cameras-fetch")
    filters: list[tuple[str, Any]] = []
    if not include_non_trustable:
        filters.append(("is_trustable", True))
    if not token_payload.is_admin:
        filters.append(("organization_id", token_payload.organization_id))
    cams = await cameras.fetch_all(order_by="id", filters=filters)
    if not cams:
        return []

    # One query for every camera; an AsyncSession cannot run concurrent pose queries.
    active_poses = await poses.fetch_all(
        filters=("active", True), in_pair=("camera_id", [cam.id for cam in cams]), order_by="id"
    )
    poses_by_camera: dict[int, list[PoseReadWithoutImgInfo]] = {}
    for pose in active_poses:
        poses_by_camera.setdefault(pose.camera_id, []).append(PoseReadWithoutImgInfo(**pose.model_dump()))

    # S3 existence checks are blocking I/O; keep them off the event loop and cap concurrency.
    urls = await asyncio.gather(*[_last_image_url(cam.organization_id, cam.last_image) for cam in cams])
    return [
        CameraRead(**cam.model_dump(), last_image_url=url, poses=poses_by_camera.get(cam.id, []))
        for cam, url in zip(cams, urls, strict=True)
    ]


@router.patch("/heartbeat", status_code=status.HTTP_200_OK, summary="Update last ping of a camera")
async def heartbeat(
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> CameraOut:
    # telemetry_client.capture(f"camera|{token_payload.sub}", event="cameras-heartbeat")
    camera = await cameras.update(token_payload.sub, LastActive(last_active_at=utcnow()))
    return CameraOut(**camera.model_dump())


@router.patch("/image", status_code=status.HTTP_200_OK, summary="Update last image of a camera")
async def update_image(
    file: UploadFile = File(..., alias="file"),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> CameraOut:
    # telemetry_client.capture(f"camera|{token_payload.sub}", event="cameras-image")
    cam = cast(Camera, await cameras.get(token_payload.sub, strict=True))
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    # If the upload succeeds, delete the previous image
    if isinstance(cam.last_image, str):
        s3_service.get_bucket(s3_service.resolve_bucket_name(token_payload.organization_id)).delete_file(cam.last_image)
    # Update the DB entry
    camera = await cameras.update(token_payload.sub, LastImage(last_image=bucket_key, last_active_at=utcnow()))
    return CameraOut(**camera.model_dump())


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
    return Token(access_token=token, token_type="bearer")  # ruff:ignore[hardcoded-password-func-arg]


@router.patch("/{camera_id}/location", status_code=status.HTTP_200_OK, summary="Update the location of a camera")
async def update_camera_location(
    payload: CameraEdit,
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> CameraOut:
    telemetry_client.capture(token_payload.sub, event="cameras-update-location", properties={"camera_id": camera_id})
    camera = await cameras.update(camera_id, payload)
    return CameraOut(**camera.model_dump())


@router.patch("/{camera_id}/name", status_code=status.HTTP_200_OK, summary="Update the name of a camera")
async def update_camera_name(
    payload: CameraName,
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> CameraOut:
    telemetry_client.capture(token_payload.sub, event="cameras-update-name", properties={"camera_id": camera_id})
    camera = await cameras.update(camera_id, payload)
    return CameraOut(**camera.model_dump())


@router.patch(
    "/{camera_id}/trustable", status_code=status.HTTP_200_OK, summary="Update the trustable status of a camera"
)
async def update_camera_trustable(
    payload: CameraTrustable,
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> CameraOut:
    telemetry_client.capture(
        token_payload.sub,
        event="cameras-update-trustable",
        properties={"camera_id": camera_id, "is_trustable": payload.is_trustable},
    )
    camera = await cameras.update(camera_id, payload)
    return CameraOut(**camera.model_dump())


@router.delete("/{camera_id}", status_code=status.HTTP_200_OK, summary="Delete a camera")
async def delete_camera(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="cameras-deletion", properties={"camera_id": camera_id})
    await cameras.delete(camera_id)


@router.patch(
    "/{camera_id}/device_config", status_code=status.HTTP_200_OK, summary="Update camera device connection config"
)
async def update_camera_device_config(
    payload: CameraDeviceConfig,
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> CameraOut:
    telemetry_client.capture(
        token_payload.sub, event="cameras-update-device-config", properties={"camera_id": camera_id}
    )
    camera = await cameras.update(camera_id, payload)
    return CameraOut(**camera.model_dump())
