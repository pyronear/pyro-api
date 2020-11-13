from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import accesses
from app.api.schemas import AccessBase, AccessRead, AccessAuth


router = APIRouter()


@router.post("/", response_model=AccessRead, status_code=201)
async def create_access(payload: AccessAuth):
    return await routing.create_access(payload)


@router.get("/{access_id}/", response_model=AccessRead)
async def get_access(access_id: int = Path(..., gt=0)):
    return await routing.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead])
async def fetch_accesses():
    return await routing.fetch_entries(accesses)


@router.put("/{access_id}/", response_model=AccessRead)
async def update_access(payload: AccessBase, access_id: int = Path(..., gt=0)):
    return await routing.update_entry(accesses, payload, access_id)


@router.delete("/{access_id}/", response_model=AccessRead)
async def delete_access(access_id: int = Path(..., gt=0)):
    return await routing.delete_entry(accesses, access_id)
