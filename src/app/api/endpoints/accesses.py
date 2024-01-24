# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import APIRouter, Path, Security

from app.api import crud
from app.api.deps import get_current_access
from app.db import accesses
from app.models import AccessType
from app.schemas.accesses import AccessRead

router = APIRouter()


@router.get("/{access_id}/", response_model=AccessRead, summary="Get information about a specific access")
async def get_access(access_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a access_id, retrieves information about the specified access
    """
    return await crud.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead], summary="Get the list of all accesses")
async def fetch_accesses(_=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Retrieves the list of all accesses and their information
    """
    return await crud.fetch_all(accesses)
