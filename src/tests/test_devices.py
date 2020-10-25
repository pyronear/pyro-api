import json
import pytest

from app.api import crud

MIN_PAYLOAD = {"name": "my_device", "owner_id": 1, "specs": "my_specs"}

FULL_PAYLOAD = {
    **MIN_PAYLOAD,
    "last_lat": None,
    "last_lon": None,
    "last_elevation": None,
    "last_yaw": None,
    "last_pitch": None,
    "last_ping": None,
}


@pytest.fixture(scope="function")
def existing_devices():
    # device id 1->4 owned by user 99 (connected_user), id 5->6 owned by user 1
    return [{"id": did, **FULL_PAYLOAD, "owner_id": 99 if did <= 4 else 1} for did in range(1, 7)]


def test_fetch_my_devices(test_app, monkeypatch, existing_devices):
    async def fetch_by_owner(owner_id):
        return [d for d in existing_devices if d["owner_id"] == owner_id]

    monkeypatch.setattr(crud.device, "fetch_by_owner", fetch_by_owner)

    response = test_app.get("/devices/my-devices")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != "created_at"} for r in response.json()] == [
        d for d in existing_devices if d["id"] <= 4
    ]


def test_create_device(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **FULL_PAYLOAD}

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/devices/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != "created_at"} == test_response_payload


def test_create_device_invalid_json(test_app):
    response = test_app.post("/devices/", data=json.dumps({"username": "my_device", "owner_id": 1, "specs": "s"}))
    assert response.status_code == 422

    response = test_app.post("/devices/", data=json.dumps({"name": "1", "owner_id": 1, "specs": "2"}))
    assert response.status_code == 422


def test_get_device(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/devices/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != "created_at"} == test_data


def test_get_device_incorrect_id(test_app, monkeypatch):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/devices/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/devices/0")
    assert response.status_code == 422


def test_fetch_devices(test_app, monkeypatch):
    test_data = [
        {"id": 1, **FULL_PAYLOAD},
        {"id": 2, **FULL_PAYLOAD},
    ]

    async def mock_get_all(table):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/devices/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != "created_at"} for r in response.json()] == test_data


def test_update_device(test_app, monkeypatch):
    test_update_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/devices/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != "created_at"} == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"last_ping": None}, 422],
        [999, {"name": "foo", "owner_id": 1, "specs": "my_specs"}, 404],
        [1, {"name": "1", "owner_id": 1, "specs": "my_specs"}, 422],
        [0, {"name": "foo", "owner_id": 1, "specs": "my_specs"}, 422],
    ],
)
def test_update_device_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(
        f"/devices/{id}/",
        data=json.dumps(payload),
    )
    assert response.status_code == status_code, print(payload)


def test_remove_device(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(id, table):
        return id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/devices/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != "created_at"} == test_data


def test_remove_device_incorrect_id(test_app, monkeypatch):
    async def mock_get(id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/devices/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/devices/0/")
    assert response.status_code == 422
