#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
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
""":class:`ZipArchive` class encapsulation."""

import os
from zipfile import ZipFile
from zipfile import ZipInfo


class ZipArchive(ZipFile, object):
    """Alternative :class:`~zipfile.ZipFile` with file permission handling."""

    def _extract_member(self, member, targetpath, pwd):
        """Extract a :class:`zipfile.ZipInfo` object to a physical file."""

        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = ZipFile._extract_member(self, member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)

        return targetpath

    def __enter__(self):
        """Enter method when using the object as a context manager."""

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit method when using the object as a context manager."""

        self.close()
