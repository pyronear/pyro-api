# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import argparse
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests


def get_token(api_url: str, login: str, pwd: str) -> str:
    response = requests.post(
        f"{api_url}/login/creds",
        data={"username": login, "password": pwd},
        timeout=5,
    )
    if response.status_code != 200:
        raise ValueError(response.json()["detail"])
    return response.json()["access_token"]


def api_request(method_type: str, route: str, headers=Dict[str, str], payload: Optional[Dict[str, Any]] = None):
    kwargs = {"json": payload} if isinstance(payload, dict) else {}

    response = getattr(requests, method_type)(route, headers=headers, **kwargs)
    try:
        detail = response.json()
    except (requests.exceptions.JSONDecodeError, KeyError):
        detail = response.text
    assert response.status_code // 100 == 2, print(detail)
    return response.json()


def main(args):
    superuser_login = "superadmin_login"
    superuser_pwd = "superadmin_pwd"  # noqa S105

    start_ts = time.time()
    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(args.endpoint, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    # Create an organization
    org_name = "my_org"
    org_id = api_request("post", f"{args.endpoint}/organizations/", superuser_auth, {"name": org_name})["id"]

    agent_login = "my_user"
    agent_pwd = "my_pwd"  # noqa S105

    # create a user
    payload = {"organization_id": org_id, "login": agent_login, "password": agent_pwd, "role": "agent"}
    user_id = api_request("post", f"{args.endpoint}/users/", superuser_auth, payload)["id"]
    agent_auth = {
        "Authorization": f"Bearer {get_token(args.endpoint, agent_login, agent_pwd)}",
        "Content-Type": "application/json",
    }
    # Get & Fetch access
    api_request("get", f"{args.endpoint}/users/{user_id}/", superuser_auth)
    api_request("get", f"{args.endpoint}/users/", superuser_auth)
    # Check that redirect is working
    api_request("get", f"{args.endpoint}/users", superuser_auth)
    # Modify access
    new_pwd = "my_new_pwd"  # noqa S105
    api_request("patch", f"{args.endpoint}/users/{user_id}/", superuser_auth, {"password": new_pwd})

    # Create a camera
    camera_name = "my_device"
    payload = {
        "name": camera_name,
        "organization_id": org_id,
        "angle_of_view": 70.0,
        "elevation": 100,
        "lat": 44.7,
        "lon": 4.5,
        "azimuth": 110,
    }
    cam_id = api_request("post", f"{args.endpoint}/cameras/", agent_auth, payload)["id"]

    cam_token = requests.post(
        f"{args.endpoint}/cameras/{cam_id}/token",
        timeout=5,
        headers=superuser_auth,
    ).json()["access_token"]

    cam_auth = {"Authorization": f"Bearer {cam_token}"}

    # Create a camera pose
    payload = {
        "camera_id": cam_id,
        "azimuth": 45,
    }
    pose_id = api_request("post", f"{args.endpoint}/poses/", agent_auth, payload)["id"]

    # Create a pose occlusion mask
    payload = {"pose_id": pose_id, "mask": "(0.1,0.1,0.9,0.9,1)"}

    occlusion_mask_id = api_request("post", f"{args.endpoint}/occlusion_masks/", agent_auth, payload)["id"]
    # Take a picture
    file_bytes = requests.get("https://pyronear.org/img/logo.png", timeout=5).content
    # Update cam last image
    response = requests.patch(
        f"{args.endpoint}/cameras/image",
        headers=cam_auth,
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    )
    assert response.status_code == 200, response.text
    assert response.json()["last_image"] is not None
    # Check that URL is displayed when we fetch all cameras
    response = requests.get(f"{args.endpoint}/cameras", headers=agent_auth, timeout=5)
    assert response.status_code == 200, response.text
    assert response.json()[0]["last_image_url"] is not None

    file_bytes = requests.get("https://pyronear.org/img/logo.png", timeout=5).content
    # Create a detection
    response = requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]", "pose_id": pose_id},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    )
    assert response.status_code == 201, response.text
    detection_id = response.json()["id"]
    today = datetime.fromisoformat(response.json()["created_at"]).date()

    # Fetch detections & their URLs
    api_request("get", f"{args.endpoint}/detections", agent_auth)
    api_request("get", f"{args.endpoint}/detections/{detection_id}/url", agent_auth)

    # Create a sequence by adding two additional detections
    det_id_2 = requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]", "pose_id": pose_id},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    ).json()["id"]
    det_id_3 = requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]", "pose_id": pose_id},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    ).json()["id"]
    # Check that a sequence has been created
    sequence = api_request("get", f"{args.endpoint}/sequences/1", agent_auth)
    assert sequence["camera_id"] == cam_id
    assert sequence["started_at"] == response.json()["created_at"]
    assert sequence["last_seen_at"] > sequence["started_at"]
    assert sequence["azimuth"] == response.json()["azimuth"]
    # Fetch the latest sequence
    assert len(api_request("get", f"{args.endpoint}/sequences/unlabeled/latest", agent_auth)) == 1
    # Fetch from date
    assert len(api_request("get", f"{args.endpoint}/sequences/all/fromdate?from_date=2019-09-10", agent_auth)) == 0
    assert (
        len(api_request("get", f"{args.endpoint}/sequences/all/fromdate?from_date={today.isoformat()}", agent_auth))
        == 1
    )
    # Label the sequence
    api_request(
        "patch", f"{args.endpoint}/sequences/{sequence['id']}/label", agent_auth, {"is_wildfire": "wildfire_smoke"}
    )
    # Check the sequence's detections
    dets = api_request("get", f"{args.endpoint}/sequences/{sequence['id']}/detections", agent_auth)
    assert len(dets) == 3
    assert dets[0]["id"] == det_id_3
    assert dets[1]["id"] == det_id_2
    assert dets[2]["id"] == detection_id
    dets = api_request("get", f"{args.endpoint}/sequences/{sequence['id']}/detections?limit=1", agent_auth)
    assert len(dets) == 1
    assert dets[0]["id"] == det_id_3
    dets = api_request("get", f"{args.endpoint}/sequences/{sequence['id']}/detections?limit=1&desc=false", agent_auth)
    assert len(dets) == 1
    assert dets[0]["id"] == detection_id

    # Cleaning (order is important because of foreign key protection in existing tables)
    api_request("delete", f"{args.endpoint}/detections/{detection_id}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/detections/{det_id_2}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/detections/{det_id_3}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/sequences/{sequence['id']}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/occlusion_masks/{occlusion_mask_id}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/poses/{pose_id}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/cameras/{cam_id}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/users/{user_id}/", superuser_auth)
    api_request("delete", f"{args.endpoint}/organizations/{org_id}/", superuser_auth)
    print(f"SUCCESS in {time.time() - start_ts:.3}s")

    return


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pyronear API End-to-End test", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--endpoint", type=str, default="http://localhost:5050/api/v1", help="the API endpoint")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
