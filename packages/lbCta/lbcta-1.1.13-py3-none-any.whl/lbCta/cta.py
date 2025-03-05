"""Interface to the spinners disk Tape backend of EOS (EOSCTADISK)

Copyright © 2022-2024 CERN for the benefit of the LHCb collaboration
Frédéric Hemmer - CERN/Experimental Physics Department

"""

import json
import logging
import pathlib
import re
import shlex
import subprocess
from collections import namedtuple
from enum import IntFlag

XRD_TIMEOUT = 60


class _StatInfoFlags(IntFlag):
    X_BIT_SET = 1
    IS_DIR = 2
    OTHER = 4
    OFFLINE = 8
    IS_READABLE = 16
    IS_WRITABLE = 32
    POSC_PENDING = 64
    BACKUP_EXISTS = 128


class XRDFile(
    namedtuple(
        "File",
        [
            "id",
            "path",
            "size",
            "mtime",
            "flags",
            # the following fields are not always present
            "ctime",
            "atime",
            "mode",
            "owner",
            "group",
        ],
        # defaults are assigned right to left
        defaults=["", "", 0, "", ""],
    )
):
    """XROOTD file with its attributes"""

    def isdir(self) -> bool:
        """Check whether a file is a directory"""
        return bool(self.flags & _StatInfoFlags.IS_DIR)

    def isfile(self) -> bool:
        """Check whether a file is a plain file"""
        return not bool(self.flags & _StatInfoFlags.IS_DIR)

    def ontape(self) -> bool:
        """Check whether a file is a plain file"""
        return bool(self.flags & _StatInfoFlags.BACKUP_EXISTS)

    def ondisk(self) -> bool:
        """Check whether a file is a plain file"""
        return not bool(self.flags & _StatInfoFlags.OFFLINE)

    def __str__(self):
        """print an EOS file"""
        permission = ["-", "-", "-", "-"]
        if self.isdir():
            permission[0] = "d"
        if self.flags & _StatInfoFlags.IS_READABLE:
            permission[1] = "r"
        if self.flags & _StatInfoFlags.IS_WRITABLE:
            permission[2] = "w"
        if self.flags & _StatInfoFlags.X_BIT_SET:
            permission[3] = "x"
        permission = "".join(permission)

        logging.debug(
            "%s: flags: %s",
            self.path,
            self.flags,
        )

        return f"{permission}" f" {self.mtime} {self.size}" f" {self.path}"


