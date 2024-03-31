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
from enum import Enum
from pathlib import Path
from typing import Optional

from doc_item.function_item import FunctionItem
from ksp_base.base_toc_parser import BaseTocParser
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class DocState(Enum):
    NONE = ""
    DESCRIPTION = "description"
    REMARKS = "remarks"
    EXAMPLES = "examples"
    SEE_ALSO = "see_also"


class BaseFunctionParser:
    # TODO: Implement BaseFunctionParser
    FUNCTION_PATTERN = re.compile(r"^on\s+([a-z_]+)(?:/([a-z_]+))?$")
    """Pattern to find a function, e.g. on init"""
    REMARKS_PATTERN = re.compile(r"^Remarks$")
    """Pattern to find the remarks for the function"""
    EXAMPLES_PATTERN = re.compile(r"^Examples$")
    """Pattern to find the examples for the function"""
    SEE_ALSO_PATTERN = re.compile(r"^See Also$")
    """Pattern to find the see also for the function"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Callbacks$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Variables$", re.IGNORECASE)
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
        Parse functions in the Kontakt KSP text manual.

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
        self.all_functions: dict[str, FunctionItem] = {}
        self.duplicate_cnt: int = 0
        self.function_cnt: int = 0
        self.function_list: list[FunctionItem] = []
        self.headline: str = ""
        self.chapter_categories: dict[str, int] = {}
        self.category: str = ""
        self.sub_category: str = ""
        self.last_line: Optional[str] = ""
        self.remarks: str = ""
        self.examples: str = ""
        self.see_also: str = ""
        self.doc_state: DocState = DocState.NONE

    def parse(self):
        """
        Parse the text file for functions.
        """
        log.info(f"Parse {self.reader.file} for functions")
        self.search_content_start()
        self.scan_functions()

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

    def scan_functions(self):
        """
        Scan functions.
        """
        self.reader.skip_lines = self.SKIP_LINES
        self.reader.merge_lines = self.MERGE_LINES
        self.function_list = []
        self.headline: str = ""
        self.chapter_categories = {}
        self.category: str = ""
        self.function_cnt = 0
        self.last_line = None
        self.doc_state = DocState.NONE
        for line in self.reader:
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
            # Check for categories
            # Be aware that the function itself is identical to the category (the line appears twice)
            elif line != self.category and line in self.chapter_categories:
                self.category = line
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
            # Check if the line contains a function
            elif m := self.FUNCTION_PATTERN.match(line):
                name_list = [m.group(1)]
                if len(m.groups()) > 1:
                    name_list.append(m.group(2))
                self.function_list = []
                for name in name_list:
                    function = self.add_function(name)
                    if function:
                        self.function_list.append(function)
                if self.function_list:
                    self.doc_state = DocState.DESCRIPTION
            # Check for remarks
            elif self.REMARKS_PATTERN.match(line):
                self.doc_state = DocState.REMARKS
            # Check for examples
            elif self.EXAMPLES_PATTERN.match(line):
                self.doc_state = DocState.EXAMPLES
            # Check for see also
            elif self.SEE_ALSO_PATTERN.match(line):
                self.doc_state = DocState.SEE_ALSO
            # Add the corresponding documentation for the last function
            elif self.doc_state:
                for function in self.function_list:
                    # Add the line to the corresponding attribute
                    text = getattr(function, self.doc_state.value)
                    setattr(function, self.doc_state.value, f"{text}{line}\n")
                # 2 empty lines are a signal for the end of the description
                if line == "" and self.last_line == "":
                    self.function_list = []
                    self.doc_state = DocState.NONE
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_function in self.all_functions.values():
            cur_function.fix_documentation()
        log.info(f"{self.function_cnt} functions found")
        log.info(f"{self.duplicate_cnt} duplicate functions")

    def add_function(self, name: str) -> FunctionItem:
        """
        Add a function if it does not exist.

        :param name: Name of the function
        :return: FunctionItem of the just created function or None if duplicate
        """
        function: Optional[FunctionItem] = None
        if name in self.all_functions:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.function_cnt += 1
            function = FunctionItem(
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
            self.all_functions[name] = function
        return function

    def export(self):
        """
        Export the internal parsed functions to the *.csv file.
        """
        log.info(f"Export functions to {self.csv_file}")
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(FunctionItem.header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_functions.keys()):
            for name in self.all_functions.keys():
                cur_function = self.all_functions[name]
                csv_writer.writerow(cur_function.as_list())