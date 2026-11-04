
************
Installation
************

Python 3.10 (or higher) and `pip <https://pip.pypa.io/en/stable/>`_ are required to install the client of the alert API.

Via Git
=======

The client is installed from the repository. Pin a tag or commit:

.. code:: bash

    pip install "git+https://github.com/pyronear/pyro-api.git@v1.0.9#subdirectory=client"

For development, install it in editable mode:

.. code:: bash

    git clone https://github.com/pyronear/pyro-api.git
    pip install -e pyro-api/client/.

The ``pyroclient`` package on PyPI is a legacy distribution and is no longer updated.
