# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, Dict, List, cast

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Detection
from app.schemas.detections import EMPTY_BBOXES


async def get_detection_counts_by_sequence_ids(session: AsyncSession, sequence_ids: List[int]) -> Dict[int, int]:
    if not sequence_ids:
        return {}

    # Continuity rows (empty bbox) carry a frame, not a detection: don't count them.
    stmt: Any = (
        select(cast(Any, Detection.sequence_id), func.count(cast(Any, Detection.id)))
        .where(cast(Any, Detection.sequence_id).in_(sequence_ids))
        .where(cast(Any, Detection.bbox) != EMPTY_BBOXES)
        .group_by(cast(Any, Detection.sequence_id))
    )
    res = await session.exec(stmt)
    return {sequence_id: detections_count for sequence_id, detections_count in res.all() if sequence_id is not None}
