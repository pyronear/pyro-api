# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from sqlalchemy import select

from app.api import crud
from app.db import webhooks


async def fetch_webhook_urls(route: str) -> List[str]:

    query = select([webhooks.c.url]).where(webhooks.c.callback == route)

    return await crud.base.database.fetch_all(query=query)
