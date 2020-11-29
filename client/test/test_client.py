import unittest

from pyroclient import client
from pyroclient.exceptions import HTTPRequestException


class ClientTester(unittest.TestCase):

    def test_client(self):

        # Wrong credentials
        self.assertRaises(HTTPRequestException, client.Client, "http://localhost:8002", "invalid_login", "invalid_pwd")

        # Correct creds
        api_client = client.Client("http://localhost:8002", "superuser", "superuser")

        # Read routes
        response = api_client.get_sites()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        response = api_client.get_all_alerts()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


if __name__ == '__main__':
    unittest.main()
