# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timezone


def utcnow() -> datetime:
    """UTC wall clock, returned as a naive datetime to match existing DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(value: datetime) -> datetime:
    """Normalize a datetime to naive UTC, matching how DB columns store time.

    A timezone-aware value (e.g. ``2026-05-27T10:00:00+02:00`` from a French engine) is
    converted to UTC before the tzinfo is dropped, so it lands at ``08:00:00``. A naive value
    is assumed to already be UTC and returned unchanged.
    """
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
