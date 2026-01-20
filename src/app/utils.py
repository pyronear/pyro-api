# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import UTC, datetime

__all__ = ["utc_now"]


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
