import json
import pytest

from app.api import crud


MIN_PAYLOAD = {"device_id": 1, "event_id": 1, "lat": 0, "lon": 0}
FULL_PAYLOAD = {**MIN_PAYLOAD, "media_id": None, "type": "start", "is_acknowledged": False}


def test_create_alert(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **FULL_PAYLOAD}

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/alerts/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


def test_create_alert_invalid_json(test_app):
    response = test_app.post("/alerts/", data=json.dumps({"device": 1}))
    assert response.status_code == 422

    response = test_app.post("/alerts/", data=json.dumps({**MIN_PAYLOAD, "type": "1"}))
    assert response.status_code == 422


def test_get_alert(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/alerts/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_get_alert_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/alerts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/alerts/0")
    assert response.status_code == 422


def test_fetch_alerts(test_app, monkeypatch):
    test_data = [
        {"id": 1, **FULL_PAYLOAD},
        {"id": 2, **FULL_PAYLOAD},
    ]

    async def mock_get_all(table):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/alerts/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_data


def test_update_alert(test_app, monkeypatch):
    test_update_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/alerts/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"site_id": 1}, 422],
        [999, FULL_PAYLOAD, 404],
        [1, {**MIN_PAYLOAD, "type": "1"}, 422],
        [0, FULL_PAYLOAD, 422],
    ],
)
def test_update_alert_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/alerts/{id}/", data=json.dumps(payload),)
    assert response.status_code == status_code, print(payload)


def test_remove_alert(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/alerts/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_remove_alert_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/alerts/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/alerts/0/")
    assert response.status_code == 422
