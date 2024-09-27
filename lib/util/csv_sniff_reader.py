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
import csv
from pathlib import Path
from types import TracebackType
from typing import Optional, TextIO


class CsvSniffReader:
    def __init__(self, csv_file: Path, delimiter: str = None, encoding: str = 'utf-8', ):
        """
        Read a *.csv file by sniffing the dialect.

        :param csv_file: Comma separated file containing the parsed variables/constants
        :param delimiter: If specified then only one of the delimiters are allowed
        :param encoding: File encoding to be used
        """
        self.csv_file: Path = csv_file
        self.delimiter: str = delimiter
        self.encoding: str = encoding
        self.handle: Optional[TextIO] = None
        self.csv_reader = None
        self.line_no: int = 0

    def __enter__(self):
        """
        Context manager: Open the file.
        """
        self.handle = self.csv_file.open(newline='', encoding=self.encoding)
        dialect = csv.Sniffer().sniff(self.handle.read(1024), delimiters=self.delimiter)
        self.handle.seek(0)
        self.csv_reader = csv.reader(self.handle, dialect)
        self.line_no = 0
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType):
        """
        Context manager: Close the file.
        """
        self.handle.close()
        self.line_no = 0

    def __iter__(self):
        """
        Iterator which reads the separate rows of the *.csv file.
        """
        return self

    def __next__(self):
        """
        Get the next row of the *.csv file.

        :return: Row read from the *.csv
        """
        row = self.csv_reader.__next__()
        if row is None:
            raise StopIteration
        self.line_no += 1
        return row
