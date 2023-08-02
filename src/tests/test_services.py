import pytest

from app.services import bucket_service, resolve_bucket_key
from app.services.bucket import S3Bucket
from app.services.utils import cfg


def test_resolve_bucket_key(monkeypatch):
    file_name = "myfile.jpg"
    bucket_subfolder = "my/bucket/subfolder"

    # Same if the bucket folder is specified
    assert resolve_bucket_key(file_name, bucket_subfolder) == f"{bucket_subfolder}/{file_name}"

    # Check that bucket folder is prepended in bucket key if set
    origin_value = cfg.BUCKET_MEDIA_FOLDER
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", bucket_subfolder)
    assert resolve_bucket_key(file_name) == f"{bucket_subfolder}/{file_name}"

    # Check that it returns the same thing when bucket folder is not set
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", None)
    assert resolve_bucket_key(file_name) == file_name
    monkeypatch.setattr(cfg, "BUCKET_MEDIA_FOLDER", origin_value)


def test_bucket_service():
    assert isinstance(bucket_service, S3Bucket)


@pytest.mark.parametrize("filename, is_binary", [("test.txt", False), ("test.binary", True)])
@pytest.mark.asyncio
async def test_upload_file(filename, is_binary, tmp_path):
    fname = str(tmp_path / filename)
    with open(fname, "wb" if is_binary else "w") as f:
        f.write(bytearray(b"This is a test") if is_binary else "This is a test")
    assert await bucket_service.upload_file(f"test/{filename}", open(fname, "rb") if is_binary else fname)
    assert await bucket_service.get_file_metadata(f"test/{filename}")
    await bucket_service.delete_file(f"test/{filename}")
