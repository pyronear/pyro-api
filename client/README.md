# API Client

![Build Status](https://github.com/pyronear/pyro-api/workflows/client-package/badge.svg)  [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](http://pyronear.org/pyro-api)

Client for the [Pyronear API](https://github.com/pyronear/pyro-api)



## Table of Contents

- [API Client](#pyro-client)
  - [Table of Contents](#table-of-contents)
  - [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
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
# Send alerts:
api_client.send_alert()

# Send medias:
api_client.send_medias()

# Update your position:
api_client.update_location(lat, lon)

```



## Documentation

The full project documentation is available [here](http://pyronear.org/pyro-api) for detailed specifications. The documentation was built with [Sphinx](https://www.sphinx-doc.org/) using a [theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org/).