class Xrd:
    """Methods interfacing with CTA (xrootd)"""

    def __init__(self, endpoint: str):
        """Inits Xrd class

        Args:
            endpoint: xrootd endpoint

        """
        self.endpoint = endpoint
        # format must be in the form root://hostname
        if not re.match(r"^root://", endpoint):
            raise ValueError(f"{endpoint}: invalid root endpoint")

    @staticmethod
    def _command(command: str) -> list:
        """Issue an EOS or XRootD command in a subproces

        Args:
            command: the XRootd command string

        Raises:
            Nothing

        Returns:
            the XRootD result or None
        """
        logging.debug("%s(%s)", Xrd, command)
        try:
            output = subprocess.run(
                shlex.split(command),
                stdin=None,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                timeout=XRD_TIMEOUT,
                universal_newlines=True,
                shell=False,
                check=True,
            ).stdout.rstrip()  # strip the last newline
            if len(output) == 0:
                return 0, None
            return 0, output
        except subprocess.CalledProcessError as exc:
            return -exc.returncode, f"{exc.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return -1, "Timed out"

    @staticmethod
    def _xrdfsres2list(text: str) -> list:
        """convert an xrdfs command result text to a list

        Args:
            text: an  command output separated by newlines

        Returns:
            a list of EOS output lines
        """
        entries = text.split("\n")
        if len(entries) > 0:
            return entries
        return None

    @staticmethod
    def _xrdstat2tuple(text: str) -> tuple:
        """Convert xrdfs stat text to a Xrdfile tuple

        Note: xrdfs stat may return different information depending on ???
        Only Path, Id, Size, MTime and Flags seem to be always present

        Args:
            entry: string as returned by xrdfs stat

        Returns:
            conversion to an Xrdfile tuple
        """

        text = text.lstrip()  # strip the leading newline
        # this code could certainly be improved
        for line in text.splitlines():
            item = line.split()

            if item[0] == "Path:":
                path = item[1]
            elif item[0] == "Id:":
                ident = int(item[1])
            elif item[0] == "Size:":
                size = int(item[1])
            elif item[0] == "MTime:":
                mtime = item[1] + " " + item[2]
            elif item[0] == "Flags:":
                flags = int(item[1])

        # pylint: disable=possibly-used-before-assignment,used-before-assignment
        return XRDFile(
            path=path,
            id=ident,
            size=size,
            mtime=mtime,
            flags=flags,
        )

    def _stat(self, path: pathlib.Path) -> list:
        """stat an XRootD file

        Note: xrdfs stat may return different information depending on ???
        Only Path, Id, Size, MTime and Flags seem to be always present

        """
        command = f"/usr/bin/xrdfs {self.endpoint} stat {path}"
        rc, res = self._command(command)
        if rc == 0:

            xrdfile = self._xrdstat2tuple(res)
            logging.debug("%s", repr(xrdfile))

            return xrdfile

        raise ValueError(f"{res}")

    @staticmethod
    def status(file: XRDFile) -> str:
        """Converts file status to eos-style text"""
        if file.ontape():
            t_str = "t1"
        else:
            t_str = "t0"
        if file.ondisk():
            d_str = "d1"
        else:
            d_str = "d0"
        return d_str + "::" + t_str

    def list_files(self, path: pathlib.Path, recursive=None) -> list:
        """List file an XRootD path"""
        rflag = "-R" if recursive else ""
        command = f"/usr/bin/xrdfs {self.endpoint} ls -l {rflag} {path}"
        rc, result = self._command(command)
        if rc == 0:
            xrdfiles = []
            if result:
                files = self._xrdfsres2list(result)
                for file in files:
                    fields = file.split()
                    # the last field is the full path name
                    xrdfiles.append(self._stat(fields[-1]))
                return xrdfiles
            return []

        raise RuntimeError(f"{rc}: {result}")

    def prepare_status(self, path: pathlib.Path) -> str:
        """Query the prepare status of a single file

        Args:
            path: absolute file path

        Returns:
            return_code, output tuple. Output is xrdfs stderr in case of error
        """
        command = f"/usr/bin/xrdfs {self.endpoint} query prepare 0 {path}"
        rc, result = self._command(command)
        if rc == 0:
            return json.loads(result)

        raise RuntimeError(f"{rc}: {result}")

    def recall(self, path: pathlib.Path) -> str:
        """Query the prepare status of a single file

        Args:
            path: absolute file path

        Returns:
            return_code, output tuple. Output is xrdfs stderr in case of error
        """
        command = f"/usr/bin/xrdfs {self.endpoint} prepare -s {path}"
        rc, result = self._command(command)
        if rc == 0:
            return result

        raise RuntimeError(f"{rc}: {result}")

    def requested(self, path, recursive=False):
        """returns all files that have been requested to be recalled

        Args:
            path: absolute file path to be queried
            recursive: walk recurivively through all sub directories

        Returns:
            A (possible empty) list of files not being recalled
        """
        files = Xrd(self.endpoint).list_files(path, recursive=recursive)
        files_on_disk = []
        for file in files:
            if not file.ondisk():
                status = self.prepare_status(file.path)
                if not status["responses"][0]["on_tape"]:
                    logging.warning("%s: has no tape copy (yet)", file.path)
                if status["responses"][0]["requested"] is True:
                    files_on_disk.append(
                        {"path": file, "reqtime": status["responses"][0]["req_time"]}
                    )
        return files_on_disk

    def not_on_disk(self, path, recursive=False):
        """returns all files that do not have a disk copy and are not being recalled

        Args:
            path: absolute file path to be queried

        Returns:
            A (possible empty) list of files not on disk nor being recalled
        """
        files = Xrd(self.endpoint).list_files(path, recursive=recursive)
        files_on_disk = []
        for file in files:
            if not file.ondisk():
                status = self.prepare_status(file.path)

                if not status["responses"][0]["on_tape"]:
                    logging.warning("%s: has no tape copy (yet)", file.path)
                if (
                    status["responses"][0]["online"]
                    or status["responses"][0]["has_reqid"]
                ):
                    continue
                files_on_disk.append(file)
        return files_on_disk
