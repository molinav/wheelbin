""":class:`PythonFile` class encapsulation."""

import os
import re
import shutil
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
        if re.match(r"Python script, ASCII text executable.*", header):
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