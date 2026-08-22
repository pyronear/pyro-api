import io

import boto3
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services import storage
from app.services.storage import S3Bucket, S3Service, _url_cache_window


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
        # The CORS policy is applied at creation so the frontend can fetch() presigned URLs
        cors_rules = service._s3.get_bucket_cors(Bucket=bucket_name)["CORSRules"]
        assert cors_rules[0]["AllowedMethods"] == ["GET", "HEAD"]
        assert cors_rules[0]["AllowedOrigins"] == [
            origin.strip() for origin in settings.S3_CORS_ORIGINS.split(",") if origin.strip()
        ]
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
    session = boto3.Session(settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, region_name=settings.S3_REGION)
    s3 = session.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)
    if expected_error is None:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION})
        bucket = S3Bucket(s3, bucket_name, proxy_url)
        bucket_key = "logo.png"
        # Create file
        assert not bucket.check_file_existence(bucket_key)
        # By default get_public_url verifies existence and raises a 404 when the object is missing
        with pytest.raises(HTTPException):
            bucket.get_public_url(bucket_key)
        # With verify_exists=False it skips the check and presigns a URL even when the object is missing
        assert bucket.get_public_url(bucket_key, verify_exists=False).startswith("http://")
        bucket.upload_file(bucket_key, io.BytesIO(mock_img))
        assert bucket.check_file_existence(bucket_key)
        assert isinstance(bucket.get_file_metadata(bucket_key), dict)
        # Cache-Control is what makes the stable presigned urls from get_public_url actually
        # cacheable browser-side; without it the upload path could silently stop setting it.
        assert bucket.get_file_metadata(bucket_key)["CacheControl"] == f"private, max-age={settings.S3_URL_EXPIRATION}"
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
        s3.delete_bucket(Bucket=bucket_name)
    else:
        with pytest.raises(expected_error):
            S3Bucket(s3, bucket_name, proxy_url)


@pytest.mark.parametrize("url_expiration", [1, 4, 20, 60, 300, 3600, 24 * 3600])
def test_url_cache_window_leaves_most_of_the_lifetime(url_expiration):
    """A cached url is always handed out with most of its lifetime left, and the window never
    exceeds the expiration, so a sub-minute expiration cannot serve an expired url."""
    assert 1 <= _url_cache_window(url_expiration) <= min(3600, url_expiration)


def test_s3_bucket_presigned_urls_are_stable_within_a_window(monkeypatch):
    """The same key presigns once per window and is re-signed once the slot advances.

    Counts presign calls rather than comparing urls, since two signatures taken in the same
    wall-clock second are identical. The clock is faked so the slot advance is deterministic.
    """
    session = boto3.Session(settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, region_name=settings.S3_REGION)
    s3 = session.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)
    bucket_name = "dummy-bucket-url-cache"
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION})
    try:
        bucket = S3Bucket(s3, bucket_name, settings.S3_PROXY_URL)
        presign_calls = []
        original_presign = bucket._presign

        def counting_presign(bucket_key, url_expiration):
            presign_calls.append(bucket_key)
            return original_presign(bucket_key, url_expiration)

        bucket._presign = counting_presign

        fake_clock = [0.0]
        monkeypatch.setattr(storage.time, "monotonic", lambda: fake_clock[0])

        first = bucket.get_public_url("stable.png", verify_exists=False)
        assert bucket.get_public_url("stable.png", verify_exists=False) == first
        assert len(presign_calls) == 1

        # Advance past the window: the slot changes, so the key misses and the url is re-signed.
        fake_clock[0] += _url_cache_window(settings.S3_URL_EXPIRATION)
        bucket.get_public_url("stable.png", verify_exists=False)
        assert len(presign_calls) == 2
        # The previous window's entry stays, aging out through eviction rather than a clear.
        assert set(bucket._url_cache) == {
            ("stable.png", settings.S3_URL_EXPIRATION, 0),
            ("stable.png", settings.S3_URL_EXPIRATION, 1),
        }
    finally:
        s3.delete_bucket(Bucket=bucket_name)


def test_s3_bucket_url_cache_evicts_coldest_entry_only(monkeypatch, pinned_url_window):
    """The size bound evicts the LRU entry only: a clear would change every url in flight."""
    session = boto3.Session(settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, region_name=settings.S3_REGION)
    s3 = session.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)
    bucket_name = "dummy-bucket-url-cache-eviction"
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION})
    try:
        bucket = S3Bucket(s3, bucket_name, settings.S3_PROXY_URL)
        monkeypatch.setattr(storage, "_URL_CACHE_MAXSIZE", 2)

        bucket.get_public_url("k1.png", verify_exists=False)
        bucket.get_public_url("k2.png", verify_exists=False)
        # Touch k1 again: it becomes most-recently-used, leaving k2 as the coldest entry.
        bucket.get_public_url("k1.png", verify_exists=False)
        # Inserting a third key over the bound of 2 must evict k2 only, never clear the dict.
        bucket.get_public_url("k3.png", verify_exists=False)

        cached_bucket_keys = {key[0] for key in bucket._url_cache}
        assert cached_bucket_keys == {"k1.png", "k3.png"}
        assert len(bucket._url_cache) == 2
    finally:
        s3.delete_bucket(Bucket=bucket_name)


@pytest.mark.asyncio
async def test_s3_service_caches_bucket_instances():
    """get_bucket must reuse instances (its __init__ does a blocking head_bucket) and evict
    the entry once the bucket is deleted."""
    service = S3Service(
        settings.S3_REGION,
        settings.S3_ENDPOINT_URL,
        settings.S3_ACCESS_KEY,
        settings.S3_SECRET_KEY,
        settings.S3_PROXY_URL,
    )
    bucket_name = "dummy-bucket-instance-cache"
    service.create_bucket(bucket_name)
    assert service.get_bucket(bucket_name) is service.get_bucket(bucket_name)

    assert await service.delete_bucket(bucket_name)
    assert bucket_name not in service._buckets

    # A missing bucket is never cached, so it keeps raising.
    with pytest.raises(ValueError, match="unable to access bucket"):
        service.get_bucket("dummy-bucket-does-not-exist")
