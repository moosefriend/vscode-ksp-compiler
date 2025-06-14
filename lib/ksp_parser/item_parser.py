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
from re import compile
from abc import abstractmethod
from typing import Optional, Callable

from doc_item.doc_item import DocItem
from ksp_parser.content_pattern import ContentPattern
from ksp_parser.toc_parser import TocParser
from config.constants import DocState
from config.system_config import SystemConfig
from util.format_util import log_step
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class ItemParser:
    REMARKS_PATTERN = compile(r"^Remarks$")
    """Pattern to find the remarks section"""
    EXAMPLES_PATTERN = compile(r"^\s*Examples?$")
    """Pattern to find the examples section"""
    SEE_ALSO_PATTERN = compile(r"^See Also$", re.IGNORECASE)
    """Pattern to find the see also section"""

    def __init__(
            self,
            doc_item_class: type[DocItem],
            content_patterns: list[ContentPattern],
            csv_file: Path,
            on_headline: Callable[[str], None] = None,
            on_category: Callable[[str], None] = None,
            finalize_item_list: Callable[[], None] = None
    ):
        """
        Base parser for documentation items in the Kontakt KSP text manual.

        :param doc_item_class: Class of the items to be parsed, e.g. CallbackItem
        :param content_patterns: List of ContentPattern objects, where each object contains the start and stop patterns
        :param csv_file: Path of the *.csv export file
        :param on_headline: Callback for each new headline e.g. for initialization
        :param on_category: Callback for each new category e.g. for initialization
        :param finalize_item_list: Callback after the item list has been processed
        """
        self.doc_item_class: type[DocItem] = doc_item_class
        """Class of the items to be parsed, e.g. CallbackItem"""
        self.content_patterns: list[ContentPattern] = content_patterns
        """List of ContentPattern objects, where each object contains the start and stop patterns"""
        self.csv_file: Path = csv_file
        """Path of the *.csv export file"""
        self.on_headline: Callable[[str], None] = on_headline
        """Optional callback for new headlines"""
        self.on_category: Callable[[str], None] = on_category
        """Optional callback for new categories"""
        self.finalize_item_list: Callable[[], None] = finalize_item_list
        """Optional callback after the item_list has been processed"""
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
        self.skip_parsed_line: bool = False
        """True if the current line shall not be included in the parsed text"""
        self.reader: RewindReader = SystemConfig().reader
        """RewindReader to be used to read from the *.txt file"""
        self.toc: TocParser = SystemConfig().toc
        """Object containing the table of contents (TOC)"""
        self.content_pattern: Optional[ContentPattern] = None
        """Current content pattern (if any)"""

    def parse(self):
        """
        Parse the text file for widgets.
        """
        log_step(f"Parse {self.doc_item_class.plural()} in {self.reader.file}")
        self.reader.reset()
        while self.search_content_start():
            self.scan_items()
        log.info(f"{self.item_cnt} {self.doc_item_class.plural()} found")
        log.info(f"{self.duplicate_cnt} duplicate {self.doc_item_class.plural()}")

    def search_content_start(self) -> ContentPattern:
        """
        Find the line where the content will start.

        :return: ContentPattern or None if not content was found
        """
        for line in self.reader:
            # Search for the content
            for content_pattern in self.content_patterns:
                if content_pattern.start(line):
                    log.debug(f"Found Content Start ({self.reader.location()})")
                    self.reader.rewind()
                    self.content_pattern = content_pattern
                    break
            if self.content_pattern:
                break
        return self.content_pattern

    def scan_items(self):
        """
        Scan items.
        """
        self.item_list: list[DocItem] = []
        self.headline = ""
        self.chapter_categories = {}
        self.category = ""
        self.item_cnt = 0
        self.last_line = None
        self.doc_state = DocState.NONE
        for line in self.reader:
            # Check if this is the end of the content search
            if self.content_pattern.stop(line):
                if self.finalize_item_list:
                    self.finalize_item_list()
                self.reader.rewind()
                self.content_pattern = None
                break
            # Check for headlines
            elif line in self.toc.all_headlines:
                if self.finalize_item_list:
                    self.finalize_item_list()
                self.headline = line
                if self.headline in self.toc.all_categories:
                    self.chapter_categories = self.toc.all_categories[self.headline]
                else:
                    self.chapter_categories = {}
                self.category = ""
                if self.on_headline:
                    self.on_headline(line)
                self.item_list = []
                log.debug(f"- Headline: {self.headline} ({self.reader.location()})")
                self.doc_state = DocState.NONE
            # Check for categories
            # Some categories are not mentioned in the table of contents => Those are marked with "[C]"
            # Sometimes in the "See Also" section there is also a reference to another category
            elif self.doc_state != DocState.SEE_ALSO and self.check_category(line):
                if self.finalize_item_list:
                    self.finalize_item_list()
                if line.startswith("[C]"):
                    line = line[3:]
                self.category = line
                if self.on_category:
                    self.on_category(line)
                self.doc_state = DocState.CATEGORY
                self.item_list = []
                log.debug(f"   - ItemType: {self.category} ({self.reader.location()})")
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
                elif self.doc_state != DocState.CATEGORY:
                    self.add_item_documentation(line)
                if self.item_list and not self.skip_parsed_line:
                    self.item_list[-1].parsed_text += f"{line}\n"
                self.skip_parsed_line = False
                # 1 empty lines in the See Also section is a signal for the end of the description or
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

    def check_category(self, line) -> bool:
        """
        Check if the line contains a category.

        :param line: Line to check
        :return: True if the line contains a category
        """
        is_category = line.startswith("[C]") or line in self.chapter_categories
        return is_category

    @abstractmethod
    def check_item(self, line) -> Optional[DocState]:
        """
        Check if the line contains an item. If so then the item will be parsed and added to ``self.all_items``.

        :param line: Line to check
        :return: The new documentation state or None if the line has not been processed, e.g. no item found in this line
        """

    def add_item(self, doc_item: DocItem):
        """
        Add the item to the list of items.

        :param doc_item: Item to add
        """
        name = doc_item.name
        if name in self.all_items:
            log.debug(f"      - Duplicate {name} ({self.reader.location()})")
            self.item_list = self.all_items[name]
            self.duplicate_cnt += 1
        else:
            log.debug(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
            self.item_list = []
            self.all_items[name] = self.item_list
        self.item_list.append(doc_item)

    def add_item_documentation(self, line):
        """
        Add the line to the corresponding documentation.
        The line will be added to the attribute matching the doc_state.

        :param line: Line to add
        """
        if self.item_list:
            item = self.item_list[-1]
            # Add the line to the corresponding attribute
            text = getattr(item, self.doc_state.value)
            setattr(item, self.doc_state.value, f"{text}{line}\n")

    def export(self):
        """
        Export the internal parsed items to the *.csv file.
        """
        log_step(f"Export {self.doc_item_class.plural()} to {self.csv_file}")
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=SystemConfig().delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(self.doc_item_class.csv_header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_items.keys()):
            for name in self.all_items.keys():
                cur_item_list = self.all_items[name]
                for cur_item in cur_item_list:
                    csv_writer.writerow(cur_item.as_csv_list())

    def dump(self, dump_text: bool = True):
        """
        Print the internal parsed data.

        :param dump_text: If True then it prints also the original parsed text
        """
        log_step(f"Dump {self.doc_item_class.plural()}")
        for name, item_list in self.all_items.items():
            log.info(f"{'-' * 30} {name} {'-' * 30}")
            for i, item in enumerate(item_list):
                if i > 0:
                    log.info(f"{'-' * 30} {name} (DUPLICATE {i}) {'-' * 30}")
                log.info(f"Page {item.page_no}, File \"{item.file}\", line {item.line_no}")
                if dump_text:
                    log.info(f"{'*' * 10} Parsed Text Start {'*' * 10}")
                    for line in item.parsed_text.splitlines():
                        log.info(line)
                    log.info(f"{'*' * 10} Parsed Text End {'*' * 10}")
                for title in ("Headline", "ItemType", "Block Headline", "Item List Headline", "Source", "Name",
                              "Parameter", "Variable Name", "Index Name", "Comment"):
                    attribute = title.replace(" ", "_").lower()
                    if attribute in item.__dict__ and (value := item.__dict__[attribute]):
                        log.info(f"{title}: {value}")
                if "parameter_list" in item.__dict__ and len(item.__dict__["parameter_list"]) > 0:
                    log.info(f"Parameters: {','.join(item.__dict__['parameter_list'])}")
                for title in ("Description", "Remarks", "Examples", "See Also"):
                    attribute = title.replace(" ", "_").lower()
                    if attribute in item.__dict__ and (value := item.__dict__[attribute]):
                        log.info(f"{'>' * 10} {title} {'<' * 10}")
                        for line in value.splitlines():
                            log.info(line)
