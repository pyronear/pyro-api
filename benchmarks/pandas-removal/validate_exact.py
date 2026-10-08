"""Exact output and ORM-caller validation. Run with a pandas-capable baseline Python.

Usage: python validate_exact.py CANDIDATE_ROOT BASE_ROOT REPORT_JSON
BASE_ROOT must contain the pre-removal source; neither tree is changed by this script.
"""

import asyncio
import importlib.util
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

report_path = Path(sys.argv.pop())
import validate_extended  # Runs all 147 adversarial cases with exact validation.
import validate
from workloads import SCENARIOS, sequences

with patch("boto3.Session.client"):
    from app.api.api_v1.endpoints import detections
    from app.models import Alert, AnnotationType, Camera, Sequence
    from app.schemas.alerts import AlertRead
    from app.services import alerts
from fastapi.responses import JSONResponse


def load_baseline(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, Path(validate.base_root) / relative_path)
    module = importlib.util.module_from_spec(spec)
    with patch("boto3.Session.client"):
        spec.loader.exec_module(module)
    module.compute_overlap = validate.parent.compute_overlap
    return module


old_detections = load_baseline("old_detections", "src/app/api/api_v1/endpoints/detections.py")
old_alerts = load_baseline("old_alerts", "src/app/services/alerts.py")

for scenario, size in [
    ("sparse", 3),
    ("sparse", 30),
    ("sparse", 300),
    ("clustered", 300),
    ("dense", 30),
    ("mast", 100),
    ("time_separated", 300),
]:
    validate.compare(sequences(size, scenario))

for scenario in SCENARIOS:
    for seed in range(20):
        rng = random.Random(seed)
        records = sequences([0, 1, 3, 6, 12][seed % 5], scenario, seed)
        rng.shuffle(records)
        for row in records:
            row["lat"] += (seed % 5 - 2) * 15
            row["lon"] += (seed % 7 - 3) * 20
            row["started_at"] += timedelta(microseconds=rng.randrange(1000000))
            row["last_seen_at"] += timedelta(microseconds=rng.randrange(1000000))
            row["is_wildfire"] = rng.choice([None, *AnnotationType])
        validate.compare(records, time_relaxation_seconds=[0, 30, 1800][seed % 3])


def orm_rows(records):
    rows = []
    for row in records:
        seq = Sequence(
            id=row["id"],
            camera_id=row["id"],
            pose_id=row["pose_id"],
            camera_azimuth=0,
            sequence_azimuth=row["sequence_azimuth"],
            cone_angle=row["cone_angle"],
            is_wildfire=AnnotationType(row["is_wildfire"]) if row["is_wildfire"] else None,
            started_at=row["started_at"],
            last_seen_at=row["last_seen_at"],
            is_validated=True,
        )
        cam = Camera(
            id=row["id"],
            organization_id=1,
            name=f"camera-{row['id']}",
            angle_of_view=60,
            elevation=100,
            lat=row["lat"],
            lon=row["lon"],
            created_at=datetime(2026, 10, 3),
        )
        rows.append((seq, cam))
    return rows


class AlertStore:
    """Capture CRUD payload bytes and render resulting alerts using the API schema."""

    def __init__(self, initial=None):
        self.items = {} if initial is None else {initial.id: initial}
        self.events = []

    async def create(self, payload):
        aid = 1000 + len(self.items)
        self.events.append(("create", aid, payload.model_dump_json().encode()))
        self.items[aid] = Alert(id=aid, **payload.model_dump())
        return self.items[aid]

    async def get(self, aid, **kwargs):
        return self.items[aid]

    async def update(self, aid, payload):
        self.events.append(("update", aid, payload.model_dump_json().encode()))
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(self.items[aid], key, value)
        return self.items[aid]

    async def delete(self, aid):
        self.events.append(("delete", aid, b""))
        del self.items[aid]

    def response_bytes(self):
        return JSONResponse([
            AlertRead.model_validate(item, from_attributes=True).model_dump(mode="json") for item in self.items.values()
        ]).body


def existing_alert(rows):
    start = min((seq.started_at for seq, _ in rows), default=datetime(2026, 10, 3))
    last = max((seq.last_seen_at for seq, _ in rows), default=start)
    return Alert(id=500, organization_id=1, lat=43.125, lon=-4.25, started_at=start, last_seen_at=last)


