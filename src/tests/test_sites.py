import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api.crud import base
from app.api.routes import sites


SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "lat": 0., "lon": 0., "type": "tower",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "lat": 10., "lon": 5., "type": "station",
     "created_at": "2020-09-13T08:18:45.447773"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(sites, "sites", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(base, "get", pytest.mock_get)
    monkeypatch.setattr(base, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(base, "post", pytest.mock_post)
    monkeypatch.setattr(base, "put", pytest.mock_put)
    monkeypatch.setattr(base, "delete", pytest.mock_delete)


def test_get_site(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.get("/sites/1")
    assert response.status_code == 200
    assert response.json() == mock_site_table[0]


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_site_invalid(test_app, monkeypatch, site_id, status_code, status_details):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.get(f"/sites/{site_id}")
    assert response.status_code == status_code, site_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_sites(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.get("/sites/")
    assert response.status_code == 200
    assert response.json() == mock_site_table


def test_create_site(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    test_payload = {"name": "my_site", "lat": 0., "lon": 0., "type": "tower"}
    test_response = {"id": len(mock_site_table) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = test_app.post("/sites/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_site_table[-1]['created_at'] > utc_dt and mock_site_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"names": "my_site", "lat": 0., "lon": 0., "type": "tower"}, 422],
        [{"name": "my_site", "lat": 0.}, 422],
    ],
)
def test_create_site_invalid(test_app, payload, status_code):
    response = test_app.post("/sites/", data=json.dumps(payload))
    assert response.status_code == status_code


def test_update_site(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    test_payload = {"name": "renamed_site", "lat": 0., "lon": 0., "type": "tower"}
    response = test_app.put("/sites/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_site_table[0].items():
        assert v == test_payload.get(k, SITE_TABLE[0][k])


@pytest.mark.parametrize(
    "site_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"site_name": "foo"}, 422],
        [999, {"name": "foo", "lat": 0., "lon": 0., "type": "tower"}, 404],
        [1, {"name": "1", "lat": 0., "lon": 0., "type": "tower"}, 422],
        [0, {"name": "foo", "lat": 0., "lon": 0., "type": "tower"}, 422],
    ],
)
def test_update_site_invalid(test_app, monkeypatch, site_id, payload, status_code):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.put(f"/sites/{site_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_site(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.delete("/sites/1/")
    assert response.status_code == 200
    assert response.json() == SITE_TABLE[0]
    for entry in mock_site_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_site_invalid(test_app, monkeypatch, site_id, status_code, status_details):
    # Sterilize DB interactions
    mock_site_table = deepcopy(SITE_TABLE)
    _patch_session(monkeypatch, mock_site_table)

    response = test_app.delete(f"/sites/{site_id}/")
    assert response.status_code == status_code, print(site_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(site_id)
