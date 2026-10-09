"""Run equivalent baseline/shards on one four-CPU host with one PostgreSQL and S3 service."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import boto3
import requests

directory = Path(__file__).resolve().parent
root = Path(sys.argv[1]).resolve() / "src"
environment = {
    **os.environ, "PYTHONPATH": str(root), "SUPERADMIN_LOGIN": "benchmark", "SUPERADMIN_PWD": "benchmark-only", "SUPERADMIN_ORG": "benchmark",
    "S3_ACCESS_KEY": "benchmark", "S3_SECRET_KEY": "benchmark", "S3_REGION": "eu-west-3", "S3_ENDPOINT_URL": "http://127.0.0.1:5567",
    "S3_PROXY_URL": "", "JWT_SECRET": "benchmark-only", "SENTRY_DSN": "", "POSTHOG_KEY": "", "TEMPORAL_API_URL": "", "RISK_API_URL": "", "SLACK_HOOK": "",
}
requests.post("http://127.0.0.1:5567/moto-api/reset", timeout=10).raise_for_status()
boto3.client("s3", endpoint_url=environment["S3_ENDPOINT_URL"], aws_access_key_id="benchmark", aws_secret_access_key="benchmark", region_name="eu-west-3").create_bucket(Bucket="admin", CreateBucketConfiguration={"LocationConstraint": "eu-west-3"})
selected = [f"tests/endpoints/test_{name}.py" for name in ("detections", "sequences", "camera_proxy", "temporal_validation")]


def environment_for(label):
    return {**environment, "POSTGRES_URL": f"postgresql+asyncpg://benchmark:benchmark-only@127.0.0.1:55435/{label}", "SERVER_NAME": f"ci-{label}"}


def start(label, paths):
    log = (directory / f"{label}.log").open("w")
    command = [sys.executable, str(directory / "run_suite.py"), label, str(directory / f"{label}.json"), *paths]
    return subprocess.Popen(command, cwd=root, env=environment_for(label), stdout=log, stderr=subprocess.STDOUT), log


for label in ("baseline", "api", "remaining"):
    subprocess.run(["docker", "exec", "ci-feedback-shared-postgres", "createdb", "-U", "benchmark", label], check=True)
    with (directory / f"{label}-init.log").open("w") as init_log:
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=root, env=environment_for(label), stdout=init_log, stderr=subprocess.STDOUT, check=True)
        subprocess.run([sys.executable, "app/db.py"], cwd=root, env=environment_for(label), stdout=init_log, stderr=subprocess.STDOUT, check=True)
started = time.perf_counter()
process, log = start("baseline", ["tests/"])
baseline_status = process.wait()
log.close()
baseline_seconds = time.perf_counter() - started
print(json.dumps({"baseline_seconds": baseline_seconds, "exit_code": baseline_status}), flush=True)
started = time.perf_counter()
processes = [start("api", selected), start("remaining", ["tests/", *(f"--ignore={path}" for path in selected)])]
codes = []
for process, log in processes:
    codes.append(process.wait())
    log.close()
result = {"baseline_process_seconds": baseline_seconds, "parallel_process_seconds": time.perf_counter() - started, "baseline_exit_code": baseline_status, "parallel_exit_codes": codes}
(directory / "comparison-wall.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result), flush=True)
raise SystemExit(baseline_status or any(codes))
