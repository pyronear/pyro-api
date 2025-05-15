# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import json
import logging

import requests

logger = logging.getLogger("uvicorn.error")

__all__ = ["slack_client"]


class SlackClient:
    def __init__(self) -> None:
        self.is_enabled = True
        # Do we want a config in settings ?

    def has_channel_access(self, slack_hook: str) -> bool:
        if not self.is_enabled:
            raise AssertionError("Slack notifications are not enabled")

        """Envoie un message à Slack via un webhook."""
        response = requests.post(
            slack_hook,
            json={"text": "Initialisation du Slack Hook in the Pyronear API"},
            headers={"Content-Type": "application/json"},
            timeout=3,
        )

        return response.status_code == 200

    def notify(self, slack_hook: str, message: str) -> requests.Response:
        if not self.is_enabled:
            raise AssertionError("Slack notifications are not enabled")

        message = {"text": f"Nouvel détection reçue :\n```{json.dumps(message, indent=2)}```"}

        """Envoie un message à Slack via un webhook."""
        response = requests.post(
            slack_hook,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=3,
        )

        if response.status_code != 200:
            logger.error(f"Failed to send message to Slack: {response.text}")

        return response


slack_client = SlackClient()
