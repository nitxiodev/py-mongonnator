import os
import re

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Read version from init
regex = re.compile(r"__version__\s*=\s*(\S+)", re.M)
data = open(os.path.join("mongonator", "__init__.py")).read()

setuptools.setup(
    name="PyMongonnator",
    version=eval(regex.search(data).group(1)),
    author="nitxiodev",
    author_email="smnitxio@gmail.com",
    description="Simple pymongo paginator using bucket pattern",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nitxiodev/py-mongonnator",
    packages=setuptools.find_packages(),
    install_requires=[
        "pymongo[srv]>=3.10.1",
    ],
    test_requires=[
        "pytest",
        "pytest-cov",
        "coverage==4.5.4",
        "tox",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
)
