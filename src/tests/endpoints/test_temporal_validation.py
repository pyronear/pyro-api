# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
from datetime import timedelta
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.time import utcnow
from app.crud import DetectionCRUD, SequenceCRUD
from app.db import session_factory
from app.models import AlertSequence, Detection, Sequence
from app.services import validation as validation_service
from app.services.risk import risk_service
from app.services.temporal import TemporalPrediction, temporal_service
from app.services.validation import (
    FAIL_OPEN_STALE,
    FAIL_OPEN_UNAVAILABLE,
    VALIDATED_BY_MODEL,
    WINDOW_EXHAUSTED,
    _notify_for_sequence,
    _process_claimed_sequence,
    _sequence_frames_and_roi,
    process_next_due_validation,
    validation_worker_loop,
)


def _prediction(probability) -> TemporalPrediction:
    """A /predict result as the worker sees it, with stable version provenance."""
    return TemporalPrediction(probability, model_version="0.1.0", api_version="1.4.0")


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


async def _enqueue(session: AsyncSession, sequence_id: int) -> None:
    await SequenceCRUD(session).enqueue_validation(sequence_id)


async def _backdate_due(seconds: float = 60.0) -> None:
    """Shift every pending due time into the past so the next claim can't miss it.

    The claim only picks rows with ``validation_due_at <= utcnow()``, and ``utcnow`` is
    the wall clock: a clock step on the CI runner between enqueue and claim can leave a
    just-queued row a few ms in the future and hide it from the claim. The shift is
    relative, so FIFO order and staleness verdicts are preserved.
    """
    due_col = cast(Any, Sequence.validation_due_at)
    async with session_factory() as session:
        stmt: Any = (
            update(Sequence).where(due_col.is_not(None)).values(validation_due_at=due_col - timedelta(seconds=seconds))
        )
        await session.exec(stmt)
        await session.commit()


async def _process_one_due() -> bool:
    """``process_next_due_validation`` with the claim made immune to runner clock steps."""
    await _backdate_due()
    return await process_next_due_validation()


async def _has_alert_link(session: AsyncSession, sequence_id: int) -> bool:
    res = await session.exec(select(AlertSequence).where(cast(Any, AlertSequence.sequence_id) == sequence_id))
    return res.first() is not None


# --- _sequence_frames_and_roi ------------------------------------------------


@pytest.mark.asyncio
async def test_sequence_frames_distinct_ordered_with_union_roi(detection_session: AsyncSession):
    seq = await _seed_sequence(detection_session, 4)  # seeded bboxes are (.1,.1,.7,.8,.9)
    now = utcnow()
    # A second detection sharing an existing frame (same image, different bbox) must not duplicate it.
    detection_session.add(
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=seq.id,
            bucket_key="frame-1.jpg",
            bbox="[(.2,.2,.9,.3,.5)]",  # widens the union on x_max
            created_at=now,
        )
    )
    await detection_session.commit()

    total, frames, roi = await _sequence_frames_and_roi(DetectionCRUD(detection_session), cast(int, seq.id))
    assert total == 4
    assert frames == ["frame-0.jpg", "frame-1.jpg", "frame-2.jpg", "frame-3.jpg"]
    assert roi == [pytest.approx(0.1), pytest.approx(0.1), pytest.approx(0.9), pytest.approx(0.8)]


@pytest.mark.asyncio
async def test_sequence_frames_truncates_to_last_n_and_scopes_roi(detection_session: AsyncSession):
    """Truncation keeps the most recent frames and the ROI only covers kept frames."""
    seq = await _seed_sequence(detection_session, 12)
    # Widen the ROI on the OLDEST frame only: it must be excluded once truncated away.
    dets = await DetectionCRUD(detection_session).fetch_all(filters=("sequence_id", seq.id), order_by="created_at")
    dets[0].bbox = "[(.0,.0,.99,.99,.9)]"
    detection_session.add(dets[0])
    await detection_session.commit()

    total, frames, roi = await _sequence_frames_and_roi(DetectionCRUD(detection_session), cast(int, seq.id), last_n=10)
    assert total == 12
    assert frames == [f"frame-{i}.jpg" for i in range(2, 12)]  # the last 10
    assert roi == [pytest.approx(0.1), pytest.approx(0.1), pytest.approx(0.7), pytest.approx(0.8)]


