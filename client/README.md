# pyroclient

Client for the [Pyronear API](https://github.com/pyronear/pyro-api)

## Installation

```shell
$pip install -e .
```

## Usage

Import the client

```python
from pyroclient import client
```

Create a client object by handling him the API keys

```python
API_URL = "http://pyronear-api.herokuapp.com"
CREDENTIALS_LOGIN = "George Abitbol"
CREDENTIALS_PASSWORD = "AStrong Password"
api_client = client.Client(API_URL, CREDENTIALS_LOGIN, CREDENTIALS_PASSWORD)
```

Use it to query alerts:
```python
# Send alerts:
api_client.send_alert()

# Send medias:
api_client.send_medias()

# Update your position:
api_client.update_location(lat, lon)

```