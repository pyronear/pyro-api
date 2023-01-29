# Copyright (C) 2022-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Any, Dict, Optional

import boto3
import botocore
from fastapi import HTTPException

from app import config as cfg

__all__ = ["S3Bucket"]


logger = logging.getLogger("uvicorn.warning")


class S3Bucket:
    """Storage bucket manipulation object on S3 storage"""

    _s3: Optional[botocore.client.BaseClient] = None
    _media_folder: Optional[str] = None

    def __init__(self) -> None:
        self._connect_to_storage()

    def _connect_to_storage(self) -> None:
        """Connect to the CSP bucket"""
        _session = boto3.Session(cfg.S3_ACCESS_KEY, cfg.S3_SECRET_KEY, region_name=cfg.S3_REGION)
        try:
            self._s3 = _session.client("s3", endpoint_url=cfg.S3_ENDPOINT_URL)
        except ValueError:
            raise ValueError(f"invalid URL: '{cfg.S3_ENDPOINT_URL}'")
        if isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
            self._media_folder = cfg.BUCKET_MEDIA_FOLDER

    @property
    def s3(self) -> botocore.client.BaseClient:
        if self._s3 is None:
            self._connect_to_storage()
        return self._s3

    async def get_file_metadata(self, bucket_key: str) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.head_object
        return self.s3.head_object(Bucket=cfg.BUCKET_NAME, Key=bucket_key)

    async def check_file_existence(self, bucket_key: str) -> bool:
        """Check whether a file exists on the bucket"""
        try:
            # Use boto3 head_object method using the Qarnot private connection attribute
            head_object = await self.get_file_metadata(bucket_key)
            return head_object["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception as e:
            logger.warning(e)
            return False

    async def get_public_url(self, bucket_key: str, url_expiration: int = 3600) -> str:
        """Generate a temporary public URL for a bucket file"""
        if not (await self.check_file_existence(bucket_key)):
            raise HTTPException(status_code=404, detail="File cannot be found on the bucket storage")

        # Point to the bucket file
        file_params = {"Bucket": cfg.BUCKET_NAME, "Key": bucket_key}
        # Generate a public URL for it using boto3 presign URL generation
        return self.s3.generate_presigned_url("get_object", Params=file_params, ExpiresIn=url_expiration)

    async def upload_file(self, bucket_key: str, file_binary: bytes) -> bool:
        """Upload a file to bucket and return whether the upload succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj
        try:
            self.s3.upload_fileobj(file_binary, cfg.BUCKET_NAME, bucket_key)
        except Exception as e:
            logger.warning(e)
            return False
        return True

    async def delete_file(self, bucket_key: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        self.s3.delete_object(Bucket=cfg.BUCKET_NAME, Key=bucket_key)