# --- enqueue / claim / finish: the DB-backed queue ---------------------------


@pytest.mark.asyncio
async def test_enqueue_is_idempotent_and_fifo_preserving(detection_session: AsyncSession):
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    await crud.enqueue_validation(cast(int, seq.id))
    await detection_session.refresh(seq)
    first_due = seq.validation_due_at
    assert first_due is not None

    await asyncio.sleep(0.01)
    await crud.enqueue_validation(cast(int, seq.id))  # second detection while queued
    await detection_session.refresh(seq)
    assert seq.validation_due_at == first_due  # one entry per sequence, oldest due kept


@pytest.mark.asyncio
async def test_enqueue_skips_validated_and_window_exhausted(detection_session: AsyncSession):
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    await crud.claim_validation(cast(int, seq.id))
    await crud.enqueue_validation(cast(int, seq.id))
    await detection_session.refresh(seq)
    assert seq.validation_due_at is None  # validated: nothing to do

    seq2 = await _seed_sequence(detection_session, 5)
    await crud.finish_validation_job(cast(int, seq2.id), validation_status=WINDOW_EXHAUSTED)
    await crud.enqueue_validation(cast(int, seq2.id))
    await detection_session.refresh(seq2)
    assert seq2.validation_due_at is None  # terminal: never resurrected


@pytest.mark.asyncio
async def test_claim_leases_and_blocks_concurrent_workers(detection_session: AsyncSession):
    """Cross-worker dedup: a claimed job is invisible to other workers until the lease expires."""
    seq = await _seed_sequence(detection_session, 5)
    await _enqueue(detection_session, cast(int, seq.id))
    await _backdate_due()

    async with session_factory() as worker_a, session_factory() as worker_b:
        claimed = await SequenceCRUD(worker_a).claim_due_validation(lease_seconds=60)
        assert claimed is not None
        assert claimed.id == seq.id
        assert claimed.validation_lease_until is not None
        assert await SequenceCRUD(worker_b).claim_due_validation(lease_seconds=60) is None  # leased

    # An expired lease (worker died mid-job) makes the job claimable again: nothing is lost.
    # 60s in the past, not 1s: a runner clock step must not make the lease look alive again.
    stale_lease = utcnow() - timedelta(seconds=60)
    crud = SequenceCRUD(detection_session)
    seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
    seq_db.validation_lease_until = stale_lease
    detection_session.add(seq_db)
    await detection_session.commit()
    async with session_factory() as worker_c:
        reclaimed = await SequenceCRUD(worker_c).claim_due_validation(lease_seconds=60)
        assert reclaimed is not None
        assert reclaimed.id == seq.id


@pytest.mark.asyncio
async def test_finish_job_keeps_due_when_frames_changed_during_scoring(detection_session: AsyncSession):
    """Frames arriving while the model scores must trigger a re-run, not be lost."""
    seq = await _seed_sequence(detection_session, 5)
    await _enqueue(detection_session, cast(int, seq.id))
    crud = SequenceCRUD(detection_session)

    await crud.finish_validation_job(cast(int, seq.id), frame_count=4)  # scored 4, now 5: stale verdict
    await detection_session.refresh(seq)
    assert seq.validation_due_at is not None  # job kept due for a fresh run
    assert seq.validation_lease_until is None  # but the lease is released

    await crud.finish_validation_job(cast(int, seq.id), frame_count=5)  # frame set unchanged
    await detection_session.refresh(seq)
    assert seq.validation_due_at is None


# --- process_next_due_validation: end-to-end gating --------------------------


@pytest.mark.asyncio
async def test_process_returns_false_when_nothing_due(detection_session: AsyncSession):
    assert await _process_one_due() is False


@pytest.mark.asyncio
async def test_process_risk_gate_blocks_low_conf(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {1: "very_low"})  # 0.6 threshold > 0.30
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_not_awaited()  # blocked before temporal
    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_due_at is None  # job completed; the next detection re-enqueues
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False


