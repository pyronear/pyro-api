# Pyronear API

<p align="center">
  <a href="https://github.com/pyronear/pyro-api/actions?query=workflow%3Abuilds">
    <img alt="CI Status" src="https://img.shields.io/github/workflow/status/pyronear/pyro-api/builds?label=CI&logo=github&style=flat-square">
  </a>
  <a href="http://pyronear-api.herokuapp.com/redoc">
    <img src="https://img.shields.io/github/workflow/status/pyronear/pyro-api/builds?label=docs&logo=read-the-docs&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/pyronear/pyro-api">
    <img src="https://img.shields.io/codecov/c/github/pyronear/pyro-api.svg?logo=codecov&style=flat-square" alt="Test coverage percentage">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://www.codacy.com/gh/pyronear/pyro-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pyronear/pyro-api&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/3bea1a63e4aa44258cfd08831d713478"/></a>
</p>
<p align="center">
  <a href="https://pypi.org/project/pyroclient/">
    <img src="https://img.shields.io/pypi/v/pyroclient.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPi Status">
  </a>
  <a href="https://anaconda.org/pyronear/pyroclient">
    <img alt="Anaconda" src="https://img.shields.io/conda/vn/pyronear/pyroclient?style=flat-square?style=flat-square&logo=Anaconda&logoColor=white&label=conda">
  </a>
  <a href="https://hub.docker.com/r/pyronear/pyro-api">
    <img alt="Docker Image Version" src="https://img.shields.io/docker/v/pyronear/pyro-api?style=flat-square&logo=Docker&logoColor=white&label=docker">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/pyroclient.svg?style=flat-square" alt="pyversions">
  <img src="https://img.shields.io/pypi/l/pyroclient.svg?style=flat-square" alt="license">
</p>


The building blocks of our wildfire detection & monitoring API.


## Getting started

### Prerequisites

- Python 3.7 (or more recent)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

You can clone and install the project dependencies as follows:

```shell
git clone https://github.com/pyronear/pyro-api.git
```

## Usage

If you wish to deploy this project on a server hosted remotely, you might want to be using [Docker](https://www.docker.com/) containers. Beforehand, you will need to set a few environment variables either manually or by writing an `.env` file in the root directory of this project, like in the example below:

```
QARNOT_TOKEN=my_very_secret_token
BUCKET_NAME=my_storage_bucket_name
BUCKET_MEDIA_FOLDER=my/media/subfolder

```

Those values will allow your API server to connect to our cloud service provider [Qarnot Computing](https://qarnot.com/), which is mandatory for your local server to be fully operational.
Then you can run the API containers using this command:

```shell
docker-compose up -d --build
```

Once completed, you will notice that you have a docker container running on the port you selected, which can process requests just like any django server.



## Documentation

The full project documentation is available [here](http://pyronear-api.herokuapp.com/redoc) for detailed specifications. The documentation was built with [ReDoc](https://redocly.github.io/redoc/).



## Contributing

Please refer to [`CONTRIBUTING`](CONTRIBUTING.md) if you wish to contribute to this project.



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
