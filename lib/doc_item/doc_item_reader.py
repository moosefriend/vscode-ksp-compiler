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
import csv
from pathlib import Path
from types import TracebackType
from typing import Optional, TextIO, Union

from config.constants import ItemType
from config.system_config import SystemConfig
from doc_item.callback_item import CallbackItem
from doc_item.command_item import CommandItem
from doc_item.function_item import FunctionItem
from doc_item.variable_item import VariableItem
from doc_item.widget_item import WidgetItem

DOC_ITEM_CLASS = Union[type[WidgetItem] | type[VariableItem] | type[FunctionItem] | type[CommandItem] | type[CallbackItem]]
DOC_ITEM_TYPE = Union[WidgetItem | VariableItem | FunctionItem | CommandItem | CallbackItem]


class DocItemReader:
    def __init__(self, item_type: ItemType, encoding: str = "utf-8"):
        """
        Read the corresponding *.csv file and provide iterators with the doc item types.

        :param item_type: ItemType to get the *.csv file for
        :param encoding: Encoding used to read the file
        """
        self.doc_item_class: DOC_ITEM_CLASS = self.get_doc_item_class(item_type)
        self.csv_file: Path = SystemConfig().get_csv_file(item_type)
        self.encoding: str = encoding
        self.handle: Optional[TextIO] = None
        self.csv_reader = None
        self.line_no: int = 0

    @staticmethod
    def get_doc_item_class(item_type) -> DOC_ITEM_CLASS:
        """
        Get the class based on DocItem matching the specified item type.

        :param item_type: ItemType to get the DocItem class for
        :return: DocItem based class
        """
        match item_type:
            case ItemType.CALLBACK:
                doc_item_class = CallbackItem
            case ItemType.COMMAND:
                doc_item_class = CommandItem
            case ItemType.FUNCTION:
                doc_item_class = FunctionItem
            case ItemType.VARIABLE:
                doc_item_class = VariableItem
            case ItemType.WIDGET:
                doc_item_class = WidgetItem
            case _:
                raise ValueError(f"No doc item type for {item_type.name}")
        return doc_item_class

    def __enter__(self):
        """
        Context manager: Open the file.
        """
        self.handle = self.csv_file.open(newline='', encoding=self.encoding)
        self.csv_reader = csv.DictReader(self.handle, delimiter=SystemConfig().delimiter)
        self.line_no = 0
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType):
        """
        Context manager: Close the file.
        """
        self.handle.close()
        self.line_no = 0

    def __iter__(self):
        """
        Iterator which reads the separate rows of the *.csv file.
        """
        return self

    def __next__(self) -> DOC_ITEM_TYPE:
        """
        Get the next row of the *.csv file and create the corresponding doc item object.

        :return: DocItem based object containing the data read from the row
        """
        row = self.csv_reader.__next__()
        if row is None:
            raise StopIteration
        doc_item = self.create_doc_item(row)
        self.line_no += 1
        return doc_item

    def create_doc_item(self, row: dict[str, str]) -> DOC_ITEM_TYPE:
        """
        Create a new doc item based object using the attributes read from the *.csv row.

        :param row: Row read from the *.csv file
        :return: Doc item based object, e.g. CallbackItem
        """
        attr = {}
        for name, value in row.items():
            name = name.lower().replace(" ", "_")
            attr[name] = value
        # Special handling for "parameter_list": Split the value by comma
        if "parameter_list" in attr:
            if attr["parameter_list"]:
                attr["parameter_list"] = attr["parameter_list"].split(",")
            else:
                attr["parameter_list"] = []
        # Special handling for variables: range_start and range_end is always 0
        if self.doc_item_class == VariableItem:
            attr["range_start"] = 0
            attr["range_end"] = 0
        doc_item = self.doc_item_class(**attr)
        return doc_item
