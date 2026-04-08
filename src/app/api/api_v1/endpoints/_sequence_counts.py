# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, Dict, List, cast

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Detection


async def get_detection_counts_by_sequence_ids(session: AsyncSession, sequence_ids: List[int]) -> Dict[int, int]:
    if not sequence_ids:
        return {}

    stmt: Any = (
        select(cast(Any, Detection.sequence_id), func.count(Detection.id))
        .where(cast(Any, Detection.sequence_id).in_(sequence_ids))
        .group_by(cast(Any, Detection.sequence_id))
    )
    res = await session.exec(stmt)
    return {int(sequence_id): int(detections_count) for sequence_id, detections_count in res.all() if sequence_id is not None}
