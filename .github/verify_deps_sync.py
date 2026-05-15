# Copyright (C) 2025-2026, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///

import logging
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

DOCKERFILES = ["src/Dockerfile", "src/Dockerfile.test"]
PRECOMMIT_CONFIG = ".pre-commit-config.yaml"
PYPROJECTS = ["./pyproject.toml", "./client/pyproject.toml"]
TRACKED_DEPS = ("uv", "ruff", "ty", "prek")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(levelname)s:     %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


def parse_dep_str(dep_str: str) -> dict[str, str]:
    dep = dep_str.split(";", maxsplit=1)[0].strip()
    if " @ " in dep:
        pkg, version = dep.split(" @ ", maxsplit=1)
        return {"pkg": pkg.strip(), "version": version.strip()}

    version_match = re.search(r"(===|==|~=|!=|<=|>=|<|>).*$", dep)
    version_idx = version_match.start() if version_match else len(dep)
    pkg = dep[:version_idx].strip()
    pkg = pkg.split("[", maxsplit=1)[0].strip()
    return {"pkg": pkg, "version": dep[version_idx:].strip()}


def add_dep(deps: dict[str, list[dict[str, str]]], dep: str, file: str, group: str) -> None:
    parsed = parse_dep_str(dep)
    pkg = parsed["pkg"].lower()
    if pkg in deps and parsed["version"]:
        deps[pkg].append({"file": file, "version": parsed["version"], "group": group})


def add_pyproject_deps(deps: dict[str, list[dict[str, str]]], pyproject_path: str) -> None:
    with Path(pyproject_path).open("rb") as f:
        pyproject: dict[str, Any] = tomllib.load(f)

    project = pyproject.get("project", {})
    if isinstance(project, dict):
        dependencies = project.get("dependencies", [])
        if isinstance(dependencies, list):
            for dep in dependencies:
                add_dep(deps, dep, pyproject_path, "[project.dependencies]")

        optional_dependencies = project.get("optional-dependencies", {})
        if isinstance(optional_dependencies, dict):
            for group, dependencies in optional_dependencies.items():
                if isinstance(dependencies, list):
                    for dep in dependencies:
                        add_dep(deps, dep, pyproject_path, f"[project.optional-dependencies.{group}]")

    dependency_groups = pyproject.get("dependency-groups", {})
    if isinstance(dependency_groups, dict):
        for group, dependencies in dependency_groups.items():
            if isinstance(dependencies, list):
                for dep in dependencies:
                    add_dep(deps, dep, pyproject_path, f"[dependency-groups.{group}]")


def main() -> None:
    deps: dict[str, list[dict[str, str]]] = {dep: [] for dep in TRACKED_DEPS}

    for dockerfile in DOCKERFILES:
        dockerfile_content = Path(dockerfile).read_text(encoding="utf-8")
        uv_versions = re.findall(r"ghcr\.io/astral-sh/uv:(\d+\.\d+\.\d+)", dockerfile_content)
        deps["uv"].extend({"file": dockerfile, "version": f"=={version}", "group": "docker"} for version in uv_versions)

    if Path(PRECOMMIT_CONFIG).exists():
        with Path(PRECOMMIT_CONFIG).open("r", encoding="utf-8") as f:
            precommit = yaml.safe_load(f)
        for repo in precommit.get("repos", []):
            repo_url = repo.get("repo")
            if repo_url == "https://github.com/astral-sh/uv-pre-commit":
                deps["uv"].append({
                    "file": PRECOMMIT_CONFIG,
                    "version": f"=={repo['rev'].lstrip('v')}",
                    "group": "pre-commit",
                })
            elif repo_url == "https://github.com/charliermarsh/ruff-pre-commit":
                deps["ruff"].append({
                    "file": PRECOMMIT_CONFIG,
                    "version": f"=={repo['rev'].lstrip('v')}",
                    "group": "pre-commit",
                })

    for pyproject_path in PYPROJECTS:
        add_pyproject_deps(deps, pyproject_path)

    for workflow_file in Path(".github/workflows").glob("*.yml"):
        with workflow_file.open("r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f) or {}
        env = workflow.get("env", {})
        if "UV_VERSION" in env:
            deps["uv"].append({
                "file": str(workflow_file),
                "version": f"=={env['UV_VERSION'].lstrip('v')}",
                "group": "workflow",
            })

    troubles = []
    for dep, versions in deps.items():
        if not versions:
            troubles.append(f"{dep}: no tracked version found")
            continue

        version_values = {entry["version"] for entry in versions}
        if len(version_values) > 1:
            inv_dict = {version: set() for version in version_values}
            for version in versions:
                inv_dict[version["version"]].add(f"{version['file']} {version['group']}")
            troubles.extend([
                f"{dep}:",
                "\n".join(f"- {version}: {', '.join(sorted(files))}" for version, files in sorted(inv_dict.items())),
            ])

    if troubles:
        raise AssertionError("Some dependencies are out of sync:\n\n" + "\n".join(troubles))
    logger.info("All dependencies are in sync!")


if __name__ == "__main__":
    main()
