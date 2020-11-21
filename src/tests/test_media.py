import json
import pytest
from copy import deepcopy
from datetime import datetime

from app.api import crud
from app.api.routes import media
from app.services import bucket_service

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(media, "media", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)


def test_get_media(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.get("/media/1")
    assert response.status_code == 200
    assert response.json() == mock_media_table[0]


@pytest.mark.parametrize(
    "media_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_media_invalid(test_app, monkeypatch, media_id, status_code, status_details):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.get(f"/media/{media_id}")
    assert response.status_code == status_code, media_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_media(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.get("/media/")
    assert response.status_code == 200
    assert response.json() == mock_media_table


def test_create_media(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    test_payload = {"device_id": 1}
    test_response = {"id": len(mock_media_table) + 1, **test_payload, "type": "image"}

    utc_dt = datetime.utcnow()
    response = test_app.post("/media/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_media_table[-1]['created_at'] > utc_dt and mock_media_table[-1]['created_at'] < datetime.utcnow()


def test_create_media_from_device(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    test_payload = {}

    test_response = {"id": len(mock_media_table) + 1, "device_id": 99, "type": "image"}  # Device_id is 99 because it is the id of the authentified sending device.

    utc_dt = datetime.utcnow()
    response = test_app.post("/media/created-by-device", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert mock_media_table[-1]['created_at'] > utc_dt and mock_media_table[-1]['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": "my_device"}, 422],
        [{}, 422],
    ],
)
def test_create_media_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.post("/media/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_media(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    test_payload = {"device_id": 1, "type": "video"}
    response = test_app.put("/media/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_media_table[0].items():
        assert v == test_payload.get(k, MEDIA_TABLE[0][k])


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
def test_update_media_invalid(test_app, monkeypatch, media_id, payload, status_code):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.put(f"/media/{media_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_media(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.delete("/media/1/")
    assert response.status_code == 200
    assert response.json() == MEDIA_TABLE[0]
    for entry in mock_media_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "media_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_media_invalid(test_app, monkeypatch, media_id, status_code, status_details):
    # Sterilize DB interactions
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    response = test_app.delete(f"/media/{media_id}/")
    assert response.status_code == status_code, print(media_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(media_id)


def test_upload_media(test_app, monkeypatch):
    mock_media_table = deepcopy(MEDIA_TABLE)
    _patch_session(monkeypatch, mock_media_table)

    ## 1 - Create a media that will have a custom
    payload_creation_device = {"device_id": 99} # 99 because it is the authentified device_id specified in the config
    newly_created_media_id = len(mock_media_table) + 1
    response = test_app.post("/media/", data=json.dumps(payload_creation_device))

    ## 2 - Upload something
    async def successful_upload(bucket_name, bucket_key, file_binary):
        return True
    monkeypatch.setattr(bucket_service, "upload_file", successful_upload)
    response = test_app.post(f"/media/{newly_created_media_id}/upload_file", files=dict(file='bar'))
    test_response = mock_media_table[-1]
    response_json = response.json()
    response_json.pop("created_at")
    assert response.status_code == 200
    assert {k: v for k, v in test_response.items() if k not in ('created_at', "bucket_key")} == response_json

    ## 2b - Upload failing
    async def failing_upload(bucket_name, bucket_key, file_binary):
        return False
    monkeypatch.setattr(bucket_service, "upload_file", failing_upload)
    response = test_app.post(f"/media/{newly_created_media_id}/upload_file", files=dict(file='bar'))
    response_json = response.json()
    response_json.pop("created_at")
    assert response.status_code == 500