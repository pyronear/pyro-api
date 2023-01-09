# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging

from qarnot.connection import Connection

from app import config as cfg

from .s3 import S3Bucket

__all__ = ["QarnotBucket"]


logger = logging.getLogger("uvicorn.warning")


class QarnotBucket(S3Bucket):
    """Storage bucket manipulation object on Qarnot computing"""

    def _connect_to_storage(self) -> None:
        """Connect to the CSP bucket"""
        self._s3 = Connection(client_token=cfg.QARNOT_TOKEN)._s3client
        if isinstance(cfg.BUCKET_MEDIA_FOLDER, str):
            self._media_folder = cfg.BUCKET_MEDIA_FOLDER
