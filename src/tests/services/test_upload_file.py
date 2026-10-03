import hashlib
import io
import threading
from datetime import datetime
from unittest.mock import Mock

import anyio
import pytest
from fastapi import HTTPException, UploadFile

from app.services import storage


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "failed", "corrupt"])
async def test_upload_streams_hashes_preserves_bytes_and_errors(outcome, monkeypatch):
    payload = b"GIF89a" + bytes(2 * 1024 * 1024)
    request_thread = threading.get_ident()

    class BoundedFile(io.BytesIO):
        def read(self, size=-1):
            assert 0 < size <= 64 * 1024
            return super().read(size)

    def upload(key, file):
        assert threading.get_ident() != request_thread
        assert file.tell() == 0
        assert b"".join(iter(lambda: file.read(65536), b"")) == payload
        return outcome != "failed"

    bucket = Mock()
    bucket.upload_file.side_effect = upload
    etag = "corrupt" if outcome == "corrupt" else hashlib.md5(payload, usedforsecurity=False).hexdigest()
    bucket.get_file_metadata.return_value = {"ETag": f'"{etag}"'}
    monkeypatch.setattr(storage.s3_service, "get_bucket", lambda _: bucket)
    monkeypatch.setattr(storage, "utcnow", lambda: datetime(2026, 10, 3, 12))
    with BoundedFile(payload) as stream:
        file = UploadFile(file=stream)
        key = f"crop_2_7-20261003120000-{hashlib.sha256(payload).hexdigest()[:8]}.gif"
        if outcome == "success":
            assert await storage.upload_file(file, 1, 7, "crop_2_") == key
        else:
            detail = "Failed upload" if outcome == "failed" else "Data was corrupted during upload"
            with pytest.raises(HTTPException, match=detail) as error:
                await storage.upload_file(file, 1, 7, "crop_2_")
            assert error.value.status_code == 500
    if outcome == "corrupt":
        bucket.delete_file.assert_called_once_with(key)
    else:
        bucket.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_upload_pool_is_bounded_and_keeps_event_loop_responsive(monkeypatch):
    started = []
    release = threading.Event()
    ready = anyio.Event()

    def upload(*args):
        started.append(threading.get_ident())
        if len(started) == 8:
            anyio.from_thread.run_sync(ready.set)
        assert release.wait(timeout=5)
        return "uploaded"

    monkeypatch.setattr(storage, "_upload_file", upload)
    try:
        async with anyio.create_task_group() as group:
            for _ in range(9):
                group.start_soon(storage.upload_file, None, 1, 7)
            with anyio.fail_after(3):
                await ready.wait()
            await anyio.sleep(0.01)
            assert len(started) == 8
            release.set()
    finally:
        release.set()
    assert len(started) == 9
