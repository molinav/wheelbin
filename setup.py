#! /usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa: E122
#
# Copyright (c) 2016 Grant Patten
# Copyright (c) 2020 Víctor Molina García
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""wheelbin -- Compile all Python files inside a wheel to bytecode files."""
import io
import os
import re
from setuptools import setup
from setuptools import find_packages


def get_content(name, splitlines=False):
    """Return the file contents with project root as root folder."""

    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, name)
    with io.open(path, "r", encoding="utf-8") as fd:
        content = fd.read()
    if splitlines:
        content = [row for row in content.splitlines() if row]
    return content


def get_version(pkgname):
    """Return package version without importing the file."""

    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, "src", pkgname, "__init__.py")
    with io.open(path, "r", encoding="utf-8") as fd:
        pattern = r"""\n__version__[ ]*=[ ]*["']([^"]+)["']"""
        return re.search(pattern, fd.read()).group(1)


setup(**{
    "name":
        "wheelbin",
    "version":
        get_version("wheelbin"),
    "license":
        "MIT",
    "description":
        "Compile all Python files inside a wheel to bytecode files",
    "long_description":
        get_content("README.md"),
    "long_description_content_type":
        "text/markdown",
    "url":
        "https://github.com/molinav/wheelbin",
    "author":
        "Grant Patten",
    "author_email":
        "grant@gpatten.com",
    "maintainer":
        "Víctor Molina García",
    "maintainer_email":
        "molinav@users.noreply.github.com",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    "keywords": [
        "pyc",
        "wheel",
        "compile",
    ],
    "package_dir":
        {"": "src"},
    "packages":
        find_packages(where="src"),
    "entry_points": {
        "console_scripts": [
            "wheelbin = wheelbin.__main__:main",
        ]
    },
    "python_requires":
        ", ".join([
            ">=2.6",
            "!=3.0.*",
            "!=3.1.*",
            "<3.11",
        ]),
    "install_requires":
        get_content("requirements.txt", splitlines=True),
    "extras_require": {
        "lint":
            get_content("requirements-lint.txt", splitlines=True),
        "test":
            get_content("requirements-test.txt", splitlines=True),
    },
    "project_urls": {
        "Bug Tracker":
            "https://github.com/molinav/wheelbin/issues",
        "Source":
            "https://github.com/molinav/wheelbin",
    },
})
