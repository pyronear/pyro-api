# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.db_utils import get_entry, fill_table
from tests.utils import update_only_datetime, parse_time


USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"},
    {"id": 3, "name": "third_groupd"},
    {"id": 4, "name": "gourth_group"}
]


DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68.,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68.,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 4, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
]

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": "2021-03-13T10:18:45.447773",
     "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "is_acknowledged": True, "created_at": "2020-09-13T08:18:45.447773"},
    {"id": 3, "lat": -5., "lon": 3., "type": "wildfire", "start_ts": "2021-03-13T08:18:45.447773",
     "end_ts": "2021-03-13T10:18:45.447773", "is_acknowledged": False, "created_at": "2020-09-13T08:18:45.447773"},
]

ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8.,
     "azimuth": 123., "created_at": "2020-11-03T11:18:45.447773"},
]
SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "group_id": 1,
     "lat": 44.1, "lon": -0.7, "type": "tower", "country": "FR", "geocode": "40",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "group_id": 2,
     "lat": 44.1, "lon": 3.9, "type": "station", "country": "FR", "geocode": "30",
     "created_at": "2020-09-13T08:18:45.447773"},
]


USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))
SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.media, MEDIA_TABLE_FOR_DB)
    await fill_table(test_db, db.events, EVENT_TABLE_FOR_DB)
    await fill_table(test_db, db.alerts, ALERT_TABLE_FOR_DB)
    await fill_table(test_db, db.sites, SITE_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "entity_id, table, expected_group_id",
    [
        [1, db.accesses, 1],
        [2, db.users, 2],
        [1, db.devices, 3],
        [1, db.media, 3],
        [2, db.events, 4],
        [3, db.alerts, 4],
        [2, db.sites, 2],
    ],
)
@pytest.mark.asyncio
async def test_entity_group_retrieval(test_app_asyncio, init_test_db, entity_id, table, expected_group_id):
    retrieved_group_id = await crud.groups.get_entity_group_id(table, entity_id)
    assert retrieved_group_id == expected_group_id
