from qarnot import connection, bucket

from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class QarnotBucketService(BaseBucketService):

    def connect_to_bucket(self, bucket_name: str):
        if not hasattr(self, 'bucket'):
            conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
            self.bucket = bucket.Bucket(conn, bucket_name)
        return self.bucket

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        return await self.connect_to_bucket(bucket_name).add_file(bucket_name, file_binary, bucket_key)

    async def get_uploaded_file(self, bucket_name: str, bucket_key: str):
        return await self.connect_to_bucket(bucket_name).get_file(bucket_name, bucket_key)

    async def fetch_bucket_filenames(self, bucket_name: str):
        return await self.connect_to_bucket(bucket_name).list_files()
