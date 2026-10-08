"""Verify the retained timezone dependency and fallback in a disposable process.

Usage: CANDIDATE_PYTHON validate_timezones.py CANDIDATE_ROOT BASE_ROOT REPORT_JSON
"""

import importlib.metadata
import json
import sys
import tomllib
import zoneinfo
from pathlib import Path

import pytz
from packaging.markers import Marker
from packaging.requirements import Requirement

candidate, baseline, report_path = map(Path, sys.argv[1:])
old_lock = tomllib.loads((baseline / "uv.lock").read_text())
new_lock = tomllib.loads((candidate / "uv.lock").read_text())
old_packages = {p["name"]: p for p in old_lock["package"]}
new_packages = {p["name"]: p for p in new_lock["package"]}
old_marker = Marker(next(d["marker"] for d in old_packages["pandas"]["dependencies"] if d["name"] == "tzdata"))
new_project = tomllib.loads((candidate / "pyproject.toml").read_text())
new_requirement = next(Requirement(d) for d in new_project["dependency-groups"]["server"] if d.startswith("tzdata"))
platforms = {}
for platform in ["linux", "darwin", "win32", "emscripten"]:
    before = old_marker.evaluate({"sys_platform": platform})
    after = new_requirement.marker.evaluate({"sys_platform": platform})
    assert before == after
    platforms[platform] = after
assert old_packages["tzdata"]["version"] == new_packages["tzdata"]["version"]
assert sys.platform == "linux"
assert zoneinfo.ZoneInfo("Europe/Paris").key == "Europe/Paris"
try:
    importlib.metadata.version("tzdata")
except importlib.metadata.PackageNotFoundError:
    pass
else:
    raise AssertionError("Linux candidate unexpectedly includes tzdata")

system_paths = list(zoneinfo.TZPATH)
zoneinfo.reset_tzpath(())
zoneinfo.ZoneInfo.clear_cache()
assert pytz.timezone("Europe/Paris").zone == "Europe/Paris"
try:
    zoneinfo.ZoneInfo("Europe/Paris")
except zoneinfo.ZoneInfoNotFoundError:
    fallback_result = "ZoneInfoNotFoundError despite installed pytz"
else:
    raise AssertionError("Unexpected zoneinfo fallback")

report = {
    "baseline_transitive_dependency": str(old_marker),
    "candidate_direct_dependency": str(new_requirement),
    "same_platform_marker_behavior": platforms,
    "same_locked_version": new_packages["tzdata"]["version"],
    "linux_tzdata_installed": False,
    "system_paths": system_paths,
    "linux_zoneinfo_lookup": "success using system data",
    "lookup_without_system_data": fallback_result,
}
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
