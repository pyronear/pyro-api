# Copyright (C) 2026, Pyronear.
# Licensed under the Apache License 2.0; see LICENSE.
"""Isolated benchmark settings: never connect to configured production services."""

import importlib
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(os.environ["PYRO_BENCH_REPO"]).expanduser().resolve()
sys.path.insert(0, str(ROOT / "src"))


def configure() -> None:
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


def load_storage():
    # S3Service probes its backend on import. Replace only that startup client;
    # individual benchmark cases supply their own local bucket/client afterward.
    with patch("boto3.Session.client") as client:
        client.return_value.list_buckets.return_value = {"Buckets": []}
        return importlib.import_module("app.services.storage")


configure()
# app.services.__init__ eagerly imports storage even for geometric services.
# Intercept that one startup probe before any app.services import occurs.
load_storage()
