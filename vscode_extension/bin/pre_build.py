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
import argparse
import sys
from pathlib import Path

import _find_lib  # noqa
from config.system_config import SystemConfig
from util.format_util import headline
from util.file_util import yml2json
from util.sublime_util import Sublime2TextMateConverter
from vscode_generator.command_completion_generator import CommandCompletionGenerator
from vscode_generator.command_name_generator import CommandNameGenerator
from vscode_generator.grammar_generator import GrammarGenerator
from vscode_generator.snippet_generator import SnippetGenerator
from vscode_generator.variable_completion_generator import VariableCompletionGenerator
from vscode_generator.variable_name_generator import VariableNameGenerator

parser = argparse.ArgumentParser(description="Convert *.yml to *.json and generate Type Script code for the extension")
parser.add_argument('-c', '--config-file', required=True, help="Path to the *.ini configuration file")
args = parser.parse_args()
ini_file = Path(args.config_file).resolve()
if not ini_file.is_file():
    print(f"*** Error: Can't find configuration file {ini_file}")
    sys.exit(-1)
config = SystemConfig(ini_file)
headline("Convert Sublime syntax *.yml to TextMate *.yml")
Sublime2TextMateConverter.convert(SystemConfig().sublime_syntax_yml, SystemConfig().text_mate_yml)
headline("Convert *.yml to *.json")
yml2json(SystemConfig().text_mate_yml, SystemConfig().text_mate_json)
yml2json(SystemConfig().lang_config_yml, SystemConfig().lang_config_json)
yml2json(SystemConfig().grammar_yml, SystemConfig().grammar_json)
yml2json(SystemConfig().snippets_yml, SystemConfig().snippets_json)
headline("Inject names into the grammar JSON file")
GrammarGenerator.process()
headline("Inject callbacks and widgets into the snippets JSON file")
SnippetGenerator.process()
headline("Generate variable names as type script file")
VariableNameGenerator.process()
headline("Generate command names as type script file")
CommandNameGenerator.process()
headline("Generate variable completion as type script file")
VariableCompletionGenerator.process()
headline("Generate command completion as type script file")
CommandCompletionGenerator.process()
