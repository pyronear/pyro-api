from urllib.parse import urljoin

import pytest
import requests

from pyroclient.client import Client
from pyroclient.exceptions import HTTPRequestException

API_URL = "http://localhost:8080"


@pytest.fixture(scope="session")
def mock_img():
    # Get Pyronear logo
    URL = "https://avatars.githubusercontent.com/u/61667887?s=200&v=4"
    return requests.get(URL).content


@pytest.fixture(scope="function")
def admin_client():
    return Client(API_URL, "dummy_login", "dummy&P@ssw0rd!")


@pytest.fixture(scope="function")
def user_client(admin_client):
    user_creds = ("dummy_user", "dummy_pwd")
    try:
        client = Client(API_URL, *user_creds)
    except HTTPRequestException:
        # Log as admin & create a user
        payload = {"login": user_creds[0], "password": user_creds[1], "group_id": 1}
        response = requests.post(urljoin(API_URL, "users"), json=payload, headers=admin_client.headers)
        assert response.status_code == 201
        # Log as that device
        client = Client(API_URL, *user_creds)

    return client


@pytest.fixture(scope="function")
def device_client(admin_client):
    device_creds = ("dummy_device", "dummy_pwd")
    try:
        client = Client(API_URL, *device_creds)
    except HTTPRequestException:
        # Log as admin & create a device
        payload = {
            "login": device_creds[0],
            "password": device_creds[1],
            "owner_id": 1,
            "specs": "dummy",
            "angle_of_view": 68.0,
            "group_id": 1,
        }
        response = requests.post(urljoin(API_URL, "devices"), json=payload, headers=admin_client.headers)
        assert response.status_code == 201
        # Log as that device
        client = Client(API_URL, *device_creds)

    return client


@pytest.fixture(scope="function")
def setup(admin_client):
    # Create a site
    payload = {"name": "dummy_site", "lat": 0.0, "lon": 0.0, "country": "FR", "geocode": "code", "group_id": 1}
    response = requests.post(urljoin(API_URL, "sites"), json=payload, headers=admin_client.headers)
    assert response.status_code == 201, print(response.text)
    # Event
    payload = {"lat": 0.0, "lon": 0.0}
    response = requests.post(urljoin(API_URL, "events"), json=payload, headers=admin_client.headers)
    assert response.status_code == 201
    event_id = response.json()["id"]
    # Media
    payload = {"device_id": 1}
    response = requests.post(urljoin(API_URL, "media"), json=payload, headers=admin_client.headers)
    assert response.status_code == 201
    media_id = response.json()["id"]
    # Alert
    payload = {"lat": 0.0, "lon": 0.0, "event_id": event_id, "media_id": media_id, "device_id": 1, "azimuth": 0}
    response = requests.post(urljoin(API_URL, "alerts"), json=payload, headers=admin_client.headers)
    assert response.status_code == 201
