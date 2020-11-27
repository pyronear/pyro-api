import json
import pytest
from copy import deepcopy
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.api import crud, security
from app.api.routes import users
from app.api.schemas import AccessRead, AccessCreation
from app import db
from tests.conf_test_db import get_entry_in_db, populate_db

USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 99, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

USER_TABLE_FOR_DB = [
    {"id": 1, "login": "first_user", "access_id": 1,
     "created_at": datetime.strptime("2020-10-13 08:18:45.447773", "%Y-%m-%d %H:%M:%S.%f")},
    {"id": 99, "login": "connected_user", "access_id": 2,
     "created_at": datetime.strptime("2020-11-13 08:18:45.447773", "%Y-%m-%d %H:%M:%S.%f")},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "connected_user", "hashed_password": "pwd_hashed", "scopes": "me"},
]


def _patch_session(monkeypatch, mock_user_table, mock_access_table=None):
    # DB patching
    monkeypatch.setattr(users, "users", mock_user_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)
    # Password
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    # Access table specific
    if mock_access_table is not None:
        async def mock_update_pwd(payload, entry_id):
            for idx, entry in enumerate(mock_access_table):
                if entry["id"] == entry_id:
                    mock_access_table[idx]["hashed_password"] = await security.hash_password(payload.password)
                    return {"login": entry["login"]}

        monkeypatch.setattr(users, "update_access_pwd", mock_update_pwd)

        async def mock_post_access(login, password, scopes):
            if any(entry['login'] == login for entry in mock_access_table):
                raise HTTPException(status_code=400, detail=f"An entry with login='{login}' already exists.")

            pwd = await security.hash_password(password)
            access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
            # Post on access table
            payload_dict = access.dict()
            payload_dict['id'] = len(mock_access_table) + 1
            mock_access_table.append(payload_dict)
            return AccessRead(id=payload_dict['id'], **access.dict())

        monkeypatch.setattr(users, "post_access", mock_post_access)


def test_get_user(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in mock_user_table[0].items() if k != "access_id"}

    # personal version
    response = test_app.get("/users/me")
    assert response.status_code == 200
    json_response = response.json()
    for k in ["id", "login"]:
        assert json_response[k] == mock_user_table[1][k]


@pytest.mark.parametrize(
    "user_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_user_invalid(test_app, monkeypatch, user_id, status_code, status_details):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.get(f"/users/{user_id}")
    assert response.status_code == status_code, user_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_users(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in mock_user_table]


@pytest.mark.asyncio
async def test_create_user(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE_FOR_DB)
    mock_access_table = deepcopy(ACCESS_TABLE)
    monkeypatch.setattr(crud, "database", test_db)
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    test_payload = {"login": "third_user", "password": "third_pwd"}
    max_user_id = max(mock_user_table, key=lambda x: x["id"])["id"]
    max_access_id = max(mock_access_table, key=lambda x: x["id"])["id"]
    test_response = {"id": max_user_id + 1, "login": test_payload["login"]}

    # The test db doesn' take into account miliseconds
    # and it takes less than one second to reach the utcnow().
    # This makes the test nondeterministic;
    #  hence the "rewind" of 1 second to make sure utcnow() is called one second later.
    utc_dt = datetime.utcnow() - timedelta(seconds=1)

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
def test_create_user_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_user_table, mock_access_table)

    response = test_app.post("/users/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_user(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    test_payload = {"login": "renamed_user"}
    response = test_app.put("/users/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_user_table[0].items():
        assert v == test_payload.get(k, USER_TABLE[0][k])

    # Self version
    test_payload = {"login": "renamed_me"}
    response = test_app.put("/users/update-info", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_user_table[1].items():
        assert v == test_payload.get(k, USER_TABLE[1][k])


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"login": "renamed_user"}, 404],
        [1, {"login": 1}, 422],
        [1, {"login": "me"}, 422],
        [0, {"login": "renamed_user"}, 422],
    ],
)
def test_update_user_invalid(test_app, monkeypatch, user_id, payload, status_code):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.put(f"/users/{user_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{}, 422],
        [{"login": 1}, 422],
        [{"login": "me"}, 422],
    ],
)
def test_update_my_info_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.put("/users/update-info", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_password(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_user_table, mock_access_table)

    test_payload = {"password": "new_password"}
    response = test_app.put("/users/1/pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"login": mock_user_table[0]["login"]}
    assert mock_access_table[0]['hashed_password'] == f"{test_payload['password']}_hashed"

    # Self version
    test_payload = {"password": "my_new_password"}
    response = test_app.put("/users/update-pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"login": mock_user_table[1]["login"]}
    assert mock_access_table[1]['hashed_password'] == f"{test_payload['password']}_hashed"


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
def test_update_password_invalid(test_app, monkeypatch, user_id, payload, status_code):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_user_table, mock_access_table)

    response = test_app.put(f"/users/{user_id}/pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{}, 422],
        [{"password": 1}, 422],
        [{"password": "me"}, 422],
    ],
)
def test_update_my_password_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_user_table, mock_access_table)

    response = test_app.put("/users/update-pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_user(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.delete("/users/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in USER_TABLE[0].items() if k in ['id', 'login', 'created_at']}
    for entry in mock_user_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "user_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_user_invalid(test_app, monkeypatch, user_id, status_code, status_details):
    # Sterilize DB interactions
    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table)

    response = test_app.delete(f"/users/{user_id}/")
    assert response.status_code == status_code, print(user_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(user_id)
