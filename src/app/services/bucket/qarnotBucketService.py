import os
from qarnot import connection, bucket
import logging

from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg

logger = logging.getLogger("uvicorn.error")


class QarnotBucketService(BaseBucketService):

    def connect_to_bucket(self):
        if not hasattr(self, 'bucket'):
            conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
            self.bucket = bucket.Bucket(conn, cfg.BUCKET_NAME)
        return self.bucket

    async def upload_file(self, bucket_key: str, file_binary: bin):
        try:
            self.connect_to_bucket().add_file(file_binary, bucket_key)
        except Exception as e:
            logging.error(e)
            return False
        return True

    async def get_uploaded_file(self, bucket_key: str):
        try:
            return self.connect_to_bucket().get_file(bucket_key)
        except Exception as e:
            logging.error(e)
            return False
        return True

    async def fetch_bucket_filenames(self):
        return self.connect_to_bucket().list_files()

    async def flush_after_get_uploaded_file(self, filename):
        os.remove(filename) if os.path.exists(filename) else None
