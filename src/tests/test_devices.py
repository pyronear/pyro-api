import json
import pytest
from app.api import crud
from datetime import datetime


MIN_PAYLOAD = {"name": "my_device", "owner_id": 1, "specs": "my_specs", "password": "my_password"}
FULL_PAYLOAD = {
    **MIN_PAYLOAD,
    "lat": None,
    "lon": None,
    "elevation": None,
    "yaw": None,
    "pitch": None,
    "last_ping": None,
}
REPLY_PAYLOAD = FULL_PAYLOAD.copy()
REPLY_PAYLOAD.pop("password")


def test_fetch_my_devices(test_app, monkeypatch):
    # device id 1->4 owned by user 99 (connected_user), id 5->6 owned by user 1
    test_data = [{"id": did, **REPLY_PAYLOAD, "owner_id": 99 if did <= 4 else 1} for did in range(1, 7)]

    async def mock_fetch_by_owner(table, query_filter):
        return [entry for entry in test_data if entry[query_filter[0]] == query_filter[1]]

    monkeypatch.setattr(crud, "fetch_all", mock_fetch_by_owner)

    response = test_app.get("/devices/my-devices")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != "created_at"} for r in response.json()] == [
        d for d in test_data if d["id"] <= 4
    ]


def test_create_device(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **REPLY_PAYLOAD}

    async def mock_fetch_one(table, query_filter):
        return None

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/devices/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k not in ('created_at')} == test_response_payload


def test_create_device_if_already_exists(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD

    async def mock_fetch_one(table, query_filter):
        return test_request_payload

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/devices/", data=json.dumps(test_request_payload))

    assert response.status_code == 400


def test_create_device_invalid_json(test_app):
    response = test_app.post("/devices/", data=json.dumps({"username": "my_device", "owner_id": 1, "specs": "s"}))
    assert response.status_code == 422

    response = test_app.post("/devices/", data=json.dumps({"name": "1", "owner_id": 1, "specs": "2"}))
    assert response.status_code == 422


def test_get_device(test_app, monkeypatch):
    test_data = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/devices/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_get_device_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/devices/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/devices/0")
    assert response.status_code == 422


def test_fetch_devices(test_app, monkeypatch):
    test_data = [
        {"id": 1, **REPLY_PAYLOAD},
        {"id": 2, **REPLY_PAYLOAD},
    ]

    async def mock_get_all(table, query_filter=None):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/devices/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_data


def test_update_device(test_app, monkeypatch):
    test_update_data = {"id": 1, **FULL_PAYLOAD}
    test_response_payload = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/devices/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"last_ping": None}, 422],
        [999, {"name": "foo", "owner_id": 1, "specs": "my_specs", "password": "my_password"}, 404],
        [1, {"name": "1", "owner_id": 1, "specs": "my_specs", "password": "my_password"}, 422],
        [0, {"name": "foo", "owner_id": 1, "specs": "my_specs", "password": "my_password"}, 422],
    ],
)
def test_update_device_invalid(test_app, monkeypatch, device_id, payload, status_code):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/devices/{device_id}/", data=json.dumps(payload),)
    assert response.status_code == status_code, print(payload)


def test_remove_device(test_app, monkeypatch):
    test_data = {"id": 1, **REPLY_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/devices/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_remove_device_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/devices/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/devices/0/")
    assert response.status_code == 422


def test_heartbeat(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return None

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.post("/devices/heartbeat")
    assert response.status_code == 200
    assert "last_ping" in response.json()
    try:
        last_ping = response.json()["last_ping"]
        datetime.fromisoformat(last_ping)

    except Exception as e:
        raise(e)


def test_update_location(test_app, monkeypatch):
    test_data = {"id": 1, **REPLY_PAYLOAD}
    update_location_data = {"lat": 1.0,
                            "lon": 2.0,
                            "elevation": 3.0,
                            "yaw": 4.0,
                            "pitch": 5.0
                            }
    test_response_payload = test_data.copy()
    for k, v in update_location_data.items():
        test_response_payload[k] = v

    async def mock_get(entry_id, table):
        return test_data
    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_fetch_one(table, query_filters):
        return True

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def mock_put(entry_id, payload, table):
        return None
    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.post("/devices/1/update-location", data=json.dumps(update_location_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


def test_update_location_on_not_owned_device(test_app, monkeypatch):
    update_location_data = {"lat": 1.0,
                            "lon": 2.0,
                            "elevation": 3.0,
                            "yaw": 4.0,
                            "pitch": 5.0
                            }

    async def mock_fetch_one(table, query_filters):
        return False
    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    response = test_app.post("/devices/1/update-location", data=json.dumps(update_location_data))
    assert response.status_code == 400
