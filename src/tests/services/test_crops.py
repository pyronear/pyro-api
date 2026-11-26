import io
from datetime import timedelta
from typing import List, Optional, Tuple, cast

import pytest  # type: ignore
from httpx import AsyncClient
from PIL import Image
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.time import utcnow
from app.crud import SequenceCRUD
from app.models import COMPLETION_PENDING, Detection, Sequence
from app.services import crops
from app.services.crops import process_next_due_crops, refresh_sequence_crops, square_box
from app.services.storage import s3_service

CAMERA_ID, POSE_ID, ORGANIZATION_ID = 1, 1, 1
# A 1280x720 native crop covering a third of each side: the frame is 3840x2160
WINDOW = "(0.35,0.35,0.683333,0.683333)"
RED, BLUE = (255, 0, 0), (0, 0, 255)


@pytest.mark.parametrize(
    ("bboxes", "expected"),
    [
        # Square in pixels (16:9 frame), centered on the bboxes, 20% wider than their longest side
        ((0.4, 0.4, 0.5, 0.5), (0.39, 0.343333, 0.51, 0.556667)),
        ((0.4, 0.4, 0.5, 0.6), (0.3825, 0.38, 0.5175, 0.62)),
        # Shifted back inside the frame near an edge
        ((0.0, 0.9, 0.1, 1.0), (0.0, 0.786667, 0.12, 1.0)),
        # No larger than the frame
        ((0.1, 0.1, 0.9, 0.9), (0.21875, 0.0, 0.78125, 1.0)),
    ],
)
def test_square_box(bboxes, expected):
    box = square_box(bboxes, 3840, 2160)
    assert box == pytest.approx(expected, abs=1e-6)
    assert (box[2] - box[0]) * 3840 == pytest.approx((box[3] - box[1]) * 2160, abs=0.01)


def _jpeg(color: Tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (1280, 720), color).save(buffer, format="JPEG")
    return buffer.getvalue()


def _bucket():
    return s3_service.get_bucket(s3_service.resolve_bucket_name(ORGANIZATION_ID))


async def _add_sequence(session: AsyncSession, is_validated: bool = True) -> Sequence:
    now = utcnow()
    sequence_ = Sequence(
        camera_id=CAMERA_ID,
        pose_id=POSE_ID,
        camera_azimuth=180.0,
        started_at=now - timedelta(minutes=5),
        last_seen_at=now,
        is_validated=is_validated,
    )
    session.add(sequence_)
    await session.commit()
    await session.refresh(sequence_)
    return sequence_


async def _add_detection(
    session: AsyncSession, sequence_: Sequence, bbox: str, window: Optional[str] = WINDOW, **kwargs
) -> Detection:
    """A detection of the sequence with a blue frame and, with a window, a red native crop"""
    detection = Detection(
        camera_id=CAMERA_ID, pose_id=POSE_ID, sequence_id=sequence_.id, bucket_key="pending", bbox=bbox, **kwargs
    )
    session.add(detection)
    await session.commit()
    await session.refresh(detection)
    detection.bucket_key = f"test-frame-{detection.id}.jpg"
    _bucket().upload_file(detection.bucket_key, io.BytesIO(_jpeg(BLUE)))
    if window is not None:
        detection.native_crop_window = window
        detection.native_crop_bucket_key = f"test-native-crop-{detection.id}.jpg"
        _bucket().upload_file(detection.native_crop_bucket_key, io.BytesIO(_jpeg(RED)))
    session.add(detection)
    await session.commit()
    return detection


async def _crop_keys(session: AsyncSession, detections: List[Detection]) -> List[Optional[str]]:
    for detection in detections:
        await session.refresh(detection)
    return [detection.crop_bucket_key for detection in detections]


def _crop_color(crop_bucket_key: Optional[str]) -> Tuple[int, int, int]:
    crop = Image.open(io.BytesIO(_bucket().download_file(cast(str, crop_bucket_key))))
    assert crop.size == (224, 224)
    red, green, blue = crop.convert("RGB").getpixel((112, 112))
    # JPEG is lossy: snap to the pure color
    return round(red / 255) * 255, round(green / 255) * 255, round(blue / 255) * 255


@pytest.mark.asyncio
async def test_refresh_sequence_crops(detection_session: AsyncSession):
    sequence_ = await _add_sequence(detection_session)
    first = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    second = await _add_detection(detection_session, sequence_, "[(0.51,0.5,0.53,0.54,0.7)]")
    # Left alone: a frame without bbox, and a detection the engine sent with its own crop and no native crop
    continuity = await _add_detection(detection_session, sequence_, "[]", window=None)
    legacy = await _add_detection(
        detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]", window=None, crop_bucket_key="engine-crop.jpg"
    )

    await refresh_sequence_crops(sequence_.id)

    first_keys = await _crop_keys(detection_session, [first, second])
    assert first_keys[0].startswith(f"crop_{first.id}_")
    assert first_keys[1].startswith(f"crop_{second.id}_")
    # Cut from the native crops
    assert [_crop_color(key) for key in first_keys] == [RED, RED]
    assert await _crop_keys(detection_session, [continuity, legacy]) == [None, "engine-crop.jpg"]
    await detection_session.refresh(sequence_)
    # One box for the whole sequence, covering the bboxes of its detections
    assert sequence_.crop_box == "(0.497000,0.488000,0.533000,0.552000)"

    # A bbox inside the box: only the new detection is cropped
    third = await _add_detection(detection_session, sequence_, "[(0.51,0.51,0.52,0.52,0.6)]")
    await refresh_sequence_crops(sequence_.id)
    assert await _crop_keys(detection_session, [first, second]) == first_keys
    third_key = (await _crop_keys(detection_session, [third]))[0]
    assert _crop_color(third_key) == RED
    await detection_session.refresh(sequence_)
    assert sequence_.crop_box == "(0.497000,0.488000,0.533000,0.552000)"

    # A bbox outside the box: the box grows and every crop is cut again. The new box is larger than
    # the native crops, so the crops are cut from the frames.
    fourth = await _add_detection(detection_session, sequence_, "[(0.2,0.2,0.25,0.25,0.6)]")
    await refresh_sequence_crops(sequence_.id)
    new_keys = await _crop_keys(detection_session, [first, second, third, fourth])
    assert set(new_keys).isdisjoint([*first_keys, third_key])
    assert [_crop_color(key) for key in new_keys] == [BLUE] * 4
    assert not any(_bucket().check_file_existence(key) for key in [*first_keys, third_key])
    await detection_session.refresh(sequence_)
    assert sequence_.crop_box == "(0.167000,0.018000,0.563000,0.722000)"

    # Nothing changed: nothing is cut
    await refresh_sequence_crops(sequence_.id)
    assert await _crop_keys(detection_session, [first, second, third, fourth]) == new_keys


