import json
from datetime import datetime

import pytest
import pytest_asyncio

from app import db
from app.api import crud, deps
from tests.db_utils import TestSessionLocal, fill_table, get_entry
from tests.utils import parse_time, update_only_datetime

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
        "azimuth": None,
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
    {"id": 3, "group_id": 2, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},
]

SITE_TABLE = [
    {
        "id": 1,
        "name": "my_first_tower",
        "lat": 44.1,
        "lon": -0.7,
        "type": "tower",
        "country": "FR",
        "geocode": "40",
        "created_at": "2020-10-13T08:18:45.447773",
        "group_id": 1,
    },
    {
        "id": 2,
        "name": "my_first_station",
        "lat": 44.1,
        "lon": 3.9,
        "type": "station",
        "country": "FR",
        "geocode": "30",
        "created_at": "2020-09-13T08:18:45.447773",
        "group_id": 2,
    },
]

INSTALLATION_TABLE = [
    {
        "id": 1,
        "device_id": 1,
        "site_id": 1,
        "start_ts": "2019-10-13T08:18:45.447773",
        "end_ts": None,
        "is_trustworthy": True,
        "created_at": "2020-10-13T08:18:45.447773",
    },
    {
        "id": 2,
        "device_id": 2,
        "site_id": 2,
        "start_ts": "2019-10-13T08:18:45.447773",
        "end_ts": None,
        "is_trustworthy": False,
        "created_at": "2020-11-13T08:18:45.447773",
    },
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))
INSTALLATION_TABLE_FOR_DB = list(map(update_only_datetime, INSTALLATION_TABLE))


@pytest_asyncio.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(deps, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.sites, SITE_TABLE_FOR_DB)
    await fill_table(test_db, db.installations, INSTALLATION_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, installation_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 200, None],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table installations has no entry with id=999"],
        [1, 0, 422, None],
        [4, 1, 403, "This access can't read resources from group_id=1"],
    ],
)
@pytest.mark.asyncio
async def test_get_installation(
    test_app_asyncio, init_test_db, access_idx, installation_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/installations/{installation_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == INSTALLATION_TABLE[installation_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [None, 401, "Not authenticated", None],
        [0, 200, None, [INSTALLATION_TABLE[0]]],
        [1, 200, None, INSTALLATION_TABLE],
        [2, 403, "Your access scope is not compatible with this operation.", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_installations(
    test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_results
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/installations/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == expected_results


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [None, {}, 401, "Not authenticated"],
        [
            0,
            {"device_id": 1, "site_id": 1, "start_ts": "2020-10-13T08:18:45.447773"},
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"device_id": 1, "site_id": 1, "start_ts": "2020-10-13T08:18:45.447773"}, 201, None],
        [
            1,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-10-13T08:18:45.447773",
                "end_ts": "2020-10-13T08:18:45.447773",
            },
            201,
            None,
        ],
        [1, {"device_id": 1, "site_id": 1, "start_ts": "2020-10-13T08:18:45.447773Z"}, 201, None],
        [
            1,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-10-13T08:18:45.447773Z",
                "end_ts": "2020-10-13T08:18:45.447773Z",
            },
            201,
            None,
        ],
        [
            2,
            {"device_id": 1, "site_id": 1, "start_ts": "2020-10-13T08:18:45.447773"},
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [1, {"device_id": 1, "site_id": "my_site"}, 422, None],
        [1, {"device_id": 1}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_installation(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/installations/", content=json.dumps(payload), headers=auth)

    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(INSTALLATION_TABLE) + 1, **payload, "is_trustworthy": True}
        test_response["start_ts"] = test_response["start_ts"].replace("Z", "")
        test_response["end_ts"] = payload["end_ts"].replace("Z", "") if payload.get("end_ts") is not None else None
        assert {k: v for k, v in json_response.items() if k != "created_at"} == test_response

        new_installation = await get_entry(test_db, db.installations, json_response["id"])
        new_installation = dict(**new_installation)

        # Timestamp consistency
        assert new_installation["created_at"] > utc_dt and new_installation["created_at"] < datetime.utcnow()
        # Check default value of is_trustworthy
        assert new_installation["is_trustworthy"]


@pytest.mark.parametrize(
    "access_idx, payload, installation_id, status_code, status_details",
    [
        [None, {}, 1, 401, "Not authenticated"],
        [
            0,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            1,
            200,
            None,
        ],
        [
            1,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            1,
            200,
            None,
        ],
        [
            2,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            1,
            403,
            "Your access scope is not compatible with this operation.",
        ],
        [
            4,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            1,
            403,
            "This access can't update resources for group_id=1",
        ],
        [1, {}, 1, 422, None],
        [1, {"device_id": 1}, 1, 422, None],
        [
            1,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            999,
            404,
            "Table installations has no entry with id=999",
        ],
        [
            1,
            {
                "device_id": 1,
                "site_id": "my_site",
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            1,
            422,
            None,
        ],
        [
            1,
            {"device_id": 1, "site_id": 1, "is_trustworthy": 5.0, "end_ts": None},
            1,
            422,
            None,
        ],
        [
            1,
            {
                "device_id": 1,
                "site_id": 1,
                "start_ts": "2020-07-13T08:18:45.447773",
                "end_ts": None,
                "is_trustworthy": True,
            },
            0,
            422,
            None,
        ],
    ],
)
@pytest.mark.asyncio
async def test_update_installation(
    test_app_asyncio, init_test_db, test_db, access_idx, payload, installation_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.put(
        f"/installations/{installation_id}/", content=json.dumps(payload), headers=auth
    )
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        updated_installation = await get_entry(test_db, db.installations, installation_id)
        updated_installation = dict(**updated_installation)
        for k, v in updated_installation.items():
            if k == "start_ts":
                assert v == parse_time(payload[k])
            else:
                assert v == payload.get(k, INSTALLATION_TABLE_FOR_DB[installation_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, installation_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [2, 1, 403, "Your access scope is not compatible with this operation."],
        [1, 999, 404, "Table installations has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_installation(
    test_app_asyncio, init_test_db, access_idx, installation_id, status_code, status_details
):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.delete(f"/installations/{installation_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == INSTALLATION_TABLE[installation_id - 1]
        remaining_installations = await test_app_asyncio.get("/installations/", headers=auth)
        assert all(entry["id"] != installation_id for entry in remaining_installations.json())


@pytest.mark.parametrize(
    "access_idx, installation_id, device_ids, status_code, status_details",
    [
        [None, 1, [], 401, "Not authenticated"],
        [0, 1, [1], 200, None],
        [1, 1, [1], 200, None],
        [4, 2, [2], 200, None],
        [1, 999, [], 200, None],  # TODO: this should fail since the site doesn't exist
        [1, 0, [], 422, None],
        [2, 1, [], 403, "Your access scope is not compatible with this operation."],
    ],
)
@pytest.mark.asyncio
async def test_get_active_devices_on_site(
    test_app_asyncio,
    init_test_db,
    test_db,
    monkeypatch,
    access_idx,
    installation_id,
    device_ids,
    status_code,
    status_details,
):
    # Custom patching for DB operations done on route
    monkeypatch.setattr(db.session, "database", test_db)

    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/installations/site-devices/{installation_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == [DEVICE_TABLE[_id - 1]["id"] for _id in device_ids]
