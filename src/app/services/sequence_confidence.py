# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import logging
import re
from ast import literal_eval
from typing import Any, Dict, Iterable, List, Union, cast

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Detection
from app.schemas.detections import BOX_PATTERN

logger = logging.getLogger("uvicorn.error")

__all__ = ["max_conf_from_bboxes", "get_max_conf_by_sequence_ids"]


def max_conf_from_bboxes(*bbox_strings: Union[str, None]) -> Union[float, None]:
    """Return the highest confidence found across the given bbox strings, or None if none parse."""
    best: Union[float, None] = None
    for raw in bbox_strings:
        if not raw:
            continue
        for match in re.finditer(BOX_PATTERN, raw):
            try:
                bbox = literal_eval(match.group(0))
            except (SyntaxError, ValueError):
                continue
            if not isinstance(bbox, tuple) or len(bbox) != 5:
                continue
            conf = bbox[4]
            if not isinstance(conf, (int, float)):
                continue
            if best is None or conf > best:
                best = float(conf)
    return best


async def get_max_conf_by_sequence_ids(
    session: AsyncSession,
    sequence_ids: Iterable[int],
) -> Dict[int, float]:
    """Return {sequence_id: max_conf} computed from all detections of those sequences.

    Sequences with no detections or unparseable bboxes are omitted from the result —
    callers should treat a missing key as "unknown" and fail open.
    """
    seq_ids: List[int] = list({int(sid) for sid in sequence_ids})
    if not seq_ids:
        return {}

    stmt: Any = select(Detection.sequence_id, Detection.bbox, Detection.others_bboxes).where(
        cast(Any, Detection.sequence_id).in_(seq_ids)
    )
    res = await session.exec(stmt)

    out: Dict[int, float] = {}
    for sequence_id, bbox, others in res.all():
        if sequence_id is None:
            continue
        conf = max_conf_from_bboxes(bbox, others)
        if conf is None:
            continue
        current = out.get(sequence_id)
        if current is None or conf > current:
            out[sequence_id] = conf
    return out
