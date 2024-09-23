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
import re
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
from typing import Optional

from ksp_base.base_toc_parser import BaseTocParser
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SystemConfig(metaclass=Singleton):
    KSP_PATTERN = re.compile(r"^ksp_(\d+)_(\d+)$")
    """Pattern to find the Kontakt version specific parser"""

    def __init__(self, ini_file: Path = None):
        """
        Read the system configuration data from the specified *.ini file.

        :param ini_file: Path to the *.ini file to read
        """
        self.ini_file: Path = ini_file
        self.ini_dir = ini_file.parent
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(self.ini_file)
        self.settings = config["General"]
        self.kontakt_version: str = self.settings["kontakt_version"].replace("_", ".")
        self.cfg_dir: Path = self._get_dir("cfg_dir")
        self.out_dir: Path = self._get_dir("out_dir")
        self.pdf_file: Path = self._get_file("pdf_file")
        self.txt_file_original: Path = self._get_file("txt_file_original")
        self.txt_file_fixed: Path = self._get_file("txt_file_fixed")
        self.page_offset: int = self._get_int("page_offset")
        self.page_header_lines: int = self._get_int("page_header_lines")
        self.callbacks_csv: Path = self._get_file("callbacks_csv")
        self.widgets_csv: Path = self._get_file("widgets_csv")
        self.functions_csv: Path = self._get_file("functions_csv")
        self.commands_csv: Path = self._get_file("commands_csv")
        self.variables_csv: Path = self._get_file("variables_csv")
        self.delimiter: str = self.settings["delimiter"]
        self.verbose: bool = self._get_bool("verbose")
        self.reader: Optional[RewindReader] = None
        self.toc: Optional[BaseTocParser] = None

    def _get_dir(self, name: str) -> Path:
        """
        Get the path of the directory read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Path of the directory
        """
        path = Path(self.settings[name])
        if not path.is_absolute():
            path = self.ini_dir / path
        return path.resolve()

    def _get_file(self, name: str) -> Path:
        """
        Get the path of the file read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Path of the file
        """
        return self._get_dir(name)

    def _get_int(self, name: str) -> int:
        """
        Convert the string number to an integer read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Integer of the number
        """
        number = int(self.settings[name])
        return number

    def _get_bool(self, name: str) -> bool:
        """
        Convert the string value to a boolean read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Boolean of the value
        """
        boolean = (self.settings[name].lower() == "true")
        return boolean


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    ini_file = root / "cfg" / "ksp_7_10" / "system.ini"
    config = SystemConfig(ini_file)
    log.info(SystemConfig().kontakt_version)
