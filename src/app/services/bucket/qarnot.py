import os
import logging
from typing import List, Optional
from qarnot.connection import Connection
from qarnot.bucket import Bucket

from app import config as cfg


__all__ = ['QarnotBucket']


logger = logging.getLogger("uvicorn.warning")


class QarnotBucket:

    _bucket: Optional[Bucket] = None
    _media_folder: Optional[str] = None

    def __init__(self) -> None:
        self._connect_to_bucket()

    def _connect_to_bucket(self) -> None:
        """Connect to the CSP bucket"""
        conn = Connection(client_token=cfg.QARNOT_TOKEN)
        self._bucket = Bucket(conn, cfg.BUCKET_NAME.rpartition("/")[0])
        if len(cfg.BUCKET_NAME) > bucket_name.find("/"):
            self._media_folder = cfg.BUCKET_NAME[cfg.BUCKET_NAME.find('/') + 1:]

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

    async def is_file(self, bucket_key: str) -> bool:
        """Check whether a file exists on the bucket"""
        try:
            # Filter the bucket summary if this is in a subfolder
            if isinstance(self._media_folder, str):
                obj_summary = self.bucket.directory(self._media_folder)
            else:
                obj_summary = self.bucket.list_files()
            return len(list(obj_summary.filter(Prefix=bucket_key))) > 0
        except Exception as e:
            logger.warning(e)
            return False

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
        os.remove(filename) if os.path.exists(filename) else None

    async def delete_file(self, filename: str) -> None:
        """Remove bucket file and return whether the deletion succeeded"""
        self.bucket.delete_file(filename)
