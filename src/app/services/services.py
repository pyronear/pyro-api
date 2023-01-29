# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from app.services.bucket import S3Bucket

__all__ = ["bucket_service"]


bucket_service = S3Bucket()
