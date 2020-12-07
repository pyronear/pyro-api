from qarnot import connection, bucket

from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class QarnotBucketService(BaseBucketService):

    def connect_to_bucket(self):
        if not hasattr(self, 'bucket'):
            conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
            self.bucket = bucket.Bucket(conn, cfg.BUCKET_NAME)
        return self.bucket

    async def upload_file(self, bucket_key: str, file_binary: bin):
        return await self.connect_to_bucket().add_file(file_binary, bucket_key)

    async def get_uploaded_file(self, bucket_key: str):
        return await self.connect_to_bucket().get_file(bucket_key)

    async def fetch_bucket_filenames(self):
        return await self.connect_to_bucket().list_files()
