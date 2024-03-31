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

from doc_item.callback_item import CallbackItem
from ksp_base.base_toc_parser import BaseTocParser
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class DocState(Enum):
    NONE = ""
    CATEGORY = "category"
    DESCRIPTION = "description"
    REMARKS = "remarks"
    EXAMPLES = "examples"
    SEE_ALSO = "see_also"


class BaseCallbackParser:
    CALLBACK_PATTERN = re.compile(r"^on\s+([a-z_]+)(?:/([a-z_]+))?(?:\s+\(<([a-z-]+)>\))?$")
    """Pattern to find a callback, e.g. on init"""
    REMARKS_PATTERN = re.compile(r"^Remarks$")
    """Pattern to find the remarks for the callback"""
    EXAMPLES_PATTERN = re.compile(r"^\s*Examples$")
    """Pattern to find the examples for the callback"""
    SEE_ALSO_PATTERN = re.compile(r"^See Also$")
    """Pattern to find the see also for the callback"""
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
        Parse callbacks in the Kontakt KSP text manual.

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
        self.all_callbacks: dict[str, CallbackItem] = {}
        self.duplicate_cnt: int = 0
        self.callback_cnt: int = 0
        self.callback_list: list[CallbackItem] = []
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
        Parse the text file for callbacks.
        """
        log.info(f"Parse {self.reader.file} for callbacks")
        self.search_content_start()
        self.scan_callbacks()

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

    def scan_callbacks(self):
        """
        Scan callbacks.
        """
        self.reader.skip_lines = self.SKIP_LINES
        self.reader.merge_lines = self.MERGE_LINES
        self.callback_list = []
        self.headline: str = ""
        self.chapter_categories = {}
        self.category: str = ""
        self.callback_cnt = 0
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
            # A new callback start with the callback name, an empty line and again the callback
            elif self.doc_state == DocState.NONE and line in self.chapter_categories:
                self.category = line
                self.doc_state = DocState.CATEGORY
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
            # Search for the actual callback
            elif self.doc_state == DocState.CATEGORY:
                if line:
                    if line.startswith(self.category) and (m := self.CALLBACK_PATTERN.match(line)):
                        name_list = [m.group(1)]
                        # Check if there is a list of callbacks e.g. rpn/nrpn
                        if m.group(2):
                            name_list.append(m.group(2))
                        # Check if there is a parameter
                        parameter = m.group(3)
                        self.callback_list = []
                        for name in name_list:
                            callback = self.add_callback(name, parameter)
                            self.callback_list.append(callback)
                        self.doc_state = DocState.DESCRIPTION
                    else:
                        log.error(f"Can't find the expected callback {self.category}, but got {line}")
            # Check for remarks
            elif self.doc_state and self.REMARKS_PATTERN.match(line):
                self.doc_state = DocState.REMARKS
            # Check for examples
            elif self.doc_state and self.EXAMPLES_PATTERN.match(line):
                self.doc_state = DocState.EXAMPLES
            # Check for see also
            elif self.doc_state and self.SEE_ALSO_PATTERN.match(line):
                self.doc_state = DocState.SEE_ALSO
            # Add the corresponding documentation for the last callback
            elif self.doc_state:
                for callback in self.callback_list:
                    # Add the line to the corresponding attribute
                    text = getattr(callback, self.doc_state.value)
                    setattr(callback, self.doc_state.value, f"{text}{line}\n")
                # 1 empty lines in the See Also section is a signal for the end of the description
                if self.doc_state == DocState.SEE_ALSO and line == "":
                    self.callback_list = []
                    self.doc_state = DocState.NONE
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_callback in self.all_callbacks.values():
            cur_callback.fix_documentation()
        log.info(f"{self.callback_cnt} callbacks found")
        log.info(f"{self.duplicate_cnt} duplicate callbacks")

    def add_callback(self, name: str, parameter: str) -> CallbackItem:
        """
        Add a callback if it does not exist.

        :param name: Name of the callback
        :param parameter: Optional parameter for the callback
        :return: CallbackItem of the just created callback or None if duplicate
        """
        callback: Optional[CallbackItem] = None
        if name in self.all_callbacks:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.callback_cnt += 1
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
            self.all_callbacks[name] = callback
        return callback

    def export(self):
        """
        Export the internal parsed callbacks to the *.csv file.
        """
        log.info(f"Export callbacks to {self.csv_file}")
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(CallbackItem.header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_callbacks.keys()):
            for name in self.all_callbacks.keys():
                cur_callback = self.all_callbacks[name]
                csv_writer.writerow(cur_callback.as_list())