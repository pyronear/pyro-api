"""Run the proposed shards concurrently with isolated PostgreSQL, S3 and coverage."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

directory = Path(__file__).resolve().parent
python = sys.executable
root = sys.argv[1]
selected = [f"src/tests/endpoints/test_{name}.py" for name in ("detections", "sequences", "camera_proxy", "temporal_validation")]
processes = []
started = time.perf_counter()
for label, paths, overrides in (
    ("api", selected, {}),
    ("remaining", ["src/tests/", *(f"--ignore={path}" for path in selected)], {
        "FEEDBACK_BENCH_PG_PORT": "55436", "FEEDBACK_BENCH_S3_PORT": "5568", "FEEDBACK_BENCH_PG_CONTAINER": "ci-feedback-postgres-2",
    }),
):
    log = (directory / f"{label}.log").open("w")
    command = [python, str(directory / "profile.py"), root, label, str(directory / f"{label}.json"), *paths]
    processes.append((label, subprocess.Popen(command, env={**os.environ, **overrides}, stdout=log, stderr=subprocess.STDOUT), log))
results = {}
for label, process, log in processes:
    results[label] = process.wait()
    log.close()
summary = {"wall_seconds": time.perf_counter() - started, "exit_codes": results}
(directory / "parallel.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
raise SystemExit(any(results.values()))
