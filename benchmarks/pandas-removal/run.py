"""Fresh-process comparison of #706 and the Python-record replacement.

Usage: python run.py BASE_ROOT CANDIDATE_ROOT OUTPUT_DIR
Both roots need .venv with matching Python and locked server/test/quality deps.
"""

import gc
import json
import os
import random
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch


def setup(root):
    os.environ.update({
        "SUPERADMIN_LOGIN": "benchmark",
        "SUPERADMIN_PWD": "benchmark-only",
        "SUPERADMIN_ORG": "benchmark",
        "POSTGRES_URL": "sqlite+aiosqlite:///:memory:",
        "S3_ACCESS_KEY": "benchmark",
        "S3_SECRET_KEY": "benchmark",
        "S3_REGION": "us-east-1",
        "S3_ENDPOINT_URL": "http://127.0.0.1:1",
        "S3_PROXY_URL": "",
        "JWT_SECRET": "benchmark-only",
        "SENTRY_DSN": "",
        "POSTHOG_KEY": "",
        "TEMPORAL_API_URL": "",
        "RISK_API_URL": "",
        "SLACK_HOOK": "",
    })
    sys.path.insert(0, str(Path(root) / "src"))


def child(root, variant, scenario, size):
    setup(root)
    start = time.perf_counter()
    with patch("boto3.Session.client"):
        import app.main
    import_ms = (time.perf_counter() - start) * 1000
    import_peak_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    from app.services.overlap import compute_overlap
    from workloads import sequences

    records = sequences(size, scenario)
    if variant == "pandas":
        import pandas as pd

        def call():
            return compute_overlap(pd.DataFrame.from_records(records))

    else:
        assert not any(name == "pandas" or name.startswith("pandas.") for name in sys.modules)

        def call():
            return compute_overlap(records)

    call()
    gc.collect()
    times = []
    for _ in range(7):
        start = time.perf_counter()
        call()
        times.append((time.perf_counter() - start) * 1000)
    return dict(
        variant=variant,
        scenario=scenario,
        size=size,
        times_ms=times,
        median_ms=statistics.median(times),
        import_ms=import_ms,
        import_peak_kib=import_peak_kib,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )


def matrix(base, candidate, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    cases = [
        (scenario, size)
        for scenario, size in [
            ("sparse", 3),
            ("sparse", 30),
            ("sparse", 300),
            ("clustered", 300),
            ("dense", 30),
            ("mast", 100),
            ("time_separated", 300),
        ]
    ]
    jobs = [
        (root, variant, scenario, size, trial)
        for root, variant in [(base, "pandas"), (candidate, "records")]
        for scenario, size in cases
        for trial in range(5)
    ]
    random.Random(706).shuffle(jobs)
    raw = []
    with (output / "raw.jsonl").open("w") as file:
        for root, variant, scenario, size, trial in jobs:
            cmd = [
                str(Path(root) / ".venv/bin/python"),
                str(Path(__file__).resolve()),
                "--child",
                root,
                variant,
                scenario,
                str(size),
            ]
            completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
            result = {**json.loads(completed.stdout), "trial": trial}
            raw.append(result)
            file.write(json.dumps(result) + "\n")
            file.flush()
            print(
                f"{variant} {scenario}/{size} trial={trial}: {result['median_ms']:.2f}ms, {result['peak_rss_kib'] / 1024:.2f}MiB",
                flush=True,
            )
    summary = []
    for scenario, size in cases:
        row = dict(scenario=scenario, size=size)
        for variant in ["pandas", "records"]:
            runs = [r for r in raw if (r["variant"], r["scenario"], r["size"]) == (variant, scenario, size)]
            row[variant] = {
                metric: statistics.median(r[metric] for r in runs)
                for metric in ["median_ms", "import_ms", "import_peak_kib", "peak_rss_kib"]
            }
        row["time_saved_pct"] = (1 - row["records"]["median_ms"] / row["pandas"]["median_ms"]) * 100
        row["rss_saved_pct"] = (1 - row["records"]["peak_rss_kib"] / row["pandas"]["peak_rss_kib"]) * 100
        summary.append(row)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "--child":
        print(json.dumps(child(*sys.argv[2:5], int(sys.argv[5]))))
    else:
        matrix(*sys.argv[1:])
