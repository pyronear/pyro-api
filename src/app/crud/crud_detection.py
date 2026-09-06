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
from app.models import Detection
from app.schemas.detections import EMPTY_BBOXES, DetectionCreate, DetectionSequence

__all__ = ["DetectionCRUD"]


class DetectionCRUD(BaseCRUD[Detection, DetectionCreate, DetectionSequence]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Detection)

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
