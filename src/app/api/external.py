# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Optional

import requests
from pydantic import BaseModel


def post_request(url: str, payload: Optional[BaseModel] = None, timeout: int = 10) -> requests.Response:
    """Performs a POST request to a given URL

    Args:
        url: URL to send the POST request to
        payload: payload to be sent
        timeout: timeout for the HTTP request
    Returns:
        HTTP response
    """
    return requests.post(url, timeout=timeout, json={} if payload is None else payload.model_dump())
