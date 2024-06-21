import os
from urllib.parse import urljoin

import pytest
import requests

API_URL = os.getenv("API_URL", "http://localhost:5050/api/v1/")
SUPERADMIN_LOGIN = os.getenv("SUPERADMIN_LOGIN", "superadmin_login")
SUPERADMIN_PWD = os.getenv("SUPERADMIN_PWD", "superadmin_pwd")
SUPERADMIN_ORGANIZATION = os.getenv("SUPERADMIN_ORGANIZATION", "superadmin_organization")
SUPERADMIN_TOKEN = requests.post(
    urljoin(API_URL, "login/creds"),
    data={"username": SUPERADMIN_LOGIN, "password": SUPERADMIN_PWD, "organization": SUPERADMIN_ORGANIZATION},
    timeout=5,
).json()["access_token"]


def pytest_configure():
    # api.security patching
    pytest.admin_token = SUPERADMIN_TOKEN


@pytest.fixture(scope="session")
def mock_img():
    # Get Pyronear logo
    return requests.get("https://avatars.githubusercontent.com/u/61667887?s=200&v=4", timeout=5).content


@pytest.fixture(scope="session")
def cam_token():
    admin_headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    payload = {
        "name": "pyro-camera-01",
        "organization_id": 1,
        "angle_of_view": 120,
        "elevation": 1582,
        "lat": 44.765181,
        "lon": 4.51488,
        "is_trustable": True,
    }
    response = requests.post(urljoin(API_URL, "cameras"), json=payload, headers=admin_headers, timeout=5)
    assert response.status_code == 201
    cam_id = response.json()["id"]
    # Create a cam token
    return requests.post(urljoin(API_URL, f"cameras/{cam_id}/token"), headers=admin_headers, timeout=5).json()[
        "access_token"
    ]


@pytest.fixture(scope="session")
def agent_token():
    admin_headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    agent_login, agent_pwd = "agent-1", "PickARobustOne"
    payload = {
        "role": "agent",
        "login": agent_login,
        "password": agent_pwd,
        "organization_id": 1,
    }
    response = requests.post(urljoin(API_URL, "users"), json=payload, headers=admin_headers, timeout=5)
    assert response.status_code == 201
    # Create a cam token
    return requests.post(
        urljoin(API_URL, "login/creds"), data={"username": agent_login, "password": agent_pwd}, timeout=5
    ).json()["access_token"]


@pytest.fixture(scope="session")
def user_token():
    admin_headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    user_login, user_pwd = "user-1", "PickARobustOne"
    payload = {
        "role": "user",
        "login": user_login,
        "password": user_pwd,
        "organization_id": 1,
    }
    response = requests.post(urljoin(API_URL, "users"), json=payload, headers=admin_headers, timeout=5)
    assert response.status_code == 201
    # Create a cam token
    return requests.post(
        urljoin(API_URL, "login/creds"), data={"username": user_login, "password": user_pwd}, timeout=5
    ).json()["access_token"]
