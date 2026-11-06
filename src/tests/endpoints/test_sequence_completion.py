import pytest
from sqlalchemy import update

from app.models import COMPLETION_COMPLETED, COMPLETION_FAILED, COMPLETION_PENDING, Sequence


@pytest.mark.parametrize("scope", ["agent", "user", "camera", None])
@pytest.mark.asyncio
async def test_completion_recovery_requires_admin(async_client, scope):
    headers = pytest.get_token(1, [scope], 1) if scope else {}
    expected = 403 if scope else 401
    response = await async_client.get("/sequences/completion/failed", headers=headers)
    assert response.status_code == expected
    response = await async_client.post("/sequences/1/completion/retry", headers=headers)
    assert response.status_code == expected


@pytest.mark.asyncio
async def test_failed_completions_are_paginated_across_organizations(async_client, sequence_session):
    await sequence_session.exec(
        update(Sequence).values(is_validated=True, completion_status=COMPLETION_FAILED, completion_attempts=5)
    )
    await sequence_session.commit()
    auth = pytest.get_token(1, ["admin"], 1)
    first = await async_client.get("/sequences/completion/failed?limit=1", headers=auth)
    second = await async_client.get("/sequences/completion/failed?limit=1&offset=1", headers=auth)
    assert first.status_code == second.status_code == 200
    assert [row["id"] for row in first.json()] == [1]
    assert [row["id"] for row in second.json()] == [2]
    for query in ("limit=0", "limit=501", "offset=-1"):
        response = await async_client.get(f"/sequences/completion/failed?{query}", headers=auth)
        assert response.status_code == 422


@pytest.mark.parametrize(
    ("validated", "completion", "verdict"),
    [
        (False, None, None),
        (False, None, "failed"),
        (True, COMPLETION_PENDING, "model"),
        (True, COMPLETION_COMPLETED, "fail_open_stale"),
    ],
)
@pytest.mark.asyncio
async def test_retry_rejects_sequences_without_failed_completion(
    async_client, sequence_session, validated, completion, verdict
):
    await sequence_session.exec(
        update(Sequence)
        .where(Sequence.id == 1)
        .values(is_validated=validated, completion_status=completion, validation_status=verdict)
    )
    await sequence_session.commit()
    auth = pytest.get_token(1, ["admin"], 1)
    response = await async_client.post("/sequences/1/completion/retry", headers=auth)
    assert response.status_code == 409
    row = await sequence_session.get(Sequence, 1)
    assert row.is_validated == validated
    assert row.completion_status == completion
    assert row.validation_status == verdict


@pytest.mark.asyncio
async def test_retry_missing_sequence_returns_not_found(async_client, sequence_session):
    response = await async_client.post("/sequences/999/completion/retry", headers=pytest.get_token(1, ["admin"], 1))
    assert response.status_code == 404
