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

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        # TODO: Main variable in the block header followed by description, then the constants
        #    The constants should be also listed in the main variable
        # Check for normal variable
        if m := self.VAR_PATTERN.match(line):
            name = m.group(1)
            parameter = m.group(3)
            self.comment = m.group(4)
            variable = self.add_variable(name, parameter)
            if variable:
                self.item_list.append(variable)
            # if self.doc_state == DocState.DESCRIPTION:
            #     self.add_item_documentation(line)
            doc_state = DocState.DESCRIPTION
        # Check variable in a table, e.g. $VAR: Description
        elif m := self.VAR_TABLE_PATTERN.match(line):
            name = m.group(1)
            parameter = m.group(3)
            description = m.group(4)
            variable = self.add_variable(name, parameter)
            if variable:
                self.item_list.append(variable)
                self.add_item_documentation(description)
            doc_state = DocState.DESCRIPTION
        # Check for variable ranges, e.g. $MARK1 ... $MARK28
        elif m := self.VAR_RANGE_PATTERN.match(line):
            base_name = m.group(1)
            start_index = int(m.group(2))
            end_index = int(m.group(4))
            for i in range(start_index, end_index + 1):
                name = f"{base_name}{i}"
                variable = self.add_variable(name, "")
                if variable:
                    self.item_list.append(variable)
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
            # Remove the colon from the end
            self.item_list_headline = line[:-1]
            log.info(f"   - Item List Headline: {self.item_list_headline} ({self.reader.location()})")
            # Don't change the documentation state
            doc_state = self.doc_state
        # Check for block headline or description block before the variable(s)
        elif self.doc_state == DocState.CATEGORY and line != "":
            if not self.block_headline:
                self.block_headline = line
                log.info(f"   - Block Header: {line} ({self.reader.location()})")
            else:
                self.block_description += line + "\n"
                log.info(f"   - Block Description: {line} ({self.reader.location()})")
            # Don't change the documentation state
            doc_state = self.doc_state
        return doc_state

    def add_variable(self, name: str, parameter) -> VariableItem:
        """
        Add a variable if it is not in the ignore list or already exists.

        :param name: Name of the variable
        :param parameter: Parameter name if it is e.g. an array
        :return: VariableItem of the just created variable or None if duplicate or ignored
        """
        variable = VariableItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            parameter=parameter,
            description=self.block_description,
            block_headline=self.block_headline,
            item_list_headline=self.item_list_headline,
            comment=self.comment,
            see_also=[],
            source="BUILT-IN"
        )
        if name in self.all_items:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
            self.all_items[name] = []
        self.all_items[name].append(variable)
        return variable

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
                variable.see_also = see_also.copy()
                # Remove the self reference
                variable.see_also.remove(variable.name)
                if i == 0:
                    continue
                else:
                    variable.description = first_variable.description
        self.reset_descriptions("")
