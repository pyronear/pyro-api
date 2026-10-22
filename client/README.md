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

Client for the [Alert management API](https://github.com/pyronear/pyro-api)


## Quick Tour

### Interacting with the wildfire alert API

General users can use the API client to request available data within their respective scope (i.e. as a private individual, you won't have access to the data from devices of firefighters; however you will have access to all the data related to your devices). You can find several examples below:

```python
API_URL = os.getenv("API_URL", "http://localhost:5050/api/v1/")
login = os.getenv("USER_LOGIN", "superadmin_login")
pwd = os.getenv("USER_PWD", "superadmin_pwd")
token = requests.post(
    urljoin(API_URL, "login/creds"),
    data={"username": login, "password": pwd},
    timeout=5,
).json()["access_token"]
api_client = Client(token, "http://localhost:5050", timeout=10)

# List organizations accessible in your scope
organizations = api_client.fetch_organizations()
# Get the url of the image of a detection
url = api_client.get_detection_url(detection_id)
```


```python
cam_token = requests.post(urljoin(API_URL, f"cameras/{cam_id}/token"), headers=admin_headers, timeout=5).json()[
    "access_token"
]

camera_client = Client(cam_token, "http://localhost:5050", timeout=10)
response = cam_client.create_detection(image, 123.2)
```

## Installation

### Prerequisites

Python 3.10 (or higher) and [pip](https://pip.pypa.io/en/stable/) are required to install the client of the alert API.

### Installation

The client is not published on PyPI. Install it from source *(install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) first)*:

```shell
git clone https://github.com/pyronear/pyro-api.git
pip install -e pyro-api/client/.
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
