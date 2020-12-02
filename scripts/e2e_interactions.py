import requests
from getpass import getpass

def get_token(api_url: str, login: str, pwd: str) -> str:

    response = requests.post(f"{api_url}/login/access-token",
                             data=f"username={login}&password={pwd}",
                             headers={"Content-Type": "application/x-www-form-urlencoded",
                                      "accept": "application/json"})
    if response.status_code != 200:
        raise ValueError(response.json()['detail'])
    return response.json()['access_token']

def main(args):

    api_url = f"http://localhost:{args.port}"

    superuser_login = getpass('Login: ')
    superuser_pwd = getpass()

    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(api_url, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    user_login = 'my_user'
    user_pwd = 'my_pwd'

    # create a user
    response = requests.post(f"{api_url}/users/", json=dict(login=user_login, password=user_pwd, scopes="me"), headers=superuser_auth)
    import ipdb; ipdb.set_trace()
    user_auth = {
        "Authorization": f"Bearer {get_token(api_url, user_login, user_pwd)}",
        "Content-Type": "application/json",
    }
    user_id = response.json()['id']

    # Create a site
    response = requests.post(f"{api_url}/sites/", data=dict(name='first_site', country="FR", geocode="01", lat=44.1, lon=3.9), headers=superuser_auth)
    site_id = response.json()['id']

    # Update the user password
    response = requests.post(f"{api_url}/users/update-pwd", data=dict(password='my_second_pwd'), headers=user_auth)

    # Create a device (as admin until #79 is closed)
    response = requests.post(f"{api_url}/devices/", data=dict(login='my_device', owner_id=user_id, specs="raspberry_pi"), headers=superuser_auth)
    device_id = response.json()['id']

    # create an installation with this device and the site
    response = requests.post(f"{api_url}/installations/", data=dict(device_id=device_id, site_id=site_id, lat=44.1, lon=3.9, elevation=100., yaw=0., pitch=0.), headers=superuser_auth)
    installation_id = response.json()['id']

    # the installation creates an event and a related wildfire alert (+ a related media)
    # the installation throws later a second alert that terminates the event


    # Cleaning
    response = requests.delete(f"{api_url}/users/{user_id}/", headers=superuser_auth)
    response = requests.delete(f"{api_url}/accesses/{access_id}/", headers=superuser_auth)


    return

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Pyronear API End-to-End test',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('port', type=int, help='Port on localhost where the API is exposed')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
