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
import re
from ksp_base.base_main_parser import BaseMainParser


class KspMainParser(BaseMainParser):
    """Page ksp_parser for Kontakt 6.0 KSP reference manual"""

    KSP_MANUAL_PATTERN = re.compile(r"^\s*KSP Reference Manual\s*$")

    @staticmethod
    def visitor_body(text: str, user_matrix, tm_matrix, font_dict, font_size):
        # Skip footer like "14 KSP Reference Manual"
        if KspMainParser.KSP_MANUAL_PATTERN.match(text):
            # Remove the page number
            while KspMainParser._parts and not KspMainParser._parts.pop(-1).isdigit():
                pass
        else:
            KspMainParser._parts.append(text)
