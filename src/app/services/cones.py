# Copyright (C) 2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from ast import literal_eval
from operator import itemgetter
from typing import Tuple


def resolve_cone(azimuth: float, bboxes_str: str, aov: float) -> Tuple[float, float]:
    """Compute the cone azimuth and opening angle using the most confident bbox."""
    bboxes = literal_eval(bboxes_str)
    xmin, _, xmax, _, _ = max(bboxes, key=itemgetter(2))
    cone_azimuth = azimuth + aov * ((xmin + xmax) / 2 - 0.5)
    cone_angle = aov * (xmax - xmin)
    return cone_azimuth, cone_angle
