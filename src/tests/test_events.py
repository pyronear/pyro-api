import json
import pytest
from datetime import datetime
from app import db
from app.api import crud
from tests.conf_test_db import get_entry_in_db, populate_db

EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-09-13T08:18:45.447773"},
]


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict):
    to_return = entity_as_dict.copy()
    if "created_at" in to_return:
        to_return["created_at"] = datetime.strptime(to_return["created_at"], DATETIME_FORMAT)
    return to_return


EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud, "database", test_db)

    await populate_db(test_db, db.events, EVENT_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_event(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/events/1")
    assert response.status_code == 200
    assert response.json() == EVENT_TABLE[0]


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_event_invalid(test_app_asyncio, test_db, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/events/{event_id}")
    assert response.status_code == status_code, event_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_events(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/events/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in EVENT_TABLE]


@pytest.mark.asyncio
async def test_create_event(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}
    test_response = {"id": len(EVENT_TABLE) + 1, **test_payload}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/events/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()

    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    new_event_in_db = await get_entry_in_db(test_db, db.events, json_response["id"])
    new_event_in_db = dict(**new_event_in_db)
    assert new_event_in_db['created_at'] > utc_dt and new_event_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 422],
        [{"lat": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_event_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/events/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_event(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"lat": 5., "lon": 10., "type": "wildfire"}
    response = await test_app_asyncio.put("/events/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_event_in_db = await get_entry_in_db(test_db, db.events, 1)
    updated_event_in_db = dict(**updated_event_in_db)
    for k, v in updated_event_in_db.items():
        assert v == test_payload.get(k, EVENT_TABLE_FOR_DB[0][k])


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
@pytest.mark.asyncio
async def test_update_event_invalid(test_app_asyncio, test_db, monkeypatch, event_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/events/{event_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_event(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == EVENT_TABLE[0]
    remaining_events = await test_app_asyncio.get("/events/")
    for entry in remaining_events.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_event_invalid(test_app_asyncio, test_db, monkeypatch, event_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/events/{event_id}/")
    assert response.status_code == status_code, print(event_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(event_id)
