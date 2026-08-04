# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from ast import literal_eval
from math import asin, cos, radians, sin, sqrt
from operator import itemgetter
from typing import Tuple


def resolve_cone(azimuth: float, bboxes_str: str, aov: float) -> Tuple[float, float]:
    """Compute the cone azimuth and opening angle using the most confident bbox."""
    bboxes = literal_eval(bboxes_str)
    xmin, _, xmax, _, _ = max(bboxes, key=itemgetter(2))
    cone_azimuth = round(azimuth + aov * ((xmin + xmax) / 2 - 0.5), 1) % 360
    cone_angle = round(aov * (xmax - xmin), 1)
    return cone_azimuth, cone_angle


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance between two coordinates in kilometres."""
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371.0 * asin(sqrt(a))
