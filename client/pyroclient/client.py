import time
import requests
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_URL = os.getenv("API_URL") if os.getenv("API_URL") else os.getenv("DEFAULT_API_URL")


class Client():
    def __init__(self):
        self.token = ACCESS_TOKEN
        self.api = API_URL
        self.headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    def hearbeat(self):
        return requests.put(self.api + "/devices/heartbeat", headers=self.headers)

    # Remaining routes:
    # devices/location: updating last known position
    # media/post: creating a new media entry
    # media/upload: uploading the content media to a remote bucket / storage + updating the key/path of the corresponding media in the table
    # alerts/post: creating a new alert (we might also have to think about whether it should be creating the involved event)


if __name__ == "__main__":

    client = Client()
    while(True):
        time.sleep(1)
        answer = client.hearbeat()