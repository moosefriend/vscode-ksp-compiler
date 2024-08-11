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

"""
Inject lists in the file "out/ksp.tmGrammar.json":
- Replace <<built_in_callbacks>> with the list of built_in_callbacks.csv column "Name"
- Replace <<built_in_widgets>> with the list of built_in_widgets.csv column "Name"
- Replace <<built_in_commands>> with the list of built_in_commands.csv column "Name"
- Replace <<built_in_functions>> with the list of built_in_functions.csv column "Name"
"""
import csv
from pathlib import Path

def replace_in_file(file: Path, search_string: str, replace_string: str):
    """
    Replace the search string with the replace string in the given file.

    :param file: File in which to replace the string
    :param search_string: String to search which will be replaced
    :param replace_string: String to replace in the file
    """
    file.write_text(file.read_text().replace(search_string, replace_string))


def read_name_list(csv_file: Path) -> str:
    """
    From the given *.csv file read the Name column and combine the names with "|"
    """
    with csv_file.open(newline='') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            print(row['first_name'], row['last_name'])


root_dir = Path(__file__).parent.parent
replace_list = [
    "buit_in_callbacks",
    "built_in_commands",
    "built_in_functions",
    "built_in_widgets"
]
input_dir = root_dir / "in"
output_dir = root_dir / "out"

grammar_file = output_dir / "ksp.tmGrammar.json"

for category in replace_list:
    csv_file = input_dir / f"{category}.csv"
    search_string = f"<<{category}>>"
    replace_string = read_name_list(csv_file)
    replace_in_file(grammar_file, search_string, replace_string)
