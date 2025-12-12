# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_camera_crud, get_jwt, get_pose_crud
from app.crud import CameraCRUD, PoseCRUD
from app.models import UserRole
from app.schemas.login import TokenPayload
from app.schemas.poses import PoseCreate, PoseRead, PoseUpdate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new pose for a camera")
async def create_pose(
    payload: PoseCreate = Body(...),
    poses: PoseCRUD = Depends(get_pose_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> PoseRead:
    telemetry_client.capture(
        token_payload.sub,
        event="poses-create",
        properties={"camera_id": payload.camera_id, "azimuth": payload.azimuth},
    )

    camera = await cameras.get(payload.camera_id, strict=True)

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    db_pose = await poses.create(payload)
    return PoseRead(**db_pose.model_dump())


@router.get("/{pose_id}", status_code=status.HTTP_200_OK, summary="Fetch information of a specific pose")
async def get_pose(
    pose_id: int = Path(..., gt=0),
    poses: PoseCRUD = Depends(get_pose_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> PoseRead:
    telemetry_client.capture(token_payload.sub, event="poses-get", properties={"pose_id": pose_id})

    pose = await poses.get(pose_id, strict=True)
    camera = await cameras.get(pose.camera_id, strict=True)

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    return PoseRead(**pose.model_dump())


@router.patch("/{pose_id}", status_code=status.HTTP_200_OK, summary="Update a pose")
async def update_pose(
    pose_id: int = Path(..., gt=0),
    payload: PoseUpdate = Body(...),
    poses: PoseCRUD = Depends(get_pose_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.AGENT, UserRole.ADMIN]),
) -> PoseRead:
    pose = await poses.get(pose_id, strict=True)
    camera = await cameras.get(pose.camera_id, strict=True)

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    db_pose = await poses.update(pose_id, payload)
    return PoseRead(**db_pose.model_dump())


@router.delete("/{pose_id}", status_code=status.HTTP_200_OK, summary="Delete a pose")
async def delete_pose(
    pose_id: int = Path(..., gt=0),
    poses: PoseCRUD = Depends(get_pose_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="poses-deletion", properties={"pose_id": pose_id})
    await poses.delete(pose_id)
