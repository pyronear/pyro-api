# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from __future__ import annotations

import itertools
import logging
from datetime import timedelta
from math import atan2, cos, radians, sin, sqrt
from statistics import median

import networkx as nx
from pyproj import Geod, Transformer
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform

from inference.schemas import SequenceRecord, SmokeLocation, TriangulationGroup

logger = logging.getLogger(__name__)

_GEOD = Geod(ellps="WGS84")
_TO_WEB_MERCATOR = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
_TO_GEOGRAPHIC = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return r_earth * 2 * atan2(sqrt(a), sqrt(1 - a))


def get_centroid_latlon(geom: BaseGeometry) -> tuple[float, float]:
    centroid = geom.centroid
    lon, lat = _TO_GEOGRAPHIC.transform(centroid.x, centroid.y)
    return float(lat), float(lon)


def _linspace(start: float, stop: float, count: int) -> list[float]:
    if count < 2:
        raise ValueError("count must be at least 2")
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def _destination(lat: float, lon: float, azimuth: float, distance_km: float) -> tuple[float, float]:
    destination_lon, destination_lat, _ = _GEOD.fwd(lon, lat, azimuth % 360, distance_km * 1000)
    return float(destination_lon), float(destination_lat)


def _build_cone_polygon(
    lat: float,
    lon: float,
    azimuth: float,
    opening_angle: float,
    dist_km: float,
    r_min_km: float,
    resolution: int = 36,
) -> Polygon:
    half_angle = opening_angle / 2.0
    angles = _linspace(azimuth - half_angle, azimuth + half_angle, resolution)
    outer_points = [_destination(lat, lon, angle, dist_km) for angle in angles]

    if r_min_km > 0:
        inner_points = [_destination(lat, lon, angle, r_min_km) for angle in reversed(angles)]
        return Polygon(outer_points + inner_points, holes=[inner_points]).buffer(0)
    return Polygon([(lon, lat), *outer_points]).buffer(0)


def get_projected_cone(sequence: SequenceRecord, r_km: float, r_min_km: float) -> Polygon:
    polygon = _build_cone_polygon(
        sequence.lat,
        sequence.lon,
        sequence.sequence_azimuth,
        sequence.cone_angle,
        r_km,
        r_min_km,
    )
    return shapely_transform(_TO_WEB_MERCATOR.transform, polygon)


def _is_degenerate_pair(apex_by_id: dict[int, tuple[float, float]], id1: int, id2: int, min_apex_km: float) -> bool:
    apex1 = apex_by_id.get(id1)
    apex2 = apex_by_id.get(id2)
    if apex1 is None or apex2 is None:
        return False
    return haversine_km(apex1[0], apex1[1], apex2[0], apex2[1]) < min_apex_km


def _compute_localized_groups_from_cliques(
    all_ids: set[int],
    cliques: list[tuple[int, ...]],
    projected_cones: dict[int, Polygon],
    max_dist_km: float,
    apex_by_id: dict[int, tuple[float, float]],
    min_apex_km: float,
) -> list[tuple[int, ...]]:
    base = [tuple(sorted(group)) for group in cliques]
    ids_in_cliques = {sequence_id for group in base for sequence_id in group}
    work = base + [(sequence_id,) for sequence_id in sorted(all_ids - ids_in_cliques)]

    def split_one_group(group: tuple[int, ...]) -> list[tuple[int, ...]]:
        group = tuple(sorted(group))
        if len(group) <= 1:
            return [group]

        pair_barycenters: list[tuple[float, float]] = []
        has_triangulable_pair = False
        for id1, id2 in itertools.combinations(group, 2):
            if _is_degenerate_pair(apex_by_id, id1, id2, min_apex_km):
                continue
            has_triangulable_pair = True
            cone1 = projected_cones.get(id1)
            cone2 = projected_cones.get(id2)
            if cone1 is None or cone2 is None:
                continue
            intersection = cone1.intersection(cone2)
            if intersection.is_empty or intersection.area <= 0:
                continue
            pair_barycenters.append(get_centroid_latlon(intersection))

        if len(group) == 2 or not has_triangulable_pair:
            return [group]
        if len(pair_barycenters) < 2:
            return [tuple(sorted(pair)) for pair in itertools.combinations(group, 2)]

        max_distance = max(
            (
                haversine_km(lat1, lon1, lat2, lon2)
                for (lat1, lon1), (lat2, lon2) in itertools.combinations(pair_barycenters, 2)
            ),
            default=0.0,
        )
        if max_distance <= max_dist_km:
            return [group]
        return [tuple(sorted(pair)) for pair in itertools.combinations(group, 2)]

    candidates = [group for clique in sorted(set(work)) for group in split_one_group(clique)]
    candidates = sorted({tuple(sorted(group)) for group in candidates})
    candidate_sets = [set(group) for group in candidates]
    return [
        candidates[index]
        for index, group in enumerate(candidate_sets)
        if not any(index != other and group.issubset(candidate_sets[other]) for other in range(len(candidate_sets)))
    ]


