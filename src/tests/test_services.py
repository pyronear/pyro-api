from app.services import bucket_service, resolve_bucket_key
from app import config as cfg


def test_resolve_bucket_key(monkeypatch):
    file_name = "myfile.jpg"
    # Check that it returns the same thing when bucket folder is not set
    assert resolve_bucket_key(file_name) == file_name

    # Check that bucket folder is prepended in bucket key if set
    bucket_subfolder = "my/bucket/subfolder"
    origin_value = cfg.BUCKET_NAME
    monkeypatch.setattr(cfg, "BUCKET_NAME", f"my_bucket_name/{bucket_subfolder}")
    assert resolve_bucket_key(file_name) == f"{bucket_subfolder}/{file_name}"

    # Same if the bucket folder is specified
    monkeypatch.setattr(cfg, "BUCKET_NAME", origin_value)
    assert resolve_bucket_key(file_name, bucket_subfolder) == f"{bucket_subfolder}/{file_name}"
