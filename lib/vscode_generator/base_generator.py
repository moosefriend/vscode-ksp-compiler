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
import logging
from abc import abstractmethod
from inspect import cleandoc

from config.constants import ItemType
from doc_item.callback_item import CallbackItem
from doc_item.command_item import CommandItem
from doc_item.doc_item_reader import DocItemReader
from doc_item.function_item import FunctionItem
from doc_item.variable_item import VariableItem
from doc_item.widget_item import WidgetItem

log = logging.getLogger(__name__)

ANY_ITEM_TYPE = CallbackItem | CommandItem | FunctionItem | VariableItem | WidgetItem


class BaseGenerator:
    COPYRIGHT_HEADER = cleandoc("""
        /**
         * This file is part of the vscode-ksp-compiler distribution
         * (https://github.com/moosefriend/vscode-ksp-compiler).
         *
         * Copyright (c) 2024 MooseFriend (https://github.com/moosefriend)
         *
         * This program is free software: you can redistribute it and/or modify
         * it under the terms of the GNU General Public License as published by
         * the Free Software Foundation, version 3.
         *
         * This program is distributed in the hope that it will be useful, but
         * WITHOUT ANY WARRANTY; without even the implied warranty of
         * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
         * General Public License for more details.
         *
         * You should have received a copy of the GNU General Public License
         * along with this program. If not, see <http://www.gnu.org/licenses/>.
         */
    """)

    @staticmethod
    def read_name_list(item_type: ItemType) -> set[str]:
        """
        From the *.csv file read the Name column.

        :param item_type: ItemType for the file to read
        :return: Set of names read from the *.csv file
        """
        # Use a set to overwrite duplicates
        name_list = set()
        with DocItemReader(item_type) as csv_reader:
            for doc_item in csv_reader:
                name_list.add(doc_item.name)
        return name_list

    @staticmethod
    def read_doc_items(item_type: ItemType) -> dict[str, ANY_ITEM_TYPE]:
        """
        From the *.csv file read all columns as doc_items.

        :param item_type: ItemType for the file to read
        :return: Dictionary where the key is the name and the value is the DocItem object read from the *.csv file
        """
        # Use a dictionary to overwrite duplicates
        all_doc_items: dict[str, ANY_ITEM_TYPE] = {}
        with DocItemReader(item_type) as csv_reader:
            for doc_item in csv_reader:
                all_doc_items[doc_item.name] = doc_item
        return all_doc_items

    @staticmethod
    @abstractmethod
    def process():
        """
        Generate the corresponding objects.
        This method must be overridden.
        """
