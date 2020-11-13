import json
import pytest
from datetime import datetime

from app.api import crud


MOCK_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "me"},
]


def _patch_crud(monkeypatch, mock_table):
    # Sterilize all DB interactions
    async def mock_get(entry_id, table):
        for entry in mock_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_fetch_all(table, query_filters):
        if query_filters is None:
            return mock_table
        response = []
        for entry in mock_table:
            if all(entry[k] == v for k, v in query_filters):
                response.append(entry)
        return response

    monkeypatch.setattr(crud, "fetch_all", mock_fetch_all)

    async def mock_fetch_one(table, query_filters):
        for entry in mock_table:
            if all(entry[k] == v for k, v in query_filters):
                return entry
        return None

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def mock_post(payload, table):
        payload_dict = payload.dict()
        payload_dict['created_at'] = datetime.utcnow()
        payload_dict['id'] = len(mock_table) + 1
        mock_table.append(payload_dict)
        return payload_dict['id']

    monkeypatch.setattr(crud, "post", mock_post)

    async def mock_put(entry_id, payload, table):
        for idx, entry in enumerate(mock_table):
            if entry['id'] == entry_id:
                for k, v in payload.dict().items():
                    mock_table[idx][k] = v
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    async def mock_delete(entry_id, table):
        for idx, entry in enumerate(mock_table):
            if entry['id'] == entry_id:
                del mock_table[idx]
                break
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)


def test_get_access(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get("/accesses/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in local_db[0].items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_access_invalid(test_app, monkeypatch, access_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get(f"/accesses/{access_id}")
    assert response.status_code == status_code, access_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_accesses(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get("/accesses/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"} for entry in local_db]


def test_create_access(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    test_payload = {"login": "third_login", "scopes": "me", "password": "PickARobustOne"}
    test_response = {"id": len(local_db) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = test_app.post("/accesses/", data=json.dumps(test_payload))

    assert response.status_code == 201
    assert response.json() == {k: v for k, v in test_response.items() if k != "password"}


@pytest.mark.parametrize(
    "payload, status_code, status_details",
    [
        [{"login": "first_login", "password": "PickARobustOne", "scopes": "me"}, 400, "An entry with login='first_login' already exists."],
        [{"login": "third_login", "scopes": "me", "hashed_password": "PickARobustOne"}, 422, None],
        [{"login": 1, "scopes": "me", "password": "PickARobustOne"}, 422, None],
        [{"login": "third_login", "scopes": "me"}, 422, None],
    ],
)
def test_create_access_invalid(test_app, monkeypatch, payload, status_code, status_details):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.post("/accesses/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)


def test_update_access(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    test_payload = {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}
    response = test_app.put("/accesses/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in local_db[0].items():
        assert v == test_payload.get(k, MOCK_TABLE[0][k])


@pytest.mark.parametrize(
    "access_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"login": "first_login"}, 422],
        [999, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 404],
        [1, {"login": 1, "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
        [0, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
    ],
)
def test_update_access_invalid(test_app, monkeypatch, access_id, payload, status_code):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.put(f"/accesses/{access_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_access(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.delete("/accesses/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in MOCK_TABLE[0].items() if k != "hashed_password"}
    for entry in local_db:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_access_invalid(test_app, monkeypatch, access_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.delete(f"/accesses/{access_id}/")
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)
