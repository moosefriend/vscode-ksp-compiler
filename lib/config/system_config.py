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

from config.constants import ItemType
from ksp_parser.content_pattern import ContentPattern
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

    CONTENT_START_STOP_PATTERN = re.compile(r"^\s*(.+?)\s*==>\s*(.+)\s*")
    """Pattern to get the content start and stop patterns from the *.ini file"""

    def __init__(self, ini_file: Path = None):
        """
        Read the system configuration data from the specified *.ini file.

        :param ini_file: Path to the *.ini file to read
        """
        self.ini_file: Path = ini_file
        self.ini_dir = ini_file.parent
        self.root_dir = self.ini_dir.parent.parent.resolve()
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
        self.pdf_file: Path = self._get_file("pdf_file")
        self.txt_file_original: Path = self._get_file("txt_file_original")
        self.txt_file_fixed: Path = self._get_file("txt_file_fixed")
        # Parser Settings
        self.page_offset: int = self._get_int("page_offset")
        self.page_header_lines: int = self._get_int("page_header_lines")
        self.csv_dir: Path = self._get_dir("csv_dir")
        self.callbacks_content_patterns: list[ContentPattern] = self._get_content_patterns("callbacks_content_patterns")
        self.callbacks_csv: Path = self._get_file("callbacks_csv")
        self.widgets_content_patterns: list[ContentPattern] = self._get_content_patterns("widgets_content_patterns")
        self.widgets_csv: Path = self._get_file("widgets_csv")
        self.functions_content_patterns: list[ContentPattern] = self._get_content_patterns("functions_content_patterns")
        self.functions_csv: Path = self._get_file("functions_csv")
        self.commands_content_patterns: list[ContentPattern] = self._get_content_patterns("commands_content_patterns")
        self.commands_csv: Path = self._get_file("commands_csv")
        self.variables_content_patterns: list[ContentPattern] = self._get_content_patterns("variables_content_patterns")
        self.variables_csv: Path = self._get_file("variables_csv")
        self.delimiter: str = self.settings["delimiter"]
        self.dump: bool = self._get_bool("dump")
        self.verbose: bool = self._get_bool("verbose")
        self.phases: set[ItemType] = self._get_phases("phases")
        self.reader: Optional[RewindReader] = None
        self.toc: Optional[TocParser] = None
        # VS Code Generator Settings
        self.lang_config_yml: Path = self._get_file("lang_config_yml")
        self.lang_config_json: Path = self._get_file("lang_config_json")
        self.sublime_syntax_yml: Path = self._get_file("sublime_syntax_yml")
        self.text_mate_yml: Path = self._get_file("text_mate_yml")
        self.text_mate_json: Path = self._get_file("text_mate_json")
        self.grammar_yml: Path = self._get_file("grammar_yml")
        self.grammar_json: Path = self._get_file("grammar_json")
        self.snippets_yml: Path = self._get_file("snippets_yml")
        self.snippets_json: Path = self._get_file("snippets_json")
        self.ts_dir: Path = self._get_dir("ts_dir", create=True)
        self.variable_names_ts: Path = self._get_file("variable_names_ts")
        self.variable_completion_ts: Path = self._get_file("variable_completion_ts")
        self.command_names_ts: Path = self._get_file("command_names_ts")
        self.command_completion_ts: Path = self._get_file("command_completion_ts")

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

    def _get_phases(self, name: str) -> set[ItemType]:
        """
        Get the list of parser types to run read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: List of active parser types
        """
        phases = set()
        for line in self.settings[name].splitlines():
            if line:
                item_type = ItemType.from_string(line)
                if item_type in ItemType.all_phases():
                    phases.add(item_type)
                else:
                    log.warning(f"Phase {item_type.value} will allways be called and needs not to be specified")
        return phases

    def _get_content_patterns(self, name: str) -> list[ContentPattern]:
        """
        Get the list of content start and end patterns.

        :param name: Name of the setting in the *.ini file
        :return: List of ContentPattern objects for each section to be parsed
        """
        content_pattern_list: list[ContentPattern] = []
        for line in self.settings[name].splitlines():
            if line:
                if m := SystemConfig.CONTENT_START_STOP_PATTERN.match(line):
                    start_pattern = re.compile(m.group(1))
                    stop_pattern = re.compile(m.group(2))
                    content_pattern = ContentPattern(start_pattern, stop_pattern)
                    content_pattern_list.append(content_pattern)
                else:
                    log.error(f"Can't parse start and stop pattern: {line}")
        return content_pattern_list

    def _get_log_level(self, name: str) -> int:
        """
        Convert the string value to Log level read from the *.ini file.

        :param name: Name of the setting in the *.ini file
        :return: Log level
        """
        log_level = logging.getLevelName(self.settings[name].upper())
        return log_level

    def has_phase(self, item_type: ItemType) -> bool:
        """
        Check if the specified phase is active.

        :param item_type: ItemType to check if it's active
        :return: True if the phase is active, False otherwise
        """
        ret_val: bool = False
        if item_type in self.phases:
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

    def get_csv_file(self, item_type: ItemType, rel_path: bool = False) -> Path:
        """
        Get the *.csv file for the specified item type, e.g. for callbacks.

        :param item_type: ItemType to get the path for
        :param rel_path: If True then the relative path to the root folder is returned
        :return: Path of the *.csv file
        """
        match item_type:
            case ItemType.CALLBACK:
                path = self.callbacks_csv
            case ItemType.WIDGET:
                path = self.widgets_csv
            case ItemType.FUNCTION:
                path = self.functions_csv
            case ItemType.COMMAND:
                path = self.commands_csv
            case ItemType.VARIABLE:
                path = self.variables_csv
            case _:
                raise ValueError(f"No *.csv file for {item_type.name}")
        if rel_path:
            path = path.relative_to(self.root_dir)
        return path

    def get_patch_csv_file(self, item_type: ItemType, rel_path: bool = False) -> Optional[Path]:
        """
        Get the patch *.csv file for the specified item type, e.g. for callbacks.

        :param item_type: ItemType to get the path for
        :param rel_path: If True then the relative path to the root folder is returned
        :return: Path of the patch *.csv file or None if there is no file
        """
        match item_type:
            case ItemType.CALLBACK:
                path = self.callbacks_csv
            case ItemType.WIDGET:
                path = self.widgets_csv
            case ItemType.FUNCTION:
                path = self.functions_csv
            case ItemType.COMMAND:
                path = self.commands_csv
            case ItemType.VARIABLE:
                path = self.variables_csv
            case _:
                raise ValueError(f"No *.csv file for {item_type.name}")
        filename = path.name.replace("built_in", "patch")
        path = path.parent / filename
        if not path.is_file():
            path = None
        elif rel_path:
            path = path.relative_to(self.root_dir)
        return path

    def get_csv_path(self, item_type: ItemType) -> str:
        """
        Get the path of the *.csv file for the specified item type.

        :param item_type: ItemType to get the *.csv file for
        :return: Path of the *.csv file or "None" if there is no file
        """
        csv_file = self.get_csv_file(item_type, rel_path=True)
        if csv_file:
            csv_path = csv_file.as_posix()
        else:
            csv_path = "None"
        return csv_path

    def get_patch_csv_path(self, item_type: ItemType) -> str:
        """
        Get the path of the patch *.csv file for the specified item type.

        :param item_type: ItemType to get the patch *.csv file for
        :return: Path of the patch *.csv file or "None" if there is no file
        """
        patch_csv_file = self.get_patch_csv_file(item_type, rel_path=True)
        if patch_csv_file:
            patch_csv_path = patch_csv_file.as_posix()
        else:
            patch_csv_path = "None"
        return patch_csv_path

    def rel_to_root(self, file: Path) -> str:
        """
        Get the file path relative to the root directory.

        :param file: File to get the relative path for
        :return: Path of the file relative to the root directory
        """
        path = file.relative_to(self.root_dir).as_posix()
        return path


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    ini_file = root / "cfg" / "ksp_7_10" / "system.ini"
    config = SystemConfig(ini_file)
    log.info(SystemConfig().kontakt_version)
