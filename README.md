# Pyronear API

<p align="center">
  <a href="https://github.com/pyronear/pyro-api/actions?query=workflow%3Abuilds">
    <img alt="CI Status" src="https://img.shields.io/github/actions/workflow/status/pyronear/pyro-api/builds.yml?branch=main&label=CI&logo=github&style=flat-square">
  </a>
  <a href="http://pyronear-api.herokuapp.com/redoc">
    <img src="https://img.shields.io/github/actions/workflow/status/pyronear/pyro-api/builds.yml?brain=main&label=docs&logo=read-the-docs&style=flat-square" alt="Documentation Status">
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
  <a href="https://hub.docker.com/r/pyronear/alert-api">
    <img alt="Docker Image Version" src="https://img.shields.io/docker/v/pyronear/alert-api?style=flat-square&logo=Docker&logoColor=white&label=docker">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/pyroclient.svg?style=flat-square" alt="pyversions">
  <img src="https://img.shields.io/pypi/l/pyroclient.svg?style=flat-square" alt="license">
</p>


The building blocks of our wildfire detection & monitoring API.

## Quick Tour

### Running/stopping the service

You can run the API containers using this command:

```shell
make run
```

You can now navigate to `http://localhost:8080/docs` to interact with the API (or do it through HTTP requests) and explore the documentation.

![Swagger](https://github.com/pyronear/pyro-api/releases/download/v0.1.2/swagger_interface.png)

In order to stop the service, run:
```shell
make stop
```

## Installation

### Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/)

### Starting your service

#### 1 - Clone the repository
```shell
git clone https://github.com/pyronear/pyro-api.git && cd pyro-api
```
#### 2 - Set your environment variables
First copy the example environment setup
```shell
cp .env.example .env
```

#### 3 - Start the services

```shell
docker compose pull
docker compose up
```

#### 4 - Check how what you've deployed

You can now access your backend API at [http://localhost:5050/docs](http://localhost:5050/docs)


## More goodies

### Python client

This project is a REST-API, and you can interact with the service through HTTP requests. However, if you want to ease the integration into a Python project, take a look at our [Python client](client).


## Contributing

Any sort of contribution is greatly appreciated!

You can find a short guide in [`CONTRIBUTING`](CONTRIBUTING.md) to help grow this project!



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
