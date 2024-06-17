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
import json
from pathlib import Path
import yaml
from yaml import SafeLoader

cur_dir = Path(__file__).parent
input_file_list = [
    Path("language-configuration.yml"),
    Path("syntaxes/ksp.tmGrammar.yml"),
    Path("snippets/ksp.snippets.yml")
]
output_dir = Path("out")

for input_file in input_file_list:
    base_name = input_file.stem
    output_file = output_dir / f"{base_name}.json"
    print(f"Converting {input_file.as_posix()} -> {output_file.as_posix()}", end="")
    input_path = cur_dir / input_file
    output_path = cur_dir / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if input_path.is_file():
        with input_path.open("r") as f:
            data = yaml.load(f, Loader=SafeLoader)
        with output_path.open("w") as f:
            json.dump(data, f, indent=4)
        print(": OK")
    else:
        print(f": *** ERROR: {input_file.resolve().as_posix()} not found!")
