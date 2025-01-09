# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime

from pydantic import BaseModel

__all__ = ["StreamUpdate"]


# Accesses
class StreamUpdate(BaseModel):
    last_seen_at: datetime
