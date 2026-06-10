# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import timedelta
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.detections import (
    _run_temporal_validation,
    _sequence_frames,
    validate_sequence,
)
from app.core.time import utcnow
from app.crud import DetectionCRUD, SequenceCRUD
from app.models import AlertSequence, Detection, Sequence
from app.services.risk import risk_service
from app.services.temporal import temporal_service


async def _seed_sequence(
    session: AsyncSession,
    n_frames: int,
    *,
    max_conf: float = 0.9,
    camera_id: int = 1,
    pose_id: int = 1,
) -> Sequence:
    now = utcnow()
    seq = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=180.0,
        sequence_azimuth=175.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(minutes=30),
        last_seen_at=now,
        max_conf=max_conf,
    )
    session.add(seq)
    await session.commit()
    await session.refresh(seq)
    for i in range(n_frames):
        session.add(
            Detection(
                camera_id=camera_id,
                pose_id=pose_id,
                sequence_id=seq.id,
                bucket_key=f"frame-{i}.jpg",
                bbox="[(.1,.1,.7,.8,.9)]",
                created_at=now - timedelta(minutes=n_frames - i),
            )
        )
    await session.commit()
    return seq


# --- _sequence_frames -------------------------------------------------------


@pytest.mark.asyncio
async def test_sequence_frames_distinct_and_ordered(detection_session: AsyncSession):
    seq = await _seed_sequence(detection_session, 4)
    now = utcnow()
    # A second detection sharing an existing frame (same image, different bbox) must not duplicate it.
    detection_session.add(
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=seq.id,
            bucket_key="frame-1.jpg",
            bbox="[(.2,.2,.3,.3,.5)]",
            created_at=now,
        )
    )
    await detection_session.commit()

    frames = await _sequence_frames(DetectionCRUD(detection_session), cast(int, seq.id))
    assert frames == ["frame-0.jpg", "frame-1.jpg", "frame-2.jpg", "frame-3.jpg"]


# --- _run_temporal_validation: sliding window & frame bounds ----------------


@pytest.mark.asyncio
async def test_temporal_validation_sends_last_six_frames(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 10)
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is True
    sent_frames = predict.await_args.args[1]
    assert sent_frames == [f"frame-{i}.jpg" for i in range(4, 10)]  # window = frames[n-6:n]
    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.9)


@pytest.mark.asyncio
async def test_temporal_validation_sends_all_four_frames_at_minimum(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 4)
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    await _run_temporal_validation(seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session))

    assert predict.await_args.args[1] == [f"frame-{i}.jpg" for i in range(4)]


@pytest.mark.asyncio
async def test_temporal_validation_skips_below_min_frames(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 3)
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is False
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_validation_skips_above_max_frames(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 11)
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is False
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_validation_below_threshold_stores_score_and_fails(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=0.40))

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is False
    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.40)


@pytest.mark.asyncio
async def test_temporal_validation_fails_open_when_unavailable(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 2)
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)
    monkeypatch.setattr(temporal_service, "predict", predict)

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is True
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_validation_fails_open_on_predict_failure(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=None))  # call failed

    validated = await _run_temporal_validation(
        seq, 1, DetectionCRUD(detection_session), SequenceCRUD(detection_session)
    )

    assert validated is True


# --- validate_sequence: end-to-end gating ----------------------------------


async def _has_alert_link(session: AsyncSession, sequence_id: int) -> bool:
    res = await session.exec(select(AlertSequence).where(cast(Any, AlertSequence.sequence_id) == sequence_id))
    return res.first() is not None


@pytest.mark.asyncio
async def test_validate_sequence_risk_gate_blocks_low_conf(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(risk_service, "_scores", {1: "very_low"})  # 0.6 threshold > 0.30
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    predict.assert_not_awaited()  # blocked before temporal
    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False


@pytest.mark.asyncio
async def test_validate_sequence_marks_validated_and_triangulates(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    monkeypatch.setattr(risk_service, "_scores", {})  # no threshold -> gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # fail open

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_validate_sequence_idempotent_when_already_validated(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5)
    await SequenceCRUD(detection_session).set_validation(cast(int, seq.id), mark_validated=True)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    predict.assert_not_awaited()
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False
