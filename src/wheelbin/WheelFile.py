""":class:`WheelFile` class encapsulation."""

import os
import sys
import csv
import glob
import shutil
import fnmatch
from distutils import sysconfig
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
        """Repack wheel contents into a wheel file again."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        if path is None:
            path = self.filename
        shutil.make_archive(self.tmpdir.name, "zip", self.tmpdir.name)
        shutil.move("{0}.zip".format(self.tmpdir.name), path)

    def compile_files(self, exclude=None):
        """Compile non-excluded Python files within unpacked wheel file."""

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
                    print("Skipping file: {0}".format(ipath_rel))
                    continue

                # Try to open as Python file.
                try:
                    fileobj = PythonFile(ipath)
                except ValueError:
                    continue

                if fileobj.is_pyfile():
                    # Compile if it is a Python source file.
                    fileobj.compile()
                    opath = fileobj.path
                    opath_rel = os.path.relpath(opath, self.tmpdir.name)
                    # Update the entry in the record.
                    index = record_filenames.index(ipath_rel)
                    record[index] = [opath_rel, fileobj.hash, fileobj.filesize]
                    self.record = record

    @property
    def record(self):
        """Wheel file record."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        record_path = os.path.join(distinfo_dir, "RECORD")

        with open(record_path, "r") as fd:
            value = list(csv.reader(fd))
        return value

    @record.setter
    def record(self, value):
        """Set the wheel file record."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        record_path = os.path.join(distinfo_dir, "RECORD")

        with open(record_path, "w") as fd:
            csv.writer(fd, lineterminator="\n").writerows(value)

    @property
    def tag(self):
        """Package tag."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        wheel_path = os.path.join(distinfo_dir, "WHEEL")

        with open(wheel_path, "r") as fd:
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

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        wheel_path = os.path.join(distinfo_dir, "WHEEL")

        with open(wheel_path, "r") as fd:
            rows = [row if not row.startswith("Tag:")
                    else "Tag: {0}\n".format(value) for row in fd.readlines()]
        with open(wheel_path, "w") as fd:
            fd.write("".join(rows))

    @property
    def pkgname(self):
        """Package name."""

        if self.tmpdir is None:
            raise OSError("{0} is not unpacked".format(self.filename))

        distinfo_dir = glob.glob("{0}/*.dist-info".format(self.tmpdir.name))[0]
        wheel_path = os.path.join(distinfo_dir, "METADATA")

        with open(wheel_path, "r") as fd:
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
        wheel_path = os.path.join(distinfo_dir, "METADATA")

        with open(wheel_path, "r") as fd:
            for row in fd.readlines():
                if row.startswith("Version:"):
                    value = row.strip("\n").split(":")[-1].strip()
                    break
        return value

    def get_compiled_tag(self):
        """Return the tag for the compiled version of the wheel file."""

        pyarch_orig = self.tag.split("-")[-1]

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
        pyarch = pyarch_orig

        return "-".join([pyver, pyabi, pyarch])

    def get_compiled_wheelname(self):
        """Return the canonical name for the compiled wheel file."""

        return "{0}-{1}-{2}.bin.whl".format(self.pkgname, self.pkgversion,
                                            self.get_compiled_tag())
