import json
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app import db
from app.api import crud, deps
from app.api.endpoints.alerts import check_media_existence
from tests.db_utils import TestSessionLocal, fill_table, get_entry
from tests.utils import parse_time, ts_to_string, update_only_datetime

USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
    {"id": 3, "login": "fifth_login", "access_id": 5, "created_at": "2020-11-13T08:18:45.447773"},
]


DEVICE_TABLE = [
    {
        "id": 1,
        "login": "third_login",
        "owner_id": 1,
        "access_id": 3,
        "specs": "v0.1",
        "elevation": None,
        "lat": None,
        "angle_of_view": 68.0,
        "software_hash": None,
        "lon": None,
        "azimuth": 0.0,
        "pitch": None,
        "last_ping": None,
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "login": "fourth_login",
        "owner_id": 2,
        "access_id": 4,
        "specs": "v0.1",
        "elevation": None,
        "lat": None,
        "lon": None,
        "azimuth": None,
        "pitch": None,
        "last_ping": None,
        "angle_of_view": 68.0,
        "software_hash": None,
        "created_at": "2020-10-13T08:18:45.447773",
    },
]

GROUP_TABLE = [{"id": 1, "name": "first_group"}, {"id": 2, "name": "second_group"}]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},
]

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 1, "type": "image", "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 4, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


EVENT_TABLE = [
    {
        "id": 1,
        "lat": 0.0,
        "lon": 0.0,
        "type": "wildfire",
        "start_ts": "2020-10-13T08:18:45.447773",
        "end_ts": "2021-03-13T10:18:45.447773",
        "is_acknowledged": True,
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "lat": 6.0,
        "lon": 8.0,
        "type": "wildfire",
        "start_ts": "2020-10-13T08:18:45.447773",
        "end_ts": None,
        "is_acknowledged": True,
        "created_at": "2020-09-13T08:18:45.447773",
    },
    {
        "id": 3,
        "lat": -5.0,
        "lon": 3.0,
        "type": "wildfire",
        "start_ts": "2021-03-13T08:18:45.447773",
        "end_ts": None,
        "is_acknowledged": False,
        "created_at": "2020-09-13T08:18:45.447773",
    },
]

ALERT_TABLE = [
    {
        "id": 1,
        "device_id": 1,
        "event_id": 1,
        "media_id": 1,
        "lat": 0.0,
        "lon": 0.0,
        "azimuth": 0.0,
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "device_id": 1,
        "event_id": 1,
        "media_id": 2,
        "lat": 0.0,
        "lon": 0.0,
        "azimuth": 47.0,
        "created_at": "2020-10-13T09:18:45.447773",
    },
    {
        "id": 3,
        "device_id": 2,
        "event_id": 2,
        "media_id": 3,
        "lat": 10.0,
        "lon": 8.0,
        "azimuth": 123.0,
        "created_at": "2020-11-03T11:18:45.447773",
    },
    {
        "id": 4,
        "device_id": 1,
        "event_id": 3,
        "media_id": 4,
        "lat": 0.0,
        "lon": 0.0,
        "azimuth": 47.0,
        "created_at": ts_to_string(datetime.utcnow()),
    },
]

RECIPIENT_TABLE = [
    {
        "id": 1,
        "group_id": 1,
        "notification_type": "telegram",
        "address": "my_chat_id",
        "subject_template": "New alert on $device_name",
        "message_template": "Group 1: alert $alert_id issued by $device_name",
        "send_image": True,
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "group_id": 2,
        "notification_type": "telegram",
        "address": "my_other_chat_id",
        "subject_template": "New alert on $device_name",
        "message_template": "Group 2: alert $alert_id issued by $device_name",
        "send_image": False,
        "created_at": "2020-10-13T08:18:45.447773",
    },
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))
RECIPIENT_TABLE_FOR_DB = list(map(update_only_datetime, RECIPIENT_TABLE))


async def check_notifications(alert_id: int, device_id: int, media_id: int, is_new_event: bool):
    notifications = await crud.fetch_all(db.notifications, {"alert_id": alert_id})
    assert len(notifications) == is_new_event
    if not is_new_event:
        return
    for device in DEVICE_TABLE:
        if device["id"] == device_id:
            group_id = next(item["id"] for item in USER_TABLE if device["owner_id"] == item["id"])
            login = device["login"]
            break
    recipient = next(item for item in RECIPIENT_TABLE if item["group_id"] == group_id)
    recipient_id = recipient["id"]
    media_id = media_id if recipient["send_image"] else None
    expected_notification = {
        "alert_id": alert_id,
        "recipient_id": recipient_id,
        "subject": f"New alert on {login}",
        "message": f"Group {group_id}: alert {alert_id} issued by {login}",
        "media_id": media_id,
    }
    assert {k: v for k, v in notifications[0].items() if k not in ("id", "created_at")} == expected_notification


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


@pytest.mark.asyncio
async def test_check_media_existence_raise(init_test_db):
    with pytest.raises(HTTPException):
        await check_media_existence(-9999)


