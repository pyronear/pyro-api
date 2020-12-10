import os
import logging
from typing import List, Optional
from fastapi import HTTPException
from qarnot.connection import Connection
from qarnot.bucket import Bucket

from app import config as cfg


__all__ = ['QarnotBucket']


logger = logging.getLogger("uvicorn.warning")


class QarnotBucket:
    """Storage bucket manipulation object on Qarnot computing"""

    _bucket: Optional[Bucket] = None
    _media_folder: Optional[str] = None

    def __init__(self) -> None:
        self._connect_to_bucket()

    def _connect_to_bucket(self) -> None:
        """Connect to the CSP bucket"""
        self._conn = Connection(client_token=cfg.QARNOT_TOKEN)
        self._bucket = Bucket(self._conn, cfg.BUCKET_NAME)
        if isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
            self._media_folder = cfg.BUCKET_MEDIA_FOLDER

    @property
    def bucket(self) -> Bucket:
        if self._bucket is None:
            self._connect_to_bucket()
        return self._bucket

    async def get_file(self, bucket_key: str) -> Optional[str]:
        """Download a file locally and returns the local temp path"""
        try:
            return self.bucket.get_file(bucket_key)
        except Exception as e:
            logger.warning(e)
            return None

    async def check_file_existence(self, bucket_key: str) -> bool:
        """Check whether a file exists on the bucket"""
        try:
            # Use boto3 head_object method using the Qarnot private connection attribute
            # cf. https://github.com/qarnot/qarnot-sdk-python/blob/master/qarnot/connection.py#L188
            head_object = self._conn._s3client.head_object(Bucket=cfg.BUCKET_NAME, Key=bucket_key)
            return head_object['ResponseMetadata']['HTTPStatusCode'] == 200
        except Exception as e:
            logger.warning(e)
            return False

    async def get_public_url(self, bucket_key: str, url_expiration: int = 3600) -> str:
        """Generate a temporary public URL for a bucket file"""
        if not await self.check_file_existence(bucket_key):
            raise HTTPException(status_code=404, detail="File cannot be found on the bucket storage")

        # Point to the bucket file
        file_params = {'Bucket': cfg.BUCKET_NAME, 'Key': bucket_key}
        # Generate a public URL for it using boto3 presign URL generation
        return self._conn._s3client.generate_presigned_url('get_object', Params=file_params, ExpiresIn=url_expiration)

    async def upload_file(self, bucket_key: str, file_binary: bin) -> bool:
        """Upload a file to bucket and return whether the upload succeeded"""
        try:
            self.bucket.add_file(file_binary, bucket_key)
        except Exception as e:
            logger.warning(e)
            return False
        return True

    async def fetch_bucket_filenames(self) -> List[str]:
        """List all bucket files"""

        if isinstance(self._media_folder, str):
            obj_summary = self.bucket.directory(self._media_folder)
        else:
            obj_summary = self.bucket.list_files()

        return [file.key for file in list(obj_summary)]

    async def flush_tmp_file(self, filename: str) -> None:
        """Remove temporary file"""
        if os.path.exists(filename):
            os.remove(filename)

    async def delete_file(self, bucket_key: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        self.bucket.delete_file(bucket_key)
