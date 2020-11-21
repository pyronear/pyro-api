
from fastapi import APIRouter, Path, Security, File, UploadFile
from app.api import crud
from app.db import media
from typing import List
from app.api.schemas import MediaOut, MediaIn, DeviceOut
from app.api.deps import get_current_device
from app.services import bucket_service


router = APIRouter()


@router.post("/upload_file", response_model=MediaOut, status_code=201)
async def upload_media(file: UploadFile = File(...),
                       current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    bucket_service.upload_file("mypyroneartest", file.filename, file.file)
    media_created = MediaIn(device_id=current_device.id)
    return await crud.create_entry(media, media_created)


@router.post("/", response_model=MediaOut, status_code=201, summary="Create a media related to a specific device")
async def create_media(payload: MediaIn):
    """
    Creates a media related to specific device, based on device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(media, payload)


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
