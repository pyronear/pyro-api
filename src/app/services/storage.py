# Copyright (C) 2022-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import HTTPException

from app.core.config import settings

__all__ = ["s3_bucket"]


logger = logging.getLogger("uvicorn.warning")


class S3Bucket:
    """Storage bucket manipulation object on S3 storage

    Args:
        region: S3 region
        endpoint_url: the S3 storage endpoint
        access_key: the S3 access key
        secret_key: the S3 secret key
        proxy_url: the proxy url
    """

    def __init__(self, region: str, endpoint_url: str, access_key: str, secret_key: str, proxy_url: str) -> None:
        _session = boto3.Session(access_key, secret_key, region_name=region)
        self._s3 = _session.client("s3", endpoint_url=endpoint_url)
        # Ensure S3 is connected
        try:
            self._s3.head_bucket(Bucket="admin")
        except EndpointConnectionError:
            raise ValueError(f"unable to access endpoint {endpoint_url}")
        except ClientError:
            raise ValueError("unable to access bucket admin")
        logger.info(f"S3 bucket admin connected on {endpoint_url}")
        self.proxy_url = proxy_url

    async def get_file_metadata(self, bucket_key: str, bucket_name: str) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.head_object
        return self._s3.head_object(Bucket=bucket_name, Key=bucket_key)

    async def check_file_existence(self, bucket_key: str, bucket_name: str) -> bool:
        """Check whether a file exists on the bucket"""
        try:
            # Use boto3 head_object method using the Qarnot private connection attribute
            head_object = await self.get_file_metadata(bucket_key, bucket_name)
            return head_object["ResponseMetadata"]["HTTPStatusCode"] == 200
        except ClientError as e:
            logger.warning(e)
            return False

    async def get_public_url(self, bucket_key: str, url_expiration: int = settings.S3_URL_EXPIRATION) -> str:
        """Generate a temporary public URL for a bucket file"""
        if not (await self.check_file_existence(bucket_key, bucket_name)):
            raise HTTPException(status_code=404, detail="File cannot be found on the bucket storage")

        # Point to the bucket file
        file_params = {"Bucket": bucket_name, "Key": bucket_key}
        # Generate a public URL for it using boto3 presign URL generation\
        presigned_url = self._s3.generate_presigned_url("get_object", Params=file_params, ExpiresIn=url_expiration)
        if len(self.proxy_url) > 0:
            return presigned_url.replace(self._s3.meta.endpoint_url, self.proxy_url)
        return presigned_url

    async def upload_file(self, bucket_key: str, bucket_name: str, file_binary: bytes) -> bool:
        """Upload a file to bucket and return whether the upload succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj
        try:
            self._s3.upload_fileobj(file_binary, bucket_name, bucket_key)
            return True
        except:
            raise

    async def delete_file(self, bucket_key: str, bucket_name: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        self._s3.delete_object(Bucket=bucket_name, Key=bucket_key)

    async def create_bucket(self, bucket_name: str) -> bool:
        """Create a new bucket in S3 storage"""
        try:
            self._s3.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": self._s3.meta.region_name}
            )
            return True
        except ClientError as e:
            logger.error(e)
            return False

    def get_bucket_name(self, organization_id: int) -> str:
        return f"alert-api-{organization_id!s}"


s3_bucket = S3Bucket(
    settings.S3_REGION,
    settings.S3_ENDPOINT_URL,
    settings.S3_ACCESS_KEY,
    settings.S3_SECRET_KEY,
    settings.S3_PROXY_URL,
)