@pytest.mark.asyncio
async def test_process_validates_and_triangulates_on_fail_open(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})  # no threshold -> gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # fail open

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_status == FAIL_OPEN_UNAVAILABLE
    assert seq.validation_due_at is None
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_scores_with_fresh_frames_and_roi(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    assert predict.await_args.args[1] == [f"frame-{i}.jpg" for i in range(5)]  # frames read at call time
    # The bbox-union ROI is forwarded so the verdict is scoped to the sequence's region.
    assert predict.await_args.kwargs["roi_xyxyn"] == [
        pytest.approx(0.1),
        pytest.approx(0.1),
        pytest.approx(0.7),
        pytest.approx(0.8),
    ]
    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.9)
    # Version provenance is stored with the score, for per-release offline evaluation.
    assert seq.temporal_model_version == "0.1.0"
    assert seq.temporal_api_version == "1.4.0"
    assert seq.is_validated is True
    assert seq.validation_status == VALIDATED_BY_MODEL
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_persists_score_below_threshold_without_validating(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(0.40)))  # below 0.45

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.40)  # latest score persisted
    assert seq.is_validated is False  # but not validated
    assert seq.validation_status is None
    assert seq.validation_due_at is None  # retried when the next detection re-enqueues
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False


@pytest.mark.asyncio
async def test_process_skips_below_min_frames(detection_session: AsyncSession, monkeypatch):
    seq = await _seed_sequence(detection_session, 3, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_not_awaited()
    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_due_at is None


@pytest.mark.asyncio
async def test_process_truncates_never_scored_sequence_past_max_frames(detection_session: AsyncSession, monkeypatch):
    """Backlog must delay sequences, never silently drop them: first scoring uses the last 10."""
    seq = await _seed_sequence(detection_session, 12, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    assert predict.await_args.args[1] == [f"frame-{i}.jpg" for i in range(2, 12)]  # last 10
    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_status == VALIDATED_BY_MODEL


@pytest.mark.asyncio
async def test_process_window_exhausted_when_scored_and_past_max_frames(detection_session: AsyncSession, monkeypatch):
    """A sequence the model already scored (and declined) is terminal past the window."""
    seq = await _seed_sequence(detection_session, 11, max_conf=0.30)
    crud = SequenceCRUD(detection_session)
    await crud.set_temporal_score(cast(int, seq.id), 0.20)  # model had its chances
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_not_awaited()  # don't call the model again
    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_status == WINDOW_EXHAUSTED
    assert seq.temporal_model_score == pytest.approx(0.20)  # the real score is not overwritten
    assert seq.validation_due_at is None

    # Terminal: a later fail-open or enqueue can't resurrect it.
    await crud.enqueue_validation(cast(int, seq.id))
    await detection_session.refresh(seq)
    assert seq.validation_due_at is None


@pytest.mark.asyncio
async def test_process_stale_job_fails_open_explicitly(detection_session: AsyncSession, monkeypatch):
    """A job queued past TEMPORAL_VALIDATION_MAX_AGE fails open, traced as such."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    crud = SequenceCRUD(detection_session)
    seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
    seq_db.validation_due_at = utcnow() - timedelta(seconds=600)  # queued for 10 min
    detection_session.add(seq_db)
    await detection_session.commit()
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_not_awaited()  # too late to be useful: don't burn model time
    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_status == FAIL_OPEN_STALE
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_scoreless_response_does_not_validate(detection_session: AsyncSession, monkeypatch):
    """A successful but scoreless (probability=None) response must not fail open."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(None)))

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.temporal_model_score is None
    assert seq.validation_due_at is None


@pytest.mark.asyncio
async def test_process_resumes_post_claim_crash(detection_session: AsyncSession, monkeypatch):
    """A worker dying after winning the claim leaves a validated-but-due row: it must be
    resumed (triangulated + completed), not skipped forever."""
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    await _enqueue(detection_session, cast(int, seq.id))
    await crud.claim_validation(cast(int, seq.id))  # crash right after the claim: due survives
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True  # resumed, not skipped

    predict.assert_not_awaited()  # resume goes straight to post-claim work
    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_due_at is None  # job completed this time
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_nothing_due_for_completed_validated_sequence(detection_session: AsyncSession):
    """A validated sequence whose job completed (due cleared) is not picked up again."""
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    await _enqueue(detection_session, cast(int, seq.id))
    await crud.claim_validation(cast(int, seq.id))
    await crud.finish_validation_job(cast(int, seq.id))

    assert await _process_one_due() is False


@pytest.mark.asyncio
async def test_process_validates_from_prior_high_score_past_window(detection_session: AsyncSession, monkeypatch):
    """A stored above-threshold score must validate past MAX_FRAMES, never decay into
    window_exhausted (regression: scored 0.9 -> attach failed -> retry past the window)."""
    seq = await _seed_sequence(detection_session, 12, max_conf=0.30)
    crud = SequenceCRUD(detection_session)
    await crud.set_temporal_score(cast(int, seq.id), 0.90)  # scored high, never completed
    await _enqueue(detection_session, cast(int, seq.id))
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_not_awaited()  # validated from the stored score, no extra model call
    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_status == VALIDATED_BY_MODEL
    assert seq.temporal_model_score == pytest.approx(0.90)
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_attach_failure_past_window_does_not_window_exhaust(detection_session: AsyncSession, monkeypatch):
    """End-to-end regression: high score persisted, attach fails, retry past MAX_FRAMES
    must validate from the stored score instead of dropping the sequence."""
    from app.api.api_v1.endpoints import detections as detections_api

    seq = await _seed_sequence(detection_session, 12, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(0.90)))

    async def boom(*_args, **_kwargs):
        await asyncio.sleep(0)
        raise RuntimeError("attach failed")

    monkeypatch.setattr(detections_api, "_attach_sequence_to_alert", boom)
    assert await _process_one_due() is True  # scores 0.90, then attach fails

    await detection_session.refresh(seq)
    assert seq.temporal_model_score == pytest.approx(0.90)
    assert seq.is_validated is True  # verdict kept: the retry resumes attach, not the decision

    monkeypatch.undo()
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    predict_retry = AsyncMock(return_value=_prediction(0.90))
    monkeypatch.setattr(temporal_service, "predict", predict_retry)
    seq_db = cast(Sequence, await SequenceCRUD(detection_session).get(cast(int, seq.id), strict=True))
    seq_db.validation_due_at = utcnow()  # fast-forward past the retry backoff
    detection_session.add(seq_db)
    await detection_session.commit()

    assert await _process_one_due() is True

    predict_retry.assert_not_awaited()
    await detection_session.refresh(seq)
    assert seq.is_validated is True  # not window_exhausted
    assert seq.validation_status == VALIDATED_BY_MODEL
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_risk_gates_on_current_max_conf(detection_session: AsyncSession, monkeypatch):
    """The worker risk-gates on the CURRENT max_conf: a bump while the job was queued counts
    (the pipeline takes only the sequence id and reads all state fresh from the DB)."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)  # below the 0.6 gate
    await _enqueue(detection_session, cast(int, seq.id))
    seq_db = cast(Sequence, await SequenceCRUD(detection_session).get(cast(int, seq.id), strict=True))
    seq_db.max_conf = 0.90  # bumped by a detection while the job sat in the queue
    detection_session.add(seq_db)
    await detection_session.commit()
    predict = AsyncMock(return_value=_prediction(0.9))
    monkeypatch.setattr(risk_service, "_scores", {1: "very_low"})  # 0.6 threshold
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", predict)

    assert await _process_one_due() is True

    predict.assert_awaited()  # gate evaluated on the fresh 0.90, not the enqueue-time 0.30


@pytest.mark.asyncio
async def test_process_survives_job_error_and_keeps_job_due(detection_session: AsyncSession, monkeypatch):
    """An unexpected error releases the lease but keeps the job due: retried, never lost."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(side_effect=RuntimeError("boom")))

    assert await _process_one_due() is True  # error swallowed, loop survives

    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_due_at is not None  # still due
    assert seq.validation_lease_until is None  # lease released for retry
    assert seq.validation_attempts == 1  # consecutive-error counter ticking


@pytest.mark.asyncio
async def test_poison_job_dead_letters_after_max_attempts(detection_session: AsyncSession, monkeypatch):
    """A persistently failing job dead-letters as 'failed' instead of retrying forever."""
    from app.services.validation import MAX_VALIDATION_ATTEMPTS

    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(side_effect=RuntimeError("poison")))
    crud = SequenceCRUD(detection_session)

    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        if attempt:  # fast-forward past the retry backoff
            seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
            seq_db.validation_due_at = utcnow()
            detection_session.add(seq_db)
            await detection_session.commit()
        assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.validation_attempts == MAX_VALIDATION_ATTEMPTS
    assert seq.validation_status == validation_service.VALIDATION_FAILED
    assert seq.validation_due_at is None  # dead-lettered: no more retries
    assert seq.is_validated is False

    # Terminal: new detections can't resurrect it, the worker sees nothing due.
    await crud.enqueue_validation(cast(int, seq.id))
    await detection_session.refresh(seq)
    assert seq.validation_due_at is None
    assert await _process_one_due() is False


