"""Record an unchanged pytest invocation and covered source lines in an owned CI stack."""

import collections
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import pytest

label, output, *selection = sys.argv[1:]
output = Path(output)
os.environ["COVERAGE_FILE"] = str(output.with_suffix(".coverage"))


class Reports:
    def __init__(self):
        self.reports = []

    def pytest_runtest_logreport(self, report):
        self.reports.append({"test": report.nodeid, "phase": report.when, "outcome": report.outcome, "seconds": report.duration})


reports = Reports()
started = time.perf_counter()
status = pytest.main([*selection, "--cov=app", f"--cov-report=xml:{output.with_suffix('.coverage.xml')}", "--durations=15"], plugins=[reports])
result = {
    "label": label, "elapsed_seconds": time.perf_counter() - started, "exit_code": int(status),
    "outcomes": dict(collections.Counter(r["outcome"] for r in reports.reports if r["phase"] == "call" or r["outcome"] == "skipped")),
    "fixture_sha256": hashlib.sha256(Path("tests/conftest.py").read_bytes()).hexdigest(),
    "selection": selection, "reports": reports.reports,
}
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("label", "elapsed_seconds", "outcomes", "exit_code")}))
raise SystemExit(status)
