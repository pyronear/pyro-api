import json
import pytest
from copy import deepcopy

from app.services.bucket.baseBucketService import BaseBucketService
from app.services import bucket_service


def test_bucket_service_is_BaseBucketService(test_app, monkeypatch):
    assert isinstance(bucket_service, BaseBucketService), "selected service is not an instance of BaseBucketService"
