# API Client

![Build Status](https://github.com/pyronear/pyro-api/workflows/client-package/badge.svg)  [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](http://pyronear.org/pyro-api)

Client for the [Pyronear API](https://github.com/pyronear/pyro-api)



## Table of Contents

- [API Client](#api-client)
  - [Table of Contents](#table-of-contents)
  - [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)
  - [Documentation](#documentation)



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

Distributed under the GPLv3 License. See `LICENSE` for more information.



## Documentation

The full project documentation is available [here](http://pyronear.org/pyro-api) for detailed specifications. The documentation was built with [Sphinx](https://www.sphinx-doc.org/) using a [theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org/).

