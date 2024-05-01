from datetime import datetime, timedelta

import pytest
import requests
from jose import jwt

from app import config as cfg
from app.api import security


@pytest.mark.asyncio()
async def test_hash_password():
    pwd1 = "my_password"
    hash_pwd1 = await security.hash_password(pwd1)

    assert hash_pwd1 != pwd1
    assert hash_pwd1 != await security.hash_password(pwd1 + "bis")
    # Check that it's non deterministic
    assert hash_pwd1 != await security.hash_password(pwd1)


@pytest.mark.asyncio()
async def test_verify_password():
    pwd1 = "my_password"
    hash_pwd1 = await security.hash_password(pwd1)

    assert await security.verify_password(pwd1, hash_pwd1)
    assert not await security.verify_password("another_try", hash_pwd1)


def test_hash_content_file():
    # Download a small file
    file_url1 = "https://github.com/pyronear/pyro-api/releases/download/v0.1.1/pyronear_logo.png"
    file_url2 = "https://github.com/pyronear/pyro-api/releases/download/v0.1.1/pyronear_logo_mini.png"

    # Hash it
    hash1 = security.hash_content_file(requests.get(file_url1, timeout=5).content)
    hash2 = security.hash_content_file(requests.get(file_url2, timeout=5).content)

    # Check data integrity
    assert security.hash_content_file(requests.get(file_url1, timeout=5).content) == hash1
    assert hash1 != hash2


@pytest.mark.parametrize(
    "content, expiration, expected_delta",
    [
        [{"data": "my_data"}, 60, 60],
        [{"data": "my_data"}, None, cfg.ACCESS_TOKEN_EXPIRE_MINUTES],
    ],
)
@pytest.mark.asyncio()
async def test_create_access_token(content, expiration, expected_delta):
    delta = timedelta(minutes=expiration) if isinstance(expiration, int) else None
    payload = await security.create_access_token(content, expires_delta=delta)
    after = datetime.utcnow()
    assert isinstance(payload, str)
    decoded_data = jwt.decode(payload, cfg.SECRET_KEY)
    # Verify data integrity
    assert all(v == decoded_data[k] for k, v in content.items())
    # Check expiration
    assert datetime.utcfromtimestamp(decoded_data["exp"]) - timedelta(minutes=expected_delta) < after
