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


class VariableItem(DocItem):
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, header_description: str,
                 item_list_headline: str, name: str, parameter: str, comment: str, description: str, source: str = None):
        """
        Container for variable documentation.

        :param file: File where the variable has been found
        :param page_no: Page number in the PDF where the variable has been found
        :param line_no: Line number in the file where the variable has been found
        :param headline: Main headline where the item has been found
        :param category: Category (= Sub-headline in the table of contents) where the item has been found
        :param header_description: Headline of a table e.g. containing constants (if any)
        :param item_list_headline: Headline for an item list e.g. for constants (if any)
        :param name: Variable name
        :param parameter: Parameter for variable e.g. for an array
        :param comment: Comment found behind the variable in brackets
        :param description: Item documentation
        :param source: Where the item has been parsed, e.g. build-in
        """
        super().__init__(file, page_no, line_no, headline, category, name, description)
        self.header_description: str = header_description
        self.item_list_headline: str = item_list_headline
        self.name: str = name
        self.parameter: str = parameter
        self.comment: str = comment
        self.description: str = description
        self.source: str = source

    def fix_documentation(self):
        """
        Remove newlines at the end and some spaces.
        """
        super().fix_description()
        self.header_description = self.header_description.strip()

    @staticmethod
    def header():
        """
        :return: Tuple of headline for the *.csv file
        """
        return ("File", "Page No", "Line No", "Headline", "Category", "Table Headline", "Item List Headline", "Name",
                "Parameter", "Comment", "Description", "Source")

    def as_list(self) -> tuple[str, int, int, str, str, str, str, str, str, str, str, str]:
        """
        :return: Tuple of the data
        """
        return (self.file.name, self.page_no, self.line_no, self.headline, self.category, self.header_description,
                self.item_list_headline,  self.name, self.parameter, self.comment, self.description, self.source)
