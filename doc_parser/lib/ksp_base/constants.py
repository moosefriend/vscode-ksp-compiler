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
    VARIABLE = "Variable"

    def plural(self) -> str:
        """
        :return: Plural version of the constant, e.g. "callbacks"
        """
        return self.value.lower() + "s"


class DocState(Enum):
    NONE = ""
    CATEGORY = "category"
    ITEM = "item"
    DESCRIPTION = "description"
    REMARKS = "remarks"
    EXAMPLES = "examples"
    SEE_ALSO = "see_also"
