import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api.crud import base
from app.api.routes import events


EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-09-13T08:18:45.447773"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(events, "events", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(base, "get", pytest.mock_get)
    monkeypatch.setattr(base, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(base, "post", pytest.mock_post)
    monkeypatch.setattr(base, "put", pytest.mock_put)
    monkeypatch.setattr(base, "delete", pytest.mock_delete)


def test_get_event(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.get("/events/1")
    assert response.status_code == 200
    assert response.json() == mock_event_table[0]


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_event_invalid(test_app, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.get(f"/events/{event_id}")
    assert response.status_code == status_code, event_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_events(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.get("/events/")
    assert response.status_code == 200
    assert response.json() == mock_event_table


def test_create_event(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    test_payload = {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}
    test_response = {"id": len(mock_event_table) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = test_app.post("/events/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_event_table[-1]['created_at'] > utc_dt and mock_event_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 422],
        [{"lat": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 422],
    ],
)
def test_create_event_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.post("/events/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_event(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    test_payload = {"lat": 5., "lon": 10., "type": "wildfire"}
    response = test_app.put("/events/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_event_table[0].items():
        assert v == test_payload.get(k, EVENT_TABLE[0][k])


@pytest.mark.parametrize(
    "event_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "wildfire"}, 422],
        [999, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 404],
        [1, {"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 422],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": "now", "end_ts": None}, 422],
        [0, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 422],
    ],
)
def test_update_event_invalid(test_app, monkeypatch, event_id, payload, status_code):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.put(f"/events/{event_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_event(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == EVENT_TABLE[0]
    for entry in mock_event_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_event_invalid(test_app, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    mock_event_table = deepcopy(EVENT_TABLE)
    _patch_session(monkeypatch, mock_event_table)

    response = test_app.delete(f"/events/{event_id}/")
    assert response.status_code == status_code, print(event_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(event_id)
