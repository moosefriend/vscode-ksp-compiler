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
from ksp_base.base_variable_parser import BaseVariableParser


class KspVariableParser(BaseVariableParser):
    MERGE_LINES = {
        # <line number in the text file>
        9072,
        9074,
        9075,
        9076,
        9078,
        9533
    }
    """Set of lines to be merged, because they are wrapped and therefore not correctly identified"""
    # TODO: WRAPPED_VARIABLES are tables with 2 columns. Maybe for such complex use cases it would be easier to have
    #    an overwrite mechanism, so to ignore lines and manually configure the values.
    WRAPPED_CELLS = {
        # <line number in the text file>: (<variable part in the first line>, <variable part in the second line>)
        9905: ("$CONTROL_PAR_WAVE_END_", "COLOR"),
        9907: ("$CONTROL_PAR_WAVE_END_", "ALPHA"),
        9909: ("$CONTROL_PAR_WAVETABLE", "_END_COLOR"),
        9911: ("$CONTROL_PAR_WAVETABLE", "_END_ALPHA")
    }
    """Dictionary of wrapped table cells to be merged"""
