from typing import Any, Dict, List, Union
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status # Import status

from app.models import Alert, AlertSequence, Organization, Sequence, Camera, Pose
from app.services.storage import s3_service


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"name": "pyro-organization"},
            401,
            "Not authenticated",
        ),
        (
            0,
            {"name": "pyro-organization"},
            201,
            None,
        ),
        (
            1,
            {"name": "pyro-organization2"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            {"name": "pyro-organization"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_organization(
    async_client: AsyncClient,
    user_idx: Union[int, None],
    payload: Dict[str, Any],
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.post("/organizations", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {k: v for k, v in response.json().items() if k not in {"id", "telegram_id", "slack_hook"}} == payload


@pytest.mark.parametrize(
    ("user_idx", "organization_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, 0),
        (1, 1, 403, "Incompatible token scope.", 0),
        (2, 1, 403, "Incompatible token scope.", 0),
    ],
)
@pytest.mark.asyncio
async def test_get_organization(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.get(f"/organizations/{organization_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.organization_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.organization_table),
        (1, 403, "Incompatible token scope.", None),
        (2, 403, "Incompatible token scope.", None),
    ],
)
@pytest.mark.asyncio
async def test_fetch_organizations(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    status_code: int,
    status_detail: Union[str, None],
    expected_response: Union[List[Dict[str, Any]], None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get("/organizations", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ("user_idx", "organization_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_organization(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.delete(f"/organizations/{organization_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.asyncio
async def test_delete_organization_with_alerts_and_sequences(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    # Create a separate dummy organization for the dummy camera
    dummy_cam_organization = Organization(id=98, name="dummy-cam-org", telegram_id=None, slack_hook=None)
    async_session.add(dummy_cam_organization)
    await async_session.commit()
    await async_session.refresh(dummy_cam_organization)

    # Create dummy camera and pose for the sequence and alert, linked to the dummy_cam_organization
    dummy_camera = Camera(
        id=998,
        organization_id=dummy_cam_organization.id,
        name="dummy-cam",
        angle_of_view=1.0,
        elevation=1.0,
        lat=1.0,
        lon=1.0,
        is_trustable=True,
        last_active_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    async_session.add(dummy_camera)
    await async_session.commit()
    await async_session.refresh(dummy_camera)

    dummy_pose = Pose(
        id=997,
        camera_id=dummy_camera.id,
        azimuth=1.0,
        patrol_id=1,
    )
    async_session.add(dummy_pose)
    await async_session.commit()
    await async_session.refresh(dummy_pose)

    # Create a dummy sequence as AlertSequence needs a sequence_id
    dummy_sequence = Sequence(
        id=999,
        camera_id=dummy_camera.id,
        pose_id=dummy_pose.id,
        camera_azimuth=1.0,
        is_wildfire="wildfire_smoke",
        sequence_azimuth=1.0,
        cone_angle=1.0,
        started_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
    )
    async_session.add(dummy_sequence)
    await async_session.commit()
    await async_session.refresh(dummy_sequence)

    # 1. Create the new organization to be deleted
    new_organization = Organization(id=99, name="temp-organization-with-alerts", telegram_id=None, slack_hook=None)
    async_session.add(new_organization)
    await async_session.commit()
    await async_session.refresh(new_organization)

    # Create S3 bucket for the new organization
    s3_service.create_bucket(s3_service.resolve_bucket_name(new_organization.id))

    # 2. Create an alert associated with the new organization
    new_alert = Alert(
        id=9999,
        organization_id=new_organization.id, # This alert is linked to the organization to be deleted
        event_at=datetime.utcnow(),
        score=0.9,
        latitude=10.0,
        longitude=20.0,
        camera_id=dummy_camera.id,  # Link to the dummy camera (not to be deleted)
        sensor_id=1,
        started_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
    )
    async_session.add(new_alert)
    await async_session.commit()
    await async_session.refresh(new_alert)

    # 3. Create an alert sequence associated with the new alert
    new_alert_sequence = AlertSequence(
        alert_id=new_alert.id,
        sequence_id=dummy_sequence.id, # Link to the dummy sequence (not to be deleted)
    )
    async_session.add(new_alert_sequence)
    await async_session.commit()
    await async_session.refresh(new_alert_sequence)

    # Get an admin token for the organization
    auth = pytest.get_token(pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), new_organization.id)

    # 4. Delete the organization
    response = await async_client.delete(f"/organizations/{new_organization.id}", headers=auth)
    assert response.status_code == 200, response.text
    assert response.json() is None

    # 5. Verify that the organization is deleted from the API's perspective
    get_response = await async_client.get(f"/organizations/{new_organization.id}", headers=auth)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND, get_response.text

    # Verify that the S3 bucket is also deleted
    with pytest.raises(ValueError, match="unable to access bucket"):
        s3_service.get_bucket(s3_service.resolve_bucket_name(new_organization.id))
    
    # Assert that the dummy camera, pose, sequence, and their organization are NOT deleted
    dummy_cam_org_in_db = await async_session.get(Organization, dummy_cam_organization.id)
    assert dummy_cam_org_in_db is not None

    dummy_camera_in_db = await async_session.get(Camera, dummy_camera.id)
    assert dummy_camera_in_db is not None

    dummy_pose_in_db = await async_session.get(Pose, dummy_pose.id)
    assert dummy_pose_in_db is not None

    dummy_sequence_in_db = await async_session.get(Sequence, dummy_sequence.id)
    assert dummy_sequence_in_db is not None



@pytest.mark.parametrize(
    ("user_idx", "organization_id", "payload", "status_code", "status_detail"),
    [
        (
            None,
            1,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            401,
            "Not authenticated",
        ),
        (0, 1, {"slack_hook": "test"}, 422, None),
        (
            0,
            1,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            404,
            "Unable to access Slack channel",
        ),
        (
            1,
            2,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            2,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_slack_hook(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    payload: str,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.patch(f"/organizations/slack-hook/{organization_id}", json=payload, headers=auth)
    print(response.text)
    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert str(response.json()["detail"]) == status_detail
