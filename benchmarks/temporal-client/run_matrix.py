# Copyright (C) 2026, Pyronear.
# Licensed under the Apache License 2.0; see LICENSE.
"""Reproduce the frozen-source matrix and refresh raw data and medians together."""

import argparse
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path

folder = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--repeats", type=int, default=5)
parser.add_argument("--count", type=int, default=100)
parser.add_argument("--scenarios", nargs="+", default=["serial", "concurrent8", "server_close", "https", "model50ms"])
parser.add_argument("--cert", default=str(folder / "benchmark.crt"))
parser.add_argument("--key", default=str(folder / "benchmark.key"))
parser.add_argument("--output", default=str(folder / "reproduced_results.jsonl"))
args = parser.parse_args()
sources = {"baseline": folder / "baseline_temporal.py", "reused": folder / "updated_temporal.py"}
cases = [(rep, scenario, variant) for rep in range(args.repeats) for scenario in args.scenarios for variant in sources]
random.Random(705707).shuffle(cases)
rows = []
with Path(args.output).open("w") as result_file:
    for idx, (rep, scenario, variant) in enumerate(cases):
        cmd = [sys.executable, str(folder / "temporal_client.py"), "--source", str(sources[variant]),
               "--variant", variant, "--scenario", scenario, "--count", str(args.count),
               "--cert", args.cert, "--key", args.key]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=90)
        row = json.loads(result.stdout)
        row.update(rep=rep, order=idx)
        rows.append(row)
        result_file.write(json.dumps(row) + "\n")
        result_file.flush()
        print(f"{idx + 1}/{len(cases)} {scenario} {variant}: p50 {row['p50_ms']:.2f} ms", flush=True)

metrics = ["cold_ms", "p50_ms", "p95_ms", "batch_ms", "python_peak_kib", "rss_before_kib", "rss_after_kib", "process_peak_kib", "timed_connections"]
summary = {scenario: {variant: {key: statistics.median(row[key] for row in rows if row["scenario"] == scenario and row["variant"] == variant) for key in metrics} for variant in sources} for scenario in args.scenarios}
Path(args.output).with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
