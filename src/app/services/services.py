# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from app.services.bucket import QarnotBucket

__all__ = ['bucket_service']


bucket_service = QarnotBucket()
