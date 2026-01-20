# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from ast import literal_eval
from operator import itemgetter


def resolve_cone(azimuth: float, bboxes_str: str, aov: float) -> tuple[float, float]:
    """Compute the cone azimuth and opening angle using the most confident bbox.

    Args:
        azimuth: The azimuth of the camera.
        bboxes_str: The string representation of the bboxes.
        aov: The angle of view of the camera.

    Returns:
        A tuple of the cone azimuth and opening angle.
    """
    bboxes = literal_eval(bboxes_str)
    xmin, _, xmax, _, _ = max(bboxes, key=itemgetter(2))
    cone_azimuth = round(azimuth + aov * ((xmin + xmax) / 2 - 0.5), 1)
    cone_angle = round(aov * (xmax - xmin), 1)
    return cone_azimuth, cone_angle
