import os

import pytest

from app.services import bucket_service, resolve_bucket_key
from app.services.bucket import S3Bucket
from app.services.utils import cfg, send_telegram_msg


def test_resolve_bucket_key(monkeypatch):
    file_name = "myfile.jpg"
    bucket_subfolder = "my/bucket/subfolder"

    # Same if the bucket folder is specified
    assert resolve_bucket_key(file_name, bucket_subfolder) == f"{bucket_subfolder}/{file_name}"

    # Check that bucket folder is prepended in bucket key if set
    origin_value = cfg.BUCKET_MEDIA_FOLDER
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", bucket_subfolder)
    assert resolve_bucket_key(file_name) == f"{bucket_subfolder}/{file_name}"

    # Check that it returns the same thing when bucket folder is not set
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", None)
    assert resolve_bucket_key(file_name) == file_name
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", origin_value)


def test_bucket_service():
    assert isinstance(bucket_service, S3Bucket)


@pytest.fixture
def unset_telegram_token(monkeypatch):
    monkeypatch.setattr(cfg, "TELEGRAM_TOKEN", None)


@pytest.mark.asyncio
async def test_no_send_telegram_msg(unset_telegram_token):
    assert await send_telegram_msg("invalid-chat-id", "Fake message") is None


@pytest.mark.skipif(not cfg.TELEGRAM_TOKEN, reason="TELEGRAM_TOKEN not set")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "chat_id, text, photo, valid",
    [
        ("invalid-chat-id", "Fake message", None, False),
        pytest.param(
            os.environ.get("TELEGRAM_TEST_CHAT_ID"),
            "Test message",
            None,
            True,
            marks=pytest.mark.skipif("TELEGRAM_TEST_CHAT_ID" not in os.environ, reason="TELEGRAM_TEST_CHAT_ID not set"),
        ),
        pytest.param(
            os.environ.get("TELEGRAM_TEST_CHAT_ID"),
            "Test message with photo",
            "https://avatars.githubusercontent.com/u/61667887?s=200&v=4",
            True,
            marks=pytest.mark.skipif("TELEGRAM_TEST_CHAT_ID" not in os.environ, reason="TELEGRAM_TEST_CHAT_ID not set"),
        ),
    ],
)
async def test_send_telegram_msg(chat_id, text, photo, valid):
    msg = await send_telegram_msg(chat_id=chat_id, text=text, photo=photo, test=True)
    if not valid:
        assert msg is None
    elif photo is None:
        assert msg.text == text
    else:
        assert msg.caption == text
        assert len(msg.photo)
