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
from pathlib import Path
from time import strftime

from natsort import natsorted

from config.constants import ItemType
from config.system_config import SystemConfig
from vscode_generator.base_generator import BaseGenerator

log = logging.getLogger(__name__)


class VariableNameGenerator(BaseGenerator):
    @staticmethod
    def process():
        """
        Reads the names from the *.csv file and generate the variable names type script file.
        """
        log.info(f"Generate {SystemConfig().variable_names_ts.as_posix()}")
        name_list = BaseGenerator.read_name_list(ItemType.VARIABLE)
        with SystemConfig().variable_names_ts.open("w", encoding="utf-8") as f:
            f.write(f"{BaseGenerator.COPYRIGHT_HEADER}\n")
            f.write(f"// This file is automatically generated by {SystemConfig().rel_to_root(Path(__file__))}\n")
            f.write(f"// The variable names are based on\n")
            f.write(f"// - Parsed Variables: {SystemConfig().get_csv_path(ItemType.VARIABLE)}\n")
            f.write(f"// - Manual Overrides: {SystemConfig().get_patch_csv_path(ItemType.VARIABLE)}\n")
            f.write(f"// Generated at: {strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"export var NameList: string[] = [\n")
            for name in natsorted(name_list):
                f.write(f'    "{name}",\n')
            f.write(f"]\n")
