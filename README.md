# Pyronear API

<p align="center">
  <a href="https://github.com/pyronear/pyro-api/actions?query=workflow%3Abuilds">
    <img alt="CI Status" src="https://img.shields.io/github/actions/workflow/status/pyronear/pyro-api/builds.yml?branch=main&label=CI&logo=github&style=flat-square">
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

The API stores access metadata (Users, Cameras, Organizations), the core wildfire-monitoring workflow (Detections grouped into Sequences), and client integrations (Webhooks). End to end, an alert flows like this: an admin registers a user, the user registers a camera and mints a camera token, then the camera uploads a picture as a detection, which is grouped into a sequence over a dense time window. For the full data model, UML diagram, codebase tour and developer setup, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Quick Tour

Two ways to run the stack, depending on whether you just want to use the API or to develop against it.

### As a user (no Poetry needed)

Pull the published `ghcr.io/pyronear/alert-api` image and start the stack:

```shell
cp .env.example .env
docker compose pull
docker compose up
```

Then navigate to [http://localhost:5050/docs](http://localhost:5050/docs) to interact with the API and explore the OpenAPI documentation.

To stop the service:
```shell
docker compose down
```

### As a contributor (builds locally, requires Poetry)

```shell
make run
```

This regenerates `requirements.txt` from `poetry.lock` and builds the backend image locally, so it requires [Poetry](https://python-poetry.org/docs/) to be installed. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full developer setup, tests, and migration workflow.

To stop the service:
```shell
make stop
```

## Installation

### Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/)

Contributors building the image locally also need [Poetry](https://python-poetry.org/docs/); see [`CONTRIBUTING.md`](CONTRIBUTING.md).

### First-time setup

```shell
git clone https://github.com/pyronear/pyro-api.git && cd pyro-api
cp .env.example .env
```

Then run the stack as described in the [Quick Tour](#quick-tour) above.


## More goodies

### Python client

This project is a REST-API, and you can interact with the service through HTTP requests. However, if you want to ease the integration into a Python project, take a look at our [Python client](client).


## Contributing

Any sort of contribution is greatly appreciated!

[`CONTRIBUTING.md`](CONTRIBUTING.md) covers more than the contribution guidelines: it also documents the data model, codebase structure, developer setup, testing workflow and database migrations. Start there if you want to understand how the project is organised.



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
