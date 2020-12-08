from typing import List
from fastapi import APIRouter, Path, Security
from app.api import crud
from app.db import sites
from app.api.schemas import SiteOut, SiteIn
from app.api.deps import get_current_access


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201, summary="Create a new site")
async def create_site(payload: SiteIn, _=Security(get_current_access, scopes=["admin"])):
    """Creates a new site based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(sites, payload)


@router.get("/{site_id}/", response_model=SiteOut, summary="Get information about a specific site")
async def get_site(site_id: int = Path(..., gt=0)):
    """
    Based on a site_id, retrieves information about the specified site
    """
    return await crud.get_entry(sites, site_id)


@router.get("/", response_model=List[SiteOut], summary="Get the list of all sites")
async def fetch_sites():
    """
    Retrieves the list of all sites and their information
    """
    return await crud.fetch_all(sites)


@router.put("/{site_id}/", response_model=SiteOut, summary="Update information about a specific site")
async def update_site(
    payload: SiteIn,
    site_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=["admin"])
):
    """
    Based on a site_id, updates information about the specified site
    """
    return await crud.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut, summary="Delete a specific site")
async def delete_site(site_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Based on a site_id, deletes the specified site
    """
    return await crud.delete_entry(sites, site_id)
