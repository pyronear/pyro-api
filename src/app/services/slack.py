# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

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

        azimuth = detection_data.get("azimuth")
        if azimuth is None:
            azimuth = detection_data.get("pose_azimuth")
        if azimuth is None:
            azimuth = detection_data.get("sequence_azimuth")
        if azimuth is None:
            azimuth = detection_data.get("camera_azimuth")
        if azimuth is None:
            azimuth = "Inconnu"
        created_at_str = detection_data.get("created_at", "Inconnu")
        utc_dt = datetime.fromisoformat(created_at_str)
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
        paris_dt = utc_dt.astimezone(ZoneInfo("Europe/Paris"))

        if url is not None:
            message = {
                "text": "Un feu a été detecté !",
                "blocks": [
                    {
                        "type": "section",
                        "block_id": "section567",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":date: "
                            + paris_dt.strftime("%Y-%m-%d %H:%M:%S")
                            + "\n Nom du site concerné : "
                            + camera_name
                            + "\n Azimuth de detection : "
                            + str(azimuth)
                            + "°"
                            + "\n https://platform.pyronear.org/"
                            + "\n "
                            + url,
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
                            "text": ":date: "
                            + paris_dt.strftime("%Y-%m-%d %H:%M:%S")
                            + "\n Nom du site concerné : "
                            + camera_name
                            + "\n Azimuth de detection : "
                            + str(azimuth)
                            + "°"
                            + "\n https://platform.pyronear.org/",
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
