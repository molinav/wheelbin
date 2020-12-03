""":class:`WheelFile` class encapsulation."""

import os
import shutil
import fnmatch
from tempfile import TemporaryDirectory
from . PythonFile import PythonFile
from . ZipArchive import ZipArchive


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

    def repack(self, path=None):
        """Repack wheel contents into a wheel file again."""

        if path is None:
            path = self.filename
        shutil.make_archive(self.tmpdir.name, "zip", self.tmpdir.name)
        shutil.move("{0}.zip".format(self.tmpdir.name), path)

    def compile_files(self, exclude=None):
        """Compile non-excluded Python files within unpacked wheel file."""

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

                # Try to compile if it is a Python source file.
                if fileobj.is_pyfile():
                    fileobj.compile()