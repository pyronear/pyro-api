# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import argparse
import os
import time
from getpass import getpass
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv


def get_token(api_url: str, login: str, pwd: str) -> str:
    response = requests.post(
        f"{api_url}/login/access-token",
        data={"username": login, "password": pwd},
        timeout=5,
    )
    if response.status_code != 200:
        raise ValueError(response.json()["detail"])
    return response.json()["access_token"]


def api_request(method_type: str, route: str, headers=Dict[str, str], payload: Optional[Dict[str, Any]] = None):
    kwargs = {"json": payload} if isinstance(payload, dict) else {}

    response = getattr(requests, method_type)(route, headers=headers, **kwargs)
    assert response.status_code // 100 == 2, print(response.text)
    return response.json()


def main(args):
    api_url = f"http://localhost:{args.port}"

    load_dotenv()

    # Log as superuser
    superuser_login = input("Login: ") if args.creds else os.environ["SUPERUSER_LOGIN"]
    superuser_pwd = getpass() if args.creds else os.environ["SUPERUSER_PWD"]

    start_ts = time.time()
    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(api_url, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    user_login = "my_user"
    user_pwd = "my_pwd"  # nosec B105
    user_group = 1

    # create a user
    payload = {"login": user_login, "password": user_pwd, "scope": "user", "group_id": user_group}
    user_id = api_request("post", f"{api_url}/users/", superuser_auth, payload)["id"]
    user_auth = {
        "Authorization": f"Bearer {get_token(api_url, user_login, user_pwd)}",
        "Content-Type": "application/json",
    }

    # Create a site
    payload = {"name": "first_site", "country": "FR", "geocode": "01", "lat": 44.1, "lon": 3.9, "group_id": 1}
    site_id = api_request("post", f"{api_url}/sites/", superuser_auth, payload)["id"]
    # Check internal redirect of slashes
    api_request("get", f"{api_url}/sites/", superuser_auth)
    api_request("get", f"{api_url}/sites", superuser_auth)

    # Update the user password
    payload = {"password": "my_second_pwd"}  # nosec B106
    api_request("put", f"{api_url}/users/update-pwd", user_auth, payload)

    # Create a device (as admin until #79 is closed)
    device_login = "my_device"
    device_pwd = "my_third_password"  # nosec B105
    payload = {"login": device_login, "password": device_pwd, "specs": "raspberry_pi", "angle_of_view": 0.68}
    device_id = api_request("post", f"{api_url}/devices/register", user_auth, payload)["id"]

    device_auth = {
        "Authorization": f"Bearer {get_token(api_url, device_login, device_pwd)}",
        "Content-Type": "application/json",
    }

    # create an installation with this device and the site
    payload = {"device_id": device_id, "site_id": site_id, "start_ts": "2019-08-24T14:15:22.00"}
    installation_id = api_request("post", f"{api_url}/installations/", superuser_auth, payload)["id"]

    # Installation creates a media
    payload = {"type": "image"}
    media_id = api_request("post", f"{api_url}/media/from-device", device_auth, payload)["id"]

    # Installation creates an event & alert
    payload = {"lat": 44.1, "lon": 3.9, "type": "wildfire"}
    event_id = api_request("post", f"{api_url}/events/", superuser_auth, payload)["id"]

    payload = {"lat": 44.1, "lon": 3.9, "azimuth": 0, "event_id": event_id, "media_id": media_id, "localization": None}
    alert_id = api_request("post", f"{api_url}/alerts/from-device", device_auth, payload)["id"]

    # Acknowledge it
    api_request("put", f"{api_url}/events/{event_id}/acknowledge", superuser_auth)

    # Cleaning (order is important because of foreign key protection in existing tables)
    api_request("delete", f"{api_url}/alerts/{alert_id}/", superuser_auth)
    api_request("delete", f"{api_url}/events/{event_id}/", superuser_auth)
    api_request("delete", f"{api_url}/media/{media_id}/", superuser_auth)
    api_request("delete", f"{api_url}/installations/{installation_id}/", superuser_auth)
    api_request("delete", f"{api_url}/devices/{device_id}/", superuser_auth)
    api_request("delete", f"{api_url}/sites/{site_id}/", superuser_auth)
    api_request("delete", f"{api_url}/users/{user_id}/", superuser_auth)

    print(f"SUCCESS in {time.time() - start_ts:.3}s")

    return


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pyronear API End-to-End test", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("port", type=int, help="Port on localhost where the API is exposed")
    parser.add_argument(
        "--creds", dest="creds", help="Enter different credentials than the default ones", action="store_true"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
