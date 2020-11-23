import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api import crud
from app.api.routes import installations


INSTALLATION_TABLE = [
    {"id": 1, "device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
     "start_ts": None, "end_ts": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 2, "site_id": 2, "elevation": 58., "lat": 5., "lon": 8., "yaw": 10., "pitch": 0.,
     "start_ts": None, "end_ts": None, "created_at": "2020-11-13T08:18:45.447773"},
]


async def mock_get_custom_entry(query):

    return [INSTALLATION_TABLE[0]["device_id"]]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(installations, "installations", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)


def test_get_installation(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.get("/installations/1")
    assert response.status_code == 200
    assert response.json() == mock_installation_table[0]


@pytest.mark.parametrize(
    "installation_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_installation_invalid(test_app, monkeypatch, installation_id, status_code, status_details):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.get(f"/installations/{installation_id}")
    assert response.status_code == status_code, installation_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_installations(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.get("/installations/")
    assert response.status_code == 200
    assert response.json() == mock_installation_table


def test_create_installation(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    test_payload = {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}
    test_response = {"id": len(mock_installation_table) + 1, **test_payload, "start_ts": None, "end_ts": None}

    utc_dt = datetime.utcnow()
    response = test_app.post("/installations/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_installation_table[-1]['created_at'] > utc_dt
    assert mock_installation_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
        [{"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0.}, 422],
    ],
)
def test_create_installation_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.post("/installations/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_installation(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    test_payload = {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}
    response = test_app.put("/installations/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_installation_table[0].items():
        assert v == test_payload.get(k, INSTALLATION_TABLE[0][k])


@pytest.mark.parametrize(
    "installation_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"device_id": 1}, 422],
        [999, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 404],
        [1, {"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
        [0, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
    ],
)
def test_update_installation_invalid(test_app, monkeypatch, installation_id, payload, status_code):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.put(f"/installations/{installation_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_installation(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.delete("/installations/1/")
    assert response.status_code == 200
    assert response.json() == INSTALLATION_TABLE[0]
    for entry in mock_installation_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "installation_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_installation_invalid(test_app, monkeypatch, installation_id, status_code, status_details):
    # Sterilize DB interactions
    mock_installation_table = deepcopy(INSTALLATION_TABLE)
    _patch_session(monkeypatch, mock_installation_table)

    response = test_app.delete(f"/installations/{installation_id}/")
    assert response.status_code == status_code, print(installation_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(installation_id)


def test_list_devices(test_app, monkeypatch):
    monkeypatch.setattr(crud, "get_custom_entry", mock_get_custom_entry)

    response = test_app.get("/installations/list_devices/1?timestamp=2020-11-13T08:18:45.447773")
    assert response.status_code == 200
    assert response.json() == [INSTALLATION_TABLE[0]["device_id"]]
