import json
import pytest

from app.api import crud

BASE_PAYLOAD = {"login": "scope_login", "scopes": "ada"}
MIN_PAYLOAD = {**BASE_PAYLOAD, "password": "password"}
FULL_PAYLOAD = {**MIN_PAYLOAD}
REPLY_PAYLOAD = FULL_PAYLOAD.copy()
REPLY_PAYLOAD.pop("password")


def test_create_access(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **REPLY_PAYLOAD}

    async def mock_fetch_one(table, query_filter):
        return None

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/accesses/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


def test_create_access_invalid_json(test_app):
    response = test_app.post("/accesses/", data=json.dumps({"device": 1}))
    assert response.status_code == 422

    response = test_app.post("/accesses/", data=json.dumps({**REPLY_PAYLOAD}))
    assert response.status_code == 422


def test_get_access(test_app, monkeypatch):
    test_data = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/accesses/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_get_access_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/accesses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/accesses/0")
    assert response.status_code == 422


def test_fetch_access(test_app, monkeypatch):
    test_data = [
        {"id": 1, **REPLY_PAYLOAD},
        {"id": 2, **REPLY_PAYLOAD},
    ]

    async def mock_get_all(table, query_filter=None):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/accesses/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_data


def test_update_access(test_app, monkeypatch):
    test_update_data = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/accesses/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_update_data


@pytest.mark.parametrize(
    "access_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"access_id": 1}, 422],
        [999, FULL_PAYLOAD, 404],
        [1, {"acces_id": 2}, 422],
        [0, FULL_PAYLOAD, 422],
    ],
)
def test_update_access_invalid(test_app, monkeypatch, access_id, payload, status_code):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/accesses/{access_id}/", data=json.dumps(payload),)
    assert response.status_code == status_code, print(payload)


def test_remove_access(test_app, monkeypatch):
    test_data = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/accesses/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_remove_access_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/accesses/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/accesses/0/")
    assert response.status_code == 422
