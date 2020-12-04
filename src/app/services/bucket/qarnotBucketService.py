from qarnot import connection, bucket
import os

from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class QarnotBucketService(BaseBucketService):

    def connet_to_bucket(self, bucket_name: str):
        conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
        return bucket.Bucket(conn, bucket_name)

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        return await connet_to_bucket(bucket_name).add_file(bucket_name, file_binary, bucket_key)

    async def get_uploaded_file(self, bucket_name: str, bucket_key: str):
        return await connet_to_bucket(bucket_name).get_file(bucket_name, bucket_key)

    async def fetch_bucket_filenames(self, bucket_name: str):
        return await connet_to_bucket(bucket_name).list_files()
