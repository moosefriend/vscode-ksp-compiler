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
import logging
import re
from pathlib import Path
from typing import Optional

from doc_item.variable_item import VariableItem
from ksp_base.base_toc_parser import BaseTocParser
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseVariableParser:
    VAR_PATTERN = re.compile(r"^(?:•\s*)?([$%!~@?][A-Z]+[A-Z_0-9]*)(\[<(.+)>]+)?(?:\s+(\(.+\)))?$")
    """Pattern to find a variable or constant, e.g. $VAR1, •$VAR1 (comment)"""
    VAR_RANGE_PATTERN = re.compile(r"^(?:•\s*)?([$%!~@?][A-Z_]+)(\d+)\s+\.\.\.\s+([$%!~@?][A-Z_]+)(\d+)$")
    """Pattern to find variable ranges, e.g. $MARK_1 ... $MARK_28"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Built-in Variables and Constants$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Advanced Concepts$", re.IGNORECASE)
    """Pattern to find the end headline for scanning the content"""
    SKIP_LINES = {
        # <start line number in the text file>: <end line number in the text file>
    }
    """Dictionary of lines to be skipped"""
    MERGE_LINES = {
        # <line number in the text file>
    }
    """Set of lines to be merged, because they are wrapped and therefore not correctly identified"""
    WRAPPED_CELLS = {
        # <line number in the text file>: (<left cell part in the first line>, <left cell part in the second line>)
    }
    """Dictionary of wrapped table cells to be merged"""

    def __init__(self, version: str, toc: BaseTocParser, reader: RewindReader, csv_file: Path, delimiter: str, page_offset: int = 0):
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
        self.version: str = version
        self.ksp_name: str = f"ksp_{version.replace('.', '_')}"
        self.toc: BaseTocParser = toc
        self.reader: RewindReader = reader
        self.csv_file: Path = csv_file
        self.delimiter: str = delimiter
        self.page_offset: int = page_offset
        self.cfg_version_dir: Path = Path(__file__).parent.parent.parent / "cfg" / self.ksp_name
        self.all_variables: dict[str, VariableItem] = {}
        self.duplicate_cnt: int = 0
        self.variable_cnt: int = 0
        self.variable_list: list[VariableItem] = []
        self.headline: str = ""
        self.chapter_categories: dict[str, int] = {}
        self.category: str = ""
        self.sub_category: str = ""
        self.last_line: Optional[str] = ""
        self.header_description: str = ""
        self.item_list_headline: str = ""
        self.comment: str = ""

    def parse(self):
        """
        Parse the text file for variables.
        """
        log.info(f"Parse {self.reader.file} for variables and constants")
        self.search_content_start()
        self.scan_variables()

    def search_content_start(self):
        """
        Find the line where the content will start.
        """
        for line in self.reader:
            # Search for the content
            if self.CONTENT_START_PATTERN.match(line):
                log.info(f"Found Content Start ({self.reader.location()})")
                self.reader.rewind()
                break

    def scan_variables(self):
        """
        Scan variables and constants.
        """
        self.reader.skip_lines = self.SKIP_LINES
        self.reader.merge_lines = self.MERGE_LINES
        self.variable_list = []
        self.headline: str = ""
        self.chapter_categories = {}
        self.category: str = ""
        self.duplicate_cnt = 0
        self.variable_cnt = 0
        self.last_line = None
        self.header_description = ""
        self.item_list_headline = ""
        for line in self.reader:
            # TODO: Multiple variables in the table header sharing the same documentation, e.g. line 9645.
            #    The documentation should be added to all those variables.
            # TODO: Variable in the table header. In the table body description follows with and item list of constants,
            #    e.g. line 9753
            #    The constants should have a reference to the variable incl. its description.
            # TODO: Table header with a description in the table body followed by a list of variables, e.g. line 8995.
            #    The Table header should only by the first line, and the description should be assigned to all variables
            #    in the list.

            # Check if this is the end of the content search
            if self.CONTENT_STOP_PATTERN.match(line):
                self.reader.rewind()
                break
            # Check for headlines
            elif line in self.toc.all_headlines:
                self.headline = line
                if self.headline in self.toc.all_categories:
                    self.chapter_categories = self.toc.all_categories[self.headline]
                else:
                    self.chapter_categories = {}
                self.category = ""
                log.info(f"- Headline: {self.headline} ({self.reader.location()})")
                if self.header_description:
                    log.info(f"   - Header Description reset ({self.reader.location()})")
                self.header_description = ""
                if self.item_list_headline:
                    log.info(f"   - Item List Headline reset ({self.reader.location()})")
                self.item_list_headline = ""
            # Check for categories
            elif line in self.chapter_categories:
                self.category = line
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
                if self.header_description:
                    log.info(f"   - Header Description reset ({self.reader.location()})")
                self.header_description = ""
                if self.item_list_headline:
                    log.info(f"   - Item List Headline reset ({self.reader.location()})")
                self.item_list_headline = ""
            # Check if the line contains a variable or constant
            elif m := self.VAR_PATTERN.match(line):
                name = m.group(1)
                parameter = m.group(3)
                self.comment = m.group(4)
                variable = self.add_variable(name, parameter)
                if variable:
                    self.variable_list = [variable]
                else:
                    self.variable_list = []
            # Check if the line contains a variable range, e.g. $MARK1 ... $MARK28
            elif m := self.VAR_RANGE_PATTERN.match(line):
                base_name = m.group(1)
                start_index = int(m.group(2))
                end_index = int(m.group(4))
                self.variable_list = []
                for i in range(start_index, end_index + 1):
                    name = f"{base_name}{i}"
                    variable = self.add_variable(name, "")
                    if variable:
                        self.variable_list.append(variable)
            # Check for item list headlines
            elif line.endswith(":"):
                # TODO: When the line also contains a "." then the item list headline shall only be after the "."
                #    The text before the "." should be added to the description of the previous variable.
                # Remove the colon from the end
                self.item_list_headline = line[:-1]
                log.info(f"   - Item List Headline: {self.item_list_headline} ({self.reader.location()})")
            # Add the documentation for the last variable or constant
            elif self.variable_list:
                for variable in self.variable_list:
                    variable.description += line + "\n"
                # 2 empty lines are a signal for the end of the description
                if line == "" and self.last_line == "":
                    self.variable_list = []
                    if self.header_description:
                        log.info(f"   - Header Description reset ({self.reader.location()})")
                    self.header_description = ""
                    if self.item_list_headline:
                        log.info(f"   - Item List Headline reset ({self.reader.location()})")
                    self.item_list_headline = ""
            # Check for table headline or description block before the variable(s)
            elif line != "":
                self.header_description += line + "\n"
                log.info(f"   - Header Description: {line} ({self.reader.location()})")
                if self.item_list_headline:
                    log.info(f"   - Item List Headline reset ({self.reader.location()})")
                self.item_list_headline = ""
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_variable in self.all_variables.values():
            cur_variable.fix_documentation()
        log.info(f"{self.variable_cnt} variables found")
        log.info(f"{self.duplicate_cnt} duplicate variables")

    def add_variable(self, name: str, parameter) -> VariableItem:
        """
        Add a variable if it is not in the ignore list or already exists.

        :param name: Name of the variable
        :param parameter: Parameter name if it is e.g. an array
        :return: VariableItem of the just created variable or None if duplicate or ignored
        """
        variable: Optional[VariableItem] = None
        if name in self.all_variables:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.variable_cnt += 1
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
            self.all_variables[name] = variable
        return variable

    def export(self):
        """
        Export the internal parsed variables to the *.csv file.
        """
        log.info(f"Export variables and constants to {self.csv_file}")
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(VariableItem.header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_variables.keys()):
            for name in self.all_variables.keys():
                cur_var = self.all_variables[name]
                csv_writer.writerow(cur_var.as_list())
