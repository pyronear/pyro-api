from typing import List
from fastapi import APIRouter, HTTPException, Path
from . import crud
from .schemas import SiteIn, SiteOut


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201)
async def create_site(payload: SiteIn):
    _id = await crud.post(payload)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=SiteOut)
async def get_site(id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Site not found")
    return entry


@router.get("/", response_model=List[SiteOut])
async def fetch_sites():
    return await crud.get_all()


@router.put("/{id}/", response_model=SiteOut)
async def update_site(payload: SiteIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Site not found")

    _id = await crud.put(id, payload)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=SiteOut)
async def delete_site(id: int = Path(..., gt=0)):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Site not found")

    await crud.delete(id)

    return entry