def _build_projected_cones(sequences: list[SequenceRecord], r_km: float, r_min_km: float) -> dict[int, Polygon]:
    projected_cones: dict[int, Polygon] = {}
    for sequence in sequences:
        try:
            projected_cones[sequence.id] = get_projected_cone(sequence, r_km, r_min_km)
        except Exception as exc:  # ruff:ignore[blind-except]
            logger.warning("Failed to build cone for sequence %s: %s", sequence.id, exc)
    return projected_cones


def _find_overlapping_pairs(
    sequences: list[SequenceRecord],
    projected_cones: dict[int, Polygon],
    time_relaxation_seconds: float,
) -> list[tuple[int, int]]:
    tolerance = timedelta(seconds=time_relaxation_seconds)
    overlapping_pairs: list[tuple[int, int]] = []
    for index, sequence1 in enumerate(sequences):
        cone1 = projected_cones.get(sequence1.id)
        if cone1 is None:
            continue
        for sequence2 in sequences[index + 1 :]:
            if (
                sequence1.started_at - sequence2.last_seen_at > tolerance
                or sequence2.started_at - sequence1.last_seen_at > tolerance
            ):
                continue
            cone2 = projected_cones.get(sequence2.id)
            if cone2 is not None and cone1.intersects(cone2):
                overlapping_pairs.append((sequence1.id, sequence2.id))
    return overlapping_pairs


def _build_overlap_cliques(overlapping_pairs: list[tuple[int, int]]) -> list[tuple[int, ...]]:
    graph = nx.Graph()
    graph.add_edges_from(overlapping_pairs)
    return [tuple(sorted(clique)) for clique in nx.find_cliques(graph) if len(clique) >= 2]


def _group_smoke_location(
    group: tuple[int, ...],
    projected_cones: dict[int, Polygon],
    apex_by_id: dict[int, tuple[float, float]],
    min_apex_km: float,
) -> tuple[float, float] | None:
    if len(group) < 2:
        return None
    points: list[tuple[float, float]] = []
    has_triangulable_pair = False
    for id1, id2 in itertools.combinations(group, 2):
        if _is_degenerate_pair(apex_by_id, id1, id2, min_apex_km):
            continue
        has_triangulable_pair = True
        cone1 = projected_cones.get(id1)
        cone2 = projected_cones.get(id2)
        if cone1 is None or cone2 is None:
            continue
        intersection = cone1.intersection(cone2)
        if intersection.is_empty or intersection.area <= 0:
            continue
        points.append(get_centroid_latlon(intersection))

    if not points:
        if not has_triangulable_pair:
            return None
        polygons = [polygon for sequence_id in group if (polygon := projected_cones.get(sequence_id)) is not None]
        if not polygons:
            return None
        try:
            merged: BaseGeometry = polygons[0]
            for polygon in polygons[1:]:
                merged = merged.union(polygon)
            return get_centroid_latlon(merged)
        except Exception as exc:  # ruff:ignore[blind-except]
            logger.warning("Failed fallback centroid for group %s: %s", group, exc)
            return None

    latitudes, longitudes = zip(*points, strict=False)
    return float(median(latitudes)), float(median(longitudes))


def compute_overlap(
    sequences: list[SequenceRecord],
    *,
    r_km: float = 35.0,
    r_min_km: float = 0.5,
    max_dist_km: float = 2.0,
    time_relaxation_seconds: float = 30 * 60,
    min_apex_km: float = 0.1,
) -> list[TriangulationGroup]:
    valid_sequences = [sequence for sequence in sequences if sequence.is_wildfire in (None, "wildfire_smoke")]
    if not valid_sequences:
        return [TriangulationGroup(sequence_ids=[sequence.id], smoke_location=None) for sequence in sequences]

    projected_cones = _build_projected_cones(valid_sequences, r_km, r_min_km)
    apex_by_id = {sequence.id: (sequence.lat, sequence.lon) for sequence in valid_sequences}
    overlapping_pairs = _find_overlapping_pairs(valid_sequences, projected_cones, time_relaxation_seconds)
    localized_groups = _compute_localized_groups_from_cliques(
        {sequence.id for sequence in sequences},
        _build_overlap_cliques(overlapping_pairs),
        projected_cones,
        max_dist_km,
        apex_by_id,
        min_apex_km,
    )
    return [
        TriangulationGroup(
            sequence_ids=list(group),
            smoke_location=(
                SmokeLocation(lat=location[0], lon=location[1])
                if (location := _group_smoke_location(group, projected_cones, apex_by_id, min_apex_km))
                else None
            ),
        )
        for group in localized_groups
    ]
