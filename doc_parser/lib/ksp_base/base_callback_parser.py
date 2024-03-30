#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).

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
    DESCRIPTION = "description"
    REMARKS = "remarks"
    EXAMPLES = "examples"
    SEE_ALSO = "see_also"


class BaseCallbackParser:
    CALLBACK_PATTERN = re.compile(r"^on\s+([a-z_]+)(?:/([a-z_]+))?$")
    """Pattern to find a callback, e.g. on init"""
    REMARKS_PATTERN = re.compile(r"^Remarks$")
    """Pattern to find the remarks for the callback"""
    EXAMPLES_PATTERN = re.compile(r"^Examples$")
    """Pattern to find the examples for the callback"""
    SEE_ALSO_PATTERN = re.compile(r"^See Also$")
    """Pattern to find the see also for the callback"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?Callbacks$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?Variables$", re.IGNORECASE)
    """Pattern to find the end headline for scanning the content"""
    MERGE_LINES = {
        # <start line>: <character used to merge with the next line>
    }
    """List of lines to be merged, because they are wrapped and therefore not correctly identified"""
    WRAPPED_CELLS = {
        # <line no in the text file>: (<left cell part in the first line>, <left cell part in the second line>)
    }
    """List of wrapped table cells to be merged"""

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
            # Be aware that the callback itself is identical to the category (the line appears twice)
            elif line != self.category and line in self.chapter_categories:
                self.category = line
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
            # Check if the line contains a callback
            elif m := self.CALLBACK_PATTERN.match(line):
                name_list = [m.group(1)]
                if len(m.groups()) > 1:
                    name_list.append(m.group(2))
                self.callback_list = []
                for name in name_list:
                    callback = self.add_callback(name)
                    if callback:
                        self.callback_list.append(callback)
                if self.callback_list:
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
            # Add the corresponding documentation for the last callback
            elif self.doc_state:
                for callback in self.callback_list:
                    # Add the line to the corresponding attribute
                    text = getattr(callback, self.doc_state.value)
                    setattr(callback, self.doc_state.value, f"{text}{line}\n")
                # 2 empty lines are a signal for the end of the description
                if line == "" and self.last_line == "":
                    self.callback_list = []
                    self.doc_state = DocState.NONE
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_callback in self.all_callbacks.values():
            cur_callback.fix_documentation()
        log.info(f"{self.callback_cnt} callbacks found")
        log.info(f"{self.duplicate_cnt} duplicate callbacks")

    def add_callback(self, name: str) -> CallbackItem:
        """
        Add a callback if it does not exist.

        :param name: Name of the callback
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
