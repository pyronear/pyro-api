from typing import List
from fastapi import APIRouter, HTTPException, Path
from . import crud
from .schemas import MediaIn, MediaOut


router = APIRouter()


@router.post("/", response_model=MediaOut, status_code=201)
async def create_media(payload: MediaIn):
    _id = await crud.post(payload)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=MediaOut)
async def get_media(id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")
    return entry


@router.get("/", response_model=List[MediaOut])
async def fetch_medias():
    return await crud.get_all()


@router.put("/{id}/", response_model=MediaOut)
async def update_media(payload: MediaIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    _id = await crud.put(id, payload)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=MediaOut)
async def delete_media(id: int = Path(..., gt=0)):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    await crud.delete(id)

    return entry