@pytest.mark.asyncio
async def test_attempts_reset_on_completed_job(detection_session: AsyncSession, monkeypatch):
    """The dead-letter cap counts CONSECUTIVE failures: a completed job resets the counter."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(side_effect=RuntimeError("blip")))

    assert await _process_one_due() is True  # one transient error
    await detection_session.refresh(seq)
    assert seq.validation_attempts == 1

    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(0.9)))  # recovered
    crud = SequenceCRUD(detection_session)
    seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
    seq_db.validation_due_at = utcnow()  # fast-forward past the retry backoff
    detection_session.add(seq_db)
    await detection_session.commit()

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_attempts == 0  # reset on completion


@pytest.mark.asyncio
async def test_attach_failure_keeps_verdict_and_resumes(detection_session: AsyncSession, monkeypatch):
    """A failed alert attachment keeps the verdict (and its status label, written atomically
    at the claim); the retry resumes the post-claim work instead of re-deciding."""
    from app.api.api_v1.endpoints import detections as detections_api

    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})  # gate open
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # fail open -> validated

    async def boom(*_args, **_kwargs):
        await asyncio.sleep(0)
        raise RuntimeError("attach failed")

    monkeypatch.setattr(detections_api, "_attach_sequence_to_alert", boom)
    assert await _process_one_due() is True  # error swallowed by the worker

    await detection_session.refresh(seq)
    assert seq.is_validated is True  # verdict durable from the claim
    assert seq.validation_status == FAIL_OPEN_UNAVAILABLE  # status written with the verdict
    assert seq.validation_due_at is not None  # job still due: the worker retries it
    assert seq.validation_due_at > utcnow()  # ... after a backoff, not in a tight loop
    assert seq.validation_lease_until is None  # lease released
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False

    # A later run (attach healthy again) resumes the post-claim work end-to-end.
    monkeypatch.undo()
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)
    seq_db = cast(Sequence, await SequenceCRUD(detection_session).get(cast(int, seq.id), strict=True))
    seq_db.validation_due_at = utcnow()  # fast-forward past the retry backoff
    detection_session.add(seq_db)
    await detection_session.commit()
    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_due_at is None  # job completed
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_stale_below_min_frames_stays_unvalidated(detection_session: AsyncSession, monkeypatch):
    """Deliberate: stale fail-open does NOT apply below MIN_FRAMES — a short sequence isn't
    waiting on the model; if its job went stale, the sequence stopped emitting (noise)."""
    seq = await _seed_sequence(detection_session, 3, max_conf=0.30)
    crud = SequenceCRUD(detection_session)
    seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
    seq_db.validation_due_at = utcnow() - timedelta(seconds=600)  # queued for 10 min
    detection_session.add(seq_db)
    await detection_session.commit()
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(0.9)))

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is False  # no stale fail-open below MIN_FRAMES
    assert seq.validation_status is None
    assert seq.validation_due_at is None  # job completed; a new frame re-enqueues


@pytest.mark.asyncio
async def test_claim_validation_is_won_once(detection_session: AsyncSession):
    """Concurrent claims on the same sequence: exactly one wins the flip."""
    seq = await _seed_sequence(detection_session, 5)
    crud = SequenceCRUD(detection_session)
    first = await crud.claim_validation(cast(int, seq.id))
    second = await crud.claim_validation(cast(int, seq.id))
    assert first is True
    assert second is False


# --- edge cases and failure paths --------------------------------------------


@pytest.mark.asyncio
async def test_sequence_frames_skips_unparseable_bboxes(detection_session: AsyncSession, monkeypatch):
    """Unparseable bboxes are skipped (full-frame ROI), never abort the job."""
    from fastapi import HTTPException

    from app.api.api_v1.endpoints import detections as detections_api

    seq = await _seed_sequence(detection_session, 4)

    def bad_parse(_bbox_str):
        raise HTTPException(status_code=422, detail="bad bbox")

    monkeypatch.setattr(detections_api, "_parse_bbox", bad_parse)
    total, frames, roi = await _sequence_frames_and_roi(DetectionCRUD(detection_session), cast(int, seq.id))
    assert total == 4
    assert frames == [f"frame-{i}.jpg" for i in range(4)]
    assert roi is None  # no parseable corner -> full-frame behavior


@pytest.mark.asyncio
async def test_sequence_frames_degenerate_roi_is_dropped(detection_session: AsyncSession):
    """A zero-area bbox union (xmin == xmax) yields no ROI (full-frame behavior)."""
    seq = await _seed_sequence(detection_session, 0)
    now = utcnow()
    for i in range(2):
        detection_session.add(
            Detection(
                camera_id=1,
                pose_id=1,
                sequence_id=seq.id,
                bucket_key=f"flat-{i}.jpg",
                bbox="[(.5,.1,.5,.8,.9)]",  # zero width
                created_at=now,
            )
        )
    await detection_session.commit()

    total, _frames, roi = await _sequence_frames_and_roi(DetectionCRUD(detection_session), cast(int, seq.id))
    assert total == 2
    assert roi is None


async def _drain_notifications() -> None:
    """Await the detached notification tasks fired by completed validations."""
    pending = list(validation_service._pending_notifications)
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)


@pytest.mark.asyncio
async def test_notify_without_detections_is_a_noop(detection_session: AsyncSession, monkeypatch):
    """A sequence with no detections (deleted meanwhile) notifies nothing and doesn't crash."""
    seq = await _seed_sequence(detection_session, 0)
    slack_notify = AsyncMock()
    monkeypatch.setattr(validation_service.slack_client, "is_enabled", True)
    monkeypatch.setattr(validation_service.slack_client, "notify", slack_notify)

    await _notify_for_sequence(cast(int, seq.id), 1, alert_id=None)
    await _notify_for_sequence(999_999, 1, alert_id=None)  # vanished sequence: same no-op

    slack_notify.assert_not_called()


