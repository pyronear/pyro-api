# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import io
import logging
from typing import Any, Dict, Union
from urllib.parse import urljoin

import requests
from requests.models import Response

from .exceptions import HTTPRequestException

__all__ = ["Client"]

logging.basicConfig()

ROUTES: Dict[str, str] = {
    "token": "/login/access-token",
    #################
    # DEVICES
    #################
    # Device-logged
    "heartbeat": "/devices/heartbeat",
    "get-self-device": "/devices/me",
    # User-logged
    "get-user-devices": "/devices/my-devices",
    #################
    # SITES
    #################
    "get-sites": "/sites",
    #################
    # EVENTS
    #################
    "get-unacknowledged-events": "/events/unacknowledged",
    "get-past-events": "/events/past",
    "acknowledge-event": "/events/{event_id}/acknowledge",
    "get-alerts-for-event": "/events/{event_id}/alerts",
    #################
    # INSTALLATIONS
    #################
    "get-site-devices": "/installations/site-devices/{site_id}",
    #################
    # MEDIA
    #################
    "create-media-from-device": "/media/from-device",
    "upload-media": "/media/{media_id}/upload",
    "get-media-url": "/media/{media_id}/url",
    #################
    # ALERTS
    #################
    "send-alert-from-device": "/alerts/from-device",
    "get-alerts": "/alerts",
    "get-ongoing-alerts": "/alerts/ongoing",
}


