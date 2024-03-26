#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).

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
from pathlib import Path

from ksp_base.base_main_parser import BaseMainParser


class KspMainParser(BaseMainParser):
    """Page ksp_parser for Kontakt 7.6 KSP reference manual"""

    def __init__(self, version: str, pdf_file: Path, out_dir: Path, delimiter: str):
        super().__init__(version, pdf_file, out_dir, delimiter, page_offset=8, skip_lines=2)
