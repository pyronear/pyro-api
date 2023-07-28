import datetime
import json

import pytest
import pytest_asyncio

from app import db
from app.api import crud, deps
from tests.db_utils import TestSessionLocal, fill_table, get_entry
from tests.utils import update_only_datetime

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user", "group_id": 1},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin", "group_id": 1},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device", "group_id": 1},
]

RECIPIENT_TABLE = [
    {
        "id": 1,
        "group_id": 1,
        "notification_type": "email",
        "address": "my@mail.com",
        "subject_template": "New alert on $device",
        "message_template": "Group 1: alert $alert_id issued by $device on $date",
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "group_id": 2,
        "notification_type": "email",
        "address": "my@othermail.com",
        "subject_template": "New alert on $device",
        "message_template": "Group 2: alert $alert_id issued by $device on $date",
        "created_at": "2020-10-13T08:18:45.447773",
    },
]

PAYLOAD_TABLE = [{k: v for k, v in entry.items() if k not in ("id", "created_at")} for entry in RECIPIENT_TABLE]

RECIPIENT_TABLE_FOR_DB = list(map(update_only_datetime, RECIPIENT_TABLE))


@pytest_asyncio.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(deps, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.recipients, RECIPIENT_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, recipient_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table recipients has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_recipient(test_app_asyncio, init_test_db, access_idx, recipient_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/recipients/{recipient_id}", headers=auth)
    response_json = response.json()
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response_json["detail"] == status_details
    if response.status_code == 200:
        assert response_json == RECIPIENT_TABLE[recipient_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_recipients",
    [
        [None, 401, "Not authenticated", []],
        [0, 403, "Your access scope is not compatible with this operation.", None],
        [1, 200, None, RECIPIENT_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_recipients(
    test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_recipients
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/recipients/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_recipients


@pytest.mark.parametrize(
    "access_idx, group_id, status_code, status_details, expected_recipients",
    [
        [None, 1, 401, "Not authenticated", []],
        [0, 1, 403, "Your access scope is not compatible with this operation.", None],
        [1, 1, 200, None, RECIPIENT_TABLE[0:1]],
        [1, 2, 200, None, RECIPIENT_TABLE[1:2]],
        [1, 3, 200, None, []],
        [2, 1, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_recipients_for_group(
    test_app_asyncio, init_test_db, access_idx, group_id, status_code, status_details, expected_recipients
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/recipients/group-recipients/{group_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_recipients


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [
            0,
            PAYLOAD_TABLE[0],
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, PAYLOAD_TABLE[0], 201, None],
        [
            2,
            PAYLOAD_TABLE[1],
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, PAYLOAD_TABLE[1], 201, None],
    ],
)
@pytest.mark.asyncio
async def test_create_recipient(
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

    test_response = {"id": len(RECIPIENT_TABLE) + 1, **payload}

    response = await test_app_asyncio.post("/recipients/", content=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        test_response["created_at"] = response.json()["created_at"]
        assert response.json() == test_response


@pytest.mark.parametrize(
    "access_idx, payload, recipient_id, status_code, status_details",
    [
        [None, PAYLOAD_TABLE[0], 1, 401, "Not authenticated"],
        [
            0,
            PAYLOAD_TABLE[0],
            1,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, PAYLOAD_TABLE[1], 1, 200, None],
        [
            2,
            PAYLOAD_TABLE[0],
            1,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, PAYLOAD_TABLE[0], 0, 422, None],
        [
            1,
            PAYLOAD_TABLE[0],
            999,
            404,
            "Table recipients has no entry with id=999",
        ],
    ],
)
@pytest.mark.asyncio
async def test_update_recipient(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, recipient_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.put(f"/recipients/{recipient_id}/", content=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        updated_item = await get_entry(test_db, db.recipients, recipient_id)
        for k, v in dict(**updated_item).items():
            if isinstance(v, datetime.datetime):
                continue
            assert v == payload.get(k, RECIPIENT_TABLE[recipient_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, recipient_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [1, 1, 200, None],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table recipients has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_recipient(test_app_asyncio, init_test_db, access_idx, recipient_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.delete(f"/recipients/{recipient_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == RECIPIENT_TABLE[recipient_id - 1]
        remaining_recipients = await test_app_asyncio.get("/recipients/", headers=auth)
        assert all(entry["id"] != recipient_id for entry in remaining_recipients.json())
