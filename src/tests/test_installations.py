import json
import pytest

from app.api import crud

MIN_PAYLOAD = {"device_id": 1, "site_id": 1, "elevation": 100, "lat": 0, "lon": 0, "yaw": 0, "pitch": 0}
FULL_PAYLOAD = {**MIN_PAYLOAD, "start_ts": None, "end_ts": None}


def test_create_installation(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **FULL_PAYLOAD}

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/installations/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


def test_create_installation_invalid_json(test_app):
    response = test_app.post("/installations/", data=json.dumps({"device": 1}))
    assert response.status_code == 422

    response = test_app.post("/installations/", data=json.dumps({"device_id": 1, "site_id": "1", "elevation": 0,
                                                                 "lat": 0, "lon": 0, "yaw": 0, "pitch": 0}))
    assert response.status_code == 422


def test_get_installation(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/installations/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_get_installation_incorrect_id(test_app, monkeypatch):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/installations/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/installations/0")
    assert response.status_code == 422


def test_fetch_installations(test_app, monkeypatch):
    test_data = [
        {"id": 1, **FULL_PAYLOAD},
        {"id": 2, **FULL_PAYLOAD},
    ]

    async def mock_get_all(table, query_filter=None):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/installations/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_data


def test_update_installation(test_app, monkeypatch):
    test_update_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/installations/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"site_id": 1}, 422],
        [999, FULL_PAYLOAD, 404],
        [1, {"device_id": "1", "site_id": 1, "elevation": 0, "lat": 0, "lon": 0, "yaw": 0, "pitch": 0}, 422],
        [0, FULL_PAYLOAD, 422],
    ],
)
def test_update_installation_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/installations/{id}/", data=json.dumps(payload),)
    assert response.status_code == status_code, print(payload)


def test_remove_installation(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(id, table):
        return id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/installations/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_remove_installation_incorrect_id(test_app, monkeypatch):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/installations/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/installations/0/")
    assert response.status_code == 422
