import json
import pytest
from datetime import datetime

from app.api import crud


MOCK_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None, "created_at": "2020-10-13T08:18:45.447773"},
]


def _patch_crud(monkeypatch, mock_table):
    # Sterilize all DB interactions
    async def mock_get(entry_id, table):
        for entry in mock_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_fetch_all(entry_id, table):
        return mock_table

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


def test_get_event(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get("/events/1")
    assert response.status_code == 200
    assert response.json() == local_db[0]


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_event_invalid(test_app, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get(f"/events/{event_id}")
    assert response.status_code == status_code, event_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_events(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.get("/events/")
    assert response.status_code == 200
    assert response.json() == local_db


def test_create_event(test_app, monkeypatch):

    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    test_payload = {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}
    test_response = {"id": len(local_db) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = test_app.post("/events/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert local_db[-1]['created_at'] > utc_dt and local_db[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 422],
        [{"lat": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 422],
    ],
)
def test_create_event_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.post("/events/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_event(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    test_payload = {"lat": 5., "lon": 10., "type": "wildfire"}
    response = test_app.put("/events/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in local_db[0].items():
        assert v == test_payload.get(k, MOCK_TABLE[0][k])


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
def test_update_site_invalid(test_app, monkeypatch, event_id, payload, status_code):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.put(f"/events/{event_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_event(test_app, monkeypatch):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == MOCK_TABLE[0]
    for entry in local_db:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_site_invalid(test_app, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    local_db = MOCK_TABLE.copy()
    _patch_crud(monkeypatch, local_db)

    response = test_app.delete(f"/events/{event_id}/")
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)
