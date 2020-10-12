# Pyronear API

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/3bea1a63e4aa44258cfd08831d713478)](https://www.codacy.com/gh/pyronear/pyronear-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pyronear/pyronear-api&amp;utm_campaign=Badge_Grade)![Build Status](https://github.com/pyronear/pyronear-api/workflows/fastapi-project/badge.svg) [![codecov](https://codecov.io/gh/pyronear/pyronear-api/branch/master/graph/badge.svg)](https://codecov.io/gh/pyronear/pyronear-api) [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](http://pyronear-api.herokuapp.com/redoc)

The building blocks of our wildfire detection & monitoring API.



## Table of Contents

- [Pyronear API](#pyronear-api)
  - [Table of Contents](#table-of-contents)
  - [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Run tests on Docker](#run-tests-on-docker)
  - [Documentation](#documentation)
  - [Contributing](#contributing)
  - [License](#license)



## Getting started

### Prerequisites

- Python 3.6 (or more recent)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

You can clone and install the project dependencies as follows:

```bash
git clone https://github.com/pyronear/pyronear-api.git
pip install -r pyronear-api/requirements.txt
```



## Usage

If you wish to deploy this project on a server hosted remotely, you might want to be using [Docker](https://www.docker.com/) containers. You can perform the same using this command:

```bash
PORT=8002 docker-compose up -d --build
```

Once completed, you will notice that you have a docker container running on the port you selected, which can process requests just like any django server.


## Run tests on Docker
Once the project has been built with docker using the previous command above. One can launch the unit tests using the following instruction:

```bash
PORT=8002 docker-compose exec web pyttest .
```


## Documentation

The full project documentation is available [here](http://pyronear-api.herokuapp.com/redoc) for detailed specifications. The documentation was built with [ReDoc](https://redocly.github.io/redoc/).



## Contributing

Please refer to `CONTRIBUTING` if you wish to contribute to this project.



## License

Distributed under the GPLv3 License. See `LICENSE` for more information.