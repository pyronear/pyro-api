# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from mimetypes import guess_extension
from typing import Any, Dict, List, Optional, cast

import magic
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Path, Security, UploadFile, status

from app.api import crud
from app.api.crud.authorizations import check_group_read, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_current_device, get_db
from app.api.security import hash_content_file
from app.db import devices, media
from app.models import Access, AccessType, Device, Media
from app.schemas import BaseMedia, DeviceOut, MediaCreation, MediaIn, MediaOut, MediaUrl
from app.services import resolve_bucket_key, s3_bucket
from app.services.telemetry import telemetry_client

router = APIRouter()


async def check_media_registration(media_id: int, device_id: Optional[int] = None) -> Dict[str, Any]:
    """Checks whether the media is registered in the DB"""
    if device_id is None:
        media_dict = await crud.get_entry(media, media_id)
    else:
        media_dict = await crud.fetch_one(media, {"id": media_id, "device_id": device_id})  # type: ignore[assignment]
        if media_dict is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to find media with id={media_id} & device_id={device_id}",
            )
    return media_dict


@router.post(
    "/",
    response_model=MediaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a media related to a specific device",
)
async def create_media(payload: MediaIn, access=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Creates a media related to specific device, based on device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(access.id, event="media-create")
    # Check that the device exits
    await crud.get_entry(devices, payload.device_id)
    return await crud.create_entry(media, payload)


@router.post(
    "/from-device",
    response_model=MediaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a media related to the authentified device",
)
async def create_media_from_device(
    payload: BaseMedia, device: DeviceOut = Security(get_current_device, scopes=[AccessType.device])
):
    """
    Creates a media related to the authentified device, uses its device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(device.id, event="media-create-from-device", properties={"owner_id": device.owner_id})
    return await crud.create_entry(media, MediaIn(**payload.model_dump(), device_id=device.id))


@router.get("/{media_id}/", response_model=MediaOut, summary="Get information about a specific media")
async def get_media(
    media_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a media_id, retrieves information about the specified media
    """
    telemetry_client.capture(requester.id, event="media-get", properties={"media_id": media_id})
    # TODO: confirm this one
    requested_group_id = await get_entity_group_id(media, media_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(media, media_id)


@router.get("/", response_model=List[MediaOut], summary="Get the list of all media")
async def fetch_media(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all media and their information
    """
    telemetry_client.capture(requester.id, event="media-fetch")
    if await is_admin_access(requester.id):
        return await crud.fetch_all(media)
    else:
        retrieved_media = (
            session.query(Media).join(Device).join(Access).filter(Access.group_id == requester.group_id).all()
        )
        retrieved_media = [x.__dict__ for x in retrieved_media]
        return retrieved_media


@router.delete("/{media_id}/", response_model=MediaOut, summary="Delete a specific media")
async def delete_media(media_id: int = Path(..., gt=0), access=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a media_id, deletes the specified media
    """
    telemetry_client.capture(access.id, event="media-delete", properties={"media_id": media_id})
    # Delete entry
    entry = await crud.delete_entry(media, media_id)
    # Delete media file if one exists
    if isinstance(entry["bucket_key"], str) and len(entry["bucket_key"]) > 0:
        await s3_bucket.delete_file(entry["bucket_key"])
    return entry


@router.post("/{media_id}/upload", response_model=MediaOut, status_code=200)
async def upload_media_from_device(
    background_tasks: BackgroundTasks,
    media_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    device: DeviceOut = Security(get_current_device, scopes=[AccessType.device]),
):
    """
    Upload a media (image or video) linked to an existing media object in the DB
    """
    telemetry_client.capture(
        device.id, event="media-upload", properties={"media_id": media_id, "owner_id": device.owner_id}
    )
    # Check in DB
    entry = await check_media_registration(media_id, device.id)

    # Concatenate the first 8 chars (to avoid system interactions issues) of SHA256 hash with file extension
    sha_hash = hash_content_file(file.file.read())
    await file.seek(0)
    # Use MD5 to verify upload
    md5_hash = hash_content_file(file.file.read(), use_md5=True)
    await file.seek(0)
    # guess_extension will return none if this fails
    extension = guess_extension(magic.from_buffer(file.file.read(), mime=True)) or ""
    # Concatenate timestamp & hash
    file_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sha_hash[:8]}{extension}"
    # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    await file.seek(0)
    # If files are in a subfolder of the bucket, prepend the folder path
    bucket_key = resolve_bucket_key(file_name)

    # Upload if bucket_key is different (otherwise the content is the exact same)
    if isinstance(entry["bucket_key"], str) and entry["bucket_key"] == bucket_key:
        return await crud.get_entry(media, media_id)
    else:
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
        # If a file was previously uploaded, delete it
        if isinstance(entry["bucket_key"], str):
            await s3_bucket.delete_file(entry["bucket_key"])

        entry_dict = dict(**entry)
        entry_dict["bucket_key"] = bucket_key
        return await crud.update_entry(media, MediaCreation(**entry_dict), media_id)


@router.get("/{media_id}/url", response_model=MediaUrl, status_code=200)
async def get_media_url(
    media_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """Resolve the temporary media image URL"""
    telemetry_client.capture(requester.id, event="media-get-url", properties={"media_id": media_id})
    requested_group_id = await get_entity_group_id(media, media_id)
    await check_group_read(requester.id, cast(int, requested_group_id))

    # Check in DB
    media_instance = await check_media_registration(media_id)
    # Check in bucket
    temp_public_url = await s3_bucket.get_public_url(media_instance["bucket_key"])
    return MediaUrl(url=temp_public_url)
