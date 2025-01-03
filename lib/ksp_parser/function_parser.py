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

from doc_item.function_item import FunctionItem
from ksp_parser.content_pattern import ContentPattern
from ksp_parser.item_parser import ItemParser
from config.constants import DocState
from config.system_config import SystemConfig

log = logging.getLogger(__name__)


class FunctionParser(ItemParser):
    FUNCTION_PATTERN = re.compile(r"^([a-z_]+)\((x(?:, y)?|<expression>, <shift-bits>)\)(?::\s+(.*))?$")
    """Pattern to find a function, e.g. inc(x)"""
    CONTENT_PATTERNS = [
        ContentPattern(
            start_pattern=re.compile(r"^(\d+\.\s+)?Arithmetic Commands & Operators$", re.IGNORECASE),
            stop_pattern=re.compile(r"^(\d+\.\s+)?Control Statements$", re.IGNORECASE)
        )
    ]
    """Content start and stop patterns for headlines"""

    def __init__(self):
        """
        Parse commands in the Kontakt KSP text manual.
        """
        super().__init__(
            FunctionItem,
            FunctionParser.CONTENT_PATTERNS,
            SystemConfig().functions_csv,
        )

    def check_item(self, line) -> Optional[DocState]:
        doc_state: Optional[DocState] = None
        if m := FunctionParser.FUNCTION_PATTERN.match(line):
            name = m.group(1)
            arguments = m.group(2)
            description = m.group(3)
            parameter_list = []
            if arguments:
                for parameter in arguments.split(","):
                    parameter = parameter.strip()
                    parameter_list.append(parameter)
            self.add_function(name, parameter_list, description)
            doc_state = DocState.DESCRIPTION
        return doc_state

    def add_function(self, name: str, parameter_list: list[str], description: str):
        """
        Add a function if it does not exist.

        :param name: Name of the function
        :param parameter_list: List or parameter names
        :param description: Description (if any)
        """
        if description is None:
            description = ""
        function = FunctionItem(
            file=self.reader.file,
            page_no=self.reader.page_no,
            line_no=self.reader.line_no,
            headline=self.headline,
            category=self.category,
            name=name,
            parameter_list=parameter_list,
            description=description,
            source="BUILT-IN"
        )
        self.add_item(function)
