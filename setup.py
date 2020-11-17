#
# Copyright (c) 2016 Grant Patten
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
"""wheelbin -- Compile all py files in a wheel to pyc files."""
import io
import os
from setuptools import setup
from setuptools import find_packages
from src.wheelbin import __version__


def get_content(name, splitlines=False):
    """Return the file contents with project root as root folder."""

    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, name)
    with io.open(path, encoding="utf-8") as fd:
        content = fd.read()
    if splitlines:
        content = [row for row in content.splitlines() if row]
    return content


setup(
    name="wheelbin",
    version=__version__,
    author="Grant Patten",
    author_email="grant@gpatten.com",
    url="https://github.com/molinav/wheelbin",
    py_modules=["wheelbin"],
    entry_points={
        "console_scripts": [
            "wheelbin = wheelbin:main",
        ]
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="Compile all py files in a wheel to pyc files",
    long_description=open("README.rst").read(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
    keywords="pyc wheel compile",
    install_requires=get_content("requirements.txt", splitlines=True),
)
