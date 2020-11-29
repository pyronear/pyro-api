import requests
from requests.models import Response
import logging
from urllib.parse import urljoin
from typing import Dict, Any

from .exceptions import HTTPRequestException


__all__ = ['Client']

logging.basicConfig()


class Client:
    """Client class to interact with the PyroNear API

    Args:
        api_url (str): url of the pyronear API
        credentials_login (str): Login (e.g: username)
        credentials_password (str): Password (e.g: 123456 (don't do this))
    """

    routes = {"token": "/login/access-token",
              "heartbeat": "/device/heartbeat",
              "update-my-location": "/device/update-my-location",
              "send-alert": "/alerts",
              "create-media": "/media",
              "upload-media": "/media/upload",
              "get-my-devices": "/devices/my-devices",
              "get-sites": "/sites",
              "get-alerts": "/alerts",
              "get-ongoing-alerts": "/alerts/ongoing",
              "get-unacknowledged-alerts": "/alerts/unacknowledged",
              "get-site-devices": "/installations/site-devices/{site_id}",
              "get-media-url": "/media/{media_id}/url",
              "get-media-image": "/media/{media_id}/image"
              }

    def __init__(self, api_url: str, credentials_login: str, credentials_password: str) -> None:
        self.api = api_url
        self._add_api_url_to_routes()
        self.token = self._retrieve_token(credentials_login, credentials_password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _add_api_url_to_routes(self) -> None:
        for k, v in self.routes.items():
            self.routes[k] = urljoin(self.api, v)

    def _retrieve_token(self, login: str, password: str) -> str:
        response = requests.post(self.routes["token"],
                                 data=f"username={login}&password={password}",
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "accept": "application/json"
                                          })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            # Anyone has a better suggestion?
            raise HTTPRequestException(response.status_code, response.text)

    # Device functions
    def hearbeat(self) -> Response:
        """Updates the last ping of the device"""
        return requests.put(self.routes["heartbeat"], headers=self.headers)

    def update_my_location(self) -> Response:
        """Updates the location of the device"""
        return requests.put(self.routes["update-my-location"], headers=self.headers)

    def send_alert(self):
        """Raise an alert to the API"""
        return requests.post(self.routes["send-alert"], headers=self.headers)

    def create_media(self) -> Response:
        """Create a media entry"""
        return requests.post(self.routes["create-media"], headers=self.headers)

    def upload_media(self) -> Response:
        """Upload the media content"""
        return requests.post(self.routes["upload-media"], headers=self.headers)

    # User functions
    def get_my_devices(self) -> Response:
        """Get the devices who are owned by the logged user"""
        return requests.get(self.routes["get-my-devices"], headers=self.headers)

    def get_sites(self) -> Response:
        """Get all the existing sites in the DB"""
        return requests.get(self.routes["get-sites"], headers=self.headers)

    def get_all_alerts(self) -> Response:
        """Get all the existing alerts in the DB"""
        return requests.get(self.routes["get-alerts"], headers=self.headers)

    def get_ongoing_alerts(self) -> Response:
        """Get all the existing alerts in the DB that have the status 'start'"""
        return requests.get(self.routes["get-ongoing-alerts"], headers=self.headers)

    def get_unacknowledged_alerts(self) -> Response:
        """Get all the existing alerts in the DB that have the field "is_acknowledged" set to `False`"""
        return requests.get(self.routes["get-unacknowledged-alerts"], headers=self.headers)

    def get_site_devices(self, site_id: int, payload: Dict[str, Any]) -> Response:
        """ Get all devices installed in a specific site"""
        return requests.get(self.routes["get-site-devices"].format(site_id=site_id), headers=self.headers, data=payload)

    def get_media_url(self, media_id: int) -> Response:
        """ Get the image as a url"""
        return requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)

    def get_media_url_and_read(self, media_id: int) -> Response:
        """ Get the image as a url and read it"""
        image_url = requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)
        return requests.get(image_url)

    def get_media_image(self, media_id: int) -> Response:
        """ Get the image as a streaming file"""
        return requests.get(self.routes["get-media-image"].format(media_id=media_id), headers=self.headers)
