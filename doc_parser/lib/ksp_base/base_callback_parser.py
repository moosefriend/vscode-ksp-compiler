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

    @staticmethod
    def content_start_pattern():
        return re.compile(r"^(\d+\.\s+)?Callbacks$", re.IGNORECASE)

    @staticmethod
    def content_stop_pattern():
        return re.compile(r"^(\d+\.\s+)?Variables$", re.IGNORECASE)

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
        super().__init__(version, toc, CallbackItem, reader, csv_file, delimiter, page_offset)

    def check_item(self, line) -> bool:
        callback_found: bool = False
        if self.doc_state == DocState.CATEGORY:
            if line:
                if line.startswith(self.category) and (m := self.CALLBACK_PATTERN.match(line)):
                    name_list = [m.group(1)]
                    # Check if there is a list of callbacks e.g. rpn/nrpn
                    if m.group(2):
                        name_list.append(m.group(2))
                    # Check if there is a parameter
                    parameter = m.group(3)
                    self.item_list = []
                    for name in name_list:
                        callback = self.add_callback(name, parameter)
                        self.item_list.append(callback)
                    self.doc_state = DocState.DESCRIPTION
                    callback_found = True
                else:
                    log.error(f"Can't find the expected callback {self.category}, but got {line}")
        return callback_found

    def add_item_documentation(self, line):
        for callback in self.item_list:
            # Add the line to the corresponding attribute
            text = getattr(callback, self.doc_state.value)
            setattr(callback, self.doc_state.value, f"{text}{line}\n")

    def add_callback(self, name: str, parameter: str) -> CallbackItem:
        """
        Add a callback if it does not exist.

        :param name: Name of the callback
        :param parameter: Optional parameter for the callback
        :return: CallbackItem of the just created callback or None if duplicate
        """
        callback: Optional[CallbackItem] = None
        if name in self.all_items:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
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
            self.all_items[name] = callback
        return callback