class Client:
    """Client class to interact with the PyroNear API

    Args:
        api_url (str): url of the pyronear API
        credentials_login (str): Login (e.g: username)
        credentials_password (str): Password (e.g: 123456 (don't do this))
        timeout (int): number of seconds before request timeout
        kwargs: optional parameters of `requests.post`
    """

    api: str
    routes: Dict[str, str]
    token: str

    def __init__(
        self, api_url: str, credentials_login: str, credentials_password: str, timeout: int = 10, **kwargs: Any
    ) -> None:
        self.api = api_url
        # Prepend API url to each route
        self.routes = {k: urljoin(self.api, v) for k, v in ROUTES.items()}
        self.timeout = timeout
        self.refresh_token(credentials_login, credentials_password, **kwargs)

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def refresh_token(self, login: str, password: str, **kwargs: Any) -> None:
        self.token = self._retrieve_token(login, password, **kwargs)

    def _retrieve_token(self, login: str, password: str, **kwargs: Any) -> str:
        response = requests.post(
            self.routes["token"], data={"username": login, "password": password}, timeout=self.timeout, **kwargs
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            # Anyone has a better suggestion?
            raise HTTPRequestException(response.status_code, response.text)

    # Device functions
    def heartbeat(self) -> Response:
        """Updates the last ping of the device

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "DEVICE_LOGIN", "MY_PWD")
        >>> response = api_client.heartbeat()

        Returns:
            HTTP response containing the update device info
        """
        return requests.put(self.routes["heartbeat"], headers=self.headers, timeout=self.timeout)

    def send_alert_from_device(
        self,
        lat: float,
        lon: float,
        media_id: int,
        azimuth: Union[float, None] = None,
        event_id: Union[int, None] = None,
    ) -> Response:
        """Raise an alert to the API from a device (no need to specify device ID).

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "DEVICE_LOGIN", "MY_PWD")
        >>> response = api_client.send_alert_from_device(lat=10., lon=-5.45)

        Args:
            lat: the latitude of the alert
            lon: the longitude of the alert
            media_id: media ID linked to this alert
            azimuth: the azimuth of the alert
            event_id: the ID of the event this alerts relates to

        Returns:
            HTTP response containing the created alert
        """
        payload = {"lat": lat, "lon": lon, "event_id": event_id}
        if isinstance(media_id, int):
            payload["media_id"] = media_id

        if isinstance(azimuth, float):
            payload["azimuth"] = azimuth

        return requests.post(
            self.routes["send-alert-from-device"], headers=self.headers, json=payload, timeout=self.timeout
        )

    def create_media_from_device(self):
        """Create a media entry from a device (no need to specify device ID).

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "DEVICE_LOGIN", "MY_PWD")
        >>> response = api_client.create_media_from_device()

        Returns:
            HTTP response containing the created media
        """
        return requests.post(
            self.routes["create-media-from-device"], headers=self.headers, json={}, timeout=self.timeout
        )

    def upload_media(self, media_id: int, media_data: bytes) -> Response:
        """Upload the media content

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> with open("path/to/my/file.ext", "rb") as f: data = f.read()
        >>> response = api_client.upload_media(media_id=1, media_data=data)

        Args:
            media_id: ID of the associated media entry
            media_data: byte data

        Returns:
            HTTP response containing the updated media
        """
        return requests.post(
            self.routes["upload-media"].format(media_id=media_id),
            headers=self.headers,
            files={"file": io.BytesIO(media_data)},
            timeout=self.timeout,
        )

    # User functions
    def get_user_devices(self) -> Response:
        """Get the devices who are owned by the logged user

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_user_devices()

        Returns:
            HTTP response containing the list of owned devices
        """
        return requests.get(self.routes["get-user-devices"], headers=self.headers, timeout=self.timeout)

    def get_sites(self) -> Response:
        """Get all the existing sites in the DB

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_sites()

        Returns:
            HTTP response containing the list of sites
        """
        return requests.get(self.routes["get-sites"], headers=self.headers, timeout=self.timeout)

    def get_all_alerts(self) -> Response:
        """Get all the existing alerts in the DB

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_all_alerts()

        Returns:
            HTTP response containing the list of all alerts
        """
        return requests.get(self.routes["get-alerts"], headers=self.headers, timeout=self.timeout)

    def get_ongoing_alerts(self) -> Response:
        """Get all the existing alerts in the DB that have the status 'start'

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_ongoing_alerts()

        Returns:
            HTTP response containing the list of all ongoing alerts
        """
        return requests.get(self.routes["get-ongoing-alerts"], headers=self.headers, timeout=self.timeout)

    def get_alerts_for_event(self, event_id: int) -> Response:
        """Get all the alerts in the DB for the given event

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_alerts_for_event()

        Returns:
            HTTP response containing the list of all alerts for the given event
        """
        return requests.get(self.routes["get-alerts-for-event"], headers=self.headers, timeout=self.timeout)

    def get_unacknowledged_events(self) -> Response:
        """Get all the existing events in the DB that have the field "is_acknowledged" set to `False`

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_unacknowledged_events()

        Returns:
            HTTP response containing the list of all events that haven't been acknowledged
        """
        return requests.get(self.routes["get-unacknowledged-events"], headers=self.headers, timeout=self.timeout)

    def acknowledge_event(self, event_id: int) -> Response:
        """Switch the `is_acknowledged` field value of the event to `True`

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.acknowledge_event(event_id=1)

        Args:
            event_id: ID of the associated event entry

        Returns:
            HTTP response containing the updated event
        """
        return requests.put(
            self.routes["acknowledge-event"].format(event_id=event_id), headers=self.headers, timeout=self.timeout
        )

    def get_site_devices(self, site_id: int) -> Response:
        """Fetch the devices that are installed on a specific site

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_site_devices(1)

        Args:
            site_id: the identifier of the site

        Returns:
            HTTP response containing the list of corresponding devices
        """
        return requests.get(
            self.routes["get-site-devices"].format(site_id=site_id), headers=self.headers, timeout=self.timeout
        )

    def get_media_url(self, media_id: int) -> Response:
        """Get the image as a URL

        >>> import requests
        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_media_url(1)
        >>> file_response = requests.get(response.json()["url"])

        Args:
            media_id: the identifier of the media entry

        Returns:
            HTTP response containing the URL to the media content
        """
        return requests.get(
            self.routes["get-media-url"].format(media_id=media_id), headers=self.headers, timeout=self.timeout
        )

    def get_past_events(self) -> Response:
        """Get all past events

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_past_events()

        Returns:
            HTTP response containing the list of past events
        """
        return requests.get(self.routes["get-past-events"], headers=self.headers, timeout=self.timeout)

    def get_self_device(self) -> Response:
        """Get information about the current device

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_self_device()

        Returns:
            HTTP response containing the device information
        """
        return requests.get(self.routes["get-self-device"], headers=self.headers, timeout=self.timeout)
