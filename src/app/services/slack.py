# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from app.core.config import settings

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

    def notify(
        self,
        slack_hook: str,
        message_detection: str,
        camera_name: str,
        alert_id: int | None = None,
    ) -> requests.Response:
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

        base_url = settings.PLATFORM_URL.rstrip("/")
        platform_url = f"{base_url}/alert/{alert_id}" if alert_id is not None else f"{base_url}/"

        text_body = (
            f":date: {paris_dt.strftime('%Y-%m-%d %H:%M:%S')}"
            f"\n Nom du site concerné : {camera_name}"
            f"\n Azimuth de détection : {azimuth}°"
            f"\n <{platform_url}|Visualiser l'alerte en détail sur la plateforme Pyronear>"
        )

        message = {
            "text": "Un feu a été détecté !",
            "blocks": [
                {
                    "type": "section",
                    "block_id": "section567",
                    "text": {"type": "mrkdwn", "text": text_body},
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
            logger.error(f"Failed to send message to Slack: {response.text} | payload={json.dumps(message)}")

        return response


slack_client = SlackClient()
