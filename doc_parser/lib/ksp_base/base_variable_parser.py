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

from doc_item.variable_item import VariableItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseVariableParser(BaseItemParser):
    VAR_PATTERN = re.compile(r"^(?:•?\s*)?([$%!~@?][A-Z]+[A-Z_0-9]*)(\[<(.+)>])?(?:\s+\((.+)\))?$")
    """Pattern to find a variable or constant, e.g. $VAR1, •$VAR1 (comment)"""
    VAR_TABLE_PATTERN = re.compile(r"^([$%!~@?][A-Z]+[A-Z_0-9]*)(\[<(.+)>])?:\s+(.+)$")
    """Pattern to find a variable or constant in a table, e.g. $VAR1: Description"""
    VAR_RANGE_PATTERN = re.compile(r"^(?:•\s*)?([$%!~@?][A-Z_]+)(\d+)\s+\.\.\.\s+([$%!~@?][A-Z_]+)(\d+)$")
    """Pattern to find variable ranges, e.g. $MARK_1 ... $MARK_28"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Built-in Variables and Constants$", re.IGNORECASE)
    """Pattern to find the headline for the content start"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Advanced Concepts$", re.IGNORECASE)
    """Pattern to find the headline for the content end"""

    def __init__(self, version: str, toc: BaseTocParser, reader: RewindReader, csv_file: Path, delimiter: str,
                 page_offset: int = 0):
        """
        Parse variables in the Kontakt KSP text manual.

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
            VariableItem,
            reader,
            self.CONTENT_START_PATTERN,
            self.CONTENT_STOP_PATTERN,
            csv_file,
            delimiter,
            page_offset,
            on_headline=self.reset_descriptions,
            on_category=self.reset_descriptions,
            finalize_item_list=self.finalize_item_list
        )
        self.block_headline: str = ""
        self.block_description: str = ""
        self.item_list_headline: str = ""
        self.comment: str = ""

    def scan_items(self):
        super().scan_items()
        # Special handling for variable ranges, e.g. $MARK_1 ... $MARK_28
        # Copy some attributes from the last variable in range to the other
        for item_list in self.all_items.values():
            variable = item_list[0]
            if isinstance(variable, VariableItem) and variable.range_end:
                # Get the base variable name
                base_name = re.sub(r"_\d+$", "_", variable.name)
                last_name = f"{base_name}{variable.range_end}"
                for i in range(variable.range_start, variable.range_end + 1):
                    cur_name = f"{base_name}{i}"
                    for attribute in ("description", "parsed_text"):
                        value = self.all_items[last_name][0].__dict__[attribute]
                        self.all_items[cur_name][0].__dict__[attribute] = value

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        # TODO: Main variable in the block header followed by description, then the constants
        #    The constants should be also listed in the main variable
        # Check for normal variable
        if m := self.VAR_PATTERN.match(line):
            name = m.group(1)
            parameter = m.group(3)
            self.comment = m.group(4)
            self.add_variable(name, parameter)
            doc_state = DocState.DESCRIPTION
        # Check variable in a table, e.g. $VAR: Description
        elif m := self.VAR_TABLE_PATTERN.match(line):
            name = m.group(1)
            parameter = m.group(3)
            description = m.group(4)
            self.add_variable(name, parameter)
            self.add_item_documentation(description)
            doc_state = DocState.DESCRIPTION
        # Check for variable ranges, e.g. $MARK_1 ... $MARK_28
        elif m := self.VAR_RANGE_PATTERN.match(line):
            base_name = m.group(1)
            range_start = int(m.group(2))
            range_end = int(m.group(4))
            for i in range(range_start, range_end + 1):
                name = f"{base_name}{i}"
                self.add_variable(name, "", range_start, range_end)
            if self.doc_state == DocState.DESCRIPTION:
                self.add_item_documentation(line)
            doc_state = DocState.DESCRIPTION
        # Check for item list headlines
        elif line.endswith(":"):
            # When the line also contains a "." then the item list headline shall only be after the "."
            # The text before the "." should be added to the description of the previous variable.
            if "." in line:
                description, line = line.split(".", 2)
                if self.doc_state == DocState.DESCRIPTION:
                    self.add_item_documentation(description + ".")
                else:
                    self.block_description += description + "."

            # TODO: In the dump of variables also the next item list header is printed:
            #   ********** Parsed Text Start **********
            #   •  $EVENT_PAR_MIDI_CHANNEL
            #   Event parameters to be used with set_event_par_arr() and get_event_par_arr():
            #   ********** Parsed Text End **********
            # Remove the colon from the end
            self.item_list_headline = line[:-1]
            log.debug(f"   - Item List Headline: {self.item_list_headline} ({self.reader.location()})")
            # Don't change the documentation state
            doc_state = self.doc_state
        # Check for block headline or description block before the variable(s)
        elif self.doc_state == DocState.CATEGORY and line != "":
            if not self.block_headline:
                self.block_headline = line
                log.debug(f"   - Block Header: {line} ({self.reader.location()})")
            else:
                self.block_description += line + "\n"
                log.debug(f"   - Block Description: {line} ({self.reader.location()})")
            # Don't change the documentation state
            doc_state = self.doc_state
        return doc_state

    def add_variable(self, name: str, parameter: str, range_start: int = 0, range_end: int = 0):
        """
        Add a variable if it is not in the ignore list or already exists.

        :param name: Name of the variable
        :param parameter: Parameter name if it is e.g. an array
        :param range_start: Start index for variable ranges (e.g. $MARK_0 ... $MARK_28)
        :param range_end: End index for variable ranges (e.g. $MARK_0 ... $MARK_28)
        """
        variable = VariableItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            range_start=range_start,
            range_end=range_end,
            parameter=parameter,
            description=self.block_description,
            block_headline=self.block_headline,
            item_list_headline=self.item_list_headline,
            comment=self.comment,
            see_also="",
            source="BUILT-IN"
        )
        self.add_item(variable)

    def add_item_documentation(self, line):
        # Add the documentation to first found variable or constant
        if self.item_list:
            self.item_list[0].description += line + "\n"

    def reset_descriptions(self, _: str):
        self.block_headline = ""
        self.block_description = ""
        self.item_list_headline = ""

    def finalize_item_list(self):
        """
        Copy the description for all variables.
        """
        if self.item_list:
            first_variable = self.item_list[0]
            see_also = [x.name for x in self.item_list]
            for i, variable in enumerate(self.item_list):
                cur_see_also = see_also.copy()
                # Remove the self reference
                cur_see_also.remove(variable.name)
                variable.see_also = "\n".join(cur_see_also)
                if i == 0:
                    continue
                else:
                    variable.description = first_variable.description
        self.reset_descriptions("")
