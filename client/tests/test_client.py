from datetime import datetime

import pytest
from requests.exceptions import ConnectionError as ConnError
from requests.exceptions import ReadTimeout

from pyroclient.client import Client
from pyroclient.exceptions import HTTPRequestError


@pytest.mark.parametrize(
    ("token", "host", "timeout", "expected_error"),
    [
        ("invalid_token", "http://localhost:5050", 10, HTTPRequestError),
        (pytest.admin_token, "http://localhost:8003", 10, ConnError),
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
    response = cam_client.heartbeat()
    assert response.status_code == 200
    # Check that last_image gets changed
    assert response.json()["last_image"] is None
    response = cam_client.update_last_image(mock_img)
    assert response.status_code == 200, response.__dict__
    assert isinstance(response.json()["last_image"], str)
    # Check that adding bboxes works
    with pytest.raises(ValueError, match="bboxes must be a non-empty list of tuples"):
        cam_client.create_detection(mock_img, 123.2, None)
    with pytest.raises(ValueError, match="bboxes must be a non-empty list of tuples"):
        cam_client.create_detection(mock_img, 123.2, [])
    response = cam_client.create_detection(mock_img, 123.2, [(0, 0, 1.0, 0.9, 0.5)], pose_id=1)
    assert response.status_code == 201, response.__dict__
    response = cam_client.create_detection(mock_img, 123.2, [(0, 0, 1.0, 0.9, 0.5), (0.2, 0.2, 0.7, 0.7, 0.8)])
    assert response.status_code == 201, response.__dict__
    response = cam_client.create_detection(mock_img, 123.2, [(0, 0, 1.0, 0.9, 0.5)])
    assert response.status_code == 201, response.__dict__
    return response.json()["id"]


def test_agent_workflow(test_cam_workflow, agent_token):
    # Agent workflow
    agent_client = Client(agent_token, "http://localhost:5050", timeout=10)
    response = agent_client.fetch_latest_sequences().json()
    assert len(response) == 1
    response = agent_client.label_sequence(response[0]["id"], "wildfire_smoke")
    assert response.status_code == 200, response.__dict__


def test_user_workflow(test_cam_workflow, user_token):
    # User workflow
    user_client = Client(user_token, "http://localhost:5050", timeout=10)
    response = user_client.get_detection_url(test_cam_workflow)
    assert response.status_code == 200, response.__dict__
    response = user_client.fetch_detections()
    assert response.status_code == 200, response.__dict__
    response = user_client.fetch_sequences_from_date("2018-06-06")
    assert len(response.json()) == 0
    assert response.status_code == 200, response.__dict__
    response = user_client.fetch_latest_sequences()
    assert response.status_code == 200, response.__dict__
    assert len(response.json()) == 0  # Sequence was labeled by agent
    response = user_client.fetch_sequences_from_date(datetime.utcnow().date().isoformat())
    assert len(response.json()) == 1
    response = user_client.fetch_sequences_detections(response.json()[0]["id"])
    assert response.status_code == 200, response.__dict__
    assert len(response.json()) == 3
