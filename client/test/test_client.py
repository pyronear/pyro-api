# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import unittest
import time
from copy import deepcopy
from requests import ConnectionError

from pyroclient import client
from pyroclient.exceptions import HTTPRequestException


class ClientTester(unittest.TestCase):

    def _test_route_return(self, response, return_type, status_code=200):
        self.assertEqual(response.status_code, status_code)
        self.assertIsInstance(response.json(), return_type)

        return response.json()

    def test_client(self):

        # Wrong credentials
        self.assertRaises(HTTPRequestException, client.Client, "http://localhost:8080", "invalid_login", "invalid_pwd")

        # Incorrect URL port
        self.assertRaises(ConnectionError, client.Client, "http://localhost:8003", "dummy_login", "dummy_pwd")

        api_client = client.Client("http://localhost:8080", "dummy_login", "dummy_pwd")

        # Sites
        site_id = self._test_route_return(
            api_client.create_no_alert_site(
                lat=44.870959, lon=4.395387, name="dummy_tower", country="FR", geocode="07"
            ),
            dict,
            201
        )['id']
        sites = self._test_route_return(api_client.get_sites(), list)
        assert sites[-1]['id'] == site_id

        # Devices
        all_devices = self._test_route_return(api_client.get_my_devices(), list)
        self._test_route_return(api_client.get_site_devices(site_id), list)

        # Alerts
        self._test_route_return(api_client.get_all_alerts(), list)
        self._test_route_return(api_client.get_ongoing_alerts(), list)
        # Events
        self._test_route_return(api_client.get_unacknowledged_events(), list)
        self._test_route_return(api_client.get_past_events(), list)

        if len(all_devices) > 0:
            # Media
            media_id = self._test_route_return(api_client.create_media(all_devices[0]['id']), dict, 201)['id']
            # Create event
            event_id = self._test_route_return(api_client.create_event(0., 0.), dict, 201)['id']
            # Create an alert
            _ = self._test_route_return(
                api_client.send_alert(0., 0., event_id, all_devices[0]['id'], media_id=media_id),
                dict,
                201
            )
            # Acknowledge it
            updated_event = self._test_route_return(api_client.acknowledge_event(event_id), dict)
            self.assertTrue(updated_event['is_acknowledged'])

        # Check token refresh
        prev_headers = deepcopy(api_client.headers)
        # In case the 2nd token creation request is done in the same second, since the expiration is truncated to the
        # second, it returns the same token
        time.sleep(1)
        api_client.refresh_token("dummy_login", "dummy_pwd")
        self.assertNotEqual(prev_headers, api_client.headers)


if __name__ == '__main__':
    unittest.main()
