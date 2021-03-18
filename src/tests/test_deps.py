# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest
from app import db
from app.api import crud, deps, security
from app.api.schemas import AccessRead, UserRead, DeviceOut
from tests.conf_test_db import populate_db
from tests.utils import update_only_datetime


USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "connected_device", "owner_id": 1, "access_id": 3,
     "specs": "raspberry", "elevation": None, "lat": None, "angle_of_view": 68,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_device", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 3, "login": "third_device", "owner_id": 1, "access_id": 5, "specs": "v0.1", "elevation": None,
     "lat": None, "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 2, "login": "connected_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 3, "login": "first_device", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 4, "login": "second_device", "hashed_password": "second_pwd_hashed", "scopes": "device"},
    {"id": 5, "login": "connected_device", "hashed_password": "third_pwd_hashed", "scopes": "device"},
]


ACCESS_TABLE_FOR_DB = list(map(update_only_datetime, ACCESS_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE_FOR_DB)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)
    await populate_db(test_db, db.devices, DEVICE_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_current_user(test_app_asyncio, test_db, monkeypatch):

    await init_test_db(monkeypatch, test_db)

    response = await deps.get_current_user(AccessRead(**ACCESS_TABLE[0]))
    assert response == UserRead(**USER_TABLE_FOR_DB[0])


@pytest.mark.asyncio
async def test_get_current_device(test_app_asyncio, test_db, monkeypatch):

    await init_test_db(monkeypatch, test_db)

    response = await deps.get_current_device(AccessRead(**ACCESS_TABLE[2]))
    assert response == DeviceOut(**DEVICE_TABLE_FOR_DB[0])
