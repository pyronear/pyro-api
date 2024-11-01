import pytest

from app.core.config import settings
from app.services.telegram import TelegramClient


def test_telegram_client():
    with pytest.raises(ValueError, match="Invalid Telegram Bot token"):
        TelegramClient("invalid-token")

    client = TelegramClient(None)
    assert not client.is_enabled

    client = TelegramClient(settings.TELEGRAM_TOKEN)
    assert client.is_enabled == isinstance(settings.TELEGRAM_TOKEN, str)

    if isinstance(settings.TELEGRAM_TOKEN, str):
        assert not client.has_channel_access("invalid-channel-id")
        assert client.notify("invalid-channel-id", "test").status_code == 404
    else:
        with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
            client.has_channel_access("invalid-channel-id")
        with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
            client.notify("invalid-channel-id", "test")