@pytest.mark.asyncio
async def test_notify_swallows_unexpected_errors(detection_session: AsyncSession, monkeypatch):
    """The detached notification task never leaks an exception (it would go unobserved)."""
    seq = await _seed_sequence(detection_session, 5)
    monkeypatch.setattr(DetectionCRUD, "fetch_all", AsyncMock(side_effect=RuntimeError("db hiccup")))

    await _notify_for_sequence(cast(int, seq.id), 1, alert_id=None)  # must not raise


@pytest.mark.asyncio
async def test_notification_channel_failures_never_abort_the_job(detection_session: AsyncSession, monkeypatch):
    """Every channel failing (webhook, Telegram, Slack) still completes validation."""
    from app.models import Organization, Webhook

    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    org = await detection_session.get(Organization, 1)
    assert org is not None
    org.telegram_id = "tg"
    org.slack_hook = "http://example.com/hook"
    detection_session.add(org)
    detection_session.add(Webhook(url="http://example.com/webhook"))
    await detection_session.commit()

    def sync_boom(*_args, **_kwargs):
        raise RuntimeError("channel down")

    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: False)  # fail open -> validated
    monkeypatch.setattr(validation_service, "dispatch_webhook", AsyncMock(side_effect=RuntimeError("down")))
    monkeypatch.setattr(validation_service.telegram_client, "is_enabled", True)
    monkeypatch.setattr(validation_service.telegram_client, "notify", sync_boom)
    monkeypatch.setattr(validation_service.slack_client, "is_enabled", True)
    monkeypatch.setattr(validation_service.slack_client, "notify", sync_boom)

    assert await _process_one_due() is True
    await _drain_notifications()  # notifications run detached, off the worker's critical path

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_due_at is None  # job completed despite every channel failing
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_process_handles_vanished_sequence_and_camera(detection_session: AsyncSession, monkeypatch):
    """A sequence (or its camera) gone by processing time completes the job quietly."""
    from app.crud import CameraCRUD

    await _process_claimed_sequence(999_999)  # vanished sequence: no-op

    seq = await _seed_sequence(detection_session, 5)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(CameraCRUD, "get", AsyncMock(return_value=None))  # vanished camera

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_due_at is None  # job completed


