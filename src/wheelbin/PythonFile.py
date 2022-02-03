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
""":class:`PythonFile` class encapsulation."""

import os
import re
import shutil
import base64
import hashlib
import py_compile
from tempfile import NamedTemporaryFile
try:
    from winmagic import magic
except ImportError:
    try:
        import magic
    except ImportError:
        magic = None


class PythonFile(object):
    """Thin wrapper to handle Python source code and bytecode files."""

    def __init__(self, path):

        self.path = path
        if not self.is_pyfile() and not self.is_pycfile():
            raise ValueError("{0} is not a Python file".format(path))

    def is_pyfile(self):
        """Return True if it is a Python file, otherwise False."""

        if magic is None:
            raise ImportError("No module named magic")

        header = magic.from_file(self.path)
        if re.match(r".*[pP]ython3? script.*", header):
            return True

        if self.path.endswith(".py"):
            if re.match(r"empty", header) or re.match(r"ASCII text.*", header):
                return True

        return False

    def is_pycfile(self):
        """Return True if it is a Python bytecode file, otherwise False."""

        if magic is None:
            raise ImportError("No module named magic")

        header = magic.from_file(self.path)
        if re.match(r"python (2\.[6-7]|3.[0-9]) byte-compiled", header):
            return True

        if header == "data":
            return True

        return False

    def compile(self):
        """Replace the Python source code file with the bytecode file."""

        if self.is_pycfile():
            raise ValueError("cannot compile Python bytecode file")

        # Read source file permissions.
        istat = os.stat(self.path).st_mode & 0o777

        # Define bytecode file path.
        iname, iext = os.path.splitext(self.path)
        oext = ".pyc" if iext == ".py" else iext
        opath = "{0}{1}".format(iname, oext)

        # Compile the source file.
        with NamedTemporaryFile(dir=os.path.dirname(self.path)) as tmpfile:
            py_compile.compile(self.path, tmpfile.name)
            shutil.copyfile(tmpfile.name, opath)

        # Keep the source file permissions in the bytecode file.
        os.chmod(opath, istat)

        # Delete the source code file and update the `PythonFile` instance.
        if self.path != opath:
            os.remove(self.path)
        self.path = opath

    @property
    def filesize(self):
        """File size."""

        return os.path.getsize(self.path)

    @property
    def hash(self):
        """File SHA256 hash value."""

        blocksize = 1024
        hash_type = "sha256"
        hash_obj = hashlib.new(hash_type)
        with open(self.path, "rb") as fd:
            for block in iter(lambda: fd.read(blocksize), b""):
                hash_obj.update(block)

        hash_value = base64.urlsafe_b64encode(hash_obj.digest())
        hash_value = hash_value.decode().rstrip("=")
        hash_value = "{0}={1}".format(hash_obj.name, hash_value)
        return hash_value
