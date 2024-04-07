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
from re import compile, Pattern
from abc import abstractmethod
from pathlib import Path
from typing import Optional, Callable

from doc_item.doc_item import DocItem
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseItemParser:
    REMARKS_PATTERN = compile(r"^Remarks$")
    """Pattern to find the remarks section"""
    EXAMPLES_PATTERN = compile(r"^\s*Examples$")
    """Pattern to find the examples section"""
    SEE_ALSO_PATTERN = compile(r"^See Also$")
    """Pattern to find the see also section"""

    def __init__(
        self,
        version: str,
        toc: BaseTocParser,
        doc_item_class: type[DocItem],
        reader: RewindReader,
        content_start_pattern: Pattern,
        content_stop_pattern: Pattern,
        csv_file: Path,
        delimiter: str,
        page_offset: int = 0,
        on_headline: Callable[[str], None] = None,
        on_category: Callable[[str], None] = None,
        finalize_item_list: Callable[[], None] = None
    ):
        """
        Parse widgets in the Kontakt KSP text manual.

        :param version: Kontakt manual version needed to select the right parser
        :param toc: Table of content parser containing the headlines and categories
        :param doc_item_class: Class of the items to be parsed, e.g. CallbackItem
        :param reader: Reader for the already open Kontakt KSP text manual
        :param content_start_pattern: Pattern to find the content start headline
        :param content_stop_pattern: Pattern to find the content end headline
        :param on_headline: Callback for each new headline e.g. for initialization
        :param on_category: Callback for each new category e.g. for initialization
        :param finalize_item_list: Callback after the item list has been processed
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
        self.content_start_pattern: Pattern = content_start_pattern
        """Pattern to find the content start headline"""
        self.content_stop_pattern: Pattern = content_stop_pattern
        """Pattern to find the content end headline"""
        self.csv_file: Path = csv_file
        """Export *.csv file"""
        self.delimiter: str = delimiter
        """CSV delimiter, e.g. ';'"""
        self.page_offset: int = page_offset
        """Page offset when the content starts in order to skip the table of contents"""
        self.on_headline: Callable[[str], None] = on_headline
        """Optional callback for new headlines"""
        self.on_category: Callable[[str], None] = on_category
        """Optional callback for new categories"""
        self.finalize_item_list: Callable[[], None] = finalize_item_list
        """Optional callback afte the item_list has been processed"""
        self.cfg_version_dir: Path = Path(__file__).parent.parent.parent / "cfg" / self.ksp_name
        """Directory containing the configuration data"""
        self.duplicate_cnt: int = 0
        """Number of duplicate items"""
        self.item_cnt: int = 0
        """Number of found items"""
        self.item_list: list[DocItem] = []
        """Current list of found items"""
        self.all_items: dict[str, list[DocItem]] = {}
        """Dictionary where the key is the item name and the value is a list of the items inclusive duplicates"""
        self.headline: str = ""
        """Last found headline in the content"""
        self.chapter_categories: dict[str, int] = {}
        """Valid categories for the last found headline"""
        self.category: str = ""
        """Last found category"""
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
            if self.content_start_pattern.match(line):
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
        self.item_cnt = 0
        self.last_line = None
        self.doc_state = DocState.NONE
        for line in self.reader:
            # Check if this is the end of the content search
            if self.content_stop_pattern.match(line):
                if self.finalize_item_list:
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
                if self.on_headline:
                    self.on_headline(line)
                self.item_list = []
                log.info(f"- Headline: {self.headline} ({self.reader.location()})")
            # Check for categories
            # Some categories are not mentioned in the table of contents => Those are marked with "[C]"
            # Special case for callbacks: The category, e.g. on init appears twice
            # So check if the category is already set
            elif line.startswith("[C]") or (line in self.chapter_categories and line != self.category):
                if line.startswith("[C]"):
                    line = line[3:]
                self.category = line
                if self.on_category:
                    self.on_category(line)
                self.doc_state = DocState.CATEGORY
                self.item_list = []
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
            elif self.doc_state != DocState.NONE:
                # Check for items
                if new_doc_state := self.check_item(line):
                    self.doc_state = new_doc_state
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
                    if self.finalize_item_list:
                        self.finalize_item_list()
                    self.item_list = []
                    self.doc_state = DocState.CATEGORY
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_item_list in self.all_items.values():
            for cur_item in cur_item_list:
                cur_item.fix_documentation()
        log.info(f"{self.item_cnt} {self.doc_item_class.plural()} found")
        log.info(f"{self.duplicate_cnt} duplicate {self.doc_item_class.plural()}")

    @abstractmethod
    def check_item(self, line) -> Optional[DocState]:
        """
        Check if the line contains an item. If so then the item will be parsed and added to self.all_items.

        :param line: Line to check
        :return: The new documentation state or None if the line has not been processed, e.g. no item found in this line
        """

    def add_item_documentation(self, line):
        """
        Add the line to the corresponding documentation.
        The line will be added to the attribute matching the doc_state.

        :param line: Line to add
        """
        for item in self.item_list:
            # Add the line to the corresponding attribute
            text = getattr(item, self.doc_state.value)
            setattr(item, self.doc_state.value, f"{text}{line}\n")

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
                cur_item_list = self.all_items[name]
                for cur_item in cur_item_list:
                    csv_writer.writerow(cur_item.as_csv_list())
