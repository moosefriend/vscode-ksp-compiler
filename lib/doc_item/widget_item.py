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


class WidgetItem(DocItem):
    def __init__(self, file: Path, page_no: int, line_no: int, headline: str, category: str, name: str,
                 variable_name: str, index_name: str, parameter_list: list[str],
                 description: str, remarks: str, examples: str, see_also: str, source: str = None):
        """
        Container for type documentation.

        :param file: File where the widget has been found
        :param page_no: Page number in the PDF where the widget has been found
        :param line_no: Line number in the file where the widget has been found
        :param headline: Main headline where the item has been found
        :param category: ItemType (= Sub-headline in the table of contents) where the widget has been found
        :param name: Widget name
        :param variable_name: Name of the variable
        :param index_name: Name of the index if any
        :param parameter_list: List of parameter names
        :param description: Widget documentation
        :param remarks: Remarks for the widget
        :param examples: Examples for the widget
        :param see_also: See also references
        :param source: Where the widget has been parsed, e.g. build-in
        """
        super().__init__(file, page_no, line_no, headline, category, name, description, source)
        self.variable_name: str = variable_name
        self.index_name: str = index_name
        self.parameter_list: list[str] = parameter_list
        self.remarks: str = remarks
        self.examples: str = examples
        self.see_also: str = see_also

    def fix_documentation(self):
        """
        Remove newlines at the end and some spaces.
        """
        self.description = self.description.strip()
        self.remarks = self.remarks.strip()
        self.remarks = self.fix_bullet_items(self.remarks)
        self.examples = self.examples.strip()
        self.see_also = self.see_also.strip()

    @staticmethod
    def csv_header():
        return ("File", "Page No", "Line No", "Headline", "Category", "Name", "Variable Name", "Index Name",
                "Parameter List", "Description", "Remarks", "Examples", "See Also", "Source")

    def as_csv_list(self) -> tuple[str, int, int, str, str, str, str, str, str, str, str, str, str, str]:
        return (self.file.name, self.page_no, self.line_no, self.headline, self.category, self.name, self.variable_name,
                self.index_name, ",".join(self.parameter_list), self.description,  self.remarks, self.examples,
                self.see_also, self.source)

    def get_snippet_variable_name(self):
        """
        Construct the variable name to be used in the snippets.

        :return: Variable name to be used in snippets
        """
        snippet_variable_name = self.variable_name
        snippet_variable_name = snippet_variable_name.replace("<", "${<<index>>:")
        # Replace the last occurrence of ">" with "}"
        pre, post = snippet_variable_name.rsplit(">", 1)
        snippet_variable_name = pre + "}" + post
        if snippet_variable_name.startswith("$"):
            # Escape the snippet variable name
            snippet_variable_name = r"\\" + snippet_variable_name
        return snippet_variable_name

    def get_snippet_index_name(self):
        """
        Construct the index name to be used in the snippets.

        :return: Index name to be used in snippets
        """
        if self.index_name:
            snippet_index_name = f"[${{<<index>>:{self.index_name}}}]"
        else:
            snippet_index_name = ""
        return snippet_index_name

    def get_snippet_parameter_list(self):
        """
        Construct the parameter list to be used in the snippets.

        :return: Parameter list to be used in snippets
        """
        # "declare ui_table %${1:array}[${2:colmns}](${3:width}, ${4:height}, ${5:range})"
        if self.parameter_list:
            par_list = []
            for cur_parameter in self.parameter_list:
                snippet_parameter = f"${{<<index>>:{cur_parameter}}}"
                par_list.append(snippet_parameter)
            snippet_parameter_list = f"({', '.join(par_list)})"
        else:
            snippet_parameter_list = ""
        return snippet_parameter_list

    def format_sections(self) -> str:
        text = DocItem.check_section("Remarks", self.remarks)
        text += DocItem.check_section("Example", self.examples)
        text += DocItem.check_section("See also", self.see_also)
        return text
