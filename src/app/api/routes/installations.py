from typing import List
from fastapi import APIRouter, Path
from app.api import crud
from app.db import installations
from app.api.schemas import InstallationOut, InstallationIn


router = APIRouter()


@router.post("/", response_model=InstallationOut, status_code=201)
async def create_installation(payload: InstallationIn):
    return await crud.create_entry(installations, payload)


@router.get("/{installation_id}/", response_model=InstallationOut)
async def get_installation(installation_id: int = Path(..., gt=0)):
    return await crud.get_entry(installations, installation_id)


@router.get("/", response_model=List[InstallationOut])
async def fetch_installations():
    return await crud.fetch_all(installations)


@router.put("/{installation_id}/", response_model=InstallationOut)
async def update_installation(payload: InstallationIn, installation_id: int = Path(..., gt=0)):
    return await crud.update_entry(installations, payload, installation_id)


@router.delete("/{installation_id}/", response_model=InstallationOut)
async def delete_installation(installation_id: int = Path(..., gt=0)):
    return await crud.delete_entry(installations, installation_id)
