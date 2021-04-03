# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List
from sqlalchemy import select

from app.api.crud import database
from app.db import webhooks


async def fetch_webhook_urls(route: str) -> List[str]:

    query = (
        select([webhooks.c.url])
        .where(webhooks.c.callback == route)
    )

    return await database.fetch_all(query=query)
