#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (C) 2016 Grant Patten
# Copyright (C) 2020 Víctor Molina García
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
"""wheelbin-cli -- Compile all Python files inside a wheel to bytecode files."""

import os
import argparse
from . import __version__
from . WheelFile import WheelFile


def convert_wheel(whl_file, ignore=None):
    """Generate a new wheel with only bytecode files.

    This wheel will append '.compiled' to the version information.
    """

    whl_fold = os.path.dirname(whl_file)
    file_ext = os.path.splitext(whl_file)[-1]
    if file_ext != ".whl":
        raise TypeError("File to convert must be a *.whl")

    with WheelFile(whl_file, "r") as whl_zip:
        # Unpack to temporary directory and compile.
        whl_zip.unpack()
        whl_zip.compile_files(exclude=ignore)
        # Pack again with the appropriate compiled wheel filename.
        compiled_whlname = whl_zip.get_compiled_wheelname()
        whl_zip.pack(os.path.join(whl_fold, compiled_whlname))


def main(args=None):
    """Entry point for wheelbin."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "whl_file",
        help="path to wheel being converted")
    parser.add_argument(
        "--ignore", type=str, default=None,
        help="pattern for files that skip compilation")
    parser.add_argument(
        "-v", "--version", action="version",
        version="%(prog)s {0}".format(__version__))
    args = parser.parse_args(args)
    convert_wheel(args.whl_file, ignore=args.ignore)


if __name__ == "__main__":
    main()
