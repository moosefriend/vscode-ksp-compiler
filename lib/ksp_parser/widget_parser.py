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
from typing import Optional

from doc_item.widget_item import WidgetItem
from ksp_parser.item_parser import ItemParser
from config.constants import DocState
from config.system_config import SystemConfig

log = logging.getLogger(__name__)


class WidgetParser(ItemParser):
    # Example: declare ui_table %<array-name>[num-elements] (<grid-width>, <grid-height>, <range>)
    WIDGET_PATTERN = re.compile(r"^declare\s+([a-z_]+)\s+([$%]<[a-z-]+>)(?:\[([^]]+)])?(?:\s+\((.*)\))?$")
    """Pattern to find a widget, e.g. declare ui_button $<variable-name>"""

    def __init__(self):
        """
        Parse widgets in the Kontakt KSP text manual.
        """
        super().__init__(
            WidgetItem,
            SystemConfig().widgets_content_patterns,
            SystemConfig().widgets_csv
        )

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        # Check if the line contains a widget
        if m := WidgetParser.WIDGET_PATTERN.match(line):
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
