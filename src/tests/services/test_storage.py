from app.services.storage import S3Bucket, s3_bucket


def test_s3_bucket():
    assert isinstance(s3_bucket, S3Bucket)
