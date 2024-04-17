# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def get_api_status():
    """
    Returns the status of the API
    """
    # TODO : implement a more complexe behavior to check if everything is initialized for ex
    return {"status": "API is running smoothly"}
