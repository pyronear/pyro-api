"""Access route read-only for debugging purpose, aims to be removed"""

from typing import List
from fastapi import APIRouter, Path
from app.api import crud
from app.db import accesses
from app.api.schemas import AccessRead


router = APIRouter()


@router.get("/{access_id}/", response_model=AccessRead)
async def get_access(access_id: int = Path(..., gt=0)):
    return await crud.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead])
async def fetch_accesses():
    return await crud.fetch_all(accesses)
