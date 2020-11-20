import requests
import logging
from exceptions import HTTPRequestException
from urllib.parse import urljoin

logging.basicConfig()


class Client:

    routes = {"token": "/login/access-token",
              "heartbeat": "/device/heartbeat",
              "update-my-location": "/device/update-my-location",
              "send-alert": "/alerts",
              "create-media": "/media",
              "upload-media": "/media/upload"
              }

    def __init__(self, api_url, credentials_login, credentials_password):
        """Client class to interact with the PyroNear API

        Args:
            api_url (str): url of the pyronear API
            credentials_login (str): Login (e.g: username)
            credentials_password (str): Password (e.g: 123456 (don't do this))
        """
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

    def hearbeat(self):
        return requests.put(self.routes["heartbeat"], headers=self.headers)

    def update_my_location(self):
        return requests.put(self.routes["uppdate-my-location"], headers=self.headers)

    def create_alert(self):
        return requests.post(self.routes["create_alert"], headers=self.headers)

    def create_media(self):
        return requests.post(self.routes["create-media"], headers=self.headers)

    def upload_media(self):
        return requests.post(self.routes["upload-media"], headers=self.headers)


if __name__ == "__main__":
    client = Client("http://localhost:8002", "superuser", "superuser")
