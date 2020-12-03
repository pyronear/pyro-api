from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class QarnotBucketService(BaseBucketService):

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        return True

    async def get_uploaded_file(self, bucket_name: str, bucket_key: str):
        return cfg.DUMMY_BUCKET_FILE

    async def fetch_bucket_files(self, bucket_name: str):
        return []
