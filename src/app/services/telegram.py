# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Union

import requests

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

__all__ = ["telegram_client"]


class TelegramClient:
    BASE_URL = "https://api.telegram.org/bot{token}"

    def __init__(self, token: Union[str, None] = None) -> None:
        self.is_enabled = isinstance(token, str)
        if isinstance(token, str):
            self.token = token
            # Validate token
            response = requests.get(
                f"{self.BASE_URL.format(token=self.token)}/getMe",
                timeout=1,
            )
            if response.status_code != 200:
                raise ValueError(f"Invalid Telegram Bot token: {response.text}")
            logger.info("Telegram notifications enabled")

    def has_channel_access(self, channel_id: str) -> bool:
        response = requests.get(
            f"{self.BASE_URL.format(token=self.token)}/getChat",
            json={"chat_id": channel_id},
            timeout=1,
        )
        return response.status_code == 200

    def notify(self, channel_id: str, message: str) -> requests.Response:
        response = requests.post(
            f"{self.BASE_URL.format(token=self.token)}/sendMessage",
            json={"chat_id": channel_id, "text": message},
            timeout=2,
        )
        if response.status_code != 200:
            logger.error(f"Failed to send message to Telegram: {response.text}")

        return response


telegram_client = TelegramClient(token=settings.TELEGRAM_TOKEN)
