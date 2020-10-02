#!/usr/bin/env python
import json
import requests

from pprint import pprint


def check_response(response, expected_status=200):
    """Verify JSON request success

    Args:
        response (requests.models.Response): HTTP response
        expected_status (int, optional): expected status code in case of success
    """

    if response.status_code != expected_status:
        raise ValueError(json.loads(response.text).get('traceback', response.text))


def sample_request(port, route='pyronear/user', host='localhost'):
    """Make a sample hint request for word association

    Args:
        port (int): port to request
        route (str, optional): route to request on host
        host (str, optional): host to send the request to
    Returns:
        requests.models.Response: HTTP response
    """

    payload = {"username": "my_username"}
    url = f"http://{host}:{port}/{route}/"

    # Check get
    get_response = requests.get(url)
    check_response(get_response)
    num_users = len(get_response.json()['objects'])

    # Check post
    post_response = requests.post(url, json=payload)
    check_response(post_response, 201)
    get_response = requests.get(url)
    if len(get_response.json()['objects']) != num_users + 1:
        raise AssertionError("Table entry was not added correctly")

    return get_response


def main(args):

    response = sample_request(args.port, args.route, args.host)
    response = response.json()
    pprint(response)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Docker container request testing',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", type=int, default=8000, help="Port used for the container")
    parser.add_argument("--route", type=str, default='pyronear/user', help="API route to be used for request")
    parser.add_argument("--host", type=str, default='localhost', help="host of the server")
    args = parser.parse_args()

    main(args)
