# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import requests
import pytest
import os
import tempfile
from datetime import datetime

from app import db
from app.api import crud
from app.services import bucket_service
from tests.db_utils import get_entry, fill_table, TestSessionLocal
from tests.utils import update_only_datetime


USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
    {"id": 3, "login": "fifth_login", "access_id": 5, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68., "software_hash": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68., "software_hash": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},

]

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 2, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(db, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.media, MEDIA_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, media_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 200, None],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table media has no entry with id=999"],
        [1, 0, 422, None],
        [4, 1, 403, "This access can't read resources from group_id=1"],
    ],
)
@pytest.mark.asyncio
async def test_get_media(test_app_asyncio, init_test_db, access_idx, media_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get(f"/media/{media_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == MEDIA_TABLE[media_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [None, 401, "Not authenticated", None],
        [0, 200, None, [MEDIA_TABLE[0]]],
        [1, 200, None, MEDIA_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_media(test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_results):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/media/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_results


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [0, {"device_id": 1}, 403, "Your access scope is not compatible with this operation."],
        [1, {"device_id": 1}, 201, None],
        [2, {"device_id": 1}, 403, "Your access scope is not compatible with this operation."],
        [1, {"device_id": "device"}, 422, None],
        [1, {}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_media(test_app_asyncio, init_test_db, test_db, access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/media/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(MEDIA_TABLE) + 1, **payload, "type": "image"}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        new_media = await get_entry(test_db, db.media, json_response["id"])
        new_media = dict(**new_media)

        # Timestamp consistency
        assert new_media['created_at'] > utc_dt and new_media['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [0, {}, 403, "Your access scope is not compatible with this operation."],
        [1, {}, 403, "Your access scope is not compatible with this operation."],
        [2, {}, 201, None],
    ],
)
@pytest.mark.asyncio
async def test_create_media_from_device(test_app_asyncio, init_test_db, test_db,
                                        access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/media/from-device", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        device_id = None
        for entry in DEVICE_TABLE:
            if entry['access_id'] == ACCESS_TABLE[access_idx]['id']:
                device_id = entry['id']
                break
        test_response = {"id": len(MEDIA_TABLE) + 1, "device_id": device_id, "type": "image"}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        new_media = await get_entry(test_db, db.media, json_response["id"])
        new_media = dict(**new_media)
        # Timestamp consistency
        assert new_media['created_at'] > utc_dt and new_media['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, media_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [0, {"device_id": 1, "type": "video"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {"device_id": 1, "type": "video"}, 1, 200, None],
        [2, {"device_id": 1, "type": "video"}, 1, 403, "Your access scope is not compatible with this operation."],
        [1, {}, 1, 422, None],
        [1, {"type": "audio"}, 1, 422, None],
        [1, {"device_id": 1, "type": "image"}, 999, 404, "Table media has no entry with id=999"],
        [1, {"device_id": 1, "type": "audio"}, 1, 422, None],
        [1, {"device_id": "my_device", "type": "image"}, 1, 422, None],
        [1, {"device_id": 1, "type": "image"}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_media(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, media_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/media/{media_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_media = await get_entry(test_db, db.media, media_id)
        updated_media = dict(**updated_media)
        for k, v in updated_media.items():
            if k != "bucket_key":
                assert v == payload.get(k, MEDIA_TABLE_FOR_DB[media_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, media_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table media has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_media(test_app_asyncio, init_test_db, access_idx, media_id, status_code, status_details):

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/media/{media_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == MEDIA_TABLE[media_id - 1]
        remaining_media = await test_app_asyncio.get("/media/", headers=auth)
        assert all(entry['id'] != media_id for entry in remaining_media.json())


@pytest.mark.asyncio
async def test_upload_media(test_app_asyncio, init_test_db, test_db, monkeypatch):

    device_idx = 2
    admin_idx = 1
    device_id = None
    for entry in DEVICE_TABLE:
        if entry['access_id'] == ACCESS_TABLE[device_idx]['id']:
            device_id = entry['id']
            break
    # Create a custom access token
    device_auth = await pytest.get_token(ACCESS_TABLE[device_idx]['id'], ACCESS_TABLE[device_idx]['scope'].split())
    admin_auth = await pytest.get_token(ACCESS_TABLE[admin_idx]['id'], ACCESS_TABLE[admin_idx]['scope'].split())

    # 1 - Create a media that will have an upload
    payload = {"device_id": device_id}
    new_media_id = len(MEDIA_TABLE_FOR_DB) + 1
    response = await test_app_asyncio.post("/media/", data=json.dumps(payload), headers=admin_auth)
    assert response.status_code == 201

    # 2 - Upload something
    async def mock_upload_file(bucket_key, file_binary):
        return True
    monkeypatch.setattr(bucket_service, "upload_file", mock_upload_file)

    # Download and save a temporary file
    local_tmp_path = os.path.join(tempfile.gettempdir(), "my_temp_image.jpg")
    img_content = requests.get("https://pyronear.org/img/logo_letters.png").content
    with open(local_tmp_path, 'wb') as f:
        f.write(img_content)

    async def mock_get_file(bucket_key):
        return local_tmp_path
    monkeypatch.setattr(bucket_service, "get_file", mock_get_file)

    async def mock_delete_file(filename):
        return True
    monkeypatch.setattr(bucket_service, "delete_file", mock_delete_file)

    # Switch content-type from JSON to multipart
    del device_auth["Content-Type"]

    response = await test_app_asyncio.post(f"/media/{new_media_id}/upload",
                                           files=dict(file=img_content), headers=device_auth)

    assert response.status_code == 200, print(response.json()['detail'])
    response_json = response.json()
    updated_media = await get_entry(test_db, db.media, response_json["id"])
    updated_media = dict(**updated_media)
    response_json.pop("created_at")
    assert {k: v for k, v in updated_media.items() if k not in ('created_at', "bucket_key")} == response_json
    assert updated_media["bucket_key"] is not None

    # 2b - Upload failing
    async def failing_upload(bucket_key, file_binary):
        return False
    monkeypatch.setattr(bucket_service, "upload_file", failing_upload)
    response = await test_app_asyncio.post(f"/media/{new_media_id}/upload", files=dict(file='bar'), headers=device_auth)
    assert response.status_code == 500
