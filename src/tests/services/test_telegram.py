import os

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
        # Telegram answers 400 (chat not found) with a valid token, 404 with an invalid one
        assert client.notify("invalid-channel-id", "test").status_code in {400, 404}
    else:
        with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
            client.has_channel_access("invalid-channel-id")
        with pytest.raises(AssertionError, match="Telegram notifications are not enabled"):
            client.notify("invalid-channel-id", "test")


@pytest.mark.skipif(
    not os.environ.get("TELEGRAM_TOKEN") or not os.environ.get("TELEGRAM_TEST_CHAT_ID"),
    reason="requires TELEGRAM_TOKEN and TELEGRAM_TEST_CHAT_ID",
)
def test_telegram_notify_end_to_end():
    client = TelegramClient(os.environ["TELEGRAM_TOKEN"])
    chat_id = os.environ["TELEGRAM_TEST_CHAT_ID"]
    assert client.has_channel_access(chat_id)
    assert client.notify(chat_id, "Pyronear API CI: Telegram notification check").status_code == 200
