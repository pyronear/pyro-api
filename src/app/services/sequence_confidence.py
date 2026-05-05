# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import logging
import re
from ast import literal_eval
from typing import Dict, List, Union
from typing import Sequence as TypingSequence

from app.models import Sequence
from app.schemas.detections import BOX_PATTERN
from app.services.risk import min_confidence_for_class

logger = logging.getLogger("uvicorn.error")

__all__ = ["filter_by_class_per_camera", "max_conf_from_bboxes"]


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


def filter_by_class_per_camera(
    sequences: TypingSequence[Sequence],
    class_per_camera: Dict[int, Union[str, None]],
) -> List[Sequence]:
    """Drop sequences whose stored ``max_conf`` falls below the threshold for their camera's FWI class.

    Fail-open: a sequence is kept when its camera has no FWI class (moderate+ or unknown)
    or when ``seq.max_conf`` is NULL.
    """
    if not sequences:
        return []
    thresholds = {cid: min_confidence_for_class(c) for cid, c in class_per_camera.items()}
    if all(t is None for t in thresholds.values()):
        return list(sequences)
    return [
        seq
        for seq in sequences
        if (t := thresholds.get(seq.camera_id)) is None or seq.max_conf is None or seq.max_conf >= t
    ]
