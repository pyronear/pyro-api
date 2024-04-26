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
  <a href="https://hub.docker.com/r/pyronear/pyro-api">
    <img alt="Docker Image Version" src="https://img.shields.io/docker/v/pyronear/pyro-api?style=flat-square&logo=Docker&logoColor=white&label=docker">
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

### How is the database organized

The back-end core feature is to interact with the metadata tables. For the service to be useful for wildfire detection, multiple tables/object types are introduced and described as follows:

#### Access-related tables

- Groups: defines collections of credentials that share a similar scope (e.g. you won't be able to access the same data as the local firefighters).
- Accesses: stores the hashed credentials and access level for users & devices.
- Users: actual humans registered in the database.
- Devices: the registered cameras.

#### Setup-specific tables

- Sites: specific locations (firefighter watchtowers, fire stations, etc.).
- Installations: association linking a device & a site over a given timespan.

#### Core detection worklow tables

- Events: wildfire events.
- Media: metadata of a picture and its storage bucket key.
- Alerts: association of a picture, a device, and an event.

#### Advanced tables

- Webhooks: advanced mechanisms to introduce callbacks on specific routes.

![UML diagram](https://github.com/pyronear/pyro-api/releases/download/v0.1.2/pyroapi_diagram.png)

### What is the full detection workflow through the API

The API has been designed to provide, for each wildfire detection, the alert metadata:
- timestamp
- the picture that was used for detection
- the location is was taken at, and the direction it was taken from

With the previously described tables, here are all the steps to send a wildfire alert:
- Prerequisites (ask the instance administrator): register user
- Register a device: declare your device on the API, using your new user credentials.
- Create a media object & upload content: using the device credentials, save the picture metadata and upload the image content.
- Create an alert: using the device credentials, send all the wildfire metadata.

## Installation

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/)
- [Poetry](https://python-poetry.org/)
- [Make](https://www.gnu.org/software/make/) (optional)

The project was designed so that everything runs with Docker orchestration (standalone virtual environment), so you won't need to install any additional libraries.

## Configuration

In order to run the project, you will need to specific some information, which can be done using a `.env` file.
This file will have to hold the following information:
- `S3_ACCESS_KEY`: public key to access to the [S3 storage service](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
- `S3_SECRET_KEY`: private key to access the resource.
- `S3_REGION`: your S3 bucket is geographically identified by its location's region
- `S3_ENDPOINT_URL`: the URL providing a S3 endpoint by your cloud provider
- `BUCKET_NAME`: the name of the storage bucket
- `POSTGRES_DB`: name of postgres database
- `POSTGRES_USER`: user of postgres database
- `POSTGRES_PASSWORD`: user password of postgres database
- `S3_PROXY_URL`: the url of the proxy to hide the real s3 url behind, do not use proxy if ""
Optionally, the following information can be added:
- `SENTRY_DSN`: the URL of the [Sentry](https://sentry.io/) project, which monitors back-end errors and report them back.
- `SENTRY_SERVER_NAME`: the server tag to apply to events.
- `BUCKET_MEDIA_FOLDER`: the optional subfolder to put the media files in
- `TELEGRAM_TOKEN`: to send notifications via telegram for a new alert (once per event)
- `POSTHOG_KEY`: to enable product analytics

So your `.env` file should look like something similar to:
```
S3_ACCESS_KEY=YOUR_ACCESS_KEY
S3_SECRET_KEY=YOUR_SECRET_KEY
S3_REGION=bucket-region
S3_ENDPOINT_URL='https://s3.mydomain.com/'
BUCKET_NAME=my_storage_bucket_name
POSTGRES_USER=dummy_pg_user
POSTGRES_PASSWORD=dummy_pg_pwd
POSTGRES_DB=dummy_pg_db
SENTRY_DSN='https://replace.with.you.sentry.dsn/'
SENTRY_SERVER_NAME=my_storage_bucket_name
```

The file should be placed at the root folder of your local copy of the project.

## More goodies

### Python client

This project is a REST-API, and you can interact with the service through HTTP requests. However, if you want to ease the integration into a Python project, take a look at our [Python client](client).


## Contributing

Any sort of contribution is greatly appreciated!

You can find a short guide in [`CONTRIBUTING`](CONTRIBUTING.md) to help grow this project!



## License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for more information.
