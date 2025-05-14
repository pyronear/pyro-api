import pytest

from app.core.config import settings
from app.services.slack import SlackClient


def test_slack_client():
    client = SlackClient(settings.TELEGRAM_TOKEN)

    with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
        client.has_channel_access("invalid-channel-id")
    with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
        client.notify("invalid-channel-id", "test")
