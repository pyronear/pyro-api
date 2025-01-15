# Copyright (C) 2020-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import argparse
import time
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

    # Take a picture
    file_bytes = requests.get("https://pyronear.org/img/logo.png", timeout=5).content
    # Create a detection
    response = requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]"},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    )
    assert response.status_code == 201, response.text
    detection_id = response.json()["id"]

    # Fetch unlabeled detections
    api_request("get", f"{args.endpoint}/detections/unlabeled/fromdate?from_date=2018-06-06T00:00:00", agent_auth)

    # Acknowledge it
    api_request("patch", f"{args.endpoint}/detections/{detection_id}/label", agent_auth, {"is_wildfire": True})

    # Fetch detections & their URLs
    api_request("get", f"{args.endpoint}/detections", agent_auth)
    api_request("get", f"{args.endpoint}/detections/{detection_id}/url", agent_auth)

    # Create a sequence by adding two additional detections
    requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]"},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    )
    requests.post(
        f"{args.endpoint}/detections",
        headers=cam_auth,
        data={"azimuth": 45.6, "bboxes": "[(0.1,0.1,0.8,0.8,0.5)]"},
        files={"file": ("logo.png", file_bytes, "image/png")},
        timeout=5,
    )
    # Check that a sequence has been created
    sequences = api_request("get", f"{args.endpoint}/sequences", superuser_auth)
    assert len(sequences) == 1
    assert sequences[0]["camera_id"] == cam_id
    assert sequences[0]["started_at"] == response.json()["created_at"]
    assert sequences[0]["last_seen_at"] > sequences[0]["started_at"]
    assert sequences[0]["azimuth"] == response.json()["azimuth"]

    # Cleaning (order is important because of foreign key protection in existing tables)
    api_request("delete", f"{args.endpoint}/detections/{detection_id}/", superuser_auth)
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
