# Copyright (C) 2022-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import hashlib
import logging
import time
from collections import OrderedDict
from mimetypes import guess_extension
from typing import Any, BinaryIO, Dict, Tuple, Union

import boto3
import magic
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError, PartialCredentialsError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.core.time import utcnow

__all__ = ["s3_service", "upload_file"]


logger = logging.getLogger("uvicorn.warning")

# Presigned URLs run 600-900 bytes, so ~1 KB per entry => ~8 MB hard ceiling per bucket.
_URL_CACHE_MAXSIZE = 8192


def _url_cache_window(url_expiration: int) -> int:
    """How long a single presigned URL string keeps being handed out, in seconds.

    Derived from the expiration rather than hardcoded, so lowering S3_URL_EXPIRATION can never
    start serving already-expired URLs: the window never exceeds the lifetime, whatever the
    input (the floor is 1, not 60, so a sub-minute expiration degrades to near-no-caching instead
    of outliving the URL). At the 24h default the cap binds instead and the window is 1h, so a
    handed-out URL always has >= 23h left.
    """
    return min(3600, max(1, url_expiration // 4))


class S3Bucket:
    """S3 bucket manager

    Args:
        s3_client: the client of the S3 service
        bucket_name: the name of the bucket
        proxy_url: the proxy url
    """

    def __init__(self, s3_client, bucket_name: str, proxy_url: Union[str, None] = None) -> None:  # ruff:ignore[missing-type-function-argument]
        self._s3 = s3_client
        try:
            self._s3.head_bucket(Bucket=bucket_name)
        except EndpointConnectionError:
            raise ValueError(f"unable to access endpoint {self._s3.meta.endpoint_url}")
        except ClientError:
            raise ValueError(f"unable to access bucket {bucket_name}")
        self.name = bucket_name
        self.proxy_url = proxy_url
        # (bucket_key, url_expiration, window slot) -> presigned URL. Scoped to the instance
        # because proxy_url and the signing credentials are fixed per bucket.
        self._url_cache: OrderedDict[Tuple[str, int, int], str] = OrderedDict()

    def get_file_metadata(self, bucket_key: str) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.head_object
        return self._s3.head_object(Bucket=self.name, Key=bucket_key)

    def check_file_existence(self, bucket_key: str) -> bool:
        """Check whether a file exists on the bucket"""
        try:
            # Use boto3 head_object method using the Qarnot private connection attribute
            head_object = self.get_file_metadata(bucket_key)
            return head_object["ResponseMetadata"]["HTTPStatusCode"] == 200
        except ClientError as e:
            logger.warning(e)
            return False

    def upload_file(self, bucket_key: str, file_binary: BinaryIO) -> bool:
        """Upload a file to bucket and return whether the upload succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj
        # Cache-Control is what turns the stable presigned URLs from get_public_url into actual
        # browser cache hits: without it browsers only cache heuristically, so the player
        # re-downloads frames it already has. Objects are immutable once written (the key
        # embeds a content hash), so max-age can match the URL lifetime.
        self._s3.upload_fileobj(
            file_binary,
            self.name,
            bucket_key,
            ExtraArgs={"CacheControl": f"private, max-age={settings.S3_URL_EXPIRATION}"},
        )
        return True

    def delete_file(self, bucket_key: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        self._s3.delete_object(Bucket=self.name, Key=bucket_key)

    def get_public_url(
        self, bucket_key: str, url_expiration: int = settings.S3_URL_EXPIRATION, verify_exists: bool = True
    ) -> str:
        """Generate a temporary public URL for a bucket file

        Args:
            bucket_key: the key of the file on the bucket
            url_expiration: how long the presigned URL stays valid, in seconds
            verify_exists: when True (default), raise a 404 if the object is missing on the
                bucket. Presigning itself is a local signature computation with no network
                I/O, whereas this check adds one blocking S3 ``head_object`` round-trip per
                file. Set it to False on hot paths where the object is expected to always
                exist (e.g. sequence detections): the client then gets a 403/404 from S3
                when loading the URL instead of an upfront error.
        """
        # Checked before the cache lookup on purpose: a cache hit must not skip the existence
        # check callers opted into.
        if verify_exists and not self.check_file_existence(bucket_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File cannot be found on the bucket storage"
            )

        return self._stable_presign(bucket_key, url_expiration)

    def _presign(self, bucket_key: str, url_expiration: int) -> str:
        # Generate a public URL for it using boto3 presign URL generation
        presigned_url = self._s3.generate_presigned_url(
            "get_object", Params={"Bucket": self.name, "Key": bucket_key}, ExpiresIn=url_expiration
        )
        if self.proxy_url:
            return presigned_url.replace(self._s3.meta.endpoint_url, self.proxy_url)
        return presigned_url

    def _stable_presign(self, bucket_key: str, url_expiration: int) -> str:
        """Return the same URL string for a whole window, so the browser can cache frames.

        boto3 stamps the current clock into every signature (``X-Amz-Date`` under SigV4,
        ``Expires`` under SigV2), so re-presigning the same key yields a different string and
        busts the client cache on each poll. The browser keys its cache on the full URL.

        The window slot is part of the cache key, so a lookup against the current slot can never
        return a previous window's entry: no explicit rollover clear is needed, and stale entries
        simply age out through the size-bound eviction below.

        Stability is per-process: the cache lives on this instance, so it only dedupes URLs
        within one worker. With W workers a polling client sees up to W distinct URLs per key
        per window, one per worker that happened to answer, so a frame is fetched up to W times
        instead of once. That is still far better than re-signing on every poll (which bust the
        cache unconditionally), just divided by W. Production runs several workers, so this
        applies there; the worker count is not visible from this repo, which only carries dev
        compose files. See #671.

        Making it cross-process is not achievable without patching boto3's clock: SigV4 derives
        ``X-Amz-Date`` from the wall clock at signing time rather than taking it as a
        ``generate_presigned_url`` parameter, so a shared cache would be the way in.
        """
        window = _url_cache_window(url_expiration)
        # monotonic: only the window length matters, and it is immune to NTP steps.
        slot = int(time.monotonic()) // window
        cache_key = (bucket_key, url_expiration, slot)
        url = self._url_cache.get(cache_key)
        if url is not None:
            self._url_cache.move_to_end(cache_key)
            return url
        url = self._presign(bucket_key, url_expiration)
        if len(self._url_cache) >= _URL_CACHE_MAXSIZE:
            # Evict the coldest entry, never clear: one dict is shared by every viewer of an
            # organization, so clearing here would re-presign (and so change) every URL in
            # flight exactly when the cache is under load and stability matters most.
            self._url_cache.popitem(last=False)
        self._url_cache[cache_key] = url
        return url

    async def delete_items(self) -> None:
        """Delete all items in the bucket"""
        paginator = self._s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.name):
            if "Contents" in page:
                delete_items = [{"Key": obj["Key"]} for obj in page["Contents"]]
                self._s3.delete_objects(Bucket=self.name, Delete={"Objects": delete_items})


class S3Service:
    """S3 storage service manager

    Args:
        region: S3 region
        endpoint_url: the S3 storage endpoint
        access_key: the S3 access key
        secret_key: the S3 secret key
        proxy_url: the proxy url
    """

    def __init__(
        self, region: str, endpoint_url: str, access_key: str, secret_key: str, proxy_url: Union[str, None] = None
    ) -> None:
        session_ = boto3.Session(access_key, secret_key, region_name=region)
        self._s3 = session_.client("s3", endpoint_url=endpoint_url)
        # Ensure S3 is connected
        try:
            self._s3.list_buckets()
        except (NoCredentialsError, PartialCredentialsError):
            raise ValueError("invalid S3 credentials")
        except EndpointConnectionError:
            raise ValueError(f"unable to access endpoint {endpoint_url}")
        except ClientError:
            raise ValueError("unable to access S3")
        logger.info(f"S3 connected on {endpoint_url}")
        self.proxy_url = proxy_url
        # bucket_name -> S3Bucket. S3Bucket.__init__ does a blocking head_bucket round-trip on
        # the event loop; the bucket set is one per organization and effectively static, so
        # build each one once. Caching the instance is also what lets its URL cache ever hit.
        self._buckets: Dict[str, S3Bucket] = {}

    def create_bucket(self, bucket_name: str) -> bool:
        """Create a new bucket in S3 storage"""
        try:
            # https://stackoverflow.com/questions/51912072/invalidlocationconstraint-error-while-creating-s3-bucket-when-the-used-command-i
            # https://github.com/localstack/localstack/issues/8000
            config_ = (
                {}
                if self._s3.meta.region_name == "us-east-1"
                else {"CreateBucketConfiguration": {"LocationConstraint": self._s3.meta.region_name}}
            )
            self._s3.create_bucket(Bucket=bucket_name, **config_)
            self._put_bucket_cors(bucket_name)
            return True
        except ClientError as e:
            logger.warning(e)
            return False

    def _put_bucket_cors(self, bucket_name: str) -> None:
        """Apply the CORS policy so browsers can fetch() presigned URLs cross-origin.

        Allows the frontend origins (settings.S3_CORS_ORIGINS) to GET bucket objects, which the
        platform's "download all" buttons rely on (native fetch triggers CORS, unlike a plain
        <img> or <a download>).
        """
        origins = [origin.strip() for origin in settings.S3_CORS_ORIGINS.split(",") if origin.strip()]
        self._s3.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration={
                "CORSRules": [
                    {
                        "AllowedOrigins": origins,
                        "AllowedMethods": ["GET", "HEAD"],
                        "AllowedHeaders": ["*"],
                        "ExposeHeaders": ["Content-Length", "Content-Type"],
                        "MaxAgeSeconds": 3000,
                    }
                ]
            },
        )

    def get_bucket(self, bucket_name: str) -> S3Bucket:
        """Get an existing bucket in S3 storage (cached instance)

        Only successful lookups are cached, so a missing bucket still raises ValueError. Once
        cached, a bucket deleted out-of-band keeps answering and the failure surfaces at the S3
        call rather than here.
        """
        bucket = self._buckets.get(bucket_name)
        if bucket is None:
            bucket = S3Bucket(self._s3, bucket_name, self.proxy_url)
            self._buckets[bucket_name] = bucket
        return bucket

    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete an existing bucket in S3 storage"""
        bucket = self.get_bucket(bucket_name)
        try:
            await bucket.delete_items()
            self._s3.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            logger.warning(e)
            return False
        # Evict only once the bucket is really gone, so the cache stays coherent with the
        # organization-deletion path.
        self._buckets.pop(bucket_name, None)
        return True

    @staticmethod
    def resolve_bucket_name(organization_id: int) -> str:
        return f"{settings.SERVER_NAME}-alert-api-{organization_id!s}"


async def upload_file(file: UploadFile, organization_id: int, camera_id: int, key_prefix: str = "") -> str:
    """Upload a file to S3 storage and return the public URL"""
    # Concatenate the first 8 chars (to avoid system interactions issues) of SHA256 hash with file extension
    sha_hash = hashlib.sha256(file.file.read()).hexdigest()
    await file.seek(0)
    # Use MD5 to verify upload
    md5_hash = hashlib.md5(file.file.read()).hexdigest()  # ruff:ignore[hashlib-insecure-hash-function]
    await file.seek(0)
    # guess_extension will return none if this fails
    extension = guess_extension(magic.from_buffer(file.file.read(), mime=True)) or ""
    # Concatenate timestamp & hash; key_prefix lets callers segregate distinct uploads in the
    # same request (e.g. frame vs crop) so identical bytes don't collide on the same key.
    bucket_key = f"{key_prefix}{camera_id}-{utcnow().strftime('%Y%m%d%H%M%S')}-{sha_hash[:8]}{extension}"
    # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    await file.seek(0)
    bucket_name = s3_service.resolve_bucket_name(organization_id)
    bucket = s3_service.get_bucket(bucket_name)
    # Upload the file
    if not bucket.upload_file(bucket_key, file.file):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed upload")
    logger.info(f"File uploaded to bucket {bucket_name} with key {bucket_key}.")

    # Data integrity check
    file_meta = bucket.get_file_metadata(bucket_key)
    # Corrupted file
    if md5_hash != file_meta["ETag"].replace('"', ""):
        # Delete the corrupted upload
        bucket.delete_file(bucket_key)
        # Raise the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data was corrupted during upload",
        )
    return bucket_key


s3_service = S3Service(
    settings.S3_REGION, settings.S3_ENDPOINT_URL, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, settings.S3_PROXY_URL
)
