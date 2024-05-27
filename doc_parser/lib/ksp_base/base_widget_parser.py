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
    WIDGET_PATTERN = re.compile(r"^declare\s+([a-z_]+)\s+([$%]<[a-z-]+>)(?:\[([^]]+)])?(?:\s+\((.*)\))?$")
    """Pattern to find a widget, e.g. declare ui_button $<variable-name>"""
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
        super().__init__(
            version,
            toc,
            WidgetItem,
            reader,
            self.CONTENT_START_PATTERN,
            self.CONTENT_STOP_PATTERN,
            csv_file,
            delimiter,
            page_offset
        )

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        # Check if the line contains a widget
        if m := self.WIDGET_PATTERN.match(line):
            name = m.group(1)
            variable_name = m.group(2)
            index_name = m.group(3)
            arguments = m.group(4)
            parameter_list = []
            if arguments:
                for parameter in arguments.split(","):
                    parameter = parameter.strip().replace("<", "").replace(">", "")
                    parameter_list.append(parameter)
            self.add_widget(name, variable_name, index_name, parameter_list)
            doc_state = DocState.DESCRIPTION
        return doc_state

    def add_widget(self, name: str, var_name: str, index_name: str, parameter_list: list[str]):
        """
        Add a widget if it does not exist.

        :param name: Name of the widget
        :param var_name: Name of the variable
        :param index_name: Name of the index if any
        :param parameter_list: List of parameter names
        """
        widget = WidgetItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            variable_name=var_name,
            index_name=index_name,
            parameter_list=parameter_list,
            description="",
            remarks="",
            examples="",
            see_also="",
            source="BUILT-IN"
        )
        self.add_item(widget)
