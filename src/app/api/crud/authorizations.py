# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import Table

from app.api import crud
from app.db import accesses
from app.models import AccessType


async def is_in_same_group(table: Table, entry_id: int, group_id: int) -> bool:
    entity_group_id = await crud.groups.get_entity_group_id(table, entry_id)
    return entity_group_id == group_id


async def is_access_in_group(access_id: int, group_id: int) -> bool:
    access_group_id = await crud.groups.get_entity_group_id(accesses, access_id)
    return access_group_id == group_id


async def is_admin_access(access_id: int) -> bool:
    access = await crud.base.get_entry(accesses, access_id)
    return access["scope"] == AccessType.admin


async def check_group_read(access_id: int, group_id: int) -> bool:
    if (not await is_admin_access(access_id)) and not (await is_access_in_group(access_id, group_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"This access can't read resources from group_id={group_id}"
        )
    return True


async def check_group_update(access_id: int, group_id: Optional[int]) -> bool:
    if (
        (group_id is not None)
        and (not await is_admin_access(access_id))
        and (not await is_access_in_group(access_id, group_id))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"This access can't update resources for group_id={group_id}"
        )
    return True
