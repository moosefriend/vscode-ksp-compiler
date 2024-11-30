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
from inspect import cleandoc
from textwrap import indent

from config.constants import ItemType
from config.system_config import SystemConfig
from doc_item.doc_item_reader import DocItemReader
from util.file_util import replace_in_file
from vscode_generator.base_generator import BaseGenerator

log = logging.getLogger(__name__)


class VariableNameGenerator(BaseGenerator):
    @staticmethod
    def process():
        """
        Reads the names from the *.csv file and generate the variable names type script file.
        """
        log.info(f"Generate {SystemConfig().variable_names_ts.as_posix()}")
        ...continue...