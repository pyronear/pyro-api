# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from fastapi import APIRouter, Depends, Security, status

from app.api.dependencies import get_jwt, get_site_crud
from app.crud import SiteCRUD
from app.models import Site, UserRole
from app.schemas.login import TokenPayload
from app.schemas.sites import SiteCreate
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new camera")
async def register_camera(
    payload: SiteCreate,
    sites: SiteCRUD = Depends(get_site_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> Site:
    telemetry_client.capture(token_payload.sub, event="site-create", properties={"device_login": payload.name})
    return await sites.create(payload)
