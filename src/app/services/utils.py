from typing import Optional

import app.config as cfg

__all__ = ["resolve_bucket_key"]


def resolve_bucket_key(file_name: str, bucket_folder: Optional[str] = None) -> str:
    """Prepend file name with bucket subfolder"""

    if not isinstance(bucket_folder, str) and isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
        bucket_folder = cfg.BUCKET_MEDIA_FOLDER

    return f"{bucket_folder}/{file_name}" if isinstance(bucket_folder, str) else file_name
