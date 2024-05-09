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
from copy import deepcopy
from pathlib import Path
from typing import Optional

from doc_item.command_item import CommandItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseCommandParser(BaseItemParser):
    COMMAND_PATTERN = re.compile(r"^([a-z_]+)(?:\((.*)\))?$")
    """Pattern to find a command, e.g. random(<min>, <max>)"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Arithmetic Commands & Operators$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Built-in Variables and Constants$", re.IGNORECASE)
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
            CommandItem,
            reader,
            self.CONTENT_START_PATTERN,
            self.CONTENT_STOP_PATTERN,
            csv_file,
            delimiter,
            page_offset
        )

    def scan_items(self):
        super().scan_items()
        # Special handling for set_rpn()/set_nrpn()
        # Copy the documentation from set_nrpn() to set_rpn()
        set_nrpn_doc_item = self.all_items["set_nrpn"][0]
        set_rpn_doc_item = deepcopy(set_nrpn_doc_item)
        set_rpn_doc_item.name = "set_rpn"
        self.all_items["set_rpn"][0] = set_rpn_doc_item

    def check_category(self, line) -> bool:
        """
        Special handling for categories for commands.

        For commands the category is repeated (at least the beginning).
        So check if the line is repeated (after an empty line).

        :param line: Line to check
        :return: True if the line contains a category
        """
        is_category = False
        if line.startswith("[C]"):
            is_category = True
        elif line in self.chapter_categories:
            # Check if the next line (after an empty line) starts with the same category
            # Remember the current position
            cur_pos = self.reader.handle.tell()
            # Read the next line which should be empty
            self.reader.readline()
            # Read the next line which should start with the category
            next_line = self.reader.readline()
            # Special handling for set_rpn()/set_nrpn()
            if line == "set_rpn()/set_nrpn()":
                is_category = True
            elif line.endswith(")"):
                line = line[:-1]
            if next_line.startswith(line):
                is_category = True
            self.reader.handle.seek(cur_pos)
        return is_category

    def check_item(self, line) -> Optional[DocState]:
        # TODO: The first by_marks() contains in the description also the one from the duplicate. The description of
        #    the duplicate is OK.
        # TODO: set_rpn (line 2947) is not properly parsed, because set_rpn() is together with set_nrpn()
        doc_state: Optional[DocState] = None
        if self.doc_state == DocState.CATEGORY and line and (m := self.COMMAND_PATTERN.match(line)):
            name = m.group(1)
            arguments = m.group(2)
            parameter_list = []
            if arguments:
                for parameter in arguments.split(","):
                    parameter = parameter.strip().replace("<", "").replace(">", "")
                    parameter_list.append(parameter)
            self.add_command(name, parameter_list)
            # Special handling for set_rpn()/set_nrpn(), because there are 2 commands
            # => The doc state should not be changed for the first command
            if name != "set_rpn":
                doc_state = DocState.DESCRIPTION
        return doc_state

    def add_command(self, name: str, parameter_list: list[str]):
        """
        Add a command if it does not exist.

        :param name: Name of the command
        :param parameter_list: List or parameter names
        """
        command = CommandItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            parameter_list=parameter_list,
            description="",
            remarks="",
            examples="",
            see_also="",
            source="BUILT-IN"
        )
        self.add_item(command)