async def attach(module, rows, use_existing):
    store = AlertStore(existing_alert(rows) if use_existing else None)
    if not rows:
        return None, [], [], store.response_bytes()
    mapping = [(500, seq.id) for seq, _ in rows] if use_existing else []
    session = SimpleNamespace(exec=AsyncMock(return_value=mapping), add_all=Mock(), commit=AsyncMock())
    seq_crud = SimpleNamespace(session=session, fetch_all=AsyncMock(return_value=[seq for seq, _ in rows]))
    cam_crud = SimpleNamespace(fetch_all=AsyncMock(return_value=[cam for _, cam in rows]))
    aid = await module._attach_sequence_to_alert(rows[0][0], rows[0][1], cam_crud, seq_crud, store, True)
    links = [link.model_dump_json().encode() for call in session.add_all.call_args_list for link in call.args[0]]
    return aid, store.events, links, store.response_bytes()


async def refresh(module, rows):
    store = AlertStore(existing_alert(rows))
    session = SimpleNamespace(exec=AsyncMock(return_value=SimpleNamespace(all=lambda: rows)))
    await module.refresh_alert_state(500, session, store)
    return store.events, store.response_bytes()


def resolved_bytes(result):
    # Tuple-keyed mappings are encoded as ordered entries, preserving all output order.
    value = None if result is None else [result[0], list(result[1].items())]
    return json.dumps(value, separators=(",", ":"), allow_nan=False).encode()


cases = [orm_rows(sequences(size, scenario)) for scenario in SCENARIOS for size in [0, 1, 3, 12, 30]]
for label in [None, *AnnotationType]:
    for scenario in SCENARIOS:
        records = sequences(3, scenario)
        for row in records:
            row["is_wildfire"] = label
            row["started_at"] += timedelta(microseconds=123456)
            row["last_seen_at"] += timedelta(microseconds=987654)
        cases.append(orm_rows(records))
for field in ["sequence_azimuth", "cone_angle", "pose_id"]:
    for all_rows in [False, True]:
        rows = orm_rows(sequences(3, "dense"))
        for seq, _ in rows if all_rows else rows[:1]:
            setattr(seq, field, None)
        cases.append(rows)
for all_rows in [False, True]:
    rows = orm_rows(sequences(3, "dense"))
    for seq, _ in rows if all_rows else rows[:1]:
        seq.is_validated = False
    cases.append(rows)
for gap in [0, 0.000001, 30, 30.000001, 1800, 1800.000001]:
    rows = orm_rows(sequences(3, "dense"))
    for idx, (seq, _) in enumerate(rows):
        seq.started_at = seq.last_seen_at = datetime(2026, 10, 3, 12, 0, 0, 123456) + timedelta(seconds=gap * idx)
    cases.append(rows)


async def callers():
    resolve_checks = attach_checks = refresh_checks = 0
    for rows in cases:
        seqs, cams = [seq for seq, _ in rows], {cam.id: cam for _, cam in rows}
        # Include a missing camera in the record builder's filter path.
        for cam_map in [cams, dict(list(cams.items())[1:])]:
            expected_records = old_detections._build_overlap_records(seqs, cam_map)
            actual_records = detections._build_overlap_records(seqs, cam_map)
            assert actual_records == expected_records
            for sid in [seqs[0].id if seqs else 1, seqs[-1].id if seqs else 1, 999999]:
                expected = old_detections._resolve_groups_and_locations(expected_records, sid)
                actual = detections._resolve_groups_and_locations(actual_records, sid)
                assert resolved_bytes(actual) == resolved_bytes(expected)
                resolve_checks += 1
        if rows:
            for use_existing in [False, True]:
                assert await attach(detections, rows, use_existing) == await attach(old_detections, rows, use_existing)
                attach_checks += 1
        assert await refresh(alerts, rows) == await refresh(old_alerts, rows)
        refresh_checks += 1
    return dict(resolve=resolve_checks, attach=attach_checks, refresh=refresh_checks)


report = {
    "overlap_cases": validate.checks,
    "bit_identical_location_pairs": validate.location_pairs,
    "overlap_output_bytes": validate.output_bytes,
    "orm_scenarios": len(cases),
    "caller_comparisons": asyncio.run(callers()),
    "mismatches": 0,
    "numeric_tolerance": 0,
    "baseline_output_sha256": validate.expected_digest.hexdigest(),
    "candidate_output_sha256": validate.actual_digest.hexdigest(),
    "compared": [
        "ordered IDs/groups/locations",
        "float64 bits",
        "CRUD payload bytes",
        "alert link bytes",
        "AlertRead JSONResponse bytes",
    ],
    "external_io": "DB/CRUD/S3 boundaries mocked; real ORM models, geometry, production callers and API serializers",
}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
