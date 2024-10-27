import pytest

from app.core.config import settings
from app.services.telegram import TelegramClient


def test_telegram_client():
    with pytest.raises(ValueError, match="Invalid Telegram Bot token"):
        TelegramClient("invalid-token")

    client = TelegramClient(None)
    assert not client.is_enabled

    client = TelegramClient(settings.TELEGRAM_TOKEN)
    assert client.is_enabled

    assert not client.has_channel_access("invalid-channel-id")
    assert client.notify("invalid-channel-id", "test").status_code == 404
