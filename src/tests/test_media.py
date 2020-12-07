import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from app.services import bucket_service
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]

USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [{"id": 1, "login": "connected_device", "owner_id": 1,
                 "access_id": 3, "specs": "raspberry", "elevation": None, "lat": None,
                 "lon": None, "yaw": None, "pitch": None,
                 "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
                {"id": 2, "login": "second_device", "owner_id": 2,
                 "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
                 "lon": None, "yaw": None, "pitch": None,
                 "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
                {"id": 3, "login": "third_device", "owner_id": 1,
                 "access_id": 5, "specs": "v0.1", "elevation": None,
                 "lat": None, "lon": None, "yaw": None, "pitch": None, "last_ping": None,
                 "created_at": "2020-10-13T08:18:45.447773"}
                ]

CONNECTED_DEVICE_ID = 3

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 2, "login": "connected_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 3, "login": "first_device", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 4, "login": "second_device", "hashed_password": "second_pwd_hashed", "scopes": "device"},
    {"id": 5, "login": "connected_device", "hashed_password": "third_pwd_hashed", "scopes": "device"},
]


ACCESS_TABLE_FOR_DB = list(map(update_only_datetime, ACCESS_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE_FOR_DB)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)
    await populate_db(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await populate_db(test_db, db.media, MEDIA_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_media(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/media/1")
    assert response.status_code == 200
    assert response.json() == MEDIA_TABLE[0]


@pytest.mark.parametrize(
    "media_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_media_invalid(test_app_asyncio, test_db, monkeypatch, media_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/media/{media_id}")
    assert response.status_code == status_code, media_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_media(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/media/")
    assert response.status_code == 200
    assert response.json() == MEDIA_TABLE


@pytest.mark.asyncio
async def test_create_media(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 1}
    test_response = {"id": len(MEDIA_TABLE) + 1, **test_payload, "type": "image"}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/media/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

    new_media_in_db = await get_entry_in_db(test_db, db.media, json_response["id"])
    new_media_in_db = dict(**new_media_in_db)

    # Timestamp consistency
    assert new_media_in_db['created_at'] > utc_dt and new_media_in_db['created_at'] < datetime.utcnow()


@pytest.mark.asyncio
async def test_create_media_from_device(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {}

    # Device_id is 3 because it is the id of the authentified sending device.
    test_response = {"id": len(MEDIA_TABLE) + 1, "device_id": CONNECTED_DEVICE_ID, "type": "image"}

    response = await test_app_asyncio.post("/media/from-device", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

    new_media_in_db = await get_entry_in_db(test_db, db.media, json_response["id"])
    new_media_in_db = dict(**new_media_in_db)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": "my_device"}, 422],
        [{}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_media_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/media/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_media(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 1, "type": "video"}
    response = await test_app_asyncio.put("/media/1/", data=json.dumps(test_payload))
    assert response.status_code == 200

    updated_media_in_db = await get_entry_in_db(test_db, db.media, 1)
    updated_media_in_db = dict(**updated_media_in_db)
    for k, v in updated_media_in_db.items():
        if k != "bucket_key":
            assert v == test_payload.get(k, MEDIA_TABLE_FOR_DB[0][k])


@pytest.mark.parametrize(
    "media_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "audio"}, 422],
        [999, {"device_id": 1, "type": "image"}, 404],
        [1, {"device_id": 1, "type": "audio"}, 422],
        [1, {"device_id": "my_device", "type": "image"}, 422],
        [0, {"device_id": 1, "type": "image"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_media_invalid(test_app_asyncio, test_db, monkeypatch, media_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/media/{media_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_media(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/media/1/")
    assert response.status_code == 200
    assert response.json() == MEDIA_TABLE[0]
    remaining_media = await test_app_asyncio.get("/media/")
    for entry in remaining_media.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "media_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_media_invalid(test_app_asyncio, test_db, monkeypatch, media_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/media/{media_id}/")
    assert response.status_code == status_code, print(media_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(media_id)


@pytest.mark.asyncio
async def test_upload_media(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    # 1 - Create a media that will have an upload
    payload_creation_device = {"device_id": CONNECTED_DEVICE_ID}
    newly_created_media_id = len(MEDIA_TABLE_FOR_DB) + 1
    response = await test_app_asyncio.post("/media/", data=json.dumps(payload_creation_device))
    assert response.status_code == 201

    # 2 - Upload something
    async def successful_upload(bucket_key, file_binary):
        return True
    monkeypatch.setattr(bucket_service, "upload_file", successful_upload)
    response = await test_app_asyncio.post(f"/media/{response.json()['id']}/upload", files=dict(file='bar'))

    assert response.status_code == 200
    new_media_in_db = await get_entry_in_db(test_db, db.media, response.json()["id"])
    new_media_in_db = dict(**new_media_in_db)
    response_json = response.json()
    response_json.pop("created_at")
    assert {k: v for k, v in new_media_in_db.items() if k not in ('created_at', "bucket_key")} == response_json
    assert new_media_in_db["bucket_key"] is not None

    # 2b - Upload failing
    async def failing_upload(bucket_key, file_binary):
        return False
    monkeypatch.setattr(bucket_service, "upload_file", failing_upload)
    response = await test_app_asyncio.post(f"/media/{newly_created_media_id}/upload", files=dict(file='bar'))
    assert response.status_code == 500
