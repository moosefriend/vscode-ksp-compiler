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


class DocItem:
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, name: str,
                 description: str = None, source: str = None):
        """
        Container for documentation item.

        :param file: File where the item has been found
        :param page_no: Page number in the PDF where the item has been found
        :param line_no: Line number in the file where the item has been found
        :param headline: Main headline where the item has been found
        :param category: Category (= Sub-headline in the table of contents) where the item has been found
        :param name: Item name
        :param description: Item documentation
        :param source: Where the item has been parsed, e.g. build-in
        """
        self.file: Path = file
        self.page_no: int = page_no
        self.line_no: int = line_no
        self.headline: str = headline
        self.category: str = category
        self.name: str = name
        self.description: str = description
        self.source: str = source

    def fix_description(self):
        """
        Remove newlines at the end and some spaces.
        """
        self.description = self.description.strip()
        self.description = self.description.replace("  ", " ")
        self.description = self.description.replace(" .", ".")
        self.description = self.description.replace("( ", "(")
        self.description = self.description.replace(" )", ")")
