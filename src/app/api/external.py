# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Optional

import requests
from pydantic import BaseModel


def post_request(url: str, payload: Optional[BaseModel] = None) -> requests.Response:
    """Performs a POST request to a given URL

    Args:
        url: URL to send the POST request to
        payload: payload to be sent
    Returns:
        HTTP response
    """
    kwargs = {} if payload is None else {"json": payload}
    return requests.post(url, headers={"Content-Type": "application/json"}, **kwargs)
