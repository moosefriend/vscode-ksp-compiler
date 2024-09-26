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
from enum import Enum


class ParserType(Enum):
    """
    Parser types used for dynamic loading.
    """
    MAIN = "Main"
    TOC = "Toc"
    CALLBACK = "Callback"
    WIDGET = "Widget"
    COMMAND = "Command"
    FUNCTION = "Function"
    VARIABLE = "Variable"

    def lower_plural(self) -> str:
        """
        :return: Plural version of the constant, e.g. "callbacks"
        """
        return self.value.lower() + "s"

    def plural(self) -> str:
        """
        :return: Plural version of the constant, e.g. "Callbacks"
        """
        return self.value() + "s"

    @staticmethod
    def from_string(value: str) -> 'ParserType':
        """
        Get the parser type based on the specified string.

        :param value: String to get the parser type for
        :return: ParserType mathing the given string
        """
        for parser_type in ParserType:
            if parser_type.value.lower() == value.lower() or parser_type.lower_plural() == value.lower():
                return parser_type

    @staticmethod
    def all_phases() -> tuple['ParserType', ...]:
        """
        :return: Tuple of all ParserTypes for all phases
        """
        return ParserType.CALLBACK, ParserType.WIDGET, ParserType.COMMAND, ParserType.FUNCTION, ParserType.VARIABLE


class DocState(Enum):
    NONE = ""
    CATEGORY = "category"
    ITEM = "item"
    DESCRIPTION = "description"
    REMARKS = "remarks"
    EXAMPLES = "examples"
    SEE_ALSO = "see_also"
