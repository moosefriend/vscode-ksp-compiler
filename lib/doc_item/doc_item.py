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
from abc import abstractmethod
from pathlib import Path
from typing import Any

from util.format_util import text2markdown


class DocItem:
    BULLET_PATTERN = re.compile(r"^•\s+", re.MULTILINE)
    """Pattern for bullet list item"""
    HYPHEN_PATTERN = re.compile(r"^-\s+(.*)")
    """Pattern for hyphen list item"""

    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, name: str,
                 description: str = None, source: str = None):
        """
        Container for documentation item.

        :param file: File where the item has been found
        :param page_no: Page number in the PDF where the item has been found
        :param line_no: Line number in the file where the item has been found
        :param headline: Main headline where the item has been found
        :param category: ItemType (= Sub-headline in the table of contents) where the item has been found
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
        self.parsed_text: str = ""

    @classmethod
    def plural(cls):
        """
        :return: Plural string of the item, e.g. "callbacks"
        """
        return cls.__name__.lower().replace("item", "") + "s"

    @abstractmethod
    def fix_documentation(self):
        """
        Correct any strange characters or newlines in the documentation.
        """

    @staticmethod
    def fix_bullet_items(text: str) -> str:
        """
        Replace bullet items "• " with "- ".

        :param text: Text to replace
        :return: New text where bullets are replaced
        """
        return DocItem.BULLET_PATTERN.sub("- ", text)

    @staticmethod
    @abstractmethod
    def csv_header() -> list[str]:
        """
        :return: List of the headers to be written to the *.csv file
        """

    @abstractmethod
    def as_csv_list(self) -> list[Any]:
        """
        :return: List of the internal values to be written to the *.csv file
        """

    def fix_description(self):
        """
        Remove newlines at the end and some spaces.
        """
        self.description = self.description.strip()
        self.description = self.description.replace("  ", " ")
        self.description = self.description.replace(" .", ".")
        self.description = self.description.replace("( ", "(")
        self.description = self.description.replace(" )", ")")
        self.description = self.fix_bullet_items(self.description)

    def format_description(self) -> str:
        """
        Format the description for type script export.

        :return: Formatted description
        """
        text = text2markdown(self.description)
        text += self.format_sections()
        text += "\n"
        text += self.format_reference()
        text = text.strip()
        text = DocItem.convert_special_characters(text)
        return text

    @staticmethod
    def convert_special_characters(text: str) -> str:
        """
        Convert newlines to \\n and quotes to \\".

        :param text: Text to analyze
        :return: Converted text
        """
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "")
        text = text.replace('"', '\\"')
        return text

    @abstractmethod
    def format_sections(self) -> str:
        """
        Format additional doc item type specific sections for type script export.

        :return: Formatted sections
        """

    @staticmethod
    def format_example(text: str) -> str:
        """
        Format the "Example" section if it exists for the type script export.

        :param text: Text of the section if any
        :return: Formatted "Example" section or an empty string if the the text is emtpy
        """
        if text:
            # Format example text with ksp syntax highlighting
            text = f"\n\n**Example:**  \n```ksp\n{text}\n```\n"
        return text

    @staticmethod
    def format_see_also(text: str) -> str:
        """
        Format the "See Also" section if it exists for the type script export.

        :param text: Text of the section if any
        :return: Formatted "See Also" section or an empty string if the the text is emtpy
        """
        if text:
            # Prefix every line with a hyphen and a space
            text = f"\n\n**See Also:**  \n- " + text2markdown(text).replace("  \n", "\n- ")
        return text

    @staticmethod
    def format_remarks(text: str) -> str:
        """
        Format the "Remarks" section if it exists for the type script export.

        :param text: Text of the section if any
        :return: Formatted "Remarks" section or an empty string if the the text is emtpy
        """
        new_text = ""
        if text:
            # Remarks are already an item list
            for line in text.split("\n"):
                if m := DocItem.HYPHEN_PATTERN.match(line):
                    new_text += f"- {text2markdown(m.group(1))}  \n"
                else:
                    new_text += f"{text2markdown(line)}  \n"
            new_text = f"\n\n**Remarks:**  \n{new_text.rstrip()}"
        return new_text

    @staticmethod
    def format_comment(text: str) -> str:
        """
        Format the "Comment" section if it exists for the type script export.

        :param text: Text of the section if any
        :return: Formatted "Comment" section or an empty string if the the text is emtpy
        """
        if text:
            text = f"\n\n**Comment:** {text2markdown(text)}"
        return text

    def format_reference(self) -> str:
        """
        Format the reference for type script export.

        :return: Formatted reference
        """
        text = f"\n\n**Reference:** Chapter \"{text2markdown(self.headline)}\", Page {self.page_no}"
        return text
