import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api import crud
from app.api.routes import alerts


ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "start",
     "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "end",
     "is_acknowledged": True, "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "start",
     "is_acknowledged": False, "created_at": "2020-11-03T11:18:45.447773"},
]


async def mock_fetch_ongoing_alerts(table, query_filters=None, excluded_events_filter=None):
    excluded_events = []
    for entry in table:
        if all(entry[k] == v for k, v in excluded_events_filter.items()):
            excluded_events.append(entry["event_id"])

    response = []
    for entry in table:
        if all(entry[k] == v for k, v in query_filters.items()):
            if entry["event_id"] not in excluded_events:
                response.append(entry)
    return response


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(alerts, "alerts", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "fetch_ongoing_alerts", mock_fetch_ongoing_alerts)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)


def test_get_alert(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.get("/alerts/1")
    assert response.status_code == 200
    assert response.json() == mock_alert_table[0]


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_alert_invalid(test_app, monkeypatch, alert_id, status_code, status_details):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.get(f"/alerts/{alert_id}")
    assert response.status_code == status_code, alert_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_alerts(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.get("/alerts/")
    assert response.status_code == 200
    assert response.json() == mock_alert_table


def test_fetch_ongoing_alerts(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.get("/alerts/ongoing")
    assert response.status_code == 200
    assert response.json() == [x for x in mock_alert_table if x["id"] == 3]


def test_fetch_unacknowledged_alerts(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.get("/alerts/unacknowledged")
    assert response.status_code == 200
    assert response.json() == [x for x in mock_alert_table if x["is_acknowledged"] is False]


def test_create_alert(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    test_payload = {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "end"}
    test_response = {"id": len(mock_alert_table) + 1, **test_payload, "media_id": None, "is_acknowledged": False}

    utc_dt = datetime.utcnow()
    response = test_app.post("/alerts/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_alert_table[-1]['created_at'] > utc_dt and mock_alert_table[-1]['created_at'] < datetime.utcnow()


def test_create_alert_by_device(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    test_payload = {"event_id": 2, "lat": 10., "lon": 8., "type": "end"}
    # Device_id is 99 because it is the identified device
    test_response = {"id": len(mock_alert_table) + 1,
                     "device_id": 99, **test_payload,
                     "media_id": None, "is_acknowledged": False}

    utc_dt = datetime.utcnow()
    response = test_app.post("/alerts/from-device", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_alert_table[-1]['created_at'] > utc_dt and mock_alert_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "restart"}, 422],
        [{"event_id": 2, "lat": 10., "lon": 8., "type": "end"}, 422],
    ],
)
def test_create_alert_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.post("/alerts/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_alert(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    test_payload = {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8., "type": "start"}
    response = test_app.put("/alerts/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in test_payload.items():
        assert v == mock_alert_table[0][k]


@pytest.mark.parametrize(
    "alert_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "start"}, 422],
        [999, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 404],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "restart", "is_acknowledged": True}, 422],
        [0, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 422],
    ],
)
def test_update_alert_invalid(test_app, monkeypatch, alert_id, payload, status_code):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.put(f"/alerts/{alert_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_alert(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.delete("/alerts/1/")
    assert response.status_code == 200
    assert response.json() == ALERT_TABLE[0]
    for entry in mock_alert_table:
        assert entry['id'] != 1


def test_link_media_owner(test_app, monkeypatch):
    # Create Alert (Identical code to the create_alert above)
    mock_alert_table = deepcopy(ALERT_TABLE)
    # Set device_id to 99 because it is the one that is authentified in our testConfig.
    mock_alert_table[0]["device_id"] = 99
    _patch_session(monkeypatch, mock_alert_table)

    test_payload = {"media_id": 1}
    updated_alert = mock_alert_table[0]
    test_response = updated_alert.copy()
    test_response.update(test_payload)

    response = test_app.put(f"/alerts/{updated_alert['id']}/link-media", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in test_payload.items():
        assert v == mock_alert_table[0][k]


def test_link_media_owner_not_allowed(test_app, monkeypatch):
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    test_payload = {"media_id": 1}
    updated_alert = mock_alert_table[0]
    test_response = updated_alert.copy()
    test_response.update(test_payload)

    response = test_app.post(f"/alerts/{updated_alert['id']}/link-media", data=json.dumps(test_payload))
    assert response.status_code == 405


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_alert_invalid(test_app, monkeypatch, alert_id, status_code, status_details):
    # Sterilize DB interactions
    mock_alert_table = deepcopy(ALERT_TABLE)
    _patch_session(monkeypatch, mock_alert_table)

    response = test_app.delete(f"/alerts/{alert_id}/")
    assert response.status_code == status_code, print(alert_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(alert_id)
