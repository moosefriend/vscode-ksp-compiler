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
from util.file_util import replace_in_file
from vscode_generator.base_generator import BaseGenerator

log = logging.getLogger(__name__)


class GrammarGenerator(BaseGenerator):
    @staticmethod
    def process():
        """
        Reads the grammar JSON file and replace <<category>> with the name list.
        """
        replace_list = [
            ItemType.CALLBACK,
            ItemType.COMMAND,
            ItemType.FUNCTION,
            ItemType.WIDGET
        ]
        log.info(f"Modify {SystemConfig().grammar_json.as_posix()}")
        for item_type in replace_list:
            search_string = f"<<{item_type.category()}>>"
            name_list = BaseGenerator.read_name_list(item_type)
            replace_string = "|".join(name_list)
            replace_in_file(SystemConfig().grammar_json, search_string, replace_string)

