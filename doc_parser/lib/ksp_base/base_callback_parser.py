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

from doc_item.callback_item import CallbackItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseCallbackParser(BaseItemParser):
    CALLBACK_PATTERN = re.compile(r"^on\s+([a-z_]+)(?:/([a-z_]+))?(?:\s+\(<([a-z-]+)>\))?$")
    """Pattern to find a callback, e.g. on init"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Callbacks$", re.IGNORECASE)
    """Pattern to find the headline for the content start"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Variables$", re.IGNORECASE)
    """Pattern to find the headline for the content end"""

    def __init__(self, version: str, toc: BaseTocParser, reader: RewindReader, csv_file: Path, delimiter: str,
                 page_offset: int = 0):
        """
        Parse callbacks in the Kontakt KSP text manual.

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
            CallbackItem,
            reader,
            self.CONTENT_START_PATTERN,
            self.CONTENT_STOP_PATTERN,
            csv_file,
            delimiter,
            page_offset
        )

    def check_category(self, line) -> bool:
        """
        Special handling for categories for callbacks.

        For callbacks the category is repeated (at least the beginning).
        And it must be avoided to see examples (e.g. "on init") as callback.
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
            if next_line.startswith(line):
                is_category = True
            self.reader.handle.seek(cur_pos)
        return is_category

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        if self.doc_state == DocState.CATEGORY and line:
            if line.startswith(self.category) and (m := self.CALLBACK_PATTERN.match(line)):
                name_list = [m.group(1)]
                # Check if there is a list of callbacks e.g. rpn/nrpn
                if m.group(2):
                    name_list.append(m.group(2))
                # Check if there is a parameter
                parameter = m.group(3)
                self.item_list = []
                for name in name_list:
                    self.add_callback(name, parameter)
                doc_state = DocState.DESCRIPTION
            else:
                log.error(f"Can't find the expected callback {self.category}, but got {line}")
        return doc_state

    def add_callback(self, name: str, parameter: str):
        """
        Add a callback if it does not exist.

        :param name: Name of the callback
        :param parameter: Optional parameter for the callback
        """
        callback = CallbackItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            parameter=parameter,
            description="",
            remarks="",
            examples="",
            see_also="",
            source="BUILT-IN"
        )
        self.add_item(callback)