@pytest.mark.asyncio
async def test_process_fails_open_when_predict_raises_in_flight(detection_session: AsyncSession, monkeypatch):
    """A call failing while the breaker is closed fails open (TemporalUnavailableError path)."""
    from app.services.temporal import TemporalUnavailableError

    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(side_effect=TemporalUnavailableError("boom")))

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is True
    assert seq.validation_status == FAIL_OPEN_UNAVAILABLE


@pytest.mark.asyncio
async def test_process_lost_claim_leaves_job_due_for_resume(detection_session: AsyncSession, monkeypatch):
    """A loser of the validation claim must NOT complete the job: the winner may have died
    right after the flip, and the due marker is the only thing that resumes its work."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)

    async def predict_and_steal_claim(*_args, **_kwargs):
        # Simulate a sibling winning the claim while the model call is in flight (our lease
        # expired mid-call, the sibling reprocessed the job and died right after the flip).
        async with session_factory() as session:
            await SequenceCRUD(session).claim_validation(cast(int, seq.id))
        return _prediction(0.9)

    monkeypatch.setattr(temporal_service, "predict", predict_and_steal_claim)

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is True  # the concurrent claim stands
    assert seq.validation_due_at is not None  # job NOT completed: the winner's work may be pending
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is False  # no double attach

    # Once the loser's lease expires, the resume path completes the winner's pending work.
    crud = SequenceCRUD(detection_session)
    seq_db = cast(Sequence, await crud.get(cast(int, seq.id), strict=True))
    seq_db.validation_lease_until = utcnow() - timedelta(seconds=60)  # expired, clock-step proof
    detection_session.add(seq_db)
    await detection_session.commit()

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.validation_due_at is None  # resumed and completed
    assert await _has_alert_link(detection_session, cast(int, seq.id)) is True


@pytest.mark.asyncio
async def test_first_score_past_window_below_threshold_is_terminal(detection_session: AsyncSession, monkeypatch):
    """A never-scored sequence past MAX_FRAMES whose first (truncated) score declines must
    land in window_exhausted right away, not linger unlabeled."""
    seq = await _seed_sequence(detection_session, 12, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {})
    monkeypatch.setattr(temporal_service, "is_available", lambda: True)
    monkeypatch.setattr(temporal_service, "predict", AsyncMock(return_value=_prediction(0.40)))  # declined

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_status == WINDOW_EXHAUSTED  # the model had its last chance
    assert seq.validation_due_at is None
    assert seq.temporal_model_score == pytest.approx(0.40)

    # Terminal: a later enqueue can't resurrect it.
    await SequenceCRUD(detection_session).enqueue_validation(cast(int, seq.id))
    await detection_session.refresh(seq)
    assert seq.validation_due_at is None


@pytest.mark.asyncio
async def test_risk_gate_finish_keeps_due_when_frames_changed(detection_session: AsyncSession, monkeypatch):
    """A max_conf bump landing mid-job (it always comes with a new detection) must keep the
    risk-gated job due so the gate re-evaluates immediately instead of losing the bump."""
    seq = await _seed_sequence(detection_session, 5, max_conf=0.30)
    await _enqueue(detection_session, cast(int, seq.id))
    monkeypatch.setattr(risk_service, "_scores", {1: "very_low"})  # 0.6 threshold: gate blocks
    # Simulate a detection arriving after the frame read: the worker saw 4 frames, DB has 5.
    real_frames = validation_service._sequence_frames_and_roi

    async def stale_frames(detections, sequence_id, last_n=None):
        total, frames, roi = await real_frames(detections, sequence_id, last_n)
        return total - 1, frames[:-1], roi

    monkeypatch.setattr(validation_service, "_sequence_frames_and_roi", stale_frames)

    assert await _process_one_due() is True

    await detection_session.refresh(seq)
    assert seq.is_validated is False
    assert seq.validation_due_at is not None  # job kept due: the gate re-evaluates next claim


@pytest.mark.asyncio
async def test_validation_worker_loop_survives_errors_and_idles(monkeypatch):
    """The loop never dies on errors, idles when nothing is due, and stops on cancellation."""
    calls = AsyncMock(side_effect=[True, RuntimeError("boom"), False, asyncio.CancelledError()])
    sleeps = AsyncMock()
    monkeypatch.setattr(validation_service, "process_next_due_validation", calls)
    monkeypatch.setattr(validation_service.asyncio, "sleep", sleeps)

    with pytest.raises(asyncio.CancelledError):
        await validation_worker_loop()

    assert calls.await_count == 4
    assert sleeps.await_count == 2  # after the error and after the idle poll, not after work
