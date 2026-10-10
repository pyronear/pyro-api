from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from sqlmodel import func, select

from app.core.time import utcnow
from app.crud import AlertCRUD, OrganizationCRUD, SequenceCRUD
from app.db import session_factory
from app.models import Alert, AlertSequence, Detection, Organization, Sequence
from app.schemas.organizations import OrganizationCreate, SlackHook


@pytest.mark.asyncio
async def test_deferred_create_is_flushed_but_not_visible_until_commit(async_session):
    crud = OrganizationCRUD(async_session)
    organization = await crud.create(OrganizationCreate(name="deferred-org"), commit=False)
    assert organization.id is not None
    assert await crud.get(organization.id) is organization
    async with session_factory() as observer:
        assert await observer.get(Organization, organization.id) is None
    await async_session.rollback()
    async with session_factory() as observer:
        assert await observer.get(Organization, organization.id) is None

    committed = await crud.create(OrganizationCreate(name="committed-org"))
    async with session_factory() as observer:
        assert await observer.get(Organization, committed.id) is not None


@pytest.mark.parametrize("operation", ["update", "delete"])
@pytest.mark.asyncio
async def test_deferred_mutations_roll_back(organization_session, operation):
    crud = OrganizationCRUD(organization_session)
    if operation == "update":
        await crud.update(1, SlackHook(slack_hook="https://hooks.slack.com/services/TEST/TEST/test"), commit=False)
    else:
        await crud.delete(1, commit=False)
    async with session_factory() as observer:
        original = await observer.get(Organization, 1)
        assert original is not None
        assert original.slack_hook == pytest.organization_table[0]["slack_hook"]
    await organization_session.rollback()
    async with session_factory() as observer:
        original = await observer.get(Organization, 1)
        assert original is not None
        assert original.slack_hook == pytest.organization_table[0]["slack_hook"]


@pytest.mark.asyncio
async def test_ingestion_rolls_back_rows_membership_confidence_and_queue_on_late_failure(
    async_client, detection_session, monkeypatch
):
    from app.api.api_v1.endpoints import detections as endpoint

    now = utcnow()
    sequence = Sequence(camera_id=1, pose_id=1, camera_azimuth=45, started_at=now, last_seen_at=now, max_conf=0.1)
    detection_session.add(sequence)
    await detection_session.flush()
    detection_session.add(
        Detection(camera_id=1, pose_id=1, sequence_id=sequence.id, bucket_key="before", bbox="[(0.1,0.1,0.2,0.2,0.1)]")
    )
    await detection_session.commit()
    original_count = (await detection_session.exec(select(func.count()).select_from(Detection))).one()
    sequence_id = sequence.id

    monkeypatch.setattr(endpoint, "upload_file", AsyncMock(return_value="new-frame"))
    monkeypatch.setattr(SequenceCRUD, "enqueue_validation", AsyncMock(side_effect=RuntimeError("late queue failure")))
    with pytest.raises(RuntimeError, match="late queue failure"):
        await async_client.post(
            "/detections",
            headers=pytest.get_token(1, ["camera"], 1),
            data={"pose_id": 1, "bboxes": "[(0.1,0.1,0.2,0.2,0.9),(0.7,0.7,0.8,0.8,0.8)]"},
            files={"file": ("frame.jpg", b"frame", "image/jpeg")},
        )
    async with session_factory() as observer:
        assert (await observer.exec(select(func.count()).select_from(Detection))).one() == original_count
        persisted = await observer.get(Sequence, sequence_id)
        assert persisted.last_seen_at == now
        assert persisted.max_conf == pytest.approx(0.1)
        assert persisted.validation_due_at is None


@pytest.mark.parametrize("operation", ["label", "unmatch", "delete-sequence", "delete-alert"])
@pytest.mark.asyncio
async def test_alert_workflows_roll_back_on_late_failure(async_client, detection_session, monkeypatch, operation):
    from app.api.api_v1.endpoints import sequences as endpoint

    now = utcnow()
    sequences = [
        Sequence(camera_id=1, pose_id=1, camera_azimuth=45, started_at=now - timedelta(seconds=i), last_seen_at=now)
        for i in range(2)
    ]
    alert = Alert(organization_id=1, started_at=now - timedelta(seconds=1), last_seen_at=now)
    detection_session.add_all([alert, *sequences])
    await detection_session.flush()
    detection_session.add_all([AlertSequence(alert_id=alert.id, sequence_id=seq.id) for seq in sequences])
    detection = Detection(camera_id=1, pose_id=1, sequence_id=sequences[0].id, bucket_key="before", bbox="[]")
    detection_session.add(detection)
    await detection_session.commit()
    alert_id, sequence_id, detection_id = alert.id, sequences[0].id, detection.id
    original_pairs = {(alert_id, seq.id) for seq in sequences}

    fail = AsyncMock(side_effect=RuntimeError("late workflow failure"))

    if operation in {"label", "unmatch"}:
        monkeypatch.setattr(AlertCRUD, "create", fail)
    elif operation == "delete-sequence":
        monkeypatch.setattr(endpoint, "refresh_alert_state", fail)
    else:
        monkeypatch.setattr(AlertCRUD, "delete", fail)
    auth = pytest.get_token(1, ["admin"], 1)
    if operation == "label":
        request = async_client.patch(
            f"/sequences/{sequence_id}/label", headers=auth, json={"is_wildfire": "other_smoke"}
        )
    elif operation == "unmatch":
        request = async_client.post(f"/alerts/{alert_id}/sequences/{sequence_id}/unmatch", headers=auth)
    elif operation == "delete-sequence":
        request = async_client.delete(f"/sequences/{sequence_id}", headers=auth)
    else:
        request = async_client.delete(f"/alerts/{alert_id}", headers=auth)
    with pytest.raises(RuntimeError, match="late workflow failure"):
        await request
    async with session_factory() as observer:
        assert await observer.get(Alert, alert_id) is not None
        persisted = await observer.get(Sequence, sequence_id)
        assert persisted is not None
        assert persisted.is_wildfire is None
        assert (await observer.get(Detection, detection_id)).sequence_id == sequence_id
        links = (await observer.exec(select(AlertSequence).where(AlertSequence.alert_id == alert_id))).all()
        assert {(link.alert_id, link.sequence_id) for link in links} == original_pairs
