# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud, security
from tests.db_utils import get_entry, fill_table
from tests.utils import update_only_datetime, parse_time


USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 2, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
]


USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)


@pytest.mark.parametrize(
    "access_idx, user_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_user(test_app_asyncio, init_test_db, test_db, access_idx, user_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get(f"/users/{user_id}", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        user_in_db = await get_entry(test_db, db.users, user_id)
        user_in_db = dict(**user_in_db)
        response_json = response.json()
        response_json["created_at"] = parse_time(response_json["created_at"])

        assert response_json == {k: v for k, v in user_in_db.items() if k != "access_id"}


@pytest.mark.parametrize(
    "access_idx, user_idx, status_code, status_details",
    [
        [0, 0, 200, None],
        [1, 1, 200, None],
        [2, None, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_get_my_user(test_app_asyncio, init_test_db, test_db, access_idx, user_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/users/me", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        json_response = response.json()
        for k in ["id", "login"]:
            assert json_response[k] == USER_TABLE_FOR_DB[user_idx][k]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
        [2, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_fetch_users(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/users/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in USER_TABLE]


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"login": "fourth_user", "password": "third_pwd"}, 401, "Permission denied"],
        [1, {"login": "fourth_user", "password": "third_pwd"}, 201, None],
        [2, {"login": "fourth_user", "password": "third_pwd"}, 401, "Permission denied"],
        [1, {"login": "first_login", "password": "pwd"}, 400, "An entry with login='first_login' already exists."],
        [1, {"login": "fourth_user"}, 422, None],
        [1, {"logins": "fourth_user", "password": "third_pwd"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_user(test_app_asyncio, init_test_db, test_db, monkeypatch,
                           access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    max_user_id = max(USER_TABLE_FOR_DB, key=lambda x: x["id"])["id"]
    max_access_id = max(ACCESS_TABLE, key=lambda x: x["id"])["id"]

    utc_dt = datetime.utcnow()

    response = await test_app_asyncio.post("/users/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": max_user_id + 1, "login": payload["login"]}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        # Timestamp consistency
        new_user_in_db = await get_entry(test_db, db.users, json_response["id"])
        new_user_in_db = dict(**new_user_in_db)
        assert new_user_in_db['created_at'] > utc_dt and new_user_in_db['created_at'] < datetime.utcnow()

        # Access update
        new_access_in_db = await get_entry(test_db, db.accesses, max_access_id + 1)
        new_access_in_db = dict(**new_access_in_db)
        assert new_access_in_db['login'] == payload['login']
        assert new_access_in_db['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, payload, user_id, status_code, status_details",
    [
        [0, {"login": "renamed_user"}, 1, 401, "Permission denied"],
        [1, {"login": "renamed_user"}, 1, 200, None],
        [2, {"login": "renamed_user"}, 1, 401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"login": "renamed_user"}, 999, 404, "Entry not found"],
        [1, {"login": 1}, 1, 422, None],
        [1, {"login": "me"}, 1, 422, None],
        [1, {"login": "renamed_user"}, 0, 422, None],
        [1, {"login": "second_login"}, 1, 400, "An entry with login='second_login' already exists."],
    ],
)
@pytest.mark.asyncio
async def test_update_user(test_app_asyncio, init_test_db, test_db,
                           access_idx, payload, user_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/users/{user_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_user_in_db = await get_entry(test_db, db.users, user_id)
        updated_user_in_db = dict(**updated_user_in_db)
        for k, v in updated_user_in_db.items():
            assert v == payload.get(k, USER_TABLE_FOR_DB[user_id - 1][k])

        # Access update
        access_id = USER_TABLE[user_id - 1]["access_id"]
        updated_access = await get_entry(test_db, db.accesses, access_id)
        updated_access = dict(**updated_access)
        assert updated_access['login'] == payload['login']


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"login": "renamed_user"}, 200, None],
        [1, {"login": "renamed_user"}, 200, None],
        [2, {"login": "renamed_user"}, 401, "Permission denied"],
        [0, {}, 422, None],
        [0, {"login": 1}, 422, None],
        [0, {"login": "me"}, 422, None],
        [0, {"login": "second_login"}, 400, "An entry with login='second_login' already exists."],
    ],
)
@pytest.mark.asyncio
async def test_update_my_info(test_app_asyncio, init_test_db, test_db,
                              access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put("/users/update-info", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        my_user_in_db = await get_entry(test_db, db.users, json_response["id"])
        for k, v in dict(**my_user_in_db).items():
            assert v == payload.get(k, USER_TABLE_FOR_DB[json_response["id"] - 1][k])
        # Check that the corresponding access has also been updated
        updated_access = await get_entry(test_db, db.accesses, ACCESS_TABLE[access_idx]['id'])
        updated_access = dict(**updated_access)
        assert updated_access['login'] == payload['login']


@pytest.mark.parametrize(
    "access_idx, payload, user_id, status_code, status_details",
    [
        [0, {"password": "new_password"}, 1, 401, "Permission denied"],
        [1, {"password": "new_password"}, 1, 200, None],
        [2, {"password": "new_password"}, 1, 401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"password": "new_password"}, 999, 404, "Entry not found"],
        [1, {"password": 1}, 1, 422, None],
        [1, {"password": "me"}, 1, 422, None],
        [1, {"password": "new_password"}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_user_password(test_app_asyncio, init_test_db, test_db, monkeypatch,
                                    access_idx, payload, user_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/users/{user_id}/pwd", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == {"login": USER_TABLE_FOR_DB[user_id - 1]["login"]}
        # Access update
        access_id = USER_TABLE[user_id - 1]["access_id"]
        updated_access = await get_entry(test_db, db.accesses, access_id)
        updated_access = dict(**updated_access)
        assert updated_access['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"password": "new_password"}, 200, None],
        [1, {"password": "new_password"}, 200, None],
        [2, {"password": "new_password"}, 401, "Permission denied"],
        [0, {}, 422, None],
        [0, {"password": 1}, 422, None],
        [0, {"password": "me"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_my_password(test_app_asyncio, init_test_db, test_db, monkeypatch,
                                  access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put("/users/update-pwd", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        my_access_in_db = await get_entry(test_db, db.accesses, ACCESS_TABLE[access_idx]['id'])
        my_access_in_db = dict(**my_access_in_db)
        assert my_access_in_db['hashed_password'] == f"hashed_{payload['password']}"


@pytest.mark.parametrize(
    "access_idx, user_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_user(test_app_asyncio, init_test_db, monkeypatch,
                           access_idx, user_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/users/{user_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        assert json_response == {k: USER_TABLE[user_id - 1][k] for k in ['id', 'login', 'created_at']}

        remaining_users = await test_app_asyncio.get("/users/", headers=auth)
        assert all(entry['id'] != user_id for entry in remaining_users.json())

        # Check that the access was deleted as well
        remaining_accesses = await test_app_asyncio.get("/accesses/", headers=auth)
        assert all(entry['login'] != json_response['login'] for entry in remaining_accesses.json())
