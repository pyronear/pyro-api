from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import media
from app.api.schemas import MediaOut, MediaIn


router = APIRouter()


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
