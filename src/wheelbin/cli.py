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
"""wheelbin -- Compile all Python files inside a wheel to bytecode files."""
from __future__ import print_function

import os
import re
import shutil
import fnmatch
import csv
import json
import base64
import hashlib
import argparse
from . import __version__
from . PythonFile import PythonFile
from . WheelFile import WheelFile

try:
    from winmagic import magic
except ImportError:
    try:
        import magic
    except ImportError:
        magic = None


CHUNK_SIZE = 1024
HASH_TYPE = "sha256"


def is_python_file(path):
    """Return if a path is (very likely) a Python file."""

    if magic is None:
        raise ImportError("No module named magic")

    if str(path).endswith(".py"):
        return True

    header = magic.from_file(path)
    if re.match(r"Python script, ASCII text executable.*", header):
        return True

    return False


def convert_wheel(whl_file, ignore=None):
    """Generate a new wheel with only bytecode files.

    This wheel will append '.compiled' to the version information.
    """

    whl_name, file_ext = os.path.splitext(whl_file)

    if file_ext != ".whl":
        raise TypeError("File to convert must be a *.whl")

    # Clean up leftover files
    shutil.rmtree(whl_name, ignore_errors=True)

    # Extract our zip file temporarily
    with WheelFile(whl_file, "r") as whl_zip:
        whl_zip.extractall(whl_name)

    # Loop over files inside the wheel package.
    for root, _dirs, files in os.walk(whl_name):
        for f in files:

            ipath = os.path.join(root, f)
            ipath_rel = os.path.relpath(ipath, whl_name)
            if ignore is not None and fnmatch.fnmatch(ipath, ignore):
                print("Skipping file: {0}".format(ipath_rel))
                continue

            # Try to open as Python file.
            try:
                fileobj = PythonFile(ipath)
            except ValueError:
                continue

            # Try to compile if it is a Python source file.
            if fileobj.is_pyfile():
                fileobj.compile()

    # Update the record data.
    dist_info = "%s.dist-info" % os.path.basename(whl_name).rsplit("-", 3)[0]
    dist_info_path = os.path.join(whl_name, dist_info)
    record_path = os.path.join(dist_info_path, "RECORD")
    rewrite_record(record_path, ignore=ignore)

    # Update version to include '.compiled'.
    update_version(dist_info_path)

    # Rezip the file with the new version info.
    rezip_whl(whl_name)

    # Clean up original directory.
    shutil.rmtree(whl_name)


def rewrite_record(record_path, ignore=None):
    """Rewrite the record file with bytecode files instead of Python files."""

    record_data = []
    whl_path = os.path.dirname(os.path.dirname(record_path))

    if not os.path.exists(record_path):
        return

    with open(record_path, "r") as record:
        for file_dest, hash_, length in csv.reader(record):

            ipath = os.path.join(whl_path, file_dest)
            iext = os.path.splitext(ipath)[-1]
            if os.path.exists(ipath) and iext and not is_python_file(ipath):
                record_data.append((file_dest, hash_, length))
            elif ignore is not None and fnmatch.fnmatch(ipath, ignore):
                record_data.append((file_dest, hash_, length))
            else:

                # Define the bytecode file path.
                iname, iext = os.path.splitext(ipath)
                if iext == ".py":
                    oext = ".pyc"
                elif iext == "":
                    oext = ".exe" if os.name == "nt" else ""
                else:
                    raise ValueError(iname, iext)
                opath = "{0}{1}".format(iname, oext)
                odest_file = os.path.relpath(opath, whl_path)

                # Do not keep Python files, replace with bytecode files.
                file_length = 0
                hash_ = hashlib.new(HASH_TYPE)

                with open(opath, "rb") as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        hash_.update(data)
                        file_length += len(data)

                hash_value = base64.urlsafe_b64encode(hash_.digest())
                hash_value = hash_value.decode().rstrip("=")
                hash_value = "%s=%s" % (HASH_TYPE, hash_value)
                record_data.append((odest_file, hash_value, file_length))

    with open(record_path, "w") as record:
        rows = sorted(set(record_data))
        csv.writer(record, lineterminator="\n").writerows(rows)


def update_version(dist_info_path):
    """Update the wheel to include '.version' in the name."""

    metapath = os.path.join(dist_info_path, "METADATA")
    if os.path.exists(metapath):
        with open(metapath, "r") as f:
            original_metadata = f.read()
        with open(metapath, "w") as f:
            for line in original_metadata.splitlines():
                if line.startswith("Version: "):
                    f.write(line + ".compiled\n")
                else:
                    f.write(line + "\n")

    metapath = os.path.join(dist_info_path, "metadata.json")
    if os.path.exists(metapath):
        with open(metapath, "r") as f:
            json_metadata = json.load(f)
        json_metadata["version"] += ".compiled"
        with open(metapath, "w") as f:
            json.dump(json_metadata, f)

    # Rename dist-info directory.
    new_dist_info_path = dist_info_path[:-10] + ".compiled.dist-info"
    os.rename(dist_info_path, new_dist_info_path)


def rezip_whl(whl_name):
    """Rezip the wheel file with the new compiled name."""

    new_zip_name = whl_name.split("-")
    new_zip_name[1] += ".compiled"
    new_zip_name = "-".join(new_zip_name)

    try:
        os.remove(new_zip_name)
    except OSError:
        pass

    shutil.make_archive(new_zip_name, "zip", whl_name)
    shutil.move(new_zip_name + ".zip", new_zip_name + ".whl")


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
