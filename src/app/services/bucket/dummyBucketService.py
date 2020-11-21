from app.services.bucket.baseBucketService import BaseBucketService


class DummyBucketService(BaseBucketService):
    def __init__(self):
        """Dummy class used for testing purpose.
        """

    async def create_bucket(self, bucket_name):
        return True

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        return True

    async def get_uploaded_file(self, bucket_name: str, object_name: str, target_location: str):
        return "DummyFile"

    async def fetch_bucket_files(self, bucket_name: str):
        return []
