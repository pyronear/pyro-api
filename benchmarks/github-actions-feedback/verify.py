"""Compare completed baseline and shard profiles, including line coverage."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

directory = Path(__file__).resolve().parent
baseline, api, remaining = [json.loads((directory / f"{label}.json").read_text()) for label in ("baseline", "api", "remaining")]


def test_ids(profile):
    # Service URLs become parametrized test IDs; normalize only the isolated S3 port.
    return {report["test"].replace("http://127.0.0.1:5568", "http://127.0.0.1:5567") for report in profile["reports"]}


def coverage(label):
    tree = ET.parse(directory / f"{label}.coverage.xml")
    valid, covered = set(), set()
    for cls in tree.findall(".//class"):
        for line in cls.findall("./lines/line"):
            location = (cls.attrib["filename"], int(line.attrib["number"]))
            valid.add(location)
            if int(line.attrib["hits"]) > 0:
                covered.add(location)
    return valid, covered


assert all(profile["exit_code"] == 0 for profile in (baseline, api, remaining))
assert test_ids(baseline) == test_ids(api) | test_ids(remaining)
assert not test_ids(api) & test_ids(remaining)
assert baseline["fixture_sha256"] == api["fixture_sha256"] == remaining["fixture_sha256"]
for profile in (baseline, api, remaining):
    calls = [report["test"] for report in profile["reports"] if report["phase"] == "call"]
    assert len(calls) == len(set(calls))
baseline_valid, baseline_covered = coverage("baseline")
api_valid, api_covered = coverage("api")
remaining_valid, remaining_covered = coverage("remaining")
assert baseline_valid == api_valid | remaining_valid
assert baseline_covered == api_covered | remaining_covered
summary = {
    "baseline_seconds": baseline["elapsed_seconds"],
    "parallel_seconds": max(api["elapsed_seconds"], remaining["elapsed_seconds"]),
    "reduction_percent": 100 * (1 - max(api["elapsed_seconds"], remaining["elapsed_seconds"]) / baseline["elapsed_seconds"]),
    "tests": len(test_ids(baseline)), "api_tests": len(test_ids(api)), "remaining_tests": len(test_ids(remaining)),
    "outcomes": {profile["label"]: profile["outcomes"] for profile in (baseline, api, remaining)},
    "baseline_covered_lines": len(baseline_covered), "shards_covered_lines": len(api_covered | remaining_covered),
    "lost_covered_lines": 0,
}
(directory / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
