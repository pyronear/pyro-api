import requests
from requests.models import Response
import logging
from urllib.parse import urljoin
import io
from typing import Dict, Any

from .exceptions import HTTPRequestException


__all__ = ['Client']

logging.basicConfig()

ROUTES: Dict[str, str] = {
    "token": "/login/access-token",
    "heartbeat": "/devices/heartbeat",
    "update-my-location": "/devices/update-my-location",
    "create-event": "/events",
    "send-alert": "/alerts",
    "send-alert-from-device": "/alerts/from-device",
    "create-media": "/media",
    "create-media-from-device": "/media/from-device",
    "upload-media": "/media/{media_id}/upload",
    "get-my-devices": "/devices/my-devices",
    "get-sites": "/sites",
    "get-alerts": "/alerts",
    "get-ongoing-alerts": "/alerts/ongoing",
    "get-unacknowledged-alerts": "/alerts/unacknowledged",
    "acknowledge-alert": "/alerts/{alert_id}/acknowledge",
    "get-site-devices": "/installations/site-devices/{site_id}",
    "get-media-url": "/media/{media_id}/url",
}


class Client:
    """Client class to interact with the PyroNear API

    Args:
        api_url (str): url of the pyronear API
        credentials_login (str): Login (e.g: username)
        credentials_password (str): Password (e.g: 123456 (don't do this))
    """

    def __init__(self, api_url: str, credentials_login: str, credentials_password: str) -> None:
        self.api = api_url
        # Prepend API url to each route
        self.routes = {k: urljoin(self.api, v) for k, v in ROUTES.items()}
        self.token = self._retrieve_token(credentials_login, credentials_password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

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
    def heartbeat(self) -> Response:
        """Updates the last ping of the device"""
        return requests.put(self.routes["heartbeat"], headers=self.headers)

    def update_my_location(self, lat: float = None, lon: float = None,
                           elevation: float = None, yaw: float = None, pitch: float = None) -> Response:
        """Updates the location of the device"""
        payload = {}

        if lat is not None:
            payload["lat"] = lat
        if lon is not None:
            payload["lon"] = lon
        if elevation is not None:
            payload["elevation"] = elevation
        if yaw is not None:
            payload["yaw"] = yaw
        if pitch is not None:
            payload["pitch"] = pitch

        if len(payload) == 0:
            raise ValueError("At least one location information"
                             + "(lat, lon, elevation, yaw, pitch) must be filled")

        return requests.put(self.routes["update-my-location"], headers=self.headers, json=payload)

    def create_event(self, lat: float, lon: float) -> Response:
        """Notify an event (e.g wildfire)."""
        payload = {"lat": lat,
                   "lon": lon}
        return requests.post(self.routes["create-event"], headers=self.headers, json=payload)

    def send_alert(self, lat: float, lon: float, event_id: int, device_id: int, media_id: int = None) -> Response:
        """Raise an alert to the API"""
        payload = {"lat": lat,
                   "lon": lon,
                   "event_id": event_id,
                   "device_id": device_id
                   }
        if isinstance(media_id, int):
            payload["media_id"] = media_id

        return requests.post(self.routes["send-alert"], headers=self.headers, json=payload)

    def send_alert_from_device(self, lat: float, lon: float, event_id: int, media_id: int = None) -> Response:
        """Raise an alert to the API from a device (no need to specify device ID)."""
        payload = {"lat": lat,
                   "lon": lon,
                   "event_id": event_id
                   }
        if isinstance(media_id, int):
            payload["media_id"] = media_id

        return requests.post(self.routes["send-alert-from-device"], headers=self.headers, json=payload)

    def create_media(self, device_id: int) -> Response:
        """Create a media entry"""
        return requests.post(self.routes["create-media"], headers=self.headers, json={"device_id": device_id})

    def create_media_from_device(self):
        """Create a media entry from a device (no need to specify device ID)."""
        return requests.post(self.routes["create-media-from-device"], headers=self.headers, json={})

    def upload_media(self, media_id: int, image_data: bytes) -> Response:
        """Upload the media content"""
        return requests.post(self.routes["upload-media"].format(media_id=media_id), headers=self.headers,
                             files={'file': io.BytesIO(image_data)})

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

    def acknowledge_alert(self, alert_id: int) -> Response:
        """Switch the `is_acknowledged`field value of the alert to `True`"""
        return requests.put(self.routes["acknowledge-alert"].format(alert_id=alert_id), headers=self.headers)

    def get_site_devices(self, site_id: int, payload: Dict[str, Any]) -> Response:
        """ Get all devices installed in a specific site"""
        return requests.get(self.routes["get-site-devices"].format(site_id=site_id), headers=self.headers, data=payload)

    def get_media_url(self, media_id: int) -> Response:
        """ Get the image as a url"""
        return requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)

    def get_media_url_and_read(self, media_id: int) -> Response:
        """ Get the image as a url and read it"""
        image_url = requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)
        return requests.get(image_url.json()['url'])
