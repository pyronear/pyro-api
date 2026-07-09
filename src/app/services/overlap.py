# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from __future__ import annotations

import itertools
import logging
from collections import defaultdict
from datetime import timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd
import pyproj
from geopy.distance import geodesic
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform

from app.core.config import settings

logger = logging.getLogger(__name__)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the great circle distance between two points on the Earth surface using the Haversine formula.

    Parameters
    ----------
    lat1 : float
        Latitude of point 1 in decimal degrees.
    lon1 : float
        Longitude of point 1 in decimal degrees.
    lat2 : float
        Latitude of point 2 in decimal degrees.
    lon2 : float
        Longitude of point 2 in decimal degrees.

    Returns
    -------
    float
        Distance between the two points in kilometers.
    """
    r_earth = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r_earth * c


def get_centroid_latlon(geom: BaseGeometry) -> Tuple[float, float]:
    """
    Compute the geographic coordinates of the centroid of a given geometry.

    Parameters
    ----------
    geom : BaseGeometry
        Geometry in EPSG:3857 (Web Mercator projection).

    Returns
    -------
    tuple[float, float]
        Latitude and longitude of the centroid in EPSG:4326.
    """
    centroid = geom.centroid
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(centroid.x, centroid.y)
    return float(lat), float(lon)


def _build_cone_polygon(
    lat: float,
    lon: float,
    azimuth: float,
    opening_angle: float,
    dist_km: float,
    r_min_km: float,
    resolution: int = 36,
) -> Polygon:
    """
    Build a cone sector polygon on the sphere then return it in geographic coordinates.

    Parameters
    ----------
    lat : float
        Camera latitude.
    lon : float
        Camera longitude.
    azimuth : float
        Cone central azimuth in degrees.
    opening_angle : float
        Full opening angle in degrees.
    dist_km : float
        Outer radius in kilometers.
    r_min_km : float
        Inner radius in kilometers.
    resolution : int
        Number of points to sample the arc.

    Returns
    -------
    shapely.geometry.Polygon
        Cone polygon in EPSG:4326 coordinates.
    """
    half_angle = opening_angle / 2.0
    angles = np.linspace(azimuth - half_angle, azimuth + half_angle, resolution)

    # Outer arc points
    outer_arc = [geodesic(kilometers=dist_km).destination((lat, lon), float(az % 360)) for az in angles]
    outer_points = [(p.longitude, p.latitude) for p in outer_arc]

    if r_min_km > 0:
        # Inner arc points, walk reversed so ring orientation stays valid
        inner_arc = [geodesic(kilometers=r_min_km).destination((lat, lon), float(az % 360)) for az in reversed(angles)]
        inner_points = [(p.longitude, p.latitude) for p in inner_arc]
        # Outer ring with a hole for the inner radius
        return Polygon(outer_points + inner_points, holes=[inner_points]).buffer(0)
    # Triangle like sector with apex at camera position
    return Polygon([(lon, lat), *outer_points]).buffer(0)


def _project_polygon_from_4326_to_3857(polygon: Polygon) -> Polygon:
    """
    Project a polygon from EPSG:4326 to EPSG:3857.

    Parameters
    ----------
    polygon : Polygon
        Geometry in EPSG:4326.

    Returns
    -------
    Polygon
        Geometry in EPSG:3857.
    """
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    return shapely_transform(transformer.transform, polygon)


def get_projected_cone(row: pd.Series, r_km: float, r_min_km: float) -> Polygon:
    """
    Build and project a detection cone to Web Mercator.

    Parameters
    ----------
    row : pd.Series
        Row with fields: lat, lon, sequence_azimuth, cone_angle.
    r_km : float
        Outer radius of the camera detection cone in kilometers.
    r_min_km : float
        Inner radius of the camera detection cone in kilometers.

    Returns
    -------
    Polygon
        Cone geometry in EPSG:3857.
    """
    poly = _build_cone_polygon(
        float(row["lat"]),
        float(row["lon"]),
        float(row["sequence_azimuth"]),
        float(row["cone_angle"]),
        float(r_km),
        float(r_min_km),
    )
    return _project_polygon_from_4326_to_3857(poly)


def _build_apex_by_id(df_valid: pd.DataFrame) -> Dict[int, Tuple[float, float]]:
    return {int(row["id"]): (float(row["lat"]), float(row["lon"])) for _, row in df_valid.iterrows()}


def _is_degenerate_pair(
    apex_by_id: Dict[int, Tuple[float, float]],
    id1: int,
    id2: int,
    min_apex_km: float,
) -> bool:
    """Cameras (nearly) sharing an apex see the same event but their cone intersection
    carries no range information: such pairs must not contribute to any location math."""
    apex1 = apex_by_id.get(id1)
    apex2 = apex_by_id.get(id2)
    if apex1 is None or apex2 is None:
        return False
    return haversine_km(apex1[0], apex1[1], apex2[0], apex2[1]) < min_apex_km


def _compute_localized_groups_from_cliques(
    df: pd.DataFrame,
    cliques: List[Tuple[int, ...]],
    projected_cones: Dict[int, Polygon],
    max_dist_km: float,
    apex_by_id: Dict[int, Tuple[float, float]],
    min_apex_km: float,
) -> List[Tuple[int, ...]]:
    """
    From maximal cliques, split each clique into localized groups.

    Rules
    -----
    For groups with size at least three, keep the whole group if the maximum distance
    among all pair intersection barycenters is within max_dist_km. Otherwise split the
    clique into all two by two pairs. Pairs of cameras closer than min_apex_km are
    degenerate (no triangulation) and are ignored when collecting barycenters.

    Parameters
    ----------
    df : pd.DataFrame
        Source sequences, must contain column id.
    cliques : list[tuple[int, ...]]
        Maximal cliques computed from the overlap graph.
    projected_cones : dict[int, Polygon]
        Mapping from sequence id to its cone geometry in EPSG:3857.
    max_dist_km : float
        Maximum allowed distance between pair barycenters to keep a group.
    apex_by_id : dict[int, tuple[float, float]]
        Mapping from sequence id to its camera (lat, lon).
    min_apex_km : float
        Minimum apex distance for a pair to count as a triangulation.

    Returns
    -------
    list[tuple[int, ...]]
        Unique localized groups as sorted tuples, with strict subsets removed.
    """
    base = [tuple(sorted(g)) for g in cliques]
    ids_in_cliques = {x for g in base for x in g}
    all_ids = set(df["id"].astype(int).tolist())
    work = base + [(sid,) for sid in sorted(all_ids - ids_in_cliques)]

    def split_one_group(group: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        group = tuple(sorted(group))
        if len(group) <= 1:
            return [group]

        # Collect pairwise intersection barycenters
        pair_barys: List[Tuple[float, float]] = []
        has_triangulable_pair = False
        for i, j in itertools.combinations(group, 2):
            if _is_degenerate_pair(apex_by_id, i, j, min_apex_km):
                continue
            has_triangulable_pair = True
            gi = projected_cones.get(i)
            gj = projected_cones.get(j)
            if gi is None or gj is None:
                continue
            inter = gi.intersection(gj)
            if inter.is_empty or inter.area <= 0:
                continue
            pair_barys.append(get_centroid_latlon(inter))

        if len(group) == 2:
            return [group]

        if not has_triangulable_pair:
            # Every pair shares an apex (multi-camera mast): one event, nothing to localize
            return [group]

        if len(pair_barys) < 2:
            # Not enough info to validate locality, fall back to all pairs
            return [tuple(sorted(p)) for p in itertools.combinations(group, 2)]

        # Diameter of barycenters
        max_d = 0.0
        for (lat1, lon1), (lat2, lon2) in itertools.combinations(pair_barys, 2):
            d = haversine_km(lat1, lon1, lat2, lon2)
            if d > max_d:
                max_d = d

        if max_d <= max_dist_km:
            return [group]
        return [tuple(sorted(p)) for p in itertools.combinations(group, 2)]

    # Build candidate groups from all cliques
    candidates: List[Tuple[int, ...]] = []
    for clique in sorted(set(work)):
        candidates.extend(split_one_group(clique))

    # Remove exact duplicates
    candidates = sorted({tuple(sorted(g)) for g in candidates})

    # Drop strict subsets of any other group
    keep: List[Tuple[int, ...]] = []
    as_sets = [set(g) for g in candidates]
    for i, gi in enumerate(as_sets):
        if any(i != j and gi.issubset(as_sets[j]) for j in range(len(as_sets))):
            continue
        keep.append(candidates[i])

    return keep


def _prepare_sequences_df(api_sequences: pd.DataFrame) -> pd.DataFrame:
    df = api_sequences.copy()
    df["id"] = df["id"].astype(int)
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["last_seen_at"] = pd.to_datetime(df["last_seen_at"])
    return df


def _filter_valid_sequences(df: pd.DataFrame) -> pd.DataFrame:
    # Keep positives and unknowns
    return df[df["is_wildfire"].isin([None, "wildfire_smoke"])]


def _build_projected_cones(df_valid: pd.DataFrame, r_km: float, r_min_km: float) -> Dict[int, Polygon]:
    projected_cones: Dict[int, Polygon] = {}
    for _, row in df_valid.iterrows():
        sid = int(row["id"])
        try:
            projected_cones[sid] = get_projected_cone(row, r_km, r_min_km)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to build cone for sequence %s: %s", sid, exc)
    return projected_cones


def _find_overlapping_pairs(
    df_valid: pd.DataFrame,
    projected_cones: Dict[int, Polygon],
    time_relaxation_seconds: Optional[float] = None,
) -> List[Tuple[int, int]]:
    if time_relaxation_seconds is None:
        time_relaxation_seconds = settings.TRIANGULATION_RELAXATION_SECONDS
    ids = df_valid["id"].astype(int).tolist()
    cols = ["started_at", "last_seen_at"]
    rows_by_id: Dict[int, Dict[str, Any]] = df_valid.set_index("id")[cols].to_dict("index")
    # `_attach_sequence_to_alert` runs when the validation worker validates a sequence,
    # which can be early in its life (a few frames in) while prior sequences' windows
    # haven't been bumped yet. Treat any pair within `time_relaxation_seconds` of each
    # other as concurrent so we don't drop them before the spatial test.
    # Near-apex pairs (same pose or same mast) are kept as grouping evidence — they see
    # the same event — but are excluded from location math downstream.
    tolerance = timedelta(seconds=time_relaxation_seconds)
    overlapping_pairs: List[Tuple[int, int]] = []
    for i, id1 in enumerate(ids):
        row1 = rows_by_id[id1]
        for id2 in ids[i + 1 :]:
            row2 = rows_by_id[id2]
            if (
                row1["started_at"] - row2["last_seen_at"] > tolerance
                or row2["started_at"] - row1["last_seen_at"] > tolerance
            ):
                continue
            # Spatial overlap test
            if projected_cones[id1].intersects(projected_cones[id2]):
                overlapping_pairs.append((id1, id2))
    return overlapping_pairs


def _build_overlap_cliques(overlapping_pairs: List[Tuple[int, int]]) -> List[Tuple[int, ...]]:
    graph = nx.Graph()
    graph.add_edges_from(overlapping_pairs)
    return [tuple(sorted(c)) for c in nx.find_cliques(graph) if len(c) >= 2]


def _group_smoke_location(
    seq_tuple: Tuple[int, ...],
    projected_cones: Dict[int, Polygon],
    apex_by_id: Dict[int, Tuple[float, float]],
    min_apex_km: float,
) -> Optional[Tuple[float, float]]:
    if len(seq_tuple) < 2:
        return None
    pts: List[Tuple[float, float]] = []
    has_triangulable_pair = False
    for i, j in itertools.combinations(seq_tuple, 2):
        if _is_degenerate_pair(apex_by_id, i, j, min_apex_km):
            continue
        has_triangulable_pair = True
        gi = projected_cones.get(i)
        gj = projected_cones.get(j)
        if gi is None or gj is None:
            continue
        inter = gi.intersection(gj)
        if inter.is_empty or inter.area <= 0:
            continue
        pts.append(get_centroid_latlon(inter))
    if not pts:
        if not has_triangulable_pair:
            # Same-mast group: one event, but no pair carries range information
            logger.debug("Group %s only has near-apex pairs, no location computed", seq_tuple)
            return None
        # No intersections: use centroid of available cones as best-effort location
        polys: List[BaseGeometry] = [p for p in (projected_cones.get(sid) for sid in seq_tuple) if p is not None]
        if not polys:
            return None
        try:
            merged: BaseGeometry = polys[0]
            for p in polys[1:]:
                merged = merged.union(p)
            return get_centroid_latlon(merged)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed fallback centroid for group %s: %s", seq_tuple, exc)
            return None
    lats, lons = zip(*pts, strict=False)
    return float(np.median(lats)), float(np.median(lons))


def _attach_groups_to_df(
    df: pd.DataFrame,
    localized_groups: List[Tuple[int, ...]],
    group_to_smoke: Dict[Tuple[int, ...], Optional[Tuple[float, float]]],
) -> None:
    seq_to_groups: Dict[int, List[Tuple[int, ...]]] = defaultdict(list)
    seq_to_smokes: Dict[int, List[Optional[Tuple[float, float]]]] = defaultdict(list)
    for g in localized_groups:
        smo = group_to_smoke[g]
        for sid in g:
            seq_to_groups[sid].append(g)
            seq_to_smokes[sid].append(smo)
    df["event_groups"] = df["id"].astype(int).map(lambda sid: seq_to_groups.get(sid, [(sid,)]))
    df["event_smoke_locations"] = df["id"].astype(int).map(lambda sid: seq_to_smokes.get(sid, []))


def compute_overlap(
    api_sequences: pd.DataFrame,
    r_km: float = 35.0,
    r_min_km: float = 0.5,
    max_dist_km: float = 2.0,
    time_relaxation_seconds: Optional[float] = None,
    min_apex_km: Optional[float] = None,
) -> pd.DataFrame:
    """
    Build localized event groups and attach them to the input DataFrame.

    This function sets two columns on the returned DataFrame:
      event_groups: list of tuples of sequence ids
      event_smoke_locations: list of (lat, lon), same order as event_groups

    Parameters
    ----------
    api_sequences : pd.DataFrame
        Input with fields: id, lat, lon, sequence_azimuth, cone_angle, is_wildfire,
        started_at, last_seen_at.
    r_km : float
        Outer radius of the camera detection cone in kilometers.
    r_min_km : float
        Inner radius of the camera detection cone in kilometers.
    max_dist_km : float
        Maximum allowed distance between pair intersection barycenters to keep a group.
    time_relaxation_seconds : float, optional
        Tolerance applied to the time-window overlap check between two sequences. Pairs
        whose windows are within this slack of each other are still considered concurrent.
        Defaults to ``settings.TRIANGULATION_RELAXATION_SECONDS``.
    min_apex_km : float, optional
        Camera pairs closer than this share an apex: they still group together but are
        excluded from location computation. Defaults to
        ``settings.TRIANGULATION_MIN_APEX_DISTANCE_KM``.

    Returns
    -------
    pd.DataFrame
        DataFrame copy including event_groups and event_smoke_locations columns.
    """
    df = _prepare_sequences_df(api_sequences)
    df_valid = _filter_valid_sequences(df)

    if df_valid.empty:
        df["event_groups"] = df["id"].astype(int).map(lambda sid: [(sid,)])
        df["event_smoke_locations"] = [[] for _ in range(len(df))]
        return df

    if min_apex_km is None:
        min_apex_km = settings.TRIANGULATION_MIN_APEX_DISTANCE_KM

    # Precompute cones in Web Mercator
    projected_cones = _build_projected_cones(df_valid, r_km, r_min_km)
    apex_by_id = _build_apex_by_id(df_valid)

    # Phase 1, build overlap graph gated by time overlap
    overlapping_pairs = _find_overlapping_pairs(df_valid, projected_cones, time_relaxation_seconds)
    cliques = _build_overlap_cliques(overlapping_pairs)

    # Phase 2, localized groups from cliques
    localized_groups = _compute_localized_groups_from_cliques(
        df, cliques, projected_cones, max_dist_km, apex_by_id, min_apex_km
    )

    # Per group localization, median of pair barycenters for robustness
    group_to_smoke: Dict[Tuple[int, ...], Optional[Tuple[float, float]]] = {
        g: _group_smoke_location(g, projected_cones, apex_by_id, min_apex_km) for g in localized_groups
    }

    # Attach back to df
    _attach_groups_to_df(df, localized_groups, group_to_smoke)

    return df
