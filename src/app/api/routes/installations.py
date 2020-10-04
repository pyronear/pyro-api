from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import installations
from app.api.schemas import InstallationOut, InstallationIn


router = APIRouter()


@router.post("/", response_model=InstallationOut, status_code=201)
async def create_installation(payload: InstallationIn):
    return await routing.create_entry(installations, payload)


@router.get("/{id}/", response_model=InstallationOut)
async def get_installation(id: int = Path(..., gt=0)):
    return await routing.get_entry(installations, id)


@router.get("/", response_model=List[InstallationOut])
async def fetch_installations():
    return await routing.fetch_entries(installations)


@router.put("/{id}/", response_model=InstallationOut)
async def update_installation(payload: InstallationIn, id: int = Path(..., gt=0)):
    return await routing.update_entry(installations, payload, id)


@router.delete("/{id}/", response_model=InstallationOut)
async def delete_installation(id: int = Path(..., gt=0)):
    return await routing.delete_entry(installations, id)
