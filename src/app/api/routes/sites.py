from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import sites
from app.api.schemas import SiteOut, SiteIn


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201)
async def create_site(payload: SiteIn):
    return await routing.create_entry(sites, payload)


@router.get("/{site_id}/", response_model=SiteOut)
async def get_site(site_id: int = Path(..., gt=0)):
    return await routing.get_entry(sites, site_id)


@router.get("/", response_model=List[SiteOut])
async def fetch_sites():
    return await routing.fetch_entries(sites)


@router.put("/{site_id}/", response_model=SiteOut)
async def update_site(payload: SiteIn, site_id: int = Path(..., gt=0)):
    return await routing.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut)
async def delete_site(site_id: int = Path(..., gt=0)):
    return await routing.delete_entry(sites, site_id)
