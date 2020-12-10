# Pyronear API

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/3bea1a63e4aa44258cfd08831d713478)](https://www.codacy.com/gh/pyronear/pyro-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pyronear/pyro-api&amp;utm_campaign=Badge_Grade)![Build Status](https://github.com/pyronear/pyro-api/workflows/fastapi-project/badge.svg) [![codecov](https://codecov.io/gh/pyronear/pyro-api/branch/master/graph/badge.svg)](https://codecov.io/gh/pyronear/pyro-api) [![Docs](https://img.shields.io/badge/docs-available-blue.svg)](http://pyronear-api.herokuapp.com/redoc)

The building blocks of our wildfire detection & monitoring API.



## Table of Contents

- [Pyronear API](#pyronear-api)
  - [Table of Contents](#table-of-contents)
  - [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
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
git clone https://github.com/pyronear/pyro-api.git
pip install -r pyro-api/requirements.txt
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

```bash
PORT=8002 docker-compose up -d --build
```

Once completed, you will notice that you have a docker container running on the port you selected, which can process requests just like any django server.



## Documentation

The full project documentation is available [here](http://pyronear-api.herokuapp.com/redoc) for detailed specifications. The documentation was built with [ReDoc](https://redocly.github.io/redoc/).



## Contributing

Please refer to `CONTRIBUTING` if you wish to contribute to this project.



## License

Distributed under the GPLv3 License. See `LICENSE` for more information.