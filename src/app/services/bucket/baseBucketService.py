from abc import ABC
from abc import abstractmethod


class BaseBucketService(ABC):
    """Abstract BucketService class to setup an interface regardless of the actual service."""

    @abstractmethod
    async def upload_file(self, bucket_key: str, file_binary: bin):
        pass

    @abstractmethod
    async def get_uploaded_file(self, bucket_key: str):
        pass

    @abstractmethod
    async def fetch_bucket_filenames(self):
        pass

    @abstractmethod
    async def flush_after_get_uploaded_file(self, filename):
        pass
