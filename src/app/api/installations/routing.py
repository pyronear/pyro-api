from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.api import crud
from app.db import installations
from .schemas import InstallationIn, InstallationOut


router = APIRouter()


@router.post("/", response_model=InstallationOut, status_code=201)
async def create_installation(payload: InstallationIn):
    _id = await crud.post(payload, installations)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=InstallationOut)
async def get_installation(id: int = Path(..., gt=0),):
    entry = await crud.get(id, installations)
    if not entry:
        raise HTTPException(status_code=404, detail="Installation not found")
    return entry


@router.get("/", response_model=List[InstallationOut])
async def fetch_installations():
    return await crud.fetch_all(installations)


@router.put("/{id}/", response_model=InstallationOut)
async def update_installation(payload: InstallationIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id, installations)
    if not entry:
        raise HTTPException(status_code=404, detail="Installation not found")

    _id = await crud.put(id, payload, installations)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=InstallationOut)
async def delete_installation(id: int = Path(..., gt=0)):
    entry = await crud.get(id, installations)
    if not entry:
        raise HTTPException(status_code=404, detail="Installation not found")

    await crud.delete(id, installations)

    return entry
