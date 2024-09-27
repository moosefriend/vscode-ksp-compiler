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
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, block_headline: str,
                 item_list_headline: str, name: str, range_start: int, range_end: int, parameter: str, comment: str,
                 description: str, see_also: str = None, source: str = None):
        """
        Container for variable documentation.

        :param file: File where the variable has been found
        :param page_no: Page number in the PDF where the variable has been found
        :param line_no: Line number in the file where the variable has been found
        :param headline: Main headline where the item has been found
        :param category: ItemType (= Sub-headline in the table of contents) where the item has been found
        :param block_headline: Headline of a block e.g. containing constants (if any)
        :param item_list_headline: Headline for an item list e.g. for constants (if any)
        :param name: Variable name
        :param range_start: Start index for variable ranges (e.g. $MARK_0 ... $MARK_28)
        :param range_end: End index for variable ranges (e.g. $MARK_0 ... $MARK_28)
        :param parameter: Parameter for variable e.g. for an array
        :param comment: Comment found behind the variable in brackets
        :param description: Item documentation
        :param see_also: Other variable names in the same block
        :param source: Where the item has been parsed, e.g. build-in
        """
        super().__init__(file, page_no, line_no, headline, category, name, description)
        self.block_headline: str = block_headline
        self.item_list_headline: str = item_list_headline
        self.name: str = name
        self.range_start: int = range_start
        self.range_end: int = range_end
        self.parameter: str = parameter
        self.comment: str = comment
        self.description: str = description
        self.see_also: str = see_also
        self.source: str = source

    def fix_documentation(self):
        """
        Remove newlines at the end and some spaces.
        """
        super().fix_description()
        self.block_headline = self.block_headline.strip()

    @staticmethod
    def csv_header():
        return ("File", "Page No", "Line No", "Headline", "Category", "Block Headline", "Item List Headline", "Name",
                "Parameter", "Comment", "Description", "See Also", "Source")

    def as_csv_list(self) -> tuple[str, int, int, str, str, str, str, str, str, str, str, str, str]:
        return (self.file.name, self.page_no, self.line_no, self.headline, self.category, self.block_headline,
                self.item_list_headline,  self.name, self.parameter, self.comment, self.description, self.see_also, self.source)
