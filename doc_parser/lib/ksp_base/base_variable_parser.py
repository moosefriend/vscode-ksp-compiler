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
    VAR_PATTERN = re.compile(r"^(?:•\s*)?([$%!~@?][A-Z]+[A-Z_0-9]*)(\[<(.+)>])?(?:\s+(\(.+\)))?$")
    """Pattern to find a variable or constant, e.g. $VAR1, •$VAR1 (comment)"""
    VAR_RANGE_PATTERN = re.compile(r"^(?:•\s*)?([$%!~@?][A-Z_]+)(\d+)\s+\.\.\.\s+([$%!~@?][A-Z_]+)(\d+)$")
    """Pattern to find variable ranges, e.g. $MARK_1 ... $MARK_28"""

    @staticmethod
    def content_start_pattern():
        return re.compile(r"^(\d+\.\s+)?Built-in Variables and Constants$", re.IGNORECASE)

    @staticmethod
    def content_stop_pattern():
        return re.compile(r"^(\d+\.\s+)?Advanced Concepts$", re.IGNORECASE)

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
        super().__init__(version, toc, VariableItem, reader, csv_file, delimiter, page_offset)
        self.comment: str = ""

    def check_item(self, line) -> bool:
        line_processed: bool = False
        # TODO: Multiple variables in the table header sharing the same documentation, e.g. line 9645.
        #    The documentation should be added to all those variables.
        # TODO: Variable in the table header. In the table body description follows with and item list of constants,
        #    e.g. line 9753
        #    The constants should have a reference to the variable incl. its description.
        # TODO: Table header with a description in the table body followed by a list of variables, e.g. line 8995.
        #    The Table header should only by the first line, and the description should be assigned to all variables
        #    in the list.
        # Check if the line contains a variable or constant
        if m := self.VAR_PATTERN.match(line):
            name = m.group(1)
            parameter = m.group(3)
            self.comment = m.group(4)
            variable = self.add_variable(name, parameter)
            if variable:
                self.item_list = [variable]
            else:
                self.item_list = []
            line_processed = True
        # Check if the line contains a variable range, e.g. $MARK1 ... $MARK28
        elif m := self.VAR_RANGE_PATTERN.match(line):
            base_name = m.group(1)
            start_index = int(m.group(2))
            end_index = int(m.group(4))
            self.item_list = []
            for i in range(start_index, end_index + 1):
                name = f"{base_name}{i}"
                variable = self.add_variable(name, "")
                if variable:
                    self.item_list.append(variable)
            line_processed = True
        # Check for item list headlines
        elif line.endswith(":"):
            # TODO: When the line also contains a "." then the item list headline shall only be after the "."
            #    The text before the "." should be added to the description of the previous variable.
            # Remove the colon from the end
            self.item_list_headline = line[:-1]
            log.info(f"   - Item List Headline: {self.item_list_headline} ({self.reader.location()})")
            line_processed = True
        # Check for table headline or description block before the variable(s)
        elif self.doc_state == DocState.CATEGORY and line != "":
            self.header_description += line + "\n"
            log.info(f"   - Header Description: {line} ({self.reader.location()})")
            line_processed = True
        return line_processed

    def add_item_documentation(self, line):
        # Add the documentation for the last variable or constant
        for variable in self.item_list:
            variable.description += line + "\n"

    def add_variable(self, name: str, parameter) -> VariableItem:
        """
        Add a variable if it is not in the ignore list or already exists.

        :param name: Name of the variable
        :param parameter: Parameter name if it is e.g. an array
        :return: VariableItem of the just created variable or None if duplicate or ignored
        """
        variable: Optional[VariableItem] = None
        if name in self.all_items:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
            variable = VariableItem(
                file=self.reader.file,
                page_no=self.reader.page_no,
                line_no=self.reader.line_no,
                headline=self.headline,
                category=self.category,
                name=name,
                parameter=parameter,
                description="",
                header_description=self.header_description,
                item_list_headline=self.item_list_headline,
                comment=self.comment,
                source="BUILT-IN"
            )
            self.all_items[name] = variable
        return variable
