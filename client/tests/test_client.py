# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import time
from copy import deepcopy

import pytest
from requests import ConnectionError

from pyroclient import client
from pyroclient.exceptions import HTTPRequestException


def _test_route_return(response, return_type, status_code=200):
    assert response.status_code == status_code
    assert isinstance(response.json(), return_type)

    return response.json()


def test_client():

    # Wrong credentials
    with pytest.raises(HTTPRequestException):
        client.Client("http://localhost:8080", "invalid_login", "invalid_pwd")

    # Incorrect URL port
    with pytest.raises(ConnectionError):
        client.Client("http://localhost:8003", "dummy_login", "dummy&P@ssw0rd!")

    api_client = client.Client("http://localhost:8080", "dummy_login", "dummy&P@ssw0rd!")

    # Sites
    site_id = _test_route_return(
        api_client.create_no_alert_site(lat=44.870959, lon=4.395387, name="dummy_tower", country="FR", geocode="07"),
        dict,
        201,
    )["id"]
    sites = _test_route_return(api_client.get_sites(), list)
    assert sites[-1]["id"] == site_id

    # Devices
    all_devices = _test_route_return(api_client.get_my_devices(), list)
    _test_route_return(api_client.get_site_devices(site_id), list)

    # Alerts
    _test_route_return(api_client.get_all_alerts(), list)
    _test_route_return(api_client.get_ongoing_alerts(), list)
    # Events
    _test_route_return(api_client.get_unacknowledged_events(), list)
    _test_route_return(api_client.get_past_events(), list)

    if len(all_devices) > 0:
        # Media
        media_id = _test_route_return(api_client.create_media(all_devices[0]["id"]), dict, 201)["id"]
        # Create event
        event_id = _test_route_return(api_client.create_event(0.0, 0.0), dict, 201)["id"]
        # Create an alert
        _ = _test_route_return(
            api_client.send_alert(0.0, 0.0, event_id, all_devices[0]["id"], media_id=media_id), dict, 201
        )
        # Acknowledge it
        updated_event = _test_route_return(api_client.acknowledge_event(event_id), dict)
        assert updated_event["is_acknowledged"]

    # Check token refresh
    prev_headers = deepcopy(api_client.headers)
    # In case the 2nd token creation request is done in the same second, since the expiration is truncated to the
    # second, it returns the same token
    time.sleep(1)
    api_client.refresh_token("dummy_login", "dummy&P@ssw0rd!")
    assert prev_headers != api_client.headers
