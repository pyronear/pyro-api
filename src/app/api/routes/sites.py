from typing import List
from fastapi import APIRouter, Path
from app.api import crud
from app.db import sites
from app.api.schemas import SiteOut, SiteIn


router = APIRouter()


@router.post("/", response_model=SiteOut, status_code=201)
async def create_site(payload: SiteIn):
    return await crud.create_entry(sites, payload)


@router.get("/{site_id}/", response_model=SiteOut)
async def get_site(site_id: int = Path(..., gt=0)):
    return await crud.get_entry(sites, site_id)


@router.get("/", response_model=List[SiteOut])
async def fetch_sites():
    return await crud.fetch_all(sites)


@router.put("/{site_id}/", response_model=SiteOut)
async def update_site(payload: SiteIn, site_id: int = Path(..., gt=0)):
    return await crud.update_entry(sites, payload, site_id)


@router.delete("/{site_id}/", response_model=SiteOut)
async def delete_site(site_id: int = Path(..., gt=0)):
    return await crud.delete_entry(sites, site_id)
