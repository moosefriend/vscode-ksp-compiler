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
import logging
from pathlib import Path

from ksp_base.base_main_parser import BaseMainParser
from ksp_base.constants import ParserType

log = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', required=True, help="Kontakt KSP version")
parser.add_argument('-p', '--pdf', required=True, help="Kontakt KSP reference manual PDF input file for parsing")
parser.add_argument('-c', '--convert', help="Convert the PDF file into a text file", type=bool, default=True)
parser.add_argument('-l', '--logfile', help="Log file", default=None)
args = parser.parse_args()

logging.basicConfig(
    filename=args.logfile,
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
root = Path(__file__).parent.parent
out_dir = root / "out"
version = args.version
pdf_file = args.pdf
parser = BaseMainParser.get_parser(ParserType.MAIN, version, pdf_file, out_dir, ",")
if args.convert:
    parser.convert_to_text()
else:
    parser.parse()
