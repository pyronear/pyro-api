import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api import crud


ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "start", "is_acknowledged": True,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "end", "is_acknowledged": True,
     "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": False,
     "created_at": "2020-11-03T11:18:45.447773"},
]


def _patch_session(monkeypatch, mock_table):
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


def test_get_alert(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.get("/alerts/1")
    assert response.status_code == 200
    assert response.json() == local_db[0]


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_alert_invalid(test_app, monkeypatch, alert_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.get(f"/alerts/{alert_id}")
    assert response.status_code == status_code, alert_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_alerts(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.get("/alerts/")
    assert response.status_code == 200
    assert response.json() == local_db


def test_create_alert(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    test_payload = {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "end"}
    test_response = {"id": len(local_db) + 1, **test_payload, "media_id": None, "is_acknowledged": False}

    utc_dt = datetime.utcnow()
    response = test_app.post("/alerts/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert local_db[-1]['created_at'] > utc_dt and local_db[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "restart"}, 422],
        [{"event_id": 2, "lat": 10., "lon": 8., "type": "end"}, 422],
    ],
)
def test_create_alert_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.post("/alerts/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_alert(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    test_payload = {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8., "type": "start"}
    response = test_app.put("/alerts/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in test_payload.items():
        assert v == local_db[0][k]


@pytest.mark.parametrize(
    "alert_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "start"}, 422],
        [999, {"device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 404],
        [1, {"device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "restart", "is_acknowledged": True}, 422],
        [0, {"device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 422],
    ],
)
def test_update_alert_invalid(test_app, monkeypatch, alert_id, payload, status_code):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.put(f"/alerts/{alert_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_alert(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.delete("/alerts/1/")
    assert response.status_code == 200
    assert response.json() == ALERT_TABLE[0]
    for entry in local_db:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_alert_invalid(test_app, monkeypatch, alert_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, local_db)

    response = test_app.delete(f"/alerts/{alert_id}/")
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)
