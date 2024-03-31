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
from ksp_base.base_command_parser import BaseCommandParser


class KspCommandParser(BaseCommandParser):
    MERGE_LINES = {
        # <line number in the text file>
    }
    """Set of lines to be merged, because they are wrapped and therefore not correctly identified"""
    # TODO: WRAPPED_COMMANDS are tables with 2 columns. Maybe for such complex use cases it would be easier to have
    #    an overwrite mechanism, so to ignore lines and manually configure the values.
    WRAPPED_CELLS = {
        # <line number in the text file>: (<command part in the first line>, <command part in the second line>)
    }
    """Dictionary of wrapped table cells to be merged"""
