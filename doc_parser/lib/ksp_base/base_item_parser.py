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
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from doc_item.doc_item import DocItem
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseItemParser:
    REMARKS_PATTERN = re.compile(r"^Remarks$")
    """Pattern to find the remarks section"""
    EXAMPLES_PATTERN = re.compile(r"^\s*Examples$")
    """Pattern to find the examples section"""
    SEE_ALSO_PATTERN = re.compile(r"^See Also$")
    """Pattern to find the see also section"""

    @staticmethod
    @abstractmethod
    def content_start_pattern() -> re.Pattern:
        """
        :return: Pattern to find the start headline for scanning the content
        """

    @staticmethod
    @abstractmethod
    def content_stop_pattern() -> re.Pattern:
        """
        :return: Pattern to find the stop headline for scanning the content
        """

    @abstractmethod
    def check_item(self, line) -> bool:
        """
        Check if the line contains an item. If so then the item will be parsed and added to self.all_items.
        :param line: Line to check
        :return: True if the line contains an item, False otherwise.
        """

    @abstractmethod
    def add_item_documentation(self, line):
        """
        Add the line to the corresponding item documentation.
        :param line: Line to add to the documentation
        """

    def __init__(self, version: str, toc: BaseTocParser, doc_item_class: type[DocItem], reader: RewindReader, csv_file: Path,
                 delimiter: str, page_offset: int = 0):
        """
        Parse widgets in the Kontakt KSP text manual.

        :param version: Kontakt manual version needed to select the right parser
        :param toc: Table of content parser containing the headlines and categories
        :param doc_item_class: Class of the items to be parsed, e.g. CallbackItem
        :param reader: Reader for the already open Kontakt KSP text manual
        :param csv_file: Comma separated file to export the parsed data
        :param delimiter: CSV delimiter for the export file
        :param page_offset: The page number is decreased by this offset, e.g. if the page numbers start again with 1
            after the table of contents
        """
        self.version: str = version
        """Kontakt version"""
        self.ksp_name: str = f"ksp_{version.replace('.', '_')}"
        """Directory name to be used for finding the parser"""
        self.toc: BaseTocParser = toc
        """Parsed table of contents"""
        self.doc_item_class: type[DocItem] = doc_item_class
        """Class of the items to be parsed, e.g. CallbackItem"""
        self.reader: RewindReader = reader
        """File reader to be used for reading lines from the converted text file"""
        self.csv_file: Path = csv_file
        """Export *.csv file"""
        self.delimiter: str = delimiter
        """CSV delimiter, e.g. ';'"""
        self.page_offset: int = page_offset
        """Page offset when the content starts in order to skip the table of contents"""
        self.cfg_version_dir: Path = Path(__file__).parent.parent.parent / "cfg" / self.ksp_name
        """Directory containing the configuration data"""
        self.duplicate_cnt: int = 0
        """Number of duplicate items"""
        self.item_cnt: int = 0
        """Number of found items"""
        self.item_list: list[DocItem] = []
        """Current list of found items"""
        self.all_items: dict[str, DocItem] = {}
        """Dictionary where the key is the item name and the value it the corresponding item"""
        self.headline: str = ""
        """Last found headline in the content"""
        self.chapter_categories: dict[str, int] = {}
        """Valid categories for the last found headline"""
        self.category: str = ""
        """Last found category"""
        self.header_description: str = ""
        """Table header description"""
        self.item_list_headline: str = ""
        """Item list headline"""
        self.last_line: Optional[str] = ""
        """Previous line content"""
        self.remarks: str = ""
        """Remarks found for the current item"""
        self.examples: str = ""
        """Examples found for the current item"""
        self.see_also: str = ""
        """See also lines found for the current item"""
        self.doc_state: DocState = DocState.NONE
        """Internal parser state for current item"""

    def parse(self):
        """
        Parse the text file for widgets.
        """
        log.info(f"Parse {self.reader.file} for {self.doc_item_class.plural()}")
        self.search_content_start()
        self.scan_items()

    def search_content_start(self):
        """
        Find the line where the content will start.
        """
        for line in self.reader:
            # Search for the content
            if self.content_start_pattern().match(line):
                log.info(f"Found Content Start ({self.reader.location()})")
                self.reader.rewind()
                break

    def scan_items(self):
        """
        Scan items.
        """
        self.item_list = []
        self.headline = ""
        self.chapter_categories = {}
        self.category = ""
        self.header_description = ""
        self.item_list_headline = ""
        self.item_cnt = 0
        self.last_line = None
        self.doc_state = DocState.NONE
        for line in self.reader:
            # Check if this is the end of the content search
            if self.content_stop_pattern().match(line):
                self.finalize_item_list()
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
                self.header_description = ""
                self.item_list_headline = ""
                log.info(f"- Headline: {self.headline} ({self.reader.location()})")
            # Check for categories
            elif self.doc_state == DocState.NONE and line in self.chapter_categories:
                self.category = line
                self.header_description = ""
                self.item_list_headline = ""
                self.doc_state = DocState.CATEGORY
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
            elif self.doc_state != DocState.NONE:
                # Check for items
                if self.check_item(line):
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
                # Add line to corresponding item documentation
                else:
                    self.add_item_documentation(line)
                # 1 empty lines in the See Also section is a signal for the end of the description ot
                # 2 empty lines are a signal for the end of the description
                if line == "" and (self.doc_state == DocState.SEE_ALSO or self.last_line == ""):
                    self.finalize_item_list()
                    self.item_list = []
                    self.header_description = ""
                    self.item_list_headline = ""
                    self.doc_state = DocState.CATEGORY
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_item in self.all_items.values():
            cur_item.fix_documentation()
        log.info(f"{self.item_cnt} {self.doc_item_class.plural()} found")
        log.info(f"{self.duplicate_cnt} duplicate {self.doc_item_class.plural()}")

    def export(self):
        """
        Export the internal parsed items to the *.csv file.
        """
        log.info(f"Export {self.doc_item_class.plural()} to {self.csv_file}")
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(self.doc_item_class.csv_header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_items.keys()):
            for name in self.all_items.keys():
                cur_item = self.all_items[name]
                csv_writer.writerow(cur_item.as_csv_list())

    def finalize_item_list(self):
        """
        Once 2 empty lines or a new category is found then this method is called.
        It can be overridden in subclasses.
        """
        pass
