# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timezone


def utcnow() -> datetime:
    """UTC wall clock, returned as a naive datetime to match existing DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
