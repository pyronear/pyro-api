# Copyright (C) 2022-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import hashlib
import logging
from datetime import datetime
from mimetypes import guess_extension
from typing import Any, Dict, Union

import boto3
import magic
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError, PartialCredentialsError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

__all__ = ["s3_service", "upload_file"]


logger = logging.getLogger("uvicorn.warning")


class S3Bucket:
    """S3 bucket manager

    Args:
        s3_client: the client of the S3 service
        bucket_name: the name of the bucket
        proxy_url: the proxy url
    """

    def __init__(self, s3_client: boto3.client, bucket_name: str, proxy_url: Union[str, None] = None) -> None:
        self._s3 = s3_client
        try:
            self._s3.head_bucket(Bucket=bucket_name)
        except EndpointConnectionError:
            raise ValueError(f"unable to access endpoint {self._s3.meta.endpoint_url}")
        except ClientError:
            raise ValueError(f"unable to access bucket {bucket_name}")
        self.name = bucket_name
        self.proxy_url = proxy_url

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

    def upload_file(self, bucket_key: str, file_binary: bytes) -> bool:
        """Upload a file to bucket and return whether the upload succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj
        self._s3.upload_fileobj(file_binary, self.name, bucket_key)
        return True

    def delete_file(self, bucket_key: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        self._s3.delete_object(Bucket=self.name, Key=bucket_key)

    def get_public_url(self, bucket_key: str, url_expiration: int = settings.S3_URL_EXPIRATION) -> str:
        """Generate a temporary public URL for a bucket file"""
        if not self.check_file_existence(bucket_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File cannot be found on the bucket storage"
            )

        # Generate a public URL for it using boto3 presign URL generation\
        presigned_url = self._s3.generate_presigned_url(
            "get_object", Params={"Bucket": self.name, "Key": bucket_key}, ExpiresIn=url_expiration
        )
        if self.proxy_url:
            return presigned_url.replace(self._s3.meta.endpoint_url, self.proxy_url)
        return presigned_url

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

    def create_bucket(self, bucket_name: str) -> bool:
        """Create a new bucket in S3 storage"""
        try:
            self._s3.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": self._s3.meta.region_name}
            )
            return True
        except ClientError as e:
            logger.warning(e)
            return False

    def get_bucket(self, bucket_name: str) -> S3Bucket:
        """Get an existing bucket in S3 storage"""
        return S3Bucket(self._s3, bucket_name, self.proxy_url)

    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete an existing bucket in S3 storage"""
        bucket = S3Bucket(self._s3, bucket_name, self.proxy_url)
        try:
            await bucket.delete_items()
            self._s3.delete_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            logger.warning(e)
            return False

    @staticmethod
    def resolve_bucket_name(organization_id: int) -> str:
        return f"{settings.SERVER_NAME}-alert-api-{organization_id!s}"


async def upload_file(file: UploadFile, organization_id: int, camera_id: int) -> str:
    """Upload a file to S3 storage and return the public URL"""
    # Concatenate the first 8 chars (to avoid system interactions issues) of SHA256 hash with file extension
    sha_hash = hashlib.sha256(file.file.read()).hexdigest()
    await file.seek(0)
    # Use MD5 to verify upload
    md5_hash = hashlib.md5(file.file.read()).hexdigest()  # noqa S324
    await file.seek(0)
    # guess_extension will return none if this fails
    extension = guess_extension(magic.from_buffer(file.file.read(), mime=True)) or ""
    # Concatenate timestamp & hash
    bucket_key = f"{camera_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{sha_hash[:8]}{extension}"
    # Reset byte position of the file (cf. https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    await file.seek(0)
    bucket_name = s3_service.resolve_bucket_name(organization_id)
    bucket = s3_service.get_bucket(bucket_name)
    # Upload the file
    if not bucket.upload_file(bucket_key, file.file):  # type: ignore[arg-type]
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
