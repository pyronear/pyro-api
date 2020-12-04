import requests
from getpass import getpass
from typing import Dict, Any


def get_token(api_url: str, login: str, pwd: str) -> str:

    response = requests.post(f"{api_url}/login/access-token",
                             data=f"username={login}&password={pwd}",
                             headers={"Content-Type": "application/x-www-form-urlencoded",
                                      "accept": "application/json"})
    if response.status_code != 200:
        raise ValueError(response.json()['detail'])
    return response.json()['access_token']


def api_request(method_type: str, route: str, payload: Dict[str, Any], headers=Dict[str, str]):

    response = getattr(requests, method_type)(route, json=payload, headers=headers)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    return response.json()


def main(args):

    api_url = f"http://localhost:{args.port}"

    # Log as superuser
    superuser_login = getpass('Login: ') if args.creds else "superuser"
    superuser_pwd = getpass() if args.creds else "superuser"

    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(api_url, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    user_login = 'my_user'
    user_pwd = 'my_pwd'

    # create a user
    payload = dict(login=user_login, password=user_pwd, scopes="me")
    user_id = api_request('post', f"{api_url}/users/", payload, superuser_auth)['id']
    user_auth = {
        "Authorization": f"Bearer {get_token(api_url, user_login, user_pwd)}",
        "Content-Type": "application/json",
    }

    # Create a site
    payload = dict(name='first_site', country="FR", geocode="01", lat=44.1, lon=3.9)
    site_id = api_request('post', f"{api_url}/sites/", payload, superuser_auth)['id']

    # Update the user password
    payload = dict(password='my_second_pwd')
    api_request('put', f"{api_url}/users/update-pwd", payload, user_auth)

    # Create a device (as admin until #79 is closed)
    device_login = 'my_device'
    device_pwd = 'my_third_password'
    payload = dict(login=device_login, password=device_pwd, specs="raspberry_pi")
    device_id = api_request('post', f"{api_url}/devices/register", payload, user_auth)['id']

    device_auth = {
        "Authorization": f"Bearer {get_token(api_url, device_login, device_pwd)}",
        "Content-Type": "application/json",
    }

    # create an installation with this device and the site
    payload = dict(device_id=device_id, site_id=site_id, lat=44.1, lon=3.9, elevation=100., yaw=0., pitch=0.,
                   start_ts="2019-08-24T14:15:22.00")
    installation_id = api_request('post', f"{api_url}/installations/", payload, superuser_auth)['id']

    # Installation creates a media
    payload = dict(type='image')
    media_id = api_request('post', f"{api_url}/media/from-device", payload, device_auth)['id']

    # Installation creates an event & alert
    payload = dict(lat=44.1, lon=3.9, type='wildfire')
    event_id = api_request('post', f"{api_url}/events/", payload, superuser_auth)['id']

    payload = dict(lat=44.1, lon=3.9, event_id=event_id, media_id=media_id, type='start')
    alert_id1 = api_request('post', f"{api_url}/alerts/from-device", payload, device_auth)['id']

    # Installation throws the end alert
    payload = dict(lat=44.1, lon=3.9, event_id=event_id, type='end')
    alert_id2 = api_request('post', f"{api_url}/alerts/from-device", payload, device_auth)['id']

    # Cleaning (order is important because of foreign key protection in existing tables)
    response = requests.delete(f"{api_url}/alerts/{alert_id1}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    response = requests.delete(f"{api_url}/alerts/{alert_id2}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    response = requests.delete(f"{api_url}/media/{media_id}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    response = requests.delete(f"{api_url}/installations/{installation_id}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    response = requests.delete(f"{api_url}/devices/{device_id}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    response = requests.delete(f"{api_url}/users/{user_id}/", headers=superuser_auth)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    print("SUCCESS")

    return


def parse_args():
    import argparse
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
