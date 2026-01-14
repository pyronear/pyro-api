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


def test_get_current_poses_camera(cam_token, cam_pose_id):
    cam_client = Client(cam_token, "http://localhost:5050", timeout=10)
    response = cam_client.get_current_poses()
    assert response.status_code == 200, response.__dict__
    poses = response.json()
    assert isinstance(poses, list)
    assert any(pose["id"] == cam_pose_id for pose in poses)


def test_get_current_poses_admin(cam_id, cam_pose_id):
    admin_client = Client(pytest.admin_token, "http://localhost:5050", timeout=10)
    response = admin_client.get_current_poses(camera_id=cam_id)
    assert response.status_code == 200, response.__dict__
    payload = response.json()
    assert isinstance(payload.get("poses"), list)
    assert any(pose["id"] == cam_pose_id for pose in payload["poses"])


def test_update_pose_camera(cam_token, cam_pose_id):
    cam_client = Client(cam_token, "http://localhost:5050", timeout=10)
    with pytest.raises(ValueError, match="Either azimuth or patrol_id must be provided"):
        cam_client.update_pose(cam_pose_id)
    response = cam_client.update_pose(cam_pose_id, azimuth=123.4)
    assert response.status_code == 200, response.__dict__
    assert response.json()["azimuth"] == 123.4


@pytest.fixture(scope="session")
def test_cam_workflow(cam_token, cam_pose_id, mock_img):
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
        cam_client.create_detection(mock_img, None, pose_id=cam_pose_id)
    with pytest.raises(ValueError, match="bboxes must be a non-empty list of tuples"):
        cam_client.create_detection(mock_img, [], pose_id=cam_pose_id)
    response = cam_client.create_detection(mock_img, [(0, 0, 1.0, 0.9, 0.5)], pose_id=cam_pose_id)
    assert response.status_code == 201, response.__dict__
    response = cam_client.create_detection(
        mock_img,
        [(0, 0, 1.0, 0.9, 0.5), (0.2, 0.2, 0.7, 0.7, 0.8)],
        pose_id=cam_pose_id,
    )
    assert response.status_code == 201, response.__dict__
    response = cam_client.create_detection(mock_img, [(0, 0, 1.0, 0.9, 0.5)], pose_id=cam_pose_id)
    assert response.status_code == 201, response.__dict__
    return response.json()["id"]


def test_agent_workflow(test_cam_workflow, agent_token):
    # Agent workflow
    agent_client = Client(agent_token, "http://localhost:5050", timeout=10)
    response = agent_client.fetch_latest_sequences().json()
    assert len(response) == 1
    response = agent_client.label_sequence(response[0]["id"], "wildfire_smoke")
    assert response.status_code == 200, response.__dict__
    response = agent_client.create_occlusion_mask(pose_id=1, mask="(0.1,0.1,0.9,0.9)")  # occlusion mask creation
    assert response.status_code == 201, response.__dict__
    print("reponseeee creation du mask")
    print(response.json())
    response = agent_client.delete_occlusion_mask(mask_id=response.json()["id"])  # occlusion mask deletion
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
    assert len(response.json()) == 4
