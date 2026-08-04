# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import os
from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from timezonefinder import TimezoneFinder

from inference.overlap import compute_overlap
from inference.schemas import (
    TimezoneRequest,
    TimezoneResponse,
    TriangulationRequest,
    TriangulationResponse,
)

app = FastAPI(title="Pyronear inference service")
timezone_finder = TimezoneFinder()


def _authorize(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.environ.get("INFERENCE_API_TOKEN")
    supplied = authorization.removeprefix("Bearer ") if authorization and authorization.startswith("Bearer ") else ""
    if not expected or not compare_digest(supplied, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")


@app.get("/status")
async def service_status() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/triangulate", dependencies=[Depends(_authorize)])
async def triangulate(payload: TriangulationRequest) -> TriangulationResponse:
    groups = compute_overlap(
        payload.sequences,
        time_relaxation_seconds=float(os.environ.get("TRIANGULATION_RELAXATION_SECONDS") or 30 * 60),
        min_apex_km=float(os.environ.get("TRIANGULATION_MIN_APEX_DISTANCE_KM") or 0.1),
    )
    return TriangulationResponse(groups=groups)


@app.post("/v1/timezone", dependencies=[Depends(_authorize)])
async def resolve_timezone(payload: TimezoneRequest) -> TimezoneResponse:
    return TimezoneResponse(timezone=timezone_finder.timezone_at(lat=payload.lat, lng=payload.lon) or "UTC")
