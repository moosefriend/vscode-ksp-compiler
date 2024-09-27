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

from util.csv_sniff_reader import CsvSniffReader

log = logging.getLogger(__name__)


class VariableGenerator:
    def __init__(self, csv_file: Path):
        """
        Parse variables in the specified text file.

        :param csv_file: Comma separated file containing the parsed variables/constants
        """
        self.csv_file: Path = csv_file

    def read_csv_file(self):
        """
        Read the *.csv file.
        The delimiter will be auto-detected ("," or ";").
        """
        with CsvSniffReader(self.csv_file, delimiter=",;") as csv_reader:
            for row in csv_reader:
                # Skip the headline
                if csv_reader.line_no == 1:
                    column_headers = row
                    continue
                col = 0
                log.info(f"{'-' * 20} Line {csv_reader.line_no} {'-' * 20}")
                for value in row:
                    log.info(f">>>>> {column_headers[col]}: {value}")
                    col += 1


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    out_dir = root / "out"
    version = "7.6"
    csv_file = out_dir / f"ksp_{version.replace('.', '_')}" / "built_in_variables.csv"
    generator = VariableGenerator(csv_file)
    generator.read_csv_file()
