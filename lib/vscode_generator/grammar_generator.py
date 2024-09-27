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

from config.constants import ItemType
from config.system_config import SystemConfig
from doc_item.doc_item_reader import DocItemReader
from util.file_util import replace_in_file

log = logging.getLogger(__name__)


class GrammarGenerator:
    @staticmethod
    def read_name_list(item_type: ItemType) -> str:
        """
        From the *.csv file read the Name column and combine the names with "|".

        :param item_type: ItemType for get the file to read
        """
        name_list = []
        with DocItemReader(item_type) as csv_reader:
            log.info(f"Read name list from {csv_reader.csv_file.as_posix()}")
            for doc_item in csv_reader:
                name_list.append(doc_item.name)
        return "|".join(name_list)

    @staticmethod
    def fill_place_holders():
        """
        Reads the grammar JSON file and replace <<category>> with the name list.
        """
        replace_list = [
            ItemType.CALLBACK,
            ItemType.COMMAND,
            ItemType.FUNCTION,
            ItemType.WIDGET
        ]
        log.info(f"Modify {SystemConfig().grammar_json}")
        for item_type in replace_list:
            search_string = f"<<{item_type.category()}>>"
            replace_string = GrammarGenerator.read_name_list(item_type)
            log.info(f"=> Replace {search_string}")
            replace_in_file(SystemConfig().grammar_json, search_string, replace_string)

