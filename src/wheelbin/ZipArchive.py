""":class:`ZipArchive` class encapsulation."""

import os
from zipfile import ZipFile
from zipfile import ZipInfo


class ZipArchive(ZipFile):
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
