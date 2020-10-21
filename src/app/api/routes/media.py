from typing import List
from fastapi import APIRouter, Path, Security, File, UploadFile
from app.api import routing
from app.db import media
from app.api.schemas import MediaOut, MediaIn, UserInDb
from app.api.deps import get_current_user
from app.services.bucketService import bucket_service


router = APIRouter()


@router.post("/upload_file", response_model=MediaOut, status_code=201)
async def create_media(file: UploadFile = File(...)), device_user: UserInDb = Security(get_current_user, scopes=["device"]):
    bucket_service.upload_file("mypyroneartest", file.filename, file.file)
    MediaIn(device_id=device_user.id)
    return await routing.create_entry(media, payload)

@router.post("/", response_model=MediaOut, status_code=201)
async def create_media(payload: MediaIn):
    return await routing.create_entry(media, payload)

@router.get("/{id}/", response_model=MediaOut)
async def get_media(id: int = Path(..., gt=0)):
    return await routing.get_entry(media, id)


@router.get("/", response_model=List[MediaOut])
async def fetch_media():
    return await routing.fetch_entries(media)


@router.put("/{id}/", response_model=MediaOut)
async def update_media(payload: MediaIn, id: int = Path(..., gt=0)):
    return await routing.update_entry(media, payload, id)


@router.delete("/{id}/", response_model=MediaOut)
async def delete_media(id: int = Path(..., gt=0)):
    return await routing.delete_entry(media, id)
