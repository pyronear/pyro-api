# Alert API Client

<p align="center">
  <a href="https://github.com/pyronear/pyro-api/actions?query=workflow%3Aclient">
    <img alt="CI Status" src="https://img.shields.io/github/workflow/status/pyronear/pyro-api/client?label=CI&logo=github&style=flat-square">
  </a>
  <a href="http://pyronear.org/pyro-api">
    <img alt="Documentation Status" src="https://img.shields.io/github/workflow/status/pyronear/pyro-api/docs?label=docs&logo=read-the-docs&style=flat-square">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/pyroclient/">
    <img src="https://img.shields.io/pypi/v/pyroclient.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPi Status">
  </a>
  <a href="https://anaconda.org/pyronear/pyroclient">
    <img alt="Anaconda" src="https://img.shields.io/conda/vn/pyronear/pyroclient?style=flat-square?style=flat-square&logo=Anaconda&logoColor=white&label=conda">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/pyroclient.svg?style=flat-square" alt="pyversions">
  <img src="https://img.shields.io/pypi/l/pyroclient.svg?style=flat-square" alt="license">
</p>

Client for the [Alert management API](https://github.com/pyronear/pyro-api)


## Quick Tour

### Interacting with the wildfire alert API

General users can use the API client to request available data within their respective scope (i.e. as a private individual, you won't have access to the data from devices of firefighters; however you will have access to all the data related to your devices). You can find several examples below:

```python
API_URL = "http://pyronear-api.herokuapp.com"
USER_LOGIN = "George Abitbol"
USER_PASSWORD = "AStrong Password"
api_client = client.Client(API_URL, USER_LOGIN, USER_PASSWORD)

# List your registered devices
devices = api_client.get_my_devices().json()
# List organizations accessible in your scope
organizations = api_client.get_organizations().json()
# List all past events in your scope
events = api_client.get_past_events().json()
# List all alerts in your scope
alerts = api_client.get_alerts().json()
```

### Using the client for your local device

If you have a registered device, there are several different interactions (some client methods are restricted to specific access type):

```python
API_URL = "http://pyronear-api.herokuapp.com"
DEVICE_LOGIN = "R2D2"
DEVICE_PASSWORD = "C3POIsTheBest"
api_client = client.Client(API_URL, DEVICE_LOGIN, DEVICE_PASSWORD)

# Retrieve the registered information about your device
api_client.get_my_device()
# Notify the instance that your device is still active
api_client.heartbeat()
## Create an event
event_id = api_client.create_event(lat=10, lon=10).json()["id"]
## Create a media
media_id = api_client.create_media_from_device().json()["id"]
## Create an alert linked to the media and the event
api_client.send_alert_from_device(lat=10, lon=10, event_id=event_id, media_id=media_id)

## Upload an image linked to the media
dummy_image = "https://ec.europa.eu/jrc/sites/jrcsh/files/styles/normal-responsive/" \
                + "public/growing-risk-future-wildfires_adobestock_199370851.jpeg"
image_data = requests.get(dummy_image).content
api_client.upload_media(media_id=media_id, image_data=image_data)

## Update your position:
api_client.update_my_location(lat=1, lon=2, elevation=50, azimuth=30, pitch=3)
# Update your software hash
api_client.update_my_hash("MyNewHash")
```

## Installation

### Prerequisites

Python 3.8 (or higher) and [pip](https://pip.pypa.io/en/stable/)/[conda](https://docs.conda.io/en/latest/miniconda.html) are required to install the client of the alert API.

### Latest stable release

You can install the last stable release of the package using [pypi](https://pypi.org/project/pyroclient/) as follows:

```shell
pip install pyroclient
```

or using [conda](https://anaconda.org/pyronear/pyroclient):

```shell
conda install -c pyronear pyroclient
```

### Developer mode

Alternatively, if you wish to use the latest features of the project that haven't made their way to a release yet, you can install the package from source *(install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) first)*:

```shell
git clone https://github.com/pyronear/pyro-api.git
$pip install -e pyro-api/client/.
```

### Getting an access to the API

What you need to use the client:
- URL to the target Alert API
- credentials (login & password)

If you're running your local/own instance of the API, you can generate your own credentials. Otherwise, you will need to request credentials from the instance administrator. For our public API instance, at the moment, we don't provide public access to the API, it's only reserved to these type of users:
- Pyronear members
- firefighters and stakeholders of wildfire prevention
- People looking at registering their own device


## More goodies

### Documentation

The full package documentation is available [here](http://pyronear.org/pyro-api) for detailed specifications.


## Contributing

Any sort of contribution is greatly appreciated!

You can find a short guide in [`CONTRIBUTING`](CONTRIBUTING.md) to help grow this project!



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
