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
from pathlib import Path

from doc_item.doc_item import DocItem


class CommandItem(DocItem):
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, name: str,
                 parameter_list: list[str], description: str, remarks: str, examples: str, see_also: str,
                 source: str = None):
        """
        Container for command documentation.

        :param file: File where the command has been found
        :param page_no: Page number in the PDF where the command has been found
        :param line_no: Line number in the file where the command has been found
        :param headline: Main headline where the item has been found
        :param category: ItemType (= Sub-headline in the table of contents) where the item has been found
        :param name: Variable name
        :param parameter_list: List of parameter names
        :param description: Item documentation
        :param remarks: Remarks for the callback
        :param examples: Examples for the callback
        :param see_also: See also references
        :param source: Where the item has been parsed, e.g. build-in
        """
        super().__init__(file, page_no, line_no, headline, category, name, description, source)
        self.parameter_list: list[str] = parameter_list
        self.remarks: str = remarks
        self.examples: str = examples
        self.see_also: str = see_also

    def fix_documentation(self):
        """
        Remove newlines at the end and some spaces.
        """
        self.description = self.description.strip()
        self.description = self.fix_bullet_items(self.description)
        self.remarks = self.remarks.strip()
        self.remarks = self.fix_bullet_items(self.remarks)
        self.examples = self.examples.strip()
        self.see_also = self.see_also.strip()

    @staticmethod
    def csv_header():
        return ("File", "Page No", "Line No", "Headline", "Category", "Name", "Parameter List", "Description", "Remarks",
                "Examples", "See Also", "Source")

    def as_csv_list(self) -> tuple[str, int, int, str, str, str, str, str, str, str, str, str]:
        return (self.file.name, self.page_no, self.line_no, self.headline, self.category, self.name,
                ",".join(self.parameter_list), self.description, self.remarks, self.examples, self.see_also,
                self.source)
