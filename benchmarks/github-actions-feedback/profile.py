"""Run the full backend suite with coverage, phase timings and SQL timing/counts.

Usage: BASELINE_PYTHON profile.py SOURCE_ROOT LABEL OUTPUT_JSON [TEST_PATHS...]
Uses isolated PostgreSQL and Moto on ports 55435 and 5567.
"""

import collections
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root, label, output, *test_paths = sys.argv[1:]
root, output = Path(root).resolve(), Path(output).resolve()
pg_port = os.environ.get("FEEDBACK_BENCH_PG_PORT", "55435")
s3_port = os.environ.get("FEEDBACK_BENCH_S3_PORT", "5567")
pg_container = os.environ.get("FEEDBACK_BENCH_PG_CONTAINER", "ci-feedback-postgres")
os.environ.update({
    "COVERAGE_FILE": str(output.with_suffix(".coverage")),
    "SUPERADMIN_LOGIN": "benchmark", "SUPERADMIN_PWD": "benchmark-only", "SUPERADMIN_ORG": "benchmark",
    "POSTGRES_URL": f"postgresql+asyncpg://benchmark:benchmark-only@127.0.0.1:{pg_port}/benchmark",
    "S3_ACCESS_KEY": "benchmark", "S3_SECRET_KEY": "benchmark", "S3_REGION": "eu-west-3",
    "S3_ENDPOINT_URL": f"http://127.0.0.1:{s3_port}", "S3_PROXY_URL": "", "JWT_SECRET": "benchmark-only",
    "SENTRY_DSN": "", "POSTHOG_KEY": "", "TEMPORAL_API_URL": "", "RISK_API_URL": "", "SLACK_HOOK": "",
})
sys.path.insert(0, str(root / "src"))
os.chdir(root)
import boto3
import pytest
import requests
from botocore.exceptions import ClientError
from sqlalchemy import event
from app.db import engine

requests.post(f"http://127.0.0.1:{s3_port}/moto-api/reset", timeout=10).raise_for_status()
subprocess.run([
    "docker", "exec", pg_container, "psql", "-U", "benchmark", "-d", "benchmark",
    "-v", "ON_ERROR_STOP=1", "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;",
], check=True, capture_output=True)
s3 = boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT_URL"], aws_access_key_id="benchmark", aws_secret_access_key="benchmark", region_name="eu-west-3")
try:
    s3.head_bucket(Bucket="admin")
except ClientError:
    s3.create_bucket(Bucket="admin", CreateBucketConfiguration={"LocationConstraint": "eu-west-3"})

sql = collections.defaultdict(lambda: {"calls": 0, "seconds": 0.0})


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before(connection, cursor, statement, parameters, context, executemany):
    context._profile_started = time.perf_counter()


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after(connection, cursor, statement, parameters, context, executemany):
    kind = statement.split()[0].upper()
    if "pg_catalog" in statement:
        kind = "SCHEMA_INSPECTION"
    sql[kind]["calls"] += 1
    sql[kind]["seconds"] += time.perf_counter() - context._profile_started


class Profile:
    def __init__(self):
        self.reports = []

    def pytest_runtest_logreport(self, report):
        self.reports.append({"test": report.nodeid, "phase": report.when, "outcome": report.outcome, "seconds": report.duration})


profile = Profile()
start = time.perf_counter()
status = pytest.main([*(test_paths or [str(root / "src/tests")]), "-q", "--tb=short", "--durations=20", "--cov=app", f"--cov-report=xml:{output.with_suffix('.coverage.xml')}"], plugins=[profile])
elapsed = time.perf_counter() - start
summary = {
    "label": label, "source_root": str(root), "fixture_sha256": hashlib.sha256((root / "src/tests/conftest.py").read_bytes()).hexdigest(),
    "exit_code": int(status), "elapsed_seconds": elapsed,
    "outcomes": dict(collections.Counter(report["outcome"] for report in profile.reports if report["phase"] == "call" or report["outcome"] == "skipped")),
    "phase_seconds": {phase: sum(report["seconds"] for report in profile.reports if report["phase"] == phase) for phase in ["setup", "call", "teardown"]},
    "sql": dict(sql), "reports": profile.reports,
    "environment": "Python 3.11.15, locked main dependencies, PostgreSQL 15, Moto 5.2.3; full coverage enabled",
    "selection": test_paths or ["src/tests"],
}
output.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in ["label", "exit_code", "elapsed_seconds", "outcomes", "phase_seconds", "sql"]}, indent=2))
raise SystemExit(status)
