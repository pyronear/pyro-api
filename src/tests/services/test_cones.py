# Copyright (C) 2025-2026, Pyronear.
#
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import pytest

from app.services.cones import resolve_cone


@pytest.mark.parametrize(
    ("azimuth", "bbox", "aov", "expected_azimuth", "expected_angle"),
    [
        # Centered bbox: cone azimuth equals camera azimuth.
        (180.0, "[(0.4, 0.0, 0.6, 1.0, 0.9)]", 60.0, 180.0, 12.0),
        # Negative wrap: small camera azimuth + bbox on the left.
        (5.0, "[(0.0, 0.0, 0.2, 1.0, 0.9)]", 60.0, 341.0, 12.0),
        # Over-360 wrap: large camera azimuth + bbox on the right.
        (355.0, "[(0.8, 0.0, 1.0, 1.0, 0.9)]", 60.0, 19.0, 12.0),
        # Exactly 360 -> normalized to 0.
        (336.0, "[(0.8, 0.0, 1.0, 1.0, 0.9)]", 60.0, 0.0, 12.0),
    ],
)
def test_resolve_cone_normalizes_azimuth(azimuth, bbox, aov, expected_azimuth, expected_angle):
    cone_azimuth, cone_angle = resolve_cone(azimuth, bbox, aov)
    assert 0.0 <= cone_azimuth < 360.0
    assert cone_azimuth == expected_azimuth
    assert cone_angle == expected_angle
