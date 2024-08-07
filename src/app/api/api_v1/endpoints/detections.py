# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import hashlib
from datetime import datetime
from mimetypes import guess_extension
from typing import List, cast

import magic
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Security, UploadFile, status

from app.api.dependencies import get_camera_crud, get_detection_crud, get_jwt
from app.crud import CameraCRUD, DetectionCRUD
from app.models import Camera, Detection, Role, UserRole
from app.schemas.detections import DetectionCreate, DetectionLabel, DetectionUrl
from app.schemas.login import TokenPayload
from app.services.storage import s3_bucket
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new wildfire detection")
async def create_detection(
    azimuth: float = Form(..., gt=0, lt=360, description="angle between north and direction in degrees"),
    file: UploadFile = File(..., alias="file"),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Detection:
    telemetry_client.capture(f"camera|{token_payload.sub}", event="detections-create")
    # Upload media
    # Concatenate the first 8 chars (to avoid system interactions issues) of SHA256 hash with file extension
    sha_hash = hashlib.sha256(file.file.read()).hexdigest()
    await file.seek(0)
    # Use MD5 to verify upload
    md5_hash = hashlib.md5(file.file.read()).hexdigest()  # noqa S324
    await file.seek(0)
    # guess_extension will return none if this fails
    extension = guess_extension(magic.from_buffer(file.file.read(), mime=True)) or ""
    # Concatenate timestamp & hash
    bucket_key = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sha_hash[:8]}{extension}"
    # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    await file.seek(0)
    # Failed upload
    if not (await s3_bucket.upload_file(bucket_key, file.file)):  # type: ignore[arg-type]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed upload")
    # Data integrity check
    file_meta = await s3_bucket.get_file_metadata(bucket_key)
    # Corrupted file
    if md5_hash != file_meta["ETag"].replace('"', ""):
        # Delete the corrupted upload
        await s3_bucket.delete_file(bucket_key)
        # Raise the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data was corrupted during upload",
        )

    return await detections.create(DetectionCreate(camera_id=token_payload.sub, bucket_key=bucket_key, azimuth=azimuth))


@router.get("/{detection_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific detection")
async def get_detection(
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Detection:
    telemetry_client.capture(token_payload.sub, event="detections-get", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        return detection

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return detection


@router.get("/{detection_id}/url", response_model=DetectionUrl, status_code=200)
async def get_detection_url(
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> DetectionUrl:
    """Resolve the temporary media image URL"""
    telemetry_client.capture(token_payload.sub, event="detections-url", properties={"detection_id": detection_id})
    # Check in DB
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        return DetectionUrl(url=await s3_bucket.get_public_url(detection.bucket_key))

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    # Check in bucket
    return DetectionUrl(url=await s3_bucket.get_public_url(detection.bucket_key))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the detections")
async def fetch_detections(
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Detection]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch")
    if UserRole.ADMIN in token_payload.scopes:
        return [elt for elt in await detections.fetch_all()]

    cameras_list = await cameras.fetch_all(("organization_id", token_payload.organization_id))
    camera_ids = [camera.id for camera in cameras_list]

    return await detections.get_in(camera_ids, "camera_id")


@router.patch("/{detection_id}/label", status_code=status.HTTP_200_OK, summary="Label the nature of the detection")
async def label_detection(
    payload: DetectionLabel,
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Detection:
    telemetry_client.capture(token_payload.sub, event="detections-label", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        return await detections.update(detection_id, payload)

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return await detections.update(detection_id, payload)


@router.delete("/{detection_id}", status_code=status.HTTP_200_OK, summary="Delete a detection")
async def delete_detection(
    detection_id: int = Path(..., gt=0),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="detections-deletion", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))
    await s3_bucket.delete_file(detection.bucket_key)
    await detections.delete(detection_id)
