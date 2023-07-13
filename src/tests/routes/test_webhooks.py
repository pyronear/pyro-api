import json

import pytest
import pytest_asyncio

from app import db
from app.api import crud, deps
from tests.db_utils import TestSessionLocal, fill_table, get_entry
from tests.utils import update_only_datetime

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user", "group_id": 1},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin", "group_id": 1},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device", "group_id": 1},
]

WEBHOOK_TABLE = [
    {"id": 1, "callback": "create_site", "url": "https://github.com/pyronear/pyro-api"},
    {"id": 2, "callback": "create_alert", "url": "https://github.com/pyronear/pyro-api"},
]


WEBHOOK_TABLE_FOR_DB = list(map(update_only_datetime, WEBHOOK_TABLE))


@pytest_asyncio.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(deps, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.webhooks, WEBHOOK_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, webhook_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table webhooks has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_webhook(test_app_asyncio, init_test_db, access_idx, webhook_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/webhooks/{webhook_id}", headers=auth)
    response_json = response.json()
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response_json["detail"] == status_details
    if response.status_code == 200:
        assert response_json == WEBHOOK_TABLE[webhook_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_webhooks",
    [
        [None, 401, "Not authenticated", []],
        [0, 403, "Your access scope is not compatible with this operation.", None],
        [1, 200, None, WEBHOOK_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_webhooks(
    test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_webhooks
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/webhooks/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_webhooks


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [
            0,
            {"callback": "create_alert", "url": "https://www.pyronear.org"},
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"callback": "create_alert", "url": "https://www.pyronear.org"}, 201, None],
        [
            2,
            {"callback": "create_alert", "url": "https://www.pyronear.org"},
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"callback": "create_alert", "url": "hello"}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_wedbhook(
    test_app_asyncio,
    init_test_db,
    test_db,
    access_idx,
    payload,
    status_code,
    status_details,
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    test_response = {"id": len(WEBHOOK_TABLE) + 1, **payload}

    response = await test_app_asyncio.post("/webhooks/", content=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == test_response


@pytest.mark.parametrize(
    "access_idx, payload, webhook_id, status_code, status_details",
    [
        [None, {"callback": "create_alert", "url": "https://www.pyronear.org"}, 1, 401, "Not authenticated"],
        [
            0,
            {"callback": "create_alert", "url": "https://www.pyronear.org"},
            1,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"callback": "create_alert", "url": "https://www.pyronear.org"}, 1, 200, None],
        [
            2,
            {"callback": "create_alert", "url": "https://www.pyronear.org"},
            1,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"callback": "create_alert", "url": "hello"}, 0, 422, None],
        [
            1,
            {"callback": "create_alert", "url": "https://www.pyronear.org"},
            999,
            404,
            "Table webhooks has no entry with id=999",
        ],
    ],
)
@pytest.mark.asyncio
async def test_update_webhook(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, webhook_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.put(f"/webhooks/{webhook_id}/", content=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        updated_site_in_db = await get_entry(test_db, db.webhooks, webhook_id)
        updated_site_in_db = dict(**updated_site_in_db)
        for k, v in updated_site_in_db.items():
            assert v == payload.get(k, WEBHOOK_TABLE_FOR_DB[webhook_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, webhook_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [1, 1, 200, None],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table webhooks has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_webhook(test_app_asyncio, init_test_db, access_idx, webhook_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.delete(f"/webhooks/{webhook_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == WEBHOOK_TABLE[webhook_id - 1]
        remaining_webhooks = await test_app_asyncio.get("/webhooks/", headers=auth)
        assert all(entry["id"] != webhook_id for entry in remaining_webhooks.json())
