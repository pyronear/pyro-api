# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from app.api.external import post_request


def test_post_request():
    response = post_request("https://httpbin.org/post")
    assert response.status_code == 200
