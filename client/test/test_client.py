import unittest
from requests import ConnectionError

from pyroclient import client
from pyroclient.exceptions import HTTPRequestException


class ClientTester(unittest.TestCase):

    def _test_route_return(self, response, return_type):
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), return_type)

        return response.json()

    def test_client(self):

        # Wrong credentials
        self.assertRaises(HTTPRequestException, client.Client, "http://localhost:8002", "invalid_login", "invalid_pwd")

        # Incorrect URL port
        self.assertRaises(ConnectionError, client.Client, "http://localhost:8003", "superuser", "superuser")

        api_client = client.Client("http://localhost:8002", "superuser", "superuser")

        # Read routes
        all_devices = self._test_route_return(api_client.get_my_devices(), list)
        self._test_route_return(api_client.get_sites(), list)
        self._test_route_return(api_client.get_all_alerts(), list)
        self._test_route_return(api_client.get_ongoing_alerts(), list)
        self._test_route_return(api_client.get_unacknowledged_alerts(), list)

        if len(all_devices) > 0:
            # Create event
            event_id = self._test_route_return(api_client.create_event(0., 0.), dict)['id']
            # Create an alert
            alert = self._test_route_return(api_client.send_alert(0., 0., event_id, all_devices[0]['id']), dict)
            # Acknowledge it
            updated_alert = self._test_route_return(api_client.acknowledge_alert(alert['id']), dict)
            self.assertTrue(updated_alert['is_acknowledged'])


if __name__ == '__main__':
    unittest.main()
