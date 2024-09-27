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

from config.system_config import SystemConfig
from ksp_parser.main_parser import MainParser
from config.constants import ParserType
from util.format import headline


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config-file', required=True, help="Path to the *.ini configuration file")
args = parser.parse_args()
ini_file = Path(args.config_file).resolve()
if not ini_file.is_file():
    print(f"*** Error: Can't find configuration file {ini_file}")
    sys.exit(-1)
config = SystemConfig(ini_file)
headline("Loading Main Parser")
main_parser = MainParser.get_parser(ParserType.MAIN)
main_parser.parse()
