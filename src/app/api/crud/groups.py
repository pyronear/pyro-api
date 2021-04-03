# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


from typing import List, Dict, Mapping, Any
from sqlalchemy import Table
from fastapi import HTTPException, status

from app.api import crud
from app.api.schemas import AccessType
from app.db import (
    accesses, users, groups,
    sites, events, devices, media,
    installations, alerts)


async def get_entity_group_id(table: Table, entry_id: int) -> int:

    if table == accesses:
        return await _get_access_group_id(entry_id)
    elif table == users:
        return await _get_user_group_id(entry_id)
    elif table == sites:
        return await _get_site_group_id(entry_id)
    elif table == events:
        return await _get_event_group_id(entry_id)
    elif table == devices:
        return await _get_device_group_id(entry_id)
    elif table == media:
        return await _get_media_group_id(entry_id)
    elif table == installations:
        return await _get_installation_group_id(entry_id)
    elif table == alerts:
        return await _get_alert_group_id(entry_id)

    raise f"{table} is not an existing entity"


async def _get_access_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(accesses, entry_id)
    return entry["group_id"]


async def _get_user_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(users, entry_id)
    return await _get_access_group_id(entry["access_id"])


async def _get_site_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(sites, entry_id)
    return entry["group_id"]


async def _get_event_group_id(entry_id: int) -> int:
    entry = await crud.base.fetch_one(alerts, {"event_id": entry_id})
    return await _get_device_group_id(entry["device_id"])


async def _get_device_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(devices, entry_id)
    return await _get_access_group_id(entry["access_id"])


async def _get_media_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(media, entry_id)
    return await _get_device_group_id(entry["device_id"])


async def _get_installation_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(installations, entry_id)
    return await _get_site_group_id(entry["site_id"])


async def _get_alert_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(alerts, entry_id)
    return await _get_device_group_id(entry["device_id"])
