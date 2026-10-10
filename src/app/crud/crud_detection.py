# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, List, Union, cast

from sqlalchemy import desc, func
from sqlalchemy import select as select_sa
from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Camera, Detection
from app.schemas.detections import EMPTY_BBOXES, DetectionCreate, DetectionSequence

__all__ = ["DetectionCRUD"]


class DetectionCRUD(BaseCRUD[Detection, DetectionCreate, DetectionSequence]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Detection)

    async def fetch_page(self, *, organization_id: int | None, limit: int, offset: int) -> List[Detection]:
        stmt: Any = select(Detection)
        if organization_id is not None:
            stmt = stmt.join(Camera, cast(Any, Camera.id) == Detection.camera_id).where(
                Camera.organization_id == organization_id
            )
        stmt = stmt.order_by(cast(Any, Detection.id)).limit(limit).offset(offset)
        return list((await self.session.exec(stmt)).all())

    async def fetch_frame_window(self, sequence_id: int, last_n: int | None) -> tuple[int, list[str], list[Detection]]:
        """Count every distinct frame, but hydrate only the selected recent frames.

        A frame's first detection defines its chronological position. Multiple bboxes and
        continuity rows sharing its key still count as one frame and all contribute to ROI.
        """
        key = cast(Any, Detection.bucket_key)
        sequence = cast(Any, Detection.sequence_id)
        count_stmt: Any = select(func.count(func.distinct(key))).where(sequence == sequence_id)
        total = int((await self.session.exec(count_stmt)).one())
        first_seen = func.min(cast(Any, Detection.created_at))
        first_id = func.min(cast(Any, Detection.id))
        frames_stmt: Any = (
            select(key).where(sequence == sequence_id).group_by(key).order_by(first_seen.desc(), first_id.desc())
        )
        if last_n is not None:
            frames_stmt = frames_stmt.limit(last_n)
        frames = list(reversed((await self.session.exec(frames_stmt)).all()))
        if not frames:
            return total, [], []
        detections_stmt: Any = select(Detection).where(sequence == sequence_id, key.in_(frames))
        detections = list((await self.session.exec(detections_stmt)).all())
        return total, frames, detections

    async def get_latest_with_bbox(self, sequence_id: int) -> Union[Detection, None]:
        """Latest detection of the sequence carrying a real bbox (continuity rows excluded)."""
        statement: Any = (
            select(Detection)
            .where(cast(Any, Detection.sequence_id) == sequence_id)
            .where(cast(Any, Detection.bbox) != EMPTY_BBOXES)
            .order_by(desc(cast(Any, Detection.created_at)))
            .limit(1)
        )
        results = await self.session.exec(statement)
        return results.first()

    async def get_latest_bboxes(self, sequence_ids: list[int]) -> dict[int, Detection]:
        """Fetch one latest real detection per candidate sequence in a single query."""
        if not sequence_ids:
            return {}
        sequence = cast(Any, Detection.sequence_id)
        rank = func.row_number().over(
            partition_by=sequence,
            order_by=(cast(Any, Detection.created_at).desc(), cast(Any, Detection.id).desc()),
        )
        numbered: Any = (
            select_sa(Detection, rank.label("rn"))
            .where(sequence.in_(sequence_ids))
            .where(cast(Any, Detection.bbox) != EMPTY_BBOXES)
        )
        subq = numbered.subquery()
        latest = aliased(Detection, subq)
        stmt: Any = select(latest).where(subq.c.rn == 1)
        return {cast(int, det.sequence_id): det for det in (await self.session.exec(stmt)).all()}

    async def fetch_by_sequence(
        self,
        sequence_id: int,
        sampling: int = 1,
        order_desc: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Detection]:
        """Fetch the detections of a sequence, keeping one every ``sampling``.

        ``offset`` counts raw detections, never sampled frames. When sampling, the row number is
        computed ascending on ``created_at``, so neither the offset nor the kept set depends on
        ``order_desc``: it only flips the output order. Page by advancing ``offset`` in multiples
        of ``sampling`` to keep the grid on the same detections. Unsampled calls delegate to
        ``fetch_all``, where a SQL ``OFFSET`` applies after the sort and so counts from whichever
        end ``order_desc`` selects.
        """
        if sampling <= 1:
            return await self.fetch_all(
                filters=("sequence_id", sequence_id),
                order_by="created_at",
                order_desc=order_desc,
                limit=limit,
                offset=offset,
            )

        # id breaks created_at ties so the sampled set is deterministic run to run.
        row_num = func.row_number().over(
            order_by=(cast(Any, Detection.created_at).asc(), cast(Any, Detection.id).asc())
        )
        # sqlmodel's select on the outer query: a single-entity SelectOfScalar is what makes
        # exec return Detection instances rather than Row tuples.
        numbered: Any = select_sa(Detection, row_num.label("rn")).where(cast(Any, Detection.sequence_id) == sequence_id)
        subq = numbered.subquery()
        sampled = aliased(Detection, subq)
        created_at_col = cast(Any, sampled.created_at)
        id_col = cast(Any, sampled.id)
        # offset in the WHERE, not a SQL OFFSET: it counts raw detections on the ascending
        # numbering, and a SQL OFFSET would instead apply after ORDER BY.
        position = subq.c.rn - 1
        stmt: Any = (
            select(sampled)
            .where(position >= offset)
            .where((position - offset) % sampling == 0)
            .order_by(
                created_at_col.desc() if order_desc else created_at_col.asc(),
                id_col.desc() if order_desc else id_col.asc(),
            )
            .limit(limit)
        )
        result = await self.session.exec(stmt)
        return list(result.all())
