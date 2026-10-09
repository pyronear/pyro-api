"""Check test outcomes, a disjoint partition, and exact combined line coverage."""

import collections
import json
from pathlib import Path
import xml.etree.ElementTree as ET

directory = Path(__file__).resolve().parent
profiles = {name: json.loads((directory / f"{name}.json").read_text()) for name in ("baseline", "api", "remaining")}


def outcomes(profile):
    reports = [r for r in profile["reports"] if r["phase"] == "call" or r["outcome"] == "skipped"]
    assert len(reports) == len({r["test"] for r in reports})
    assert collections.Counter(r["outcome"] for r in reports) == profile["outcomes"]
    return {r["test"]: r["outcome"] for r in reports}


def coverage(name):
    valid, covered = set(), set()
    for cls in ET.parse(directory / f"{name}.coverage.xml").findall(".//class"):
        for line in cls.findall("./lines/line"):
            location = (cls.attrib["filename"], int(line.attrib["number"]))
            valid.add(location)
            if int(line.attrib["hits"]) > 0:
                covered.add(location)
    return valid, covered


assert all(p["exit_code"] == 0 for p in profiles.values())
assert len({p["fixture_sha256"] for p in profiles.values()}) == 1
baseline, api, remaining = [outcomes(profiles[name]) for name in profiles]
assert not api.keys() & remaining.keys()
assert baseline == api | remaining
baseline_valid, baseline_covered = coverage("baseline")
api_valid, api_covered = coverage("api")
remaining_valid, remaining_covered = coverage("remaining")
assert baseline_valid == api_valid | remaining_valid
assert baseline_covered == api_covered | remaining_covered
wall = json.loads((directory / "comparison-wall.json").read_text())
summary = {
    **wall,
    "process_wall_reduction_percent": 100 * (1 - wall["parallel_process_seconds"] / wall["baseline_process_seconds"]),
    "cases": len(baseline), "api_cases": len(api), "remaining_cases": len(remaining),
    "outcomes": {name: p["outcomes"] for name, p in profiles.items()},
    "covered_lines_baseline": len(baseline_covered), "covered_lines_shards": len(api_covered | remaining_covered),
    "missing_or_duplicate_tests": 0, "changed_test_outcomes": 0, "lost_covered_lines": 0,
}
(directory / "verified-comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
