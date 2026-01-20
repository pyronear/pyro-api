# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.
from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_camera_crud, get_jwt, get_occlusion_mask_crud, get_pose_crud
from app.crud import CameraCRUD
from app.crud.crud_occlusion_mask import OcclusionMaskCRUD
from app.crud.crud_pose import PoseCRUD
from app.models import Camera, Pose, Role, UserRole
from app.schemas.login import TokenPayload
from app.schemas.occlusion_masks import OcclusionMaskRead
from app.schemas.poses import PoseCreate, PoseRead, PoseUpdate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new pose for a camera")
async def create_pose(
    payload: Annotated[PoseCreate, Body()],
    poses: Annotated[PoseCRUD, Depends(get_pose_crud)],
    cameras: Annotated[CameraCRUD, Depends(get_camera_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT])],
) -> PoseRead:
    telemetry_client.capture(
        token_payload.sub,
        event="poses-create",
        properties={"camera_id": payload.camera_id, "azimuth": payload.azimuth},
    )

    camera = cast(Camera, await cameras.get(payload.camera_id, strict=True))

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    db_pose = await poses.create(payload)
    return PoseRead(**db_pose.model_dump())


@router.get("/{pose_id}", status_code=status.HTTP_200_OK, summary="Fetch information of a specific pose")
async def get_pose(
    pose_id: Annotated[int, Path(gt=0)],
    poses: Annotated[PoseCRUD, Depends(get_pose_crud)],
    cameras: Annotated[CameraCRUD, Depends(get_camera_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER])],
) -> PoseRead:
    telemetry_client.capture(token_payload.sub, event="poses-get", properties={"pose_id": pose_id})

    pose = cast(Pose, await poses.get(pose_id, strict=True))
    camera = cast(Camera, await cameras.get(pose.camera_id, strict=True))

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    return PoseRead(**pose.model_dump())


@router.patch("/{pose_id}", status_code=status.HTTP_200_OK, summary="Update a pose")
async def update_pose(
    pose_id: Annotated[int, Path(gt=0)],
    payload: Annotated[PoseUpdate, Body()],
    poses: Annotated[PoseCRUD, Depends(get_pose_crud)],
    cameras: Annotated[CameraCRUD, Depends(get_camera_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.AGENT, UserRole.ADMIN])],
) -> PoseRead:
    pose = cast(Pose, await poses.get(pose_id, strict=True))
    camera = cast(Camera, await cameras.get(pose.camera_id, strict=True))

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    db_pose = await poses.update(pose_id, payload)
    return PoseRead(**db_pose.model_dump())


@router.delete("/{pose_id}", status_code=status.HTTP_200_OK, summary="Delete a pose")
async def delete_pose(
    pose_id: Annotated[int, Path(gt=0)],
    poses: Annotated[PoseCRUD, Depends(get_pose_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> None:
    telemetry_client.capture(token_payload.sub, event="poses-deletion", properties={"pose_id": pose_id})
    await poses.delete(pose_id)


@router.get(
    "/{pose_id}/occlusion_masks",
    status_code=status.HTTP_200_OK,
    summary="List occlusion masks for a pose",
)
async def list_pose_masks(
    pose_id: Annotated[int, Path(gt=0)],
    masks: Annotated[OcclusionMaskCRUD, Depends(get_occlusion_mask_crud)],
    poses: Annotated[PoseCRUD, Depends(get_pose_crud)],
    cameras: Annotated[CameraCRUD, Depends(get_camera_crud)],
    token_payload: Annotated[TokenPayload, Security(
        get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER, Role.CAMERA]
    )],
) -> list[OcclusionMaskRead]:
    telemetry_client.capture(token_payload.sub, event="occlusion_masks-list", properties={"pose_id": pose_id})
    pose = cast(Pose, await poses.get(pose_id, strict=True))
    camera = cast(Camera, await cameras.get(pose.camera_id, strict=True))

    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    rows = await masks.get_by_pose(pose_id)
    return [OcclusionMaskRead(**row.model_dump()) for row in rows]
