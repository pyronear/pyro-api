from qarnot import connection, bucket
import os

from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class QarnotBucketService(BaseBucketService):

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
        media_bucket = bucket.Bucket(conn, bucket_name)
        return await media_bucket.add_file(bucket_name, file_binary, bucket_key)

    async def get_uploaded_file(self, bucket_name: str, bucket_key: str):
        conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
        media_bucket = bucket.Bucket(conn, bucket_name)
        return await media_bucket.get_file(bucket_name, bucket_key)

    async def fetch_bucket_files(self, bucket_name: str):
        conn = connection.Connection(client_token=cfg.QARNOT_TOKEN)
        media_bucket = bucket.Bucket(conn, bucket_name)
        bucket_local_copy_directory = 'bucket_local_copy'
        if not os.path.exists('bucket_local_copy_directory'):
            os.makedirs('bucket_local_copy_directory')
        return await media_bucket.get_all_files(bucket_local_copy_directory)
