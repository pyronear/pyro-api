from typing import List
from fastapi import APIRouter, Path
from app.api import crud
from app.db import accesses
from app.api.schemas import AccessRead


router = APIRouter()


@router.get("/{access_id}/", response_model=AccessRead, summary="Get information about a specific access")
async def get_access(access_id: int = Path(..., gt=0)):
    """
    Based on a access_id, retrieves information about the specified access
    """
    return await crud.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead], summary="Get the list of all accesses")
async def fetch_accesses():
    """
    Retrieves the list of all accesses and their information
    """
    return await crud.fetch_all(accesses)
