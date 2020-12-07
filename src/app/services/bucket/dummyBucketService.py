from app.services.bucket.baseBucketService import BaseBucketService
from app import config as cfg


class DummyBucketService(BaseBucketService):
    """Dummy class used for testing purpose. """

    async def upload_file(self, bucket_key: str, file_binary: bin):
        return True

    async def get_uploaded_file(self, bucket_key: str):
        return cfg.DUMMY_BUCKET_FILE

    async def fetch_bucket_filenames(self):
        return []
    
    async def flush_after_get_uploaded_file(self, filename):
        return True
