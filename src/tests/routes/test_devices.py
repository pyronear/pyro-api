# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud, security
from tests.db_utils import get_entry, fill_table, TestSessionLocal
from tests.utils import update_only_datetime, parse_time

USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
    {"id": 3, "login": "sixth_login", "access_id": 5, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68., "software_hash": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68., "software_hash": None,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 3, "login": "fifth_login", "owner_id": 3, "access_id": 6, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68., "software_hash": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 1, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 6, "group_id": 2, "login": "sixth_login", "hashed_password": "hashed_pwd", "scope": "user"},
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(db, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, device_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table devices has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_device(test_app_asyncio, init_test_db, access_idx, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get(f"/devices/{device_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == {k: v for k, v in DEVICE_TABLE[device_id - 1].items() if k != "access_id"}


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [None, 401, "Not authenticated"],
        [0, 403, "Your access scope is not compatible with this operation."],
        [1, 403, "Your access scope is not compatible with this operation."],
        [2, 200, None],
        [3, 200, None],
    ],
)
@pytest.mark.asyncio
async def test_get_my_device(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/devices/me", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        entry = None
        for device in DEVICE_TABLE:
            if device['access_id'] == ACCESS_TABLE[access_idx]['id']:
                entry = device
                break
        assert response.json() == {k: v for k, v in entry.items() if k != "access_id"}


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_devices",
    [
        [None, 401, "Not authenticated", None],
        [0, 200, None, [DEVICE_TABLE[0], DEVICE_TABLE[1]]],
        [5, 200, None, [DEVICE_TABLE[-1]]],
        [1, 200, None, DEVICE_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_devices(test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_devices):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/devices/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in expected_devices]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [None, 401, "Not authenticated"],
        [0, 200, None],
        [1, 200, None],
        [2, 403, "Your access scope is not compatible with this operation."],
    ],
)
@pytest.mark.asyncio
async def test_fetch_my_devices(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/devices/my-devices", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        owner_id = None
        for entry in USER_TABLE:
            if entry['access_id'] == ACCESS_TABLE[access_idx]['id']:
                owner_id = entry['id']
                break
        assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"}
                                   for entry in DEVICE_TABLE if entry['owner_id'] == owner_id]


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [0, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         403, "Your access scope is not compatible with this operation."],
        [1, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         201, None],
        [2, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         403, "Your access scope is not compatible with this operation."],
        [1, {"login": "third_login", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         409, "An entry with login='third_login' already exists."],  # existing device
        [1, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68., "password": "pw"},
         422, None],  # password too short
        [1, {"login": "third_device", "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         422, None],  # missing owner
        [1, {"login": "third_device", "owner_id": 10, "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         404, "Table users has no entry with id=10"],  # unknown owner
        [1, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": "alpha", "password": "my_pwd"},
         422, None],  # invalid angle_of_view
        [1, {"login": "third_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": -45., "password": "my_pwd"},
         422, None],  # invalid angle_of_view
    ],
)
@pytest.mark.asyncio
async def test_register_device(test_app_asyncio, init_test_db, test_db,
                               access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/devices/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    # Response content
    if response.status_code // 100 == 2:
        test_response = {"id": len(DEVICE_TABLE) + 1, "login": payload['login'],
                         "owner_id": payload['owner_id'], "specs": payload['specs']}
        json_response = response.json()
        assert all(v == json_response[k] for k, v in test_response.items())

        # Timestamp consistency
        new_device_in_db = await get_entry(test_db, db.devices, json_response["id"])
        new_device_in_db = dict(**new_device_in_db)
        assert new_device_in_db['created_at'] > utc_dt and new_device_in_db['created_at'] < datetime.utcnow()

        # Access table updated
        new_access_in_db = await get_entry(test_db, db.accesses, len(ACCESS_TABLE) + 1)
        new_access_in_db = dict(**new_access_in_db)
        assert new_access_in_db['login'] == payload['login']
        assert new_access_in_db['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [0, {"login": "third_device", "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         201, None],
        [1, {"login": "third_device", "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         201, None],
        [2, {"login": "third_device", "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         403, "Your access scope is not compatible with this operation."],
        [0, {"login": "third_login", "specs": "v0.2", "angle_of_view": 68., "password": "my_pwd"},
         409, "An entry with login='third_login' already exists."],  # existing device
        [1, {"login": "third_device", "specs": "v0.2", "angle_of_view": 68., "password": "pw"},
         422, None],  # password too short
        [1, {"login": "third_device", "specs": "v0.2", "angle_of_view": "alpha", "password": "my_pwd"},
         422, None],  # invalid angle_of_view
        [1, {"login": "third_device", "specs": "v0.2", "angle_of_view": -45., "password": "my_pwd"},
         422, None],  # invalid angle_of_view
    ],
)
@pytest.mark.asyncio
async def test_register_my_device(test_app_asyncio, init_test_db, test_db,
                                  access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/devices/register", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    # Response content
    if response.status_code // 100 == 2:
        owner_id = None
        for entry in USER_TABLE:
            if entry['access_id'] == ACCESS_TABLE[access_idx]['id']:
                owner_id = entry['id']
                break

        test_response = {"id": len(DEVICE_TABLE) + 1, "login": payload['login'],
                         "owner_id": owner_id, "specs": payload['specs']}
        json_response = response.json()
        assert all(v == json_response[k] for k, v in test_response.items())

        # Timestamp consistency
        new_device_in_db = await get_entry(test_db, db.devices, json_response["id"])
        new_device_in_db = dict(**new_device_in_db)
        assert new_device_in_db['created_at'] > utc_dt and new_device_in_db['created_at'] < datetime.utcnow()

        # Access table updated
        new_access_in_db = await get_entry(test_db, db.accesses, len(ACCESS_TABLE) + 1)
        new_access_in_db = dict(**new_access_in_db)
        assert new_access_in_db['login'] == payload['login']
        assert new_access_in_db['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, payload, device_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [0, {"login": "renamed_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68.}, 1,
         403, "Your access scope is not compatible with this operation."],
        [1, {"login": "renamed_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68.}, 1,
         200, None],
        [2, {"login": "renamed_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68.}, 1,
         403, "Your access scope is not compatible with this operation."],
        [1, {}, 1, 422, None],
        [1, {"login": "new_device", "owner_id": 1, "specs": "v0.2", "angle_of_view": 68.}, 999,
         404, "Table devices has no entry with id=999"],
        [1, {"login": 1, "owner_id": 1, "access_id": 1, "specs": "v0.1", "angle_of_view": 68.}, 1,
         422, None],
        [1, {"login": "renamed_device", "angle_of_view": 68.}, 1,
         422, None],
        [1, {"login": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1", "angle_of_view": 68.}, 0,
         422, None],
        [1, {"login": "fourth_login", "owner_id": 1, "access_id": 1, "specs": "v0.1", "angle_of_view": 68.}, 1,
         409, "An entry with login='fourth_login' already exists."],  # renamed to already existing login
        [1, {"login": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1", "angle_of_view": "alpha"}, 1,
         422, None],  # invalid angle_of_view
        [1, {"login": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1", "angle_of_view": -45.}, 1,
         422, None],  # invalid angle_of_view
    ],
)
@pytest.mark.asyncio
async def test_update_device(test_app_asyncio, init_test_db, test_db,
                             access_idx, payload, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/devices/{device_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_device_in_db = await get_entry(test_db, db.devices, device_id)
        updated_device_in_db = dict(**updated_device_in_db)

        assert all(v == payload.get(k, DEVICE_TABLE_FOR_DB[device_id - 1][k])
                   for k, v in updated_device_in_db.items())

        # Access table updated
        access_id = DEVICE_TABLE[response.json()['id'] - 1]["access_id"]
        updated_access = await get_entry(test_db, db.accesses, access_id)
        updated_access = dict(**updated_access)
        assert updated_access['login'] == payload['login']


@pytest.mark.parametrize(
    "access_idx, payload, device_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [0, {"lon": 5.}, 1, 200, None],
        [0, {"lon": 5.}, 2, 403, "Permission denied to modify device with id=2."],
        # TODO: admin should have permission without being owner
        [1, {"lon": 5.}, 1, 403, "Permission denied to modify device with id=1."],
        [1, {"lon": 5.}, 2, 200, None],
        [2, {"lon": 5.}, 1, 403, "Your access scope is not compatible with this operation."],
        [2, {"lon": 5.}, 2, 403, "Your access scope is not compatible with this operation."],
        [1, {"lon": 5.}, 999, 404, "Table devices has no entry with id=999"],
        [1, {"lon": "position"}, 1, 422, None],
        [1, {"lon": 5.}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_device_location(test_app_asyncio, init_test_db, test_db,
                                      access_idx, payload, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/devices/{device_id}/location", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_device = await get_entry(test_db, db.devices, device_id)
        updated_device = dict(**updated_device)

        assert all(updated_device[k] == v for k, v in payload.items())
        assert all(updated_device[k] == v for k, v in DEVICE_TABLE_FOR_DB[device_id - 1].items() if k not in payload)


@pytest.mark.parametrize(
    "access_idx, payload, device_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [0, {"software_hash": "my_sha256hash"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {"software_hash": "my_sha256hash"}, 1, 200, None],
        [2, {"software_hash": "my_sha256hash"}, 1, 403, "Your access scope is not compatible with this operation."],
        [3, {"software_hash": "my_sha256hash"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {}, 1, 422, None],
        [1, {"software_hash": "my_hash"}, 1, 422, None],
        [1, {"software_hash": "my_way_too_long_sha26_hash"}, 1, 422, None],
        [1, {"software_hash": "my_sha256hash"}, 0, 422, None],
        [1, {"software_hash": "my_sha256hash"}, 999, 404, "Table devices has no entry with id=999"],
    ],
)
@pytest.mark.asyncio
async def test_update_device_hash(test_app_asyncio, init_test_db, test_db,
                                  access_idx, payload, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/devices/{device_id}/hash", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_device = await get_entry(test_db, db.devices, device_id)
        updated_device = dict(**updated_device)
        assert updated_device['software_hash'] == payload['software_hash']


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [0, {"lon": 5.}, 403, "Your access scope is not compatible with this operation."],
        [1, {"lon": 5.}, 403, "Your access scope is not compatible with this operation."],
        [2, {"lon": 5.}, 200, None],
        [2, {"lon": "position"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_my_location(test_app_asyncio, init_test_db, test_db,
                                  access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put("/devices/my-location", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        device_id = None
        for entry in DEVICE_TABLE:
            if entry['access_id'] == ACCESS_TABLE[access_idx]['id']:
                device_id = entry['id']
                break

        updated_device = await get_entry(test_db, db.devices, device_id)
        updated_device = dict(**updated_device)

        assert all(updated_device[k] == v for k, v in payload.items())
        assert all(updated_device[k] == v for k, v in DEVICE_TABLE_FOR_DB[device_id - 1].items() if k not in payload)


@pytest.mark.parametrize(
    "access_idx, payload, device_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [0, {"password": "new_password"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {"password": "new_password"}, 1, 200, None],
        [2, {"password": "new_password"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {}, 1, 422, None],
        [1, {"password": "new_password"}, 999, 404, "Table devices has no entry with id=999"],
        [1, {"password": 1}, 1, 422, None],
        [1, {"password": "me"}, 1, 422, None],
        [1, {"password": "new_password"}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_device_password(test_app_asyncio, init_test_db, test_db,
                                      access_idx, payload, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/devices/{device_id}/pwd", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == {k: v for k, v in DEVICE_TABLE[device_id - 1].items() if k != 'access_id'}
        updated_access = await get_entry(test_db, db.accesses, DEVICE_TABLE[device_id - 1]["access_id"])
        updated_access = dict(**updated_access)
        assert updated_access['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [None, 401, "Not authenticated"],
        [0, 403, "Your access scope is not compatible with this operation."],
        [1, 403, "Your access scope is not compatible with this operation."],
        [2, 200, None],
    ],
)
@pytest.mark.asyncio
async def test_heartbeat(test_app_asyncio, init_test_db, test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()

    response = await test_app_asyncio.put("/devices/heartbeat", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        # Everything should be identical apart from ping
        assert datetime.utcnow() > datetime.fromisoformat(json_response['last_ping'])
        assert utc_dt < datetime.fromisoformat(json_response['last_ping'])

        updated_device = await get_entry(test_db, db.devices, json_response["id"])
        updated_device = dict(**updated_device)

        assert updated_device['last_ping'] > utc_dt
        if DEVICE_TABLE[json_response["id"] - 1]['last_ping'] is not None:
            assert updated_device['last_ping'] > DEVICE_TABLE[json_response["id"] - 1]['last_ping']
        assert updated_device['created_at'] == parse_time(DEVICE_TABLE[json_response["id"] - 1]['created_at'])


@pytest.mark.parametrize(
    "access_idx, device_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [3, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table devices has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_device(test_app_asyncio, init_test_db, access_idx, device_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/devices/{device_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == {k: v for k, v in DEVICE_TABLE[device_id - 1].items() if k != 'access_id'}
        remaining_devices = await test_app_asyncio.get("/devices/", headers=auth)
        assert all(entry['id'] != device_id for entry in remaining_devices.json())

        # Check that the access was deleted as well
        remaining_accesses = await test_app_asyncio.get("/accesses/", headers=auth)
        assert all(entry['login'] != response.json()['login'] for entry in remaining_accesses.json())
