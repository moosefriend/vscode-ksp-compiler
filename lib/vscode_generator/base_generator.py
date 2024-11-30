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

from config.constants import ItemType
from doc_item.doc_item_reader import DocItemReader

log = logging.getLogger(__name__)


class BaseGenerator:
    @staticmethod
    def read_name_list(item_type: ItemType) -> list[str]:
        """
        From the *.csv file read the Name column and combine the names with "|".

        :param item_type: ItemType for get the file to read
        """
        name_list = []
        with DocItemReader(item_type) as csv_reader:
            log.info(f"Read name list from {csv_reader.csv_file.as_posix()}")
            for doc_item in csv_reader:
                name_list.append(doc_item.name)
        return name_list

    @staticmethod
    @abstractmethod
    def process():
        """
        Generate the corresponding objects.
        This method must be overridden.
        """
