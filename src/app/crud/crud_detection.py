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

        The row number is always computed ascending on ``created_at``, so the sampled frame set
        is the same whatever ``order_desc`` is: the latter only flips the output order. That
        also keeps the set stable as the sequence grows, since a new detection lands last and
        cannot renumber earlier rows, so the player keeps hitting the same frames (and the same
        cached URLs) across polls. ``(rn - 1) % sampling == 0`` keeps the first detection, so a
        non-empty sequence always yields at least one row. ``limit``/``offset`` page the
        *sampled* set, not the raw rows.

        Note that ``limit`` cannot push down: ``row_number()`` has to cover every row of the
        sequence before the modulo and the limit apply, which is why detections is indexed on
        ``(sequence_id, created_at)``.
        """
        if sampling <= 1:
            # Unchanged pre-sampling behaviour, on purpose: same query, same ordering.
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
        # sqlalchemy's select for the numbering subquery (two entities, and .subquery() on it);
        # sqlmodel's select for the outer one, since a single-entity SelectOfScalar is what makes
        # session.exec return Detection instances rather than Row tuples.
        numbered: Any = select_sa(Detection, row_num.label("rn")).where(cast(Any, Detection.sequence_id) == sequence_id)
        subq = numbered.subquery()
        sampled = aliased(Detection, subq)
        created_at_col = cast(Any, sampled.created_at)
        id_col = cast(Any, sampled.id)
        stmt: Any = (
            select(sampled)
            .where((subq.c.rn - 1) % sampling == 0)
            .order_by(
                created_at_col.desc() if order_desc else created_at_col.asc(),
                id_col.desc() if order_desc else id_col.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.exec(stmt)
        return list(result.all())
