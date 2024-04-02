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

from doc_item.widget_item import WidgetItem
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


class BaseWidgetParser:
    # Example: declare ui_table %<array-name>[num-elements] (<grid-width>, <grid-height>, <range>)
    WIDGET_PATTERN = re.compile(r"^declare\s+([a-z_]+)\s+([$%]<[a-z-]+>)(?:\[(.+)])?(?:\s+\((?:<([a-z-]+)>(?:,\s+)?)+\))?$")
    """Pattern to find a widget, e.g. on init"""
    REMARKS_PATTERN = re.compile(r"^Remarks$")
    """Pattern to find the remarks for the widget"""
    EXAMPLES_PATTERN = re.compile(r"^Examples$")
    """Pattern to find the examples for the widget"""
    SEE_ALSO_PATTERN = re.compile(r"^See Also$")
    """Pattern to find the see also for the widget"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?User Interface Widgets$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?User-defined Functions$", re.IGNORECASE)
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
        Parse widgets in the Kontakt KSP text manual.

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
        self.all_widgets: dict[str, WidgetItem] = {}
        self.duplicate_cnt: int = 0
        self.widget_cnt: int = 0
        self.widget: Optional[WidgetItem] = None
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
        Parse the text file for widgets.
        """
        log.info(f"Parse {self.reader.file} for widgets")
        self.search_content_start()
        self.scan_widgets()

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

    def scan_widgets(self):
        """
        Scan widgets.
        """
        self.reader.skip_lines = self.SKIP_LINES
        self.reader.merge_lines = self.MERGE_LINES
        self.widget = None
        self.headline: str = ""
        self.chapter_categories = {}
        self.category: str = ""
        self.widget_cnt = 0
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
            elif self.doc_state == DocState.NONE and line in self.chapter_categories:
                self.category = line
                log.info(f"   - Category: {self.category} ({self.reader.location()})")
                self.doc_state = DocState.CATEGORY
            # Check if the line contains a widget
            elif m := self.WIDGET_PATTERN.match(line):
                name = m.group(1)
                var_name = m.group(2)
                index_name = m.group(3)
                par_list: list[str] = []
                n = 4
                while m.group(n):
                    par_list.append(m.group(n))
                self.widget = self.add_widget(name, var_name, index_name, par_list)
                if self.widget:
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
            # Add the corresponding documentation for the last widget
            elif self.doc_state != DocState.NONE:
                # Add the line to the corresponding attribute
                text = getattr(self.widget, self.doc_state.value)
                setattr(self.widget, self.doc_state.value, f"{text}{line}\n")
                # 1 empty lines in the See Also section is a signal for the end of the description
                if self.doc_state == DocState.SEE_ALSO and line == "":
                    self.widget = None
                    self.doc_state = DocState.NONE
            self.last_line = line
        # Fix all descriptions, e.g. remove newlines at begin and end
        for cur_widget in self.all_widgets.values():
            cur_widget.fix_documentation()
        log.info(f"{self.widget_cnt} widgets found")
        log.info(f"{self.duplicate_cnt} duplicate widgets")

    def add_widget(self, name: str, var_name: str, index_name: str, par_list: list[str]) -> WidgetItem:
        """
        Add a widget if it does not exist.

        :param name: Name of the widget
        :param var_name: Name of the variable
        :param index_name: Name of the index_name if any
        :param par_list: List of parameter names
        :return: WidgetItem of the just created widget or None if duplicate
        """
        widget: Optional[WidgetItem] = None
        if name in self.all_widgets:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.widget_cnt += 1
            widget = WidgetItem(
                file=self.reader.file,
                page_no=self.reader.page_no,
                line_no=self.reader.line_no,
                headline=self.headline,
                category=self.category,
                name=name,
                var_name=var_name,
                index_name=index_name,
                par_list=par_list,
                description="",
                remarks="",
                examples="",
                see_also="",
                source="BUILT-IN"
            )
            self.all_widgets[name] = widget
        return widget

    def export(self):
        """
        Export the internal parsed widgets to the *.csv file.
        """
        log.info(f"Export widgets to {self.csv_file}")
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            # Write the headline
            csv_writer.writerow(WidgetItem.header())
            # Sort the list for identifier rules
            # for name in natsorted(self.all_widgets.keys()):
            for name in self.all_widgets.keys():
                cur_widget = self.all_widgets[name]
                csv_writer.writerow(cur_widget.as_csv_list())