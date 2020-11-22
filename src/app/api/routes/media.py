from typing import List
from fastapi import APIRouter, Path
from app.api import crud
from app.db import media
from app.api.schemas import MediaOut, MediaIn


router = APIRouter()


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
