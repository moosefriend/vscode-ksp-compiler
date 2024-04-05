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

from doc_item.command_item import CommandItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseCommandParser(BaseItemParser):
    COMMAND_PATTERN = re.compile(r"^on\s+([a-z_]+)(?:/([a-z_]+))?$")
    """Pattern to find a command, e.g. on init"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Callbacks$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Variables$", re.IGNORECASE)
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
        super().__init__(version, toc, CommandItem, reader, self.CONTENT_START_PATTERN, self.CONTENT_STOP_PATTERN,
                         csv_file, delimiter, page_offset)

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        if m := self.COMMAND_PATTERN.match(line):
            name = m.group(1)
            self.add_command(name)
            # TODO: Implement BaseCommandParser.check_item
            doc_state = DocState.DESCRIPTION
        return doc_state

    def add_command(self, name: str) -> CommandItem:
        """
        Add a command if it does not exist.

        :param name: Name of the command
        :return: CommandItem of the just created command or None if duplicate
        """
        command: Optional[CommandItem] = None
        if name in self.all_items:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
            command = CommandItem(
                file=self.reader.file,
                page_no=self.reader.page_no,
                line_no=self.reader.line_no,
                headline=self.headline,
                category=self.category,
                name=name,
                description="",
                remarks="",
                examples="",
                see_also="",
                source="BUILT-IN"
            )
            self.all_items[name] = command
        return command
