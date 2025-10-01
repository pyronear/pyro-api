# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from __future__ import annotations

import itertools
from collections import defaultdict
from math import atan2, cos, radians, sin, sqrt
from typing import Dict, List, Optional, Tuple

import networkx as nx  # type: ignore
import numpy as np
import pandas as pd
import pyproj
from geopy.distance import geodesic
from pyproj import Transformer
from shapely.geometry import Polygon  # type: ignore
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform  # type: ignore


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


def _project_polygon_to_3857(polygon: Polygon) -> Polygon:
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
        Row with fields: lat, lon, cone_azimuth, cone_angle.
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
        float(row["cone_azimuth"]),
        float(row["cone_angle"]),
        float(r_km),
        float(r_min_km),
    )
    return _project_polygon_to_3857(poly)


def _compute_localized_groups_from_cliques(
    df: pd.DataFrame,
    cliques: List[Tuple[int, ...]],
    projected_cones: Dict[int, Polygon],
    max_dist_km: float,
) -> List[Tuple[int, ...]]:
    """
    From maximal cliques, split each clique into localized groups.

    Rules
    -----
    For groups with size at least three, keep the whole group if the maximum distance
    among all pair intersection barycenters is within max_dist_km. Otherwise split the
    clique into all two by two pairs.

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
        for i, j in itertools.combinations(group, 2):
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


def compute_overlap(
    api_sequences: pd.DataFrame,
    r_km: float = 35.0,
    r_min_km: float = 0.5,
    max_dist_km: float = 2.0,
) -> pd.DataFrame:
    """
    Build localized event groups and attach them to the input DataFrame.

    This function sets two columns on the returned DataFrame:
      event_groups: list of tuples of sequence ids
      event_smoke_locations: list of (lat, lon), same order as event_groups

    Parameters
    ----------
    api_sequences : pd.DataFrame
        Input with fields: id, lat, lon, cone_azimuth, cone_angle, is_wildfire,
        started_at, last_seen_at.
    r_km : float
        Outer radius of the camera detection cone in kilometers.
    r_min_km : float
        Inner radius of the camera detection cone in kilometers.
    max_dist_km : float
        Maximum allowed distance between pair intersection barycenters to keep a group.

    Returns
    -------
    pd.DataFrame
        DataFrame copy including event_groups and event_smoke_locations columns.
    """
    df = api_sequences.copy()
    df["id"] = df["id"].astype(int)
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["last_seen_at"] = pd.to_datetime(df["last_seen_at"])

    # keep positives and unknowns
    df_valid = df[df["is_wildfire"].isin([None, "wildfire_smoke"])]

    if df_valid.empty:
        df["event_groups"] = df["id"].astype(int).map(lambda sid: [(sid,)])
        df["event_smoke_locations"] = [[] for _ in range(len(df))]
        return df

    # Precompute cones in Web Mercator
    projected_cones: Dict[int, Polygon] = {
        int(row["id"]): get_projected_cone(row, r_km, r_min_km) for _, row in df_valid.iterrows()
    }

    # Phase 1, build overlap graph gated by time overlap
    ids = df_valid["id"].astype(int).tolist()
    rows_by_id: Dict[int, Dict[str, pd.Timestamp]] = df_valid.set_index("id")[["started_at", "last_seen_at"]].to_dict(
        "index"
    )

    overlapping_pairs: List[Tuple[int, int]] = []
    for i, id1 in enumerate(ids):
        row1 = rows_by_id[id1]
        for id2 in ids[i + 1 :]:
            row2 = rows_by_id[id2]
            # Require overlapping time windows
            if row1["started_at"] > row2["last_seen_at"] or row2["started_at"] > row1["last_seen_at"]:
                continue
            # Spatial overlap test
            if projected_cones[id1].intersects(projected_cones[id2]):
                overlapping_pairs.append((id1, id2))

    graph = nx.Graph()
    graph.add_edges_from(overlapping_pairs)
    cliques = [tuple(sorted(c)) for c in nx.find_cliques(graph) if len(c) >= 2]

    # Phase 2, localized groups from cliques
    localized_groups = _compute_localized_groups_from_cliques(df, cliques, projected_cones, max_dist_km)

    # Per group localization, median of pair barycenters for robustness
    def group_smoke_location(seq_tuple: Tuple[int, ...]) -> Optional[Tuple[float, float]]:
        if len(seq_tuple) < 2:
            return None
        pts: List[Tuple[float, float]] = []
        for i, j in itertools.combinations(seq_tuple, 2):
            inter = projected_cones[i].intersection(projected_cones[j])
            if inter.is_empty or inter.area <= 0:
                continue
            pts.append(get_centroid_latlon(inter))
        if not pts:
            return None
        lats, lons = zip(*pts)
        return float(np.median(lats)), float(np.median(lons))

    group_to_smoke: Dict[Tuple[int, ...], Optional[Tuple[float, float]]] = {
        g: group_smoke_location(g) for g in localized_groups
    }

    # Attach back to df
    seq_to_groups: Dict[int, List[Tuple[int, ...]]] = defaultdict(list)
    seq_to_smokes: Dict[int, List[Optional[Tuple[float, float]]]] = defaultdict(list)
    for g in localized_groups:
        smo = group_to_smoke[g]
        for sid in g:
            seq_to_groups[sid].append(g)
            seq_to_smokes[sid].append(smo)

    df["event_groups"] = df["id"].astype(int).map(lambda sid: seq_to_groups.get(sid, [(sid,)]))
    df["event_smoke_locations"] = df["id"].astype(int).map(lambda sid: seq_to_smokes.get(sid, []))

    return df
