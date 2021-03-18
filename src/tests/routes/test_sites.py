# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime

SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "lat": 44.1, "lon": -0.7, "type": "tower", "country": "FR", "geocode": "40",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "lat": 44.1, "lon": 3.9, "type": "station", "country": "FR", "geocode": "30",
     "created_at": "2020-09-13T08:18:45.447773"},
]


def compare_entries(ref, test):
    for k, v in ref.items():
        if isinstance(v, float):
            # For float issues
            assert abs(v - test[k]) < 1E-5
        else:
            assert v == test[k]


SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.sites, SITE_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_site(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/sites/1")
    response_json = response.json()
    assert response.status_code == 200
    compare_entries(response_json, SITE_TABLE[0])


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_site_invalid(test_app_asyncio, test_db, monkeypatch, site_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/sites/{site_id}")
    assert response.status_code == status_code, site_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_sites(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/sites/")
    assert response.status_code == 200
    response_json = response.json()
    for (i, entry) in enumerate(response_json):
        compare_entries(entry, SITE_TABLE[i])


@pytest.mark.asyncio
async def test_create_site(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"name": "my_site", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}
    test_response = {"id": len(SITE_TABLE) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/sites/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    new_site_in_db = await get_entry_in_db(test_db, db.sites, json_response["id"])
    new_site_in_db = dict(**new_site_in_db)
    assert new_site_in_db['created_at'] > utc_dt and new_site_in_db['created_at'] < datetime.utcnow()


@pytest.mark.asyncio
async def test_create_no_alert_site(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"name": "my_site", "lat": 0., "lon": 0., "country": "FR", "geocode": "01"}
    test_response = {"id": len(SITE_TABLE) + 1, "type": "no_alert", **test_payload}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/sites/create-no-alert-site/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    new_site_in_db = await get_entry_in_db(test_db, db.sites, json_response["id"])
    new_site_in_db = dict(**new_site_in_db)
    assert new_site_in_db['created_at'] > utc_dt and new_site_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"names": "my_site", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 422],
        [{"name": "my_site", "lat": 0., "country": "FR", "geocode": "01"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_site_invalid(test_app_asyncio, test_db, payload, status_code):
    response = await test_app_asyncio.post("/sites/", data=json.dumps(payload))
    assert response.status_code == status_code


@pytest.mark.asyncio
async def test_update_site(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"name": "renamed_site", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}
    response = await test_app_asyncio.put("/sites/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_site_in_db = await get_entry_in_db(test_db, db.sites, 1)
    updated_site_in_db = dict(**updated_site_in_db)
    for k, v in updated_site_in_db.items():
        assert v == test_payload.get(k, SITE_TABLE_FOR_DB[0][k])


@pytest.mark.parametrize(
    "site_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"site_name": "foo"}, 422],
        [999, {"name": "foo", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 404],
        [1, {"name": "1", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 422],
        [0, {"name": "foo", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_site_invalid(test_app_asyncio, test_db, monkeypatch, site_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/sites/{site_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_site(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/sites/1/")
    assert response.status_code == 200
    compare_entries(response.json(), SITE_TABLE[0])

    remaining_sites = await test_app_asyncio.get("/sites/")
    for entry in remaining_sites.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_site_invalid(test_app_asyncio, test_db, monkeypatch, site_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/sites/{site_id}/")
    assert response.status_code == status_code, print(site_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(site_id)
