from unittest.mock import Mock, patch

from app.core.config import settings
from app.services.telemetry import TelemetryClient


def test_posthog_v7_adapter() -> None:
    posthog_client = Mock()
    with patch("app.services.telemetry.Posthog", return_value=posthog_client) as posthog:
        client = TelemetryClient(api_key="project-key")

    posthog.assert_called_once_with(project_api_key="project-key", host=settings.POSTHOG_HOST)

    client.capture(42, event="user-login", properties={"method": "credentials"})
    posthog_client.capture.assert_called_once_with("user-login", distinct_id=42, properties={"method": "credentials"})

    client.identify(42, {"name": "Alice"})
    posthog_client.set.assert_called_once_with(distinct_id=42, properties={"name": "Alice"})

    client.alias(42, "alice")
    posthog_client.alias.assert_called_once_with(previous_id="42", distinct_id="alice")
