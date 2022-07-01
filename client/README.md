# API Client

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

Client for the [Pyronear API](https://github.com/pyronear/pyro-api)


## Getting started

### Prerequisites

- Python 3.6 (or more recent)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

You can clone and install the project dependencies as follows:

```bash
$git clone https://github.com/pyronear/pyro-api.git
$pip install -e pyro-api/client/.
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

#AS A DEVICE:
## Create a device
event_id = api_client.create_event(lat=10, lon=10).json()["id"]
## Create a media
media_id = api_client.create_media_from_device().json()["id"]
## Create an alert linked to the media and the event
api_client.send_alert_from_device(lat=10, lon=10, event_id=event_id, media_id=media_id)

## Upload an image on the media
dummy_image = "https://ec.europa.eu/jrc/sites/jrcsh/files/styles/normal-responsive/" \
                + "public/growing-risk-future-wildfires_adobestock_199370851.jpeg"
image_data = requests.get(dummy_image)
api_client.upload_media(media_id=media_id, image_data=image_data.content)

## Update your position:
api_client.update_my_location(lat=1, lon=2, pitch=3)



```


## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.



## Documentation

The full project documentation is available [here](http://pyronear.org/pyro-api) for detailed specifications. The documentation was built with [Sphinx](https://www.sphinx-doc.org/) using a [theme](https://github.com/pradyunsg/furo) provided by [Pradyun Gedam](https://github.com/pradyunsg).

