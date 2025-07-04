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
from doc_item.command_item import CommandItem
from vscode_generator.base_generator import BaseGenerator

log = logging.getLogger(__name__)


class CommandCompletionGenerator(BaseGenerator):
    @staticmethod
    def process():
        """
        Reads the data from the *.csv file and generate the command completion type script file.
        """
        log.info(f"Generate {SystemConfig().command_completion_ts.as_posix()}")
        doc_items: dict[str, CommandItem] = BaseGenerator.read_doc_items(ItemType.COMMAND) | BaseGenerator.read_doc_items(ItemType.FUNCTION)
        with SystemConfig().command_completion_ts.open("w", encoding="utf-8") as f:
            f.write(f"{BaseGenerator.COPYRIGHT_HEADER}\n")
            f.write(f"// This file is automatically generated by {SystemConfig().rel_to_root(Path(__file__))}\n")
            f.write(f"// The command completions are based on\n")
            f.write(f"// - Parsed Commands:  {SystemConfig().get_csv_path(ItemType.COMMAND)}\n")
            f.write(f"// - Manual Overrides: {SystemConfig().get_patch_csv_path(ItemType.COMMAND)}\n")
            f.write(f"// - Parsed Functions: {SystemConfig().get_csv_path(ItemType.FUNCTION)}\n")
            f.write(f"// - Manual Overrides: {SystemConfig().get_patch_csv_path(ItemType.FUNCTION)}\n")
            f.write(f"// Generated at: {strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"import {{ CompletionRecord }} from \"../config/completionRecord\";\n")
            f.write(f"export var CompletionList: Map<string, CompletionRecord> = new Map([\n")
            for doc_item in natsorted(doc_items.values(), key=lambda x: x.name):
                if doc_item.parameter_list:
                    snippet_string = f"{doc_item.name}("
                    signature = snippet_string
                    for i, cur_par in enumerate(doc_item.parameter_list):
                        snippet_string += f"${{{i + 1}:{cur_par}}}, "
                        signature += f"{cur_par}, "
                    snippet_string = snippet_string[:-2] + ")"
                    signature = signature[:-2] + ")"
                else:
                    snippet_string = f"{doc_item.name}"
                    signature = snippet_string
                description = doc_item.format_description()
                f.write(f'    ["{doc_item.name}", new CompletionRecord(\n')
                f.write(f'        "{doc_item.name}",\n')
                f.write(f'        "{description}",\n')
                f.write(f'        "{signature}",\n')
                f.write(f'        "{snippet_string}"\n')
                f.write(f'    )],\n')
            f.write(f"]);\n")
