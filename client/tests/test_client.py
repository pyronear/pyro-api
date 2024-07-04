import pytest
from requests.exceptions import ConnectionError, ReadTimeout

from pyroclient.client import Client
from pyroclient.exceptions import HTTPRequestError


@pytest.mark.parametrize(
    ("token", "host", "timeout", "expected_error"),
    [
        ("invalid_token", "http://localhost:5050", 10, HTTPRequestError),
        (pytest.admin_token, "http://localhost:8003", 10, ConnectionError),
        (pytest.admin_token, "http://localhost:5050", 0.00001, ReadTimeout),
        (pytest.admin_token, "http://localhost:5050", 10, None),
    ],
)
def test_client_constructor(token, host, timeout, expected_error):
    if expected_error is None:
        Client(token, host, timeout=timeout)
    else:
        with pytest.raises(expected_error):
            Client(token, host, timeout=timeout)


@pytest.fixture(scope="session")
def test_cam_workflow(cam_token, mock_img):
    cam_client = Client(cam_token, "http://localhost:5050", timeout=10)
    assert cam_client.heartbeat().status_code == 200
    response = cam_client.create_detection(mock_img, 123.2)
    assert response.status_code == 201, print(response.__dict__)
    return response.json()["id"]


def test_agent_workflow(test_cam_workflow, agent_token):
    # Agent workflow
    agent_client = Client(agent_token, "http://localhost:5050", timeout=10)
    response = agent_client.label_detection(test_cam_workflow, True)
    assert response.status_code == 200, print(response.__dict__)


def test_user_workflow(test_cam_workflow, user_token):
    # User workflow
    user_client = Client(user_token, "http://localhost:5050", timeout=10)
    response = user_client.get_detection_url(test_cam_workflow)
    assert response.status_code == 200, print(response.__dict__)
    response = user_client.fetch_detections()
    assert response.status_code == 200, print(response.__dict__)
    response = user_client.fetch_unacknowledged_detections()
    assert response.status_code == 200, print(response.__dict__)
