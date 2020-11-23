from setuptools import setup
from setuptools import find_namespace_packages


setup(
    name="pyronear-api",
    version="0.1",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src', include=['app', 'app.*']),
)
