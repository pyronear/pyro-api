from abc import ABC
from abc import abstractmethod


class BaseBucketService(ABC):
    """Abstract BucketService class to setup an interface regardless of the actual service."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def create_bucket(self, bucket_name: str):
        pass

    @abstractmethod
    def upload_file(self, bucket_name: str, target_location: str, file_binary: bin):
        pass

    @abstractmethod
    def get_uploaded_file(self, bucket_name: str, object_name: str, target_location: str):
        pass

    @abstractmethod
    def fetch_bucket_files(self, bucket_name: str):
        pass
