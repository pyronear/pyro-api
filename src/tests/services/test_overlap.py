# Copyright (C) 2025-2026, Pyronear.
#
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timedelta

import pandas as pd

from app.services.overlap import compute_overlap


def _make_sequence(
    id_: int,
    lat: float,
    lon: float,
    sequence_azimuth: float,
    cone_angle: float,
    started_at: datetime,
    last_seen_at: datetime,
    is_wildfire=None,
    pose_id: int | None = None,
):
    return {
        "id": id_,
        "pose_id": pose_id if pose_id is not None else id_,
        "lat": lat,
        "lon": lon,
        "sequence_azimuth": sequence_azimuth,
        "cone_angle": cone_angle,
        "is_wildfire": is_wildfire,
        "started_at": started_at,
        "last_seen_at": last_seen_at,
    }


def test_compute_overlap_groups_and_locations() -> None:
    now = datetime.utcnow()
    seqs = [
        _make_sequence(1, 48.3792, 2.8208, 276.5, 3.0, now - timedelta(seconds=9), now - timedelta(seconds=1)),
        _make_sequence(2, 48.2605, 2.7064, 8.3, 0.8, now - timedelta(seconds=8), now - timedelta(seconds=2)),
        _make_sequence(3, 48.4267, 2.7109, 163.4, 1.0, now - timedelta(seconds=7), now - timedelta(seconds=3)),
        _make_sequence(4, 10.0, 10.0, 90.0, 1.0, now - timedelta(seconds=6), now - timedelta(seconds=4)),
    ]
    df = compute_overlap(pd.DataFrame.from_records(seqs))

    row1 = df[df["id"] == 1].iloc[0]
    row4 = df[df["id"] == 4].iloc[0]

    assert row1["event_groups"] == [(1, 2, 3)]
    assert row1["event_smoke_locations"][0] is not None

    # Non-overlapping singleton keeps its own group and no location
    assert row4["event_groups"] == [(4,)]
    assert row4["event_smoke_locations"] == [None]


def test_compute_overlap_skips_same_pose_pair() -> None:
    now = datetime.utcnow()
    # Two sequences from the exact same pose with time and angular overlap
    # share the same apex, so they must not be triangulated together.
    seqs = [
        _make_sequence(
            10, 48.3792, 2.8208, 180.0, 10.0, now - timedelta(seconds=9), now - timedelta(seconds=1), pose_id=42
        ),
        _make_sequence(
            11, 48.3792, 2.8208, 185.0, 10.0, now - timedelta(seconds=8), now - timedelta(seconds=2), pose_id=42
        ),
    ]
    df = compute_overlap(pd.DataFrame.from_records(seqs))

    row10 = df[df["id"] == 10].iloc[0]
    row11 = df[df["id"] == 11].iloc[0]
    assert row10["event_groups"] == [(10,)]
    assert row11["event_groups"] == [(11,)]
