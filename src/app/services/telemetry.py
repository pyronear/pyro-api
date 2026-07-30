# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Any

from posthog import Posthog

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

__all__ = ["telemetry_client"]


class TelemetryClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.is_enabled = isinstance(api_key, str)
        if isinstance(api_key, str):
            self.ph_client = Posthog(project_api_key=api_key, host=settings.POSTHOG_HOST)
            logger.info("PostHog enabled")

    def capture(self, distinct_id: str | int, *, event: str, properties: dict[str, Any] | None = None) -> None:
        if self.is_enabled:
            self.ph_client.capture(event, distinct_id=distinct_id, properties=properties)

    def identify(self, distinct_id: str | int, properties: dict[str, Any] | None = None) -> None:
        if self.is_enabled:
            self.ph_client.set(distinct_id=distinct_id, properties=properties)

    def alias(self, previous_id: str | int, distinct_id: str | int) -> None:
        if self.is_enabled:
            self.ph_client.alias(previous_id=str(previous_id), distinct_id=str(distinct_id))


telemetry_client = TelemetryClient(api_key=settings.POSTHOG_KEY)
