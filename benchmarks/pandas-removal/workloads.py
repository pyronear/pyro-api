import random
from datetime import datetime, timedelta

from pyproj import Geod

SCENARIOS = ("sparse", "clustered", "dense", "mast", "time_separated", "mixed_labels")


def sequences(size, scenario, seed=20261003):
    rng = random.Random(seed)
    geod = Geod(ellps="WGS84")
    now = datetime(2026, 10, 3, 12)
    rows = []
    for idx in range(size):
        site = 0 if scenario in {"dense", "mast"} else idx // 3 if scenario == "clustered" else idx
        target_lat = 43.0 + (site // 20) * 0.9
        target_lon = -4.0 + (site % 20) * 1.1
        bearing = (idx % 3) * 120 if scenario == "clustered" else rng.uniform(0, 360)
        distance = 10000 + rng.uniform(-1000, 1000)
        if scenario == "mast":
            bearing, distance = 0, 10000
        lon, lat, _ = geod.fwd(target_lon, target_lat, bearing, distance)
        azimuth, _, _ = geod.inv(lon, lat, target_lon, target_lat)
        start = now - timedelta(minutes=idx * 45 if scenario == "time_separated" else rng.randrange(5))
        rows.append({
            "id": idx + 1,
            "pose_id": idx + 1,
            "lat": lat,
            "lon": lon,
            "sequence_azimuth": azimuth % 360,
            "cone_angle": 2.0 if scenario == "dense" else 5.0,
            "is_wildfire": "other" if scenario == "mixed_labels" and idx % 3 else None,
            "started_at": start,
            "last_seen_at": start + timedelta(seconds=10),
        })
    return rows
