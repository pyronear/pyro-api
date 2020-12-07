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
        self._test_route_return(api_client.get_my_devices(), list)
        self._test_route_return(api_client.get_sites(), list)
        all_alerts = self._test_route_return(api_client.get_all_alerts(), list)
        self._test_route_return(api_client.get_ongoing_alerts(), list)
        self._test_route_return(api_client.get_unacknowledged_alerts(), list)

        # Acknowledge an alert
        alert_id = None
        # Try to find an unacknowledged alert
        for alert in all_alerts:
            if not alert['is_acknowledged']:
                alert_id = alert['id']
        # Else it should not change the value
        if alert_id is None and len(all_alerts) > 0:
            alert_id = all_allerts[-1]['id']
        if isinstance(alert_id, int):
            updated_alert = self._test_route_return(api_client.acknowledge_alert(alert_id), dict)
            self.assertTrue(updated_alert['is_acknowledged'])


if __name__ == '__main__':
    unittest.main()
