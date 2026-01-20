# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.
import re
from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import (
    get_jwt,
)
from app.crud import CameraCRUD
from app.crud.crud_occlusion_mask import OcclusionMaskCRUD
from app.crud.crud_pose import PoseCRUD
from app.db import get_session
from app.models import Camera, OcclusionMask, Pose, UserRole
from app.schemas.login import TokenPayload
from app.schemas.occlusion_masks import (
    OcclusionMaskCreate,
    OcclusionMaskRead,
    OcclusionMaskUpdate,
)
from app.services.telemetry import telemetry_client

router = APIRouter()

FLOAT_PATTERN = r"(0?\.[0-9]{1,3}|0|1)"
MASK_PATTERN = rf"^\({FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN},{FLOAT_PATTERN}\)$"
mask_regex = re.compile(MASK_PATTERN)


def validate_mask(mask: str) -> None:
    if not mask_regex.match(mask):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Invalid mask format. Expected: (xmin, ymin, xmax, ymax) with float values in [0,1]."),
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create an occlusion mask",
)
async def create_mask(
    payload: Annotated[OcclusionMaskCreate, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[
        TokenPayload,
        Security(
            get_jwt,
            scopes=[UserRole.ADMIN, UserRole.AGENT],
        ),
    ],
) -> OcclusionMaskRead:
    # Validate mask format
    validate_mask(payload.mask)

    pose = cast(Pose, await PoseCRUD(session=session).get(payload.pose_id, strict=True))
    camera = cast(Camera, await CameraCRUD(session=session).get(pose.camera_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    telemetry_client.capture(
        token_payload.sub,
        event="occlusion_masks-create",
        properties={"pose_id": payload.pose_id},
    )

    db_obj = await OcclusionMaskCRUD(session=session).create(payload)
    return OcclusionMaskRead(**db_obj.model_dump())


@router.get(
    "/{mask_id}",
    status_code=status.HTTP_200_OK,
    summary="Get info about an occlusion mask",
)
async def get_mask(
    mask_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[
        TokenPayload,
        Security(
            get_jwt,
            scopes=[UserRole.ADMIN, UserRole.AGENT],
        ),
    ],
) -> OcclusionMaskRead:
    mask = cast(OcclusionMask, await OcclusionMaskCRUD(session=session).get(mask_id, strict=True))
    pose = cast(Pose, await PoseCRUD(session=session).get(mask.pose_id, strict=True))
    camera = cast(Camera, await CameraCRUD(session=session).get(pose.camera_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    telemetry_client.capture(
        token_payload.sub,
        event="occlusion_masks-get",
        properties={"mask_id": mask_id},
    )

    return OcclusionMaskRead(**mask.model_dump())


@router.patch(
    "/{mask_id}",
    status_code=status.HTTP_200_OK,
    summary="Update an occlusion mask",
)
async def update_mask(
    mask_id: Annotated[int, Path(gt=0)],
    payload: Annotated[OcclusionMaskUpdate, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[
        TokenPayload,
        Security(
            get_jwt,
            scopes=[UserRole.ADMIN, UserRole.AGENT],
        ),
    ],
) -> OcclusionMaskRead:
    # Validate mask format
    validate_mask(payload.mask)

    mask = cast(OcclusionMask, await OcclusionMaskCRUD(session=session).get(mask_id, strict=True))
    pose = cast(Pose, await PoseCRUD(session=session).get(mask.pose_id, strict=True))
    camera = cast(Camera, await CameraCRUD(session=session).get(pose.camera_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    telemetry_client.capture(
        token_payload.sub,
        event="occlusion_masks-update",
        properties={"mask_id": mask_id},
    )

    db_obj = await OcclusionMaskCRUD(session=session).update(mask_id, payload)
    return OcclusionMaskRead(**db_obj.model_dump())


@router.delete(
    "/{mask_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an occlusion mask",
)
async def delete_mask(
    mask_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[
        TokenPayload,
        Security(
            get_jwt,
            scopes=[UserRole.ADMIN, UserRole.AGENT],
        ),
    ],
) -> None:
    mask = cast(OcclusionMask, await OcclusionMaskCRUD(session=session).get(mask_id, strict=True))
    pose = cast(Pose, await PoseCRUD(session=session).get(mask.pose_id, strict=True))
    camera = cast(Camera, await CameraCRUD(session=session).get(pose.camera_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    telemetry_client.capture(
        token_payload.sub,
        event="occlusion_masks-delete",
        properties={"mask_id": mask_id},
    )

    await OcclusionMaskCRUD(session=session).delete(mask_id)
