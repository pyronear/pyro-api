# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import asyncio
from datetime import datetime, timezone
from threading import Event

import pytest
from fastapi.testclient import TestClient

from inference import main
from inference.schemas import TriangulationRequest

client = TestClient(main.app)


def _sequence(id_: int = 1) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": id_,
        "pose_id": id_,
        "lat": 43.3,
        "lon": 5.4,
        "sequence_azimuth": 45.0,
        "cone_angle": 10.0,
        "is_wildfire": None,
        "started_at": now,
        "last_seen_at": now,
    }


def test_status_does_not_require_authentication() -> None:
    assert client.get("/status").json() == {"status": "ok"}


def test_compute_endpoints_require_bearer_token(monkeypatch) -> None:
    monkeypatch.setenv("INFERENCE_API_TOKEN", "secret")
    assert client.post("/v1/triangulate", json={"sequences": []}).status_code == 401
    assert (
        client.post("/v1/triangulate", json={"sequences": []}, headers={"Authorization": "secret"}).status_code == 401
    )
    assert client.post("/v1/timezone", json={"lat": 43.3, "lon": 5.4}).status_code == 401


def test_triangulate_validates_and_returns_canonical_groups(monkeypatch) -> None:
    monkeypatch.setenv("INFERENCE_API_TOKEN", "secret")
    headers = {"Authorization": "Bearer secret"}

    response = client.post("/v1/triangulate", json={"sequences": [_sequence()]}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"groups": [{"sequence_ids": [1], "smoke_location": None}]}
    assert client.post("/v1/triangulate", json={"sequences": [_sequence()]}, headers=headers).json() == response.json()
    duplicate = client.post("/v1/triangulate", json={"sequences": [_sequence(), _sequence()]}, headers=headers)
    assert duplicate.status_code == 422
    invalid = _sequence()
    invalid["lat"] = 91
    assert client.post("/v1/triangulate", json={"sequences": [invalid]}, headers=headers).status_code == 422
    zero_angle = _sequence(2)
    zero_angle["cone_angle"] = 0
    assert client.post("/v1/triangulate", json={"sequences": [zero_angle]}, headers=headers).status_code == 200


@pytest.mark.asyncio
async def test_triangulation_is_serialized_without_blocking_health(monkeypatch) -> None:
    entered = Event()
    release = Event()
    calls = 0
    active = 0
    max_active = 0

    def slow_compute(*_args, **_kwargs):
        nonlocal active, calls, max_active
        calls += 1
        active += 1
        max_active = max(max_active, active)
        entered.set()
        release.wait(timeout=2)
        active -= 1
        return []

    monkeypatch.setattr(main, "compute_overlap", slow_compute)
    payload = TriangulationRequest.model_validate({"sequences": [_sequence()]})
    first = asyncio.create_task(main.triangulate(payload))
    assert await asyncio.to_thread(entered.wait, 1)
    second = asyncio.create_task(main.triangulate(payload))

    await asyncio.sleep(0.05)
    calls_before_release = calls
    health = await asyncio.wait_for(main.service_status(), timeout=0.1)
    release.set()
    await asyncio.gather(first, second)

    assert health == {"status": "ok"}
    assert calls_before_release == 1
    assert calls == 2
    assert max_active == 1


def test_timezone_validation_and_utc_fallback(monkeypatch) -> None:
    monkeypatch.setenv("INFERENCE_API_TOKEN", "secret")
    monkeypatch.setattr(main, "timezone_finder", type("Finder", (), {"timezone_at": lambda *_args, **_: None})())
    headers = {"Authorization": "Bearer secret"}

    response = client.post("/v1/timezone", json={"lat": 0.0, "lon": -140.0}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"timezone": "UTC"}
    assert client.post("/v1/timezone", json={"lat": 91, "lon": 0}, headers=headers).status_code == 422
