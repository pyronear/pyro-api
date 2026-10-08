"""Run the original 105 comparisons plus 42 adversarial cases."""

from datetime import datetime, timedelta, timezone

# Importing validate runs its original 105 cases using the two CLI roots.
import validate
from app.models import AnnotationType
from workloads import sequences

initial_checks = validate.checks

for label in AnnotationType:
    records = sequences(3, "dense")
    for row in records:
        row["is_wildfire"] = label
    validate.compare(records)

for field in ["sequence_azimuth", "cone_angle"]:
    for idx in range(3):
        records = sequences(3, "dense")
        records[idx][field] = None
        validate.compare(records)
    records = sequences(3, "dense")
    for row in records:
        row[field] = None
    validate.compare(records)

for scenario in ["dense", "mast", "sparse", "mixed_labels"]:
    records = sequences(3, scenario)
    records[1]["id"] = records[0]["id"]
    validate.compare(records)
    records[2]["id"] = str(records[2]["id"])
    validate.compare(records)

for offset in [-3, 0, 5]:
    records = sequences(3, "dense")
    for row in records:
        row["started_at"] = row["started_at"].replace(tzinfo=timezone(timedelta(hours=offset)))
        row["last_seen_at"] = row["last_seen_at"].replace(tzinfo=timezone(timedelta(hours=offset)))
    validate.compare(records)

for relaxation in [0, 0.000001, 0.0000005, 30]:
    for gap in [0, 0.000001, 0.000002, 30, 30.000001]:
        records = sequences(3, "dense")
        now = datetime(2026, 10, 3, 12, 0, 0, 123456)
        for idx, row in enumerate(records):
            row["started_at"] = row["last_seen_at"] = now + timedelta(seconds=idx * gap)
        validate.compare(records, time_relaxation_seconds=relaxation)

assert validate.checks - initial_checks == 42
print(f"{validate.checks} extended differential comparisons passed")
