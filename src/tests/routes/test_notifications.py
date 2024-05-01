import json

import pytest
import pytest_asyncio

from app import db
from app.api import crud, deps
from tests.db_utils import TestSessionLocal, fill_table
from tests.routes.test_alerts import (
    ACCESS_TABLE,
    ALERT_TABLE_FOR_DB,
    DEVICE_TABLE_FOR_DB,
    EVENT_TABLE_FOR_DB,
    GROUP_TABLE,
    MEDIA_TABLE_FOR_DB,
    USER_TABLE_FOR_DB,
)
from tests.routes.test_recipients import RECIPIENT_TABLE_FOR_DB
from tests.utils import update_only_datetime

NOTIFICATION_TABLE = [
    {
        "id": 1,
        "alert_id": 1,
        "recipient_id": 1,
        "subject": "New alert",
        "message": "Alert issued",
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "alert_id": 2,
        "recipient_id": 2,
        "subject": "New alert",
        "message": "Alert issued",
        "created_at": "2020-10-13T08:18:45.447773",
    },
]

PAYLOAD_TABLE = [{k: v for k, v in entry.items() if k not in ("id", "created_at")} for entry in NOTIFICATION_TABLE]

NOTIFICATION_TABLE_FOR_DB = list(map(update_only_datetime, NOTIFICATION_TABLE))


@pytest_asyncio.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(deps, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.media, MEDIA_TABLE_FOR_DB)
    await fill_table(test_db, db.events, EVENT_TABLE_FOR_DB)
    await fill_table(test_db, db.alerts, ALERT_TABLE_FOR_DB)
    await fill_table(test_db, db.recipients, RECIPIENT_TABLE_FOR_DB)
    await fill_table(test_db, db.recipients, RECIPIENT_TABLE_FOR_DB)
    await fill_table(test_db, db.notifications, NOTIFICATION_TABLE_FOR_DB)


@pytest.mark.parametrize(
    ("access_idx", "notification_id", "status_code", "status_details"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 403, "Your access scope is not compatible with this operation."),
        (1, 1, 200, None),
        (2, 1, 403, "Your access scope is not compatible with this operation."),
        (1, 999, 404, "Table notifications has no entry with id=999"),
        (1, 0, 422, None),
    ],
)
@pytest.mark.asyncio()
async def test_get_notification(
    test_app_asyncio, init_test_db, access_idx, notification_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/notifications/{notification_id}", headers=auth)
    response_json = response.json()
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response_json["detail"] == status_details
    if response.status_code == 200:
        assert response_json == NOTIFICATION_TABLE[notification_id - 1]


@pytest.mark.parametrize(
    ("access_idx", "status_code", "status_details", "expected_notifications"),
    [
        (None, 401, "Not authenticated", None),
        (0, 403, "Your access scope is not compatible with this operation.", None),
        (1, 200, None, NOTIFICATION_TABLE),
        (2, 403, "Your access scope is not compatible with this operation.", None),
    ],
)
@pytest.mark.asyncio()
async def test_fetch_notifications(
    test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_notifications
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/notifications/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_notifications


@pytest.mark.parametrize(
    ("access_idx", "payload", "status_code", "status_details"),
    [
        (None, {}, 401, "Not authenticated"),
        (
            0,
            PAYLOAD_TABLE[0],
            403,
            "Your access scope is not compatible with this operation.",
        ),
        (1, PAYLOAD_TABLE[0], 201, None),
        (
            2,
            PAYLOAD_TABLE[1],
            403,
            "Your access scope is not compatible with this operation.",
        ),
        (1, PAYLOAD_TABLE[1], 201, None),
    ],
)
@pytest.mark.asyncio()
async def test_send_notification(
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

    test_response = {"id": len(NOTIFICATION_TABLE) + 1, **payload}

    response = await test_app_asyncio.post("/notifications/", content=json.dumps(payload), headers=auth)

    assert response.status_code == status_code, response.text

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        test_response["created_at"] = response.json()["created_at"]
        assert response.json() == test_response


@pytest.mark.parametrize(
    ("access_idx", "notification_id", "status_code", "status_details"),
    [
        (None, 1, 401, "Not authenticated"),
        (1, 1, 200, None),
        (0, 1, 403, "Your access scope is not compatible with this operation."),
        (1, 999, 404, "Table notifications has no entry with id=999"),
        (1, 0, 422, None),
    ],
)
@pytest.mark.asyncio()
async def test_delete_notification(
    test_app_asyncio, init_test_db, access_idx, notification_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.delete(f"/notifications/{notification_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == NOTIFICATION_TABLE[notification_id - 1]
        remaining_notifications = await test_app_asyncio.get("/notifications/", headers=auth)
        assert all(entry["id"] != notification_id for entry in remaining_notifications.json())
