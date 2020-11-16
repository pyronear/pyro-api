from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import sites
from app.api.schemas import SiteOut, SiteIn


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201, summary="Create a new site")
async def create_site(payload: SiteIn):
    """
    Create a new site based on the given information:

    - **lon**: longitude of the site
    - **lat**: latitude of the site
    - **name**: name
    - **type**: type of the site chosen in {"tower", "station"}

    Below, click on "Schema" for more detailed information about fields
    or "Example Value" to get a concrete idea of inputs fields
    """
    return await routing.create_entry(sites, payload)


@router.get("/{site_id}/", response_model=SiteOut, summary="Get information of a given site")
async def get_site(site_id: int = Path(..., gt=0)):
    """
    Based on a site_id, get information about the given site
    """
    return await routing.get_entry(sites, site_id)


@router.get("/", response_model=List[SiteOut], summary="Get the list of all sites")
async def fetch_sites():
    """
    Get the list of all sites with each related information
    """
    return await routing.fetch_entries(sites)


@router.put("/{site_id}/", response_model=SiteOut, summary="Update information of a given site")
async def update_site(payload: SiteIn, site_id: int = Path(..., gt=0)):
    """
    Based on a site_id, update information about the given site
    """
    return await routing.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut, summary="Delete a given site")
async def delete_site(site_id: int = Path(..., gt=0)):
    """
    Based on a site_id, delete the given site
    """
    return await routing.delete_entry(sites, site_id)
