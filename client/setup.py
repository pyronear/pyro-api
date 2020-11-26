#!usr/bin/python

"Package installation setup"

import os
import subprocess
from setuptools import setup, find_packages

package_name = "pyroclient"
with open(os.path.join(package_name, "version.py")) as version_file:
    version = version_file.read().strip()
sha = "Unknown"

cwd = os.path.dirname(os.path.abspath(__file__))

try:
    sha = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd)
        .decode("ascii")
        .strip()
    )
except Exception as e:
    print(e)
    pass

if os.getenv("BUILD_VERSION"):
    version = os.getenv("BUILD_VERSION")
elif sha != "Unknown":
    version += "+" + sha[:7]
print("Building wheel {}-{}".format(package_name, version))


with open("README.md") as f:
    readme = f.read()


requirements = [
    'requests>=2.24.0',
]


setup(
    name=package_name,
    version=version,
    author="Pyronear Contributors",
    description="Client of the Pyronear API to help the fight against wildfires",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pyronear/pyro-api/tree/master/client",
    download_url="https://github.com/pyronear/pyro-api/tags",
    license="GPLv3",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["backend", "wildfire", "client", "api"],
    packages=find_packages(exclude=("test",)),
    zip_safe=True,
    python_requires=">=3.6.0",
    include_package_data=True,
    install_requires=requirements,
    package_data={"": ["LICENSE"]},
)
