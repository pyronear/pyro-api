# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import requests
import argparse
import time
from getpass import getpass
from typing import Dict, Any, Optional


def get_token(api_url: str, login: str, pwd: str) -> str:

    response = requests.post(f"{api_url}/login/access-token",
                             data=f"username={login}&password={pwd}",
                             headers={"Content-Type": "application/x-www-form-urlencoded",
                                      "accept": "application/json"})
    if response.status_code != 200:
        raise ValueError(response.json()['detail'])
    return response.json()['access_token']


def api_request(method_type: str, route: str, headers=Dict[str, str], payload: Optional[Dict[str, Any]] = None):

    kwargs = {"json": payload} if isinstance(payload, dict) else {}

    response = getattr(requests, method_type)(route, headers=headers, **kwargs)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    return response.json()


def main(args):

    api_url = f"http://localhost:{args.port}"

    # Log as superuser
    superuser_login = getpass('Login: ') if args.creds else "superuser"
    superuser_pwd = getpass() if args.creds else "superuser"

    start_ts = time.time()
    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(api_url, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    user_login = 'my_user'
    user_pwd = 'my_pwd'
    user_group = 1

    # create a user
    payload = dict(login=user_login, password=user_pwd, scope="user", group_id=user_group)
    user_id = api_request('post', f"{api_url}/users/", superuser_auth, payload)['id']
    user_auth = {
        "Authorization": f"Bearer {get_token(api_url, user_login, user_pwd)}",
        "Content-Type": "application/json",
    }

    # Create a site
    payload = dict(name='first_site', country="FR", geocode="01", lat=44.1, lon=3.9, group_id=1)
    site_id = api_request('post', f"{api_url}/sites/", superuser_auth, payload)['id']

    # Update the user password
    payload = dict(password='my_second_pwd')
    api_request('put', f"{api_url}/users/update-pwd", user_auth, payload)

    # Create a device (as admin until #79 is closed)
    device_login = 'my_device'
    device_pwd = 'my_third_password'
    payload = dict(login=device_login, password=device_pwd, specs="raspberry_pi", angle_of_view=0.68)
    device_id = api_request('post', f"{api_url}/devices/register", user_auth, payload)['id']

    device_auth = {
        "Authorization": f"Bearer {get_token(api_url, device_login, device_pwd)}",
        "Content-Type": "application/json",
    }

    # create an installation with this device and the site
    payload = dict(device_id=device_id, site_id=site_id, start_ts="2019-08-24T14:15:22.00")
    installation_id = api_request('post', f"{api_url}/installations/", superuser_auth, payload)['id']

    # Installation creates a media
    payload = dict(type='image')
    media_id = api_request('post', f"{api_url}/media/from-device", device_auth, payload)['id']

    # Installation creates an event & alert
    payload = dict(lat=44.1, lon=3.9, type='wildfire')
    event_id = api_request('post', f"{api_url}/events/", superuser_auth, payload)['id']

    payload = dict(lat=44.1, lon=3.9, event_id=event_id, media_id=media_id)
    alert_id = api_request('post', f"{api_url}/alerts/from-device", device_auth, payload)['id']

    # Acknowledge it
    api_request('put', f"{api_url}/events/{event_id}/acknowledge", superuser_auth)

    # Cleaning (order is important because of foreign key protection in existing tables)
    api_request('delete', f"{api_url}/alerts/{alert_id}/", superuser_auth)
    api_request('delete', f"{api_url}/events/{event_id}/", superuser_auth)
    api_request('delete', f"{api_url}/media/{media_id}/", superuser_auth)
    api_request('delete', f"{api_url}/installations/{installation_id}/", superuser_auth)
    api_request('delete', f"{api_url}/devices/{device_id}/", superuser_auth)
    api_request('delete', f"{api_url}/sites/{site_id}/", superuser_auth)
    api_request('delete', f"{api_url}/users/{user_id}/", superuser_auth)

    print(f"SUCCESS in {time.time() - start_ts:.3}s")

    return


def parse_args():
    parser = argparse.ArgumentParser(description='Pyronear API End-to-End test',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('port', type=int, help='Port on localhost where the API is exposed')
    parser.add_argument('--creds', dest="creds", help="Enter different credentials than the default ones",
                        action="store_true")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
