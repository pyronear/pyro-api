# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json

import pytest

from app import db
from app.api import crud
from tests.db_utils import TestSessionLocal, fill_table, get_entry
from tests.utils import update_only_datetime

# Have more groups than max request (20)
GROUP_TABLE = [{"id": idx + 1, "name": f"group_{idx}"} for idx in range(51)]


USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
    {"id": 3, "login": "third_login2", "access_id": 5, "created_at": "2020-11-13T08:18:45.447773"},
]


DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68.,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 3, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68.,
     "created_at": "2020-10-13T08:18:45.447773"},
]


ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "third_login2", "hashed_password": "hashed_pwd", "scope": "user"},
]


GROUP_TABLE_FOR_DB = list(map(update_only_datetime, GROUP_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(db, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE_FOR_DB)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "group_id, status_code, status_details",
    [
        [1, 200, None],
        [999, 404, "Table groups has no entry with id=999"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_group(test_app_asyncio, init_test_db, group_id, status_code, status_details):

    response = await test_app_asyncio.get(f"/groups/{group_id}")
    response_json = response.json()
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code == 200:
        assert response_json == GROUP_TABLE[group_id - 1]


@pytest.mark.asyncio
async def test_fetch_groups(test_app_asyncio, init_test_db):

    response = await test_app_asyncio.get("/groups/")
    assert response.status_code == 200
    response_json = response.json()
    assert all(result == entry for result, entry in zip(response_json, GROUP_TABLE[-50:]))


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [1, {"name": "my_group"}, 201, None],
        [0, {"name": "my_group"}, 403, "Your access scope is not compatible with this operation."],
        [2, {"name": "my_group"}, 403, "Your access scope is not compatible with this operation."],
        [1, {"names": "my_group"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_group(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    test_response = {"id": len(GROUP_TABLE) + 1, **payload}

    response = await test_app_asyncio.post("/groups/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response


@pytest.mark.parametrize(
    "access_idx, payload, group_id, status_code, status_details",
    [
        [None, {}, None, 401, "Not authenticated"],
        [1, {"name": "renamed_group"}, 1, 200, None],
        [0, {"name": "renamed_group"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {}, 1, 422, None],
        [1, {"group_name": "foo"}, 1, 422, None],
        [1, {"name": "foo"}, 999, 404, "Table groups has no entry with id=999"],
        [1, {"name": "1"}, 1, 422, None],
        [1, {"name": "foo"}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_group(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, group_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/groups/{group_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_group_in_db = await get_entry(test_db, db.groups, group_id)
        updated_group_in_db = dict(**updated_group_in_db)
        for k, v in updated_group_in_db.items():
            assert v == payload.get(k, GROUP_TABLE_FOR_DB[group_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, group_id, status_code, status_details",
    [
        [1, 1, 200, None],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table groups has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_group(test_app_asyncio, init_test_db, access_idx, group_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/groups/{group_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == GROUP_TABLE[group_id - 1]
        remaining_groups = await test_app_asyncio.get("/groups/")
        assert all(entry['id'] != group_id for entry in remaining_groups.json())
