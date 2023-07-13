# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from typing import Optional

from sqlalchemy import Table

from app.api import crud
from app.db import accesses, alerts, devices, events, installations, media, sites, users


async def get_entity_group_id(table: Table, entry_id: int) -> Optional[int]:
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

    raise ValueError(f"Unknown table '{table.name}'")


async def _get_access_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(accesses, entry_id)
    return entry["group_id"]


async def _get_user_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(users, entry_id)
    return await _get_access_group_id(entry["access_id"])


async def _get_site_group_id(entry_id: int) -> int:
    entry = await crud.base.get_entry(sites, entry_id)
    return entry["group_id"]


async def _get_event_group_id(entry_id: int) -> Optional[int]:
    entry = await crud.base.fetch_one(alerts, {"event_id": entry_id})
    if entry is None:
        return None
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
