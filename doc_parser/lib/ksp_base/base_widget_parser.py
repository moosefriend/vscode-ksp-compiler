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

from doc_item.widget_item import WidgetItem
from ksp_base.base_item_parser import BaseItemParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.constants import DocState
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseWidgetParser(BaseItemParser):
    # Example: declare ui_table %<array-name>[num-elements] (<grid-width>, <grid-height>, <range>)
    WIDGET_PATTERN = re.compile(r"^declare\s+([a-z_]+)\s+([$%]<[a-z-]+>)(?:\[(.+)])?(?:\s+\((?:<([a-z-]+)>(?:,\s+)?)+\))?$")
    """Pattern to find a widget, e.g. on init"""
    CONTENT_START_PATTERN = re.compile(r"^(\d+\.\s+)?User Interface Widgets$", re.IGNORECASE)
    """Pattern to find the start headline for scanning the content"""
    CONTENT_STOP_PATTERN = re.compile(r"^(\d+\.\s+)?User-defined Functions$", re.IGNORECASE)
    """Pattern to find the end headline for scanning the content"""

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
        super().__init__(version, toc, WidgetItem, reader, self.CONTENT_START_PATTERN, self.CONTENT_STOP_PATTERN,
                         csv_file, delimiter, page_offset)

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        # Check if the line contains a widget
        if m := self.WIDGET_PATTERN.match(line):
            name = m.group(1)
            var_name = m.group(2)
            index_name = m.group(3)
            par_list: list[str] = []
            n = 4
            while m.group(n):
                par_list.append(m.group(n))
            widget = self.add_widget(name, var_name, index_name, par_list)
            if widget:
                self.item_list.append(widget)
            doc_state = DocState.DESCRIPTION
        return doc_state

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
        if name in self.all_items:
            log.info(f"      - Duplicate {name} ({self.reader.location()})")
            self.duplicate_cnt += 1
        else:
            log.info(f"      - Found {name} ({self.reader.location()})")
            self.item_cnt += 1
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
            self.all_items[name] = widget
        return widget
