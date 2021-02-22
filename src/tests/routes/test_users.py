# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud, security
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime, parse_time

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "connected_user", "hashed_password": "pwd_hashed", "scopes": "me"},
]

USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]


USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))


@pytest.mark.asyncio
async def test_get_user(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.get("/users/1")
    user_1_in_db = await get_entry_in_db(test_db, db.users, 1)
    user_1_in_db = dict(**user_1_in_db)
    assert response.status_code == 200
    response_json = response.json()
    response_json["created_at"] = parse_time(response_json["created_at"])

    assert response_json == {k: v for k, v in user_1_in_db.items() if k != "access_id"}

    # personal version
    response = await test_app_asyncio.get("/users/me")
    assert response.status_code == 200
    json_response = response.json()
    for k in ["id", "login"]:
        assert json_response[k] == USER_TABLE_FOR_DB[1][k]


@pytest.mark.parametrize(
    "user_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_user_invalid(test_app_asyncio, test_db, monkeypatch, user_id, status_code, status_details):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.get(f"/users/{user_id}")
    assert response.status_code == status_code, user_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_users(test_app_asyncio, test_db, test_app, monkeypatch):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in USER_TABLE]


@pytest.mark.asyncio
async def test_create_user(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    test_payload = {"login": "third_user", "password": "third_pwd"}
    max_user_id = max(USER_TABLE_FOR_DB, key=lambda x: x["id"])["id"]
    max_access_id = max(ACCESS_TABLE, key=lambda x: x["id"])["id"]
    test_response = {"id": max_user_id + 1, "login": test_payload["login"]}

    utc_dt = datetime.utcnow()

    response = await test_app_asyncio.post("/users/", data=json.dumps(test_payload))

    assert response.status_code == 201, print(response.json()['detail'])
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

    new_user_in_db = await get_entry_in_db(test_db, db.users, json_response["id"])
    new_user_in_db = dict(**new_user_in_db)

    new_access_in_db = await get_entry_in_db(test_db, db.accesses, max_access_id + 1)
    new_access_in_db = dict(**new_access_in_db)

    assert new_user_in_db['created_at'] > utc_dt and new_user_in_db['created_at'] < datetime.utcnow()
    assert new_access_in_db['hashed_password'] == f"{test_payload['password']}_hashed"


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"login": "first_user", "password": "first_pwd"}, 400],
    ],
)
@pytest.mark.asyncio
async def test_create_user_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.post("/users/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_user(test_app_asyncio, test_db, monkeypatch):
    # Init Db data
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    # Test on another user.
    test_payload = {"login": "renamed_user"}
    response = await test_app_asyncio.put("/users/1/", data=json.dumps(test_payload))
    assert response.status_code == 200

    updated_user_in_db = await get_entry_in_db(test_db, db.users, 1)
    updated_user_in_db = dict(**updated_user_in_db)
    for k, v in updated_user_in_db.items():
        assert v == test_payload.get(k, USER_TABLE_FOR_DB[0][k])

    # Self version
    test_payload = {"login": "renamed_me"}
    response = await test_app_asyncio.put("/users/update-info", data=json.dumps(test_payload))

    assert response.status_code == 200
    json_response = response.json()
    my_user_in_db = await get_entry_in_db(test_db, db.users, json_response["id"])
    my_user_in_db = dict(**my_user_in_db)

    for k, v in my_user_in_db.items():
        assert v == test_payload.get(k, USER_TABLE_FOR_DB[1][k])


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"login": "renamed_user"}, 404],
        [1, {"login": 1}, 422],
        [1, {"login": "me"}, 422],
        [0, {"login": "renamed_user"}, 422],
        [1, {"login": "connected_user"}, 400],  # renamed to already existing login
    ],
)
@pytest.mark.asyncio
async def test_update_user_invalid(test_app_asyncio, test_db, monkeypatch, user_id, payload, status_code):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.put(f"/users/{user_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{}, 422],
        [{"login": 1}, 422],
        [{"login": "me"}, 422],
        [{"login": "first_user"}, 400],  # renamed to already existing login
    ],
)
@pytest.mark.asyncio
async def test_update_my_info_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.put("/users/update-info", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_password(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    test_payload = {"password": "new_password"}
    response = await test_app_asyncio.put("/users/1/pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"login": USER_TABLE_FOR_DB[0]["login"]}
    new_access_in_db = await get_entry_in_db(test_db, db.accesses, 1)
    new_access_in_db = dict(**new_access_in_db)
    assert new_access_in_db['hashed_password'] == f"{test_payload['password']}_hashed"

    # Self version
    test_payload = {"password": "my_new_password"}
    response = await test_app_asyncio.put("/users/update-pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"login": USER_TABLE_FOR_DB[1]["login"]}
    new_access_in_db = await get_entry_in_db(test_db, db.accesses, 2)
    new_access_in_db = dict(**new_access_in_db)
    assert new_access_in_db['hashed_password'] == f"{test_payload['password']}_hashed"


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"password": "renamed_user"}, 404],
        [1, {"password": 1}, 422],
        [1, {"password": "me"}, 422],
        [0, {"password": "renamed_user"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_password_invalid(test_app_asyncio, test_db, monkeypatch, user_id, payload, status_code):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.put(f"/users/{user_id}/pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{}, 422],
        [{"password": 1}, 422],
        [{"password": "me"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_my_password_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.put("/users/update-pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_user(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.delete("/users/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in USER_TABLE[0].items() if k in ['id', 'login', 'created_at']}

    remaining_users = await test_app_asyncio.get("/users/")
    for entry in remaining_users.json():
        assert entry['id'] != 1

    # Check that the access was deleted as well
    remaining_accesses = await test_app_asyncio.get("/accesses/")
    for access in remaining_accesses.json():
        assert access['login'] != response.json()['login']


@pytest.mark.parametrize(
    "user_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_user_invalid(test_app_asyncio, test_db, monkeypatch, user_id, status_code, status_details):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    response = await test_app_asyncio.delete(f"/users/{user_id}/")
    assert response.status_code == status_code, print(user_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(user_id)
