# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

"""DB-coordinated temporal validation worker.

Each detection marks its sequence as due (``sequences.validation_due_at``, one entry per
sequence); one worker loop per uvicorn process claims due sequences with ``FOR UPDATE SKIP
LOCKED`` + a lease and runs the risk + temporal pipeline. Postgres is the coordination
point, so the design holds with any number of uvicorn workers: no duplicate model calls,
no in-memory queue lost on restart, and a worker dying mid-job just leaves an expired
lease for a sibling to pick up.

Frames are read at scoring time (not at enqueue time), so a sequence queued behind a
backlog is scored with its freshest frame set. The job pipeline runs in three phases so
the (slow) model call never holds a DB session.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional, Set, Tuple, cast

from anyio import to_thread
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from app.api.dependencies import dispatch_webhook
from app.core.config import settings
from app.core.time import utcnow
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, OrganizationCRUD, SequenceCRUD, WebhookCRUD
from app.db import engine, session_factory
from app.models import (
    FAIL_OPEN_STALE,
    FAIL_OPEN_UNAVAILABLE,
    VALIDATED_BY_MODEL,
    VALIDATION_FAILED,
    WINDOW_EXHAUSTED,
    Camera,
    Sequence,
)
from app.services.risk import risk_service
from app.services.slack import slack_client
from app.services.storage import s3_service
from app.services.telegram import telegram_client
from app.services.temporal import TemporalUnavailableError, temporal_service

logger = logging.getLogger("uvicorn.error")

__all__ = [
    "FAIL_OPEN_STALE",
    "FAIL_OPEN_UNAVAILABLE",
    "VALIDATED_BY_MODEL",
    "VALIDATION_FAILED",
    "WINDOW_EXHAUSTED",
    "process_next_due_validation",
    "validation_worker_loop",
]

# Backoff before retrying a job that errored (keeps a persistently failing job from
# spinning the worker; the job stays due so it is never lost prematurely).
RETRY_DELAY_SECONDS = 30.0
# Consecutive errors before a job dead-letters as validation_status='failed': a poison job
# must not starve the serial worker forever (the staleness fail-open can't bound this, as
# each retry refreshes the due time).
MAX_VALIDATION_ATTEMPTS = 5

# Detached notification tasks (fired after job completion, off the worker's critical path).
# Strong references so the tasks aren't garbage-collected mid-flight.
_pending_notifications: set = set()

# Advisory-lock namespace (arbitrary app-wide constant) for per-organization alert attachment.
_ALERT_LOCK_NAMESPACE = 7341


@asynccontextmanager
async def _organization_alert_lock(organization_id: int) -> AsyncIterator[None]:
    """Cross-process mutex serializing alert attachment within an organization.

    Uses a Postgres session-level advisory lock on a dedicated connection (the attachment
    session commits mid-way, which would release a transaction-level lock too early). The
    lock is released in all cases when the connection closes.
    """
    async with engine.connect() as conn:
        await conn.execute(
            text("SELECT pg_advisory_lock(:ns, :key)"), {"ns": _ALERT_LOCK_NAMESPACE, "key": organization_id}
        )
        try:
            yield
        finally:
            await conn.execute(
                text("SELECT pg_advisory_unlock(:ns, :key)"), {"ns": _ALERT_LOCK_NAMESPACE, "key": organization_id}
            )


async def _sequence_frames_and_roi(
    detections: DetectionCRUD, sequence_id: int, last_n: Optional[int] = None
) -> Tuple[int, List[str], Optional[List[float]]]:
    """Distinct frame keys of the sequence (oldest first) and the ROI covering their bboxes.

    Returns ``(total_distinct, frames, roi)``. With ``last_n`` set, ``frames`` is truncated
    to the most recent ``last_n`` distinct frames (the most informative ones for smoke) and
    the ROI only covers the kept frames; ``total_distinct`` always reports the full count so
    the caller can apply the window rules.

    The ROI is the union envelope of the kept detections' primary bboxes (normalized xyxyn
    corners), scoping the temporal verdict to the tracked region so unrelated activity
    elsewhere in the frame can't pollute it. ``None`` when no bbox parses (full-frame).
    """
    # Imported lazily: the endpoints module imports services at module load.
    from app.api.api_v1.endpoints.detections import _extract_bbox_strings, _parse_bbox

    dets = await detections.fetch_all(
        filters=("sequence_id", sequence_id),
        order_by="created_at",
        order_desc=False,
    )
    frames: List[str] = []
    seen: Set[str] = set()
    corners_by_frame: Dict[str, List[Tuple[float, float, float, float]]] = {}
    for det in dets:
        if det.bucket_key not in seen:
            seen.add(det.bucket_key)
            frames.append(det.bucket_key)
        bbox_strs = _extract_bbox_strings(det.bbox)
        if bbox_strs:
            try:
                xmin, ymin, xmax, ymax, _ = _parse_bbox(bbox_strs[0])
                corners_by_frame.setdefault(det.bucket_key, []).append((xmin, ymin, xmax, ymax))
            except HTTPException:
                logger.debug("Skipping unparseable bbox on detection %s", det.id)
    total = len(frames)
    kept = frames if last_n is None or total <= last_n else frames[-last_n:]
    corners = [c for frame in kept for c in corners_by_frame.get(frame, [])]
    if not corners:
        return total, kept, None
    roi = [
        max(0.0, min(c[0] for c in corners)),
        max(0.0, min(c[1] for c in corners)),
        min(1.0, max(c[2] for c in corners)),
        min(1.0, max(c[3] for c in corners)),
    ]
    if not (roi[0] < roi[2] and roi[1] < roi[3]):
        return total, kept, None
    return total, kept, roi


async def _notify_for_sequence(sequence_id: int, organization_id: int, alert_id: Optional[int]) -> None:
    """Best-effort notifications (webhooks, Telegram, Slack) for a freshly validated sequence.

    All channels sit behind the validation gate, carrying the sequence's latest detection.
    Runs as a detached task AFTER job completion, off the worker's critical path: a slow or
    hanging channel must never delay the next sequence's scoring. The flip side (accepted):
    a crash between completion and delivery loses the notification — consistent with the
    channels being best-effort (errors swallowed, no retries), while the durable artifact
    is the alert row created by triangulation. Each channel is independent: one failing
    never blocks the others. Owns its session so it can outlive the worker's.
    """
    try:
        async with session_factory() as session:
            sequences = SequenceCRUD(session)
            detections = DetectionCRUD(session)
            sequence_ = await sequences.get(sequence_id)
            if sequence_ is None:
                return
            camera = await CameraCRUD(session).get(sequence_.camera_id)
            dets = await detections.fetch_all(
                filters=("sequence_id", sequence_id), order_by="created_at", order_desc=True, limit=1
            )
            if camera is None or not dets:
                return
            det = dets[0]
            org = await OrganizationCRUD(session).get(organization_id)

            for webhook in await WebhookCRUD(session).fetch_all():
                try:
                    await dispatch_webhook(webhook.url, det)
                except Exception as exc:  # noqa: BLE001 - best-effort: never let a webhook failure block the rest
                    logger.warning("Webhook dispatch to %s failed for sequence %s (%s)", webhook.url, sequence_id, exc)

            if telegram_client.is_enabled and org is not None and org.telegram_id:
                try:
                    await to_thread.run_sync(telegram_client.notify, org.telegram_id, det.model_dump_json())
                except Exception as exc:  # noqa: BLE001 - best-effort: never let a Telegram failure block the rest
                    logger.warning("Telegram notification failed for sequence %s (%s)", sequence_id, exc)

            if slack_client.is_enabled and org is not None and org.slack_hook:
                slack_payload = jsonable_encoder(det)
                slack_payload["sequence_azimuth"] = sequence_.sequence_azimuth
                try:
                    await to_thread.run_sync(
                        slack_client.notify, org.slack_hook, json.dumps(slack_payload), camera.name, alert_id
                    )
                except Exception as exc:  # noqa: BLE001 - best-effort: never let a Slack failure block the rest
                    logger.warning("Slack notification failed for sequence %s (%s)", sequence_id, exc)
    except Exception:
        logger.exception("Notification dispatch failed for sequence %s", sequence_id)


def _dispatch_notifications(sequence_id: int, organization_id: int, alert_id: Optional[int]) -> None:
    """Fire notifications as a detached task, keeping a strong reference until done."""
    task = asyncio.create_task(_notify_for_sequence(sequence_id, organization_id, alert_id))
    _pending_notifications.add(task)
    task.add_done_callback(_pending_notifications.discard)


async def _finish_job(
    sequence_id: int, frame_count: Optional[int] = None, validation_status: Optional[str] = None
) -> None:
    async with session_factory() as session:
        await SequenceCRUD(session).finish_validation_job(sequence_id, frame_count, validation_status)


async def _process_claimed_sequence(sequence_id: int) -> None:
    """Run the risk + temporal validation pipeline for a claimed sequence.

    Takes only the id on purpose: ALL state is read fresh from the DB (a detection can bump
    max_conf while the job sits in the queue, and a prior run may have persisted a score or
    the validated flag before dying — a claim-time snapshot would be stale). Three phases so
    the (possibly slow) model call never holds a DB session: read state and apply the risk
    gate, call the model, then persist + triangulate + notify.
    """
    # Phase 1 — read state and apply the risk gate (short-lived session).
    async with session_factory() as session:
        sequences = SequenceCRUD(session)
        cameras = CameraCRUD(session)
        detections = DetectionCRUD(session)
        sequence_ = await sequences.get(sequence_id)
        if sequence_ is None:
            await _finish_job(sequence_id)
            return
        if sequence_.is_validated:
            # A previous run died after winning the claim but before completing the
            # post-claim work (the due marker only clears on completion): resume it.
            await _complete_validated_sequence(sequence_id, validation_status=None, claim=False)
            return
        due_since = sequence_.validation_due_at
        camera = await cameras.get(sequence_.camera_id)
        if camera is None:
            await _finish_job(sequence_id)
            return
        organization_id = camera.organization_id
        total_frames, frames, roi_xyxyn = await _sequence_frames_and_roi(
            detections, sequence_id, last_n=temporal_service.MAX_FRAMES
        )
        # Risk pre-gate: in low fire-risk weather, low-confidence sequences are filtered out.
        # The finish is conditional on the frame count (read BEFORE the gate) so a detection
        # bumping max_conf mid-job keeps the job due and the gate re-evaluates immediately,
        # instead of the bump being lost until the next detection.
        threshold = risk_service.min_confidence(camera.id)
        if threshold is not None and (sequence_.max_conf is None or sequence_.max_conf < threshold):
            await _finish_job(sequence_id, frame_count=total_frames)
            return

    score: Optional[float] = None
    validation_status: Optional[str] = None

    # Window rules past MAX_FRAMES, decided on the stored score. Declined (score <=
    # threshold after its in-window chances) is terminal: don't call the model again and
    # never resurrect via a later fail-open. Scored ABOVE threshold means a previous run
    # validated but didn't complete (e.g. a failed alert attachment released the claim):
    # validate from the stored score — a high score must never decay into a drop. Never
    # scored (backlog, model freshly configured): score the last MAX_FRAMES anyway —
    # backlog must delay sequences, never silently drop them.
    prior_score = sequence_.temporal_model_score
    if total_frames > temporal_service.MAX_FRAMES and prior_score is not None:
        if prior_score > settings.TEMPORAL_MODEL_THRESHOLD:
            await _complete_validated_sequence(sequence_id, VALIDATED_BY_MODEL, claim=True)
            return
        await _finish_job(sequence_id, validation_status=WINDOW_EXHAUSTED)
        return

    if not temporal_service.is_available():
        # Not configured, unreachable, or breaker open: trust the risk gate already passed.
        validated = True
        validation_status = FAIL_OPEN_UNAVAILABLE
    elif total_frames < temporal_service.MIN_FRAMES:
        # Too few frames for the model to score; the next detection re-enqueues. By design a
        # sequence that never reaches MIN_FRAMES is not validated while the model is reachable
        # (short/noise sequences are suppressed); only the unavailable fail-open above lets
        # them through. Checked BEFORE staleness on purpose: a short sequence isn't waiting
        # on the model — if its job went stale at <MIN_FRAMES, the sequence stopped emitting,
        # and failing it open would notify on noise.
        await _finish_job(sequence_id, frame_count=total_frames)
        return
    elif due_since is not None and (utcnow() - due_since).total_seconds() > settings.TEMPORAL_VALIDATION_MAX_AGE:
        # Queued past the useful scoring window (sustained backlog): bound the latency by
        # failing open EXPLICITLY rather than scoring too late to matter. Traced in
        # validation_status so overload-induced fail-opens are observable.
        validated = True
        validation_status = FAIL_OPEN_STALE
        logger.warning(
            "Sequence %s queued for >%ss; failing open on the risk gate alone",
            sequence_id,
            settings.TEMPORAL_VALIDATION_MAX_AGE,
        )
    else:
        if total_frames > temporal_service.MAX_FRAMES:
            logger.warning(
                "Sequence %s exceeded %d frames before first scoring; scoring the last %d",
                sequence_id,
                temporal_service.MAX_FRAMES,
                temporal_service.MAX_FRAMES,
            )
        # Phase 2 — model call, with NO DB session held.
        bucket = s3_service.resolve_bucket_name(organization_id)
        try:
            score = await temporal_service.predict(bucket, frames, roi_xyxyn=roi_xyxyn)
        except TemporalUnavailableError:
            validated = True
            validation_status = FAIL_OPEN_UNAVAILABLE
        else:
            if score is None:
                # Successful but scoreless response (uncalibrated model): cannot confirm,
                # retry on the next frame set.
                await _finish_job(sequence_id, frame_count=total_frames)
                return
            validated = score > settings.TEMPORAL_MODEL_THRESHOLD
            validation_status = VALIDATED_BY_MODEL if validated else None

    # Phase 3 — persist the score and, once validated, claim + triangulate + notify.
    if score is not None:
        async with session_factory() as session:
            await SequenceCRUD(session).set_temporal_score(sequence_id, score)
    if not validated:
        if total_frames > temporal_service.MAX_FRAMES:
            # The model just had its LAST chance (first scoring past the window, on the
            # last MAX_FRAMES) and declined: terminal right away, consistent with the
            # stored-score-below-threshold rule above.
            await _finish_job(sequence_id, validation_status=WINDOW_EXHAUSTED)
            return
        # Below threshold in-window: keep the score, retry when the frame set grows (the
        # conditional finish keeps the job due if frames arrived during scoring).
        await _finish_job(sequence_id, frame_count=total_frames)
        return
    await _complete_validated_sequence(sequence_id, validation_status, claim=True)


async def _complete_validated_sequence(sequence_id: int, validation_status: Optional[str], *, claim: bool) -> None:
    """Post-validation work: claim, triangulate, complete the job, then notify (detached).

    Reached right after a verdict (``claim=True``) and when resuming a run that died after
    winning the claim (``claim=False`` — the due marker only clears on completion, so a
    crash mid-way is resumed by whichever worker claims the job after the lease expires).
    """
    async with session_factory() as session:
        sequences = SequenceCRUD(session)
        # Atomically claim the sequence (verdict + status in one UPDATE) so concurrent
        # workers can't both triangulate/notify. From here on the verdict is durable: any
        # failure below propagates to the caller, which releases the lease and pushes the
        # retry back — the job stays due and validated, so the retry resumes HERE
        # instead of re-deciding a verdict that was already reached.
        if claim and not await sequences.claim_validation(sequence_id, validation_status):
            # Lost the claim: someone else validated (e.g. our lease expired mid-model-call
            # and a sibling reprocessed the job). Do NOT complete the job — we can't know
            # whether the winner finished its post-claim work or died right after the flip.
            # Leaving the row due is always safe: if the winner finished, it already cleared
            # the due marker; if it died, the lease expiry resumes attach/notify here.
            return
        # Imported lazily to avoid a services -> endpoints import at module load.
        from app.api.api_v1.endpoints.detections import _attach_sequence_to_alert

        cameras = CameraCRUD(session)
        alerts = AlertCRUD(session)
        sequence_ = cast(Sequence, await sequences.get(sequence_id, strict=True))
        camera = cast(Camera, await cameras.get(sequence_.camera_id, strict=True))
        organization_id = camera.organization_id
        # Two workers validating two sequences of the same event concurrently must not
        # both create an alert: serialize attachment per organization.
        async with _organization_alert_lock(organization_id):
            alert_id = await _attach_sequence_to_alert(sequence_, camera, cameras, sequences, alerts)
        # Validated is terminal: complete the job (the due marker is the completion record
        # that makes this block resumable), THEN notify off the critical path — a slow
        # channel must never delay the next sequence's scoring.
        await sequences.finish_validation_job(sequence_id)
    _dispatch_notifications(sequence_id, organization_id, alert_id)


async def process_next_due_validation() -> bool:
    """Claim and process one due sequence. Returns True when a job was claimed.

    An error releases the lease and backs the retry off; after MAX_VALIDATION_ATTEMPTS
    consecutive errors the job dead-letters (validation_status='failed') so a poison job
    can't starve the serial worker.
    """
    async with session_factory() as session:
        sequence_ = await SequenceCRUD(session).claim_due_validation(settings.TEMPORAL_VALIDATION_LEASE_SECONDS)
    if sequence_ is None:
        return False
    sequence_id = sequence_.id
    try:
        await _process_claimed_sequence(sequence_id)
    except Exception:
        logger.exception("Sequence validation failed for sequence %s", sequence_id)
        async with session_factory() as session:
            await SequenceCRUD(session).fail_or_retry_validation(
                sequence_id, max_attempts=MAX_VALIDATION_ATTEMPTS, retry_in_seconds=RETRY_DELAY_SECONDS
            )
    return True


async def validation_worker_loop() -> None:
    """Per-process validation worker: drains due sequences, then idles on a short poll.

    Supervised by construction — every iteration is wrapped, so no exception can silently
    kill the loop (only cancellation at shutdown stops it).
    """
    logger.info("Temporal validation worker started")
    while True:
        try:
            if not await process_next_due_validation():
                await asyncio.sleep(settings.TEMPORAL_VALIDATION_POLL_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Validation worker iteration failed; continuing")
            await asyncio.sleep(settings.TEMPORAL_VALIDATION_POLL_SECONDS)
