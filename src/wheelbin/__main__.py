#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
"""wheelbin-cli -- Compile all Python files inside a wheel to bytecode files."""
from __future__ import print_function

import os
import sys
import argparse
from . import __version__
from . WheelFile import WheelFile


def convert_wheel(whl_file, exclude=None, verbose=True):
    """Generate a new wheel with only bytecode files."""

    whl_fold = os.path.dirname(whl_file)
    file_ext = os.path.splitext(whl_file)[-1]
    if file_ext != ".whl":
        raise TypeError("File to convert must be a *.whl")

    with WheelFile(whl_file, "r") as whlfd:
        # Unpack to temporary directory and compile.
        whlfd.unpack()
        whlfd.compile_files(exclude=exclude, verbose=verbose)
        # Pack again with the appropriate compiled wheel filename.
        compiled_whlname = whlfd.get_compiled_wheelname()
        compiled_whlpath = os.path.join(whl_fold, compiled_whlname)
        if verbose:
            print("Saving: {0}".format(compiled_whlpath))
        whlfd.pack(compiled_whlpath)
        whlfd.cleanup()


def progname():
    """Return program name."""

    execname = os.path.basename(sys.argv[0])
    if execname == os.path.basename(__file__):
        from . import __name__ as pkgname
        pyname = os.path.basename(sys.executable)
        return "{0} -m {1}".format(pyname, pkgname)
    return None


def main(args=None):
    """Entry point for wheelbin."""

    parser = argparse.ArgumentParser(prog=progname(), description=__doc__)
    parser.add_argument(
        "whl_file",
        help="path to wheel being converted")
    parser.add_argument(
        "-v", "--version", action="version",
        version="%(prog)s {0}".format(__version__))
    parser.add_argument(
        "-q", "--quiet", action="store_true", default=False,
        help="call the script without printing messages")
    parser.add_argument(
        "--exclude", type=str, default=None,
        help="pattern for files excluded from compilation")
    args = parser.parse_args(args)
    convert_wheel(args.whl_file, exclude=args.exclude, verbose=not args.quiet)


if __name__ == "__main__":
    main()