@pytest.mark.parametrize(
    "access_idx, alert_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 200, None],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table alerts has no entry with id=999"],
        [1, 0, 422, None],
        [4, 1, 403, "This access can't read resources from group_id=1"],
    ],
)
@pytest.mark.asyncio
async def test_get_alert(test_app_asyncio, init_test_db, access_idx, alert_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/alerts/{alert_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        response_json = response.json()
        response_json["created_at"] = parse_time(response_json["created_at"])
        assert response_json == ALERT_TABLE_FOR_DB[alert_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [0, 200, None, [ALERT_TABLE[0], ALERT_TABLE[1], ALERT_TABLE[3]]],
        [1, 200, None, ALERT_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_results):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/alerts/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_results


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 200, None],
        [1, 200, None],
        [2, 403, "Your access scope is not compatible with this operation."],
        [4, 200, None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_ongoing_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/alerts/ongoing", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        event_ids = [entry["id"] for entry in EVENT_TABLE if entry["end_ts"] is None]

        alerts_group_id = [entry["id"] for entry in ALERT_TABLE]

        # Retrieve group_id condition first
        if ACCESS_TABLE[access_idx]["scope"] != "admin":
            group_id = ACCESS_TABLE[access_idx]["group_id"]
            access_group_id = [access["id"] for access in ACCESS_TABLE if access["group_id"] == group_id]
            devices_group_id = [device["id"] for device in DEVICE_TABLE if device["access_id"] in access_group_id]
            alerts_group_id = [alert["id"] for alert in ALERT_TABLE if alert["device_id"] in devices_group_id]

        assert response.json() == [
            entry for entry in ALERT_TABLE if (entry["event_id"] in event_ids and entry["id"] in alerts_group_id)
        ]


@pytest.mark.parametrize(
    "access_idx, payload, expected_event_id, status_code, status_details",
    [
        [
            0,
            {"device_id": 2, "media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 47.5},
            None,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"device_id": 2, "media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 47.5}, None, 201, None],
        [1, {"device_id": 2, "media_id": 1, "lat": 10.0, "lon": 8.0, "azimuth": 47.5}, 4, 201, None],
        [1, {"device_id": 1, "media_id": 1, "lat": 10.0, "lon": 8.0, "azimuth": 47.5}, 3, 201, None],
        [
            2,
            {"device_id": 2, "media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 47.5},
            None,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0}, None, 422, None],
        [
            1,
            {"device_id": 2, "media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": "hello"},
            None,
            422,
            None,
        ],
        [1, {"device_id": 2, "media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": -5.0}, None, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, expected_event_id, status_code, status_details
):
    is_new_event: bool = expected_event_id is not None and expected_event_id > len(EVENT_TABLE)

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/", content=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(ALERT_TABLE) + 1, **payload}
        if isinstance(expected_event_id, int):
            test_response["event_id"] = expected_event_id
        assert {k: v for k, v in json_response.items() if k != "created_at"} == test_response

        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert utc_dt < new_alert["created_at"] < datetime.utcnow()

        await check_notifications(
            alert_id=new_alert["id"],
            device_id=payload["device_id"],
            media_id=new_alert["media_id"],
            is_new_event=is_new_event,
        )


@pytest.mark.parametrize(
    "access_idx, payload, expected_event_id, status_code, status_details",
    [
        [
            0,
            {"media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 0.0},
            None,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [
            1,
            {"media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 0.0},
            None,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [2, {"media_id": 1, "event_id": 2, "lat": 10.0, "lon": 8.0, "azimuth": 0.0}, None, 201, None],
        [2, {"media_id": 1, "lat": 10.0, "lon": 8.0, "azimuth": 0.0}, 3, 201, None],
        [2, {"media_id": 1, "lat": 10.0, "lon": 8.0}, 3, 201, None],
        [3, {"media_id": 1, "lat": 10.0, "lon": 8.0, "azimuth": 0.0}, 4, 201, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert_by_device(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, expected_event_id, status_code, status_details
):
    is_new_event: bool = expected_event_id is not None and expected_event_id > len(EVENT_TABLE)

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/from-device", content=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        device_id = None
        for entry in DEVICE_TABLE:
            if entry["access_id"] == ACCESS_TABLE[access_idx]["id"]:
                device_id = entry["id"]
                break
        # Device_id is 99 because it is the identified device
        test_response = {
            "id": len(ALERT_TABLE) + 1,
            "device_id": device_id,
            **payload,
            "azimuth": 0.0,
        }
        if isinstance(expected_event_id, int):
            test_response["event_id"] = expected_event_id
        assert {k: v for k, v in json_response.items() if k != "created_at"} == test_response
        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert utc_dt < new_alert["created_at"] < datetime.utcnow()

        await check_notifications(
            alert_id=new_alert["id"], device_id=device_id, media_id=new_alert["media_id"], is_new_event=is_new_event
        )


@pytest.mark.parametrize(
    "access_idx, alert_id, status_code, status_details",
    [
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table alerts has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_alert(test_app_asyncio, init_test_db, access_idx, alert_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.delete(f"/alerts/{alert_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == ALERT_TABLE[alert_id - 1]
        remaining_alerts = await test_app_asyncio.get("/alerts/", headers=auth)
        assert all(entry["id"] != alert_id for entry in remaining_alerts.json())
