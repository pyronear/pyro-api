from fastapi import APIRouter, Path, Security, File, UploadFile, HTTPException
from typing import List
from datetime import datetime

from app.api import crud
from app.db import media
from app.api.schemas import MediaOut, MediaIn, MediaCreation, DeviceOut, BaseMedia
from app.api.deps import get_current_device
from app.services import bucket_service
import app.config as cfg

router = APIRouter()


@router.post("/", response_model=MediaOut, status_code=201, summary="Create a media related to a specific device")
async def create_media(payload: MediaIn):
    """
    Creates a media related to specific device, based on device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    bucket_key = hash(datetime.utcnow())
    return await crud.create_entry(media, MediaCreation(**payload.dict(), bucket_key=bucket_key))


@router.post("/from-device", response_model=MediaOut, status_code=201,
             summary="Create a media related to the authentified device")
async def create_media_from_device(payload: BaseMedia,
                                   device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Creates a media related to the authentified device, uses its device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    bucket_key = hash(datetime.utcnow())
    return await crud.create_entry(media, MediaCreation(**payload.dict(), bucket_key=bucket_key, device_id=device.id))


@router.get("/{media_id}/", response_model=MediaOut, summary="Get information about a specific media")
async def get_media(media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, retrieves information about the given media
    """
    return await crud.get_entry(media, media_id)


@router.get("/", response_model=List[MediaOut], summary="Get the list of all media")
async def fetch_media():
    """
    Retrieves the list of all media with each related information
    """
    return await crud.fetch_all(media)


@router.put("/{media_id}/", response_model=MediaOut, summary="Update information about a specific media")
async def update_media(payload: MediaIn, media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, updates information about the given media
    """
    return await crud.update_entry(media, payload, media_id)


@router.delete("/{media_id}/", response_model=MediaOut, summary="Delete a specific media")
async def delete_media(media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, deletes the given media
    """
    return await crud.delete_entry(media, media_id)


@router.post("/{media_id}/upload", response_model=MediaOut, status_code=200)
async def upload_media(media_id: int = Path(..., gt=0),
                       file: UploadFile = File(...),
                       current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    existing_media = await crud.fetch_one(media, {"id": media_id, "device_id": current_device.id})
    if existing_media is None:
        raise HTTPException(
            status_code=400,
            detail="Permission denied"
        )

    bucket_key = existing_media["bucket_key"]
    upload_success = await bucket_service.upload_file(bucket_name=cfg.BUCKET_NAME,
                                                      bucket_key=bucket_key,
                                                      file_binary=file.file)
    if upload_success is False:
        raise HTTPException(
            status_code=500,
            detail="The upload did not succeed"
        )
    return existing_media
