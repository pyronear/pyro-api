from fastapi import APIRouter, Path, Security, File, UploadFile
from app.api import routing
from app.db import media
from typing import List
from app.api.schemas import MediaOut, MediaIn, DeviceOut
from app.api.deps import get_current_device
from app.services.bucketService import bucket_service


router = APIRouter()


@router.post("/upload_file", response_model=MediaOut, status_code=201)
async def upload_media(file: UploadFile = File(...),
                       current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    bucket_service.upload_file("mypyroneartest", file.filename, file.file)
    media_created = MediaIn(device_id=current_device.id)
    return await routing.create_entry(media, media_created)


@router.post("/", response_model=MediaOut, status_code=201)
async def create_media(payload: MediaIn):
    return await routing.create_entry(media, payload)


@router.get("/{media_id}/", response_model=MediaOut)
async def get_media(media_id: int = Path(..., gt=0)):
    return await routing.get_entry(media, media_id)


@router.get("/", response_model=List[MediaOut])
async def fetch_media():
    return await routing.fetch_entries(media)


@router.put("/{media_id}/", response_model=MediaOut)
async def update_media(payload: MediaIn, media_id: int = Path(..., gt=0)):
    return await routing.update_entry(media, payload, media_id)


@router.delete("/{media_id}/", response_model=MediaOut)
async def delete_media(media_id: int = Path(..., gt=0)):
    return await routing.delete_entry(media, media_id)
