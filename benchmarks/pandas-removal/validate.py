"""Compare consumed output bytes against the baseline, without numeric tolerances."""

import importlib.util
import hashlib
import json
import random
import struct
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from run import setup
from workloads import SCENARIOS, sequences

candidate_root, base_root = sys.argv[1:]
setup(candidate_root)
with patch("boto3.Session.client"):
    from app.services.overlap import compute_overlap
spec = importlib.util.spec_from_file_location("pandas_overlap", Path(base_root) / "src/app/services/overlap.py")
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
import pandas as pd

checks = 0
location_pairs = 0
output_bytes = 0
expected_digest = hashlib.sha256()
actual_digest = hashlib.sha256()


def serialize(rows):
    # Preserve row, group and location order. These are the fields both callers consume.
    return json.dumps(
        [{key: row[key] for key in ("id", "event_groups", "event_smoke_locations")} for row in rows],
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compare(records, **options):
    global checks, location_pairs, output_bytes
    frame = pd.DataFrame.from_records(records)
    if not records:
        frame = pd.DataFrame(
            columns=["id", "lat", "lon", "sequence_azimuth", "cone_angle", "is_wildfire", "started_at", "last_seen_at"]
        )
    expected = parent.compute_overlap(frame, **options).to_dict("records")
    actual = compute_overlap(records, **options)
    expected_bytes = serialize(expected)
    actual_bytes = serialize(actual)
    assert actual_bytes == expected_bytes, (records, options, expected_bytes, actual_bytes)
    expected_digest.update(struct.pack("!Q", len(expected_bytes)) + expected_bytes)
    actual_digest.update(struct.pack("!Q", len(actual_bytes)) + actual_bytes)
    for a, b in zip(actual, expected, strict=True):
        assert len(a["event_smoke_locations"]) == len(b["event_smoke_locations"])
        for x, y in zip(a["event_smoke_locations"], b["event_smoke_locations"], strict=True):
            if x is None or y is None:
                assert x is y
            else:
                # Also verify IEEE-754 bits, including the sign of zero.
                assert struct.pack("!dd", *x) == struct.pack("!dd", *y)
                location_pairs += 1
    checks += 1
    output_bytes += len(actual_bytes)


for scenario in SCENARIOS:
    for size in [0, 1, 3, 10, 30]:
        compare(sequences(size, scenario))
    for seed in range(10):
        records = sequences(12, scenario, seed)
        random.Random(seed).shuffle(records)
        for row in records:
            row["id"] *= 11
        compare(records, max_dist_km=0.01, min_apex_km=0, time_relaxation_seconds=0)
for tz in [None, timezone.utc]:
    for relaxation in [0, 30, 1800]:
        records = sequences(3, "mast")
        for row, delta in zip(records, [0, relaxation, relaxation + 0.001], strict=True):
            row["started_at"] = row["last_seen_at"] = datetime(2026, 10, 3, tzinfo=tz) + timedelta(seconds=delta)
        compare(records, time_relaxation_seconds=relaxation)
for label in [None, "wildfire_smoke", "other"]:
    for invalid in [None, "not a number"]:
        records = sequences(3, "dense")
        records[0]["sequence_azimuth"] = invalid
        for row in records:
            row["is_wildfire"] = label
        compare(records)
for label in [None, "wildfire_smoke", "other"]:
    records = sequences(3, "dense")
    records[1]["is_wildfire"] = label
    records[2]["is_wildfire"] = "wildfire_smoke"
    compare(records)
print(
    f"{checks} byte-for-byte comparisons passed ({location_pairs} bit-identical location pairs, {output_bytes} bytes)"
)
