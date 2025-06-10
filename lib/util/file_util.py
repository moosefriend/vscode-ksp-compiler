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
import logging
from pathlib import Path

import yaml
from yaml import SafeLoader

log = logging.getLogger(__name__)


def replace_in_file(file: Path, search_string: str, replace_string: str):
    """
    Replace the search string with the replace string in the given file.

    :param file: File in which to replace the string
    :param search_string: String to search which will be replaced
    :param replace_string: String to replace in the file
    """
    content = file.read_text()
    if search_string in content:
        log.info(f"Replace {search_string} in {file.as_posix()}")
        file.write_text(content.replace(search_string, replace_string))
    else:
        log.warning(f"Search string {search_string} not found in {file.as_posix()}")


def yml2json(yml_file: Path, json_file: Path):
    """
    Convert a YAML file to a JSON file.

    :param yml_file: YAML file to convert
    :param json_file: JSON file to generate
    """
    json_file.parent.mkdir(parents=True, exist_ok=True)
    if yml_file.is_file():
        log.info(f"Convert {yml_file} -> {json_file}")
        with yml_file.open("r") as f:
            data = yaml.load(f, Loader=SafeLoader)
        with json_file.open("w") as f:
            # Supress type mismatch warning
            json.dump(data, f, indent=4)
    else:
        raise FileNotFoundError(f"YAML input file {yml_file.as_posix()} not found")
