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
from pathlib import Path

from doc_item.doc_item import DocItem


class FunctionItem(DocItem):
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, name: str,
                 parameter_list: list[str], description: str, source: str = None):
        """
        Container for function documentation.

        :param file: File where the function has been found
        :param page_no: Page number in the PDF where the function has been found
        :param line_no: Line number in the file where the function has been found
        :param headline: Main headline where the item has been found
        :param category: ItemType (= Sub-headline in the table of contents) where the item has been found
        :param name: Variable name
        :param parameter_list: List of parameter names
        :param description: Item documentation
        :param source: Where the item has been parsed, e.g. build-in
        """
        super().__init__(file, page_no, line_no, headline, category, name, description, source)
        self.parameter_list: list[str] = parameter_list

    def fix_documentation(self):
        """
        Remove newlines at the end and some spaces.
        """
        self.description = self.description.strip()
        self.description = self.fix_bullet_items(self.description)

    @staticmethod
    def csv_header():
        return "File", "Page No", "Line No", "Headline", "Category", "Name", "Parameter List", "Description", "Source"

    def as_csv_list(self) -> tuple[str, int, int, str, str, str, str, str, str]:
        return (self.file.name, self.page_no, self.line_no, self.headline, self.category, self.name,
                ",".join(self.parameter_list), self.description, self.source)

    def format_sections(self) -> str:
        # No specific sections
        return ""
