import json
import pytest

from app import db
from app.api import crud
from tests.conf_test_db import populate_db

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "me"},
]


@pytest.mark.asyncio
async def test_get_access(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get("/accesses/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in ACCESS_TABLE[0].items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_access_invalid(test_app_asyncio, test_db, monkeypatch, access_id, status_code, status_details):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get(f"/accesses/{access_id}")
    assert response.status_code == status_code, access_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_accesses(test_app_asyncio, test_db, monkeypatch):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get("/accesses/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"}
                               for entry in ACCESS_TABLE]


@pytest.mark.asyncio
async def test_create_access(test_app_asyncio, test_db, monkeypatch):

    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    test_payload = {"login": "third_login", "scopes": "me", "password": "PickARobustOne"}
    test_response = {"id": len(ACCESS_TABLE) + 1, **test_payload}

    response = await test_app_asyncio.post("/accesses/", data=json.dumps(test_payload))

    assert response.status_code == 201
    assert response.json() == {k: v for k, v in test_response.items() if k != "password"}


@pytest.mark.parametrize(
    "payload, status_code, status_details",
    [
        [{"login": "first_login", "password": "PickARobustOne", "scopes": "me"}, 400,
         "An entry with login='first_login' already exists."],
        [{"login": "third_login", "scopes": "me", "hashed_password": "PickARobustOne"}, 422, None],
        [{"login": 1, "scopes": "me", "password": "PickARobustOne"}, 422, None],
        [{"login": "third_login", "scopes": "me"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_access_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code, status_details):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.post("/accesses/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)


@pytest.mark.asyncio
async def test_update_access(test_app_asyncio, test_db, monkeypatch):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    test_payload = {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}
    response = await test_app_asyncio.put("/accesses/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in ACCESS_TABLE[0].items():
        assert v == test_payload.get(k, ACCESS_TABLE[0][k])


@pytest.mark.parametrize(
    "access_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"login": "first_login"}, 422],
        [999, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 404],
        [1, {"login": 1, "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
        [0, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_access_invalid(test_app_asyncio, test_db, monkeypatch, access_id, payload, status_code):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.put(f"/accesses/{access_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_access(test_app_asyncio, test_db, monkeypatch):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.delete("/accesses/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in ACCESS_TABLE[0].items() if k != "hashed_password"}

    remaining_accesses = await test_app_asyncio.get("/accesses/")
    for entry in remaining_accesses.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_access_invalid(test_app_asyncio, test_db, monkeypatch, access_id, status_code, status_details):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.delete(f"/accesses/{access_id}/")
    assert response.status_code == status_code, print(access_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(access_id)
