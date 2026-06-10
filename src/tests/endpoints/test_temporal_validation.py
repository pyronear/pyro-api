# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
from datetime import timedelta
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.detections import (
    _sequence_frames,
    _temporal_verdict,
    validate_sequence,
)
from app.core.time import utcnow
from app.crud import DetectionCRUD, SequenceCRUD
from app.models import AlertSequence, Detection, Sequence
from app.services.risk import risk_service
from app.services.temporal import TemporalUnavailableError, temporal_service


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


# --- _temporal_verdict: frame bounds, fail-open (no DB session) --------------


@pytest.mark.asyncio
async def test_temporal_verdict_sends_all_frames(monkeypatch):
    frames = [f"frame-{i}.jpg" for i in range(10)]
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    validated, score = await _temporal_verdict(frames, 1)

    assert validated is True
    assert score == pytest.approx(0.9)
    assert predict.await_args.args[1] == frames  # all frames, no sliding window


@pytest.mark.asyncio
async def test_temporal_verdict_sends_all_four_frames_at_minimum(monkeypatch):
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    await _temporal_verdict([f"frame-{i}.jpg" for i in range(4)], 1)

    assert predict.await_args.args[1] == [f"frame-{i}.jpg" for i in range(4)]


@pytest.mark.asyncio
async def test_temporal_verdict_skips_below_min_frames(monkeypatch):
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _temporal_verdict(["a.jpg", "b.jpg", "c.jpg"], 1) == (False, None)
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_verdict_skips_above_max_frames(monkeypatch):
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _temporal_verdict([f"f{i}.jpg" for i in range(11)], 1) == (False, None)
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_verdict_above_max_is_hard_drop_even_when_unavailable(monkeypatch):
    """A sequence the model already declined (past MAX_FRAMES) must not resurrect via fail-open."""
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # breaker open / API down
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _temporal_verdict([f"f{i}.jpg" for i in range(11)], 1) == (False, None)
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_verdict_below_threshold_returns_score_unvalidated(monkeypatch):
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=0.40))

    validated, score = await _temporal_verdict([f"f{i}.jpg" for i in range(5)], 1)

    assert validated is False
    assert score == pytest.approx(0.40)


@pytest.mark.asyncio
async def test_temporal_verdict_fails_open_when_unavailable(monkeypatch):
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _temporal_verdict([f"f{i}.jpg" for i in range(5)], 1) == (True, None)
    predict.assert_not_awaited()


@pytest.mark.asyncio
async def test_temporal_verdict_fails_open_on_predict_failure(monkeypatch):
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(side_effect=TemporalUnavailableError("boom")))

    assert await _temporal_verdict([f"f{i}.jpg" for i in range(5)], 1) == (True, None)


@pytest.mark.asyncio
async def test_temporal_verdict_scoreless_response_does_not_validate(monkeypatch):
    """A successful but scoreless (probability=None) response must not fail open."""
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=None))

    assert await _temporal_verdict([f"f{i}.jpg" for i in range(5)], 1) == (False, None)


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
async def test_validate_sequence_scores_and_triangulates(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=0.9))

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.9)
    assert seq.is_validated is True
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_validate_sequence_persists_score_below_threshold_without_validating(
    detection_session: AsyncSession, monkeypatch
):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=0.40))  # below 0.45

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.40)  # latest score persisted
    assert seq.is_validated is False  # but not validated
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False


@pytest.mark.asyncio
async def test_validate_sequence_idempotent_when_already_validated(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5)
    await SequenceCRUD(detection_session).claim_validation(cast(int, seq.id))
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    predict = AsyncMock(return_value=0.9)
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    predict.assert_not_awaited()
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False


@pytest.mark.asyncio
async def test_validate_sequence_releases_claim_when_attach_fails(detection_session: AsyncSession, monkeypatch):
    """A failed alert attachment must release the claim so a later detection retries it."""
    from app.api.api_v1.endpoints import detections as detections_api

    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    det = (await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id)))[0]
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # fail open -> validated

    async def boom(*_args, **_kwargs):
        await asyncio.sleep(0)
        raise RuntimeError("attach failed")

    monkeypatch.setattr(detections_api, "_attach_sequence_to_alert", boom)
    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)  # error swallowed by wrapper

    await detection_session.refresh(seq)
    assert seq.is_validated is False  # claim released for retry
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False

    # A later run (attach healthy again) picks the sequence back up end-to-end.
    monkeypatch.undo()
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)
    await validate_sequence(cast(int, seq.id), cast(int, det.id), 1)

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_claim_validation_is_won_once(detection_session: AsyncSession):
    """Concurrent claims on the same sequence: exactly one wins the flip."""
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    first = await crud.claim_validation(cast(int, seq.id))
    second = await crud.claim_validation(cast(int, seq.id))
    assert first is True
    assert second is False
