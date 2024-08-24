import io

import boto3
import pytest

from app.core.config import settings
from app.services.storage import S3Bucket, S3Service


@pytest.mark.parametrize(
    (
        "region",
        "endpoint_url",
        "access_key",
        "secret_key",
        "proxy_url",
        "expected_error",
    ),
    [
        (None, None, None, None, None, ValueError),
        (
            "us-east-1",
            "http://localhost:9000",
            settings.S3_ACCESS_KEY,
            settings.S3_SECRET_KEY,
            settings.S3_PROXY_URL,
            ValueError,
        ),
        (
            settings.S3_REGION,
            settings.S3_ENDPOINT_URL,
            None,
            None,
            settings.S3_PROXY_URL,
            ValueError,
        ),
        (
            settings.S3_REGION,
            settings.S3_ENDPOINT_URL,
            settings.S3_ACCESS_KEY,
            settings.S3_SECRET_KEY,
            settings.S3_PROXY_URL,
            None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_s3_service(region, endpoint_url, access_key, secret_key, proxy_url, expected_error):
    if expected_error is None:
        service = S3Service(region, endpoint_url, access_key, secret_key, proxy_url)
        assert isinstance(service.resolve_bucket_name(1), str)
        # Create random bucket
        bucket_name = "dummy-bucket"
        service.create_bucket(bucket_name)
        # Delete the bucket
        await service.delete_bucket(bucket_name)
    else:
        with pytest.raises(expected_error):
            S3Service(region, endpoint_url, access_key, secret_key, proxy_url)


@pytest.mark.parametrize(
    ("bucket_name", "proxy_url", "expected_error"),
    [
        (None, None, TypeError),
        ("dummy-bucket1", None, ValueError),
        ("dummy-bucket2", settings.S3_PROXY_URL, None),
    ],
)
@pytest.mark.asyncio
async def test_s3_bucket(bucket_name, proxy_url, expected_error, mock_img):
    _session = boto3.Session(settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, region_name=settings.S3_REGION)
    _s3 = _session.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)
    if expected_error is None:
        _s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION})
        bucket = S3Bucket(_s3, bucket_name, proxy_url)
        bucket_key = "logo.png"
        # Create file
        assert not bucket.check_file_existence(bucket_key)
        bucket.upload_file(bucket_key, io.BytesIO(mock_img))
        assert bucket.check_file_existence(bucket_key)
        assert isinstance(bucket.get_file_metadata(bucket_key), dict)
        assert bucket.get_public_url(bucket_key).startswith("http://")
        # Delete file
        bucket.delete_file(bucket_key)
        assert not bucket.check_file_existence(bucket_key)
        # Delete all items
        bucket.upload_file(bucket_key, io.BytesIO(mock_img))
        assert bucket.check_file_existence(bucket_key)
        await bucket.delete_items()
        assert not bucket.check_file_existence(bucket_key)
        # Delete the bucket
        _s3.delete_bucket(Bucket=bucket_name)
    else:
        with pytest.raises(expected_error):
            S3Bucket(_s3, bucket_name, proxy_url)
