from fastapi import APIRouter, Path, Security, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime

from app.api import crud
from app.db import media
from app.api.schemas import MediaOut, MediaIn, MediaCreation, MediaUrl, DeviceOut, BaseMedia
from app.api.deps import get_current_device, get_current_user
from app.api.security import hash_content_file
from app.services import bucket_service, resolve_bucket_key


router = APIRouter()


async def check_media_registration(media_id: int, device_id: Optional[int] = None) -> MediaOut:
    """Checks whether the media is registered in the DB"""
    filters = {"id": media_id}
    if device_id is not None:
        filters.update({"device_id": device_id})

    existing_media = await crud.fetch_one(media, filters)
    if existing_media is None:
        raise HTTPException(
            status_code=400,
            detail="Permission denied"
        )
    return existing_media


@router.post("/", response_model=MediaOut, status_code=201, summary="Create a media related to a specific device")
async def create_media(payload: MediaIn):
    """
    Creates a media related to specific device, based on device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(media, payload)


@router.post("/from-device", response_model=MediaOut, status_code=201,
             summary="Create a media related to the authentified device")
async def create_media_from_device(payload: BaseMedia,
                                   device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Creates a media related to the authentified device, uses its device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(media, MediaIn(**payload.dict(), device_id=device.id))


@router.get("/{media_id}/", response_model=MediaOut, summary="Get information about a specific media")
async def get_media(media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, retrieves information about the specified media
    """
    return await crud.get_entry(media, media_id)


@router.get("/", response_model=List[MediaOut], summary="Get the list of all media")
async def fetch_media():
    """
    Retrieves the list of all media and their information
    """
    return await crud.fetch_all(media)


@router.put("/{media_id}/", response_model=MediaOut, summary="Update information about a specific media")
async def update_media(payload: MediaIn, media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, updates information about the specified media
    """
    return await crud.update_entry(media, payload, media_id)


@router.delete("/{media_id}/", response_model=MediaOut, summary="Delete a specific media")
async def delete_media(media_id: int = Path(..., gt=0)):
    """
    Based on a media_id, deletes the specified media
    """
    return await crud.delete_entry(media, media_id)


@router.post("/{media_id}/upload", response_model=MediaOut, status_code=200)
async def upload_media(media_id: int = Path(..., gt=0),
                       file: UploadFile = File(...),
                       current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Upload a media (image or video) linked to an existing media object in the DB
    """
    entry = await check_media_registration(media_id, current_device.id)

    # Concatenate the first 32 chars (to avoid system interactions issues) of SHA256 hash with file extension
    file_name = f"{hash_content_file(file.file.read())[:32]}.{file.filename.rpartition('.')[-1]}"
    # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    await file.seek(0)
    # If files are in a subfolder of the bucket, prepend the folder path
    bucket_key = resolve_bucket_key(file_name)

    upload_success = await bucket_service.upload_file(bucket_key=bucket_key,
                                                      file_binary=file.file)
    if not upload_success:
        raise HTTPException(
            status_code=500,
            detail="The upload did not succeed"
        )
    entry = dict(**entry)
    entry["bucket_key"] = bucket_key
    return await crud.update_entry(media, MediaCreation(**entry), media_id)


@router.get("/{media_id}/url", response_model=MediaUrl, status_code=200)
async def get_media_url(background_tasks: BackgroundTasks,
                        media_id: int = Path(..., gt=0),
                        _=Security(get_current_user, scopes=["admin"])):
    """
    Retrieve the media image url
    """
    # Check in DB
    media = await check_media_registration(media_id)
    # Check in bucket
    exist_on_bucket = await bucket_service.is_file(media['bucket_key'])
    if not exist_on_bucket:
        raise HTTPException(
            status_code=500,
            detail="File cannot be found on the bucket storage"
        )
    return {"url": media['bucket_key']}


@router.get("/{media_id}/image", status_code=200)
async def get_media_image(background_tasks: BackgroundTasks,
                          media_id: int = Path(..., gt=0),
                          _=Security(get_current_user, scopes=["admin"])):
    """
    Retrieve the media image as encoded in bytes
    """
    # Check in DB
    media = await check_media_registration(media_id)
    # Download the file temporarily and get its local path
    retrieved_file = await bucket_service.get_file(bucket_key=media["bucket_key"])
    if retrieved_file is None:
        raise HTTPException(
            status_code=500,
            detail="The download did not succeed"
        )
    background_tasks.add_task(bucket_service.flush_tmp_file, retrieved_file)
    return StreamingResponse(open(retrieved_file, 'rb'), media_type="image/jpeg")
