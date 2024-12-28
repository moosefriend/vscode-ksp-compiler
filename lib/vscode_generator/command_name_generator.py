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


class CommandNameGenerator(BaseGenerator):
    @staticmethod
    def process():
        """
        Reads the names from the *.csv file and generate the command names type script file.
        """
        log.info(f"Generate {SystemConfig().command_names_ts.as_posix()}")
        name_list = BaseGenerator.read_name_list(ItemType.COMMAND) | BaseGenerator.read_name_list(ItemType.FUNCTION)
        with SystemConfig().command_names_ts.open("w", encoding="utf-8") as f:
            f.write(f"{BaseGenerator.COPYRIGHT_HEADER}\n")
            f.write(f"// This file is automatically generated by {Path(__file__).as_posix()}\n")
            f.write(f"// The command names are based on\n")
            f.write(f"// - Parsed Commands: {SystemConfig().get_csv_file(ItemType.COMMAND).as_posix()}\n")
            f.write(f"// - Parsed Functions: {SystemConfig().get_csv_file(ItemType.FUNCTION).as_posix()}\n")
            f.write(f"// - Manual Overrides: {SystemConfig().get_patch_csv_file(ItemType.COMMAND).as_posix()}\n")
            f.write(f"// Generated at: {strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"export var CommandNames: string[] = [\n")
            for name in natsorted(name_list):
                f.write(f'    "{name}",\n')
            f.write(f"]\n")
