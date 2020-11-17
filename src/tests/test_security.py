import pytest

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
