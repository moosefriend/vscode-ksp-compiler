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
import sys
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from config.constants import ParserType
from util.rewind_reader import RewindReader

if TYPE_CHECKING:
    from ksp_parser.toc_parser import TocParser

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
        # Log Settings
        self.log_dir: Path = self._get_dir("log_dir", create=True)
        self.log_file: Optional[Path] = None
        self.log_level_console: int = self._get_log_level("log_level_console")
        self.log_level_file: int = self._get_log_level("log_level_file")
        self.log_format_console: str = self.settings["log_format_console"]
        self.log_format_file: str = self.settings["log_format_file"]
        self.log_date_format_console: str = self.settings["log_date_format_console"]
        self.log_date_format_file: str = self.settings["log_date_format_file"]
        self.initialize_logging()
        # PDF Converter Settings
        self.txt_dir: Path = self._get_dir("txt_dir")
        self.pdf_file: Path = self._get_file("pdf_file")
        self.txt_file_original: Path = self._get_file("txt_file_original")
        self.txt_file_fixed: Path = self._get_file("txt_file_fixed")
        # Parser Settings
        self.page_offset: int = self._get_int("page_offset")
        self.page_header_lines: int = self._get_int("page_header_lines")
        self.out_dir: Path = self._get_dir("out_dir", create=True)
        self.callbacks_csv: Path = self._get_file("callbacks_csv")
        self.widgets_csv: Path = self._get_file("widgets_csv")
        self.functions_csv: Path = self._get_file("functions_csv")
        self.commands_csv: Path = self._get_file("commands_csv")
        self.variables_csv: Path = self._get_file("variables_csv")
        self.delimiter: str = self.settings["delimiter"]
        self.dump: bool = self._get_bool("dump")
        self.verbose: bool = self._get_bool("verbose")
        self.phases: set[ParserType] = self._get_phases("phases")
        self.reader: Optional[RewindReader] = None
        self.toc: Optional[TocParser] = None

    def _get_dir(self, name: str, create: bool = False) -> Path:
        """
        Get the path of the directory read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :param create: If True then the directory is created if it does not exist
        :return: Path of the directory
        """
        path = Path(self.settings[name])
        if not path.is_absolute():
            path = self.ini_dir / path
        if create:
            path.mkdir(exist_ok=True, parents=True)
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

    def _get_phases(self, name: str) -> set[ParserType]:
        """
        Get the list of parser types to run read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: List of active parser types
        """
        phases = set()
        for line in self.settings[name].splitlines():
            if line:
                parser_type = ParserType.from_string(line)
                if parser_type in ParserType.all_phases():
                    phases.add(parser_type)
                else:
                    log.warning(f"Phase {parser_type.value} will allways be called and needs not to be specified")
        return phases

    def _get_log_level(self, name: str) -> int:
        """
        Convert the string value to Log level read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Log level
        """
        log_level = logging.getLevelName(self.settings[name].upper())
        return log_level

    def has_phase(self, parser_type: ParserType) -> bool:
        """
        Check if the specified phase is active.

        :param parser_type: ParserType to check if it's active
        :return: True if the phase is active, False otherwise
        """
        ret_val: bool = False
        if parser_type in self.phases:
            ret_val = True
        return ret_val

    def initialize_logging(self):
        """
        Initialize the logging.
        """
        # Create a custom logger
        logger = logging.getLogger()
        # Set the overall logging level
        logger.setLevel(logging.DEBUG)
        # Define a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level_console)
        console_format = logging.Formatter(self.log_format_console, self.log_date_format_console)
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        if self.log_dir:
            self.log_file = self.log_dir / (Path(sys.argv[0]).stem + ".log")
            self.log_file.unlink(missing_ok=True)
            # Define a file handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.log_level_file)
            file_format = logging.Formatter(self.log_format_file, self.log_date_format_file)
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    ini_file = root / "cfg" / "ksp_7_10" / "system.ini"
    config = SystemConfig(ini_file)
    log.info(SystemConfig().kontakt_version)
