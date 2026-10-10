# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Annotated

from pydantic import Field

# Keep the established create minimum and the database's VARCHAR(100) capacity.
ResourceName = Annotated[str, Field(min_length=3, max_length=100)]
