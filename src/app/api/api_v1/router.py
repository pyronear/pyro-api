# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from fastapi import APIRouter

from app.api.api_v1.endpoints import cameras, detections, login, organizations, poses, sequences, users, webhooks

api_router = APIRouter(redirect_slashes=True)
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(poses.router, prefix="/poses", tags=["poses"])
api_router.include_router(detections.router, prefix="/detections", tags=["detections"])
api_router.include_router(sequences.router, prefix="/sequences", tags=["sequences"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
