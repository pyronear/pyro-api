import os

import pytest

from app.services import resolve_bucket_key
from app.services.storage import S3Bucket, s3_bucket
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


def test_s3_bucket():
    assert isinstance(s3_bucket, S3Bucket)


@pytest.fixture()
def unset_telegram_token(monkeypatch):
    monkeypatch.setattr(cfg, "TELEGRAM_TOKEN", None)


def test_no_send_telegram_msg(unset_telegram_token):
    assert send_telegram_msg("invalid-chat-id", "Fake message") is None


@pytest.mark.skipif(not cfg.TELEGRAM_TOKEN, reason="TELEGRAM_TOKEN not set")
@pytest.mark.parametrize(
    ("chat_id", "msg", "expected_status_code"),
    [
        ("invalid-chat-id", "Fake message", 400),
        pytest.param(
            os.environ.get("TELEGRAM_TEST_CHAT_ID"),
            "Test message&disable_notification=true",
            200,
            marks=pytest.mark.skipif("TELEGRAM_TEST_CHAT_ID" not in os.environ, reason="TELEGRAM_TEST_CHAT_ID not set"),
        ),
    ],
)
def test_send_telegram_msg(chat_id, msg, expected_status_code):
    response = send_telegram_msg(chat_id=chat_id, message=msg, autodelete=expected_status_code == 200)
    if expected_status_code is None:
        assert response is None
    else:
        assert response.status_code == expected_status_code, response.text
