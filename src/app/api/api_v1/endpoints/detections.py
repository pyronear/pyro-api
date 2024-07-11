# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import hashlib
import logging
from datetime import datetime
from mimetypes import guess_extension
from typing import List, Optional, cast

import magic
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Security, UploadFile, status

from app.api.dependencies import get_camera_crud, get_detection_crud, get_jwt
from app.crud import CameraCRUD, DetectionCRUD
from app.models import Detection, Role, UserRole
from app.schemas.detections import DetectionCreate, DetectionLabel, DetectionUrl
from app.schemas.login import TokenPayload
from app.services.storage import s3_bucket
from app.services.telemetry import telemetry_client

logging.basicConfig(level=logging.ERROR)
logging.getLogger("uvicorn.error")

router = APIRouter()


def get_bucket_name(organization_id: int) -> str:
    return f"alert-api-{organization_id!s}"


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new wildfire detection")
async def create_detection(
    localization: Optional[str] = Form(None),
    azimuth: float = Form(..., gt=0, lt=360, description="angle between north and direction in degrees"),
    file: UploadFile = File(..., alias="file"),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Detection:
    telemetry_client.capture(f"camera|{token_payload.sub}", event="detections-create")
    try:
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
        bucket_key = f"{token_payload.sub}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sha_hash[:8]}{extension}"
        # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
        await file.seek(0)

        # Check if bucket exists, if not, create it
        bucket_name = get_bucket_name(token_payload.organization_id)
        if not (await s3_bucket.check_bucket(bucket_name)):
            logging.info(f"Bucket {bucket_name} does not exist. Creating bucket.")
            if not (await s3_bucket.create_bucket(bucket_name)):
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bucket")
            logging.info(f"Bucket {bucket_name} created successfully.")

        # Upload the file
        if not (await s3_bucket.upload_file(bucket_key, bucket_name, file.file)):  # type: ignore[arg-type]
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed upload")
        logging.info(f"File uploaded to bucket {bucket_name} with key {bucket_key}.")

        # Data integrity check
        file_meta = await s3_bucket.get_file_metadata(bucket_key, bucket_name)
        # Corrupted file
        if md5_hash != file_meta["ETag"].replace('"', ""):
            # Delete the corrupted upload
            await s3_bucket.delete_file(bucket_key, bucket_name)
            # Raise the exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data was corrupted during upload",
            )
        logging.info(f"Data integrity check passed for file {bucket_key}.")

        # No need to create the Wildfire and Detection in the same commit
        return await detections.create(
            DetectionCreate(
                camera_id=token_payload.sub, bucket_key=bucket_key, azimuth=azimuth, localization=localization
            )
        )
    except Exception as e:  # : BLE001
        logging.exception(f"Error occurred: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


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

    camera = await cameras.get(detection.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
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
        camera = await cameras.get(detection.camera_id)
        if camera is not None:
            return DetectionUrl(
                url=await s3_bucket.get_public_url(detection.bucket_key, get_bucket_name(camera.organization_id))
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No Camera found",
        )

    camera = await cameras.get(detection.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    # Check in bucket
    return DetectionUrl(
        url=await s3_bucket.get_public_url(detection.bucket_key, get_bucket_name(token_payload.organization_id))
    )


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the detections")
async def fetch_detections(
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Detection]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch")
    all_detections = [elt for elt in await detections.fetch_all()]
    if UserRole.ADMIN in token_payload.scopes:
        return all_detections
    filtered_detections = []
    for detection in all_detections:
        camera = await cameras.get(detection.camera_id, strict=True)
        if camera is not None and camera.organization_id == token_payload.organization_id:
            filtered_detections.append(detection)
    return filtered_detections


@router.get("/unacknowledged/from", status_code=status.HTTP_200_OK, summary="Fetch all the unacknowledged detections")
async def fetch_unacknowledged_detections(
    from_date: Optional[datetime] = None,
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Detection]:
    telemetry_client.capture(token_payload.sub, event="unacknowledged-fetch")

    try:
        all_unck_detections = [elt for elt in await detections.fetch_all() if elt.is_wildfire is None]
        if from_date is not None:
            all_unck_detections = [detection for detection in all_unck_detections if detection.created_at >= from_date]
    except Exception as e:  # noqa
        logging.error(f"Error fetching detections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if UserRole.ADMIN in token_payload.scopes:
        return all_unck_detections

    filtered_detections = []
    for detection in all_unck_detections:
        try:
            camera = await cameras.get(detection.camera_id, strict=True)
        except Exception as e:  # noqa
            logging.error(f"Error fetching camera with ID {detection.camera_id}: {e}")
            continue

        if camera is not None and camera.organization_id == token_payload.organization_id:
            filtered_detections.append(detection)

    return filtered_detections


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

    camera = await cameras.get(detection.camera_id, strict=True)
    if (
        camera is not None
        and token_payload.organization_id != camera.organization_id
        and UserRole.ADMIN not in token_payload.scopes
    ):
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
    await s3_bucket.delete_file(detection.bucket_key, get_bucket_name(token_payload.organization_id))
    await detections.delete(detection_id)
