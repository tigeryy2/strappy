"""
Setup script for project.

To install as a standalone project run::

    pipenv install -e .

This installs project in editable mode using this file .

To install as a package, particularly as a submodule inside another project::

    pipenv install -e path-to-submodule

This installs the project in editable mode as a package
"""
import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = "0.1.0"
PACKAGE_NAME = "strappy"
AUTHOR = "Tiger Yang"
AUTHOR_EMAIL = "tigeryyang@gmail.com"
DESCRIPTION = "Bootstrapping setup for macOS development environment."
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

# use `setuptools.find_packages` to discover all modules and packages from the project
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(exclude=["docs", "tests"]),
)
