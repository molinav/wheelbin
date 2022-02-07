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
""":class:`WheelFile` class encapsulation."""
from __future__ import print_function

import io
import os
import sys
import glob
import shutil
import fnmatch
import distutils.util
from distutils import sysconfig
from zipfile import ZIP_DEFLATED
from . PythonFile import PythonFile
from . ZipArchive import ZipArchive
from . TemporaryDirectory import TemporaryDirectory


class WheelFile(ZipArchive):
    """Interface for wheel files."""

    def __init__(self, *args, **kwargs):

        super(WheelFile, self).__init__(*args, **kwargs)
        self.tmpdir = None

    def unpack(self):
        """Unpack wheel contents into a temporary directory."""

        if self.tmpdir is not None:
            raise OSError("{0} is already unpacked".format(self.filename))

        self.tmpdir = TemporaryDirectory()
        self.extractall(self.tmpdir.name)

    def pack(self, path=None):
        """Pack wheel contents into a wheel file again."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        if path is None:
            path = self.filename

        # Store unpacked contents into a temporary zip file.
        zippath = "{0}.zip".format(self.tmpdir.name)
        zipfold = os.path.normpath(self.tmpdir.name)
        with ZipArchive(zippath, "w", compression=ZIP_DEFLATED) as fd:
            for dirpath, dirnames, filenames in os.walk(self.tmpdir.name):
                for name in sorted(dirnames):
                    item = os.path.normpath(os.path.join(dirpath, name))
                    fd.write(item, os.path.relpath(item, zipfold))
                for name in filenames:
                    item = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(item):
                        fd.write(item, os.path.relpath(item, zipfold))

        # Move temporary zip file into final destination.
        shutil.move(zippath, path)

    def cleanup(self):
        """Clean the temporary unpacking directory."""

        self.tmpdir.cleanup()
        self.tmpdir = None

    def compile_files(self, exclude=None, verbose=False):
        """Compile non-excluded Python files within unpacked wheel file."""

        log = print if verbose else (lambda *args, **kwargs: None)

        # Read the initial record.
        index = None
        record = self.record
        record_filenames = [row[0] for row in record]

        # Loop over the files inside the wheel package.
        for root, _dirs, filenames in os.walk(self.tmpdir.name):

            for filename in filenames:

                ipath = os.path.join(root, filename)
                ipath_rel = os.path.relpath(ipath, self.tmpdir.name)

                if exclude is not None and fnmatch.fnmatch(ipath_rel, exclude):
                    log("Skipping: {0} (excluded)".format(ipath_rel))
                    continue

                # Try to open as Python file.
                try:
                    fileobj = PythonFile(ipath)
                except ValueError:
                    log("Skipping: {0} (non-Python file)".format(ipath_rel))
                    continue

                if not fileobj.is_pyfile():
                    log("Skipping: {0} (non-Python file)".format(ipath_rel))
                    continue

                # Compile if it is a Python source file.
                log("Compiling: {0}".format(ipath_rel))
                fileobj.compile()
                opath = fileobj.path
                opath_rel = os.path.relpath(opath, self.tmpdir.name)
                # Update the entry in the record.
                index = record_filenames.index(ipath_rel)
                record[index] = [opath_rel, fileobj.hash, str(fileobj.filesize)]
                self.record = record

        # Update the wheel tag inside the dist-info.
        self.tag = self.get_compiled_tag()

    @property
    def record(self):
        """Wheel file record."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        record_path = os.path.join(distinfo_dir, "RECORD")

        with io.open(record_path, "r", encoding="utf-8") as fd:
            value = [row.strip("\r\n").split(",") for row in fd.readlines()]
        return value

    @record.setter
    def record(self, value):
        """Set the wheel file record."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        record_path = os.path.join(distinfo_dir, "RECORD")

        with io.open(record_path, "w", encoding="utf-8") as fd:
            fd.write("\n".join([",".join(row) for row in value]))

    @property
    def tag(self):
        """Package tag."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        wheel_path = os.path.join(distinfo_dir, "WHEEL")

        with io.open(wheel_path, "r", encoding="utf-8") as fd:
            for row in fd.readlines():
                if row.startswith("Tag:"):
                    value = row.strip("\n").split(":")[-1].strip()
                    break
        return value

    @tag.setter
    def tag(self, value):
        """Set the package tag."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))
        if isinstance(value, bytes):
            value = value = value.decode("utf-8")

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        wheel_path = os.path.join(distinfo_dir, "WHEEL")

        with io.open(wheel_path, "r", encoding="utf-8") as fd:
            # Read lines and only override the ones starting with "Tag:".
            rows = [row if not row.startswith("Tag:")
                    else "Tag: {0}\n".format(value) for row in fd.readlines()]
            # Remove duplicate tag lines (e.g. if coming from universal wheel).
            rows = [row for i, row in enumerate(rows) if row not in rows[i + 1:]]
        with io.open(wheel_path, "w", encoding="utf-8") as fd:
            fd.write("".join(rows))

    @property
    def pkgname(self):
        """Package name."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        metadata_path = os.path.join(distinfo_dir, "METADATA")

        with io.open(metadata_path, "r", encoding="utf-8") as fd:
            for row in fd.readlines():
                if row.startswith("Name:"):
                    value = row.strip("\n").split(":")[-1].strip()
                    break
        return value

    @property
    def pkgversion(self):
        """Package version."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        metadata_path = os.path.join(distinfo_dir, "METADATA")

        with io.open(metadata_path, "r", encoding="utf-8") as fd:
            for row in fd.readlines():
                if row.startswith("Version:"):
                    value = row.strip("\n").split(":")[-1].strip()
                    break
        return value

    @property
    def wheelname(self):
        """Canonical name for the wheel file."""

        return "{0}-{1}-{2}.whl".format(self.pkgname, self.pkgversion,
                                        self.tag)

    def get_compiled_tag(self):
        """Return the tag for the compiled version of the wheel file."""

        # Get ABI flags.
        abid = ("d" if sysconfig.get_config_var("WITH_PYDEBUG") or
                hasattr(sys, "gettotalrefcount") else "")
        abim = ("m" if sysconfig.get_config_var("WITH_PYMALLOC") and
                sys.version_info < (3, 8) else "")
        abiu = ("u" if sysconfig.get_config_var("Py_UNICODE_SIZE") and
                sys.version_info < (3, 3) else "")

        # Define the three tag items for the compiled wheel.
        pyver = "cp{0}{1}".format(*sys.version_info[:2])
        pyabi = "{0}{1}{2}{3}".format(*[pyver, abid, abim, abiu])
        pyarch = self.get_compiled_arch()

        return "-".join([pyver, pyabi, pyarch])

    def get_compiled_arch(self):  # pylint: disable=no-self-use
        """Return the platform name."""

        value = distutils.util.get_platform().replace("-", "_")
        if value.startswith("macosx"):
            raise NotImplementedError
        if value == "linux_x86_64" and sys.maxsize == 2147483647:
            value = "linux_i686"
        return value

    def get_compiled_wheelname(self):
        """Return the canonical name for the compiled wheel file."""

        return "{0}-{1}-{2}.bin.whl".format(self.pkgname, self.pkgversion,
                                            self.get_compiled_tag())
