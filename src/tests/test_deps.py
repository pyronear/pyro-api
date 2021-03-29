# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest
from fastapi.security import SecurityScopes
from fastapi import HTTPException

from app import db
from app.api import crud, deps, security
from app.api.schemas import AccessRead, UserRead, DeviceOut
from tests.db_utils import fill_table
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
    {"id": 1, "login": "first_user", "hashed_password": "first_pwd_hashed", "scope": "user"},
    {"id": 2, "login": "connected_user", "hashed_password": "first_pwd_hashed", "scope": "user"},
    {"id": 3, "login": "first_device", "hashed_password": "first_pwd_hashed", "scope": "device"},
    {"id": 4, "login": "second_device", "hashed_password": "second_pwd_hashed", "scope": "device"},
    {"id": 5, "login": "connected_device", "hashed_password": "third_pwd_hashed", "scope": "device"},
]


USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "token_data, scope, expected_access, exception",
    [
        [ACCESS_TABLE[3], 'admin', None, True],  # Unsufficient scope
        ['my_false_token', 'admin', None, True],  # Decoding failure
        [{"id": 100, "scopes": "admin"}, 'admin', None, True],  # Unable to find access in table
        [ACCESS_TABLE[3], 'device', 3, False],  # Correct
    ],
)
@pytest.mark.asyncio
async def test_get_current_access(init_test_db, token_data, scope, expected_access, exception):

    # Create a token for the access we'll want to retrieve
    if isinstance(token_data, str):
        token = token_data
    else:
        _data = {"sub": str(token_data['id']), "scopes": token_data['scope'].split()}
        token = await security.create_access_token(_data)
    # Check that we retrieve the correct access
    if exception:
        with pytest.raises(HTTPException):
            access = await deps.get_current_access(SecurityScopes([scope]), token=token)
    else:
        access = await deps.get_current_access(SecurityScopes([scope]), token=token)
        if isinstance(expected_access, int):
            assert access.dict() == AccessRead(**ACCESS_TABLE[expected_access]).dict()


@pytest.mark.parametrize(
    "access_idx, user_idx",
    [
        [1, 1],  # Correct
        [2, None],  # Not a user access
    ],
)
@pytest.mark.asyncio
async def test_get_current_user(init_test_db, access_idx, user_idx):

    if isinstance(user_idx, int):
        response = await deps.get_current_user(AccessRead(**ACCESS_TABLE[access_idx]))
        assert response == UserRead(**USER_TABLE_FOR_DB[user_idx])
    else:
        with pytest.raises(HTTPException):
            response = await deps.get_current_user(AccessRead(**ACCESS_TABLE[access_idx]))


@pytest.mark.parametrize(
    "access_idx, device_idx",
    [
        [2, 0],  # Correct
        [1, None],  # Not a device access
    ],
)
@pytest.mark.asyncio
async def test_get_current_device(init_test_db, access_idx, device_idx):

    if isinstance(device_idx, int):
        response = await deps.get_current_device(AccessRead(**ACCESS_TABLE[access_idx]))
        assert response == DeviceOut(**DEVICE_TABLE_FOR_DB[device_idx])
    else:
        with pytest.raises(HTTPException):
            response = await deps.get_current_device(AccessRead(**ACCESS_TABLE[access_idx]))
