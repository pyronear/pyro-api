# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime, timedelta, timezone

import pytest
from shapely.geometry import Polygon

from inference import overlap
from inference.overlap import compute_overlap
from inference.schemas import SequenceRecord


def _make_sequence(
    id_: int,
    lat: float,
    lon: float,
    sequence_azimuth: float,
    cone_angle: float,
    started_at: datetime,
    last_seen_at: datetime,
    is_wildfire: str | None = None,
    pose_id: int | None = None,
) -> SequenceRecord:
    return SequenceRecord(
        id=id_,
        pose_id=pose_id if pose_id is not None else id_,
        lat=lat,
        lon=lon,
        sequence_azimuth=sequence_azimuth,
        cone_angle=cone_angle,
        is_wildfire=is_wildfire,
        started_at=started_at,
        last_seen_at=last_seen_at,
    )


def _group_for(sequence_id: int, groups):
    return next(group for group in groups if sequence_id in group.sequence_ids)


def test_compute_overlap_groups_and_locations() -> None:
    now = datetime.now(timezone.utc)
    sequences = [
        _make_sequence(1, 48.3792, 2.8208, 276.5, 3.0, now - timedelta(seconds=9), now - timedelta(seconds=1)),
        _make_sequence(2, 48.2605, 2.7064, 8.3, 0.8, now - timedelta(seconds=8), now - timedelta(seconds=2)),
        _make_sequence(3, 48.4267, 2.7109, 163.4, 1.0, now - timedelta(seconds=7), now - timedelta(seconds=3)),
        _make_sequence(4, 10.0, 10.0, 90.0, 1.0, now - timedelta(seconds=6), now - timedelta(seconds=4)),
    ]

    groups = compute_overlap(sequences)

    assert _group_for(1, groups).sequence_ids == [1, 2, 3]
    assert _group_for(1, groups).smoke_location is not None
    assert _group_for(4, groups).sequence_ids == [4]
    assert _group_for(4, groups).smoke_location is None


def test_compute_overlap_time_relaxation_recovers_just_started_pair() -> None:
    now = datetime.now(timezone.utc)
    sequences = [
        _make_sequence(20, 48.3792, 2.8208, 276.5, 3.0, now - timedelta(seconds=30), now - timedelta(seconds=30)),
        _make_sequence(21, 48.4267, 2.7109, 163.4, 1.0, now, now),
    ]

    assert [group.sequence_ids for group in compute_overlap(sequences, time_relaxation_seconds=0)] == [[20], [21]]
    assert [group.sequence_ids for group in compute_overlap(sequences)] == [[20, 21]]


def test_compute_overlap_groups_same_pose_pair_without_location() -> None:
    now = datetime.now(timezone.utc)
    sequences = [
        _make_sequence(10, 48.3792, 2.8208, 180.0, 10.0, now, now, pose_id=42),
        _make_sequence(11, 48.3792, 2.8208, 185.0, 10.0, now, now, pose_id=42),
    ]

    group = _group_for(10, compute_overlap(sequences))

    assert group.sequence_ids == [10, 11]
    assert group.smoke_location is None


def test_compute_overlap_groups_same_mast_pair_without_location() -> None:
    now = datetime.now(timezone.utc)
    sequences = [
        _make_sequence(30, 48.4267, 2.7109, 100.0, 2.0, now, now),
        _make_sequence(31, 48.4268, 2.7110, 101.0, 2.0, now, now),
    ]

    group = _group_for(30, compute_overlap(sequences))

    assert group.sequence_ids == [30, 31]
    assert group.smoke_location is None


def test_compute_overlap_mixed_group_locates_from_triangulable_pairs_only() -> None:
    now = datetime.now(timezone.utc)
    sequences = [
        _make_sequence(40, 48.4267, 2.7109, 163.4, 1.0, now, now),
        _make_sequence(41, 48.4267, 2.7109, 163.4, 1.0, now, now),
        _make_sequence(42, 48.2605, 2.7064, 8.3, 0.8, now, now),
    ]

    group = _group_for(40, compute_overlap(sequences))

    assert group.sequence_ids == [40, 41, 42]
    assert group.smoke_location is not None
    assert 48.26 < group.smoke_location.lat < 48.43


def test_compute_overlap_handles_empty_and_dateline_inputs() -> None:
    now = datetime.now(timezone.utc)
    assert compute_overlap([]) == []

    groups = compute_overlap([
        _make_sequence(50, 0.0, 179.9, 90.0, 10.0, now, now),
        _make_sequence(51, 0.0, -179.9, 270.0, 10.0, now, now),
    ])
    assert {sequence_id for group in groups for sequence_id in group.sequence_ids} == {50, 51}


def test_overlap_defensive_geometry_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.now(timezone.utc)
    sequence = _make_sequence(60, 0.0, 0.0, 90.0, 10.0, now, now)

    with pytest.raises(ValueError, match="at least 2"):
        overlap._linspace(0.0, 1.0, 1)
    assert not overlap._build_cone_polygon(0.0, 0.0, 90.0, 10.0, 35.0, 0.0).is_empty
    assert not overlap._is_degenerate_pair({}, 1, 2, 0.1)

    def reject_cone(*_args) -> None:
        raise ValueError("invalid cone")

    monkeypatch.setattr(overlap, "get_projected_cone", reject_cone)
    assert overlap._build_projected_cones([sequence], 35.0, 0.5) == {}
    assert overlap._find_overlapping_pairs([sequence], {}, 30.0) == []

    apex_by_id = {1: (0.0, 0.0), 2: (1.0, 1.0)}
    assert overlap._group_smoke_location((1, 2), {}, apex_by_id, 0.1) is None

    polygons = {
        1: Polygon([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]),
        2: Polygon([(2.0, 2.0), (3.0, 2.0), (2.0, 3.0)]),
    }
    assert overlap._group_smoke_location((1, 2), polygons, apex_by_id, 0.1) is not None
