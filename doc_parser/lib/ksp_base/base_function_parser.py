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
import logging
import re
from pathlib import Path
from typing import Optional

from doc_item.function_item import FunctionItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseFunctionParser(BaseItemParser):
    FUNCTION_PATTERN = re.compile(r"^([a-z_]+)\((x(?:, y)?|<expression>, <shift-bits>)\)(?::\s+(.*))?$")
    """Pattern to find a function, e.g. inc(x)"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Arithmetic Commands & Operators$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Control Statements$", re.IGNORECASE)
    """Pattern to find the end headline for scanning the content"""

    def __init__(self, version: str, toc: BaseTocParser, reader: RewindReader, csv_file: Path, delimiter: str,
                 page_offset: int = 0):
        """
        Parse commands in the Kontakt KSP text manual.

        :param version: Kontakt manual version needed to select the right parser
        :param toc: Table of content parser containing the headlines and categories
        :param reader: Reader for the already open Kontakt KSP text manual
        :param csv_file: Comma separated file to export the parsed data
        :param delimiter: CSV delimiter for the export file
        :param page_offset: The page number is decreased by this offset, e.g. if the page numbers start again with 1
            after the table of contents
        """
        super().__init__(
            version,
            toc,
            FunctionItem,
            reader,
            self.CONTENT_START_PATTERN,
            self.CONTENT_STOP_PATTERN,
            csv_file,
            delimiter,
            page_offset
        )

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        if m := self.FUNCTION_PATTERN.match(line):
            name = m.group(1)
            arguments = m.group(2)
            description = m.group(3)
            parameter_list = []
            if arguments:
                for parameter in arguments.split(","):
                    parameter = parameter.strip()
                    parameter_list.append(parameter)
            self.add_function(name, parameter_list, description)
            doc_state = DocState.DESCRIPTION
        return doc_state

    def add_function(self, name: str, parameter_list: list[str], description: str):
        """
        Add a function if it does not exist.

        :param name: Name of the function
        :param parameter_list: List or parameter names
        :param description: Description (if any)
        """
        if description is None:
            description = ""
        command = FunctionItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            parameter_list=parameter_list,
            description=description,
            source="BUILT-IN"
        )
        self.add_item(command)
