# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest
import requests
from datetime import datetime, timedelta
from jose import jwt

from app.api import security
from app import config as cfg


@pytest.mark.asyncio
async def test_hash_password():

    pwd1 = "my_password"
    hash_pwd1 = await security.hash_password(pwd1)

    assert hash_pwd1 != pwd1
    assert hash_pwd1 != await security.hash_password(pwd1 + "bis")
    # Check that it's non deterministic
    assert hash_pwd1 != await security.hash_password(pwd1)


@pytest.mark.asyncio
async def test_verify_password():

    pwd1 = "my_password"
    hash_pwd1 = await security.hash_password(pwd1)

    assert await security.verify_password(pwd1, hash_pwd1)
    assert not await security.verify_password("another_try", hash_pwd1)


def test_hash_content_file():

    # Download a small file
    file_url1 = ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/"
                 "Davies-Meyer_hash.svg/230px-Davies-Meyer_hash.svg.png")
    file_url2 = ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/"
                 "Matyas-Meyer-Oseas_hash.svg/230px-Matyas-Meyer-Oseas_hash.svg.png")

    # Hash it
    hash1 = security.hash_content_file(requests.get(file_url1).content)
    hash2 = security.hash_content_file(requests.get(file_url2).content)

    # Check data integrity
    assert security.hash_content_file(requests.get(file_url1).content) == hash1
    assert hash1 != hash2


@pytest.mark.parametrize(
    "content, expiration, expected_delta",
    [
        [{"data": "my_data"}, 60, 60],
        [{"data": "my_data"}, None, cfg.ACCESS_TOKEN_EXPIRE_MINUTES],
    ],
)
@pytest.mark.asyncio
async def test_create_access_token(content, expiration, expected_delta):

    before = datetime.utcnow()
    delta = timedelta(minutes=expiration) if isinstance(expiration, int) else None
    payload = await security.create_access_token(content, expires_delta=delta)
    after = datetime.utcnow()
    assert isinstance(payload, str)
    decoded_data = jwt.decode(payload, cfg.SECRET_KEY)
    # Verify data integrity
    assert all(v == decoded_data[k] for k, v in content.items())
    # Check expiration
    assert datetime.utcfromtimestamp(decoded_data['exp']) - timedelta(minutes=expected_delta) < after
