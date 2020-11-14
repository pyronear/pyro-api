import json
import pytest
from datetime import datetime
from fastapi import HTTPException

from app.api import crud, security, routing
from app.api.routes import users
from app.api.schemas import AccessRead, AccessCreation



USER_TABLE = [
    {"id": 1, "username": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 99, "username": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "connected_user", "hashed_password": "pwd_hashed", "scopes": "me"},
]


def _patch_session(monkeypatch, user_table, access_table=None):
    # Sterilize all DB interactions
    async def mock_get(entry_id, table):
        for entry in user_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_fetch_all(table, query_filters):
        if query_filters is None:
            return user_table
        response = []
        for entry in user_table:
            if all(entry[k] == v for k, v in query_filters):
                response.append(entry)
        return response

    monkeypatch.setattr(crud, "fetch_all", mock_fetch_all)

    async def mock_post(payload, table):
        payload_dict = payload.dict()
        payload_dict['created_at'] = datetime.utcnow()
        payload_dict['id'] = len(user_table) + 1
        user_table.append(payload_dict)
        return payload_dict['id']

    monkeypatch.setattr(crud, "post", mock_post)

    async def mock_put(entry_id, payload, table):
        for idx, entry in enumerate(user_table):
            if entry['id'] == entry_id:
                for k, v in payload.dict().items():
                    user_table[idx][k] = v
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    async def mock_delete(entry_id, table):
        for idx, entry in enumerate(user_table):
            if entry['id'] == entry_id:
                del user_table[idx]
                break
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    # Override cred verification
    async def mock_hash(password):
        return f"{password}_hashed"

    monkeypatch.setattr(security, "hash_password", mock_hash)

    # Update mock accesses
    if access_table is not None:
        async def mock_update_pwd(payload, entry_id):
            for idx, entry in enumerate(access_table):
                if entry["id"] == entry_id:
                    access_table[idx]["hashed_password"] = await security.hash_password(payload.password)
                    return {"login": entry["login"]}

        monkeypatch.setattr(users, "update_access_pwd", mock_update_pwd)

        async def mock_post_access(login, password, scopes):
            if any(entry['login'] == login for entry in access_table):
                raise HTTPException(status_code=400, detail=f"An entry with login='{login}' already exists.")

            pwd = await mock_hash(password)
            access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
            # Post on access table
            payload_dict = access.dict()
            payload_dict['id'] = len(access_table) + 1
            access_table.append(payload_dict)
            return AccessRead(id=payload_dict['id'], **access.dict())

        monkeypatch.setattr(users, "post_access", mock_post_access)


def test_get_user(test_app, monkeypatch):

    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in local_table[0].items() if k != "access_id"}

    # personal version
    response = test_app.get("/users/me")
    assert response.status_code == 200
    json_response = response.json()
    for k in ["id", "username"]:
        assert json_response[k] == local_table[1][k]


@pytest.mark.parametrize(
    "user_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_user_invalid(test_app, monkeypatch, user_id, status_code, status_details):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.get(f"/users/{user_id}")
    assert response.status_code == status_code, user_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_users(test_app, monkeypatch):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in local_table]


def test_create_user(test_app, monkeypatch):

    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    local_accesses = ACCESS_TABLE.copy()
    _patch_session(monkeypatch, local_table, local_accesses)

    test_payload = {"username": "third_user", "password": "third_pwd"}
    test_response = {"id": len(local_table) + 1, "username": test_payload["username"]}

    utc_dt = datetime.utcnow()
    response = test_app.post("/users/", data=json.dumps(test_payload))

    assert response.status_code == 201, print(response.json()['detail'])
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert local_table[-1]['created_at'] > utc_dt and local_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"username": "first_user", "password": "first_pwd"}, 400],
    ],
)
def test_create_user_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    local_accesses = ACCESS_TABLE.copy()
    _patch_session(monkeypatch, local_table, local_accesses)

    response = test_app.post("/users/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_user(test_app, monkeypatch):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    test_payload = {"username": "renamed_user"}
    response = test_app.put("/users/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in local_table[0].items():
        assert v == test_payload.get(k, USER_TABLE[0][k])

    # Self version
    test_payload = {"username": "renamed_me"}
    response = test_app.put("/users/update-info", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in local_table[1].items():
        assert v == test_payload.get(k, USER_TABLE[1][k])


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"username": "renamed_user"}, 404],
        [1, {"username": 1}, 422],
        [1, {"username": "me"}, 422],
        [0, {"username": "renamed_user"}, 422],
    ],
)
def test_update_user_invalid(test_app, monkeypatch, user_id, payload, status_code):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.put(f"/users/{user_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{}, 422],
        [{"username": 1}, 422],
        [{"username": "me"}, 422],
    ],
)
def test_update_my_info_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.put(f"/users/update-info", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_password(test_app, monkeypatch):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    local_accesses = ACCESS_TABLE.copy()
    _patch_session(monkeypatch, local_table, local_accesses)

    test_payload = {"password": "new_password"}
    response = test_app.put("/users/1/pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"username": local_table[0]["username"]}
    assert local_accesses[0]['hashed_password'] == f"{test_payload['password']}_hashed"

    # Self version
    test_payload = {"password": "my_new_password"}
    response = test_app.put("/users/update-pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {"username": local_table[1]["username"]}
    assert local_accesses[1]['hashed_password'] == f"{test_payload['password']}_hashed"


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
    local_table = USER_TABLE.copy()
    local_accesses = ACCESS_TABLE.copy()
    _patch_session(monkeypatch, local_table, local_accesses)

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
    local_table = USER_TABLE.copy()
    local_accesses = ACCESS_TABLE.copy()
    _patch_session(monkeypatch, local_table, local_accesses)

    response = test_app.put(f"/users/update-pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_user(test_app, monkeypatch):
    # Sterilize DB interactions
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.delete("/users/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in USER_TABLE[0].items() if k in ['id', 'username', 'created_at']}
    for entry in local_table:
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
    local_table = USER_TABLE.copy()
    _patch_session(monkeypatch, local_table)

    response = test_app.delete(f"/users/{user_id}/")
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)
