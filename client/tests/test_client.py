import time
from contextlib import nullcontext
from copy import deepcopy
from urllib.parse import urljoin

import pytest
import requests
from requests.exceptions import ConnectionError, ReadTimeout

from pyroclient.client import Client, convert_loc_to_str
from pyroclient.exceptions import HTTPRequestException


def _test_route_return(response, return_type, status_code=200):
    assert response.status_code == status_code, print(response.text)
    assert isinstance(response.json(), return_type)

    return response.json()


@pytest.mark.parametrize(
    "url, login, pwd, timeout, expected_error",
    [
        # Wrong credentials
        ["http://localhost:8080", "invalid_login", "invalid_pwd", 10, HTTPRequestException],
        # Incorrect URL port
        ["http://localhost:8003", "dummy_login", "dummy&P@ssw0rd!", 10, ConnectionError],
        # Timeout
        ["http://localhost:8080", "dummy_login", "dummy&P@ssw0rd!", 0.01, ReadTimeout],
        # Correct
        ["http://localhost:8080", "dummy_login", "dummy&P@ssw0rd!", 10, None],
    ],
)
def test_client_constructor(url, login, pwd, timeout, expected_error):
    if expected_error is None:
        api_client = Client(url, login, pwd, timeout=timeout)
        assert isinstance(api_client.headers, dict)
    else:
        with pytest.raises(expected_error):
            Client(url, login, pwd, timeout=timeout)


def test_client_refresh_token(admin_client):
    # Check token refresh
    prev_headers = deepcopy(admin_client.headers)
    # In case the 2nd token creation request is done in the same second, since the expiration is truncated to the
    # second, it returns the same token
    time.sleep(1)
    admin_client.refresh_token("dummy_login", "dummy&P@ssw0rd!")
    assert prev_headers != admin_client.headers


def test_client_device(admin_client, device_client, mock_img):
    # Every on-site interactions (critical priority)

    # Get self
    device = _test_route_return(device_client.get_self_device(), dict)
    # Heartbeat
    last_ping = device["last_ping"]
    updated_device = _test_route_return(device_client.heartbeat(), dict)
    assert isinstance(updated_device["last_ping"], str)
    if isinstance(last_ping, str):
        assert updated_device["last_ping"] > last_ping

    # Alert
    media_id = _test_route_return(device_client.create_media_from_device(), dict, 201)["id"]
    _test_route_return(device_client.send_alert_from_device(1.0, 2.0, media_id, 0.0), dict, 201)
    response = device_client.upload_media(media_id, mock_img)
    if response.status_code == 200:
        media = _test_route_return(response, dict)
        assert isinstance(media["bucket_key"], str)
        _test_route_return(admin_client.get_media_url(media_id), str)
        # Delete media
        response = requests.delete(
            urljoin("http://localhost:8080", f"media/{media_id}"), headers=admin_client.headers, timeout=5
        )
        assert response.status_code == 200


def test_client_user(setup, user_client, mock_img):
    # Every platform interaction (medium priority)

    _test_route_return(user_client.get_user_devices(), list)
    sites = _test_route_return(user_client.get_sites(), list)
    _test_route_return(user_client.get_site_devices(sites[0]["id"]), list)
    events = _test_route_return(user_client.get_past_events(), list)
    events = _test_route_return(user_client.get_unacknowledged_events(), list)
    event = _test_route_return(user_client.acknowledge_event(events[0]["id"]), dict)
    assert event["is_acknowledged"]
    _test_route_return(user_client.get_all_alerts(), list)
    _test_route_return(user_client.get_ongoing_alerts(), list)
    _test_route_return(user_client.get_alerts_for_event(events[0]["id"]), list)
    assert user_client.get_media_url(1).status_code == 404


@pytest.mark.parametrize(
    "loc, error, expected",
    [
        (None, nullcontext(), "[]"),
        ([], nullcontext(), "[]"),
        ([[0, 0, 1, 1, 1]], nullcontext(), "[[0.000,0.000,1.000,1.000,1.000]]"),
        ([0] * 10, pytest.raises(ValueError), None),
        ("something else", pytest.raises(ValueError), None),
        ([[]], pytest.raises(ValueError), None),
        ([[0, -0.1, 1, 1, 1]], pytest.raises(ValueError), None),
        ([[0, 0.1, 1, 1.5, 1]], pytest.raises(ValueError), None),
        ([[0] * 10], pytest.raises(ValueError), None),
    ],
)
def test_convert_loc_to_str(loc, error, expected):
    with error:
        assert convert_loc_to_str(loc) == expected
