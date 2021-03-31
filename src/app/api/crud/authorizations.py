# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List, Dict, Mapping, Any
from sqlalchemy import Table
from fastapi import HTTPException

from app.api import crud
from app.api.schemas import AccessType
from app.db import accesses


async def is_in_same_group(table: Table, entry_id: int, group_id: int) -> bool:
    user_or_device = await crud.base.get_entry(table, entry_id)
    return await is_access_in_same_group(user_or_device.access_id, group_id)


async def is_access_in_same_group(access_id: int, group_id: int) -> bool:
    access = await crud.base.get_entry(accesses, access_id)
    return await are_same_group(access.group_id, group_id)


async def are_same_group(group_id_a: int, group_id_b: int) -> bool:
    if group_id_a != group_id_b:
        raise HTTPException(status_code=400, detail="You don't belong to the same group")
    return True


async def is_admin_access(access_id: int) -> bool:
    access = await crud.base.get_entry(accesses, access_id)
    return access.scope == AccessType.admin
