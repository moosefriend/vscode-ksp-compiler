#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).
#
# Copyright (c) 2024 MooseFriend (https://github.com/moosefriend)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from pathlib import Path
from types import TracebackType
from typing import Optional, TextIO, Pattern


class RewindReader:
    def __init__(self, file: Path, encoding: str = 'utf-8', right_strip: str = "\n", page_no_pattern: Pattern = None):
        """
        File reader which provides methods to rewind the file pointer to the beginning of the just read line.

        :param file: Text file to read
        :param encoding: File encoding to be used
        :param right_strip: If set then from the read line all characters at the end matching right_strip will be removed
        :param page_no_pattern: If specified then each line matching this pattern is ignored and the group(1) is extracted
            as the page number
        """
        self.file: Path = file
        self.encoding: str = encoding
        self.right_strip: str = right_strip
        self.page_no_pattern: Pattern = page_no_pattern
        self.handle: Optional[TextIO] = None
        self.pos_last_line: int = 0
        self.line_no: int = 0
        self.line_inc: int = 1
        self.page_no: int = 0
        self.rewind_enabled: bool = False

    def __enter__(self):
        """
        Context manager: Open the file and initialize the pointers.
        """
        self.handle = self.file.open(encoding=self.encoding)
        self.line_no = 0
        self.line_inc = 1
        self.page_no = 0
        self.pos_last_line = self.handle.tell()
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType):
        """
        Context manager: Close the file.
        """
        self.handle.close()
        self.line_no = 0
        self.line_inc = 1
        self.page_no = 0
        self.pos_last_line = 0

    def __iter__(self):
        """
        Iterator which reads the separate lines.
        """
        return self

    def __next__(self):
        """
        Get the next line of the file.

        :return: Line read
        """
        # Remember the current position
        self.pos_last_line = self.handle.tell()
        line = self.readline()
        self.line_no += self.line_inc
        self.line_inc = 1
        # Check for lines like "<<<<<<<<<<<<<<<<<<<< Page 259 >>>>>>>>>>>>>>>>>>>>"
        if self.page_no_pattern and (m := self.page_no_pattern.match(line)):
            self.page_no = int(m.group(1))
            line = self.__next__()
        self.rewind_enabled = True
        return line

    def readline(self) -> str:
        """
        Read the next line. If the line is None then a StopIteration is raised.
        This will not update any internal line counters!

        :return: Next line
        """
        line = self.handle.readline()
        if line == "":
            raise StopIteration
        if self.right_strip:
            line = line.rstrip(self.right_strip)
        return line

    def reset(self):
        """
        Rollback to the beginning of the file.
        """
        self.handle.seek(0)

    def rewind(self):
        """
        Rollback the file pointer before the last read line.
        """
        if self.rewind_enabled:
            self.handle.seek(self.pos_last_line)
            self.line_no -= 1
            self.rewind_enabled = False
        else:
            raise IOError("Rollback is only supported for the last read line")

    def location(self) -> str:
        """
        Current location in a way that it's displayed as hyperlink in PyCharm.
        Note that the file MUST be a python file with *.py extension or the link is not diplayed in the PyCharm console.

        :return: Current location with page, file and line number
        """
        location = f"page {self.page_no}, File \"{self.file}\", line {self.line_no}"
        return location
