# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import io
import logging
from typing import Dict, Union
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
    "update-my-location": "/devices/update-my-location",
    "get-my-device": "/devices/me",
    "update-my-hash": "/devices/hash",
    # User-logged
    "get-my-devices": "/devices/my-devices",
    #################
    # SITES
    #################
    "get-sites": "/sites",
    "no-alert-site": "/sites/no-alert",
    #################
    # EVENTS
    #################
    "create-event": "/events",
    "get-unacknowledged-events": "/events/unacknowledged",
    "get-past-events": "/events/past",
    "acknowledge-event": "/events/{event_id}/acknowledge",
    #################
    # INSTALLATIONS
    #################
    "get-site-devices": "/installations/site-devices/{site_id}",
    #################
    # MEDIA
    #################
    "create-media": "/media",
    "create-media-from-device": "/media/from-device",
    "upload-media": "/media/{media_id}/upload",
    "get-media-url": "/media/{media_id}/url",
    #################
    # ALERTS
    #################
    "send-alert": "/alerts",
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
    """

    api: str
    routes: Dict[str, str]
    token: str

    def __init__(self, api_url: str, credentials_login: str, credentials_password: str) -> None:
        self.api = api_url
        # Prepend API url to each route
        self.routes = {k: urljoin(self.api, v) for k, v in ROUTES.items()}
        self.refresh_token(credentials_login, credentials_password)

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def refresh_token(self, login: str, password: str) -> None:
        self.token = self._retrieve_token(login, password)

    def _retrieve_token(self, login: str, password: str) -> str:
        response = requests.post(
            self.routes["token"],
            data=f"username={login}&password={password}",
            headers={"Content-Type": "application/x-www-form-urlencoded", "accept": "application/json"},
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
        return requests.put(self.routes["heartbeat"], headers=self.headers)

    def update_my_location(
        self,
        lat: float,
        lon: float,
        elevation: float,
        yaw: float,
        pitch: float,
    ) -> Response:
        """Updates the location of the device

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "DEVICE_LOGIN", "MY_PWD")
        >>> response = api_client.update_my_location(lat=10., lon=-5.45)

        Returns:
            HTTP response containing the update device info
        """
        payload = {"lat": lat, "lon": lon, "elevation": elevation, "yaw": yaw, "pitch": pitch}
        return requests.put(self.routes["update-my-location"], headers=self.headers, json=payload)

    def create_event(self, lat: float, lon: float) -> Response:
        """Register an event (e.g wildfire).

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.create_event(lat=10., lon=-5.45)

        Args:
            lat: the latitude of the event
            lon: the longitude of the event

        Returns:
            HTTP response containing the created event
        """
        payload = {"lat": lat, "lon": lon}
        return requests.post(self.routes["create-event"], headers=self.headers, json=payload)

    def create_no_alert_site(
        self, lat: float, lon: float, name: str, country: str, geocode: str, group_id: Union[int, None] = None
    ) -> Response:
        """Create a site that is not supposed to generate alerts.

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.create_no_alert_site(lat=10., lon=-5.45, name="farm", country="FR", geocode="01")

        Args:
            lat: the latitude of the site
            lon: the longitude of the site
            name: the name of the site
            country: the country where the site is located
            geocode: the geocode of the site

        Returns:
            HTTP response containing the created site
        """
        payload = {"lat": lat, "lon": lon, "name": name, "country": country, "geocode": geocode}
        if group_id is not None:
            payload["group_id"] = group_id
        return requests.post(self.routes["no-alert-site"], headers=self.headers, json=payload)

    def send_alert(
        self,
        lat: float,
        lon: float,
        device_id: int,
        media_id: int,
        azimuth: Union[float, None] = None,
        event_id: Union[int, None] = None,
    ) -> Response:
        """Raise an alert to the API.

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.send_alert(lat=10., lon=-5.45, device_id=3, azimuth=2.)

        Args:
            lat: the latitude of the alert
            lon: the longitude of the alert
            device_id: ID of the device that sent this alert
            media_id: media ID linked to this alert
            azimuth: the azimuth of the alert
            event_id: the ID of the event this alerts relates to

        Returns:
            HTTP response containing the created alert
        """
        payload = {"lat": lat, "lon": lon, "event_id": event_id, "device_id": device_id}
        if isinstance(media_id, int):
            payload["media_id"] = media_id
        if isinstance(azimuth, float):
            payload["azimuth"] = azimuth

        return requests.post(self.routes["send-alert"], headers=self.headers, json=payload)

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

        return requests.post(self.routes["send-alert-from-device"], headers=self.headers, json=payload)

    def create_media(self, device_id: int) -> Response:
        """Create a media entry

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.create_media(device_id=3)

        Args:
            device_id: ID of the device that created that media

        Returns:
            HTTP response containing the created media
        """

        return requests.post(self.routes["create-media"], headers=self.headers, json={"device_id": device_id})

    def create_media_from_device(self):
        """Create a media entry from a device (no need to specify device ID).

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "DEVICE_LOGIN", "MY_PWD")
        >>> response = api_client.create_media_from_device()

        Returns:
            HTTP response containing the created media
        """

        return requests.post(self.routes["create-media-from-device"], headers=self.headers, json={})

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
        )

    # User functions
    def get_my_devices(self) -> Response:
        """Get the devices who are owned by the logged user

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_my_devices()

        Returns:
            HTTP response containing the list of owned devices
        """
        return requests.get(self.routes["get-my-devices"], headers=self.headers)

    def get_sites(self) -> Response:
        """Get all the existing sites in the DB

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_sites()

        Returns:
            HTTP response containing the list of sites
        """
        return requests.get(self.routes["get-sites"], headers=self.headers)

    def get_all_alerts(self) -> Response:
        """Get all the existing alerts in the DB

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_all_alerts()

        Returns:
            HTTP response containing the list of all alerts
        """
        return requests.get(self.routes["get-alerts"], headers=self.headers)

    def get_ongoing_alerts(self) -> Response:
        """Get all the existing alerts in the DB that have the status 'start'

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_ongoing_alerts()

        Returns:
            HTTP response containing the list of all ongoing alerts
        """

        return requests.get(self.routes["get-ongoing-alerts"], headers=self.headers)

    def get_unacknowledged_events(self) -> Response:
        """Get all the existing events in the DB that have the field "is_acknowledged" set to `False`

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_unacknowledged_events()

        Returns:
            HTTP response containing the list of all events that haven't been acknowledged
        """
        return requests.get(self.routes["get-unacknowledged-events"], headers=self.headers)

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

        return requests.put(self.routes["acknowledge-event"].format(event_id=event_id), headers=self.headers)

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
        return requests.get(self.routes["get-site-devices"].format(site_id=site_id), headers=self.headers)

    def get_media_url(self, media_id: int) -> Response:
        """Get the image as a URL

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_media_url(1)

        Args:
            media_id: the identifier of the media entry

        Returns:
            HTTP response containing the URL to the media content
        """

        return requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)

    def get_media_url_and_read(self, media_id: int) -> Response:
        """Get the image as a url and read it

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_media_url_and_read(1)

        Args:
            media_id: the identifier of the media entry

        Returns:
            HTTP response containing the media content
        """
        image_url = requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)
        return requests.get(image_url.json()["url"])

    def get_past_events(self) -> Response:
        """Get all past events

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_past_events()

        Returns:
            HTTP response containing the list of past events
        """
        return requests.get(self.routes["get-past-events"], headers=self.headers)

    def get_my_device(self) -> Response:
        """Get information about the current device

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.get_my_device()

        Returns:
            HTTP response containing the device information
        """
        return requests.get(self.routes["get-my-device"], headers=self.headers)

    def update_my_hash(self, software_hash: str) -> Response:
        """Updates the software hash of the current device

        >>> from pyroclient import client
        >>> api_client = client.Client("http://pyronear-api.herokuapp.com", "MY_LOGIN", "MY_PWD")
        >>> response = api_client.update_my_hash()

        Returns:
            HTTP response containing the updated device information
        """
        payload = {"software_hash": software_hash}

        return requests.put(self.routes["update-my-hash"], headers=self.headers, json=payload)
