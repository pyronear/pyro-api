import io

import pytest
from httpx import AsyncClient

from app.services.storage import S3Bucket, s3_bucket


@pytest.mark.asyncio
async def test_s3_bucket(async_client: AsyncClient, mock_img: bytes):
    assert isinstance(s3_bucket, S3Bucket)
    bucket_key = "logo.png"
    bucket_name = "admin"
    url_expiration = 1
    # Check the file does not exist
    assert not (await s3_bucket.check_file_existence(bucket_key, bucket_name))
    assert await s3_bucket.upload_file(bucket_key, bucket_name, io.BytesIO(mock_img))
    assert await s3_bucket.check_file_existence(bucket_key, bucket_name)
    assert isinstance(await s3_bucket.get_file_metadata(bucket_key, bucket_name), dict)
    # Get the public URL
    file_url = await s3_bucket.get_public_url(bucket_key, bucket_name, url_expiration)
    assert file_url.startswith("http://")
    # Check the file is deleted
    await s3_bucket.delete_file(bucket_key, bucket_name)
    assert not (await s3_bucket.check_file_existence(bucket_key, bucket_name))
