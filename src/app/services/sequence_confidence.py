# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import logging
import re
from ast import literal_eval
from datetime import date
from typing import Any, Dict, Iterable, List, Union, cast
from typing import Sequence as TypingSequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Detection, Sequence
from app.schemas.detections import BOX_PATTERN
from app.services.risk import min_confidence_for_class, risk_service

logger = logging.getLogger("uvicorn.error")

__all__ = [
    "filter_sequences_by_risk",
    "filter_sequences_by_risk_for_date",
    "get_max_conf_by_sequence_ids",
    "max_conf_from_bboxes",
]


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


async def _filter_sequences(
    session: AsyncSession,
    sequences: TypingSequence[Sequence],
    thresholds: Dict[int, Union[float, None]],
) -> List[Sequence]:
    if all(threshold is None for threshold in thresholds.values()):
        return list(sequences)

    seq_ids_to_check = [seq.id for seq in sequences if thresholds.get(seq.camera_id) is not None]
    confs = await get_max_conf_by_sequence_ids(session, seq_ids_to_check)

    kept: List[Sequence] = []
    for seq in sequences:
        threshold = thresholds.get(seq.camera_id)
        if threshold is None:
            kept.append(seq)
            continue
        conf = confs.get(seq.id)
        if conf is None or conf >= threshold:
            kept.append(seq)
    return kept


async def filter_sequences_by_risk(
    session: AsyncSession,
    sequences: TypingSequence[Sequence],
) -> List[Sequence]:
    """Drop sequences whose max conf is below today's risk-driven threshold for their camera.

    Fail-open: a sequence is kept if either the camera has no FWI score (moderate+ or unknown)
    or the sequence has no parseable confidence.
    """
    if not sequences:
        return []
    thresholds = {seq.camera_id: risk_service.min_confidence(seq.camera_id) for seq in sequences}
    return await _filter_sequences(session, sequences, thresholds)


async def filter_sequences_by_risk_for_date(
    session: AsyncSession,
    sequences: TypingSequence[Sequence],
    target_date: date,
    organization_id: Union[int, None] = None,
) -> List[Sequence]:
    """Like filter_sequences_by_risk, but uses the FWI class persisted for a specific date.

    When ``organization_id`` is provided, the risk-api call is scoped to that organization.
    """
    if not sequences:
        return []
    scores = await risk_service.get_scores_for_date(target_date, organization_id=organization_id)
    thresholds = {seq.camera_id: min_confidence_for_class(scores.get(seq.camera_id)) for seq in sequences}
    return await _filter_sequences(session, sequences, thresholds)