@pytest.mark.asyncio
async def test_refresh_sequence_crops_skips_unusable_images(detection_session: AsyncSession):
    sequence_ = await _add_sequence(detection_session)
    broken = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    _bucket().upload_file(broken.native_crop_bucket_key, io.BytesIO(b"not an image"))
    missing = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    _bucket().delete_file(missing.native_crop_bucket_key)
    valid = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")

    await refresh_sequence_crops(sequence_.id)

    keys = await _crop_keys(detection_session, [broken, missing, valid])
    assert keys[:2] == [None, None]
    assert _crop_color(keys[2]) == RED


@pytest.mark.asyncio
async def test_refresh_sequence_crops_waits_for_validation(detection_session: AsyncSession):
    sequence_ = await _add_sequence(detection_session, is_validated=False)
    detection = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    await refresh_sequence_crops(sequence_.id)
    assert await _crop_keys(detection_session, [detection]) == [None]
    await detection_session.refresh(sequence_)
    assert sequence_.crop_box is None


@pytest.mark.asyncio
async def test_crop_queue(detection_session: AsyncSession, monkeypatch):
    sequences = SequenceCRUD(detection_session)
    pending = await _add_sequence(detection_session, is_validated=False)
    await sequences.mark_crops_due(pending.id)
    await detection_session.commit()
    await detection_session.refresh(pending)
    # Crops are only cut once the sequence is validated
    assert pending.crops_due_at is None

    sequence_ = await _add_sequence(detection_session)
    detection = await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    sequence_.completion_status = COMPLETION_PENDING
    detection_session.add(sequence_)
    await detection_session.commit()
    # The validation queues the first cut
    assert await sequences.finish_sequence_completion(sequence_.id)
    await detection_session.refresh(sequence_)
    assert sequence_.crops_due_at is not None

    # A failed job stays due, and is left alone until its retry time
    async def failing_refresh(sequence_id: int) -> None:  # ruff:ignore[unused-async]
        raise RuntimeError("S3 is down")

    with monkeypatch.context() as patch:
        patch.setattr(crops, "refresh_sequence_crops", failing_refresh)
        assert await process_next_due_crops() is True
    assert await process_next_due_crops() is False
    await detection_session.refresh(sequence_)
    assert sequence_.crops_due_at is not None
    assert sequence_.crops_lease_until > utcnow()

    # A sequence that changes while it is refreshed stays due
    sequence_.crops_lease_until = None
    detection_session.add(sequence_)
    await detection_session.commit()
    claimed = await sequences.claim_due_crops(60)
    assert claimed == (sequence_.id, sequence_.crops_due_at)
    await sequences.mark_crops_due(sequence_.id)
    await sequences.release_crops(*claimed)
    await detection_session.refresh(sequence_)
    assert sequence_.crops_due_at > claimed[1]
    assert sequence_.crops_lease_until is None

    # A job that is done leaves the queue
    assert await process_next_due_crops() is True
    assert await process_next_due_crops() is False
    await detection_session.refresh(sequence_)
    assert sequence_.crops_due_at is None
    assert (await _crop_keys(detection_session, [detection]))[0] is not None


@pytest.mark.asyncio
async def test_create_detection_queues_the_crops_of_a_validated_sequence(
    async_client: AsyncClient, detection_session: AsyncSession, mock_img: bytes
):
    sequence_ = await _add_sequence(detection_session)
    await _add_detection(detection_session, sequence_, "[(0.5,0.5,0.52,0.53,0.6)]")
    response = await async_client.post(
        "/detections",
        data={"pose_id": POSE_ID, "bboxes": "[(0.5,0.5,0.52,0.53,0.6)]", "native_crop_windows": f"[{WINDOW}]"},
        files={
            "file": ("frame.jpg", _jpeg(BLUE), "image/jpeg"),
            "native_crop": ("native_crop.jpg", _jpeg(RED), "image/jpeg"),
            # Ignored: the API cuts the crop itself
            "crop": ("crop.jpg", mock_img, "image/jpeg"),
        },
        headers=pytest.get_token(CAMERA_ID, ["camera"], ORGANIZATION_ID),
    )
    assert response.status_code == 201, response.text
    assert response.json()["sequence_id"] == sequence_.id
    assert response.json()["crop_bucket_key"] is None
    await detection_session.refresh(sequence_)
    assert sequence_.crops_due_at is not None

    assert await process_next_due_crops() is True
    detection = await detection_session.get(Detection, response.json()["id"])
    await detection_session.refresh(detection)
    assert _crop_color(detection.crop_bucket_key) == RED
