Installation
============

The easiest way to install the published `sportsipy` package is via PyPI.
For instructions on installing PIP, visit
`PyPA.io <https://pip.pypa.io/en/stable/installing/>`_ for detailed steps on
installing the package manager for your local environment.

Next, run::

    pip install sportsipy

This installs the latest official release from the original project. The
active fork for this repository is not published to PyPI.

If the bleeding-edge version of this fork is desired, clone this repository
using git and install it from source using the ``pyproject.toml`` metadata::

    git clone https://github.com/mitch-avis/sportsipy
    cd sportsipy
    python -m pip install -e .

This repository targets Python 3.12+.

To build a wheel locally, install the build frontend and run::

    python -m pip install build
    python -m build

This will create a `.whl` file in the `dist` directory which can be installed
with the following command::

    pip install dist/*.whl

Credits: this fork builds on the original `roclark/sportsipy` project and the
`davidjkrause/sportsipy` fork which incorporated key fixes.
