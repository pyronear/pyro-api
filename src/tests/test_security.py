import pytest
import requests

from app.api import security


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
