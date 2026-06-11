# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import logging
from datetime import timedelta
from typing import Any, Union, cast

from sqlalchemy import case, distinct, func, null, or_, select, update
from sqlmodel import select as select_model
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.time import utcnow
from app.crud.base import BaseCRUD
from app.models import TERMINAL_VALIDATION_STATUSES, VALIDATION_FAILED, Detection, Sequence
from app.schemas.sequences import SequenceLabel, SequenceUpdate

__all__ = ["SequenceCRUD"]

logger = logging.getLogger("uvicorn.error")


class SequenceCRUD(BaseCRUD[Sequence, Sequence, Union[SequenceUpdate, SequenceLabel]]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Sequence)

    async def bump_max_conf(self, sequence_id: int, candidate: float) -> None:
        """Atomically raise sequences.max_conf to candidate if higher (or set if NULL).

        Uses a portable CASE expression so it runs on SQLite as well as Postgres.
        """
        max_conf_col = cast(Any, Sequence.max_conf)
        bumped: Any = cast(Any, case)(
            (or_(max_conf_col.is_(None), max_conf_col < candidate), candidate),
            else_=max_conf_col,
        )
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(max_conf=bumped)
        await self.session.exec(stmt)
        await self.session.commit()

    async def set_temporal_score(self, sequence_id: int, score: float) -> None:
        """Persist the latest temporal-model score for the sequence."""
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(temporal_model_score=score)
        await self.session.exec(stmt)
        await self.session.commit()

    async def claim_validation(self, sequence_id: int, validation_status: Union[str, None] = None) -> bool:
        """Atomically flip ``is_validated`` from False to True, recording how it concluded.

        Returns True only for the caller that won the flip, so concurrent workers for the
        same sequence don't both triangulate and notify. ``validation_status`` is written in
        the same UPDATE so the verdict and its label are durable together: post-claim work
        (triangulation, notifications) that fails or dies is resumed without re-deciding.
        """
        id_col = cast(Any, Sequence.id)
        validated_col = cast(Any, Sequence.is_validated)
        values: dict = {"is_validated": True}
        if validation_status is not None:
            values["validation_status"] = validation_status
        stmt: Any = update(Sequence).where(id_col == sequence_id).where(validated_col.is_(False)).values(**values)
        result = await self.session.exec(stmt)
        await self.session.commit()
        return bool(getattr(result, "rowcount", 0))

    async def enqueue_validation(self, sequence_id: int) -> None:
        """Mark the sequence as due for temporal validation (the DB-backed queue).

        Idempotent and FIFO-preserving: ``COALESCE`` keeps the oldest due timestamp, so a
        sequence already queued is NOT re-queued (one entry per sequence, whichever worker
        receives the detection). No-op for validated sequences and terminal states
        (window-exhausted, failed).
        """
        status_col = cast(Any, Sequence.validation_status)
        due_col = cast(Any, Sequence.validation_due_at)
        stmt: Any = (
            update(Sequence)
            .where(cast(Any, Sequence.id) == sequence_id)
            .where(cast(Any, Sequence.is_validated).is_(False))
            .where(or_(status_col.is_(None), status_col.not_in(TERMINAL_VALIDATION_STATUSES)))
            .values(validation_due_at=func.coalesce(due_col, utcnow()))
        )
        await self.session.exec(stmt)
        await self.session.commit()

    async def claim_due_validation(self, lease_seconds: float) -> Union[Sequence, None]:
        """Claim the oldest due sequence for validation, or None when nothing is due.

        ``FOR UPDATE SKIP LOCKED`` keeps concurrent workers (multi-worker uvicorn) off the
        same row; the lease keeps them off for the duration of the model call, which runs
        long after this transaction commits. ``validation_due_at`` is intentionally NOT
        cleared here: a worker dying mid-job leaves a due row whose lease expires, so the
        job is picked up again instead of being lost. Validated rows are NOT filtered out:
        a still-due validated row means a worker died after winning the validation claim
        but before triangulating/notifying, and the job must be resumed.
        """
        now = utcnow()
        due_col = cast(Any, Sequence.validation_due_at)
        lease_col = cast(Any, Sequence.validation_lease_until)
        stmt: Any = (
            select_model(Sequence)
            .where(due_col.is_not(None))
            .where(due_col <= now)
            .where(or_(lease_col.is_(None), lease_col < now))
            .order_by(due_col)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        res = await self.session.exec(stmt)
        sequence_ = res.first()
        if sequence_ is None:
            await self.session.commit()
            return None
        sequence_.validation_lease_until = now + timedelta(seconds=lease_seconds)
        self.session.add(sequence_)
        await self.session.commit()
        await self.session.refresh(sequence_)
        return sequence_

    async def finish_validation_job(
        self,
        sequence_id: int,
        frame_count: Union[int, None] = None,
        validation_status: Union[str, None] = None,
    ) -> None:
        """Release the lease and clear the due marker, completing the job.

        With ``frame_count`` set, the due marker is only cleared if the sequence still has
        exactly that many distinct frames — frames that arrived while the model was scoring
        keep the job due, so the worker re-runs it with the fresh frame set instead of
        waiting for (or losing, if the sequence just ended) the next detection. The
        comparison runs inside the UPDATE so it can't race a concurrent enqueue.
        ``validation_status`` records how validation concluded (observability, incl.
        explicit fail-open reasons) in the same UPDATE.

        Known limitation: the count is a frame-set *proxy*. A detection landing on an
        already-seen bucket_key (changing the ROI but not the count) is not detected; the
        next detection re-enqueues within the camera cadence, which is good enough at the
        expected volume.
        """
        due_col = cast(Any, Sequence.validation_due_at)
        if frame_count is None:
            new_due: Any = null()
        else:
            count_select: Any = select(func.count(distinct(cast(Any, Detection.bucket_key)))).where(
                cast(Any, Detection.sequence_id) == sequence_id
            )
            count_sq = count_select.scalar_subquery()
            new_due = cast(Any, case)((count_sq == frame_count, null()), else_=due_col)
        # Completing a job also resets the consecutive-error counter, so the dead-letter
        # cap counts consecutive failures, not lifetime ones.
        values: dict = {"validation_due_at": new_due, "validation_lease_until": None, "validation_attempts": 0}
        if validation_status is not None:
            values["validation_status"] = validation_status
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(**values)
        await self.session.exec(stmt)
        await self.session.commit()

    async def fail_or_retry_validation(self, sequence_id: int, *, max_attempts: int, retry_in_seconds: float) -> None:
        """Error path: release the lease and either back off the retry or dead-letter.

        Increments the consecutive-error counter; below ``max_attempts`` the job stays due,
        pushed ``retry_in_seconds`` into the future (no tight retry loop). At the cap the
        job dead-letters: terminal ``validation_status='failed'``, due cleared, never
        retried nor re-enqueued — a poison job must not starve the serial worker forever.
        Note the staleness fail-open can't bound this (each retry refreshes the due time),
        hence the explicit attempts cap.
        """
        sequence_ = cast(Sequence, await self.get(sequence_id, strict=True))
        attempts = (sequence_.validation_attempts or 0) + 1
        values: dict = {"validation_attempts": attempts, "validation_lease_until": None}
        if attempts >= max_attempts:
            values["validation_status"] = VALIDATION_FAILED
            values["validation_due_at"] = None
            logger.error("Sequence %s failed validation %d times; giving up", sequence_id, attempts)
        else:
            values["validation_due_at"] = utcnow() + timedelta(seconds=retry_in_seconds)
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(**values)
        await self.session.exec(stmt)
        await self.session.commit()
