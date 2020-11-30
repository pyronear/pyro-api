import requests
import logging
from .exceptions import HTTPRequestException
from urllib.parse import urljoin
import io

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
              "get-site-devices": "/installations/site-devices/{site_id}",
              "get-media-url": "/media/{media_id}/url",
              "get-media-image": "/media/{media_id}/image"
              }

    def __init__(self, api_url, credentials_login, credentials_password):
        self.api = api_url
        self._add_api_url_to_routes()
        self.token = self._retrieve_token(credentials_login, credentials_password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _add_api_url_to_routes(self):
        for k, v in self.routes.items():
            self.routes[k] = urljoin(self.api, v)

    def _retrieve_token(self, login, password):
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
    def hearbeat(self):
        """Updates the last ping of the device"""
        return requests.put(self.routes["heartbeat"], headers=self.headers)

    def update_my_location(self, lat: float = None, lon: float = None,
                           elevation: float = None, yaw: float = None, pitch: float = None):
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

    def create_event(self, lat: float, lon: float):
        """Notify an event (e.g wildfire)."""
        payload = {"lat": lat,
                   "lon": lon}
        return requests.post(self.routes["create-event"], headers=self.headers, json=payload)

    def send_alert(self, lat: float, lon: float, event_id: int, device_id: int, media_id: int = None):
        """Raise an alert to the API"""
        payload = {"lat": lat,
                   "lon": lon,
                   "event_id": event_id,
                   "device_id": device_id
                   }
        if isinstance(media_id, int):
            payload["media_id"] = media_id

        return requests.post(self.routes["send-alert"], headers=self.headers, json=payload)

    def send_alert_from_device(self, lat: float, lon: float, event_id: int, media_id: int = None):
        """Raise an alert to the API from a device (no need to specify device ID)."""
        payload = {"lat": lat,
                   "lon": lon,
                   "event_id": event_id
                   }
        if isinstance(media_id, int):
            payload["media_id"] = media_id

        return requests.post(self.routes["send-alert-from-device"], headers=self.headers, json=payload)

    def create_media(self, device_id: int):
        """Create a media entry"""
        return requests.post(self.routes["create-media"], headers=self.headers, json={"device_id": device_id})

    def create_media_from_device(self):
        """Create a media entry from a device (no need to specify device ID)."""
        return requests.post(self.routes["create-media-from-device"], headers=self.headers, json={})

    def upload_media(self, media_id: int, image_data: bytes):
        """Upload the media content"""
        return requests.post(self.routes["upload-media"].format(media_id=media_id), headers=self.headers,
                             files={'file': io.BytesIO(image_data)})

    # User functions
    def get_my_devices(self):
        """Get the devices who are owned by the logged user"""
        return requests.get(self.routes["get-my-devices"], headers=self.headers)

    def get_sites(self):
        """Get all the existing sites in the DB"""
        return requests.get(self.routes["get-sites"], headers=self.headers)

    def get_all_alerts(self):
        """Get all the existing alerts in the DB"""
        return requests.get(self.routes["get-alerts"], headers=self.headers)

    def get_ongoing_alerts(self):
        """Get all the existing alerts in the DB that have the status 'start'"""
        return requests.get(self.routes["get-ongoing-alerts"], headers=self.headers)

    def get_unacknowledged_alerts(self):
        """Get all the existing alerts in the DB that have the field "is_acknowledged" set to `False`"""
        return requests.get(self.routes["get-unacknowledged-alerts"], headers=self.headers)

    def get_site_devices(self, site_id, payload):
        """ Get all devices installed in a specific site"""
        return requests.get(self.routes["get-site-devices"].format(site_id=site_id), headers=self.headers, data=payload)

    def get_media_url(self, media_id):
        """ Get the image as a url"""
        return requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)

    def get_media_url_and_read(self, media_id):
        """ Get the image as a url and read it"""
        image_url = requests.get(self.routes["get-media-url"].format(media_id=media_id), headers=self.headers)
        return requests.get(image_url)

    def get_media_image(self, media_id):
        """ Get the image as a streaming file"""
        return requests.get(self.routes["get-media-image"].format(media_id=media_id), headers=self.headers)
