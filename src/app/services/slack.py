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

    def notify(self, slack_hook: str, message_detection: str, url: str, camera_name: str) -> requests.Response:
        if not self.is_enabled:
            raise AssertionError("Slack notifications are not enabled")

        try:
            detection_data = json.loads(message_detection)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON format for message_detection") from e

        azimuth = detection_data.get("azimuth", "Inconnu")
        if url is not None:
            message = {
                "text": "Un feu a été detecté !",
                "blocks": [
                    {
                        "type": "section",
                        "block_id": "section567",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":fire: \n\n Nom du site concerné : " + camera_name + "\n Azimuth :" + str(azimuth),
                        },
                    },
                    {"type": "image", "image_url": url, "alt_text": "Haunted hotel image"},
                ],
            }
        else:
            message = {
                "text": "Un feu a été detecté !",
                "blocks": [
                    {
                        "type": "section",
                        "block_id": "section567",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":fire: \n\n Nom du site concerné : " + camera_name + "\n Azimuth :" + str(azimuth),
                        },
                    },
                ],
            }

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
