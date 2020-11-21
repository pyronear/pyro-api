from app.services.bucket.s3 import S3Service
from app.services.bucket.baseBucketService import BaseBucketService

bucket_service = S3Service()

__all__ = ['bucket_service']
