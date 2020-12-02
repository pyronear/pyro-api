import unittest
from requests import ConnectionError

from pyroclient import client
from pyroclient.exceptions import HTTPRequestException


class ClientTester(unittest.TestCase):

    def _test_route_retun(self, response, return_type):
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), return_type)

    def test_client(self):

        # Wrong credentials
        self.assertRaises(HTTPRequestException, client.Client, "http://localhost:8002", "invalid_login", "invalid_pwd")

        # Incorrect URL port
        self.assertRaises(ConnectionError, client.Client, "http://localhost:8003", "superuser", "superuser")

        api_client = client.Client("http://localhost:8002", "superuser", "superuser")

        # Read routes
        self._test_route_retun(api_client.get_my_devices(), list)
        self._test_route_retun(api_client.get_sites(), list)
        self._test_route_retun(api_client.get_all_alerts(), list)
        self._test_route_retun(api_client.get_ongoing_alerts(), list)
        self._test_route_retun(api_client.get_unacknowledged_alerts(), list)


if __name__ == '__main__':
    unittest.main()
