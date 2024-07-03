# Contributing to pyro-api

Everything you need to know to contribute efficiently to the project!

Whatever the way you wish to contribute to the project, please respect the [code of conduct](CODE_OF_CONDUCT.md).


## Data model

The back-end core feature is to interact with the metadata tables. For the service to be useful for wildfire detection, multiple tables/object types are introduced and described as follows:

#### Access-related tables

- Users: stores the hashed credentials and access level for users.
- Cameras: stores the camera metadata.

#### Core worklow tables

- Detection: association of a picture and a camera.

![UML diagram](https://github.com/pyronear/pyro-api/assets/26927750/bf48f757-7cb0-45fd-aea1-b832e969a705)

### What is the full detection workflow through the API

The API has been designed to provide, for each wildfire detection, the alert metadata:
- timestamp
- the picture that was used for detection
- the camera that detected the event

With the previously described tables, here are all the steps to send a wildfire alert:
- Prerequisites (ask the instance administrator): register user
- Register a camera: declare your camera on the API, using your new user credentials.
- Create a camera token: create non-user token for the camera to access the API.
- Create a detection: using the camera credentials, upload the image content and the detection metadata.

## Codebase structure

- [`src/app`](https://github.com/pyronear/pyro-api/blob/main/src/app) - The actual API codebase
- [`src/tests`](https://github.com/pyronear/pyro-api/blob/main/src/tests) - The API unit tests
- [`.github`](https://github.com/pyronear/pyro-api/blob/main/.github) - Configuration for CI (GitHub Workflows)
- [`client`](https://github.com/pyronear/pyro-api/blob/main/client) - Source of the Python client
- [`scripts`](https://github.com/pyronear/pyro-api/blob/main/scripts) - Custom scripts


## Continuous Integration

This project uses the following integrations to ensure proper codebase maintenance:

- [Github Worklow](https://help.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow) - run jobs for package build and coverage
- [Codacy](https://www.codacy.com/) - analyzes commits for code quality
- [Codecov](https://codecov.io/) - reports back coverage results
- [Sentry](https://docs.sentry.io/platforms/python/) - automatically reports errors back to us
- [PostgreSQL](https://www.postgresql.org/) - storing and interacting with the metadata database
- [S3 storage](https://aws.amazon.com/s3/) - the file system for media storage (not necessarily AWS, but requires S3 interface)
- [PostHog](https://posthog.com/) - product analytics
- [Prometheus](https://prometheus.io/) - Scraping API metrics
- [Traefik](https://traefik.io/) - the reverse proxy and load balancer

As a contributor, you will only have to ensure coverage of your code by adding appropriate unit testing of your code.


## Feedback

### Feature requests & bug report

Whether you encountered a problem, or you have a feature suggestion, your input has value and can be used by contributors to reference it in their developments. For this purpose, we advise you to use Github [issues](https://github.com/pyronear/pyro-api/issues).

First, check whether the topic wasn't already covered in an open / closed issue. If not, feel free to open a new one! When doing so, use issue templates whenever possible and provide enough information for other contributors to jump in.

### Questions

If you are wondering how to do something with Pyro-API, or a more general question, you should consider checking out Github [discussions](https://github.com/pyronear/pyro-api/discussions). See it as a Q&A forum, or the Pyro-API-specific StackOverflow!

## Developer setup

### Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/)
- [Poetry](https://python-poetry.org/docs/)
- [Make](https://www.gnu.org/software/make/) (optional)

### Configure your fork

1 - Fork this [repository](https://github.com/pyronear/pyro-api) by clicking on the "Fork" button at the top right of the page. This will create a copy of the project under your GitHub account (cf. [Fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)).

2 - [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) to your local disk and set the upstream to this repo
```shell
git clone git@github.com:<YOUR_GITHUB_ACCOUNT>/pyro-api.git
cd pyro-api
git remote add upstream https://github.com/pyronear/pyro-api.git
```

### Install the dependencies

Let's install the different libraries:
```shell
poetry export -f requirements.txt --without-hashes --with quality --output requirements.txt
pip install -r requirements.txt
```

#### Pre-commit hooks
Let's make your life easier by formatting & fixing lint on each commit:
```shell
pre-commit install
```

### Environment configuration

In order to run the project, you will need to specific some information, which can be done using a `.env` file.
Copy the default environement variables from [`.env.example`](./.env.example):
```shell
cp .env.example .env
```

This file contains all the information to run the project.

#### Values you have to replace
None :)

#### Values you can edit freely
- `POSTGRES_DB`: a name for the [PostgreSQL](https://www.postgresql.org/) database that will be created
- `POSTGRES_USER`: a login for the PostgreSQL database
- `POSTGRES_PASSWORD`: a password for the PostgreSQL database
- `SUPERADMIN_LOGIN`: the login of the initial admin user
- `SUPERADMIN_PWD`: the password of the initial admin user
- `SUPERADMIN_ORG`: the organization of the initial admin user

#### Other optional values
- `JWT_SECRET`: if set, tokens can be reused between sessions. All instances sharing the same secret key can use the same token.
- `SENTRY_DSN`: the DSN for your [Sentry](https://sentry.io/) project, which monitors back-end errors and report them back.
- `SERVER_NAME`: the server tag that will be used to report events to Sentry.
- `POSTHOG_HOST`: the host for PostHog [PostHog](https://eu.posthog.com/settings/project-details).
- `POSTHOG_KEY`: the project API key for PostHog [PostHog](https://eu.posthog.com/settings/project-details).
- `SUPPORT_EMAIL`: the email used for support of your API.
- `DEBUG`: if set to false, silence debug logs.
- `S3_ACCESS_KEY`: public key to access to the [S3 storage service](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
- `S3_SECRET_KEY`: private key to access the resource.
- `S3_REGION`: your S3 bucket is geographically identified by its location's region
- `S3_ENDPOINT_URL`: the URL providing a S3 endpoint by your cloud provider
- `S3_PROXY_URL`: the url of the proxy to hide the real s3 url behind, do not use proxy if ""
- `S3_BUCKET_NAME`: the name of the storage bucket

#### Production-only values
- `ACME_EMAIL`: the email linked to your certificate for HTTPS
- `BACKEND_HOST`: the subdomain where your users will access your API (e.g "api.mydomain.com")


### Developing your feature

#### Commits

- **Code**: ensure to provide docstrings to your Python code. In doing so, please follow [Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) so it can ease the process of documentation later.
- **Commit message**: please follow [Udacity guide](http://udacity.github.io/git-styleguide/)

#### Tests

In order to run the same unit tests as the CI workflows, you can run unittests locally:

```shell
make test
```

This will run the full suite of core API unittests. However, if you're trying to run some specific unittests, you can do as follows:
```shell
make run-dev
docker-compose exec -T backend pytest tests/routes/test_XYZ.py
```

#### Code quality

To run all quality checks together

```shell
make quality
```

The previous command won't modify anything in your codebase. Some fixes (import ordering and code formatting) can be done automatically using the following command:

```shell
make style
```

#### Local deployment

To run the API locally, the easiest way is with Docker. Launch this command in the project directory:

```shell
make run-dev
```

To enable a smoother development experience, we are using [localstack](https://docs.localstack.cloud/overview/) to create a local S3 bucket.
NOTE: please check localstack documentation to understand how to create buckets or to add/delete objects.


### Submit your modifications

Push your last modifications to your remote branch
```shell
git push -u origin a-short-description
```

Then [open a Pull Request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) from your fork's branch. Follow the instructions of the Pull Request template and then click on "Create a pull request".


## Database

### Schema evolution

See [Alembic](https://github.com/pyronear/pyro-api/blob/main/src/alembic) guide to create revision and run it locally.


### Postgres upgrade

With your current PG version, we first make a data extract:
```shell
make run
docker compose exec -it db pg_dumpall -U mybdsuperuserpyro > my_local_dump.sql
./scripts/pg_extract.sh my_local_dump.sql pyro_api_prod >> upgrade_dump.sql
```
We stop the container and remove the volume to prevent it from repopulating the new database
```shell
make stop
docker volume rm pyro-api_postgres_data
```
Now update the Postgres version on your docker. We then run the DB only (to prevent the backend from initializing it) and restore the data:
```shell
docker compose up db -d
cat upgrade_dump.sql| docker compose exec -T db psql -U mybdsuperuserpyro
```
